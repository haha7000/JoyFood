"""
pytest 설정 및 공통 픽스처
"""
import tempfile
from pathlib import Path
import pytest

from gmail_crawler.core.config import Config


@pytest.fixture
def temp_config():
    """임시 설정 픽스처"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Config(
            output_dir=Path(temp_dir) / "output",
            temp_dir=Path(temp_dir) / "temp"
        )
        config.ensure_directories()
        yield config


@pytest.fixture
def sample_html_content():
    """샘플 HTML 내용 픽스처"""
    return """
    <html>
    <head><meta charset='utf-8'></head>
    <body>
        <h1>테스트 이메일</h1>
        <table>
            <tr><th>열1</th><th>열2</th></tr>
            <tr><td>값1</td><td>값2</td></tr>
            <tr><td>값3</td><td>값4</td></tr>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_table_data():
    """샘플 테이블 데이터 픽스처"""
    return {
        "tables": [
            {
                "headers": ["열1", "열2"],
                "rows": [
                    ["값1", "값2"],
                    ["값3", "값4"]
                ]
            }
        ]
    }
