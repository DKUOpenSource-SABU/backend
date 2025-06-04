# Backend (Fast API)

이 디렉토리는 서버 로직과 데이터 처리를 담당하는 **백엔드 서비스**입니다.  
API 요청 처리, 데이터 수집, 서비스 로직 수행 등을 처리합니다.

## 🔧 기술 스택
- Python Fast API
- JavaScript Puppeteer
- REST API
- Swagger 문서화

## 📁 폴더 구조

```bash
📦 backend/
 ┣ 📂 .github/ISSUE_TEMPLATE/   # 이슈 템플릿 정의
 ┣ 📂 api/                      # 외부 API 호출 및 라우팅 서브모듈
 ┣ 📂 backtest/                 # 백테스트 핵심 로직 및 전략 모듈
 ┣ 📂 clustering/               # 종목 클러스터링 로직
 ┣ 📂 collect/                  # 데이터 수집 모듈
 ┣ 📂 core/                     # 인메모리 db 처리
 ┣ 📂 data/                     # 데이터 보관
 ┣ 📂 models/                   # request/response 모델 정의
 ┣ 📂 routers/                  # FastAPI 라우터 모음
 ┣ 📂 docs/                     # 프로젝트 문서, 컨벤션 모음
 ┣ 📂 test/                     # 유닛 테스트 코드
 ┣ 📜 main.py                   # FastAPI 진입점
 ┣ 📜 requirements.txt          # 종속성 패키지 정의
 ┣ 📜 Dockerfile                # Docker 배포용 설정 파일
 ┣ 📜 .gitignore                # Git 버전관리 제외 파일 목록
 ┗ 📜 README.md                 # 프로젝트 소개 및 실행 방법
```

## 📂 `docs/` 폴더 내 문서 목록

- 📘 **[API 명세서](./docs/API_spec.md)**  
  REST API 경로, 파라미터, 응답 예시 등 상세 명세

- 🚀 **[배포 문서](./docs/deployment.md)**  
  서버 실행 방식, CI/CD 흐름 및 운영 환경 구성 설명

- 🧱 **[아키텍처 문서](./docs/architecture/architecture.md)**  
  시스템 전체 구성도 및 백엔드 내부 흐름 구조화 설명

## 🛠️ 실행 전 준비사항

- `.env` 파일 또는 환경 변수 설정이 필요합니다:

```env
TIINGO_TOKEN="tiingo_token"
```

- `data/stock` 폴더 내에 종목 CSV 파일이 있어야 백테스트, 클러스터링 기능이 정상 동작합니다.

## 배포 방식

FastAPI 기반 백엔드 서비스는 **다양한 환경에서 유연하게 배포**될 수 있도록 설계되었습니다.  
아래는 사용 가능한 3가지 대표 배포 방식입니다.

## 1. 단일 스레드 배포 (Uvicorn 단독 실행)

가장 단순한 배포 방식으로, **테스트 환경** 또는 **개발 초기 단계**에서 사용하기 적합합니다.

### ✅ 실행 명령어

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 2. 멀티 스레드 / 프로세스 배포 (Gunicorn + Uvicorn worker)

프로덕션 환경에 적합한 방식으로, 여러 워커를 통해 고부하 트래픽을 처리할 수 있습니다.

### ✅ 실행 명령어

``` bash
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

## 3. Docker 기반 배포

### ✅ 실행 명령어
```bash
# 이미지 빌드
docker build -t my-sabu-app .

# 컨테이너 실행
docker run -d -p 8000:8000 my-sabu-app
```

## 📦 사용한 주요 오픈소스 및 버전 요약

### 🐍 Python 런타임
- **Python**: 3.9 이상

---

### 🚀 핵심 백엔드 프레임워크
| 라이브러리     | 버전       | 설명                                  |
|----------------|------------|---------------------------------------|
| FastAPI        | 0.115.12   | 비동기 Python 웹 프레임워크           |
| Uvicorn        | 0.34.2     | ASGI 서버, FastAPI 실행용             |
| Gunicorn       | 23.0.0     | 멀티 프로세스 기반 프로덕션 서버     |

---
### 📊 데이터 처리 및 ML
| 라이브러리     | 버전       | 설명                            |
|----------------|------------|---------------------------------|
| numpy          | 2.0.2      | 수치 연산                       |
| pandas         | 2.2.3      | 데이터프레임 처리               |
| scikit-learn   | 1.6.1      | 머신러닝 알고리즘 및 평가도구  |
| scipy          | 1.13.1     | 과학 계산 라이브러리           |

---

### 🤖 딥러닝 & NLP
| 라이브러리     | 버전       | 설명                            |
|----------------|------------|---------------------------------|
| torch          | 2.7.0      | PyTorch 딥러닝 프레임워크       |
| transformers   | 4.52.3     | Hugging Face 트랜스포머 모델   |

---

### 🧪 기타 유틸리티
| 라이브러리     | 버전       | 설명                            |
|----------------|------------|---------------------------------|
| requests       | 2.32.3     | HTTP 요청 처리 라이브러리       |
| playwrighᴛ     | 1.52.0     | 웹 데이터 크롤링 및 자동화 도구 |

---

## 🧪 부하 테스트 (k6)

본 프로젝트는 **API의 안정성과 성능을 검증**하기 위해 [k6](https://k6.io/)를 사용한 부하 테스트를 수행했습니다.

### ✅ 테스트 목적

- API 응답 지연 확인 및 병목 구간 파악
- 실제 사용자를 가정한 시나리오 기반 스트레스 테스트
- 병렬 요청 처리 시 FastAPI + Gunicorn 성능 검증

### ✅ k6 설치 방법

```bash
# MacOS
brew install k6

# Ubuntu
sudo apt install k6
```

### 테스트 방법
```bash
k6 run test/{testfile}.js
```