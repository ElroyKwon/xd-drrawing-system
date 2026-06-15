"""시트 영역별 crop 렌더 (A04.01 / A04.02 / A04.03).

진단 11 결과: A04.03 영역에는 벽 기하 INSERT 가 없고, XR-PLAN 의 실제 평면은
A04.01·02 영역에 투영됨. 이 스크립트는 3개 시트 영역을 각각 crop 렌더하여
"합성 효과가 나타나는 곳"과 "gap 이 드러나는 곳"을 분리 시각화한다.

산출물:
- renders/main_bound_sheet_A04_01.png
- renders/main_bound_sheet_A04_02.png
- renders/main_bound_sheet_A04_03.png
"""
from __future__ import annotations
import json
import traceback
import time
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

# 시트 영역 (x0, y0, x1, y1) — margin 적용
MARGIN = 3000
SHEETS = {
    "A04_01": (0, 0, 84100, 84100),
    "A04_02": (84100, 0, 168200, 84100),
    "A04_03": (168200, 0, 252300, 84100),
}

# A04.01 / A04.02 영역 은 XR-PLAN 내부 기하가 주로 **음의 y** 위치에 있으므로 확장
# XR-PLAN INSERT 위치 (-214810, -34637) 등 참고. 하지만 sheet 영역 기준으로 crop 하면
# XR-PLAN 렌더 자체가 안 나올 수 있다. render_box 는 **sheet 좌표 기준** 으로 하되,
# XR-PLAN INSERT 가 sheet 영역 외부에 있으면 기하가 crop 밖으로 나감.
# → 일단 sheet 영역만 렌더하고 결과 확인


def render_with_box(dxf_path, out_png, box, page_mm=(841, 594), dpi=150):
    t0 = time.time()
    doc = ezdxf.readfile(dxf_path)
    t_read = time.time() - t0

    msp = doc.modelspace()
    ctx = RenderContext(doc)
    backend = PyMuPdfBackend()
    backend.set_background("#ffffff")

    t1 = time.time()
    Frontend(ctx, backend).draw_layout(msp)
    t_draw = time.time() - t1

    page = Page(width=page_mm[0], height=page_mm[1], margins=Margins.all(5))
    settings = Settings(fit_page=True)

    t2 = time.time()
    png_bytes = backend.get_pixmap_bytes(
        page, fmt="png", dpi=dpi, alpha=False, settings=settings, render_box=box,
    )
    t_png = time.time() - t2

    out_png.write_bytes(png_bytes)
    return {
        "out": out_png.name, "kb": round(len(png_bytes) / 1024, 1),
        "t_read_s": round(t_read, 2),
        "t_draw_s": round(t_draw, 2),
        "t_png_s": round(t_png, 2),
    }


def main():
    report = {"dxf": str(MAIN_BOUND), "results": {}}

    # DXF 는 한 번만 로드해도 되지만, render_box 를 바꾸려면 backend 재구성이 필요.
    # PyMuPdfBackend 는 draw_layout 후에 get_pixmap_bytes 로 render_box 만 바꿔도 호출 가능할 것.
    # 하지만 우리는 검증을 위해 각 시트마다 새로 로드.

    for sheet_key, (x0, y0, x1, y1) in SHEETS.items():
        box = BoundingBox2d([
            Vec2(x0 - MARGIN, y0 - MARGIN),
            Vec2(x1 + MARGIN, y1 + MARGIN),
        ])
        out = RENDER_DIR / f"main_bound_sheet_{sheet_key}.png"
        print(f"== {sheet_key} box={box} ==")
        try:
            info = render_with_box(MAIN_BOUND, out, box)
            print(f"  OK {info}")
            report["results"][sheet_key] = info
        except Exception as e:
            err = {
                "error": f"{type(e).__name__}: {e}",
                "traceback": traceback.format_exc(),
            }
            print(f"  FAILED: {err['error']}")
            report["results"][sheet_key] = err

    (LAB / "12_render_per_sheet.out.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\nwrote 12_render_per_sheet.out.json")


if __name__ == "__main__":
    main()
