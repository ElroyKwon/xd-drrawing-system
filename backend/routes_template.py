"""S9.3: 프로젝트 템플릿(허브 레벨) 영속 라우트 + 적용 로직.

템플릿은 새 프로젝트에 사전구성(추가 폴더 + 기본 구성원)을 적용하기 위한 청사진이다.
허브 레벨 자원이라 프로젝트 RBAC 대상이 아니다(허브 역할 모델은 미도입).
prefix=/api/templates. apply_template_to_project는 routes_auth.create_project에서 호출한다.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from store import get_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/templates", tags=["template"])

_SOURCES = {"blank", "existing"}


class TemplateCreate(BaseModel):
    name: str
    access: str = "일반 액세스"
    source: str = "blank"
    source_project: Optional[str] = None
    folders: Optional[list[str]] = None
    default_members: Optional[list[dict]] = None


@router.get("")
async def list_templates():
    return get_store().list_templates()


@router.post("")
async def create_template(body: TemplateCreate):
    store = get_store()
    name = body.name.strip()
    if not name:
        raise HTTPException(400, "템플릿 이름은 필수입니다")
    if body.source not in _SOURCES:
        raise HTTPException(400, f"알 수 없는 소스: {body.source}")
    folders = list(body.folders or [])
    members = list(body.default_members or [])
    # 기존 프로젝트에서 작성: 그 프로젝트의 폴더(비시드) + 구성원(생성자 외)을 청사진으로 복사.
    if body.source == "existing":
        if not body.source_project:
            raise HTTPException(400, "기존 프로젝트 소스에는 source_project가 필요합니다")
        src = body.source_project
        # 소스의 폴더 구조(ACC 기본 폴더 포함) + 구성원을 청사진으로 캡처.
        folders = [f["name"] for f in store.list_folders(src)]
        members = [{"member_id": pm["member_id"], "role": pm["role"]}
                   for pm in store.list_project_members(src)]
    meta = {
        "template_id": f"template-{uuid.uuid4().hex[:8]}",
        "name": name,
        "access": body.access,
        "source": body.source,
        "source_project": body.source_project,
        "folders": folders,
        "default_members": members,
        "created_by": store.get_current_user(),
        "created_at": datetime.now().strftime("%Y.%m.%d."),
    }
    store.add_template(meta)
    logger.info("template created %s (%s)", meta["template_id"], name)
    return meta


@router.delete("/{template_id}")
async def delete_template(template_id: str):
    if not get_store().delete_template(template_id):
        raise HTTPException(404, f"템플릿 없음: {template_id}")
    return {"deleted": template_id}


def _resolve_template(store, template_ref: Optional[str]):
    """create 폼의 templateId는 template_id 또는 template name일 수 있다(프론트 호환). 둘 다 조회."""
    if not template_ref or template_ref in ("", "none", "owner"):
        return None
    tpl = store.get_template(template_ref)
    if tpl:
        return tpl
    return next((t for t in store.list_templates() if t.get("name") == template_ref), None)


def apply_template_to_project(store, template_ref: Optional[str], project_name: str, creator: str) -> dict:
    """템플릿의 추가 폴더 + 기본 구성원을 새 프로젝트에 시드. 적용 요약 반환."""
    tpl = _resolve_template(store, template_ref)
    if not tpl:
        return {"applied": False}
    now = datetime.now().isoformat()
    # 1) 추가 폴더(루트 레벨). 대상의 기존 폴더명(ACC 기본 폴더 포함)과 중복은 건너뜀.
    existing_names = {f["name"] for f in store.list_folders(project_name)}
    added_folders = []
    for fname in tpl.get("folders", []):
        if fname in existing_names:
            continue
        existing_names.add(fname)
        fid = f"{project_name}::tmpl-{uuid.uuid4().hex[:8]}"
        store.add_folder({
            "folder_id": fid, "project_name": project_name, "name": fname,
            "parent_id": None, "share_status": "프로젝트 공유",
            "permissions": [{"role": "관리자", "level": "관리"},
                            {"role": "편집자", "level": "편집"},
                            {"role": "뷰어", "level": "보기"}],
            "updated_at": now, "updated_by": "템플릿", "seeded": True,
        })
        added_folders.append(fname)
    # 2) 기본 구성원(생성자=관리자는 이미 등록됨 → 중복/자기강등 방지 위해 건너뜀).
    added_members = []
    for m in tpl.get("default_members", []):
        mid = m.get("member_id")
        if not mid or mid == creator:
            continue
        if store.get_project_member(project_name, mid):
            continue
        if not store.get_member(mid):
            continue
        store.add_project_member({
            "project_name": project_name, "member_id": mid,
            "role": m.get("role", "뷰어"), "status": "활성",
            "added_at": datetime.now().strftime("%Y.%m.%d."),
        })
        added_members.append(mid)
    logger.info("template %s applied to %s: folders=%s members=%s",
                tpl["template_id"], project_name, added_folders, added_members)
    return {"applied": True, "template_id": tpl["template_id"],
            "folders": added_folders, "members": added_members}
