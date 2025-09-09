"""
데이터 모델 클래스들
애플리케이션에서 사용되는 데이터 구조를 정의합니다.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class EmailData:
    """이메일 데이터를 담는 클래스"""
    message_id: str
    sender: str
    subject: str
    date: str
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    tables_html: Optional[str] = None
    
    @property
    def has_tables(self) -> bool:
        """테이블이 있는지 확인합니다."""
        return bool(self.tables_html and self.tables_html.strip())
    
    @property
    def has_html(self) -> bool:
        """HTML 내용이 있는지 확인합니다."""
        return bool(self.html_content and self.html_content.strip())


@dataclass
class TableData:
    """테이블 데이터를 담는 클래스"""
    headers: List[str]
    rows: List[List[Optional[str]]]
    
    @property
    def row_count(self) -> int:
        """행 개수를 반환합니다."""
        return len(self.rows)
    
    @property
    def col_count(self) -> int:
        """열 개수를 반환합니다."""
        return len(self.headers) if self.headers else 0
    
    def is_empty(self) -> bool:
        """테이블이 비어있는지 확인합니다."""
        return self.row_count == 0 or self.col_count == 0


@dataclass
class ProcessingResult:
    """처리 결과를 담는 클래스"""
    success: bool
    message: str
    input_file: Optional[Path] = None
    output_files: List[Path] = None
    error: Optional[Exception] = None
    processing_time: Optional[float] = None
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []


@dataclass
class FilePaths:
    """파일 경로들을 관리하는 클래스"""
    html_file: Optional[Path] = None
    png_file: Optional[Path] = None
    json_file: Optional[Path] = None
    excel_file: Optional[Path] = None
    
    def get_all_files(self) -> List[Path]:
        """모든 파일 경로를 반환합니다."""
        return [f for f in [self.html_file, self.png_file, self.json_file, self.excel_file] if f is not None]
    
    def get_existing_files(self) -> List[Path]:
        """존재하는 파일들만 반환합니다."""
        return [f for f in self.get_all_files() if f.exists()]
