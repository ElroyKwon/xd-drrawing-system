"""로드타임 병합 — confirm→curated·reject→drop·비llm 보호·dangling 무시·재빌드 생존."""
import importlib
import json

import pytest

_SNAP = {
    "graphs": {
        "P1": {
            "built_at": "2026-07-09T00:00:00",
            "nodes": [
                {"id": "eq:E1", "type": "equipment", "ref_id": "E1", "label": "MTR-1", "props": {}},
                {"id": "eq:E2", "type": "equipment", "ref_id": "E2", "label": "VCB-1", "props": {}},
                {"id": "eq:E3", "type": "equipment", "ref_id": "E3", "label": "TR-1", "props": {}},
                {"id": "sh:s1", "type": "sheet", "ref_id": "s1", "label": "E-101", "props": {}},
            ],
            "edges": [
                {"src": "eq:E1", "dst": "sh:s1", "type": "appears_on", "confidence": 1.0, "track": "curated", "evidence": None},
                {"src": "eq:E1", "dst": "eq:E2", "type": "relates_to", "confidence": 0.6, "track": "llm", "evidence": "공출현"},
                {"src": "eq:E2", "dst": "eq:E3", "type": "relates_to", "confidence": 0.5, "track": "llm", "evidence": "공출현2"},
            ],
        }
    }
}


@pytest.fixture()
def kg(tmp_path, monkeypatch):
    monkeypatch.setenv("XD_UPLOADS_DIR", str(tmp_path))
    import config
    importlib.reload(config)
    import kg_store
    importlib.reload(kg_store)
    (tmp_path / "_knowledge_graph.json").write_text(json.dumps(_SNAP), encoding="utf-8")
    return kg_store


def _rel(g, a, b):
    return [e for e in g["edges"] if e["type"] == "relates_to"
            and {e["src"], e["dst"]} == {a, b}]


def test_confirm_promotes_llm_to_curated(kg):
    kg.append_override("P1", kg.edge_key("eq:E1", "eq:E2"), "confirm", actor="k", at=None, reason=None)
    g = kg._merged_graph("P1")
    edge = _rel(g, "eq:E1", "eq:E2")[0]
    assert edge["track"] == "curated"


def test_reject_drops_edge(kg):
    kg.append_override("P1", kg.edge_key("eq:E2", "eq:E3"), "reject", actor=None, at=None, reason="오탐")
    g = kg._merged_graph("P1")
    assert _rel(g, "eq:E2", "eq:E3") == []


def test_curated_edge_is_protected(kg):
    # appears_on(curated) 에 대해 (있을 수 없는) override 가 있어도 무시 — 비llm 보호.
    kg.append_override("P1", "eq:E1|sh:s1|relates_to", "reject", actor=None, at=None, reason=None)
    g = kg._merged_graph("P1")
    assert any(e["type"] == "appears_on" and e["track"] == "curated" for e in g["edges"])


def test_dangling_override_is_ignored(kg):
    # 스냅샷에 없는 edge_key → 조용히 무시(로드 실패 아님).
    kg.append_override("P1", "eq:GONE|eq:X|relates_to", "confirm", actor=None, at=None, reason=None)
    g = kg._merged_graph("P1")  # 예외 없이 로드.
    assert len(g["nodes"]) == 4


def test_promotion_survives_rebuild(kg, tmp_path):
    # confirm 후 스냅샷을 순수 재생성(오버레이 미포함) → 병합은 여전히 curated.
    kg.append_override("P1", kg.edge_key("eq:E1", "eq:E2"), "confirm", actor="k", at=None, reason=None)
    (tmp_path / "_knowledge_graph.json").write_text(json.dumps(_SNAP), encoding="utf-8")  # 순수 재빌드 모사.
    g = kg._merged_graph("P1")
    assert _rel(g, "eq:E1", "eq:E2")[0]["track"] == "curated"


def test_read_paths_see_merge(kg):
    # 공개 읽기 API(neighbors)도 reject 를 반영한다(내부 _merged_graph 배선 확인).
    kg.append_override("P1", kg.edge_key("eq:E2", "eq:E3"), "reject", actor=None, at=None, reason=None)
    r = kg.neighbors("P1", "eq:E2", depth=1)
    ids = {n["id"] for n in r["nodes"]}
    assert "eq:E3" not in ids  # reject 로 E2–E3 관계 사라짐 → E3 이웃 아님.
