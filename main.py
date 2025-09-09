"""
Gmail 테이블 추출기 메인 모듈
리팩토링된 버전의 메인 실행 파일입니다.
"""
import sys
from pathlib import Path

from gmail_crawler.core.config import Config
from gmail_crawler.core.workflow import GmailTableExtractor
from gmail_crawler.utils.logger import setup_logger
from gmail_crawler.utils.exceptions import GmailCrawlerError


def main():
    """메인 실행 함수"""
    try:
        # 설정 로드
        config = Config.from_env()
        config.validate()
        
        # 로거 설정
        logger = setup_logger("GmailTableExtractor", config)
        logger.info("Gmail 테이블 추출기 시작")
        
        # 워크플로우 실행
        extractor = GmailTableExtractor(config)
        result = extractor.run(config.target_date)
        
        # 결과 출력
        if result.success:
            logger.info(f"성공: {result.message}")
            if result.output_files:
                logger.info(f"생성된 파일들: {[str(f) for f in result.output_files]}")
            if result.processing_time:
                logger.info(f"처리 시간: {result.processing_time:.2f}초")
        else:
            logger.error(f"실패: {result.message}")
            if result.error:
                logger.error(f"오류 상세: {result.error}")
            sys.exit(1)
            
    except GmailCrawlerError as e:
        print(f"애플리케이션 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


