"""GET /api/chat/health — 8001 자체 상태 + 8000 연결성/현재 사용자 (S8.0).

health는 연결성·현재 사용자만 보고한다. 시트 수 등 그라운딩 데이터는 툴이 반환하며
health 스키마에 넣지 않는다(설계 v2 §4, 검수 교정 ①).
"""
from __future__ import annotations

from fastapi import APIRouter

from client import BackendError, base_url, get_me

router = APIRouter(prefix="/api/chat", tags=["chat-health"])


@router.get("/health")
async def health():
    backend = {"base_url": base_url(), "reachable": False}
    checks = {"self": "ok"}
    try:
        me = get_me()
        backend["reachable"] = True
        backend["current_user"] = me.get("member_id")
        checks["backend_8000"] = "reachable"
    except BackendError as exc:
        # 8000 미도달 — degraded로 정직하게 응답(크래시 없음).
        checks["backend_8000"] = f"degraded: {exc.message}"
    # 8001 자체는 8000 상태와 무관하게 항상 ok.
    return {"ok": True, "backend_8000": backend, "checks": checks}
