"""
유틸리티 모듈 테스트
"""
import tempfile
from pathlib import Path
import pytest

from utils import (
    save_html_file,
    create_table_html,
    create_full_html,
    save_json_file,
    load_json_file,
    generate_timestamp,
    clean_filename,
    ensure_directory_exists
)
from exceptions import FileProcessingError


class TestUtils:
    """유틸리티 함수 테스트"""
    
    def test_save_html_file(self):
        """HTML 파일 저장 테스트"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            content = "<html><body>테스트</body></html>"
            filename = "test.html"
            
            result_path = save_html_file(content, filename, output_dir)
            
            assert result_path.exists()
            assert result_path.name == filename
            assert result_path.read_text(encoding="utf-8") == content
    
    def test_create_table_html(self):
        """테이블 HTML 생성 테스트"""
        tables_html = "<table><tr><td>테스트</td></tr></table>"
        result = create_table_html(tables_html)
        
        assert "<html>" in result
        assert "<head>" in result
        assert "<meta charset='utf-8'>" in result
        assert tables_html in result
        assert "<style>" in result
    
    def test_create_full_html(self):
        """전체 HTML 생성 테스트"""
        content = "<p>테스트 내용</p>"
        result = create_full_html(content)
        
        assert "<html>" in result
        assert "<head>" in result
        assert "<meta charset='utf-8'>" in result
        assert content in result
    
    def test_save_and_load_json_file(self):
        """JSON 파일 저장 및 로드 테스트"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            test_data = {"test": "data", "number": 123}
            
            save_json_file(test_data, file_path)
            loaded_data = load_json_file(file_path)
            
            assert loaded_data == test_data
    
    def test_generate_timestamp(self):
        """타임스탬프 생성 테스트"""
        timestamp = generate_timestamp()
        
        # YYYYMMDD_HHMMSS 형식인지 확인
        assert len(timestamp) == 15  # 8 + 1 + 6
        assert "_" in timestamp
        assert timestamp.replace("_", "").isdigit()
    
    def test_clean_filename(self):
        """파일명 정리 테스트"""
        # 안전하지 않은 문자들
        unsafe_filename = "test<>:\"/\\|?*file.txt"
        cleaned = clean_filename(unsafe_filename)
        
        assert "<" not in cleaned
        assert ">" not in cleaned
        assert ":" not in cleaned
        assert '"' not in cleaned
        assert "/" not in cleaned
        assert "\\" not in cleaned
        assert "|" not in cleaned
        assert "?" not in cleaned
        assert "*" not in cleaned
        assert "file.txt" in cleaned
    
    def test_ensure_directory_exists(self):
        """디렉토리 생성 테스트"""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new_directory"
            
            ensure_directory_exists(new_dir)
            
            assert new_dir.exists()
            assert new_dir.is_dir()
    
    def test_save_html_file_error(self):
        """HTML 파일 저장 오류 테스트"""
        # 읽기 전용 디렉토리에 저장 시도
        with tempfile.TemporaryDirectory() as temp_dir:
            readonly_dir = Path(temp_dir) / "readonly"
            readonly_dir.mkdir()
            readonly_dir.chmod(0o444)  # 읽기 전용
            
            try:
                with pytest.raises(FileProcessingError):
                    save_html_file("test", "test.html", readonly_dir)
            finally:
                # 권한 복원
                readonly_dir.chmod(0o755)
    
    def test_parse_date_from_subject(self):
        """제목에서 날짜 추출 테스트"""
        from utils import parse_date_from_subject
        
        # 패턴 1: "2025년09월04일" 형식
        subject1 = "(조이푸드)금일2편/익일1편 2025년09월04일(2편) ~ 09월05일(1편)"
        result1 = parse_date_from_subject(subject1)
        assert result1 == "20250904"
        
        # 패턴 2: "20250902" 형식
        subject2 = "삼립_푸드코아 확정주문 및 센터 별 픽업수량 안내 / SO 납품일 : 20250902"
        result2 = parse_date_from_subject(subject2)
        assert result2 == "20250902"
        
        # 패턴 3: "09월04일" 형식 (올해 기준)
        subject3 = "일반 제목 09월04일 테스트"
        result3 = parse_date_from_subject(subject3)
        assert result3 is not None
        assert len(result3) == 8  # YYYYMMDD 형식
        
        # 날짜가 없는 제목
        subject4 = "일반 제목입니다"
        result4 = parse_date_from_subject(subject4)
        assert result4 is None
    
    def test_find_message_by_date(self):
        """특정 날짜 메시지 찾기 테스트"""
        from utils import find_message_by_date
        
        messages_data = [
            {"id": "msg1", "subject": "2025년09월04일 테스트", "date": "2025-09-04"},
            {"id": "msg2", "subject": "2025년09월05일 테스트", "date": "2025-09-05"},
            {"id": "msg3", "subject": "일반 제목", "date": "2025-09-06"}
        ]
        
        # 특정 날짜 찾기
        result = find_message_by_date(messages_data, "20250904")
        assert result is not None
        assert result["id"] == "msg1"
        
        # 없는 날짜 찾기
        result = find_message_by_date(messages_data, "20250910")
        assert result is None
    
    def test_find_latest_message(self):
        """최신 메시지 찾기 테스트"""
        from utils import find_latest_message
        
        messages_data = [
            {"id": "msg1", "subject": "2025년09월04일 테스트", "date": "2025-09-04"},
            {"id": "msg2", "subject": "2025년09월06일 테스트", "date": "2025-09-06"},
            {"id": "msg3", "subject": "2025년09월05일 테스트", "date": "2025-09-05"}
        ]
        
        # 최신 메시지 찾기 (날짜 순으로 정렬)
        result = find_latest_message(messages_data)
        assert result is not None
        assert result["id"] == "msg2"  # 09월06일이 가장 최신
        
        # 빈 목록
        result = find_latest_message([])
        assert result is None
