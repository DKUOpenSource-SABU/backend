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

- 📘 **[API 명세서](./docs/api-spec.md)**  
  REST API 경로, 파라미터, 응답 예시 등 상세 명세

- 🚀 **[배포 문서](./docs/deployment.md)**  
  서버 실행 방식, CI/CD 흐름 및 운영 환경 구성 설명

- 🧱 **[아키텍처 문서](./docs/architecture.md)**  
  시스템 전체 구성도 및 백엔드 내부 흐름 구조화 설명
