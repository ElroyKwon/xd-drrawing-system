"""바인딩된 MAIN DXF (A04.01~03 확대평면도_bound.dxf) 의 modelspace 렌더.

이전 (06b) 에는 MAIN msp 가 empty bbox 로 실패했으나, xref 합성 후에는
INSERT 들이 실제 기하를 담은 BLOCK 을 참조하므로 렌더 가능해야 함.

산출물:
- `renders/main_bound_msp.png`  — 전체 A04.01~03 (3 시트 가로 배치)
- `renders/main_bound_a0403.png` — A04.03 영역만 crop (render_box 사용)
"""
from __future__ import annotations
import json
import time
import traceback
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


def render_msp(
    dxf_path: Path,
    out_png: Path,
    page_mm=(1189, 841),   # A0 landscape (3 시트 가로 합본)
    dpi=150,
    render_box: BoundingBox2d | None = None,
):
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
    kwargs = dict(fmt="png", dpi=dpi, alpha=False, settings=Settings(fit_page=True))
    if render_box is not None:
        kwargs["render_box"] = render_box

    t2 = time.time()
    png_bytes = backend.get_pixmap_bytes(page, **kwargs)
    t_png = time.time() - t2

    out_png.write_bytes(png_bytes)
    return {
        "out": out_png.name,
        "bytes": len(png_bytes),
        "kb": round(len(png_bytes) / 1024, 1),
        "t_read_s": round(t_read, 2),
        "t_draw_s": round(t_draw, 2),
        "t_png_s": round(t_png, 2),
    }


def main():
    report = {"dxf": str(MAIN_BOUND)}

    if not MAIN_BOUND.exists():
        report["fatal"] = "MAIN_BOUND not found"
        _save(report)
        return

    # (1) 전체 렌더 (A0 용지, 150dpi)
    print("== [1] MAIN_bound msp 전체 렌더 (A0 landscape, 150dpi) ==")
    try:
        info = render_msp(MAIN_BOUND, RENDER_DIR / "main_bound_msp.png")
        report["main_bound_full"] = info
        print(f"  OK {info}")
    except Exception as e:
        err = {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()}
        report["main_bound_full_error"] = err
        print(f"  FAILED: {err['error']}")

    # (2) A04.03 영역 crop 렌더
    # 타이틀블록 좌표 (168200, 0). A1 용지 폭 84100 기준으로 (168200, 0) ~ (252300, 84100)
    # 여유 margin 5000 mm
    a0403_box = BoundingBox2d([
        Vec2(168200 - 5000, 0 - 5000),
        Vec2(252300 + 5000, 84100 + 5000),
    ])
    print("\n== [2] A04.03 영역 crop 렌더 (A1 landscape, 200dpi) ==")
    print(f"  render_box: {a0403_box}")
    try:
        info = render_msp(
            MAIN_BOUND,
            RENDER_DIR / "main_bound_a0403.png",
            page_mm=(841, 594),  # A1 landscape
            dpi=200,
            render_box=a0403_box,
        )
        report["main_bound_a0403"] = info
        print(f"  OK {info}")
    except Exception as e:
        err = {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()}
        report["main_bound_a0403_error"] = err
        print(f"  FAILED: {err['error']}")

    _save(report)


def _save(report):
    (LAB / "10_render_bound.out.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\nwrote 10_render_bound.out.json")


if __name__ == "__main__":
    main()
