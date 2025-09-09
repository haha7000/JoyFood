"""
JSON 테이블 데이터를 Excel 파일로 변환하는 모듈
"""
import json
from pathlib import Path
from typing import Any, List, Optional

import pandas as pd

from ..utils.exceptions import FileProcessingError, ValidationError
from ..utils.logger import LoggerMixin


class JSONToExcelConverter(LoggerMixin):
    """JSON 테이블 데이터를 Excel로 변환하는 클래스"""
    
    def __init__(self):
        pass
    
    def _normalize_rows(self, rows: List[List[Any]], num_cols: int) -> List[List[Any]]:
        """
        행 데이터를 정규화합니다.
        
        Args:
            rows: 원본 행 데이터
            num_cols: 목표 열 개수
            
        Returns:
            정규화된 행 데이터
        """
        normalized: List[List[Any]] = []
        for row in rows:
            normalized_row = list(row)
            if len(normalized_row) < num_cols:
                normalized_row.extend([None] * (num_cols - len(normalized_row)))
            elif len(normalized_row) > num_cols:
                normalized_row = normalized_row[:num_cols]
            normalized.append(normalized_row)
        return normalized
    
    def json_tables_to_excel(self, json_path: str | Path, out_xlsx: Optional[str | Path] = None) -> Path:
        """
        JSON 테이블 데이터를 Excel 파일로 변환합니다.
        
        Args:
            json_path: JSON 파일 경로
            out_xlsx: 출력 Excel 파일 경로 (None이면 자동 생성)
            
        Returns:
            생성된 Excel 파일 경로
            
        Raises:
            FileProcessingError: 파일 처리 실패 시
            ValidationError: 데이터 검증 실패 시
        """
        try:
            json_file = Path(json_path)
            if not json_file.exists():
                raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {json_file}")
            
            self.logger.info(f"JSON을 Excel로 변환 시작: {json_file}")
            
            # JSON 데이터 로드
            data = json.loads(json_file.read_text(encoding="utf-8"))
            tables = data.get("tables") or []
            
            if not isinstance(tables, list) or not tables:
                raise ValidationError("JSON에 tables 항목이 없거나 비어있습니다.")
            
            # 출력 파일 경로 설정
            if out_xlsx is None:
                out_xlsx = json_file.with_suffix(".xlsx")
            out_path = Path(out_xlsx)
            
            # Excel 파일 생성
            with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
                for idx, table in enumerate(tables, start=1):
                    headers = table.get("headers") or []
                    rows = table.get("rows") or []
                    
                    # 열 개수 결정: 헤더 우선, 없으면 최대 행 길이
                    num_cols = len(headers) if headers else max((len(r) for r in rows), default=0)
                    rows_norm = self._normalize_rows(rows, num_cols)
                    
                    # 헤더 정규화
                    if headers and len(headers) != num_cols:
                        headers = headers[:num_cols]
                    
                    if not headers:
                        headers = [f"col_{i+1}" for i in range(num_cols)]
                    
                    # DataFrame 생성 및 저장
                    df = pd.DataFrame(rows_norm, columns=headers)
                    sheet_name = f"Table{idx}"
                    df.to_excel(writer, index=False, sheet_name=sheet_name)
                    
                    self.logger.info(f"테이블 {idx} 변환 완료: {len(rows_norm)}행, {len(headers)}열")
            
            self.logger.info(f"Excel 저장 완료: {out_path}")
            return out_path
            
        except Exception as e:
            self.logger.error(f"Excel 변환 실패: {e}")
            raise FileProcessingError(f"Excel 변환 실패: {e}")


# 하위 호환성을 위한 함수
def json_tables_to_excel(json_path: str | Path, out_xlsx: Optional[str | Path] = None) -> Path:
    """하위 호환성을 위한 함수"""
    converter = JSONToExcelConverter()
    return converter.json_tables_to_excel(json_path, out_xlsx)


