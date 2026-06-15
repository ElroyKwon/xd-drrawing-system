"""read_sheet — 특정 시트의 상세 KB YAML 또는 classifications 요약 반환."""
import json
from .base import KB_DIR, SHEETS_DIR

try:
    import yaml
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pyyaml"])
    import yaml

SCHEMA = {
    "name": "read_sheet",
    "description": (
        "특정 sheet_id의 상세 정보를 반환한다. "
        "knowledge-base/sheets/{sheet_id}.yml 이 있으면 그것을 읽어 반환 (최상급 정보). "
        "없으면 classifications.json의 요약과 'kb_yaml_missing=true' 반환. "
        "Agent는 missing이면 extract_sheet → build_kb_from_extract 호출 권장."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "sheet_id": {
                "type": "string",
                "description": "예: arch_p062",
            },
        },
        "required": ["sheet_id"],
    },
}


def execute(tool_input, context=None):
    sid = tool_input.get("sheet_id")
    if not sid:
        return {"error": "sheet_id 필수"}

    kb_path = SHEETS_DIR / f"{sid}.yml"
    class_path = KB_DIR / "classifications.json"

    summary = None
    if class_path.exists():
        data = json.loads(class_path.read_text(encoding="utf-8"))
        rec = data.get(sid)
        if rec:
            summary = {
                "sheet_number": rec.get("sheet_number"),
                "sheet_title": rec.get("sheet_title"),
                "discipline": rec.get("discipline"),
                "view_type": rec.get("view_type"),
                "is_3d_candidate": rec.get("is_3d_candidate"),
                "png_path": rec.get("_png_path"),
                "classifier_notes": rec.get("notes"),
            }

    if kb_path.exists():
        kb = yaml.safe_load(kb_path.read_text(encoding="utf-8"))
        return {
            "sheet_id": sid,
            "summary": summary,
            "kb_yaml_present": True,
            "kb_yaml_path": str(kb_path.relative_to(kb_path.parents[3])).replace("\\", "/"),
            "kb": kb,
        }

    return {
        "sheet_id": sid,
        "summary": summary,
        "kb_yaml_present": False,
        "kb_yaml_missing": True,
        "next_action_hint": "extract_sheet → build_kb_from_extract 순서로 호출하면 KB 생성됨.",
    }
