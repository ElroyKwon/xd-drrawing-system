"""
Stage 1 — 배치 분류기.

_png_dpi400/ 의 모든 arch_p*.png (15장) 를 Gemini 로 분류하여 classifications.json 집계.

사용:
  python 01_classify_all.py                       # 전체 실행, 기존 결과 skip
  python 01_classify_all.py --force               # 기존 결과 무시하고 재실행
  python 01_classify_all.py --only arch_p062      # 특정 시트만

산출: docs/ai-3d-builder/knowledge-base/classifications.json

프롬프트: docs/ai-3d-builder/prompts/00-standard-classifier.md
모델: gemini-3.1-flash-image-preview (fallback: gemini-3.1-flash-preview)
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

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
PNG_DIR = ROOT / "dwg" / "1) 건축공사" / "0. PDF 도면" / "_png_dpi400"
KB_DIR = ROOT / "docs" / "ai-3d-builder" / "knowledge-base"
OUT_PATH = KB_DIR / "classifications.json"

DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
FALLBACK_MODEL = "gemini-3.1-flash-preview"


def load_api_key():
    keys = json.loads(KEYS_PATH.read_text(encoding="utf-8"))
    return keys["google"]


def load_prompt_spec_00():
    content = (PROMPTS_DIR / "00-standard-classifier.md").read_text(encoding="utf-8")

    def extract(header):
        marker = f"## {header}"
        idx = content.find(marker)
        rest = content[idx + len(marker):]
        cs = rest.find("```")
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


def classify_one(client, spec, png_path, models):
    """1장 분류. 성공시 dict, 실패시 {'_error': ...} 반환."""
    img_bytes = png_path.read_bytes()
    contents = [
        types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
        spec["system"] + "\n\n" + spec["user"],
    ]

    attempt_errors = []
    t0 = time.time()
    for i, m in enumerate(models):
        try:
            resp = client.models.generate_content(
                model=m,
                contents=contents,
                config=types.GenerateContentConfig(
                    max_output_tokens=4000,
                    temperature=0.1,
                ),
            )
            elapsed = time.time() - t0
            text = resp.text or ""
            parsed = try_parse_json(text)
            if parsed is None:
                return {
                    "_error": "json_parse_failed",
                    "_raw_text_head": text[:300],
                    "model_used": m,
                    "fallback_used": i > 0,
                    "elapsed_sec": round(elapsed, 2),
                }
            usage = {}
            um = getattr(resp, "usage_metadata", None)
            if um:
                for attr in ("prompt_token_count", "candidates_token_count",
                             "total_token_count", "thoughts_token_count"):
                    v = getattr(um, attr, None)
                    if v is not None:
                        usage[attr] = v
            parsed["_meta"] = {
                "model_used": m,
                "fallback_used": i > 0,
                "elapsed_sec": round(elapsed, 2),
                "usage": usage,
                "attempt_errors": attempt_errors,
                "classified_at": datetime.now().isoformat(timespec="seconds"),
            }
            return parsed
        except Exception as e:
            attempt_errors.append({"model": m, "error": f"{type(e).__name__}: {e}"})
            print(f"  [!] {m} failed: {type(e).__name__}: {e}", file=sys.stderr)

    return {
        "_error": "all_models_failed",
        "attempt_errors": attempt_errors,
        "elapsed_sec": round(time.time() - t0, 2),
    }


def load_existing():
    if OUT_PATH.exists():
        try:
            return json.loads(OUT_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_all(data):
    KB_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="기존 결과 무시하고 재실행")
    ap.add_argument("--only", help="특정 sheet_id만 (예: arch_p062)")
    ap.add_argument("--dry-run", action="store_true", help="API 호출 없이 목록만")
    args = ap.parse_args()

    if not PNG_DIR.exists():
        print(f"PNG 디렉토리 없음: {PNG_DIR}", file=sys.stderr)
        sys.exit(1)

    pngs = sorted(PNG_DIR.glob("arch_p*.png"))
    pngs = [p for p in pngs if "_crops" not in p.parts]
    if args.only:
        pngs = [p for p in pngs if p.stem == args.only]

    print(f"[classify_all] 대상 {len(pngs)}장")
    for p in pngs:
        print(f"  - {p.stem}")
    if args.dry_run:
        return

    existing = load_existing() if not args.force else {}
    models = [DEFAULT_MODEL, FALLBACK_MODEL]

    client = genai.Client(api_key=load_api_key())
    spec = load_prompt_spec_00()

    results = dict(existing)
    new_count = 0
    skip_count = 0
    fail_count = 0

    for idx, png_path in enumerate(pngs, 1):
        sheet_id = png_path.stem
        if sheet_id in results and "_error" not in results[sheet_id] and not args.force:
            print(f"[{idx}/{len(pngs)}] {sheet_id} — skip (기존 결과 사용)")
            skip_count += 1
            continue

        print(f"[{idx}/{len(pngs)}] {sheet_id} — 분류 중 ({png_path.stat().st_size // 1024} KB)...",
              flush=True)
        result = classify_one(client, spec, png_path, models)
        result["_sheet_id"] = sheet_id
        result["_png_path"] = str(png_path.relative_to(ROOT)).replace("\\", "/")
        results[sheet_id] = result

        if "_error" in result:
            print(f"  [FAIL] {result['_error']}")
            fail_count += 1
        else:
            print(f"  -> discipline={result.get('discipline')} "
                  f"view_type={result.get('view_type')} "
                  f"is_3d={result.get('is_3d_candidate')} "
                  f"conf={result.get('confidence')} "
                  f"({result.get('_meta', {}).get('elapsed_sec')}s)")
            new_count += 1

        # 매 호출 후 저장 (중단 대비)
        save_all(results)

    print(f"\n[classify_all] 완료")
    print(f"  신규 분류: {new_count}")
    print(f"  기존 재사용: {skip_count}")
    print(f"  실패: {fail_count}")
    print(f"  저장 위치: {OUT_PATH}")

    summary = {
        "total": len(pngs),
        "classified": new_count + skip_count,
        "failed": fail_count,
        "is_3d_candidate_true": sum(
            1 for r in results.values()
            if r.get("is_3d_candidate") is True
        ),
    }
    print(f"  summary: {summary}")


if __name__ == "__main__":
    main()
