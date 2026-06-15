"""Agent 툴 공통 유틸 — 경로·로깅."""
import json
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(r"D:/_Project/prototype-도면지식관리-mvp")
DOCS_DIR = ROOT / "docs" / "ai-3d-builder"
KB_DIR = DOCS_DIR / "knowledge-base"
IDX_DIR = KB_DIR / "indexes"
SHEETS_DIR = KB_DIR / "sheets"
SCRIPTS_DIR = DOCS_DIR / "scripts"
AGENT_DIR = DOCS_DIR / "agent"
PROMPTS_DIR = DOCS_DIR / "prompts"
OUTPUTS_DIR = DOCS_DIR / "outputs"
THREEJS_DIR = DOCS_DIR / "threejs-scene"
KEYS_PATH = ROOT / "api_keys.json"


def rel(p):
    """ROOT 기준 상대 경로 문자열."""
    try:
        return str(Path(p).relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p)


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def load_keys():
    return json.loads(KEYS_PATH.read_text(encoding="utf-8"))


def session_dir(session_id):
    d = AGENT_DIR / "runs" / session_id
    d.mkdir(parents=True, exist_ok=True)
    return d
