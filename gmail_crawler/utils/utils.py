"""
공통 유틸리티 함수들
애플리케이션 전반에서 사용되는 공통 기능들을 제공합니다.
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
from .exceptions import FileProcessingError, ValidationError


def save_html_file(content: str, filename: str, output_dir: Path) -> Path:
    """
    HTML 파일을 저장합니다.
    
    Args:
        content: HTML 내용
        filename: 파일명
        output_dir: 출력 디렉토리
        
    Returns:
        저장된 파일 경로
        
    Raises:
        FileProcessingError: 파일 저장 실패 시
    """
    try:
        output_dir.mkdir(exist_ok=True)
        file_path = output_dir / filename
        
        with file_path.open("w", encoding="utf-8") as f:
            f.write(content)
        
        return file_path
    except Exception as e:
        raise FileProcessingError(f"HTML 파일 저장 실패: {e}")


def create_table_html(tables_html: str) -> str:
    """
    테이블 HTML을 완전한 HTML 문서로 생성합니다.
    
    Args:
        tables_html: 테이블 HTML 내용
        
    Returns:
        완전한 HTML 문서
    """
    return (
        "<html><head><meta charset='utf-8'>"
        "<style>table{border-collapse:collapse;} td,th{border:1px solid #ccc;padding:4px;}</style>"
        "</head><body>"
        + tables_html +
        "</body></html>"
    )


def create_full_html(html_content: str) -> str:
    """
    HTML 내용을 완전한 HTML 문서로 생성합니다.
    
    Args:
        html_content: HTML 내용
        
    Returns:
        완전한 HTML 문서
    """
    return f"<html><head><meta charset='utf-8'></head><body>{html_content}</body></html>"


def save_json_file(data: Dict[str, Any], file_path: Path) -> None:
    """
    JSON 파일을 저장합니다.
    
    Args:
        data: 저장할 데이터
        file_path: 저장할 파일 경로
        
    Raises:
        FileProcessingError: 파일 저장 실패 시
    """
    try:
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise FileProcessingError(f"JSON 파일 저장 실패: {e}")


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    JSON 파일을 로드합니다.
    
    Args:
        file_path: 로드할 파일 경로
        
    Returns:
        로드된 데이터
        
    Raises:
        FileProcessingError: 파일 로드 실패 시
    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise FileProcessingError(f"JSON 파일 로드 실패: {e}")


def generate_timestamp() -> str:
    """
    현재 시간을 기반으로 타임스탬프를 생성합니다.
    
    Returns:
        타임스탬프 문자열 (YYYYMMDD_HHMMSS)
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def validate_file_exists(file_path: Path) -> None:
    """
    파일이 존재하는지 검증합니다.
    
    Args:
        file_path: 검증할 파일 경로
        
    Raises:
        ValidationError: 파일이 존재하지 않을 때
    """
    if not file_path.exists():
        raise ValidationError(f"파일이 존재하지 않습니다: {file_path}")


def clean_filename(filename: str) -> str:
    """
    파일명에서 안전하지 않은 문자를 제거합니다.
    
    Args:
        filename: 원본 파일명
        
    Returns:
        정리된 파일명
    """
    # 안전하지 않은 문자들을 언더스코어로 대체
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # 연속된 언더스코어를 하나로 정리
    while '__' in filename:
        filename = filename.replace('__', '_')
    
    return filename.strip('_')


def ensure_directory_exists(directory: Path) -> None:
    """
    디렉토리가 존재하지 않으면 생성합니다.
    
    Args:
        directory: 생성할 디렉토리 경로
    """
    directory.mkdir(parents=True, exist_ok=True)


def parse_date_from_subject(subject: str) -> Optional[str]:
    """
    제목에서 날짜를 추출합니다.
    
    Args:
        subject: 이메일 제목
        
    Returns:
        추출된 날짜 문자열 (YYYYMMDD 형식) 또는 None
    """
    import re
    from datetime import datetime
    
    # 패턴 1: "2025년09월04일" 형식
    pattern1 = r'(\d{4})년(\d{1,2})월(\d{1,2})일'
    match1 = re.search(pattern1, subject)
    if match1:
        year, month, day = match1.groups()
        return f"{year}{month.zfill(2)}{day.zfill(2)}"
    
    # 패턴 2: "20250902" 형식 (8자리 숫자)
    pattern2 = r'(\d{8})'
    match2 = re.search(pattern2, subject)
    if match2:
        date_str = match2.group(1)
        # 유효한 날짜인지 확인
        try:
            datetime.strptime(date_str, '%Y%m%d')
            return date_str
        except ValueError:
            pass
    
    # 패턴 3: "09월04일" 형식 (올해 기준)
    pattern3 = r'(\d{1,2})월(\d{1,2})일'
    match3 = re.search(pattern3, subject)
    if match3:
        month, day = match3.groups()
        current_year = datetime.now().year
        return f"{current_year}{month.zfill(2)}{day.zfill(2)}"
    
    return None


def find_message_by_date(messages_data: List[Dict[str, Any]], target_date: str) -> Optional[Dict[str, Any]]:
    """
    메시지 목록에서 특정 날짜의 메시지를 찾습니다.
    
    Args:
        messages_data: 메시지 데이터 목록 (제목과 날짜 포함)
        target_date: 찾을 날짜 (YYYYMMDD 형식)
        
    Returns:
        해당 날짜의 메시지 데이터 또는 None
    """
    for msg_data in messages_data:
        subject = msg_data.get('subject', '')
        parsed_date = parse_date_from_subject(subject)
        
        if parsed_date == target_date:
            return msg_data
    
    return None


def find_latest_message(messages_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    메시지 목록에서 가장 최신 메시지를 찾습니다.
    
    Args:
        messages_data: 메시지 데이터 목록 (제목과 날짜 포함)
        
    Returns:
        가장 최신 메시지 데이터 또는 None
    """
    if not messages_data:
        return None
    
    # 날짜별로 정렬 (최신순)
    sorted_messages = sorted(
        messages_data,
        key=lambda x: parse_date_from_subject(x.get('subject', '')) or '00000000',
        reverse=True
    )
    
    return sorted_messages[0]
