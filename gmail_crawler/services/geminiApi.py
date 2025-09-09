"""
Gemini API 모듈
Google Gemini API를 사용하여 이미지에서 테이블을 추출합니다.
"""
import os
import getpass
import json
import base64
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any

from google import genai

from ..utils.exceptions import AIParsingError, ConfigurationError
from ..utils.logger import LoggerMixin


class GeminiAPIClient(LoggerMixin):
    """Gemini API 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._get_api_key()
        self.client = genai.Client(api_key=self.api_key)
    
    def _get_api_key(self) -> str:
        """
        API 키를 가져옵니다.
        
        Returns:
            API 키
            
        Raises:
            ConfigurationError: API 키를 찾을 수 없을 때
        """
        # 1) 환경변수 우선
        key = os.environ.get("GEMINI_API_KEY")
        if key:
            return key.strip()

        # 2) 직접 입력(콘솔 비노출)
        key = getpass.getpass("Enter Gemini API key: ").strip()
        if not key:
            raise ConfigurationError("API key is required.")
        return key


    def table_image_to_json(self, image_path: str | Path) -> Dict[str, Any]:
        """
        이미지(표)를 Gemini에 입력하여 표를 JSON으로 추출합니다.
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            추출된 테이블 데이터 ({"tables": [{"headers": [...], "rows": [[...], ...]}]})
            
        Raises:
            AIParsingError: 파싱 실패 시
        """
        p = Path(image_path)
        if not p.exists():
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {p}")

        try:
            self.logger.info(f"이미지에서 테이블 추출 시작: {p}")
            
            mime, _ = mimetypes.guess_type(str(p))
            if mime is None:
                mime = "image/png"

            image_bytes = p.read_bytes()
            b64 = base64.b64encode(image_bytes).decode("ascii")

            prompt = (
                "You are an expert at table extraction. "
                "Extract ALL tables from the provided image and return STRICT JSON only. "
                "Do not include any commentary. Schema: {\n"
                "  \"tables\": [ { \n"
                "    \"headers\": [string, ...], \n"
                "    \"rows\": [ [string|null, ...], ... ] \n"
                "  } ]\n"
                "}. Use null for empty cells."
            )

            config = {
                "response_mime_type": "application/json",
                "temperature": 0.2,
            }

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": mime, "data": b64}},
                        ],
                    }
                ],
                config=config,
            )

            text = response.text or "{}"
            result = self._parse_json_response(text)
            
            self.logger.info("테이블 추출 완료")
            return result
            
        except Exception as e:
            self.logger.error(f"테이블 추출 실패: {e}")
            raise AIParsingError(f"테이블 추출 실패: {e}")
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """
        Gemini 응답에서 JSON을 파싱합니다.
        
        Args:
            text: Gemini 응답 텍스트
            
        Returns:
            파싱된 JSON 객체
            
        Raises:
            AIParsingError: JSON 파싱 실패 시
        """
        # 코드펜스 제거 등 방어적 처리
        text = text.strip()
        if text.startswith("```"):
            # ```json ... ``` 형태 제거
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 마지막 시도: 중괄호 범위 추출
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start : end + 1])
            else:
                raise AIParsingError("JSON 파싱 실패: 유효한 JSON을 찾을 수 없습니다")


# 하위 호환성을 위한 함수들
def get_api_key() -> str:
    """하위 호환성을 위한 함수"""
    client = GeminiAPIClient()
    return client.api_key

def table_image_to_json(image_path: str | Path, api_key: str | None = None) -> Dict[str, Any]:
    """하위 호환성을 위한 함수"""
    client = GeminiAPIClient(api_key)
    return client.table_image_to_json(image_path)

def main():
    """하위 호환성을 위한 메인 함수"""
    try:
        client = GeminiAPIClient()
        response = client.client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Explain how AI works in a few words",
        )
        print(response.text)
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()  