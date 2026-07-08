"""라이브 데이터 경로 단위 테스트 (respx 스텁) + degraded (S8.0 K5·K3·K2).

respx로 8000을 결정적 스텁해 client·tools·health를 검증한다. 8000 실기동
라이브 스모크는 별도(smoke_live.py)로 실 시트 수를 입증한다.
"""
from __future__ import annotations

import httpx
import respx
from fastapi.testclient import TestClient

import client as client_mod
import tools
from main_ai import app

BASE = "http://127.0.0.1:8000"

_DRAWINGS = [
    {
        "file_id": "f1", "filename": "single-line.pdf",
        "conversion_status": "completed",
        "sheets": [
            {"sheet_id": "s1", "sheet_number": "E-101", "sheet_title": "단선결선도",
             "discipline_code": "E", "discipline_label": "E (전기)"},
            {"sheet_id": "s2", "sheet_number": "M-201", "sheet_title": "배관도",
             "discipline_code": "M", "discipline_label": "M (기계)"},
        ],
    },
    # 미완 변환은 시트 집계에서 제외되어야 한다.
    {"file_id": "f2", "filename": "wip.dwg", "conversion_status": "converting", "sheets": []},
]
_SEARCH = {
    "query": "EE", "sheets": [{"sheet_id": "s1", "number": "E-101"}],
    "issues": [], "files": [], "folders": [], "truncated": False,
}
_ME = {"member_id": "m-1", "member": {"id": "m-1", "name": "개혁"}, "roles": {}}
_META_EMPTY = {"count": 0, "results": [], "truncated": False}  # S15 단계8 강화 호출 스텁


@respx.mock
def test_list_sheets_maps_completed_only():
    respx.get(f"{BASE}/api/drawings").mock(return_value=httpx.Response(200, json=_DRAWINGS))
    respx.get(f"{BASE}/api/sheet-meta").mock(return_value=httpx.Response(200, json=_META_EMPTY))
    out = tools.list_sheets("Study_Project")
    assert out["count"] == 2
    assert {s["sheet_id"] for s in out["sheets"]} == {"s1", "s2"}
    assert out["sheets"][0]["number"] == "E-101"


@respx.mock
def test_list_sheets_discipline_filter():
    respx.get(f"{BASE}/api/drawings").mock(return_value=httpx.Response(200, json=_DRAWINGS))
    respx.get(f"{BASE}/api/sheet-meta").mock(return_value=httpx.Response(200, json=_META_EMPTY))
    out = tools.list_sheets("Study_Project", discipline="E")
    assert out["count"] == 1
    assert out["sheets"][0]["number"] == "E-101"


@respx.mock
def test_search_passthrough():
    respx.get(f"{BASE}/api/search").mock(return_value=httpx.Response(200, json=_SEARCH))
    respx.get(f"{BASE}/api/sheet-meta/search").mock(return_value=httpx.Response(200, json=_META_EMPTY))
    out = tools.search("Study_Project", "EE")
    assert out["sheets"][0]["sheet_id"] == "s1"
    assert out["content_matches"] == []
    assert out["truncated"] is False


@respx.mock
def test_health_reachable():
    respx.get(f"{BASE}/api/auth/me").mock(return_value=httpx.Response(200, json=_ME))
    r = TestClient(app).get("/api/chat/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["backend_8000"]["reachable"] is True
    assert body["backend_8000"]["current_user"] == "m-1"


@respx.mock
def test_health_degraded_when_backend_down():
    respx.get(f"{BASE}/api/auth/me").mock(side_effect=httpx.ConnectError("refused"))
    r = TestClient(app).get("/api/chat/health")
    assert r.status_code == 200          # 8000 다운이어도 크래시 없음
    body = r.json()
    assert body["ok"] is True
    assert body["backend_8000"]["reachable"] is False
    assert "degraded" in body["checks"]["backend_8000"]


def test_client_base_url_lazy():
    # 모듈 import 시 연결하지 않는다 — base_url만 계산.
    assert client_mod.base_url().startswith("http")
