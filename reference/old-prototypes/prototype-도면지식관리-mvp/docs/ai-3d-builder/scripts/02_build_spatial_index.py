"""
Stage 2+3 — 공간 그룹핑 + 뷰타입 인덱스 빌드.

입력: knowledge-base/classifications.json (Stage 1 산출)
출력:
  knowledge-base/indexes/floor_to_sheets.yml   (Stage 2)
  knowledge-base/indexes/view_type_index.yml   (Stage 3)
  knowledge-base/indexes/building_to_floors.yml (보너스 — 층 스택 요약)

로직:
  - sheet_title 괄호 안 콤마 분리로 다중 뷰 감지 ("PIT, 지상1층" → v1=PIT, v2=1F)
  - 층 키워드 매칭 (지상N층 / 옥탑 / PIT / 계단실)
  - view_type 으로 평면·단면·입면·상세 분류
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pyyaml"])
    import yaml

ROOT = Path(r"D:/_Project/prototype-도면지식관리-mvp")
KB_DIR = ROOT / "docs" / "ai-3d-builder" / "knowledge-base"
IDX_DIR = KB_DIR / "indexes"
CLASS_PATH = KB_DIR / "classifications.json"


FLOOR_PATTERNS = [
    (re.compile(r"지상\s*(\d+)\s*층"), lambda m: f"지상{m.group(1)}층"),
    (re.compile(r"지하\s*(\d+)\s*층"), lambda m: f"지하{m.group(1)}층"),
    (re.compile(r"옥탑"), lambda m: "옥탑"),
    (re.compile(r"지붕"), lambda m: "옥탑"),
    (re.compile(r"PIT", re.IGNORECASE), lambda m: "PIT"),
]

SPECIAL_TOKENS = {
    "계단실": "stair",
    "외창호": "window",
    "창호": "window",
}


def extract_views(sheet_title):
    """
    sheet_title 분석 → [{label: '1층', raw: '지상1층'}, ...]
    괄호 안 콤마 분리로 다중 뷰 감지.
    반환 리스트 비면 [{label: '-', raw: sheet_title}] (전체 시트 1 뷰).
    """
    if not sheet_title:
        return [{"label": "unknown", "raw": "", "tokens": []}]

    paren_match = re.search(r"\(([^)]+)\)", sheet_title)
    views_raw = []
    if paren_match:
        parts = [p.strip() for p in paren_match.group(1).split(",")]
        for p in parts:
            views_raw.append(p)
    else:
        views_raw.append(sheet_title)

    views = []
    for raw in views_raw:
        floor_label = None
        for pat, builder in FLOOR_PATTERNS:
            m = pat.search(raw)
            if m:
                floor_label = builder(m)
                break
        special = None
        for tok, tag in SPECIAL_TOKENS.items():
            if tok in raw or tok in sheet_title:
                special = tag
                break
        views.append({
            "label": floor_label or special or raw,
            "raw": raw,
            "floor": floor_label,
            "special": special,
        })
    return views


def floor_order_key(floor):
    """지상1층 < 지상2층 < 옥탑, PIT 먼저, 기타 나중."""
    if floor == "PIT":
        return (-1, 0)
    if floor and floor.startswith("지하"):
        n = int(re.search(r"\d+", floor).group())
        return (0, -n)
    if floor and floor.startswith("지상"):
        n = int(re.search(r"\d+", floor).group())
        return (1, n)
    if floor == "옥탑":
        return (2, 0)
    return (3, 0)


def main():
    data = json.loads(CLASS_PATH.read_text(encoding="utf-8"))

    sheets_3d = {}
    sheets_non3d = {}
    per_sheet_views = {}

    for sheet_id, rec in data.items():
        if "_error" in rec:
            print(f"[skip] {sheet_id}: {rec['_error']}")
            continue
        if rec.get("is_3d_candidate") is True:
            sheets_3d[sheet_id] = rec
        else:
            sheets_non3d[sheet_id] = rec
        per_sheet_views[sheet_id] = extract_views(rec.get("sheet_title", ""))

    # ---------------- Stage 2: floor_to_sheets.yml ----------------
    floor_to_sheets = {}

    def ensure(floor):
        if floor not in floor_to_sheets:
            floor_to_sheets[floor] = {
                "plans": [],
                "sections_through": [],
                "elevations": [],
                "details": [],
                "stair": [],
            }
        return floor_to_sheets[floor]

    for sheet_id, rec in sheets_3d.items():
        vtype = rec.get("view_type")
        views = per_sheet_views[sheet_id]
        sheet_number = rec.get("sheet_number") or sheet_id
        for vi, v in enumerate(views, 1):
            ref = f"{sheet_id}#v{vi}"
            label = v["label"]
            floor = v["floor"]
            special = v["special"]

            if vtype in ("floor_plan", "enlarged_plan"):
                if floor:
                    ensure(floor)["plans"].append({
                        "ref": ref, "sheet_number": sheet_number, "raw": v["raw"],
                    })
                elif special == "stair":
                    ensure("전층관통-계단실")["stair"].append({
                        "ref": ref, "sheet_number": sheet_number, "raw": v["raw"],
                        "role": "plan",
                    })
                else:
                    ensure("미배정").setdefault("plans", []).append({
                        "ref": ref, "sheet_number": sheet_number, "raw": v["raw"],
                    })
            elif vtype == "section":
                # section 은 어느 층을 가로지르는지 미정 — 후속 처리로 남김
                # 현재는 "전층관통-단면" 바구니
                target_floor = floor or "전층관통-단면"
                if special == "stair":
                    target_floor = "전층관통-계단실"
                    ensure(target_floor)["stair"].append({
                        "ref": ref, "sheet_number": sheet_number, "raw": v["raw"],
                        "role": "section",
                    })
                else:
                    ensure(target_floor)["sections_through"].append({
                        "ref": ref, "sheet_number": sheet_number, "raw": v["raw"],
                    })
            elif vtype == "elevation":
                target_floor = floor or "전층-입면"
                if special == "window":
                    ensure("창호일람").setdefault("elevations", []).append({
                        "ref": ref, "sheet_number": sheet_number, "raw": v["raw"],
                        "role": "window_schedule",
                    })
                else:
                    ensure(target_floor)["elevations"].append({
                        "ref": ref, "sheet_number": sheet_number, "raw": v["raw"],
                    })
            elif vtype == "detail":
                ensure("상세").setdefault("details", []).append({
                    "ref": ref, "sheet_number": sheet_number, "raw": v["raw"],
                })

    ordered_floors = sorted(floor_to_sheets.keys(),
                            key=lambda f: floor_order_key(f) if f.startswith(("지상", "지하", "옥탑", "PIT")) else (99, f))

    floor_yaml = {f: floor_to_sheets[f] for f in ordered_floors}

    # ---------------- Stage 3: view_type_index.yml ----------------
    view_index = {
        "plans": [],
        "enlarged_plans": [],
        "sections": [],
        "elevations": [],
        "details": [],
        "schedule_tables": [],
        "indexes": [],
        "covers": [],
        "other": [],
    }
    for sheet_id, rec in data.items():
        if "_error" in rec:
            continue
        vtype = rec.get("view_type")
        entry = {
            "sheet_id": sheet_id,
            "sheet_number": rec.get("sheet_number"),
            "title": rec.get("sheet_title"),
            "is_3d_candidate": rec.get("is_3d_candidate"),
        }
        bucket_map = {
            "floor_plan": "plans",
            "enlarged_plan": "enlarged_plans",
            "section": "sections",
            "elevation": "elevations",
            "detail": "details",
            "schedule_table": "schedule_tables",
            "index": "indexes",
            "cover": "covers",
        }
        view_index.setdefault(bucket_map.get(vtype, "other"), []).append(entry)

    # ---------------- building_to_floors.yml (보너스) ----------------
    building_summary = {
        "building": "LS Electric R-Center",
        "classified_at": datetime.now().isoformat(timespec="seconds"),
        "source": str(CLASS_PATH.relative_to(ROOT)).replace("\\", "/"),
        "total_sheets": len(data),
        "is_3d_candidate_count": len(sheets_3d),
        "floor_stack_ordered": [
            f for f in ordered_floors
            if f.startswith(("지상", "지하", "옥탑", "PIT"))
        ],
        "cross_cutting": [
            f for f in ordered_floors
            if f.startswith(("전층", "창호", "상세", "미배정"))
        ],
    }

    # ---------------- Save ----------------
    IDX_DIR.mkdir(parents=True, exist_ok=True)

    def dump(path, obj):
        path.write_text(
            yaml.dump(obj, allow_unicode=True, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )
        print(f"  -> {path.relative_to(ROOT)}")

    dump(IDX_DIR / "floor_to_sheets.yml", floor_yaml)
    dump(IDX_DIR / "view_type_index.yml", view_index)
    dump(IDX_DIR / "building_to_floors.yml", building_summary)

    # ---------------- Report ----------------
    print("\n[stage 2+3] 요약")
    print(f"  총 시트: {len(data)}")
    print(f"  3D 후보: {len(sheets_3d)}")
    print(f"  3D 비후보: {len(sheets_non3d)}")
    print(f"  층 스택: {building_summary['floor_stack_ordered']}")
    print(f"  cross-cutting: {building_summary['cross_cutting']}")
    print(f"  뷰타입별:")
    for k, v in view_index.items():
        if v:
            print(f"    {k}: {len(v)}장")


if __name__ == "__main__":
    main()
