"""
Claude Advisor API (Haiku executor + Opus advisor) 테스트 스크립트.

사용:
  python docs/ai-3d-builder/scripts/test_advisor.py <image_path>
  python docs/ai-3d-builder/scripts/test_advisor.py <image_path> --stage 00
  python docs/ai-3d-builder/scripts/test_advisor.py <image_path> --stage 10

결과는 docs/ai-3d-builder/outputs/<timestamp>/ 에 저장.
"""
import argparse
import base64
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("pip install anthropic ...", flush=True)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "anthropic"])
    import anthropic

ROOT = Path(r"D:/_Project/prototype-도면지식관리-mvp")
KEYS_PATH = ROOT / "api_keys.json"
PROMPTS_DIR = ROOT / "docs" / "ai-3d-builder" / "prompts"
OUTPUTS_DIR = ROOT / "docs" / "ai-3d-builder" / "outputs"

EXECUTOR_MODEL = "claude-haiku-4-5-20251001"
ADVISOR_MODEL = "claude-opus-4-7"
BETA_HEADER = "advisor-tool-2026-03-01"
ADVISOR_TOOL_TYPE = "advisor_20260301"
OPUS_SOLO_MODEL = "claude-opus-4-7"


def load_api_key() -> str:
    with open(KEYS_PATH, "r", encoding="utf-8") as f:
        keys = json.load(f)
    return keys["anthropic"]


def load_prompt_spec(stage: str) -> dict:
    """프롬프트 md에서 System Prompt + 사용자 프롬프트 블록 파싱."""
    files = {
        "00": PROMPTS_DIR / "00-standard-classifier.md",
        "10": PROMPTS_DIR / "10-architectural-plan.md",
    }
    if stage not in files:
        raise ValueError(f"Unknown stage: {stage}")
    content = files[stage].read_text(encoding="utf-8")

    def extract_block(section_header: str) -> str:
        marker = f"## {section_header}"
        idx = content.find(marker)
        if idx < 0:
            raise ValueError(f"Section not found: {section_header}")
        rest = content[idx + len(marker):]
        code_start = rest.find("```")
        if code_start < 0:
            raise ValueError(f"No code block after {section_header}")
        code_start += 3
        nl = rest.find("\n", code_start)
        code_end = rest.find("```", nl)
        return rest[nl + 1:code_end].strip()

    return {
        "stage": stage,
        "system": extract_block("System Prompt"),
        "user": extract_block("사용자 프롬프트"),
    }


def encode_image(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    media_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(ext, "image/png")
    return base64.standard_b64encode(path.read_bytes()).decode("ascii"), media_type


def call_advisor(client, spec: dict, image_path: Path, max_tokens: int = 8000,
                 mode: str = "advisor", user_text_override: str | None = None) -> dict:
    """mode: 'advisor' (Haiku+Opus advisor) | 'opus' (Opus solo) | 'haiku' (Haiku solo)"""
    img_b64, media_type = encode_image(image_path)
    t0 = time.time()
    user_text = user_text_override if user_text_override is not None else spec["user"]
    common = dict(
        max_tokens=max_tokens,
        system=spec["system"],
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64",
                                              "media_type": media_type,
                                              "data": img_b64}},
                {"type": "text", "text": user_text},
            ],
        }],
    )
    if mode == "advisor":
        resp = client.messages.create(
            model=EXECUTOR_MODEL,
            extra_headers={"anthropic-beta": BETA_HEADER},
            tools=[{"type": ADVISOR_TOOL_TYPE, "name": "advisor", "model": ADVISOR_MODEL}],
            **common,
        )
    elif mode == "opus":
        resp = client.messages.create(model=OPUS_SOLO_MODEL, **common)
    elif mode == "haiku":
        resp = client.messages.create(model=EXECUTOR_MODEL, **common)
    else:
        raise ValueError(f"Unknown mode: {mode}")
    elapsed = time.time() - t0

    text_parts = []
    tool_uses = []
    for block in resp.content:
        if block.type == "text":
            text_parts.append(block.text)
        else:
            tool_uses.append({"type": block.type, "raw": str(block)})

    full_text = "\n".join(text_parts).strip()

    advisor_texts = []
    for block in resp.content:
        if getattr(block, "type", None) == "advisor_tool_result":
            bc = getattr(block, "content", None)
            if isinstance(bc, dict) and "text" in bc:
                advisor_texts.append(bc["text"] or "")
            elif isinstance(bc, str):
                advisor_texts.append(bc)

    def _try_parse_json(s: str):
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

    parsed_json = _try_parse_json(full_text)
    json_err = None
    json_source = "executor_text" if parsed_json is not None else None
    if parsed_json is None:
        for at in advisor_texts:
            parsed_json = _try_parse_json(at)
            if parsed_json is not None:
                json_source = "advisor_tool_result"
                break
    if parsed_json is None:
        json_err = "No parseable JSON in executor text or advisor result"

    usage = {}
    if resp.usage:
        usage = {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
        }
        for attr in ("cache_creation_input_tokens", "cache_read_input_tokens"):
            v = getattr(resp.usage, attr, None)
            if v is not None:
                usage[attr] = v

    return {
        "model": resp.model,
        "stop_reason": resp.stop_reason,
        "elapsed_sec": round(elapsed, 2),
        "usage": usage,
        "text": full_text,
        "advisor_texts": advisor_texts,
        "parsed_json": parsed_json,
        "json_source": json_source,
        "json_parse_error": json_err,
        "tool_uses": tool_uses,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", help="도면 이미지 경로 (png/jpg)")
    ap.add_argument("--stage", default="00", choices=["00", "10", "both"])
    ap.add_argument("--max-tokens", type=int, default=8000)
    ap.add_argument("--mode", default="advisor", choices=["advisor", "opus", "haiku"])
    ap.add_argument("--reference", help="다른 모델 결과 JSON 경로 (참조 컨텍스트)")
    ap.add_argument("--reference-label", default="다른 모델", help="참조 결과 라벨")
    ap.add_argument("--tag-suffix", default="", help="run_dir 디렉토리 suffix (_ref 등)")
    args = ap.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"이미지 없음: {image_path}", file=sys.stderr)
        sys.exit(1)

    api_key = load_api_key()
    client = anthropic.Anthropic(api_key=api_key)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    suffix = args.tag_suffix or ("_ref" if args.reference else "")
    run_dir = OUTPUTS_DIR / f"{ts}_{image_path.stem}_{args.mode}{suffix}"
    run_dir.mkdir(parents=True, exist_ok=True)

    ref_block_text = None
    if args.reference:
        ref_data = json.loads(Path(args.reference).read_text(encoding="utf-8"))
        ref_block_text = (
            f"\n\n## 참고 컨텍스트: {args.reference_label}의 추출 결과\n"
            f"```json\n{json.dumps(ref_data, ensure_ascii=False, indent=2)}\n```\n\n"
            "위 결과는 참고용이다. 너는 이미지를 직접 분석하여 너의 판단으로 JSON을 출력하라.\n"
            "참고 결과가 옳다고 판단되면 동일한 값을 사용해도 되고, 틀렸다고 판단되면 정정하라.\n"
            "특히 Y축 그리드 간격, 실의 polygon_grid 좌표, 벽 두께, 치수 grid 앵커를 정확히 채워라."
        )

    stages = ["00", "10"] if args.stage == "both" else [args.stage]
    summary = {
        "image": str(image_path),
        "run_dir": str(run_dir),
        "mode": args.mode,
        "executor": EXECUTOR_MODEL if args.mode != "opus" else OPUS_SOLO_MODEL,
        "advisor": ADVISOR_MODEL if args.mode == "advisor" else None,
        "beta_header": BETA_HEADER if args.mode == "advisor" else None,
        "stages": {},
    }

    for stg in stages:
        print(f"\n[Stage {stg}] prompt loading...", flush=True)
        spec = load_prompt_spec(stg)
        model_label = (f"advisor: {EXECUTOR_MODEL}+{ADVISOR_MODEL}" if args.mode == "advisor"
                       else f"opus: {OPUS_SOLO_MODEL}" if args.mode == "opus"
                       else f"haiku: {EXECUTOR_MODEL}")
        print(f"[Stage {stg}] calling API ({model_label}){' +ref' if ref_block_text else ''}...", flush=True)
        try:
            user_override = (spec["user"] + ref_block_text) if ref_block_text else None
            result = call_advisor(client, spec, image_path, max_tokens=args.max_tokens, mode=args.mode,
                                  user_text_override=user_override)
        except Exception as e:
            print(f"[Stage {stg}] ERROR: {type(e).__name__}: {e}", flush=True)
            result = {"error": f"{type(e).__name__}: {e}"}
        summary["stages"][stg] = result

        (run_dir / f"stage-{stg}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if result.get("parsed_json"):
            (run_dir / f"stage-{stg}-parsed.json").write_text(
                json.dumps(result["parsed_json"], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        print(f"[Stage {stg}] saved -> {run_dir}", flush=True)
        if "usage" in result:
            print(f"  tokens: {result['usage']}", flush=True)
        if result.get("json_parse_error"):
            print(f"  JSON parse 실패: {result['json_parse_error']}", flush=True)

    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n완료: {run_dir}")


if __name__ == "__main__":
    main()
