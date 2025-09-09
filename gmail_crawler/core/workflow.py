"""
메인 워크플로우 모듈
Gmail 이메일에서 테이블을 추출하여 Excel로 변환하는 전체 프로세스를 관리합니다.
"""
import time
from pathlib import Path
from typing import Optional

from googleapiclient.discovery import build

from .config import Config
from ..utils.exceptions import GmailCrawlerError
from ..utils.logger import LoggerMixin
from ..models.models import EmailData, ProcessingResult, FilePaths
from ..services.gmail_auth import GmailAuthenticator
from ..services.read_body import EmailExtractor
from ..services.html_to_image import capture_html_to_png
from ..services.geminiApi import GeminiAPIClient
from ..services.json_to_excel import json_tables_to_excel
from ..utils.utils import (
    save_html_file, 
    create_table_html, 
    create_full_html, 
    save_json_file,
    generate_timestamp,
    clean_filename,
    parse_date_from_subject,
    find_message_by_date,
    find_latest_message
)


class GmailTableExtractor(LoggerMixin):
    """Gmail 이메일에서 테이블을 추출하는 메인 클래스"""
    
    def __init__(self, config: Config):
        self.config = config
        self.gmail_service: Optional[build] = None
        self.email_extractor: Optional[EmailExtractor] = None
        self.gemini_client: Optional[GeminiAPIClient] = None
        
        # 디렉토리 생성
        self.config.ensure_directories()
    
    def authenticate(self) -> None:
        """Gmail API 인증을 수행합니다."""
        try:
            self.logger.info("Gmail 인증 시작")
            authenticator = GmailAuthenticator()
            self.gmail_service = authenticator.authenticate()
            self.email_extractor = EmailExtractor(self.gmail_service)
            self.logger.info("Gmail 인증 완료")
        except Exception as e:
            self.logger.error(f"Gmail 인증 실패: {e}")
            raise
    
    def initialize_gemini(self) -> None:
        """Gemini API 클라이언트를 초기화합니다."""
        try:
            self.logger.info("Gemini API 초기화 시작")
            self.gemini_client = GeminiAPIClient(self.config.gemini_api_key)
            self.logger.info("Gemini API 초기화 완료")
        except Exception as e:
            self.logger.error(f"Gemini API 초기화 실패: {e}")
            raise
    
    def extract_email_data(self, target_date: Optional[str] = None) -> Optional[EmailData]:
        """
        이메일 데이터를 추출합니다.
        
        Args:
            target_date: 특정 날짜의 메시지를 찾을 경우 (YYYYMMDD 형식)
        
        Returns:
            이메일 데이터 또는 None
        """
        try:
            if not self.email_extractor:
                raise GmailCrawlerError("이메일 추출기가 초기화되지 않았습니다")
            
            if self.config.message_id:
                # 특정 메시지 ID로 추출
                self.logger.info(f"특정 메시지 추출: {self.config.message_id}")
                return self.email_extractor.get_email_data(self.config.message_id)
            else:
                # 발신자로부터 메시지 목록 추출
                self.logger.info(f"발신자로부터 메시지 목록 추출: {self.config.sender_name}")
                messages_data = self.email_extractor.list_messages_from_sender(
                    self.config.sender_name, 
                    self.config.max_results
                )
                
                if not messages_data:
                    self.logger.warning("처리할 메시지가 없습니다")
                    return None
                
                # 메시지 선택 로직
                selected_message = None
                
                if target_date:
                    # 특정 날짜의 메시지 찾기
                    self.logger.info(f"특정 날짜 메시지 검색: {target_date}")
                    selected_message = find_message_by_date(messages_data, target_date)
                    if selected_message:
                        self.logger.info(f"날짜 {target_date}의 메시지 발견: {selected_message['subject']}")
                    else:
                        self.logger.warning(f"날짜 {target_date}의 메시지를 찾을 수 없습니다")
                else:
                    # 가장 최신 메시지 선택
                    self.logger.info("가장 최신 메시지 선택")
                    selected_message = find_latest_message(messages_data)
                    if selected_message:
                        parsed_date = parse_date_from_subject(selected_message['subject'])
                        self.logger.info(f"최신 메시지 선택: {selected_message['subject']} (날짜: {parsed_date})")
                
                if not selected_message:
                    self.logger.warning("선택할 수 있는 메시지가 없습니다")
                    return None
                
                return self.email_extractor.get_email_data(selected_message['id'])
                
        except Exception as e:
            self.logger.error(f"이메일 데이터 추출 실패: {e}")
            raise
    
    def save_email_html(self, email_data: EmailData) -> Optional[Path]:
        """
        이메일 HTML을 파일로 저장합니다.
        
        Args:
            email_data: 이메일 데이터
            
        Returns:
            저장된 HTML 파일 경로 또는 None
        """
        try:
            if not email_data.has_html and not email_data.has_tables:
                self.logger.warning("저장할 HTML 내용이 없습니다")
                return None
            
            timestamp = generate_timestamp()
            sender_clean = clean_filename(self.config.sender_name)
            
            if email_data.has_tables:
                # 테이블이 있는 경우
                html_content = create_table_html(email_data.tables_html)
                filename = f"{sender_clean}_{timestamp}.html"
                self.logger.info("테이블 HTML 저장")
            else:
                # 일반 HTML
                html_content = create_full_html(email_data.html_content)
                filename = f"{sender_clean}_{timestamp}.html"
                self.logger.info("일반 HTML 저장")
            
            file_path = save_html_file(html_content, filename, self.config.output_dir)
            self.logger.info(f"HTML 파일 저장 완료: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"HTML 파일 저장 실패: {e}")
            raise
    
    def process_tables(self, html_file: Path) -> FilePaths:
        """
        HTML 파일을 처리하여 테이블을 Excel로 변환합니다.
        
        Args:
            html_file: HTML 파일 경로
            
        Returns:
            생성된 파일 경로들
        """
        file_paths = FilePaths(html_file=html_file)
        
        try:
            # 1. HTML을 이미지로 변환
            self.logger.info("HTML을 이미지로 변환 중...")
            png_file = capture_html_to_png(
                html_file, 
                full_page=self.config.full_page_capture,
                device_scale_factor=self.config.device_scale_factor
            )
            file_paths.png_file = png_file
            self.logger.info(f"이미지 저장 완료: {png_file}")
            
            # 2. Gemini로 테이블 추출
            if not self.gemini_client:
                self.initialize_gemini()
            
            self.logger.info("Gemini로 테이블 추출 중...")
            table_data = self.gemini_client.table_image_to_json(png_file)
            
            # 3. JSON 파일 저장
            json_file = html_file.with_suffix(".json")
            save_json_file(table_data, json_file)
            file_paths.json_file = json_file
            self.logger.info(f"JSON 저장 완료: {json_file}")
            
            # 4. Excel 파일 생성
            self.logger.info("Excel 파일 생성 중...")
            excel_file = json_tables_to_excel(json_file)
            file_paths.excel_file = excel_file
            self.logger.info(f"Excel 저장 완료: {excel_file}")
            
            return file_paths
            
        except Exception as e:
            self.logger.error(f"테이블 처리 실패: {e}")
            raise
    
    def run(self, target_date: Optional[str] = None) -> ProcessingResult:
        """
        전체 워크플로우를 실행합니다.
        
        Args:
            target_date: 특정 날짜의 메시지를 처리할 경우 (YYYYMMDD 형식)
        
        Returns:
            처리 결과
        """
        start_time = time.time()
        
        try:
            self.logger.info("Gmail 테이블 추출 워크플로우 시작")
            
            # 1. 인증
            self.authenticate()
            
            # 2. 이메일 데이터 추출
            email_data = self.extract_email_data(target_date)
            if not email_data:
                return ProcessingResult(
                    success=False,
                    message="처리할 이메일이 없습니다",
                    processing_time=time.time() - start_time
                )
            
            # 3. HTML 파일 저장
            html_file = self.save_email_html(email_data)
            if not html_file:
                return ProcessingResult(
                    success=False,
                    message="저장할 HTML 내용이 없습니다",
                    processing_time=time.time() - start_time
                )
            
            # 4. 테이블 처리 (이미지 → JSON → Excel)
            file_paths = self.process_tables(html_file)
            
            processing_time = time.time() - start_time
            self.logger.info(f"워크플로우 완료 (소요시간: {processing_time:.2f}초)")
            
            return ProcessingResult(
                success=True,
                message="워크플로우가 성공적으로 완료되었습니다",
                input_file=html_file,
                output_files=file_paths.get_all_files(),
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"워크플로우 실행 중 오류: {e}")
            
            return ProcessingResult(
                success=False,
                message=f"워크플로우 실행 중 오류 발생: {e}",
                error=e,
                processing_time=processing_time
            )
