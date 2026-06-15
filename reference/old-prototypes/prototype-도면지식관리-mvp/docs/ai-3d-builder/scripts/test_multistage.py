"""
test_multistage.py — D단계: 1장 시트를 4개 서브프롬프트(grid/rooms/dimensions/objects)로
분리 추출 후 stage-10 스키마로 병합.

사용:
  python test_multistage.py <image> --mode opus
"""
import argparse
import base64
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
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
OUTPUTS_DIR = ROOT / "docs" / "ai-3d-builder" / "outputs"

OPUS_MODEL = "claude-opus-4-7"
HAIKU_MODEL = "claude-haiku-4-5-20251001"

SYSTEM_BASE = (
    "너는 한국 건축 평면도 판독 전문가다. 이미지 1장에서 3D 복원용 데이터를 추출한다.\n"
    "원칙: 출력은 JSON 단 하나, 마크다운 금지. 모든 길이는 mm. 그리드 기반 좌표 우선.\n"
    "읽을 수 없으면 null. 추측 금지. 2개 이상 서브뷰가 있으면 각각 views[]에 분리."
)

GRID_PROMPT = """
이미지에서 그리드·레벨 정보만 추출하라. 다른 요소(실·벽·치수·객체)는 무시.

출력 JSON:
{
  "sheet_number": "<시트번호>",
  "views": [
    {
      "view_id": "v1",
      "view_label": "<예: 지상2층 확대평면도>",
      "view_scale": "<예: 1:200>",
      "grid": {
        "x_labels": ["..."], "y_labels": ["..."],
        "x_spacings_mm": [...], "y_spacings_mm": [...],
        "x_direction": "left_to_right", "y_direction": "top_to_bottom"
      },
      "level": {"name": "<층>", "elevation_mm": null, "ceiling_height_mm": null}
    }
  ]
}
X 라벨(숫자 1,2,2A,3...)과 Y 라벨(A,B,B1,C,D...) 순서대로. spacings는 인접 라벨 사이 치수(mm).
""".strip()

ROOMS_PROMPT = """
이미지에서 실(room) 구획만 추출하라. 그리드·치수·벽·기둥은 무시.
실명과 polygon_grid(그리드 라벨 좌표 4~8개)를 정확히. void/shaft/stair/EV는 제외.

출력:
{
  "sheet_number": "<시트>",
  "views": [{
    "view_id": "v1",
    "rooms": [
      {"id": "r1", "name": "<실명>", "room_number": "<번호/null>",
       "polygon_grid": [["1","A"],["2","A"],["2","B"],["1","B"]],
       "ceiling_height_mm": null, "area_m2": null, "confidence": 0.7}
    ]
  }]
}
""".strip()

DIMENSIONS_PROMPT = """
이미지에서 치수(dimensions)만 추출하라. 다른 모든 요소 무시.
치수 숫자 텍스트와 from_grid/to_grid(가능하면). 불명확하면 from_grid/to_grid=null.

출력:
{
  "sheet_number": "<시트>",
  "views": [{
    "view_id": "v1",
    "dimensions_raw": [
      {"text": "8125", "from_grid": ["5","A"], "to_grid": ["5B","A"]},
      {"text": "4500", "from_grid": null, "to_grid": null}
    ]
  }]
}
가능한 모든 치수를 누락 없이 포함. 텍스트 정확히 (comma 없이 숫자만).
""".strip()

OBJECTS_PROMPT = """
이미지에서 비-실 객체(wall, column, door, stair, elevator, shaft, void, opening)만 추출.
실(room)과 그리드·치수는 무시.

출력:
{
  "sheet_number": "<시트>",
  "views": [{
    "view_id": "v1",
    "elements": [
      {"id": "w1", "type": "wall", "path_grid": [["5","A"],["7","A"]], "thickness_mm": 200, "confidence": 0.7},
      {"id": "c1", "type": "column", "at_grid": ["5","B"], "size_mm": {"w":600,"d":600}, "confidence": 0.7},
      {"id": "d1", "type": "door", "on_wall_from": ["1","B"], "on_wall_to": ["2","B"], "width_mm": 900, "confidence": 0.6},
      {"id": "s1", "type": "stair", "polygon_grid": [["5","B1"],["5B","B1"],["5B","B2"],["5","B2"]], "label": "계단", "confidence": 0.7},
      {"id": "sh1", "type": "shaft", "at_grid": ["6","B2"], "label": "PS", "confidence": 0.6},
      {"id": "v1", "type": "void", "polygon_grid": [["5","A"],["7","A"],["7","B"],["5","B"]], "label": "보이드", "confidence": 0.6}
    ]
  }]
}
""".strip()

SUB_PROMPTS = {
    "grid": GRID_PROMPT,
    "rooms": ROOMS_PROMPT,
    "dimensions": DIMENSIONS_PROMPT,
    "objects": OBJECTS_PROMPT,
}


def encode_image(path: Path):
    return base64.b64encode(path.read_bytes()).decode("ascii"), "image/png"


def try_parse_json(s: str):
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


def call_one(client, model: str, image_b64: str, media: str, user_text: str, max_tokens: int):
    t0 = time.time()
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_BASE,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media, "data": image_b64}},
                {"type": "text", "text": user_text},
            ],
        }],
    )
    text = "\n".join(b.text for b in resp.content if b.type == "text").strip()
    usage = {}
    if resp.usage:
        usage = {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
    return {
        "elapsed_sec": round(time.time() - t0, 2),
        "usage": usage,
        "text": text,
        "parsed_json": try_parse_json(text),
    }


def merge_results(subs: dict) -> dict:
    """4개 서브결과를 stage-10 스키마로 병합."""
    grid = (subs.get("grid") or {}).get("parsed_json") or {}
    rooms = (subs.get("rooms") or {}).get("parsed_json") or {}
    dims = (subs.get("dimensions") or {}).get("parsed_json") or {}
    objs = (subs.get("objects") or {}).get("parsed_json") or {}

    sheet_number = (grid.get("sheet_number") or rooms.get("sheet_number")
                    or dims.get("sheet_number") or objs.get("sheet_number"))

    def views_of(d):
        return d.get("views") or []

    grid_views = views_of(grid)
    rooms_views = views_of(rooms)
    dims_views = views_of(dims)
    objs_views = views_of(objs)

    n = max(len(grid_views), len(rooms_views), len(dims_views), len(objs_views), 1)

    def get_i(lst, i):
        return lst[i] if i < len(lst) else {}

    merged_views = []
    for i in range(n):
        gv = get_i(grid_views, i)
        rv = get_i(rooms_views, i)
        dv = get_i(dims_views, i)
        ov = get_i(objs_views, i)

        elements = []
        for rm in (rv.get("rooms") or []):
            elements.append({**rm, "type": "room"})
        for el in (ov.get("elements") or []):
            elements.append(el)

        merged_views.append({
            "view_id": gv.get("view_id") or rv.get("view_id") or f"v{i+1}",
            "view_label": gv.get("view_label"),
            "view_scale": gv.get("view_scale"),
            "grid": gv.get("grid"),
            "level": gv.get("level"),
            "elements": elements,
            "dimensions_raw": dv.get("dimensions_raw") or [],
            "annotations_ko": [],
            "unresolved": [],
        })

    return {
        "sheet_number": sheet_number,
        "views": merged_views,
        "global_confidence": 0.7,
        "_source": "multistage_merge",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--mode", default="opus", choices=["opus", "haiku"])
    ap.add_argument("--max-tokens", type=int, default=6000)
    args = ap.parse_args()

    image_path = Path(args.image)
    client = anthropic.Anthropic(api_key=json.loads(KEYS_PATH.read_text(encoding="utf-8"))["anthropic"])
    model = OPUS_MODEL if args.mode == "opus" else HAIKU_MODEL

    img_b64, media = encode_image(image_path)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = OUTPUTS_DIR / f"{ts}_{image_path.stem}_{args.mode}_multistage"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"D단계: {image_path.name} -> {args.mode} 4개 서브프롬프트 병렬 실행", flush=True)

    subs = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {name: ex.submit(call_one, client, model, img_b64, media, p, args.max_tokens)
                   for name, p in SUB_PROMPTS.items()}
        for name, fut in futures.items():
            try:
                subs[name] = fut.result()
                print(f"  {name}: {subs[name]['elapsed_sec']}s  parse_ok={subs[name]['parsed_json'] is not None}", flush=True)
            except Exception as e:
                print(f"  {name}: ERROR {type(e).__name__}: {e}", flush=True)
                subs[name] = {"error": f"{type(e).__name__}: {e}"}

    for name, res in subs.items():
        (run_dir / f"sub-{name}.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

    merged = merge_results(subs)
    (run_dir / "stage-10-parsed.json").write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "image": str(image_path),
        "mode": args.mode,
        "model": model,
        "run_dir": str(run_dir),
        "totals": {
            "views": len(merged.get("views") or []),
            "rooms": sum(len([e for e in v.get("elements", []) if e.get("type") == "room"]) for v in merged.get("views", [])),
            "walls": sum(len([e for e in v.get("elements", []) if e.get("type") == "wall"]) for v in merged.get("views", [])),
            "dims": sum(len(v.get("dimensions_raw", [])) for v in merged.get("views", [])),
        },
        "sub_usage": {name: r.get("usage") for name, r in subs.items()},
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {run_dir}", flush=True)
    print(f"totals: {summary['totals']}", flush=True)


if __name__ == "__main__":
    main()
