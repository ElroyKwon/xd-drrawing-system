"""S9: 작업(Tasks) 영속 라우트.

프로젝트 전역 작업 항목(담당·상태·기한). 이슈와 달리 도면 핀이 없고 하드 삭제한다.
mutation은 편집자 이상 역할을 요구한다(S7 RBAC 계승). prefix=/api/tasks.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth import require_role
from store import get_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tasks", tags=["task"])

_TASK_STATUSES = {"할 일", "진행중", "완료"}
_TASK_PRIORITIES = {"높음", "보통", "낮음"}
_OPEN_STATUSES = {"할 일", "진행중"}


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    assignee: str = ""
    status: str = "할 일"
    priority: str = "보통"
    due_date: str = ""                     # ISO 날짜(YYYY-MM-DD) 또는 빈 문자열
    project_name: str = "Study_Project"


class TaskPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None


def _require_task_role(task_id: str, min_role: str):
    """task_id 작업의 프로젝트에서 역할 강제 + 작업 반환."""
    task = get_store().get_task(task_id)
    if not task:
        raise HTTPException(404, f"작업 없음: {task_id}")
    require_role(task.get("project_name"), min_role)
    return task


def _validate(status: str, priority: str) -> None:
    if status not in _TASK_STATUSES:
        raise HTTPException(400, f"알 수 없는 상태: {status}")
    if priority not in _TASK_PRIORITIES:
        raise HTTPException(400, f"알 수 없는 우선순위: {priority}")


@router.get("")
async def list_tasks(project_name: Optional[str] = None, status: Optional[str] = None,
                     assignee: Optional[str] = None):
    return get_store().list_tasks(project_name=project_name, status=status, assignee=assignee)


@router.get("/summary")
async def task_summary(project_name: Optional[str] = None):
    """상태별 집계(홈 위젯용). 진행 중(할 일+진행중)/완료/전체."""
    rows = get_store().list_tasks(project_name=project_name)
    counts = {s: 0 for s in _TASK_STATUSES}
    for r in rows:
        s = r.get("status")
        if s in counts:
            counts[s] += 1
    return {
        "total": len(rows),
        "open": sum(counts[s] for s in _OPEN_STATUSES),
        "done": counts["완료"],
        "by_status": counts,
    }


@router.post("")
async def create_task(body: TaskCreate):
    require_role(body.project_name, "편집자")  # S7: 작업 작성 = 편집자 이상
    store = get_store()
    if not body.title.strip():
        raise HTTPException(400, "작업 제목은 필수입니다")
    _validate(body.status, body.priority)
    now = datetime.now().isoformat()
    meta = {
        "task_id": str(uuid.uuid4()),
        "title": body.title.strip(),
        "description": body.description,
        "assignee": body.assignee,
        "status": body.status,
        "priority": body.priority,
        "due_date": body.due_date,
        "project_name": body.project_name,
        "created_at": now,
        "updated_at": now,
    }
    store.add_task(meta)
    logger.info("task created %s (%s, %s)", meta["task_id"], meta["title"], meta["status"])
    return meta


@router.patch("/{task_id}")
async def patch_task(task_id: str, body: TaskPatch):
    _require_task_role(task_id, "편집자")
    store = get_store()
    fields = body.model_dump(exclude_none=True)
    if "status" in fields and fields["status"] not in _TASK_STATUSES:
        raise HTTPException(400, f"알 수 없는 상태: {fields['status']}")
    if "priority" in fields and fields["priority"] not in _TASK_PRIORITIES:
        raise HTTPException(400, f"알 수 없는 우선순위: {fields['priority']}")
    updated = store.update_task(task_id, **fields)
    if not updated:
        raise HTTPException(404, f"작업 없음: {task_id}")
    return updated


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    _require_task_role(task_id, "편집자")
    if not get_store().delete_task(task_id):
        raise HTTPException(404, f"작업 없음: {task_id}")
    return {"deleted": task_id}
