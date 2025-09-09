"""
설정 관리 모듈
환경변수와 기본값을 통합 관리합니다.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()  # .env 파일 로드
except ImportError:
    # python-dotenv가 설치되지 않은 경우 무시
    pass


@dataclass
class Config:
    """애플리케이션 설정을 관리하는 클래스"""
    
    # Gmail 관련 설정
    sender_name: str = "이도한"  # 발신자 이름 또는 이메일 주소
    message_id: Optional[str] = None
    target_date: Optional[str] = None  # 특정 날짜의 메시지 처리 (YYYYMMDD 형식)
    max_results: int = 10
    
    # API 설정
    gemini_api_key: Optional[str] = None
    
    # 출력 설정
    output_dir: Path = Path("output")
    temp_dir: Path = Path("temp")
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    
    # HTML 캡처 설정
    device_scale_factor: int = 2
    full_page_capture: bool = True
    
    @classmethod
    def from_env(cls) -> "Config":
        """환경변수에서 설정을 로드합니다."""
        return cls(
            sender_name=os.environ.get("SENDER_NAME", "이도한"),
            message_id=os.environ.get("MESSAGE_ID"),
            target_date=os.environ.get("TARGET_DATE"),
            max_results=int(os.environ.get("MAX_RESULTS", "10")),
            gemini_api_key=os.environ.get("GEMINI_API_KEY"),
            output_dir=Path(os.environ.get("OUTPUT_DIR", "output")),
            temp_dir=Path(os.environ.get("TEMP_DIR", "temp")),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            log_file=Path(os.environ.get("LOG_FILE")) if os.environ.get("LOG_FILE") else None,
            device_scale_factor=int(os.environ.get("DEVICE_SCALE_FACTOR", "2")),
            full_page_capture=os.environ.get("FULL_PAGE_CAPTURE", "true").lower() == "true",
        )
    
    def ensure_directories(self) -> None:
        """필요한 디렉토리들을 생성합니다."""
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> None:
        """설정값의 유효성을 검증합니다."""
        if self.max_results <= 0:
            raise ValueError("max_results는 0보다 커야 합니다")
        
        if self.device_scale_factor <= 0:
            raise ValueError("device_scale_factor는 0보다 커야 합니다")
        
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"잘못된 로그 레벨: {self.log_level}")
