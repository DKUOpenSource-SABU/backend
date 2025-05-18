from fastapi import FastAPI
from routers import search, cluster
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Stock Clustering API")

origins = [
    "http://localhost:5173",  # React 개발 서버
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # ✅ 허용할 Origin
    allow_credentials=True,           # ✅ 쿠키 인증 등 포함할지
    allow_methods=["*"],              # ✅ 허용할 HTTP method (GET, POST 등)
    allow_headers=["*"],              # ✅ 허용할 요청 헤더
)

app.include_router(search.router, prefix="/search")
app.include_router(cluster.router, prefix="/cluster")
