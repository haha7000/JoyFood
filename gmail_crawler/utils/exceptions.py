"""
커스텀 예외 클래스들.
"""


class GmailCrawlerError(Exception):
    """기본 예외 클래스"""
    pass


class AuthenticationError(GmailCrawlerError):
    """인증 관련 오류"""
    pass


class EmailNotFoundError(GmailCrawlerError):
    """이메일을 찾을 수 없을 때"""
    pass


class EmailExtractionError(GmailCrawlerError):
    """이메일 내용 추출 실패"""
    pass


class TableExtractionError(GmailCrawlerError):
    """테이블 추출 실패"""
    pass


class AIParsingError(GmailCrawlerError):
    """AI 파싱 실패"""
    pass


class FileProcessingError(GmailCrawlerError):
    """파일 처리 실패"""
    pass


class ConfigurationError(GmailCrawlerError):
    """설정 관련 오류"""
    pass


class ValidationError(GmailCrawlerError):
    """데이터 검증 실패"""
    pass
