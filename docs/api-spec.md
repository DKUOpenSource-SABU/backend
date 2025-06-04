# 📘 API 명세서

## 인증

- 방식: JWT
- 헤더 예시:
  ```
  Authorization: Bearer <token>
  ```

---

## 엔드포인트 목록

| 메서드 | 경로                     | 설명                     |
|--------|--------------------------|--------------------------|
| GET    | /api/projects            | 전체 프로젝트 조회       |
| POST   | /api/projects            | 프로젝트 생성            |
| GET    | /api/projects/:id        | 특정 프로젝트 상세 조회  |

---

## 상세 명세

### GET `/api/projects`

- 응답:
```json
[
  {
    "id": 1,
    "name": "Demo Project",
    "created_at": "2024-01-01"
  }
]
```

### POST `/api/projects`

- 요청:
```json
{
  "name": "New Project"
}
```

- 응답:
```json
{
  "id": 2,
  "name": "New Project",
  "created_at": "2024-01-02"
}
```
