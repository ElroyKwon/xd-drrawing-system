"""
Gemini로 도면 분석 (옵션: 다른 모델의 추출 결과를 참조 컨텍스트로 포함).

사용:
  python test_gemini.py <image> --stage 10 --reference <other-result.json>
  python test_gemini.py <image> --stage 10 --model gemini-3.1-pro-preview
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "google-genai"])
    from google import genai
    from google.genai import types

ROOT = Path(r"D:/_Project/prototype-도면지식관리-mvp")
KEYS_PATH = ROOT / "api_keys.json"
PROMPTS_DIR = ROOT / "docs" / "ai-3d-builder" / "prompts"
OUTPUTS_DIR = ROOT / "docs" / "ai-3d-builder" / "outputs"

DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
DEFAULT_FALLBACK_MODEL = "gemini-3.1-flash-preview"


def load_api_key():
    keys = json.loads(KEYS_PATH.read_text(encoding="utf-8"))
    return keys["google"]


def load_prompt_spec(stage):
    files = {
        "00": PROMPTS_DIR / "00-standard-classifier.md",
        "10": PROMPTS_DIR / "10-architectural-plan.md",
    }
    content = files[stage].read_text(encoding="utf-8")

    def extract(header):
        marker = f"## {header}"
        idx = content.find(marker)
        rest = content[idx + len(marker):]
        cs = rest.find("```")
        if cs < 0:
            raise RuntimeError("no code fence")
        cs += 3
        nl = rest.find("\n", cs)
        ce = rest.find("```", nl)
        return rest[nl + 1:ce].strip()

    return {"system": extract("System Prompt"), "user": extract("사용자 프롬프트")}


def try_parse_json(s):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--stage", default="10", choices=["00", "10"])
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--fallback-model", default=DEFAULT_FALLBACK_MODEL,
                    help="1차 모델 실패 시 재시도할 모델. 빈 문자열이면 fallback 비활성.")
    ap.add_argument("--reference", help="다른 모델 결과 JSON 경로 (참조 컨텍스트)")
    ap.add_argument("--reference-label", default="다른 모델", help="참조 결과 라벨")
    ap.add_argument("--max-tokens", type=int, default=16000)
    args = ap.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"이미지 없음: {image_path}", file=sys.stderr)
        sys.exit(1)

    spec = load_prompt_spec(args.stage)
    user_text = spec["user"]

    if args.reference:
        ref_path = Path(args.reference)
        ref_data = json.loads(ref_path.read_text(encoding="utf-8"))
        ref_block = json.dumps(ref_data, ensure_ascii=False, indent=2)
        user_text += (
            f"\n\n## 참고 컨텍스트: {args.reference_label}의 추출 결과\n"
            f"```json\n{ref_block}\n```\n\n"
            "위 결과는 참고용이다. 너는 이미지를 직접 분석하여 너의 판단으로 JSON을 출력하라.\n"
            "참고 결과가 옳다고 판단되면 동일한 값을 사용해도 되고, 틀렸다고 판단되면 정정하라.\n"
            "참고 결과가 빠뜨린 항목이 있으면 추가하라.\n"
            "특히 Y축 그리드 간격(y_spacings_mm), 실의 polygon_grid 좌표, 벽 두께를 정확히 채워라."
        )

    client = genai.Client(api_key=load_api_key())
    img_bytes = image_path.read_bytes()

    contents = [
        types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
        spec["system"] + "\n\n" + user_text,
    ]

    models_to_try = [args.model]
    if args.fallback_model and args.fallback_model != args.model:
        models_to_try.append(args.fallback_model)

    print(f"[Gemini] primary={args.model}  fallback={args.fallback_model or '(none)'}", flush=True)
    print(f"[Gemini] image={image_path.name} ({len(img_bytes)//1024}KB)", flush=True)
    print(f"[Gemini] reference={'YES' if args.reference else 'NO'}", flush=True)

    def call_model(model_name):
        return client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                max_output_tokens=args.max_tokens,
                temperature=0.1,
            ),
        )

    attempted_models = []
    attempt_errors = []
    fallback_used = False
    actual_model = None
    resp = None

    t0 = time.time()
    for i, m in enumerate(models_to_try):
        attempted_models.append(m)
        print(f"[Gemini] attempt {i+1}/{len(models_to_try)}: {m}", flush=True)
        try:
            resp = call_model(m)
            actual_model = m
            if i > 0:
                fallback_used = True
                print(f"[Gemini] fallback succeeded: {models_to_try[0]} → {m}", flush=True)
            break
        except Exception as e:
            err_msg = f"{type(e).__name__}: {e}"
            attempt_errors.append({"model": m, "error": err_msg})
            print(f"[Gemini] attempt {i+1} FAILED: {err_msg}", file=sys.stderr)
            if i < len(models_to_try) - 1:
                print(f"[Gemini] fallback triggered: {m} → {models_to_try[i+1]}", flush=True)

    if resp is None:
        print(f"[Gemini] ALL ATTEMPTS FAILED ({len(attempted_models)})", file=sys.stderr)
        for rec in attempt_errors:
            print(f"  - {rec['model']}: {rec['error']}", file=sys.stderr)
        sys.exit(2)
    elapsed = time.time() - t0

    text = resp.text or ""
    parsed = try_parse_json(text)

    usage = {}
    um = getattr(resp, "usage_metadata", None)
    if um:
        for attr in ("prompt_token_count", "candidates_token_count", "total_token_count",
                     "thoughts_token_count"):
            v = getattr(um, attr, None)
            if v is not None:
                usage[attr] = v

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    tag = f"gemini-{actual_model.replace('-preview','').replace('gemini-','')}"
    if fallback_used:
        tag += "_fb"
    if args.reference:
        tag += "_ref"
    run_dir = OUTPUTS_DIR / f"{ts}_{image_path.stem}_{tag}"
    run_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "model": actual_model,
        "model_requested": args.model,
        "attempted_models": attempted_models,
        "attempt_errors": attempt_errors,
        "fallback_used": fallback_used,
        "stage": args.stage,
        "elapsed_sec": round(elapsed, 2),
        "usage": usage,
        "text": text,
        "parsed_json": parsed,
        "json_parse_ok": parsed is not None,
        "reference_used": str(Path(args.reference).resolve()) if args.reference else None,
    }

    (run_dir / f"stage-{args.stage}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if parsed:
        (run_dir / f"stage-{args.stage}-parsed.json").write_text(
            json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print(f"\nsaved: {run_dir}")
    print(f"  elapsed: {elapsed:.1f}s  usage: {usage}")
    print(f"  parse_ok: {parsed is not None}")
    if not parsed:
        print(f"  text head: {text[:300]}")


if __name__ == "__main__":
    main()
