"""지식그래프 빌드 — 투영 노드/엣지 + AI relates_to 병합, 참조 무결성."""
import importlib

import pytest


@pytest.fixture()
def build_mod(tmp_path, monkeypatch):
    monkeypatch.setenv("XD_UPLOADS_DIR", str(tmp_path))
    import config
    importlib.reload(config)
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
    import build_knowledge_graph as b
    importlib.reload(b)
    return b


def test_build_projects_and_merges_relations(build_mod, monkeypatch):
    b = build_mod
    # 8000/8002 접근을 스텁으로.
    monkeypatch.setattr(b, "_fetch_equipment", lambda p: [
        {"equipment_id": "E1", "tag": "MTR-1", "type": "motor", "sheet_ids": ["s1"]},
        {"equipment_id": "E2", "tag": "VCB-1", "type": "breaker", "sheet_ids": ["s1"]}])
    monkeypatch.setattr(b, "_fetch_sheets", lambda p: [{"sheet_id": "s1", "title": "E-101", "tags": [{"tag": "MTR-1"}, {"tag": "VCB-1"}]}])
    monkeypatch.setattr(b, "_fetch_issues", lambda p: [])
    monkeypatch.setattr(b, "_fetch_tasks", lambda p: [])
    monkeypatch.setattr(b, "_fetch_files", lambda p: [])
    monkeypatch.setattr(b, "_call_analyze", lambda eq, sh: {
        "relations": [{"src_tag": "MTR-1", "dst_tag": "VCB-1", "relation": "relates_to",
                       "confidence": 0.5, "evidence": "같은 시트"}], "notes": []})
    g = b.build_graph("P1", built_at="2026-07-09T00:00:00")
    ids = {n["id"] for n in g["nodes"]}
    assert {"eq:E1", "eq:E2", "sh:s1", "tg:MTR-1", "tg:VCB-1"} <= ids
    etypes = sorted({e["type"] for e in g["edges"]})
    assert "appears_on" in etypes and "has_tag" in etypes and "relates_to" in etypes
    # AI 관계는 track=llm.
    rel = [e for e in g["edges"] if e["type"] == "relates_to"][0]
    assert rel["track"] == "llm" and rel["src"] == "eq:E1" and rel["dst"] == "eq:E2"
    # 무결성 위반 0.
    import kg_store
    assert kg_store.check_integrity(g) == []


def test_note_id_is_stable_content_hash(build_mod, monkeypatch):
    b = build_mod
    monkeypatch.setattr(b, "_fetch_equipment", lambda p: [
        {"equipment_id": "E1", "tag": "MTR-1", "type": "motor", "sheet_ids": []}])
    for fn in ("_fetch_sheets", "_fetch_issues", "_fetch_tasks", "_fetch_files"):
        monkeypatch.setattr(b, fn, lambda p: [])
    monkeypatch.setattr(b, "_call_analyze", lambda eq, sh: {
        "relations": [],
        "notes": [{"about_tag": "MTR-1", "text": "정격 15kW 모터", "confidence": 0.5}]})
    g = b.build_graph("P1", built_at="2026-07-09T00:00:00")
    # 기대 note id = content sha256 파생(프로세스 해시시드 무관하게 결정적).
    import hashlib
    expected = "nt:" + hashlib.sha256("MTR-1|정격 15kW 모터".encode("utf-8")).hexdigest()[:16]
    note_nodes = [n for n in g["nodes"] if n["type"] == "note"]
    assert len(note_nodes) == 1
    assert note_nodes[0]["id"] == expected and note_nodes[0]["id"].startswith("nt:")
    desc = [e for e in g["edges"] if e["type"] == "describes"]
    assert len(desc) == 1
    assert desc[0]["src"] == expected and desc[0]["dst"] == "eq:E1" and desc[0]["track"] == "llm"


def test_build_persists_snapshot(build_mod, monkeypatch, tmp_path):
    b = build_mod
    for fn in ("_fetch_equipment", "_fetch_sheets", "_fetch_issues", "_fetch_tasks", "_fetch_files"):
        monkeypatch.setattr(b, fn, lambda p: [])
    monkeypatch.setattr(b, "_call_analyze", lambda eq, sh: {"relations": [], "notes": []})
    b.build_and_save("P1", built_at="2026-07-09T00:00:00")
    import json
    snap = json.loads((tmp_path / "_knowledge_graph.json").read_text(encoding="utf-8"))
    assert "P1" in snap["graphs"]


def test_call_analyze_forwards_sheet_ids(build_mod, monkeypatch):
    """slim_eq 가 sheet_ids 를 8002 로 넘겨야 provider 가 공존을 계산할 수 있다(변경점 1)."""
    b = build_mod
    captured = {}
    monkeypatch.setattr(b, "_post",
                        lambda url, body: (captured.update(body), {"relations": [], "notes": []})[1])
    b._call_analyze(
        [{"tag": "MTR-1", "type": "motor", "sheet_ids": ["s1", "s2"]}], [])
    assert captured["equipment"][0]["sheet_ids"] == ["s1", "s2"]
    assert captured["equipment"][0]["tag"] == "MTR-1"
