"""extract_sheet — Gemini로 시트 1장을 Stage-10(또는 Stage-00) JSON 추출."""
import json
import sys
import time
from datetime import datetime

from .base import PROMPTS_DIR, OUTPUTS_DIR, KB_DIR, load_keys, rel

try:
    from google import genai
    from google.genai import types
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "google-genai"])
    from google import genai
    from google.genai import types


SCHEMA = {
    "name": "extract_sheet",
    "description": (
        "Gemini로 시트 1장을 상세 추출한다. stage='10'은 건축평면 구조화 추출 "
        "(grid/rooms/walls/dims/annotations). stage='00'은 분류만. "
        "결과는 outputs/{ts}_{sheet_id}_{tag}/stage-{stage}-parsed.json 에 저장. "
        "반환값의 output_dir 를 build_kb_from_extract 의 input_json_path 로 전달할 수 있다. "
        "주의: 비용 발생. 이미 KB에 시트가 있다면 read_sheet 먼저 호출 권장."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "sheet_id": {
                "type": "string",
                "description": "예: arch_p062 (classifications.json의 키)",
            },
            "stage": {
                "type": "string",
                "enum": ["00", "10"],
                "description": "00=분류기, 10=건축평면 추출. 기본 10.",
            },
            "model": {
                "type": "string",
                "description": "Gemini 모델 명. 기본 gemini-3.1-flash-image-preview.",
            },
        },
        "required": ["sheet_id"],
    },
}


def _load_prompt(stage):
    path = {
        "00": PROMPTS_DIR / "00-standard-classifier.md",
        "10": PROMPTS_DIR / "10-architectural-plan.md",
    }[stage]
    content = path.read_text(encoding="utf-8")

    def extract(header):
        marker = f"## {header}"
        idx = content.find(marker)
        rest = content[idx + len(marker):]
        cs = rest.find("```") + 3
        nl = rest.find("\n", cs)
        ce = rest.find("```", nl)
        return rest[nl + 1:ce].strip()

    return {"system": extract("System Prompt"), "user": extract("사용자 프롬프트")}


def _try_parse_json(s):
    if not s:
        return None
    s = s.strip()
    if s.startswith("```"):
        inner = s.split("```", 2)
        if len(inner) >= 2:
            s = inner[1]
            if s.startswith("json"):
                s = s[4:]
            s = s.rstrip("`").strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    start = s.find("{")
    while start >= 0:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(s)):
            c = s[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        cand = s[start:i + 1]
                        try:
                            return json.loads(cand)
                        except Exception:
                            break
        start = s.find("{", start + 1)
    return None


def execute(tool_input, context=None):
    sheet_id = tool_input.get("sheet_id")
    stage = tool_input.get("stage", "10")
    model = tool_input.get("model", "gemini-3.1-flash-image-preview")
    fallback_model = "gemini-3.1-flash-preview"

    if not sheet_id:
        return {"error": "sheet_id 필수"}

    classifications_path = KB_DIR / "classifications.json"
    if not classifications_path.exists():
        return {"error": "classifications.json 없음 — Stage 1 먼저 실행 필요"}
    classifications = json.loads(classifications_path.read_text(encoding="utf-8"))
    rec = classifications.get(sheet_id)
    if not rec:
        return {"error": f"sheet_id '{sheet_id}' classifications.json 에 없음"}

    from .base import ROOT
    png_path = ROOT / rec.get("_png_path", "")
    if not png_path.exists():
        return {"error": f"PNG 파일 없음: {png_path}"}

    spec = _load_prompt(stage)
    img_bytes = png_path.read_bytes()
    contents = [
        types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
        spec["system"] + "\n\n" + spec["user"],
    ]

    models_to_try = [model]
    if fallback_model and fallback_model != model:
        models_to_try.append(fallback_model)

    client = genai.Client(api_key=load_keys()["google"])
    attempted = []
    errors = []
    resp = None
    actual_model = None
    fallback_used = False

    t0 = time.time()
    for i, m in enumerate(models_to_try):
        attempted.append(m)
        try:
            resp = client.models.generate_content(
                model=m,
                contents=contents,
                config=types.GenerateContentConfig(max_output_tokens=16000, temperature=0.1),
            )
            actual_model = m
            fallback_used = i > 0
            break
        except Exception as e:
            errors.append({"model": m, "error": f"{type(e).__name__}: {e}"})

    if resp is None:
        return {"error": "all_models_failed", "attempt_errors": errors}

    elapsed = round(time.time() - t0, 2)
    text = resp.text or ""
    parsed = _try_parse_json(text)
    usage = {}
    um = getattr(resp, "usage_metadata", None)
    if um:
        for attr in ("prompt_token_count", "candidates_token_count", "total_token_count"):
            v = getattr(um, attr, None)
            if v is not None:
                usage[attr] = v

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    tag = f"gemini-{actual_model.replace('gemini-', '').replace('-preview','')}"
    if fallback_used:
        tag += "_fb"
    tag += "_agent"
    run_dir = OUTPUTS_DIR / f"{ts}_{sheet_id}_{tag}"
    run_dir.mkdir(parents=True, exist_ok=True)

    result_payload = {
        "model": actual_model,
        "stage": stage,
        "elapsed_sec": elapsed,
        "usage": usage,
        "text": text,
        "parsed_json": parsed,
        "json_parse_ok": parsed is not None,
    }
    (run_dir / f"stage-{stage}.json").write_text(
        json.dumps(result_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    parsed_path = None
    if parsed:
        parsed_path = run_dir / f"stage-{stage}-parsed.json"
        parsed_path.write_text(
            json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # 요약만 리턴 (agent 컨텍스트 비대화 방지)
    summary = {
        "sheet_id": sheet_id,
        "stage": stage,
        "model_used": actual_model,
        "fallback_used": fallback_used,
        "elapsed_sec": elapsed,
        "usage": usage,
        "json_parse_ok": parsed is not None,
        "output_dir": rel(run_dir),
        "parsed_json_path": rel(parsed_path) if parsed_path else None,
    }

    if parsed:
        if stage == "10":
            views = parsed.get("views") or []
            summary["views_count"] = len(views)
            per_view = []
            for v in views:
                per_view.append({
                    "view_id": v.get("view_id"),
                    "view_label": v.get("view_label"),
                    "elements_count": len(v.get("elements") or []),
                    "dimensions_count": len(v.get("dimensions_raw") or []),
                    "annotations_count": len(v.get("annotations_ko") or []),
                })
            summary["per_view"] = per_view
        else:
            summary["classifier_result"] = {
                k: parsed.get(k)
                for k in ("discipline", "view_type", "is_3d_candidate",
                          "sheet_number", "sheet_title", "confidence")
            }
    else:
        summary["raw_text_head"] = text[:300]

    return summary
