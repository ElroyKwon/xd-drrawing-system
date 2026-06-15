"""시트 영역에 교차하는 msp 엔티티만 필터링해서 draw_entities + fit_page 렌더.

관측: 10_render_bound (fit_page=True) 에서 전체 msp bbox 가 453m×90m 이라 기하가
픽셀 수준으로 축소됨. sheet 영역만의 기하로 한정하면 fit 스케일이 커져 볼 수 있음.

핵심 질문: XR-PLAN INSERT (음의 y 위치) 가 sheet 영역과 교차하는가? XCLIP 을
ezdxf 가 어떻게 처리하는가?
"""
from __future__ import annotations
import json
import time
from collections import defaultdict
from pathlib import Path

import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.pymupdf import PyMuPdfBackend
from ezdxf.addons.drawing.layout import Page, Settings, Margins
from ezdxf.math import BoundingBox2d, Vec2

LAB = Path(__file__).parent
DXF_OUT = LAB / "_dxf_out"
MAIN_BOUND = DXF_OUT / "A04.01~03 확대평면도_bound.dxf"
RENDER_DIR = LAB / "renders"
RENDER_DIR.mkdir(exist_ok=True)

SHEETS = {
    "A04_01": (0, 0, 84100, 84100),
    "A04_02": (84100, 0, 168200, 84100),
    "A04_03": (168200, 0, 252300, 84100),
}


def bbox_intersects(a: BoundingBox2d, b_tuple) -> bool:
    x0, y0, x1, y1 = b_tuple
    if not a.has_data:
        return False
    return not (a.extmax.x < x0 or a.extmin.x > x1 or
                a.extmax.y < y0 or a.extmin.y > y1)


def entity_bbox_safe(e):
    try:
        box = e.bbox()
        if box is None or not box.has_data:
            return None
        return BoundingBox2d([Vec2(box.extmin.x, box.extmin.y),
                              Vec2(box.extmax.x, box.extmax.y)])
    except Exception:
        return None


def filter_entities_for_sheet(msp, sheet_box):
    """sheet_box 와 bbox 가 교차하는 엔티티만 선택.

    INSERT 의 bbox 는 block 전체 기하 범위를 포함 — sheet 밖에 있어도 intersect 면 포함.
    bbox 계산 실패 시 (예: DIMENSION 등) 안전하게 포함.
    """
    stats = defaultdict(int)
    kept = []
    for e in msp:
        bb = entity_bbox_safe(e)
        if bb is None:
            kept.append(e)
            stats[f"{e.dxftype()}_nobbox"] += 1
            continue
        if bbox_intersects(bb, sheet_box):
            kept.append(e)
            stats[e.dxftype()] += 1
    return kept, dict(stats)


def render_entities(doc, entities, out_png, page_mm=(841, 594), dpi=200):
    ctx = RenderContext(doc)
    backend = PyMuPdfBackend()
    backend.set_background("#ffffff")
    t0 = time.time()
    Frontend(ctx, backend).draw_entities(entities)
    t_draw = time.time() - t0
    page = Page(width=page_mm[0], height=page_mm[1], margins=Margins.all(5))
    settings = Settings(fit_page=True)
    t1 = time.time()
    png = backend.get_pixmap_bytes(page, fmt="png", dpi=dpi, alpha=False, settings=settings)
    t_png = time.time() - t1
    out_png.write_bytes(png)
    return {
        "out": out_png.name, "kb": round(len(png)/1024, 1),
        "t_draw_s": round(t_draw, 2), "t_png_s": round(t_png, 2),
    }


def main():
    report = {"dxf": str(MAIN_BOUND), "results": {}}

    print("== loading MAIN_bound ==")
    t0 = time.time()
    doc = ezdxf.readfile(MAIN_BOUND)
    print(f"  read {round(time.time()-t0, 2)}s")
    msp = doc.modelspace()

    for sheet_key, box in SHEETS.items():
        print(f"\n== {sheet_key} box={box} ==")
        entities, stats = filter_entities_for_sheet(msp, box)
        print(f"  filtered entities: {len(entities)}")
        print(f"  stats: {stats}")

        out = RENDER_DIR / f"main_bound_filtered_{sheet_key}.png"
        try:
            info = render_entities(doc, entities, out)
            print(f"  render: {info}")
            report["results"][sheet_key] = {"filter_stats": stats, **info}
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {e}")
            report["results"][sheet_key] = {
                "filter_stats": stats, "error": f"{type(e).__name__}: {e}",
            }

    (LAB / "14_render_filtered.out.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\nwrote 14_render_filtered.out.json")


if __name__ == "__main__":
    main()
