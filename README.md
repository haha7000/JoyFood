# 푸드코아 수주관리 - 샌드팜, 삼립

Gmail 이메일에서 테이블 데이터를 자동으로 추출하여 Excel 파일로 변환하는 도구입니다. Google Gemini AI를 사용하여 이미지에서 테이블을 인식하고 구조화된 데이터로 변환합니다.

## ✨ 주요 기능

- **Gmail API 연동**: Gmail에서 이메일을 자동으로 가져옵니다
- **테이블 자동 인식**: HTML 테이블을 자동으로 감지하고 추출합니다
- **AI 기반 파싱**: Google Gemini AI를 사용하여 이미지에서 테이블을 정확하게 인식합니다
- **Excel 변환**: 추출된 테이블을 Excel 파일로 자동 변환합니다
- **로깅 시스템**: 상세한 로그를 통해 처리 과정을 추적할 수 있습니다
- **설정 관리**: 환경변수를 통한 유연한 설정 관리

## 🏗️ 아키텍처

리팩토링된 코드는 다음과 같은 모듈 구조를 가집니다:

```
GmailCrawler/
├── main.py                      # 실행 파일
├── gmail_crawler/               # 메인 패키지
│   ├── core/                    # 핵심 기능
│   │   ├── config.py           # 설정 관리
│   │   └── workflow.py         # 메인 워크플로우
│   ├── services/               # 서비스 계층
│   │   ├── gmail_auth.py       # Gmail API 인증
│   │   ├── read_body.py        # 이메일 내용 추출
│   │   ├── html_to_image.py    # HTML → 이미지 변환
│   │   ├── geminiApi.py        # Gemini AI 연동
│   │   └── json_to_excel.py    # JSON → Excel 변환
│   ├── models/                 # 데이터 모델
│   │   └── models.py           # 데이터 구조 정의
│   └── utils/                  # 공통 유틸리티
│       ├── logger.py           # 로깅 시스템
│       ├── exceptions.py       # 커스텀 예외
│       └── utils.py            # 공통 함수
└── tests/                      # 테스트 코드
    ├── test_config.py
    ├── test_utils.py
    ├── test_models.py
    └── conftest.py
```

## 🚀 설치 및 설정

### 1. 의존성 설치

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 패키지 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### 2. Gmail API 설정

Gmail API를 사용하기 위해서는 Google Cloud 프로젝트 설정과 OAuth 2.0 인증이 필요합니다.

#### 사전 요구사항
- Python 3.10.7 이상
- Gmail이 활성화된 Google 계정
- Google Cloud 프로젝트

#### 단계별 설정 방법

**① Google Cloud 프로젝트 생성 및 Gmail API 활성화**
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트를 생성하거나 기존 프로젝트 선택
3. 검색창에서 "Gmail API"를 검색하여 활성화

**② OAuth 동의 화면 구성**
1. 좌측 메뉴에서 "Google Auth platform" > "브랜딩" 이동
2. 앱 이름과 지원 이메일 설정
3. 사용자 유형을 "내부" 또는 "외부" 선택 (개인용은 "외부" 권장)
4. 필요한 정보를 입력하여 동의 화면 구성 완료

**③ OAuth 2.0 클라이언트 ID 생성**
1. 좌측 메뉴에서 "Google Auth platform" > "사용자 인증 정보" 이동
2. "+ 사용자 인증 정보 만들기" → "OAuth 클라이언트 ID" 선택
3. 애플리케이션 유형을 "데스크톱 애플리케이션" 선택
4. 이름을 입력하고 "만들기" 클릭
5. **중요**: 생성된 클라이언트의 JSON 파일을 다운로드
6. 다운로드한 파일을 프로젝트 루트 디렉토리에 `credentials.json`으로 저장

**④ 첫 실행 및 토큰 생성**
- 처음 실행 시 브라우저에서 Google 로그인 및 권한 승인 필요
- 승인 완료 후 `token.json` 파일이 자동으로 생성됨
- 이후 실행부터는 자동으로 인증됨

```bash
# 첫 실행 시 브라우저에서 인증 진행
python main.py
# → Google 로그인 페이지가 열리고 권한 승인 후 token.json 생성
```

#### 파일 구조
```
GmailCrawler/
├── credentials.json    # OAuth 2.0 클라이언트 정보 (직접 다운로드)
├── token.json         # 인증 토큰 (첫 실행 시 자동 생성)
└── ...
```

#### 권한 범위
이 도구는 Gmail 읽기 전용 권한만 사용합니다:
- `https://www.googleapis.com/auth/gmail.readonly`

#### 보안 주의사항
⚠️ **중요**: 다음 파일들은 민감한 정보를 포함하므로 절대 공유하지 마세요:
- `credentials.json`: OAuth 2.0 클라이언트 정보
- `token.json`: 인증 토큰 정보
- `.env`: API 키 및 설정 정보

이 파일들은 `.gitignore`에 포함되어 버전 관리에서 자동 제외됩니다.

### 3. Gemini API 설정

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키 생성
2. 환경변수 설정:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

## 📖 사용법

### 기본 사용법

```bash
# 가장 최신 메시지 처리
python main.py

# 특정 날짜의 메시지 처리
TARGET_DATE="20250904" python main.py

# 특정 발신자의 특정 날짜 메시지 처리
SENDER_NAME="AA@naver.com" TARGET_DATE="20250904" python main.py
```

### 날짜 설정 기능

이 도구는 이메일 제목에서 날짜를 자동으로 인식하고 특정 날짜의 메시지를 찾을 수 있습니다.

#### 지원하는 날짜 형식
- **한글 형식**: "2025년09월04일", "09월04일" (현재 연도 자동 추가)
- **숫자 형식**: "20250904" (8자리 YYYYMMDD)

#### 날짜 기반 메시지 선택
```bash
# 특정 날짜의 메시지 처리 (YYYYMMDD 형식)
TARGET_DATE="20250904" python main.py

# 또는 .env 파일에 설정
echo "TARGET_DATE=20250904" >> .env
python main.py
```

#### 날짜 설정 우선순위
1. **MESSAGE_ID가 설정된 경우**: 특정 메시지 ID로 직접 처리
2. **TARGET_DATE가 설정된 경우**: 해당 날짜의 메시지를 검색하여 처리
3. **기본값**: 발신자의 가장 최신 메시지 처리

#### 예시 시나리오
```bash
# 시나리오 1: 2025년 9월 4일 메시지 처리
TARGET_DATE="20250904" python main.py

# 시나리오 2: 특정 이메일 주소의 2025년 9월 4일 메시지
SENDER_NAME="sender@naver.net" TARGET_DATE="20250904" python main.py

# 시나리오 3: 가장 최신 메시지 (날짜 설정 없음)
SENDER_NAME="sender@naver.net" python main.py
```

### 환경변수 설정

```bash
# 발신자 이름 또는 이메일 주소 설정
export SENDER_NAME="홍길동"  # 또는 "sender@example.com"

# 특정 메시지 ID로 처리 (SENDER_NAME보다 우선)
export MESSAGE_ID="message_id_here"

# 특정 날짜의 메시지 처리 (YYYYMMDD 형식)
export TARGET_DATE="20250904"

# 출력 디렉토리 설정
export OUTPUT_DIR="custom_output"

# 로그 레벨 설정
export LOG_LEVEL="DEBUG"

# 최대 결과 수 설정
export MAX_RESULTS="5"
```

### 프로그래밍 방식 사용

```python
from gmail_crawler.core.config import Config
from gmail_crawler.core.workflow import GmailTableExtractor
from gmail_crawler.utils.logger import setup_logger

# 설정 로드
config = Config.from_env()
config.validate()

# 로거 설정
logger = setup_logger("GmailTableExtractor", config)

# 워크플로우 실행
extractor = GmailTableExtractor(config)
result = extractor.run()

if result.success:
    print(f"성공: {result.message}")
    print(f"생성된 파일들: {result.output_files}")
else:
    print(f"실패: {result.message}")
```

## 🔧 설정 옵션

| 환경변수 | 기본값 | 설명 |
|---------|--------|------|
| `SENDER_NAME` | "홍길동" | 검색할 발신자 이름 또는 이메일 주소 |
| `MESSAGE_ID` | None | 특정 메시지 ID (설정 시 우선 사용) |
| `TARGET_DATE` | None | 특정 날짜의 메시지 처리 (YYYYMMDD 형식) |
| `MAX_RESULTS` | 10 | 최대 검색 결과 수 |
| `GEMINI_API_KEY` | None | Gemini API 키 |
| `OUTPUT_DIR` | "output" | 출력 디렉토리 |
| `TEMP_DIR` | "temp" | 임시 파일 디렉토리 |
| `LOG_LEVEL` | "INFO" | 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_FILE` | None | 로그 파일 경로 |
| `DEVICE_SCALE_FACTOR` | 2 | 이미지 캡처 해상도 |
| `FULL_PAGE_CAPTURE` | true | 전체 페이지 캡처 여부 |

## 🧪 테스트

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 실행
pytest tests/test_config.py

# 커버리지와 함께 실행
pytest --cov=. --cov-report=html
```

## 📁 출력 파일

처리 완료 후 `output/` 디렉토리에 다음 파일들이 생성됩니다:

- `[발신자]_[타임스탬프].html`: 원본 이메일 HTML
- `[발신자]_[타임스탬프].png`: HTML을 이미지로 변환한 파일  
- `[발신자]_[타임스탬프].json`: AI가 추출한 테이블 데이터
- `[발신자]_[타임스탬프].xlsx`: 최종 Excel 파일

### 디렉토리 구조
- **`output/`**: 최종 결과 파일들이 저장되는 디렉토리

## 🔍 로깅

애플리케이션은 상세한 로그를 제공합니다:

- **INFO**: 일반적인 처리 과정
- **WARNING**: 주의가 필요한 상황
- **ERROR**: 오류 발생 시
- **DEBUG**: 디버깅 정보

로그는 콘솔과 파일(설정된 경우)에 동시에 출력됩니다.


## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.
