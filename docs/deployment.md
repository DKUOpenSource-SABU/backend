# 🚀 배포 문서

## 로컬 실행

### Python (Flask)

```bash
pip install -r requirements.txt
python main.py
```

### 환경 변수 (`.env`)

```
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET=supersecret
```

---

## Docker 실행

```bash
docker build -t backend-server .
docker run -p 8000:8000 backend-server
```

---

## CI/CD 구성

- 플랫폼: GitHub Actions

```yaml
name: CI/CD

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: docker build -t my-app .
      - run: docker push ghcr.io/user/my-app
```

---