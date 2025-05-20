from fastapi import FastAPI
from routers import search, cluster
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Stock Clustering API")

origins = [
    "http://localhost:5173",  # React 개발 서버
    "http://127.0.0.1:3000",
    "https://dkuopensource-sabu.github.io",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/search")
app.include_router(cluster.router, prefix="/cluster")
