"""
Stage 4 — 모델링 순서 DAG 빌드.

입력:
  knowledge-base/indexes/floor_to_sheets.yml
  knowledge-base/indexes/building_to_floors.yml
  knowledge-base/classifications.json
  knowledge-base/level-stack.yml (선택, 기존 KB)

출력:
  knowledge-base/indexes/modeling_order.yml

규칙:
  1. reference_floor = 지상1층 (그리드·FL datum 수립)
  2. queue 순서: reference plan → 같은 층 보완 plan → 다른 층 plans → cross-cutting
  3. 각 step 에 needs/produces/validates 명시
  4. blocked 에 3D에 필수지만 부재인 정보 기록
"""
import json
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import yaml

ROOT = Path(r"D:/_Project/prototype-도면지식관리-mvp")
KB_DIR = ROOT / "docs" / "ai-3d-builder" / "knowledge-base"
IDX_DIR = KB_DIR / "indexes"

FLOOR_SHEETS_PATH = IDX_DIR / "floor_to_sheets.yml"
BUILDING_PATH = IDX_DIR / "building_to_floors.yml"
CLASS_PATH = KB_DIR / "classifications.json"
LEVEL_STACK_PATH = KB_DIR / "level-stack.yml"

OUT_PATH = IDX_DIR / "modeling_order.yml"

REFERENCE_FLOOR = "지상1층"


def load_all():
    floor_sheets = yaml.safe_load(FLOOR_SHEETS_PATH.read_text(encoding="utf-8"))
    building = yaml.safe_load(BUILDING_PATH.read_text(encoding="utf-8"))
    classifications = json.loads(CLASS_PATH.read_text(encoding="utf-8"))
    level_stack = None
    if LEVEL_STACK_PATH.exists():
        level_stack = yaml.safe_load(LEVEL_STACK_PATH.read_text(encoding="utf-8"))
    return floor_sheets, building, classifications, level_stack


def main():
    floor_sheets, building, classifications, level_stack = load_all()

    floor_stack = building["floor_stack_ordered"]
    if REFERENCE_FLOOR not in floor_stack:
        print(f"[!] reference floor '{REFERENCE_FLOOR}' 층 스택에 없음 — 첫 번째 사용")
        ref_floor = floor_stack[0]
    else:
        ref_floor = REFERENCE_FLOOR

    queue = []
    step_no = 0

    def add_step(**kw):
        nonlocal step_no
        step_no += 1
        queue.append({"step": step_no, **kw})

    # ---- Priority 1: reference floor 의 첫 plan = baseline
    ref_plans = floor_sheets.get(ref_floor, {}).get("plans", [])
    if not ref_plans:
        print(f"[!] reference floor '{ref_floor}' 에 plan 없음")
    else:
        first = ref_plans[0]
        add_step(
            sheet=first["ref"],
            sheet_number=first["sheet_number"],
            role="baseline_plan",
            floor=ref_floor,
            produces=["grid_mm", "FL_datum", f"slab_polygon_{ref_floor}", f"rooms_{ref_floor}"],
            needs=[],
            validates=None,
            notes=f"{ref_floor} 기준 평면. 그리드·FL datum 수립.",
        )
        # 같은 층 보완 plans
        for p in ref_plans[1:]:
            add_step(
                sheet=p["ref"],
                sheet_number=p["sheet_number"],
                role="supplementary_plan",
                floor=ref_floor,
                produces=[f"rooms_{ref_floor}_extra", f"slab_extension_{ref_floor}"],
                needs=["grid_mm", "FL_datum"],
                validates="grid_consistency(prev_step, this)",
                notes=f"{ref_floor} 보완 평면. 기준 그리드와 일치 확인.",
            )

    # ---- Priority 2: 다른 층 plans (층 스택 순)
    for floor in floor_stack:
        if floor == ref_floor:
            continue
        plans = floor_sheets.get(floor, {}).get("plans", [])
        for pi, p in enumerate(plans):
            role = "floor_plan" if pi == 0 else "supplementary_plan"
            add_step(
                sheet=p["ref"],
                sheet_number=p["sheet_number"],
                role=role,
                floor=floor,
                produces=[f"slab_polygon_{floor}", f"rooms_{floor}"],
                needs=["grid_mm", "FL_datum"],
                validates=f"grid_consistency(ref, {floor})" if pi == 0 else f"grid_consistency(prev_step, this)",
                notes=f"{floor} 평면. 기준 그리드 재사용.",
            )

    # ---- Priority 3: cross-cutting sections
    stair_entries = floor_sheets.get("전층관통-계단실", {}).get("stair", [])
    stair_plans = [e for e in stair_entries if e.get("role") == "plan"]
    stair_sections = [e for e in stair_entries if e.get("role") == "section"]

    for sp in stair_plans:
        add_step(
            sheet=sp["ref"],
            sheet_number=sp["sheet_number"],
            role="vertical_core_plan",
            floor="전층관통",
            produces=["stair_polygon", "ev_polygon"],
            needs=["grid_mm"],
            validates="stair_consistency_across_floors",
            notes="계단실 수평 위치 — 모든 층에 걸친 수직 관통.",
        )

    for ss in stair_sections:
        add_step(
            sheet=ss["ref"],
            sheet_number=ss["sheet_number"],
            role="vertical_section",
            floor="전층관통",
            produces=["FFH_per_floor", "slab_thickness", "parapet_height", "stair_height"],
            needs=["FL_datum", "stair_polygon"],
            validates="FL_consistency(section vs annotations)",
            notes="★ Z축 정보의 주 소스. 슬라브 두께·층간 높이·옥탑 파라펫.",
        )

    # ---- Priority 4: elevations (faces)
    # 실제 입면도가 있다면 추가. 현재 cross-cutting 에 "전층-입면" 으로 분류된 p121/p122 는 "무창층 검토서"로 elevation 오분류. skip.

    # ---- blocked 식별
    blocked = []

    if not stair_sections:
        blocked.append({
            "missing": "층 단면도",
            "impact": "FFH 는 level-stack.yml 값 사용, 슬라브 두께 기본 250mm 가정",
        })

    # elevation (p121/p122 는 무창층 검토서 — 실제 입면도 아님)
    real_elevations = [
        e for f in floor_sheets.values()
        for e in f.get("elevations", [])
        if "무창층" not in e.get("raw", "")
    ]
    if not real_elevations:
        blocked.append({
            "missing": "건물 입면도 (정입면·측입면)",
            "impact": "외벽 마감·창호 개구부 반영 불가. 박스 매싱으로 근사.",
            "note": "p121/p122 는 '무창층 검토서'로 elevation 오분류 — 실제 입면도 아님.",
        })

    # RCP (반자 평면도 — 천장고)
    blocked.append({
        "missing": "RCP (반자 평면도)",
        "impact": "각 실별 천장고 추정 불가. 실 높이 = FFH 에서 균일 2700mm 가정.",
    })

    # detail sheets (슬라브 두께, 마감 상세)
    blocked.append({
        "missing": "외벽 상세도, 슬라브 상세도",
        "impact": "외벽 두께 200mm 기본값 사용. 슬라브 두께 단면도 값 또는 250mm.",
    })

    # 3D 비후보 시트 중 재참조 가능한 것
    secondary_refs = []
    for sid, rec in classifications.items():
        if rec.get("is_3d_candidate") is False:
            vtype = rec.get("view_type")
            if vtype in ("schedule_table",):
                title = rec.get("sheet_title") or ""
                if "창호" in title or "열관류" in title or "외창" in title:
                    secondary_refs.append({
                        "sheet_id": sid,
                        "sheet_number": rec.get("sheet_number"),
                        "title": title,
                        "use_for": "창호 개구부 위치·크기 참고 (있으면 이용, 없으면 skip)",
                    })

    # ---- final output
    output = {
        "baseline": {
            "reference_floor": ref_floor,
            "reference_sheet": queue[0]["sheet"] if queue else None,
            "rationale": "지상1층의 첫 평면에서 그리드와 FL datum 을 수립. 이후 모든 층이 동일 그리드로 정렬되는지 검증.",
            "floor_stack_ordered": floor_stack,
            "level_stack_source": str(LEVEL_STACK_PATH.relative_to(ROOT)).replace("\\", "/") if level_stack else None,
            "level_stack": level_stack,
        },
        "queue": queue,
        "blocked": blocked,
        "secondary_refs": secondary_refs,
        "meta": {
            "planned_at": datetime.now().isoformat(timespec="seconds"),
            "queue_length": len(queue),
            "blocked_count": len(blocked),
        },
    }

    IDX_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        yaml.dump(output, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )

    print(f"[plan_modeling_order] 완료")
    print(f"  queue 길이: {len(queue)}")
    for s in queue:
        print(f"    step {s['step']}: {s['sheet']} ({s['role']}) — {s['floor']}")
    print(f"  blocked: {len(blocked)}")
    for b in blocked:
        print(f"    - {b['missing']}: {b['impact']}")
    print(f"  secondary_refs: {len(secondary_refs)}")
    print(f"  저장: {OUT_PATH}")


if __name__ == "__main__":
    main()
