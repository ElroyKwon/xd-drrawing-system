"""액션 제안(propose_*) 단위 테스트 — 정규화 스펙 생성 + 격리(8000 write 0).

라벨→id 해소는 tools.py의 READ 경로(HTTP GET)만 쓴다. propose_*는 어떤 POST/PATCH도
발생시키지 않는다(휴먼인더루프 — 실행은 프론트 확인 카드가 트리거). list_sheets는
/api/drawings + /api/sheet-meta를 함께 조회하므로 두 GET을 스텁한다(강화 태그 조인).
"""
from __future__ import annotations

import httpx
import respx

import actions

BASE = "http://127.0.0.1:8000"

_NO_META = {"count": 0, "results": [], "truncated": False}


@respx.mock
def test_propose_create_issue_resolves_sheet():
    # list_sheets(그라운딩용 GET)로 라벨→sheet_id 해소.
    respx.get(f"{BASE}/api/drawings").mock(return_value=httpx.Response(200, json=[
        {"file_id": "F1", "conversion_status": "completed",
         "sheets": [{"sheet_id": "F1_sheet_001", "sheet_number": "EE-01-001", "sheet_title": "22.9kV 단선결선도"}]},
    ]))
    respx.get(f"{BASE}/api/sheet-meta").mock(return_value=httpx.Response(200, json=_NO_META))
    pa = actions.propose_create_issue(
        "청주사업장",
        {"title": "차단기 정격 확인", "category": "quality", "sheet_ref": "EE-01-001"},
    )
    assert pa["type"] == "create_issue"
    assert pa["params"]["title"] == "차단기 정격 확인"
    assert pa["params"]["sheet_id"] == "F1_sheet_001"
    assert pa["params"]["file_id"] == "F1"
    assert pa["target_label"] == "EE-01-001"
    assert "action_id" in pa


@respx.mock
def test_propose_create_issue_no_side_effect():
    # 제안은 어떤 POST/PATCH도 하지 않는다(격리).
    post = respx.post(f"{BASE}/api/issues")
    respx.get(f"{BASE}/api/drawings").mock(return_value=httpx.Response(200, json=[]))
    respx.get(f"{BASE}/api/sheet-meta").mock(return_value=httpx.Response(200, json=_NO_META))
    actions.propose_create_issue("청주사업장", {"title": "전역 이슈"})
    assert not post.called


from provider import LLMProvider  # noqa: E402
import agent  # noqa: E402


class _ScriptProvider(LLMProvider):
    """propose_create_task 한 번 호출 후 마무리하는 가짜 provider."""
    name = "mock"

    def __init__(self):
        self._step = 0

    def complete(self, messages, tools_schema):
        self._step += 1
        if self._step == 1:
            return {"content": None, "tool_calls": [
                {"id": "c1", "name": "propose_create_task",
                 "arguments": '{"title": "접지저항 측정 제출"}'}]}
        return {"content": "작업 생성을 제안했습니다. 카드에서 확인해 주세요.", "tool_calls": []}


def test_run_chat_returns_pending_action():
    out = agent.run_chat("청주사업장", "접지저항 측정 작업 만들어줘",
                         provider=_ScriptProvider())
    assert len(out["pending_actions"]) == 1
    pa = out["pending_actions"][0]
    assert pa["type"] == "create_task"
    assert pa["params"]["title"] == "접지저항 측정 제출"
