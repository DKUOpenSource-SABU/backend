# 🧱 아키텍처 문서: 백테스팅 시스템

## 시스템 구성도

![architecture_image.png](%E1%84%8C%E1%85%A6%E1%84%86%E1%85%A9%E1%86%A8%20%E1%84%8B%E1%85%A5%E1%86%B9%E1%84%8B%E1%85%B3%E1%86%B7%./architecture_image.png)

---

## 구성 요소 상세 설명

### 1. `routers/` – 라우팅 진입점

- FastAPI의 엔드포인트들을 등록하는 최상위 모듈
- `/backtest/`, `/cluster/`, `/collect/` 등 실제 라우팅 구조 정의

### 2. `backtest/` – 전략 실행 핵심

- 전략별 로직이 독립된 모듈로 구현: `buy_and_hold.py`, `rsi.py`, `sma_cross.py`
- 입력된 포트폴리오와 전략에 따라 백테스트 실행
- 결과로 총 수익률, CAGR, MDD, 월별 수익률 등을 반환

### 3. `clustering/` – 종목 분석 및 추천

- 선택 종목에 대한 KMeans 클러스터링 수행
- 클러스터 기반 유사 종목 추천, 점수 산정 API 제공
- 시각화를 위한 Convex Hull 좌표 반환

### 4. `api/` – 외부 데이터 수집 및 분석 API

- `tiingo.py`: Tiingo 시세 데이터 수집 + 캐싱
- `finBERT.py`: 금융 뉴스에 대한 감정 분석 수행 (긍정/부정/중립)

### 5. `collect/` – 종목 검색 및 시세/뉴스 수집

- `collect_ticker.py`: 키워드 기반 ETF 종목 검색
- `tiingo_api.py`: Tiingo API 기반 시세 수집 기능 (일간/주간/월간 등)
- `vantage_api.py`: Vantage API 기반 시세 대체 수집 기능
- `nasdaq-download.js`: 나스닥 상장 종목 목록 수집용 스크립트 (크롤링)
- `idx.lc`, `package.json`: 수집 환경 구성 및 실행 스크립트 정의

### 6. `core/` – 인프라/유틸리티

- `db.py`: CSV 기반 초기 데이터 로딩 및 병합

### 7. `models/` – 데이터 구조 정의

- 모든 API 요청/응답에 대한 Pydantic 기반 schema 명세

### 8. `test/` – 단위 테스트

- 전략, 분석기, 데이터 처리 등 기능별 검증 코드 작성 위치

---

## 📦 디렉토리 구조

```
backend/
 ┣ 📂 .github/ISSUE_TEMPLATE/   # 이슈 템플릿 정의
 ┣ 📂 api/                      # 시세 수집(Tiingo), 감정 분석(FinBERT)
 ┣ 📂 backtest/                 # 백테스트 전략 구현 (Buy&Hold, RSI, SMA)
 ┣ 📂 clustering/               # 클러스터링 분석 및 추천 알고리즘
 ┣ 📂 collect/                  # 종목 검색, ETF 메타데이터, 뉴스 API
 ┣ 📂 core/                     # DB 초기화 및 공통 유틸리티
 ┣ 📂 data/                     # 예시 CSV 데이터 저장 경로
 ┣ 📂 models/                   # Pydantic 기반 요청/응답 schema
 ┣ 📂 routers/                  # API 라우터 등록 모듈
 ┣ 📂 docs/                     # 아키텍처, API 명세서, 배포 문서 등
 ┣ 📂 test/                     # 유닛 테스트 코드
 ┣ 📜 main.py                   # FastAPI 진입점 (라우터 포함)
 ┣ 📜 requirements.txt          # 종속성 명세
 ┣ 📜 Dockerfile                # Docker 설정
 ┣ 📜 .gitignore                # Git 제외 항목
 ┗ 📜 README.md                 # 프로젝트 개요 및 실행법
```

---

## 💡 실제 시스템 흐름 (프론트 기준)

```
flowchart TD
    A[Frontend] --> B[Routers]
    B --> C1[/collect/]
    B --> C2[/cluster/]
    B --> C3[/backtest/]

    C1 --> D1[Collect
collect_ticker.py
tiingo_api.py]
    C2 --> D2[Clustering
kmeans_module.py
diversification_score.py
recommend.py]
    C3 --> D3[Backtest
backtest_runner.py
buy_and_hold.py
rsi.py
sma_cross.py]
```

---

## 🧱 설계 기준

- FastAPI 기반 RESTful 구조로 모든 기능 통합
- 전략 실행, 감정 분석, 시세 수집, 클러스터링 전부 단일 서버에서 처리
- 기능별 디렉토리 분리로 유지보수성과 확장성 확보
- 실제 실행 구조에 맞춰 API 문서화 및 기능 분리 구현

---

## 🚀 향후 개선 방향

- 전략 결과 저장 및 분석을 위한 DB 구축 (PostgreSQL 등)
- 사용자 맞춤 전략 업로드/저장 기능
- 종목 확장 (ETF 외 개별 종목, 글로벌 주식 등)