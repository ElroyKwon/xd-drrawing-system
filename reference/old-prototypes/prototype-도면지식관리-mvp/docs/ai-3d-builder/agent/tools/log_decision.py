"""log_decision — 에이전트 결정을 JSONL로 기록."""
import json
from .base import AGENT_DIR, now_iso, rel


SCHEMA = {
    "name": "log_decision",
    "description": (
        "에이전트의 주요 결정을 감사 로그에 기록한다. "
        "session_id 별 runs/{session_id}/decisions.jsonl 에 append. "
        "decision(짧은 제목), rationale(왜), artifacts(생성·수정 파일 목록)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "decision": {"type": "string", "description": "결정 요약 한 줄"},
            "rationale": {"type": "string", "description": "이유·근거"},
            "artifacts": {
                "type": "array",
                "items": {"type": "string"},
                "description": "생성·수정된 파일 경로 목록",
            },
        },
        "required": ["decision", "rationale"],
    },
}


def execute(tool_input, context=None):
    sid = (context or {}).get("session_id", "default")
    d = AGENT_DIR / "runs" / sid
    d.mkdir(parents=True, exist_ok=True)
    path = d / "decisions.jsonl"
    entry = {
        "ts": now_iso(),
        "decision": tool_input.get("decision"),
        "rationale": tool_input.get("rationale"),
        "artifacts": tool_input.get("artifacts") or [],
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"logged": True, "path": rel(path), "entry": entry}
