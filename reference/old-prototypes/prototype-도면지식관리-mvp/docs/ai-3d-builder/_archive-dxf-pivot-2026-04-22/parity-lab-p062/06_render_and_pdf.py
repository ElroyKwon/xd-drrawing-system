"""Phase D — DXF 자가 렌더 + 공급 PDF 페이지 PNG 추출.

축소 범위 (오늘 실험):
  1. MAIN DXF 의 modelspace 를 렌더 (INSERT 중 XR-* 는 비어있으므로 주석·타이틀블록만)
  2. XR-PLAN.dxf 의 modelspace 를 독립 렌더 (실제 평면 기하)
  3. 공급 PDF page 62 를 fitz 로 400dpi PNG
  4. 3장의 이미지를 옆에 놓고 시각 확인

후속 세션 (축소 제외):
  - xref 블록 합성 (MAIN 의 XR-PLAN 블록을 XR-PLAN.dxf msp 로 채워 renderable 로 만들기)
  - A04.03 sheet 영역 (168200, 0)~(252300, 84100) crop
  - Affine alignment + IoU 측정
"""
from __future__ import annotations
import json, sys
from pathlib import Path

import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.pymupdf import PyMuPdfBackend
from ezdxf.addons.drawing.config import Configuration
import fitz  # PyMuPDF

LAB = Path(__file__).parent
DXF_OUT = LAB / "_dxf_out"
MAIN = DXF_OUT / "A04.01~03 확대평면도.dxf"
XR_PLAN = DXF_OUT / "xref" / "XR-PLAN.dxf"
SUPPLY_PDF = Path(r"D:/_Project/prototype-도면지식관리-mvp/dwg/1) 건축공사/0. PDF 도면/[LS ELECTRIC R-Center 구축] 1. 건축.pdf")

RENDER_DIR = LAB / "renders"
RENDER_DIR.mkdir(exist_ok=True)

out = {}

def render_modelspace_to_png(dxf_path: Path, out_png: Path, dpi: int = 150):
    """DXF modelspace → PNG (fitz backend)."""
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    ctx = RenderContext(doc)
    backend = PyMuPdfBackend()
    frontend = Frontend(ctx, backend)
    frontend.draw_layout(msp)

    # fitz Document 추출
    fitz_doc = backend.get_pdf_bytes()
    # ezdxf 가 반환하는 건 bytes (PDF). fitz 로 다시 열어 PNG 저장
    tmp = fitz.open(stream=fitz_doc, filetype="pdf")
    assert len(tmp) >= 1, "empty fitz doc"
    page = tmp[0]
    # 픽스맵 (dpi 기반)
    matrix = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    pix.save(str(out_png))
    tmp.close()
    return {"size_kb": round(out_png.stat().st_size / 1024, 1),
            "w": pix.width, "h": pix.height}

# ---- 1. MAIN modelspace 렌더 ----
print("== rendering MAIN modelspace ==")
try:
    main_info = render_modelspace_to_png(MAIN, RENDER_DIR / "main_msp.png", dpi=150)
    print(f"  main_msp.png: {main_info}")
    out["main_msp"] = main_info
except Exception as e:
    print(f"  MAIN render FAILED: {type(e).__name__}: {e}")
    out["main_msp_error"] = f"{type(e).__name__}: {e}"

# ---- 2. XR-PLAN modelspace 렌더 ----
print("\n== rendering XR-PLAN modelspace ==")
try:
    xp_info = render_modelspace_to_png(XR_PLAN, RENDER_DIR / "xr_plan_msp.png", dpi=100)
    print(f"  xr_plan_msp.png: {xp_info}")
    out["xr_plan_msp"] = xp_info
except Exception as e:
    print(f"  XR-PLAN render FAILED: {type(e).__name__}: {e}")
    out["xr_plan_msp_error"] = f"{type(e).__name__}: {e}"

# ---- 3. 공급 PDF page 62 → PNG ----
print("\n== extracting supply PDF page 62 as PNG ==")
try:
    sup = fitz.open(str(SUPPLY_PDF))
    page = sup[61]  # 0-indexed
    pix = page.get_pixmap(matrix=fitz.Matrix(400/72, 400/72), alpha=False)
    out_png = RENDER_DIR / "supply_p62_400dpi.png"
    pix.save(str(out_png))
    sup.close()
    info = {"size_kb": round(out_png.stat().st_size / 1024, 1), "w": pix.width, "h": pix.height}
    print(f"  supply_p62_400dpi.png: {info}")
    out["supply_p62"] = info
except Exception as e:
    print(f"  PDF extract FAILED: {type(e).__name__}: {e}")
    out["supply_p62_error"] = f"{type(e).__name__}: {e}"

# ---- 4. MAIN 만 A04.03 영역으로 crop 된 view 도 시도 (xref 비어있어도 주석/타이틀은 볼 수 있음) ----
# ezdxf drawing 에 ViewBox 지원이 버전마다 다름. 여기선 전체 렌더 후 PIL crop 이 더 안전.

(LAB / "06_render_and_pdf.out.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote 06_render_and_pdf.out.json")
