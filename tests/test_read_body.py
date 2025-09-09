"""
이메일 본문 추출 모듈 테스트
"""
import pytest
from unittest.mock import Mock, patch
from read_body import EmailExtractor


class TestEmailExtractor:
    """EmailExtractor 클래스 테스트"""
    
    def test_list_messages_from_sender_with_name(self):
        """이름으로 메시지 검색 테스트"""
        # Mock 서비스 생성
        mock_service = Mock()
        mock_response = {
            "messages": [
                {"id": "msg1"},
                {"id": "msg2"}
            ]
        }
        mock_service.users().messages().list().execute.return_value = mock_response
        
        # Mock 메시지 메타데이터
        mock_metadata = {
            "payload": {
                "headers": [
                    {"name": "From", "value": "이도한 <sender@example.com>"},
                    {"name": "Subject", "value": "테스트 제목"},
                    {"name": "Date", "value": "2024-01-01"}
                ]
            }
        }
        mock_service.users().messages().get().execute.return_value = mock_metadata
        
        extractor = EmailExtractor(mock_service)
        
        # 이름으로 검색
        result = extractor.list_messages_from_sender("이도한", 10)
        
        assert len(result) == 2
        assert result[0]["id"] == "msg1"
        assert result[1]["id"] == "msg2"
        assert result[0]["subject"] == "테스트 제목"
    
    def test_list_messages_from_sender_with_email(self):
        """이메일 주소로 메시지 검색 테스트"""
        # Mock 서비스 생성
        mock_service = Mock()
        mock_response = {
            "messages": [
                {"id": "msg1"}
            ]
        }
        mock_service.users().messages().list().execute.return_value = mock_response
        
        # Mock 메시지 메타데이터
        mock_metadata = {
            "payload": {
                "headers": [
                    {"name": "From", "value": "이도한 <sender@example.com>"},
                    {"name": "Subject", "value": "테스트 제목"},
                    {"name": "Date", "value": "2024-01-01"}
                ]
            }
        }
        mock_service.users().messages().get().execute.return_value = mock_metadata
        
        extractor = EmailExtractor(mock_service)
        
        # 이메일 주소로 검색
        result = extractor.list_messages_from_sender("sender@example.com", 10)
        
        assert len(result) == 1
        assert result[0]["id"] == "msg1"
        assert result[0]["subject"] == "테스트 제목"
    
    def test_extract_tables_only_with_beautifulsoup(self):
        """BeautifulSoup를 사용한 테이블 추출 테스트"""
        html = """
        <html>
        <body>
            <p>일반 텍스트</p>
            <table>
                <tr><th>열1</th><th>열2</th></tr>
                <tr><td>값1</td><td>값2</td></tr>
            </table>
            <p>다른 텍스트</p>
        </body>
        </html>
        """
        
        extractor = EmailExtractor(None)
        result = extractor.extract_tables_only(html)
        
        assert "<table>" in result
        assert "<tr><th>열1</th><th>열2</th></tr>" in result
        assert "<tr><td>값1</td><td>값2</td></tr>" in result
        assert "<p>일반 텍스트</p>" not in result
    
    def test_extract_tables_only_empty_html(self):
        """빈 HTML에서 테이블 추출 테스트"""
        extractor = EmailExtractor(None)
        result = extractor.extract_tables_only("")
        
        assert result == ""
    
    def test_extract_tables_only_no_tables(self):
        """테이블이 없는 HTML에서 추출 테스트"""
        html = "<html><body><p>테이블 없음</p></body></html>"
        
        extractor = EmailExtractor(None)
        result = extractor.extract_tables_only(html)
        
        assert result == ""
