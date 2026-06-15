"""Phase D (수정): ezdxf 1.4 API — layout.Page + get_pixmap_bytes."""
from __future__ import annotations
import json
from pathlib import Path

import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.pymupdf import PyMuPdfBackend
from ezdxf.addons.drawing.layout import Page, Settings, Margins

LAB = Path(__file__).parent
DXF_OUT = LAB / "_dxf_out"
MAIN = DXF_OUT / "A04.01~03 확대평면도.dxf"
XR_PLAN = DXF_OUT / "xref" / "XR-PLAN.dxf"
RENDER_DIR = LAB / "renders"
RENDER_DIR.mkdir(exist_ok=True)

def render_msp(dxf_path: Path, out_png: Path, page_mm=(420, 297), dpi=150):
    """DXF modelspace → PNG. 용지: A3 landscape 기본, fit_page."""
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    ctx = RenderContext(doc)
    backend = PyMuPdfBackend()
    backend.set_background('#ffffff')
    Frontend(ctx, backend).draw_layout(msp)

    page = Page(width=page_mm[0], height=page_mm[1], margins=Margins.all(5))
    settings = Settings(fit_page=True)
    png_bytes = backend.get_pixmap_bytes(page, fmt='png', dpi=dpi, alpha=False, settings=settings)
    out_png.write_bytes(png_bytes)
    return {"bytes": len(png_bytes), "size_kb": round(len(png_bytes)/1024, 1)}

out = {}

print("== MAIN msp → PNG (A3 landscape, 150dpi) ==")
try:
    info = render_msp(MAIN, RENDER_DIR / "main_msp.png")
    print(f"  OK  {info}")
    out["main_msp"] = info
except Exception as e:
    print(f"  FAILED: {type(e).__name__}: {e}")
    out["main_msp_error"] = f"{type(e).__name__}: {e}"

print("\n== XR-PLAN msp → PNG (A1 landscape-ish, 100dpi) ==")
try:
    info = render_msp(XR_PLAN, RENDER_DIR / "xr_plan_msp.png", page_mm=(841, 594), dpi=100)
    print(f"  OK  {info}")
    out["xr_plan_msp"] = info
except Exception as e:
    print(f"  FAILED: {type(e).__name__}: {e}")
    out["xr_plan_msp_error"] = f"{type(e).__name__}: {e}"

# PDF page 62 이미 06에서 성공적으로 떨어짐 — 재사용
supply_png = RENDER_DIR / "supply_p62_400dpi.png"
if supply_png.exists():
    out["supply_p62_exists"] = True
    print(f"\n== supply PNG reused: {supply_png.name} ({supply_png.stat().st_size/1024:.1f} KB)")

(LAB / "06b_render_and_pdf.out.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("\nwrote 06b_render_and_pdf.out.json")
