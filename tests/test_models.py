"""
모델 클래스 테스트
"""
import tempfile
import pytest
from pathlib import Path

from models import EmailData, TableData, ProcessingResult, FilePaths


class TestEmailData:
    """EmailData 클래스 테스트"""
    
    def test_email_data_creation(self):
        """이메일 데이터 생성 테스트"""
        email = EmailData(
            message_id="test123",
            sender="test@example.com",
            subject="테스트 제목",
            date="2024-01-01",
            html_content="<html>테스트</html>",
            text_content="테스트 텍스트",
            tables_html="<table>테이블</table>"
        )
        
        assert email.message_id == "test123"
        assert email.sender == "test@example.com"
        assert email.subject == "테스트 제목"
        assert email.has_html is True
        assert email.has_tables is True
    
    def test_has_tables_property(self):
        """has_tables 속성 테스트"""
        # 테이블이 있는 경우
        email_with_tables = EmailData(
            message_id="1", sender="test", subject="test", date="2024-01-01",
            tables_html="<table>테이블</table>"
        )
        assert email_with_tables.has_tables is True
        
        # 테이블이 없는 경우
        email_without_tables = EmailData(
            message_id="1", sender="test", subject="test", date="2024-01-01",
            tables_html=""
        )
        assert email_without_tables.has_tables is False
        
        # None인 경우
        email_none_tables = EmailData(
            message_id="1", sender="test", subject="test", date="2024-01-01",
            tables_html=None
        )
        assert email_none_tables.has_tables is False
    
    def test_has_html_property(self):
        """has_html 속성 테스트"""
        # HTML이 있는 경우
        email_with_html = EmailData(
            message_id="1", sender="test", subject="test", date="2024-01-01",
            html_content="<html>테스트</html>"
        )
        assert email_with_html.has_html is True
        
        # HTML이 없는 경우
        email_without_html = EmailData(
            message_id="1", sender="test", subject="test", date="2024-01-01",
            html_content=""
        )
        assert email_without_html.has_html is False


class TestTableData:
    """TableData 클래스 테스트"""
    
    def test_table_data_creation(self):
        """테이블 데이터 생성 테스트"""
        table = TableData(
            headers=["열1", "열2"],
            rows=[["값1", "값2"], ["값3", "값4"]]
        )
        
        assert table.headers == ["열1", "열2"]
        assert table.rows == [["값1", "값2"], ["값3", "값4"]]
        assert table.row_count == 2
        assert table.col_count == 2
        assert table.is_empty() is False
    
    def test_empty_table(self):
        """빈 테이블 테스트"""
        empty_table = TableData(headers=[], rows=[])
        
        assert empty_table.row_count == 0
        assert empty_table.col_count == 0
        assert empty_table.is_empty() is True
    
    def test_table_with_none_values(self):
        """None 값이 포함된 테이블 테스트"""
        table = TableData(
            headers=["열1", "열2"],
            rows=[["값1", None], [None, "값4"]]
        )
        
        assert table.row_count == 2
        assert table.col_count == 2
        assert table.is_empty() is False


class TestProcessingResult:
    """ProcessingResult 클래스 테스트"""
    
    def test_success_result(self):
        """성공 결과 테스트"""
        result = ProcessingResult(
            success=True,
            message="성공",
            input_file=Path("input.html"),
            output_files=[Path("output.xlsx")],
            processing_time=1.5
        )
        
        assert result.success is True
        assert result.message == "성공"
        assert result.input_file == Path("input.html")
        assert len(result.output_files) == 1
        assert result.processing_time == 1.5
        assert result.error is None
    
    def test_failure_result(self):
        """실패 결과 테스트"""
        error = Exception("테스트 오류")
        result = ProcessingResult(
            success=False,
            message="실패",
            error=error,
            processing_time=0.5
        )
        
        assert result.success is False
        assert result.message == "실패"
        assert result.error == error
        assert result.input_file is None
        assert len(result.output_files) == 0


class TestFilePaths:
    """FilePaths 클래스 테스트"""
    
    def test_file_paths_creation(self):
        """파일 경로 생성 테스트"""
        file_paths = FilePaths(
            html_file=Path("test.html"),
            png_file=Path("test.png"),
            json_file=Path("test.json"),
            excel_file=Path("test.xlsx")
        )
        
        assert file_paths.html_file == Path("test.html")
        assert file_paths.png_file == Path("test.png")
        assert file_paths.json_file == Path("test.json")
        assert file_paths.excel_file == Path("test.xlsx")
    
    def test_get_all_files(self):
        """모든 파일 경로 반환 테스트"""
        file_paths = FilePaths(
            html_file=Path("test.html"),
            png_file=Path("test.png"),
            json_file=None,
            excel_file=Path("test.xlsx")
        )
        
        all_files = file_paths.get_all_files()
        
        assert len(all_files) == 3
        assert Path("test.html") in all_files
        assert Path("test.png") in all_files
        assert Path("test.xlsx") in all_files
        assert None not in all_files
    
    def test_get_existing_files(self):
        """존재하는 파일들만 반환 테스트"""
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_file = Path(temp_dir) / "existing.txt"
            existing_file.write_text("test")
            
            file_paths = FilePaths(
                html_file=existing_file,
                png_file=Path("nonexistent.png"),
                json_file=None,
                excel_file=Path("nonexistent.xlsx")
            )
            
            existing_files = file_paths.get_existing_files()
            
            assert len(existing_files) == 1
            assert existing_file in existing_files
