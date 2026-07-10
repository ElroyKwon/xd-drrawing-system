"""P2: 액션 감사로그(8000) — 확인된 대화형 액션(origin=ai_chat) 기록/조회.

repo 관례대로 XD_UPLOADS_DIR을 tmp로 격리(실 uploads 오염 방지) 후 store/main 재적재.
"""
import importlib
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("XD_UPLOADS_DIR", str(tmp_path))
    import config
    importlib.reload(config)
    import store as store_mod
    importlib.reload(store_mod)
    import routes_audit
    importlib.reload(routes_audit)
    import main
    importlib.reload(main)
    return TestClient(main.app)


def test_action_audit_record_and_list(client):
    r = client.post("/api/audit/action", json={
        "actor": "member-owner", "action_type": "create_issue",
        "target_id": "ISS-1", "origin": "ai_chat", "conversation_id": "conv-1"})
    assert r.status_code == 200
    rows = client.get("/api/audit/actions").json()
    assert any(a["target_id"] == "ISS-1" and a["origin"] == "ai_chat" for a in rows)
