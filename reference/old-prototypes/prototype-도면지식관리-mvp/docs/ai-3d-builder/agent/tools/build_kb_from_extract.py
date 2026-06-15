"""build_kb_from_extract — stage-10 parsed JSON → sheets/{id}.yml + level-stack.yml 갱신."""
import importlib.util
import json
import sys
from pathlib import Path

from .base import SCRIPTS_DIR, SHEETS_DIR, KB_DIR, ROOT, rel

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pyyaml"])
    import yaml


# build_kb_sheet.py 의 순수 함수들을 import (main() 은 우회)
_spec = importlib.util.spec_from_file_location(
    "_build_kb_sheet", SCRIPTS_DIR / "build_kb_sheet.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

compute_anchored_counts = _mod.compute_anchored_counts
validate_grid = _mod.validate_grid
parse_level_stack = _mod.parse_level_stack


SCHEMA = {
    "name": "build_kb_from_extract",
    "description": (
        "extract_sheet가 만든 stage-10-parsed.json(또는 기존 consensus JSON)을 KB YAML로 변환한다. "
        "결과: knowledge-base/sheets/{sheet_id}.yml (앵커율·그리드 검증 포함) "
        "+ knowledge-base/level-stack.yml (annotations_ko에서 파싱한 FL mm). "
        "extract_sheet 의 output_dir/stage-10-parsed.json 을 input_json_path 로 넘기면 된다."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "input_json_path": {
                "type": "string",
                "description": "stage-10-parsed.json 또는 consensus JSON 의 ROOT 기준 상대경로 또는 절대경로.",
            },
            "sheet_id": {
                "type": "string",
                "description": "예: arch_p062",
            },
            "source_png": {
                "type": "string",
                "description": "선택. 미지정 시 _png_dpi400/{sheet_id}.png.",
            },
        },
        "required": ["input_json_path", "sheet_id"],
    },
}


def execute(tool_input, context=None):
    input_raw = tool_input.get("input_json_path")
    sheet_id = tool_input.get("sheet_id")
    source_png = tool_input.get("source_png")
    if not input_raw or not sheet_id:
        return {"error": "input_json_path와 sheet_id 필수"}

    input_path = Path(input_raw)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    if not input_path.exists():
        return {"error": f"입력 파일 없음: {input_path}"}

    data = json.loads(input_path.read_text(encoding="utf-8"))
    if not source_png:
        source_png = str(ROOT / "dwg" / "1) 건축공사" / "0. PDF 도면" / "_png_dpi400" / f"{sheet_id}.png")

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

    parsed_stack = parse_level_stack(all_annotations)

    # Merge 로직: 기존 level-stack.yml 이 있으면 병합. 빈 levels 로 덮어쓰기 금지.
    existing_stack = {"levels_mm": {}, "offsets_mm": {}, "ffh_mm": {}}
    existing_path = KB_DIR / "level-stack.yml"
    if existing_path.exists():
        try:
            prev = yaml.safe_load(existing_path.read_text(encoding="utf-8")) or {}
            for k in ("levels_mm", "offsets_mm", "ffh_mm"):
                if isinstance(prev.get(k), dict):
                    existing_stack[k].update(prev[k])
        except Exception:
            pass

    merged = {
        "levels_mm": {**existing_stack["levels_mm"], **parsed_stack.get("levels_mm", {})},
        "offsets_mm": {**existing_stack["offsets_mm"], **parsed_stack.get("offsets_mm", {})},
        "ffh_mm": {**existing_stack["ffh_mm"], **parsed_stack.get("ffh_mm", {})},
    }
    level_stack = merged

    sheet_yaml = {
        "sheet_id": sheet_id,
        "sheet_number": data.get("sheet_number"),
        "source_png": source_png,
        "discipline": "architectural",
        "extraction_source": str(input_path.resolve()).replace("\\", "/"),
        "global_confidence": data.get("global_confidence"),
        "views": views_out,
    }

    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    out_sheet = SHEETS_DIR / f"{sheet_id}.yml"
    out_sheet.write_text(
        yaml.safe_dump(sheet_yaml, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    KB_DIR.mkdir(parents=True, exist_ok=True)
    out_levels = KB_DIR / "level-stack.yml"
    out_levels.write_text(
        yaml.safe_dump(level_stack, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    return {
        "sheet_id": sheet_id,
        "sheet_yaml_path": rel(out_sheet),
        "level_stack_yaml_path": rel(out_levels),
        "views_count": len(views_out),
        "per_view": [
            {
                "view_id": v["view_id"],
                "view_label": v["view_label"],
                "anchored_counts": v["anchored_counts"],
                "grid_validation": v["grid_validation"],
            }
            for v in views_out
        ],
        "level_stack": level_stack,
    }
