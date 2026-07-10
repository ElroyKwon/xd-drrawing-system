"""액션 감사 — 확인된 대화형 액션(origin=ai_chat 등)의 메타데이터 기록/조회."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from store import get_store

router = APIRouter(prefix="/api/audit", tags=["audit"])


class ActionAudit(BaseModel):
    actor: str = ""
    action_type: str
    target_id: str = ""
    origin: str = "ai_chat"
    conversation_id: str = ""
    project_name: str = ""


@router.post("/action")
async def record_action(body: ActionAudit):
    rec = body.model_dump()
    rec["ts"] = datetime.now().isoformat()
    return get_store().add_action_audit(rec)


@router.get("/actions")
async def list_actions(project_name: Optional[str] = None):
    return get_store().list_action_audit(project_name)
