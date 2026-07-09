"""시연 전용 시드 — 개발 스냅샷에 relates_to(track=llm) 엣지 1개 주입.

⚠️ 실데이터 아님. relates_to(llm)=0(설비 큐레이트태그 ∩ 시트 추출태그 겹침 0) 현실에서
write-back UI·통합 스모크가 볼 llm 엣지를 만들기 위한 개발 편의 스크립트다.
주입 엣지는 props.demo_seed=true 로 표식. 재빌드하면 사라진다(정상 — 시연 후 청소).
mock확장/GATE-7 트랙이 실 relates_to 를 공급하면 이 시드는 불필요.

사용: python scripts/seed_demo_llm_edge.py <project_name>
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import config  # noqa: E402

_SNAP = Path(config.UPLOADS_DIR) / "_knowledge_graph.json"


def seed(project: str) -> dict:
    """지정 프로젝트의 앞선 두 설비 노드 사이에 demo relates_to(llm) 엣지 1개 주입(멱등)."""
    snap = json.loads(_SNAP.read_text(encoding="utf-8"))
    g = snap.get("graphs", {}).get(project)
    if not g:
        raise SystemExit(f"프로젝트 없음: {project} (먼저 build_knowledge_graph.py 실행)")
    eqs = [n for n in g["nodes"] if n["type"] == "equipment"]
    if len(eqs) < 2:
        raise SystemExit(f"설비 노드 2개 미만 — 시드 불가(project={project})")
    a, b = eqs[0]["id"], eqs[1]["id"]
    # 멱등: 이미 demo_seed 엣지가 있으면 재주입 안 함.
    for e in g["edges"]:
        if e["type"] == "relates_to" and (e.get("props") or {}).get("demo_seed"):
            print(f"이미 시드됨: {e['src']}↔{e['dst']}")
            return snap
    g["edges"].append({
        "src": a, "dst": b, "type": "relates_to", "confidence": 0.55, "track": "llm",
        "evidence": "[DEMO SEED] 시연용 AI 제안 관계(실데이터 아님)",
        "props": {"demo_seed": True},
    })
    tmp = _SNAP.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, _SNAP)
    print(f"시드 주입: {a} ↔ {b} (relates_to, llm, demo_seed)")
    return snap


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: seed_demo_llm_edge.py <project_name>")
        sys.exit(2)
    seed(sys.argv[1])
