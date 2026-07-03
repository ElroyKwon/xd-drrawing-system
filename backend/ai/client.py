"""8000 백엔드 공개 HTTP API를 읽는 lazy read-only 클라이언트 (S8.0).

격리 불변식: 기존 backend 모듈(store/routes_*/auth/...)을 import하지 않는다.
오직 HTTP로만 8000과 통신한다. 모듈 import 시 연결하지 않는다(lazy).
"""
from __future__ import annotations

import os
from typing import Any, Optional

import httpx

DEFAULT_BASE = "http://127.0.0.1:8000"
_TIMEOUT = 5.0


class BackendError(Exception):
    """8000 도달 실패/에러 응답을 구조화한 예외."""

    def __init__(self, message: str, *, status: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status = status


def base_url() -> str:
    """8000 베이스 URL. 환경변수 XD_BACKEND_BASE로 재정의 가능(기본 8000)."""
    return os.environ.get("XD_BACKEND_BASE", DEFAULT_BASE).rstrip("/")


def get(path: str, params: Optional[dict] = None) -> Any:
    """8000에 GET. 연결 실패/타임아웃/4xx·5xx는 BackendError로 승격.

    호출 시점에만 연결한다(lazy) — 모듈 import는 네트워크를 건드리지 않는다.
    """
    url = f"{base_url()}{path}"
    try:
        resp = httpx.get(url, params=params, timeout=_TIMEOUT)
    except httpx.RequestError as exc:
        raise BackendError(f"8000 연결 실패: {exc}") from exc
    if resp.status_code >= 400:
        raise BackendError(f"8000 오류 {resp.status_code}: {path}", status=resp.status_code)
    return resp.json()


def get_me() -> dict:
    """현재 사용자(로컬 모의) — GET /api/auth/me. 연결성 프로브로도 사용."""
    return get("/api/auth/me")
