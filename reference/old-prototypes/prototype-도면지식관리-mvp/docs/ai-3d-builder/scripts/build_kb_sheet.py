"""
stage-10-parsed.json (또는 consensus_*.json) → KB YAML 변환.

생성물:
- knowledge-base/sheets/{sheet_id}.yml  : 시트 단위 전체 데이터 + 앵커율/그리드 검증
- knowledge-base/level-stack.yml        : annotations_ko 에서 파싱한 FL mm 좌표

사용:
  python build_kb_sheet.py <input.json> <sheet_id> [--source-png <path>]

예:
  python build_kb_sheet.py ../outputs/consensus/consensus_p062.json arch_p062
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pyyaml"])
    import yaml

ROOT = Path(r"D:/_Project/prototype-도면지식관리-mvp")
KB_DIR = ROOT / "docs" / "ai-3d-builder" / "knowledge-base"
SHEETS_DIR = KB_DIR / "sheets"
PNG_DIR = ROOT / "dwg" / "1) 건축공사" / "0. PDF 도면" / "_png_dpi400"


def pct(n, total):
    return round(100 * n / total, 1) if total else 0.0


def compute_anchored_counts(view):
    elements = view.get("elements", []) or []
    dims = view.get("dimensions_raw", []) or []

    rooms = [e for e in elements if e.get("type") == "room"]
    walls = [e for e in elements if e.get("type") == "wall"]
    cores = [e for e in elements if e.get("type") in ("stair", "elevator", "shaft")]
    voids = [e for e in elements if e.get("type") == "void"]
    doors = [e for e in elements if e.get("type") == "door"]
    columns = [e for e in elements if e.get("type") == "column"]

    rooms_anchored = sum(1 for r in rooms if r.get("polygon_grid") and len(r.get("polygon_grid") or []) >= 3)
    walls_anchored = sum(1 for w in walls if w.get("path_grid") and len(w.get("path_grid") or []) >= 2)
    cores_anchored = sum(1 for c in cores if c.get("polygon_grid") or c.get("at_grid"))
    dims_anchored = sum(1 for d in dims if d.get("from_grid") and d.get("to_grid"))

    return {
        "rooms": {"total": len(rooms), "anchored": rooms_anchored, "pct": pct(rooms_anchored, len(rooms))},
        "walls": {"total": len(walls), "anchored": walls_anchored, "pct": pct(walls_anchored, len(walls))},
        "cores": {"total": len(cores), "anchored": cores_anchored, "pct": pct(cores_anchored, len(cores))},
        "voids": {"total": len(voids)},
        "doors": {"total": len(doors)},
        "columns": {"total": len(columns)},
        "dims": {"total": len(dims), "anchored": dims_anchored, "pct": pct(dims_anchored, len(dims))},
    }


def validate_grid(grid):
    xs = grid.get("x_spacings_mm") or []
    ys = grid.get("y_spacings_mm") or []
    x_labels = grid.get("x_labels") or []
    y_labels = grid.get("y_labels") or []
    xs_sum = sum(x for x in xs if isinstance(x, (int, float)))
    ys_sum = sum(y for y in ys if isinstance(y, (int, float)))
    return {
        "x_spacings_sum_mm": xs_sum,
        "y_spacings_sum_mm": ys_sum,
        "x_labels_count": len(x_labels),
        "y_labels_count": len(y_labels),
        "x_spacings_count": len(xs),
        "y_spacings_count": len(ys),
        "x_labels_vs_spacings_ok": len(x_labels) == len(xs) + 1 if xs else True,
        "y_labels_vs_spacings_ok": len(y_labels) == len(ys) + 1 if ys else True,
    }


def _to_int_mm_from_m(val_m):
    """94.20 → 94200"""
    return int(round(float(val_m) * 1000))


def parse_level_stack(annotations_ko):
    """
    annotations_ko 각 줄에서 레벨 이름 → mm 엘리베이션 추출.

    기본 레벨(±0 기준 절대값)과 파생 오프셋(RSFL+1800 등)을 분리해 저장.

    인정 패턴 (먼저 나오는 것이 우선):
      "2FL±0 FH+99.70"              → levels["2FL"] = 99700
      "GL±0=EL+94.00"               → levels["GL"]  = 94000
      "RFL±0=1FL+10,000=EL+104.20"  → levels["RFL"] = 104200 (체인의 마지막 EL+)
      "RSFL+1,800 FH+106.00"        → offsets["RSFL+1800"] = 106000
      "RFL+200 FH+104.50"           → offsets["RFL+200"]   = 104500

    원칙: 이름 뒤 "±0" 이 붙은 경우만 절대 기본 레벨로 인정.
          이름 뒤 "+숫자" 는 오프셋 파생 키로 분리.
    """
    levels = {}
    offsets = {}

    name_re = r"(?:GL|[1-9]\d*FL|RFL|RSFL)"

    # 기본 절대: "<name>±0 ... FH+xx.xx" (이름과 FH 사이에 등호 없음)
    pat_fh_base = re.compile(rf"({name_re})\s*±\s*0?\s+FH\s*\+\s*(\d+(?:\.\d+)?)")

    # 기본 절대: "<name>±0 = ... EL+xx.xx" (중간에 체인 허용, 마지막 EL+ 만 잡음)
    pat_el_base = re.compile(
        rf"({name_re})\s*±\s*0?\s*=\s*(?:[^=,\n]*?=\s*)*EL\s*\+\s*(\d+(?:\.\d+)?)"
    )

    # 오프셋: "<name>+<offset_mm> FH+xx.xx" 또는 EL+xx.xx
    pat_offset_fh = re.compile(
        rf"({name_re})\s*\+\s*(\d+(?:,\d+)?)\s+FH\s*\+\s*(\d+(?:\.\d+)?)"
    )
    pat_offset_el = re.compile(
        rf"({name_re})\s*\+\s*(\d+(?:,\d+)?)\s*=\s*(?:[^=,\n]*?=\s*)*EL\s*\+\s*(\d+(?:\.\d+)?)"
    )

    for ann in annotations_ko:
        for m in pat_fh_base.finditer(ann):
            name = m.group(1)
            levels.setdefault(name, _to_int_mm_from_m(m.group(2)))
        for m in pat_el_base.finditer(ann):
            name = m.group(1)
            levels.setdefault(name, _to_int_mm_from_m(m.group(2)))
        for m in pat_offset_fh.finditer(ann):
            base_name = m.group(1)
            offset_mm = int(m.group(2).replace(",", ""))
            abs_m = float(m.group(3))
            offsets[f"{base_name}+{offset_mm}"] = _to_int_mm_from_m(abs_m)
        for m in pat_offset_el.finditer(ann):
            base_name = m.group(1)
            offset_mm = int(m.group(2).replace(",", ""))
            abs_m = float(m.group(3))
            offsets.setdefault(f"{base_name}+{offset_mm}", _to_int_mm_from_m(abs_m))

    # 파생 FFH (인접 층간 높이) — 기본 레벨만 대상
    floor_order = ["GL", "1FL", "2FL", "3FL", "4FL", "5FL", "RFL"]
    ffh = {}
    prev_name = None
    for fn in floor_order:
        if fn in levels:
            if prev_name is not None:
                ffh[f"{prev_name}→{fn}"] = levels[fn] - levels[prev_name]
            prev_name = fn

    return {
        "levels_mm": levels,
        "offsets_mm": offsets,
        "ffh_mm": ffh,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_json", help="stage-10-parsed.json 또는 consensus_*.json 경로")
    ap.add_argument("sheet_id", help="예: arch_p062")
    ap.add_argument("--source-png", help="원본 PNG 경로 (지정 없으면 _png_dpi400/{sheet_id}.png)")
    args = ap.parse_args()

    input_path = Path(args.input_json)
    if not input_path.exists():
        print(f"입력 파일 없음: {input_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    source_png = args.source_png or str(PNG_DIR / f"{args.sheet_id}.png")

    views_out = []
    all_annotations = []

    for v in data.get("views", []):
        grid_val = validate_grid(v.get("grid", {}))
        anchored = compute_anchored_counts(v)
        anns = v.get("annotations_ko", []) or []
        all_annotations.extend(anns)

        views_out.append({
            "view_id": v.get("view_id"),
            "view_label": v.get("view_label"),
            "view_scale": v.get("view_scale"),
            "level": v.get("level", {}) or {},
            "grid": v.get("grid", {}) or {},
            "grid_validation": grid_val,
            "anchored_counts": anchored,
            "elements": v.get("elements", []) or [],
            "dimensions_raw": v.get("dimensions_raw", []) or [],
            "annotations_ko": anns,
            "unresolved": v.get("unresolved", []) or [],
        })

    level_stack = parse_level_stack(all_annotations)

    sheet_yaml = {
        "sheet_id": args.sheet_id,
        "sheet_number": data.get("sheet_number"),
        "source_png": source_png,
        "discipline": "architectural",
        "extraction_source": str(input_path.resolve()).replace("\\", "/"),
        "global_confidence": data.get("global_confidence"),
        "views": views_out,
    }

    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    out_sheet = SHEETS_DIR / f"{args.sheet_id}.yml"
    out_sheet.write_text(
        yaml.safe_dump(sheet_yaml, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8"
    )

    KB_DIR.mkdir(parents=True, exist_ok=True)
    out_levels = KB_DIR / "level-stack.yml"
    out_levels.write_text(
        yaml.safe_dump(level_stack, allow_unicode=True, sort_keys=False),
        encoding="utf-8"
    )

    print(f"saved: {out_sheet}")
    print(f"saved: {out_levels}")
    print()
    print("---- anchored counts ----")
    for v in views_out:
        print(f"  {v['view_id']} ({v['view_label']}):")
        for k, val in v["anchored_counts"].items():
            if isinstance(val, dict):
                if "pct" in val:
                    print(f"    {k}: {val.get('anchored', 0)}/{val.get('total', 0)} ({val.get('pct', 0)}%)")
                else:
                    print(f"    {k}: {val.get('total', 0)}")
    print()
    print("---- level stack ----")
    print(json.dumps(level_stack, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
