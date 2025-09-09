"""
로깅 시스템 모듈
애플리케이션 전반에 걸친 로깅을 관리합니다.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from ..core.config import Config


def setup_logger(name: str, config: Config) -> logging.Logger:
    """
    로거를 설정하고 반환합니다.
    
    Args:
        name: 로거 이름
        config: 설정 객체
        
    Returns:
        설정된 로거
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.log_level.upper()))
    
    # 이미 핸들러가 설정되어 있으면 중복 설정 방지
    if logger.handlers:
        return logger
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (설정된 경우)
    if config.log_file:
        file_handler = logging.FileHandler(config.log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    기존 로거를 가져옵니다.
    
    Args:
        name: 로거 이름
        
    Returns:
        로거
    """
    return logging.getLogger(name)


class LoggerMixin:
    """로깅 기능을 제공하는 믹스인 클래스"""
    
    @property
    def logger(self) -> logging.Logger:
        """클래스별 로거를 반환합니다."""
        return get_logger(self.__class__.__name__)
