"""
test_consensus.py — C단계: 두 모델의 stage-10 결과를 병합해 합의 JSON 생성.

규칙:
- grid/level: 더 완전한(라벨·간격 채워진) 쪽 채택, 불일치 시 diff 기록
- rooms: 이름 키로 union, 동일 이름이면 polygon_grid 긴 쪽 채택
- dimensions_raw: union, (text, from_grid, to_grid) 키로 dedup
- 객체(wall/column/door/stair/elevator/shaft/void): union, type+anchor 키로 dedup

사용:
  python test_consensus.py <opus.json> <gemini.json> <out.json>
"""
import argparse
import json
import sys
from pathlib import Path


def score_grid(g):
    if not g:
        return -1
    score = 0
    for k in ("x_labels", "y_labels"):
        score += len(g.get(k) or [])
    for k in ("x_spacings_mm", "y_spacings_mm"):
        vals = g.get(k) or []
        score += sum(1 for v in vals if v is not None)
    return score


def norm_name(s):
    if not s:
        return ""
    return str(s).strip().lower().replace(" ", "").replace("-", "")


def dedup_dims(dims):
    seen = set()
    out = []
    for d in dims:
        key = (d.get("text"), tuple(d.get("from_grid") or []), tuple(d.get("to_grid") or []))
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out


def obj_key(el):
    t = el.get("type")
    if t == "wall":
        return ("wall", tuple(tuple(p) for p in (el.get("path_grid") or [])))
    if t in ("column", "elevator", "shaft", "stair") and el.get("at_grid"):
        return (t, tuple(el.get("at_grid")))
    if el.get("polygon_grid"):
        return (t, tuple(tuple(p) for p in el.get("polygon_grid") or []))
    if el.get("on_wall_from") and el.get("on_wall_to"):
        return (t, tuple(el.get("on_wall_from")), tuple(el.get("on_wall_to")))
    return (t, el.get("id"), el.get("label") or el.get("name"))


def merge_views(v_a, v_b):
    """두 view를 합의 view로 병합."""
    ga, gb = v_a.get("grid"), v_b.get("grid")
    grid = ga if score_grid(ga) >= score_grid(gb) else gb

    la = v_a.get("level") or {}
    lb = v_b.get("level") or {}
    level = {
        "name": la.get("name") or lb.get("name"),
        "elevation_mm": la.get("elevation_mm") if la.get("elevation_mm") is not None else lb.get("elevation_mm"),
        "ceiling_height_mm": la.get("ceiling_height_mm") if la.get("ceiling_height_mm") is not None else lb.get("ceiling_height_mm"),
    }

    rooms_a = [e for e in (v_a.get("elements") or []) if e.get("type") == "room"]
    rooms_b = [e for e in (v_b.get("elements") or []) if e.get("type") == "room"]
    merged_rooms = {}
    for r in rooms_a + rooms_b:
        key = norm_name(r.get("name")) or r.get("id")
        if not key:
            continue
        if key not in merged_rooms:
            merged_rooms[key] = r
        else:
            existing = merged_rooms[key]
            if len(r.get("polygon_grid") or []) > len(existing.get("polygon_grid") or []):
                merged_rooms[key] = r

    objs_a = [e for e in (v_a.get("elements") or []) if e.get("type") != "room"]
    objs_b = [e for e in (v_b.get("elements") or []) if e.get("type") != "room"]
    merged_objs = {}
    for e in objs_a + objs_b:
        k = obj_key(e)
        if k not in merged_objs:
            merged_objs[k] = e

    dims = dedup_dims((v_a.get("dimensions_raw") or []) + (v_b.get("dimensions_raw") or []))

    annots = list(dict.fromkeys((v_a.get("annotations_ko") or []) + (v_b.get("annotations_ko") or [])))

    return {
        "view_id": v_a.get("view_id") or v_b.get("view_id"),
        "view_label": v_a.get("view_label") or v_b.get("view_label"),
        "view_scale": v_a.get("view_scale") or v_b.get("view_scale"),
        "grid": grid,
        "level": level,
        "elements": list(merged_rooms.values()) + list(merged_objs.values()),
        "dimensions_raw": dims,
        "annotations_ko": annots,
        "unresolved": [],
        "_merge_stats": {
            "rooms_a": len(rooms_a), "rooms_b": len(rooms_b), "rooms_merged": len(merged_rooms),
            "objs_a": len(objs_a), "objs_b": len(objs_b), "objs_merged": len(merged_objs),
            "dims_a": len(v_a.get("dimensions_raw") or []), "dims_b": len(v_b.get("dimensions_raw") or []),
            "dims_merged": len(dims),
        },
    }


def merge_sheets(a, b):
    views_a = a.get("views") or []
    views_b = b.get("views") or []
    n = max(len(views_a), len(views_b))
    merged = []
    for i in range(n):
        va = views_a[i] if i < len(views_a) else {}
        vb = views_b[i] if i < len(views_b) else {}
        if not va:
            merged.append(vb)
        elif not vb:
            merged.append(va)
        else:
            merged.append(merge_views(va, vb))
    return {
        "sheet_number": a.get("sheet_number") or b.get("sheet_number"),
        "views": merged,
        "global_confidence": max(a.get("global_confidence") or 0, b.get("global_confidence") or 0),
        "_source": "consensus_merge",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_a")
    ap.add_argument("input_b")
    ap.add_argument("output")
    args = ap.parse_args()
    a = json.loads(Path(args.input_a).read_text(encoding="utf-8"))
    b = json.loads(Path(args.input_b).read_text(encoding="utf-8"))
    merged = merge_sheets(a, b)
    Path(args.output).write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {args.output}")
    for i, v in enumerate(merged["views"]):
        st = v.get("_merge_stats") or {}
        print(f"  view[{i}] {v.get('view_label') or v.get('view_id')}: {st}")


if __name__ == "__main__":
    main()
