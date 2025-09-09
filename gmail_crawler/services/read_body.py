"""
이메일 본문 추출 모듈
Gmail API에서 이메일 내용을 추출하고 파싱합니다.
"""
import base64
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from googleapiclient.discovery import build

try:
    from bs4 import BeautifulSoup  # pip install beautifulsoup4
except ImportError:
    BeautifulSoup = None

from ..utils.exceptions import EmailNotFoundError, EmailExtractionError, TableExtractionError
from ..utils.logger import LoggerMixin
from ..models.models import EmailData

class EmailExtractor(LoggerMixin):
    """이메일 내용 추출을 담당하는 클래스"""
    
    def __init__(self, service: build):
        self.service = service
    
    def decode_part(self, data: str) -> str:
        """
        Gmail API의 base64url 인코딩된 데이터를 디코딩합니다.
        
        Args:
            data: base64url 인코딩된 데이터
            
        Returns:
            디코딩된 문자열
        """
        if not data:
            return ""
        try:
            return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="ignore")
        except Exception as e:
            self.logger.warning(f"데이터 디코딩 실패: {e}")
            return ""
    
    def extract_html(self, payload: Dict[str, Any]) -> str:
        """
        멀티파트 구조를 순회하며 text/html을 추출합니다.
        
        Args:
            payload: Gmail API 메시지 페이로드
            
        Returns:
            HTML 내용
        """
        mime_type = payload.get("mimeType", "")
        body_data = payload.get("body", {}).get("data")
        parts = payload.get("parts")

        if mime_type == "text/html" and body_data:
            return self.decode_part(body_data)

        if parts:
            for part in parts:
                html = self.extract_html(part)
                if html:
                    return html
        return ""
    
    def extract_tables_only(self, html: str) -> str:
        """
        HTML에서 테이블만 추출합니다.
        
        Args:
            html: HTML 내용
            
        Returns:
            추출된 테이블 HTML
            
        Raises:
            TableExtractionError: 테이블 추출 실패 시
        """
        if not html:
            return ""
        
        try:
            # 1) BeautifulSoup 사용 (권장)
            if BeautifulSoup is not None:
                soup = BeautifulSoup(html, "html.parser")
                tables = soup.find_all("table")
                if tables:
                    return "\n".join(str(t) for t in tables)
                return ""
            
            # 2) 폴백: 정규식
            tables = re.findall(r"(?is)<table\b.*?</table>", html)
            return "\n".join(tables)
            
        except Exception as e:
            self.logger.error(f"테이블 추출 실패: {e}")
            raise TableExtractionError(f"테이블 추출 실패: {e}")
    
    def extract_text(self, payload: Dict[str, Any]) -> str:
        """
        멀티파트 구조를 순회하며 텍스트를 추출합니다.
        
        Args:
            payload: Gmail API 메시지 페이로드
            
        Returns:
            텍스트 내용
        """
        mime_type = payload.get("mimeType", "")
        body_data = payload.get("body", {}).get("data")
        parts = payload.get("parts")

        if mime_type.startswith("text/") and body_data:
            return self.decode_part(body_data)

        if parts:
            texts = []
            for part in parts:
                text = self.extract_text(part)
                if text:
                    texts.append(text)
            return "\n".join(texts)
        return ""
    
    def list_messages_from_sender(self, sender: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        특정 발신자로부터 온 메시지 목록을 가져옵니다.
        발신자는 이름 또는 이메일 주소일 수 있습니다.
        
        Args:
            sender: 발신자 이름 또는 이메일 주소
            max_results: 최대 결과 수
            
        Returns:
            메시지 데이터 목록 (ID, 제목, 날짜 포함)
            
        Raises:
            EmailNotFoundError: 메시지를 찾을 수 없을 때
        """
        try:
            # 이메일 주소인지 확인 (간단한 이메일 패턴 체크)
            is_email = "@" in sender and "." in sender.split("@")[-1]
            
            if is_email:
                # 이메일 주소인 경우 정확한 매칭
                query = f'from:{sender}'
                self.logger.info(f'이메일 주소로 검색: {sender}')
            else:
                # 이름인 경우 부분 매칭
                query = f'from:"{sender}"'
                self.logger.info(f'이름으로 검색: {sender}')
            
            response = self.service.users().messages().list(
                userId="me", q=query, maxResults=max_results
            ).execute()
            
            messages = response.get("messages", [])
            if not messages:
                self.logger.warning(f'"{sender}"로부터 온 메일 없음')
                raise EmailNotFoundError(f'"{sender}"로부터 온 메일이 없습니다')
            
            results = []
            self.logger.info(f'"{sender}"로부터 온 메일 목록:')
            
            for msg in messages:
                msg_id = msg["id"]
                msg_data = self.service.users().messages().get(
                    userId="me", 
                    id=msg_id, 
                    format="metadata", 
                    metadataHeaders=["From", "Subject", "Date"]
                ).execute()
                
                headers = msg_data.get("payload", {}).get("headers", [])
                header_dict = {h["name"]: h["value"] for h in headers}
                from_val = header_dict.get("From", "")
                subject_val = header_dict.get("Subject", "")
                date_val = header_dict.get("Date", "")
                
                # 이메일 주소로 검색한 경우 정확한 매칭, 이름으로 검색한 경우 부분 매칭
                if is_email:
                    # 이메일 주소가 From 헤더에 포함되어 있는지 확인
                    if sender.lower() in from_val.lower():
                        self.logger.info(f"Date: {date_val}, From: {from_val}, Subject: {subject_val}, ID: {msg_id}")
                        results.append({
                            "id": msg_id,
                            "subject": subject_val,
                            "date": date_val,
                            "from": from_val
                        })
                else:
                    # 이름이 From 헤더에 포함되어 있는지 확인
                    if sender in from_val:
                        self.logger.info(f"Date: {date_val}, From: {from_val}, Subject: {subject_val}, ID: {msg_id}")
                        results.append({
                            "id": msg_id,
                            "subject": subject_val,
                            "date": date_val,
                            "from": from_val
                        })
            
            return results
            
        except Exception as e:
            self.logger.error(f"메시지 목록 조회 실패: {e}")
            raise EmailNotFoundError(f"메시지 목록 조회 실패: {e}")
    
    def get_email_data(self, message_id: str) -> EmailData:
        """
        특정 메시지의 이메일 데이터를 가져옵니다.
        
        Args:
            message_id: 메시지 ID
            
        Returns:
            이메일 데이터 객체
            
        Raises:
            EmailExtractionError: 이메일 추출 실패 시
        """
        try:
            # 메시지 메타데이터 가져오기
            msg_metadata = self.service.users().messages().get(
                userId="me", 
                id=message_id, 
                format="metadata", 
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()
            
            headers = msg_metadata.get("payload", {}).get("headers", [])
            header_dict = {h["name"]: h["value"] for h in headers}
            
            # 전체 메시지 가져오기
            msg_full = self.service.users().messages().get(
                userId="me", id=message_id, format="full"
            ).execute()
            
            # HTML과 텍스트 추출
            html_content = self.extract_html(msg_full["payload"])
            text_content = self.extract_text(msg_full["payload"])
            tables_html = self.extract_tables_only(html_content) if html_content else ""
            
            return EmailData(
                message_id=message_id,
                sender=header_dict.get("From", ""),
                subject=header_dict.get("Subject", ""),
                date=header_dict.get("Date", ""),
                html_content=html_content,
                text_content=text_content,
                tables_html=tables_html
            )
            
        except Exception as e:
            self.logger.error(f"이메일 데이터 추출 실패: {e}")
            raise EmailExtractionError(f"이메일 데이터 추출 실패: {e}")


# 하위 호환성을 위한 함수들
def decode_part(data: str) -> str:
    """하위 호환성을 위한 함수"""
    extractor = EmailExtractor(None)  # type: ignore
    return extractor.decode_part(data)

def extract_html(payload: Dict[str, Any]) -> str:
    """하위 호환성을 위한 함수"""
    extractor = EmailExtractor(None)  # type: ignore
    return extractor.extract_html(payload)

def extract_tables_only(html: str) -> str:
    """하위 호환성을 위한 함수"""
    extractor = EmailExtractor(None)  # type: ignore
    return extractor.extract_tables_only(html)

def extract_text(payload: Dict[str, Any]) -> str:
    """하위 호환성을 위한 함수"""
    extractor = EmailExtractor(None)  # type: ignore
    return extractor.extract_text(payload)

def list_messages_from_name(service: build, name: str, max_results: int = 10) -> List[str]:
    """하위 호환성을 위한 함수 (deprecated: list_messages_from_sender 사용 권장)"""
    extractor = EmailExtractor(service)
    messages_data = extractor.list_messages_from_sender(name, max_results)
    return [msg['id'] for msg in messages_data]

def list_messages_from_sender(service: build, sender: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """하위 호환성을 위한 함수"""
    extractor = EmailExtractor(service)
    return extractor.list_messages_from_sender(sender, max_results)

def main():
    """하위 호환성을 위한 메인 함수"""
    from .gmail_auth import build_gmail
    from ..utils.utils import create_table_html, create_full_html, save_html_file
    
    try:
        service = build_gmail()
        extractor = EmailExtractor(service)
        
        message_ids = extractor.list_messages_from_name(name="이도한", max_results=10)
        if not message_ids:
            print("메일 없음")
            return

        email_data = extractor.get_email_data(message_ids[0])
        
        if email_data.has_tables:
            html_content = create_table_html(email_data.tables_html)
            filename = "selected_email_tables.html"
            save_html_file(html_content, filename, Path("."))
            print(f"테이블 저장 완료 → {filename}")
        elif email_data.has_html:
            html_content = create_full_html(email_data.html_content)
            filename = "selected_email.html"
            save_html_file(html_content, filename, Path("."))
            print(f"HTML 메일을 {filename} 파일로 저장했습니다.")
        else:
            print(email_data.text_content[:2000] if email_data.text_content else "내용 없음")
            
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    # 라이브러리화: 단독 실행은 지양하고, main.py에서 오케스트레이션합니다.
    main()