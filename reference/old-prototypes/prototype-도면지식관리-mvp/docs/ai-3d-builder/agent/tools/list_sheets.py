"""list_sheets — KB에 있는 시트 목록 조회 (classifications.json + sheets/ yaml 기반)."""
import json
from .base import KB_DIR, SHEETS_DIR

SCHEMA = {
    "name": "list_sheets",
    "description": (
        "도면 KB에 있는 시트 목록을 반환한다. "
        "각 시트의 discipline/view_type/is_3d_candidate/sheet_number/sheet_title 과 "
        "이미 추출된 상세 KB(sheets/{id}.yml) 존재 여부를 보여준다. "
        "filter 파라미터로 discipline·view_type·is_3d_candidate 필터 가능."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "filter_discipline": {
                "type": "string",
                "description": "architectural/structural/mechanical 등. 지정 시 해당 분야만.",
            },
            "filter_view_type": {
                "type": "string",
                "description": "floor_plan/enlarged_plan/section/elevation 등. 지정 시 해당 뷰타입만.",
            },
            "only_3d_candidates": {
                "type": "boolean",
                "description": "true면 is_3d_candidate=true 만 반환.",
            },
        },
    },
}


def execute(tool_input, context=None):
    class_path = KB_DIR / "classifications.json"
    if not class_path.exists():
        return {"error": "classifications.json 없음. Stage 1 먼저 실행."}

    data = json.loads(class_path.read_text(encoding="utf-8"))

    fd = tool_input.get("filter_discipline")
    fv = tool_input.get("filter_view_type")
    only3d = tool_input.get("only_3d_candidates", False)

    sheets = []
    for sid, rec in data.items():
        if "_error" in rec:
            continue
        if fd and rec.get("discipline") != fd:
            continue
        if fv and rec.get("view_type") != fv:
            continue
        if only3d and not rec.get("is_3d_candidate"):
            continue
        kb_path = SHEETS_DIR / f"{sid}.yml"
        sheets.append({
            "sheet_id": sid,
            "sheet_number": rec.get("sheet_number"),
            "sheet_title": rec.get("sheet_title"),
            "discipline": rec.get("discipline"),
            "view_type": rec.get("view_type"),
            "is_3d_candidate": rec.get("is_3d_candidate"),
            "has_kb_yaml": kb_path.exists(),
            "png_path": rec.get("_png_path"),
        })

    return {
        "count": len(sheets),
        "filter_applied": {
            "discipline": fd, "view_type": fv, "only_3d_candidates": only3d,
        },
        "sheets": sheets,
    }
