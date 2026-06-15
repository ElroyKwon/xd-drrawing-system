"""MAIN_bound.dxf 진단: 전체 bbox, 시트 영역별 INSERT 분포, XR-PLAN 내부 구조.

10_render 결과에서 관측된 현상:
- 전체 렌더: 거의 빈 이미지 (fit_page 가 너무 넓은 bbox 에 맞춰 기하가 축소됨)
- A04.03 crop: MAIN msp 의 room INSERT 만 일부 보이고, 평면 기하 (벽/그리드) 부족

진단 목표:
1. MAIN msp 의 전체 bbox 측정
2. sheet 영역별 (A04.01/02/03) INSERT·entity 수·bbox
3. XR-PLAN BLOCK 내부 엔티티의 좌표 분포 — 5 개 서브시트가 어느 위치에 있는지
4. A04.03 영역 (168200~252300, 0~84100) 에 실제로 있는 엔티티 종류
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

import ezdxf
from ezdxf.math import BoundingBox2d, Vec2

LAB = Path(__file__).parent
DXF_OUT = LAB / "_dxf_out"
MAIN_BOUND = DXF_OUT / "A04.01~03 확대평면도_bound.dxf"

SHEETS = {
    "A04.01": (0, 0, 84100, 84100),
    "A04.02": (84100, 0, 168200, 84100),
    "A04.03": (168200, 0, 252300, 84100),
}


def entity_bbox(entity) -> BoundingBox2d | None:
    try:
        box = entity.bbox()
    except Exception:
        return None
    if box is None or not box.has_data:
        return None
    return BoundingBox2d([Vec2(box.extmin.x, box.extmin.y), Vec2(box.extmax.x, box.extmax.y)])


def in_sheet(px, py, sheet_box) -> bool:
    x0, y0, x1, y1 = sheet_box
    return x0 <= px <= x1 and y0 <= py <= y1


def main():
    report: dict = {"dxf": str(MAIN_BOUND)}

    doc = ezdxf.readfile(MAIN_BOUND)
    msp = doc.modelspace()

    # (1) msp 전체 통계 + 전체 bbox (INSERT 위치 기준)
    msp_types = defaultdict(int)
    insert_positions = []  # (name, x, y)
    xs, ys = [], []

    for e in msp:
        msp_types[e.dxftype()] += 1
        if e.dxftype() == "INSERT":
            p = e.dxf.insert
            insert_positions.append((e.dxf.name, float(p.x), float(p.y)))
            xs.append(float(p.x))
            ys.append(float(p.y))

    report["msp_total_entities"] = sum(msp_types.values())
    report["msp_entity_types"] = dict(msp_types)

    if xs:
        report["msp_insert_position_bbox"] = {
            "x_min": min(xs), "x_max": max(xs),
            "y_min": min(ys), "y_max": max(ys),
            "width": max(xs) - min(xs),
            "height": max(ys) - min(ys),
        }

    # (2) sheet 영역별 INSERT 분포
    by_sheet = {name: defaultdict(int) for name in SHEETS}
    outside = defaultdict(int)
    for name, x, y in insert_positions:
        placed = False
        for sheet, box in SHEETS.items():
            if in_sheet(x, y, box):
                by_sheet[sheet][name] += 1
                placed = True
                break
        if not placed:
            outside[name] += 1

    report["inserts_per_sheet"] = {}
    for sheet, d in by_sheet.items():
        top = sorted(d.items(), key=lambda kv: -kv[1])[:20]
        report["inserts_per_sheet"][sheet] = {
            "total": sum(d.values()),
            "unique_blocks": len(d),
            "top20": top,
        }
    report["inserts_outside_sheets"] = {
        "total": sum(outside.values()),
        "top20": sorted(outside.items(), key=lambda kv: -kv[1])[:20],
    }

    # (3) XR-PLAN BLOCK 내부 탐색
    xrplan = doc.blocks.get("XR-PLAN")
    if xrplan is not None:
        xrplan_types = defaultdict(int)
        xrplan_inserts = []
        xs2, ys2 = [], []
        for e in xrplan:
            xrplan_types[e.dxftype()] += 1
            if e.dxftype() == "INSERT":
                p = e.dxf.insert
                xrplan_inserts.append((e.dxf.name, float(p.x), float(p.y)))
                xs2.append(float(p.x))
                ys2.append(float(p.y))

        xrplan_bbox = None
        for e in xrplan:
            if e.dxftype() in ("LWPOLYLINE", "LINE", "POLYLINE", "CIRCLE", "ARC"):
                bb = entity_bbox(e)
                if bb is None:
                    continue
                if xrplan_bbox is None:
                    xrplan_bbox = bb
                else:
                    xrplan_bbox.extend([bb.extmin, bb.extmax])

        info = {
            "total_entities": sum(xrplan_types.values()),
            "types": dict(xrplan_types),
        }
        if xs2:
            info["insert_position_bbox"] = {
                "x_min": min(xs2), "x_max": max(xs2),
                "y_min": min(ys2), "y_max": max(ys2),
            }
            info["top10_inserts"] = sorted(
                [(n, x, y) for n, x, y in xrplan_inserts],
                key=lambda t: (t[1], t[2]),
            )[:10]
        if xrplan_bbox is not None:
            info["geom_bbox"] = {
                "x_min": float(xrplan_bbox.extmin.x),
                "x_max": float(xrplan_bbox.extmax.x),
                "y_min": float(xrplan_bbox.extmin.y),
                "y_max": float(xrplan_bbox.extmax.y),
            }
        report["XR-PLAN_block"] = info

    # (4) msp 에서 A04.03 영역에 있는 INSERT 이름 unique 목록
    a0403_box = SHEETS["A04.03"]
    a0403_inserts = [(n, x, y) for n, x, y in insert_positions if in_sheet(x, y, a0403_box)]
    a0403_unique = defaultdict(int)
    for n, x, y in a0403_inserts:
        a0403_unique[n] += 1
    report["a0403_msp_inserts"] = {
        "total": len(a0403_inserts),
        "unique_blocks_count": len(a0403_unique),
        "top30": sorted(a0403_unique.items(), key=lambda kv: -kv[1])[:30],
    }

    # (5) msp 에서 전체 geom bbox (LINE/LWPOLYLINE/POLYLINE 기반)
    geom_bbox = None
    checked = 0
    for e in msp:
        if e.dxftype() not in ("LINE", "LWPOLYLINE", "POLYLINE"):
            continue
        bb = entity_bbox(e)
        if bb is None:
            continue
        checked += 1
        if geom_bbox is None:
            geom_bbox = bb
        else:
            geom_bbox.extend([bb.extmin, bb.extmax])
    if geom_bbox is not None:
        report["msp_geom_bbox_native"] = {
            "x_min": float(geom_bbox.extmin.x),
            "x_max": float(geom_bbox.extmax.x),
            "y_min": float(geom_bbox.extmin.y),
            "y_max": float(geom_bbox.extmax.y),
            "checked": checked,
        }

    (LAB / "11_diagnose_bound.out.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("wrote 11_diagnose_bound.out.json")

    # 요약 콘솔 출력
    print("\n=== MSP 전체 ===")
    print(f"entities: {report['msp_total_entities']}")
    print(f"types: {report['msp_entity_types']}")
    if "msp_insert_position_bbox" in report:
        b = report["msp_insert_position_bbox"]
        print(f"INSERT 위치 bbox: x [{b['x_min']:.0f}, {b['x_max']:.0f}], "
              f"y [{b['y_min']:.0f}, {b['y_max']:.0f}]")

    print("\n=== 시트별 INSERT ===")
    for sheet, data in report["inserts_per_sheet"].items():
        print(f"{sheet}: total={data['total']}, unique={data['unique_blocks']}, "
              f"top3={data['top20'][:3]}")
    print(f"밖: {report['inserts_outside_sheets']['total']}개")

    if "XR-PLAN_block" in report:
        x = report["XR-PLAN_block"]
        print(f"\n=== XR-PLAN BLOCK ===")
        print(f"entities: {x['total_entities']}")
        print(f"types: {x['types']}")
        if "geom_bbox" in x:
            g = x["geom_bbox"]
            print(f"geom_bbox: x [{g['x_min']:.0f}, {g['x_max']:.0f}], "
                  f"y [{g['y_min']:.0f}, {g['y_max']:.0f}]")

    print(f"\n=== A04.03 영역 msp INSERT ===")
    a = report["a0403_msp_inserts"]
    print(f"total: {a['total']}, unique_blocks: {a['unique_blocks_count']}")
    print(f"top10: {a['top30'][:10]}")


if __name__ == "__main__":
    main()
