"""S5: 이슈 영속 CRUD + 상태 전이 + 핀 좌표 검증 + 카테고리 집계 회귀."""
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


def _drawing_with_sheet(tmp_path, file_id, sheet_id):
    return {
        "file_id": file_id,
        "filename": f"{file_id}.dwg",
        "file_path": str(tmp_path / file_id / "original.dwg"),
        "file_format": "dwg",
        "file_size": 10,
        "upload_date": "2026-06-29T00:00:01",
        "project_name": "P",
        "version": "1",
        "conversion_status": "completed",
        "sheets": [{"sheet_id": sheet_id, "sheet_name": "S", "sheet_index": 0}],
    }


def _issue(issue_id, title, status="열림", category="clash", file_id=None,
           sheet_id=None, pin=None, project_name="P", created="2026-06-29T00:00:01"):
    return {
        "issue_id": issue_id, "file_id": file_id, "sheet_id": sheet_id,
        "title": title, "type": "설계 검토", "status": status, "category": category,
        "assignee": "", "author": "사용자", "description": "", "project_name": project_name,
        "pin": pin, "created_at": created, "updated_at": created,
    }


# --- store: 이슈 CRUD + 스코프/필터 ---

def test_issue_crud_and_filters(tmp_path, monkeypatch):
    _, s = _fresh_store(tmp_path, monkeypatch)
    s.add_issue(_issue("i1", "현장 패널 번호와 도면 표기가 다름", category="clash",
                       file_id="F", sheet_id="S1",
                       pin={"point": [120.0, 80.0], "coord_space": "world"}, created="t1"))
    s.add_issue(_issue("i2", "배선 경로 도면과 현장 상이", category="coordination",
                       file_id="F", sheet_id="S2", created="t2"))
    s.add_issue(_issue("i3", "전역 검토 이슈(핀 없음)", category="quality", created="t3"))
    # 전역 목록(최신 우선)
    assert [r["issue_id"] for r in s.list_issues()] == ["i3", "i2", "i1"]
    # 파일/시트 스코프
    assert [r["issue_id"] for r in s.list_issues(file_id="F", sheet_id="S1")] == ["i1"]
    assert s.list_issues(file_id="F", sheet_id="S9") == []
    # 카테고리 필터
    assert [r["issue_id"] for r in s.list_issues(category="quality")] == ["i3"]
    # 핀 없는 전역 이슈 허용
    assert s.get_issue("i3")["pin"] is None
    # update: 상태 + 핀 재배치, 스코프 키(file_id) 불변
    upd = s.update_issue("i1", status="진행중", file_id="HACK")
    assert upd["status"] == "진행중"
    assert upd["file_id"] == "F"
    assert s.update_issue("ghost", status="닫힘") is None
    # soft delete: 레코드 보존 + status=삭제됨
    assert s.delete_issue("i2") is True
    assert s.get_issue("i2")["status"] == "삭제됨"
    assert s.delete_issue("ghost") is False


def test_issue_index_isolated(tmp_path, monkeypatch):
    """이슈 인덱스는 도면/마크업 인덱스와 분리돼 서로 오염되지 않는다."""
    _, s = _fresh_store(tmp_path, monkeypatch)
    s.add_issue(_issue("i1", "x"))
    assert s.list_drawings("P") == []
    assert s.list_markups("F", "S") == []
    assert (tmp_path / "_issues.json").exists()


# --- routes ---

def _reload_routes(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "UPLOADS_DIR", tmp_path)
    monkeypatch.setattr(config, "STORE_BACKEND", "json")
    import store as store_mod
    importlib.reload(store_mod)
    import routes_drawing
    importlib.reload(routes_drawing)
    import routes_issue as ri
    importlib.reload(ri)
    return ri


def test_issue_route_create_list_patch_delete(tmp_path, monkeypatch):
    ri = _reload_routes(tmp_path, monkeypatch)
    s = ri.get_store()
    s.add_drawing(_drawing_with_sheet(tmp_path, "F", "F_sheet_001"))
    # 핀 있는 이슈 생성(world)
    created = asyncio.run(ri.create_issue(ri.IssueCreate(
        title="현장 패널 번호와 도면 표기가 다름 — CAD 확인 요청", type="현장 확인",
        category="clash", assignee="도면 검토자", file_id="F", sheet_id="F_sheet_001",
        pin=ri.IssuePin(point=[120.0, 80.0], coord_space="world"))))
    iid = created["issue_id"]
    assert created["status"] == "열림"
    assert created["pin"]["coord_space"] == "world"
    # 전역 목록 + 파일 스코프
    assert [r["issue_id"] for r in asyncio.run(ri.list_issues())] == [iid]
    assert [r["issue_id"] for r in asyncio.run(ri.list_issues(file_id="F", sheet_id="F_sheet_001"))] == [iid]
    # 상태 전이 영속
    patched = asyncio.run(ri.patch_issue(iid, ri.IssuePatch(status="진행중")))
    assert patched["status"] == "진행중"
    patched = asyncio.run(ri.patch_issue(iid, ri.IssuePatch(status="답변됨")))
    assert patched["status"] == "답변됨"
    # soft delete → 기본 목록(삭제됨 제외)에서 사라짐, status 목록엔 보임
    assert asyncio.run(ri.delete_issue(iid))["deleted"] == iid
    assert asyncio.run(ri.list_issues()) == []
    assert [r["issue_id"] for r in asyncio.run(ri.list_issues(status="삭제됨"))] == [iid]


def test_issue_pinless_global_create(tmp_path, monkeypatch):
    """핀 없는 전역 이슈는 file_id/sheet_id 없이 생성된다."""
    ri = _reload_routes(tmp_path, monkeypatch)
    created = asyncio.run(ri.create_issue(ri.IssueCreate(
        title="구역명/장비 태그 식별 불명확", type="설계 검토", category="quality")))
    assert created["pin"] is None
    assert created["file_id"] is None


def test_issue_pdf_image_pin(tmp_path, monkeypatch):
    """PDF/래스터 시트 핀은 정규화 image 좌표([0,1])로 저장된다."""
    ri = _reload_routes(tmp_path, monkeypatch)
    s = ri.get_store()
    s.add_drawing(_drawing_with_sheet(tmp_path, "PF", "PF_sheet_001"))
    created = asyncio.run(ri.create_issue(ri.IssueCreate(
        title="단선도 분전반 표기 확인", file_id="PF", sheet_id="PF_sheet_001",
        pin=ri.IssuePin(point=[0.42, 0.63], coord_space="image"))))
    assert created["pin"]["coord_space"] == "image"
    assert created["pin"]["point"] == [0.42, 0.63]


def test_issue_route_validation(tmp_path, monkeypatch):
    ri = _reload_routes(tmp_path, monkeypatch)
    from fastapi import HTTPException
    s = ri.get_store()
    s.add_drawing(_drawing_with_sheet(tmp_path, "F", "F_sheet_001"))
    # 빈 제목 → 400
    with pytest.raises(HTTPException) as e1:
        asyncio.run(ri.create_issue(ri.IssueCreate(title="   ")))
    assert e1.value.status_code == 400
    # 알 수 없는 유형 → 400
    with pytest.raises(HTTPException) as e2:
        asyncio.run(ri.create_issue(ri.IssueCreate(title="t", type="외계인")))
    assert e2.value.status_code == 400
    # 알 수 없는 카테고리 → 400
    with pytest.raises(HTTPException) as e3:
        asyncio.run(ri.create_issue(ri.IssueCreate(title="t", category="nope")))
    assert e3.value.status_code == 400
    # 핀 있는데 file/sheet 없음 → 400
    with pytest.raises(HTTPException) as e4:
        asyncio.run(ri.create_issue(ri.IssueCreate(title="t", pin=ri.IssuePin(point=[1, 2]))))
    assert e4.value.status_code == 400
    # 핀 file_id 도면 없음 → 404
    with pytest.raises(HTTPException) as e5:
        asyncio.run(ri.create_issue(ri.IssueCreate(
            title="t", file_id="ghost", sheet_id="x", pin=ri.IssuePin(point=[1, 2]))))
    assert e5.value.status_code == 404
    # image 핀 범위 초과 → 400
    with pytest.raises(HTTPException) as e6:
        asyncio.run(ri.create_issue(ri.IssueCreate(
            title="t", file_id="F", sheet_id="F_sheet_001",
            pin=ri.IssuePin(point=[1.5, 0.2], coord_space="image"))))
    assert e6.value.status_code == 400


def test_issue_patch_pin_location_invariant(tmp_path, monkeypatch):
    """PATCH도 create와 동일하게 핀-위치 불변식을 강제한다(부유 핀·유령 시트 금지)."""
    ri = _reload_routes(tmp_path, monkeypatch)
    from fastapi import HTTPException
    s = ri.get_store()
    s.add_drawing(_drawing_with_sheet(tmp_path, "F", "F_sheet_001"))
    # 핀 없는 전역 이슈
    g = asyncio.run(ri.create_issue(ri.IssueCreate(title="전역 이슈", category="quality")))
    gid = g["issue_id"]
    # 전역(file/sheet 없음) 이슈에 PATCH로 핀 부착 시도 → 400(부유 핀 금지)
    with pytest.raises(HTTPException) as e1:
        asyncio.run(ri.patch_issue(gid, ri.IssuePatch(
            pin=ri.IssuePin(point=[10.0, 20.0], coord_space="world"))))
    assert e1.value.status_code == 400
    # 핀 있는 이슈를 만들고, PATCH로 존재하지 않는 시트로 재배치 시도 → 404
    p = asyncio.run(ri.create_issue(ri.IssueCreate(
        title="핀 이슈", file_id="F", sheet_id="F_sheet_001",
        pin=ri.IssuePin(point=[1.0, 2.0], coord_space="world"))))
    with pytest.raises(HTTPException) as e2:
        asyncio.run(ri.patch_issue(p["issue_id"], ri.IssuePatch(sheet_id="GHOST")))
    assert e2.value.status_code == 404
    # 유효 시트로의 핀 좌표 변경은 허용
    ok = asyncio.run(ri.patch_issue(p["issue_id"], ri.IssuePatch(
        pin=ri.IssuePin(point=[3.0, 4.0], coord_space="world"))))
    assert ok["pin"]["point"] == [3.0, 4.0]


def test_issue_pin_rejects_non_finite(tmp_path, monkeypatch):
    """world 핀도 NaN/Infinity를 거부(JSON 직렬화 깨짐·콘솔 에러 방지)."""
    ri = _reload_routes(tmp_path, monkeypatch)
    from fastapi import HTTPException
    s = ri.get_store()
    s.add_drawing(_drawing_with_sheet(tmp_path, "F", "F_sheet_001"))
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(HTTPException) as e:
            asyncio.run(ri.create_issue(ri.IssueCreate(
                title="t", file_id="F", sheet_id="F_sheet_001",
                pin=ri.IssuePin(point=[bad, 1.0], coord_space="world"))))
        assert e.value.status_code == 400


def test_issue_status_transition_rejected(tmp_path, monkeypatch):
    """허용되지 않은 상태 전이는 거부(닫힘 → 진행중)."""
    ri = _reload_routes(tmp_path, monkeypatch)
    from fastapi import HTTPException
    created = asyncio.run(ri.create_issue(ri.IssueCreate(title="t")))
    iid = created["issue_id"]
    asyncio.run(ri.patch_issue(iid, ri.IssuePatch(status="닫힘")))
    # 닫힘 → 진행중 은 불가(재오픈 필요)
    with pytest.raises(HTTPException) as e1:
        asyncio.run(ri.patch_issue(iid, ri.IssuePatch(status="진행중")))
    assert e1.value.status_code == 400
    # 닫힘 → 열림(재오픈)은 허용
    assert asyncio.run(ri.patch_issue(iid, ri.IssuePatch(status="열림")))["status"] == "열림"
    # 없는 이슈 patch → 404
    with pytest.raises(HTTPException) as e2:
        asyncio.run(ri.patch_issue("ghost", ri.IssuePatch(status="닫힘")))
    assert e2.value.status_code == 404


def test_issue_category_counts(tmp_path, monkeypatch):
    """카테고리 count = 진행 중(닫힘/삭제 제외) 이슈 수."""
    ri = _reload_routes(tmp_path, monkeypatch)
    asyncio.run(ri.create_issue(ri.IssueCreate(title="a", category="clash")))
    asyncio.run(ri.create_issue(ri.IssueCreate(title="b", category="clash")))
    c = asyncio.run(ri.create_issue(ri.IssueCreate(title="c", category="quality")))
    # quality 1건을 닫음 → quality count 0
    asyncio.run(ri.patch_issue(c["issue_id"], ri.IssuePatch(status="닫힘")))
    counts = asyncio.run(ri.issue_categories())
    assert counts == {"clash": 2, "quality": 0, "coordination": 0}
