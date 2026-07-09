"""시연 시드 — 스냅샷 두 설비 노드 사이 relates_to(llm, demo_seed) 엣지 1개 주입."""
import importlib
import json
import pathlib
import sys

import pytest

_SNAP = {"graphs": {"P1": {"built_at": None,
    "nodes": [
        {"id": "eq:E1", "type": "equipment", "ref_id": "E1", "label": "MTR-1", "props": {}},
        {"id": "eq:E2", "type": "equipment", "ref_id": "E2", "label": "VCB-1", "props": {}}],
    "edges": []}}}


@pytest.fixture()
def seed_mod(tmp_path, monkeypatch):
    monkeypatch.setenv("XD_UPLOADS_DIR", str(tmp_path))
    import config
    importlib.reload(config)
    (tmp_path / "_knowledge_graph.json").write_text(json.dumps(_SNAP), encoding="utf-8")
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
    import seed_demo_llm_edge as s
    importlib.reload(s)
    return s, tmp_path


def test_seed_injects_llm_relates_to(seed_mod):
    s, tmp = seed_mod
    s.seed("P1")
    snap = json.loads((tmp / "_knowledge_graph.json").read_text(encoding="utf-8"))
    edges = snap["graphs"]["P1"]["edges"]
    rel = [e for e in edges if e["type"] == "relates_to"]
    assert len(rel) == 1
    e = rel[0]
    assert e["track"] == "llm"
    assert e["props"]["demo_seed"] is True
    assert {e["src"], e["dst"]} == {"eq:E1", "eq:E2"}


def test_seed_idempotent(seed_mod):
    # 두 번 시드해도 demo_seed 엣지는 1개(중복 주입 방지).
    s, tmp = seed_mod
    s.seed("P1")
    s.seed("P1")
    snap = json.loads((tmp / "_knowledge_graph.json").read_text(encoding="utf-8"))
    rel = [e for e in snap["graphs"]["P1"]["edges"] if e["type"] == "relates_to"]
    assert len(rel) == 1
