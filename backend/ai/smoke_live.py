"""라이브 스모크 (S8.0 K5·K10) — 실기동 8000 대상 end-to-end 그라운딩 증명.

전제: 8000이 127.0.0.1:8000에 기동 + 대상 프로젝트에 최소 1개 도면 업로드(완료).
health는 연결성만, tools.list_sheets가 실 시트 수를 반환함을 입증한다.
8000 반환값과 일치하면 합격(0장도 실값, 하드코딩 카운트만 불합격).

    .venv/Scripts/python.exe smoke_live.py [PROJECT]
"""
from __future__ import annotations

import json
import sys

import client
import tools


def main(project: str = "Study_Project") -> int:
    print(f"[smoke] base={client.base_url()} project={project}")

    # 1) 연결성 — get_me (health가 쓰는 프로브).
    me = client.get_me()
    print(f"[smoke] current_user={me.get('member_id')}")

    # 2) 그라운딩 — 툴이 실 시트 수를 반환.
    sheets = tools.list_sheets(project)
    print(f"[smoke] list_sheets count={sheets['count']}")
    for s in sheets["sheets"][:5]:
        print(f"          - {s['number']} · {s['title']} [{s['discipline_code']}] id={s['sheet_id']}")

    # 3) 교차 검증 — 8000 raw /api/drawings 시트 합과 일치(툴이 하드코딩 아님).
    raw = client.get("/api/drawings", params={"project_name": project})
    raw_count = sum(
        len(d.get("sheets") or [])
        for d in raw
        if d.get("conversion_status") == "completed"
    )
    print(f"[smoke] raw completed-sheet count={raw_count}")
    assert sheets["count"] == raw_count, (
        f"툴 카운트({sheets['count']}) != 8000 raw({raw_count}) — 하드코딩/매핑 불일치"
    )

    # 4) 검색 툴 라이브(빈 쿼리 방어 — 프로젝트명 일부로 시트 검색).
    q = project.split("_")[0]
    res = tools.search(project, q)
    print(f"[smoke] search q={q!r} sheets={len(res['sheets'])} files={len(res['files'])}")

    print("[smoke] OK (툴 카운트 == 8000 raw)")
    print(json.dumps({"count": sheets["count"], "raw": raw_count, "user": me.get("member_id")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(*(sys.argv[1:2] or ["Study_Project"])))
