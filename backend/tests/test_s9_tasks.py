"""S9: 작업(Tasks) 영속 CRUD + 정렬 + 라우트 + 검증 + 집계."""
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


def _task(task_id, title, status="할 일", priority="보통", project_name="P", created="2026-06-29T00:00:01"):
    return {
        "task_id": task_id, "title": title, "description": "", "assignee": "",
        "status": status, "priority": priority, "due_date": "", "project_name": project_name,
        "created_at": created, "updated_at": created,
    }


# --- store ---

def test_task_crud_and_filters(tmp_path, monkeypatch):
    _, s = _fresh_store(tmp_path, monkeypatch)
    s.add_task(_task("t1", "접지저항 측정", status="진행중", created="t1"))
    s.add_task(_task("t2", "케이블 발주", status="할 일", created="t2"))
    s.add_task(_task("t3", "준공 검사", status="완료", created="t3"))
    s.add_task(_task("t4", "다른 프로젝트", project_name="Q", created="t4"))
    # 프로젝트 스코프
    ids = [r["task_id"] for r in s.list_tasks(project_name="P")]
    assert set(ids) == {"t1", "t2", "t3"}
    # 미완료 우선 + 최신순: 완료(t3)는 맨 뒤, 미완료는 최신(t2) 먼저
    assert ids[-1] == "t3"
    assert ids.index("t2") < ids.index("t1")
    # status/assignee 필터
    assert [r["task_id"] for r in s.list_tasks(status="완료")] == ["t3"]
    # update
    upd = s.update_task("t2", status="완료", priority="높음")
    assert upd["status"] == "완료" and upd["priority"] == "높음"
    assert s.update_task("ghost", status="완료") is None
    # hard delete
    assert s.delete_task("t1") is True
    assert s.get_task("t1") is None
    assert s.delete_task("ghost") is False


def test_task_index_isolated(tmp_path, monkeypatch):
    _, s = _fresh_store(tmp_path, monkeypatch)
    s.add_task(_task("t1", "x"))
    assert s.list_drawings("P") == []
    assert s.list_issues() == []
    assert (tmp_path / "_tasks.json").exists()


# --- routes ---

def _reload_routes(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "UPLOADS_DIR", tmp_path)
    monkeypatch.setattr(config, "STORE_BACKEND", "json")
    import store as store_mod
    importlib.reload(store_mod)
    import routes_task as rt
    importlib.reload(rt)
    return rt


def test_task_route_create_list_patch_delete(tmp_path, monkeypatch):
    rt = _reload_routes(tmp_path, monkeypatch)
    created = asyncio.run(rt.create_task(rt.TaskCreate(
        title="수전실 접지저항 측정 결과 제출", assignee="시공 전기팀",
        status="진행중", priority="높음", due_date="2026-07-10", project_name="P")))
    tid = created["task_id"]
    assert created["status"] == "진행중" and created["priority"] == "높음"
    assert [r["task_id"] for r in asyncio.run(rt.list_tasks(project_name="P"))] == [tid]
    # 상태 변경 영속
    patched = asyncio.run(rt.patch_task(tid, rt.TaskPatch(status="완료")))
    assert patched["status"] == "완료"
    # summary 집계
    summary = asyncio.run(rt.task_summary(project_name="P"))
    assert summary == {"total": 1, "open": 0, "done": 1, "by_status": {"할 일": 0, "진행중": 0, "완료": 1}}
    # 삭제(하드)
    assert asyncio.run(rt.delete_task(tid))["deleted"] == tid
    assert asyncio.run(rt.list_tasks(project_name="P")) == []


def test_task_route_validation(tmp_path, monkeypatch):
    rt = _reload_routes(tmp_path, monkeypatch)
    from fastapi import HTTPException
    # 빈 제목 → 400
    with pytest.raises(HTTPException) as e1:
        asyncio.run(rt.create_task(rt.TaskCreate(title="   ")))
    assert e1.value.status_code == 400
    # 알 수 없는 상태 → 400
    with pytest.raises(HTTPException) as e2:
        asyncio.run(rt.create_task(rt.TaskCreate(title="t", status="완결")))
    assert e2.value.status_code == 400
    # 알 수 없는 우선순위 → 400
    with pytest.raises(HTTPException) as e3:
        asyncio.run(rt.create_task(rt.TaskCreate(title="t", priority="긴급")))
    assert e3.value.status_code == 400
    # 없는 작업 patch/delete → 404
    with pytest.raises(HTTPException) as e4:
        asyncio.run(rt.patch_task("ghost", rt.TaskPatch(status="완료")))
    assert e4.value.status_code == 404
    with pytest.raises(HTTPException) as e5:
        asyncio.run(rt.delete_task("ghost"))
    assert e5.value.status_code == 404
    # patch에서 잘못된 상태 → 400
    ok = asyncio.run(rt.create_task(rt.TaskCreate(title="유효")))
    with pytest.raises(HTTPException) as e6:
        asyncio.run(rt.patch_task(ok["task_id"], rt.TaskPatch(status="XXX")))
    assert e6.value.status_code == 400
