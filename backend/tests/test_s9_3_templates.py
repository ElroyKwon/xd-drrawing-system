"""S9.3: 프로젝트 템플릿 CRUD + 시드 + 생성 시 적용(폴더/구성원)."""
import asyncio
import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/

import config  # noqa: E402


def _fresh_store(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "UPLOADS_DIR", tmp_path)
    import store as store_mod
    importlib.reload(store_mod)
    return store_mod, store_mod.JsonDrawingStore()


# --- store ---

def test_template_seed_and_crud(tmp_path, monkeypatch):
    _, s = _fresh_store(tmp_path, monkeypatch)
    # 비었으면 허브 기본 템플릿 시드
    names = {t["name"] for t in s.list_templates()}
    assert "표준 프로젝트 템플릿" in names and "전기 시공 표준" in names
    s.add_template({"template_id": "t-custom", "name": "커스텀", "access": "소유자",
                    "source": "blank", "source_project": None, "folders": ["X"],
                    "default_members": [], "created_by": "member-owner", "created_at": "2026.07.02."})
    assert s.get_template("t-custom")["name"] == "커스텀"
    assert s.delete_template("t-custom") is True
    assert s.get_template("t-custom") is None
    assert s.delete_template("ghost") is False


# --- routes ---

def _reload_routes(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "UPLOADS_DIR", tmp_path)
    monkeypatch.setattr(config, "STORE_BACKEND", "json")
    import store as store_mod
    importlib.reload(store_mod)
    import auth as auth_mod
    importlib.reload(auth_mod)
    import routes_files
    importlib.reload(routes_files)
    import routes_template as rt
    importlib.reload(rt)
    import routes_auth as ra
    importlib.reload(ra)
    return rt, ra, store_mod


def test_template_route_create_blank_and_delete(tmp_path, monkeypatch):
    rt, _, _ = _reload_routes(tmp_path, monkeypatch)
    created = asyncio.run(rt.create_template(rt.TemplateCreate(name="빈 템플릿 A", access="소유자")))
    tid = created["template_id"]
    assert created["source"] == "blank" and created["folders"] == []
    assert any(t["template_id"] == tid for t in asyncio.run(rt.list_templates()))
    assert asyncio.run(rt.delete_template(tid))["deleted"] == tid
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as e:
        asyncio.run(rt.delete_template(tid))
    assert e.value.status_code == 404


def test_template_from_existing_project_copies_folders_and_members(tmp_path, monkeypatch):
    rt, _, store_mod = _reload_routes(tmp_path, monkeypatch)
    s = rt.get_store()
    # Study_Project는 시드 폴더 + 구성원 3명 보유
    created = asyncio.run(rt.create_template(rt.TemplateCreate(
        name="Study 복제", source="existing", source_project="Study_Project")))
    assert created["source"] == "existing"
    assert len(created["folders"]) > 0            # ACC 기본 폴더 복사
    member_ids = {m["member_id"] for m in created["default_members"]}
    assert "member-reviewer" in member_ids and "member-viewer" in member_ids
    # source_project 누락 시 400
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as e:
        asyncio.run(rt.create_template(rt.TemplateCreate(name="X", source="existing")))
    assert e.value.status_code == 400


def test_create_project_applies_template(tmp_path, monkeypatch):
    """생성 시 템플릿의 추가 폴더 + 기본 구성원이 새 프로젝트에 시드된다."""
    rt, ra, store_mod = _reload_routes(tmp_path, monkeypatch)
    s = rt.get_store()
    # 템플릿 준비: 폴더 2 + 구성원 1(field=편집자)
    tpl = asyncio.run(rt.create_template(rt.TemplateCreate(name="시공 표준")))
    s.add_template  # noqa: touch
    tpl_full = s.get_template(tpl["template_id"])
    tpl_full["folders"] = ["시방서", "제출물"]
    tpl_full["default_members"] = [{"member_id": "member-field", "role": "편집자"}]
    s.add_template(tpl_full)
    # 관리자(개혁)로 프로젝트 생성 + templateId 지정
    proj = asyncio.run(ra.create_project({"name": "템플릿 적용 현장", "templateId": tpl["template_id"]}))
    assert proj["template_applied"]["applied"] is True
    assert set(proj["template_applied"]["folders"]) == {"시방서", "제출물"}
    assert proj["template_applied"]["members"] == ["member-field"]
    # 실제 시드 확인: 폴더 + 구성원
    folder_names = {f["name"] for f in s.list_folders("템플릿 적용 현장", seed=False)}
    assert {"시방서", "제출물"} <= folder_names
    assert s.get_project_member("템플릿 적용 현장", "member-field")["role"] == "편집자"
    # 생성자(관리자)는 그대로
    assert s.get_project_member("템플릿 적용 현장", "member-owner")["role"] == "관리자"


def test_create_project_no_template_no_apply(tmp_path, monkeypatch):
    rt, ra, _ = _reload_routes(tmp_path, monkeypatch)
    proj = asyncio.run(ra.create_project({"name": "무템플릿 현장"}))
    assert proj["template_applied"]["applied"] is False
