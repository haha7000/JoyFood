"""
설정 모듈 테스트
"""
import os
import tempfile
from pathlib import Path
import pytest

from gmail_crawler.core.config import Config


class TestConfig:
    """Config 클래스 테스트"""
    
    def test_default_config(self):
        """기본 설정 테스트"""
        config = Config()
        assert config.sender_name == "이도한"
        assert config.max_results == 10
        assert config.output_dir == Path("output")
        assert config.temp_dir == Path("temp")
        assert config.device_scale_factor == 2
        assert config.full_page_capture is True
    
    def test_from_env(self):
        """환경변수에서 설정 로드 테스트"""
        # 환경변수 설정
        os.environ["SENDER_NAME"] = "테스트발신자"
        os.environ["MAX_RESULTS"] = "5"
        os.environ["OUTPUT_DIR"] = "custom_output"
        os.environ["LOG_LEVEL"] = "DEBUG"
        
        try:
            config = Config.from_env()
            assert config.sender_name == "테스트발신자"
            assert config.max_results == 5
            assert config.output_dir == Path("custom_output")
            assert config.log_level == "DEBUG"
        finally:
            # 환경변수 정리
            for key in ["SENDER_NAME", "MAX_RESULTS", "OUTPUT_DIR", "LOG_LEVEL"]:
                os.environ.pop(key, None)
    
    def test_from_env_with_email(self):
        """이메일 주소로 설정 로드 테스트"""
        # 환경변수 설정
        os.environ["SENDER_NAME"] = "test@example.com"
        
        try:
            config = Config.from_env()
            assert config.sender_name == "test@example.com"
        finally:
            # 환경변수 정리
            os.environ.pop("SENDER_NAME", None)
    
    def test_ensure_directories(self):
        """디렉토리 생성 테스트"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(
                output_dir=Path(temp_dir) / "output",
                temp_dir=Path(temp_dir) / "temp"
            )
            
            config.ensure_directories()
            
            assert config.output_dir.exists()
            assert config.temp_dir.exists()
    
    def test_validate_success(self):
        """유효한 설정 검증 테스트"""
        config = Config()
        # 예외가 발생하지 않아야 함
        config.validate()
    
    def test_validate_invalid_max_results(self):
        """잘못된 max_results 검증 테스트"""
        config = Config(max_results=0)
        with pytest.raises(ValueError, match="max_results는 0보다 커야 합니다"):
            config.validate()
    
    def test_validate_invalid_device_scale_factor(self):
        """잘못된 device_scale_factor 검증 테스트"""
        config = Config(device_scale_factor=0)
        with pytest.raises(ValueError, match="device_scale_factor는 0보다 커야 합니다"):
            config.validate()
    
    def test_validate_invalid_log_level(self):
        """잘못된 log_level 검증 테스트"""
        config = Config(log_level="INVALID")
        with pytest.raises(ValueError, match="잘못된 로그 레벨"):
            config.validate()
