"""Phase B — step 1: 건축 PDF 벡터/텍스트 여부 + p062 대응 페이지 식별.

근거:
- `_png_dpi400/arch_p062.png` 는 이전 세션(`04-session-2026-04-21-ultrathink.md`)에서
  건축 PDF 를 pdftoppm 또는 동급 도구로 400dpi 변환한 결과.
- 파일명 규칙상 `arch_pNNN` 의 NNN 은 PDF 페이지 번호(1-based) 로 추정.
- 본 스크립트는 그 가정을 검증하고 타이틀블록 텍스트를 덤프한다.

출력: 01_probe_pdf.out.json (다음 단계 소비)
"""
from __future__ import annotations
import json, sys
from pathlib import Path

import pdfplumber

PDF = Path(r"D:/_Project/prototype-도면지식관리-mvp/dwg/1) 건축공사/0. PDF 도면/[LS ELECTRIC R-Center 구축] 1. 건축.pdf")
OUT = Path(__file__).parent / "01_probe_pdf.out.json"

assert PDF.exists(), f"not found: {PDF}"

result = {"pdf": str(PDF), "size_mb": round(PDF.stat().st_size / 1024 / 1024, 2)}

with pdfplumber.open(PDF) as pdf:
    result["n_pages"] = len(pdf.pages)

    # 1페이지: 벡터/텍스트 존재 확인
    p0 = pdf.pages[0]
    result["page_1"] = {
        "width": p0.width, "height": p0.height,
        "n_chars": len(p0.chars),
        "n_lines": len(p0.lines),
        "n_rects": len(p0.rects),
        "n_curves": len(p0.curves) if hasattr(p0, 'curves') else 0,
        "sample_text": p0.extract_text()[:500] if p0.chars else None,
    }

    # 62 페이지 (arch_p062 가정) — 타이틀블록 추출 시도
    target_idx = 62 - 1  # 1-based → 0-based
    if target_idx < len(pdf.pages):
        p62 = pdf.pages[target_idx]
        # 타이틀블록은 보통 우하단. 전체 텍스트 먼저 + 우하단 크롭.
        full_text = p62.extract_text() or ""
        # 우하단 1/4 영역 크롭
        w, h = p62.width, p62.height
        crop = p62.crop((w * 0.7, h * 0.7, w, h))
        crop_text = crop.extract_text() or ""
        result["page_62"] = {
            "width": w, "height": h,
            "n_chars": len(p62.chars),
            "full_text_head": full_text[:1500],
            "full_text_tail": full_text[-800:] if len(full_text) > 800 else full_text,
            "bottom_right_quadrant_text": crop_text,
        }
    else:
        result["page_62"] = {"error": f"only {len(pdf.pages)} pages"}

    # 인접 페이지들도 맛보기 — p060~p064 까지 (다중 시트 비교)
    neighbors = {}
    for n in (60, 61, 63, 64):
        idx = n - 1
        if idx < len(pdf.pages):
            p = pdf.pages[idx]
            t = p.extract_text() or ""
            neighbors[f"page_{n}"] = {
                "n_chars": len(p.chars),
                "head": t[:300],
                "tail": t[-400:] if len(t) > 400 else t,
            }
    result["neighbors"] = neighbors

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {OUT}")
print(f"pages={result['n_pages']} size={result['size_mb']}MB")
print(f"page_1 chars={result['page_1']['n_chars']} lines={result['page_1']['n_lines']}")
if "page_62" in result and "bottom_right_quadrant_text" in result["page_62"]:
    print("--- page 62 bottom-right ---")
    print(result["page_62"]["bottom_right_quadrant_text"])
