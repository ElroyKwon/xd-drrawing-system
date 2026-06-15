"""
test_critique.py — A단계: Render-and-Critique.

기존 JSON을 Canvas로 재구성해 PNG로 렌더 → 원본 PNG + 렌더 PNG + 현재 JSON을
Opus에 보내 불일치 영역을 찾고 정정된 JSON을 받음.

렌더 PNG는 caller가 별도로 준비 (build_viewer_single + Chrome screenshot).

사용:
  python test_critique.py <original.png> <rendered.png> <current.json> <out_dir>
"""
import argparse
import base64
import json
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import anthropic
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "anthropic"])
    import anthropic


ROOT = Path(r"D:/_Project/prototype-도면지식관리-mvp")
KEYS_PATH = ROOT / "api_keys.json"
OPUS_MODEL = "claude-opus-4-7"


SYSTEM = """너는 건축 평면도 판독 검증자다. 다음을 수행한다:
1) 원본 도면(이미지1)과 현재 추출 JSON을 Canvas로 재구성한 이미지(이미지2)를 비교
2) 재구성이 원본과 다른 부분을 식별 (실 위치/크기/이름, 치수 누락, 그리드 오류 등)
3) 현재 JSON을 수정한 **전체 JSON**을 출력 (부분 patch 아님)

출력은 JSON 단 하나. 마크다운 금지. 스키마는 입력 JSON과 동일.
모든 길이는 mm. 읽을 수 없는 값은 null 유지. 추측 금지.
"""

USER_TMPL = """아래는 이미지1(원본)과 이미지2(Canvas 재구성)다. 그리고 현재 JSON:

```json
{current_json}
```

이미지2가 이미지1과 다른 점을 찾아 현재 JSON을 정정한 **전체 JSON**을 출력하라.
수정 포인트: 그리드 간격, 실명/polygon_grid 좌표, 치수의 from_grid/to_grid 앵커, 벽 두께, 누락 객체.
"""


def encode(path: Path):
    return base64.b64encode(path.read_bytes()).decode("ascii")


def try_parse_json(s):
    if not s:
        return None
    s = s.strip()
    if s.startswith("```"):
        parts = s.split("```", 2)
        if len(parts) >= 2:
            s = parts[1]
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
    ap.add_argument("original")
    ap.add_argument("rendered")
    ap.add_argument("current_json")
    ap.add_argument("out_dir")
    ap.add_argument("--max-tokens", type=int, default=12000)
    args = ap.parse_args()

    orig = Path(args.original)
    rendered = Path(args.rendered)
    current_path = Path(args.current_json)
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    current = json.loads(current_path.read_text(encoding="utf-8"))
    current_str = json.dumps(current, ensure_ascii=False, indent=2)
    user_text = USER_TMPL.format(current_json=current_str)

    client = anthropic.Anthropic(api_key=json.loads(KEYS_PATH.read_text(encoding="utf-8"))["anthropic"])

    t0 = time.time()
    print(f"A critique: orig={orig.name}  rendered={rendered.name}  current={current_path.name}", flush=True)
    resp = client.messages.create(
        model=OPUS_MODEL,
        max_tokens=args.max_tokens,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encode(orig)}},
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encode(rendered)}},
                {"type": "text", "text": user_text},
            ],
        }],
    )
    elapsed = time.time() - t0
    text = "\n".join(b.text for b in resp.content if b.type == "text").strip()
    parsed = try_parse_json(text)

    (out / "critique-raw.json").write_text(json.dumps({
        "elapsed_sec": round(elapsed, 2),
        "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens} if resp.usage else {},
        "text": text,
        "parse_ok": parsed is not None,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    if parsed:
        (out / "stage-10-parsed.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"saved (parsed): {out}  elapsed={elapsed:.1f}s", flush=True)
    else:
        print(f"saved (raw only, parse failed): {out}  elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    main()
