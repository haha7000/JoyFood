"""
Gmail API 인증 모듈
Gmail API 인증 및 서비스 빌드를 담당합니다.
"""
import os
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..utils.exceptions import AuthenticationError
from ..utils.logger import LoggerMixin

# 필요한 권한만: 읽기 전용
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailAuthenticator(LoggerMixin):
    """Gmail API 인증을 담당하는 클래스"""
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
    
    def authenticate(self) -> build:
        """
        Gmail API 인증을 수행합니다.
        
        Returns:
            Gmail API 서비스 객체
            
        Raises:
            AuthenticationError: 인증 실패 시
        """
        try:
            self.logger.info("Gmail API 인증 시작")
            
            creds = self._load_credentials()
            
            if not creds or not creds.valid:
                creds = self._refresh_or_create_credentials(creds)
            
            service = build("gmail", "v1", credentials=creds)
            self.logger.info("Gmail API 인증 완료")
            return service
            
        except Exception as e:
            self.logger.error(f"Gmail API 인증 실패: {e}")
            raise AuthenticationError(f"Gmail API 인증 실패: {e}")
    
    def _load_credentials(self) -> Optional[Credentials]:
        """저장된 인증 정보를 로드합니다."""
        if self.token_file.exists():
            try:
                return Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
            except Exception as e:
                self.logger.warning(f"토큰 파일 로드 실패: {e}")
        return None
    
    def _refresh_or_create_credentials(self, creds: Optional[Credentials]) -> Credentials:
        """인증 정보를 갱신하거나 새로 생성합니다."""
        if creds and creds.expired and creds.refresh_token:
            self.logger.info("토큰 갱신 중...")
            creds.refresh(Request())
        else:
            if not self.credentials_file.exists():
                raise AuthenticationError(f"인증 파일이 없습니다: {self.credentials_file}")
            
            self.logger.info("새로운 인증 정보 생성 중...")
            flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_file), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 토큰 저장
        self._save_credentials(creds)
        return creds
    
    def _save_credentials(self, creds: Credentials) -> None:
        """인증 정보를 저장합니다."""
        try:
            with self.token_file.open("w") as f:
                f.write(creds.to_json())
            self.logger.info(f"인증 정보 저장 완료: {self.token_file}")
        except Exception as e:
            self.logger.warning(f"인증 정보 저장 실패: {e}")


def build_gmail() -> build:
    """
    Gmail API 서비스를 빌드합니다.
    
    Returns:
        Gmail API 서비스 객체
    """
    authenticator = GmailAuthenticator()
    return authenticator.authenticate()