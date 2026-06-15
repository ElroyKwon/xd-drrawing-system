"""render_preview — Three.js HTML → Chrome headless 스크린샷 + scene_bbox 덤프."""
import json
import sys
from pathlib import Path
from datetime import datetime

from .base import ROOT, AGENT_DIR, rel


SCHEMA = {
    "name": "render_preview",
    "description": (
        "Three.js HTML 파일을 Chrome headless 로 로드하여 여러 카메라 뷰로 스크린샷을 찍고 "
        "scene_bbox 덤프를 반환한다. 씬은 window.__scene 훅을 제공해야 하며 "
        "이 훅에 topView()/isoView()/resetView() 등 카메라 프리셋 메서드가 있어야 한다. "
        "각 스크린샷은 PNG 파일 경로로 반환. console_errors 도 반환 — 에이전트는 이를 검사해 코드 수정 여부 결정."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "html_path": {
                "type": "string",
                "description": "ROOT 기준 상대 또는 절대 경로. 예: docs/ai-3d-builder/threejs-scene/full-building/index.html",
            },
            "screenshot_dir": {
                "type": "string",
                "description": "스크린샷 저장 디렉토리 (없으면 자동 생성). 미지정 시 agent/runs/{session_id}/screenshots/.",
            },
            "views": {
                "type": "array",
                "description": "각 원소는 {name, action} — action은 window.__scene에서 호출할 메서드 명.",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "action": {"type": "string"},
                    },
                },
            },
            "wait_selector": {
                "type": "string",
                "description": "렌더 완료를 기다릴 CSS 선택자. 기본 #status.",
            },
            "timeout_ms": {"type": "integer"},
        },
        "required": ["html_path"],
    },
}

DEFAULT_VIEWS = [
    {"name": "iso", "action": "isoView"},
    {"name": "top", "action": "topView"},
    {"name": "southeast", "action": "southeastView"},
]


def execute(tool_input, context=None):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "playwright"])
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"],
                                  stderr=subprocess.STDOUT)
            from playwright.sync_api import sync_playwright
        except Exception as e:
            return {"error": f"playwright 설치 실패: {e}"}

    html_raw = tool_input.get("html_path")
    if not html_raw:
        return {"error": "html_path 필수"}
    html_path = Path(html_raw)
    if not html_path.is_absolute():
        html_path = ROOT / html_path
    if not html_path.exists():
        return {"error": f"HTML 파일 없음: {html_path}"}

    views = tool_input.get("views") or DEFAULT_VIEWS
    wait_selector = tool_input.get("wait_selector", "#status")
    timeout_ms = int(tool_input.get("timeout_ms", 15000))

    ss_dir_raw = tool_input.get("screenshot_dir")
    if ss_dir_raw:
        ss_dir = Path(ss_dir_raw)
        if not ss_dir.is_absolute():
            ss_dir = ROOT / ss_dir
    else:
        sid = (context or {}).get("session_id", "default")
        ss_dir = AGENT_DIR / "runs" / sid / "screenshots"
    ss_dir.mkdir(parents=True, exist_ok=True)

    screenshots = []
    console_errors = []
    scene_bbox = None
    render_ok = False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context_br = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context_br.new_page()

        page.on("console", lambda msg: console_errors.append({
            "type": msg.type, "text": msg.text,
        }) if msg.type == "error" else None)

        file_url = "file:///" + str(html_path.resolve()).replace("\\", "/")
        try:
            page.goto(file_url, timeout=timeout_ms)
            try:
                page.wait_for_selector(wait_selector, timeout=timeout_ms)
                render_ok = True
            except Exception as e:
                console_errors.append({"type": "wait_timeout", "text": str(e)})

            # scene_bbox 덤프
            try:
                scene_bbox = page.evaluate(
                    "() => (window.__scene && window.__scene.dumpBBox) ? window.__scene.dumpBBox() : null"
                )
            except Exception as e:
                console_errors.append({"type": "bbox_eval_error", "text": str(e)})

            # 각 뷰 스크린샷
            for i, v in enumerate(views, 1):
                action = v.get("action")
                try:
                    if action:
                        page.evaluate(f"() => window.__scene && window.__scene['{action}'] && window.__scene['{action}']()")
                        page.wait_for_timeout(400)
                    ts = datetime.now().strftime("%H%M%S")
                    fname = f"{i:02d}-{v.get('name', 'view')}-{ts}.png"
                    fpath = ss_dir / fname
                    page.screenshot(path=str(fpath), full_page=False)
                    screenshots.append({
                        "name": v.get("name", f"view_{i}"),
                        "path": rel(fpath),
                        "width": 1600, "height": 1000,
                    })
                except Exception as e:
                    console_errors.append({"type": "screenshot_error", "text": str(e)})

        finally:
            browser.close()

    return {
        "render_ok": render_ok,
        "screenshots": screenshots,
        "screenshot_count": len(screenshots),
        "console_errors": console_errors,
        "scene_bbox": scene_bbox,
        "html_path": rel(html_path),
        "screenshot_dir": rel(ss_dir),
    }
