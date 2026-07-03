"""AI 챗 사이드카 — 독립 FastAPI 프로세스(8001) (S8.0 부트스트랩).

기존 8000 앱과 완전 격리: backend 모듈 import 0(격리 불변식 K6),
8000 공개 HTTP API만 소비(순수 클라이언트, OPEN-1 (a)).
CORS origin은 자체 상수 — backend.config import 금지(격리 불변식, 검수 교정 ④).
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from health import router as health_router

# 프론트 dev origin만 자체 상수로 허용(실사용 CORS/소비자는 S8.3).
_CORS_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:5173",
    "http://localhost:5174",
]

app = FastAPI(title="XD AI 사이드카", version="0.1.0 (S8.0)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(health_router)


@app.get("/")
async def root():
    return {"service": "xd-ai-sidecar", "stage": "S8.0", "docs": "/docs"}
