"""validate_coordinate_system — scene_bbox 덤프에서 좌표계 분리 버그 탐지.

교훈 소스: docs/ai-3d-builder/threejs-scene/p062/decisions.md §2.1~2.3
- BUG-A: makeExtrudedShape 이중 translate (층 한 칸 위로 떠 있음)
- BUG-B: Z 부호 분리 (rooms Z 음수 / walls Z 양수)
- BUG-C: 슬라브 반투명 → 바닥 인식 X (렌더 설정, bbox로는 불검출)
"""
from .base import rel


SCHEMA = {
    "name": "validate_coordinate_system",
    "description": (
        "render_preview가 반환한 scene_bbox 덤프를 입력받아 좌표계 분리 버그를 감지한다. "
        "특히 같은 view 내 rooms/walls/slabs 의 Z 부호가 일치하는지, "
        "Y 값이 층 스택 순서(1FL<2FL<RFL)인지, 바닥이 baseY와 일치하는지 검사. "
        "출력: issues[] — severity ∈ {error, warn, info}. "
        "BUG-A (이중 translate), BUG-B (Z 부호 분리), BUG 기타 방지용."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "scene_bbox": {
                "type": "object",
                "description": (
                    "render_preview 반환값 scene_bbox. 예상 형식: "
                    "{views: {v1: {rooms: {min, max}, walls: {min, max}, slabs: {min, max}}, ...}, "
                    "floor_stack: [{name, y}, ...]}"
                ),
            },
            "expected_levels_mm": {
                "type": "object",
                "description": "선택. level-stack.yml 의 levels_mm. 예: {GL: 94000, 1FL: 94200, 2FL: 99700, RFL: 104200}",
            },
        },
        "required": ["scene_bbox"],
    },
}


def _sign_of(a, b):
    if a < 0 and b < 0:
        return "negative"
    if a > 0 and b > 0:
        return "positive"
    if a == 0 == b:
        return "zero"
    return "mixed"


def execute(tool_input, context=None):
    bbox = tool_input.get("scene_bbox") or {}
    expected_levels = tool_input.get("expected_levels_mm") or {}

    issues = []

    if not bbox:
        issues.append({
            "severity": "error", "type": "empty_bbox",
            "detail": "scene_bbox가 비어 있음 — window.__scene.dumpBBox() 훅 누락 의심",
        })
        return {"issues": issues, "ok": False}

    views = bbox.get("views") or bbox.get("groups") or {}
    if isinstance(views, list):
        views = {str(i): v for i, v in enumerate(views)}

    for view_id, groups in (views.items() if isinstance(views, dict) else []):
        zs = {}
        for g_name in ("rooms", "walls", "slabs", "grid"):
            g = groups.get(g_name)
            if not g:
                continue
            mn = g.get("min") or [None, None, None]
            mx = g.get("max") or [None, None, None]
            if len(mn) >= 3 and len(mx) >= 3 and mn[2] is not None and mx[2] is not None:
                zs[g_name] = _sign_of(mn[2], mx[2])

        # Z 부호 분리 검사 (BUG-B)
        signs = set(zs.values())
        if len(signs) >= 2 and "mixed" not in signs:
            if "positive" in signs and "negative" in signs:
                issues.append({
                    "severity": "error",
                    "type": "z_axis_split",
                    "view": view_id,
                    "detail": f"Z 부호 분리 탐지: {zs}. decisions.md §2.2 BUG-B 재현 위험.",
                    "fix_hint": (
                        "makeExtrudedShape 에서 shape.moveTo(x, y) 대신 shape.moveTo(x, -y) 사용 "
                        "(rotateX(-π/2) 적용 후 부호 일치)."
                    ),
                })

        # Y 범위 (층 스택 순서)
        ys_per_group = {}
        for g_name, g in (groups.items() if isinstance(groups, dict) else []):
            if not isinstance(g, dict):
                continue
            mn = g.get("min") or [None, None, None]
            mx = g.get("max") or [None, None, None]
            if len(mn) >= 2 and len(mx) >= 2 and mn[1] is not None and mx[1] is not None:
                ys_per_group[g_name] = (mn[1], mx[1])

        # BUG-A 힌트: 같은 층에서 rooms 의 baseY 가 slab 의 top 보다 한 층(높이) 위
        if "rooms" in ys_per_group and "slabs" in ys_per_group:
            r_bot = ys_per_group["rooms"][0]
            s_top = ys_per_group["slabs"][1]
            gap = r_bot - s_top
            if gap > 2000:  # 2m 초과 gap → 의심
                issues.append({
                    "severity": "warn",
                    "type": "rooms_above_slab",
                    "view": view_id,
                    "detail": f"rooms bottom Y={r_bot} 이 slab top Y={s_top} 보다 {gap}mm 위. BUG-A(이중 translate) 의심.",
                    "fix_hint": "makeExtrudedShape 내부의 mesh.geometry.translate(0, heightMm, 0) 삭제.",
                })

    # 기대 층 스택 비교
    fs = bbox.get("floor_stack") or []
    if fs and expected_levels:
        for entry in fs:
            name = entry.get("name")
            y = entry.get("y")
            if name in expected_levels and y is not None:
                diff = y - expected_levels[name]
                if abs(diff) > 50:
                    issues.append({
                        "severity": "warn",
                        "type": "floor_y_mismatch",
                        "detail": f"{name}: scene Y={y} vs expected {expected_levels[name]} (diff={diff}mm)",
                    })

    return {
        "issues": issues,
        "ok": all(i.get("severity") != "error" for i in issues),
        "error_count": sum(1 for i in issues if i.get("severity") == "error"),
        "warn_count": sum(1 for i in issues if i.get("severity") == "warn"),
    }
