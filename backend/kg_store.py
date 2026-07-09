"""지식그래프 스토어 (읽기·순회·무결성) — SoT는 uploads/_knowledge_graph.json.

TypeDB 와 물리 분리(온톨로지 원칙 LOCKED). 쓰기 시드는 scripts/build_knowledge_graph.py.
순회 알고리즘(neighbors/path BFS·evidence)을 여기 모아 라우트는 얇게 유지한다.
"""
from __future__ import annotations

import json
import logging
import os
from collections import deque
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger(__name__)

_PATH = Path(config.UPLOADS_DIR) / "_knowledge_graph.json"
_OVERLAY_PATH = Path(config.UPLOADS_DIR) / "_kg_overlay.json"


def _load() -> dict:
    if _PATH.exists():
        try:
            return json.loads(_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.error("지식그래프 스냅샷 파싱 실패(%s) → 빈 그래프 반환", _PATH)
    return {"graphs": {}}


def _graph(project: str) -> dict:
    return _load().get("graphs", {}).get(project, {"nodes": [], "edges": [], "built_at": None})


def _index(g: dict) -> dict:
    return {n["id"]: n for n in g.get("nodes", [])}


def _incident(g: dict, node_id: str) -> list:
    return [e for e in g.get("edges", []) if e["src"] == node_id or e["dst"] == node_id]


def get_node(project: str, node_id: str) -> dict:
    g = _merged_graph(project)
    n = _index(g).get(node_id)
    if n is None:
        return {"found": False, "id": node_id}
    return {"found": True, "node": n, "edges": _incident(g, node_id)}


def neighbors(project: str, node_id: str, depth: int = 1, types: Optional[list] = None) -> dict:
    """N홉 이웃(순회). depth 상한 5(폭주 방어). types 지정 시 그 노드 타입만 포함."""
    depth = max(1, min(int(depth), 5))
    g = _merged_graph(project)
    idx = _index(g)
    if node_id not in idx:
        return {"found": False, "id": node_id}
    seen = {node_id}
    frontier = {node_id}
    for _ in range(depth):
        nxt = set()
        for e in g.get("edges", []):
            for a, b in ((e["src"], e["dst"]), (e["dst"], e["src"])):
                if a in frontier and b not in seen:
                    nxt.add(b)
        seen |= nxt
        frontier = nxt
        if not frontier:
            break
    nodes = [idx[i] for i in seen if i in idx]
    if types:
        nodes = [n for n in nodes if n["type"] in types]
    # 반환 엣지 = 최종 노드 집합에 대한 유도 서브그래프(양 끝점이 모두 포함된 엣지만) → dangling 없음.
    kept = {n["id"] for n in nodes}
    edges_out = [e for e in g.get("edges", []) if e["src"] in kept and e["dst"] in kept]
    return {"found": True, "nodes": nodes, "edges": edges_out}


def path(project: str, src: str, dst: str) -> dict:
    """두 노드 최단 경로(BFS, 무방향)."""
    g = _merged_graph(project)
    idx = _index(g)
    if src not in idx or dst not in idx:
        return {"found": False, "from": src, "to": dst}
    adj: dict = {}
    for e in g.get("edges", []):
        adj.setdefault(e["src"], []).append((e["dst"], e))
        adj.setdefault(e["dst"], []).append((e["src"], e))
    q = deque([src])
    prev: dict = {src: None}
    while q:
        cur = q.popleft()
        if cur == dst:
            break
        for nb, e in adj.get(cur, []):
            if nb not in prev:
                prev[nb] = (cur, e)
                q.append(nb)
    if dst not in prev:
        return {"found": True, "from": src, "to": dst, "path": None, "reachable": False}
    chain = []
    node = dst
    while prev[node] is not None:
        cur, e = prev[node]
        chain.append({"edge": e})
        node = cur
    chain.reverse()
    return {"found": True, "from": src, "to": dst, "reachable": True,
            "hops": len(chain), "edges": [c["edge"] for c in chain]}


def evidence(project: str, node_id: str) -> dict:
    """근거체인 — 노드의 인접 엣지 evidence + 그 노드를 describes 하는 note."""
    g = _merged_graph(project)
    idx = _index(g)
    if node_id not in idx:
        return {"found": False, "id": node_id}
    ev = [{"edge": e["type"], "src": e["src"], "dst": e["dst"],
           "track": e["track"], "confidence": e["confidence"], "evidence": e.get("evidence")}
          for e in _incident(g, node_id) if e.get("evidence")]
    notes = [idx[e["src"]] for e in g.get("edges", [])
             if e["type"] == "describes" and e["dst"] == node_id and e["src"] in idx]
    return {"found": True, "id": node_id, "evidence": ev, "notes": notes}


def subgraph(project: str, scope: Optional[str] = None) -> dict:
    """시각화용 — scope 미지정 시 전체. scope=<node_id> 면 그 노드 2홉 이웃."""
    if scope:
        return neighbors(project, scope, depth=2)
    g = _merged_graph(project)
    return {"found": True, "nodes": g.get("nodes", []), "edges": g.get("edges", []),
            "built_at": g.get("built_at")}


def check_integrity(g: dict) -> list:
    """참조 무결성 — 모든 엣지 src/dst 가 노드로 존재해야. 위반 문자열 목록 반환."""
    ids = {n["id"] for n in g.get("nodes", [])}
    problems = []
    for e in g.get("edges", []):
        for end in ("src", "dst"):
            if e[end] not in ids:
                problems.append(f"dangling {e['type']} {end}={e[end]}")
    return problems


# ── 오버레이 저널 (⑥ write-back) ──────────────────────────────
def edge_key(a: str, b: str) -> str:
    """relates_to 무방향 정규화 키 — A↔B 동일. (relates_to 전용, 다른 엣지 타입엔 쓰지 않음.)"""
    lo, hi = sorted([a, b])
    return f"{lo}|{hi}|relates_to"


def _load_overlay() -> dict:
    if _OVERLAY_PATH.exists():
        try:
            data = json.loads(_OVERLAY_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
            logger.error("오버레이 저널이 dict 아님(%s) → 빈 오버레이 반환", _OVERLAY_PATH)
        except json.JSONDecodeError:
            logger.error("오버레이 저널 파싱 실패(%s) → 빈 오버레이 반환", _OVERLAY_PATH)
    return {"version": 1, "graphs": {}}


def _overlay_map(project: str) -> dict:
    """프로젝트 오버레이를 {edge_key: action} 로 축약(last-write-wins).

    같은 edge_key 에 override 가 여러 개면 리스트 마지막 항목이 유효.
    """
    overrides = _load_overlay().get("graphs", {}).get(project, {}).get("overrides", [])
    m: dict = {}
    for o in overrides:  # 리스트 순서대로 덮어쓰기 → 마지막이 이김.
        m[o["edge_key"]] = o["action"]
    return m


def append_override(project: str, key: str, action: str,
                    actor: Optional[str] = None, at: Optional[str] = None,
                    reason: Optional[str] = None) -> dict:
    """오버레이 저널에 override 1건 append(기존 항목 불변). 저장 후 그 항목 반환."""
    data = _load_overlay()
    graphs = data.setdefault("graphs", {})
    proj = graphs.setdefault(project, {"overrides": []})
    entry = {"edge_key": key, "action": action, "actor": actor, "at": at, "reason": reason}
    proj.setdefault("overrides", []).append(entry)
    _OVERLAY_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = _OVERLAY_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, _OVERLAY_PATH)
    return entry


def _merge(g: dict, omap: dict) -> dict:
    """스냅샷 그래프 g 에 오버레이 맵(omap: {edge_key: action})을 적용한 병합 그래프 반환.

    규칙(스펙 §4):
      - track != 'llm' → 무시(rule·curated 보호).
      - track == 'llm' + override 없음 → 그대로.
      - track == 'llm' + confirm → track 을 'curated' 로 치환.
      - track == 'llm' + reject → 결과에서 제외(drop).
      - dangling override(어느 엣지와도 안 맞음) → 조용히 무시(로그 경고).
    스냅샷 파일 자체는 변경하지 않는다(병합은 읽기 경로 메모리에서만).
    """
    out_edges = []
    matched = set()
    for e in g.get("edges", []):
        if e.get("track") != "llm" or e.get("type") != "relates_to":
            out_edges.append(e)
            continue
        key = edge_key(e["src"], e["dst"])
        action = omap.get(key)
        if action is None:
            out_edges.append(e)
        elif action == "confirm":
            matched.add(key)
            out_edges.append({**e, "track": "curated"})
        elif action == "reject":
            matched.add(key)
            # drop — 결과 목록에서 제외.
        else:  # 알 수 없는 action → 안전하게 원본 유지(매칭은 됐으므로 dangling 아님).
            matched.add(key)
            out_edges.append(e)
    dangling = set(omap) - matched
    if dangling:
        logger.debug("오버레이 dangling override 무시(%d건): %s",
                     len(dangling), ", ".join(sorted(dangling)[:5]))
    return {**g, "edges": out_edges}


def _merged_graph(project: str) -> dict:
    """순수 스냅샷(_graph) + 오버레이 병합 — 모든 읽기 경로의 단일 진입점."""
    return _merge(_graph(project), _overlay_map(project))
