"""
HTML을 이미지로 변환하는 모듈
Playwright를 사용하여 HTML을 PNG 이미지로 캡처합니다.
"""
from pathlib import Path
from typing import Optional

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

from ..utils.exceptions import FileProcessingError
from ..utils.logger import LoggerMixin


class HTMLToImageConverter(LoggerMixin):
    """HTML을 이미지로 변환하는 클래스"""
    
    def __init__(self):
        if sync_playwright is None:
            raise RuntimeError(
                "Playwright가 설치되어 있지 않습니다. "
                "venv에서 'playwright install chromium'을 먼저 실행하세요."
            )
    
    def capture_html_to_png(
        self, 
        html_path: Path, 
        out_png: Optional[Path] = None, 
        *, 
        full_page: bool = True, 
        device_scale_factor: int = 2
    ) -> Path:
        """
        HTML 파일을 PNG 이미지로 캡처합니다.
        
        Args:
            html_path: HTML 파일 경로
            out_png: 출력 PNG 파일 경로 (None이면 자동 생성)
            full_page: 전체 페이지 캡처 여부
            device_scale_factor: 디바이스 스케일 팩터
            
        Returns:
            생성된 PNG 파일 경로
            
        Raises:
            FileProcessingError: 이미지 생성 실패 시
        """
        try:
            if not html_path.exists():
                raise FileNotFoundError(f"HTML 파일이 존재하지 않습니다: {html_path}")
            
            self.logger.info(f"HTML을 이미지로 변환 시작: {html_path}")
            
            html_uri = html_path.resolve().as_uri()
            if out_png is None:
                out_png = html_path.with_suffix(".png")

            with sync_playwright() as p:
                browser = p.chromium.launch()
                context = browser.new_context(device_scale_factor=device_scale_factor)
                page = context.new_page()
                page.goto(html_uri, wait_until="load")
                page.screenshot(path=str(out_png), full_page=full_page)
                browser.close()
            
            self.logger.info(f"이미지 저장 완료: {out_png}")
            return out_png
            
        except Exception as e:
            self.logger.error(f"이미지 생성 실패: {e}")
            raise FileProcessingError(f"이미지 생성 실패: {e}")


# 하위 호환성을 위한 함수
def capture_html_to_png(
    html_path: Path, 
    out_png: Optional[Path] = None, 
    *, 
    full_page: bool = True, 
    device_scale_factor: int = 2
) -> Path:
    """하위 호환성을 위한 함수"""
    converter = HTMLToImageConverter()
    return converter.capture_html_to_png(html_path, out_png, full_page=full_page, device_scale_factor=device_scale_factor)


if __name__ == "__main__":
    # 기본 CLI 사용: 기존 파일명을 기본값으로 사용
    default_html = Path("selected_email_tables.html")
    if default_html.exists():
        try:
            capture_html_to_png(default_html)
        except Exception as e:
            print(f"오류 발생: {e}")
    else:
        print("기본 HTML 파일이 없습니다: selected_email_tables.html")