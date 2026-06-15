"""Phase E 준비: 공급 PDF page 62 에서 그리드 라벨 좌표 추출.

도면의 그리드 라벨: A/B/C/D (수평 그리드), 5/6/7 (수직 그리드)
이들 좌표 → DXF 의 그리드 라벨 좌표와 매칭 → affine 변환 추정

pdfplumber.chars 에서 single-char "A"/"B"/"C"/"D"/"5"/"6"/"7" 을 위치와 함께 추출.
타이틀블록 영역(우하단) 은 제외해서 도면 영역의 그리드 라벨만 남김.
"""
from __future__ import annotations
import json
from pathlib import Path

import pdfplumber

PDF = Path(r"D:/_Project/prototype-도면지식관리-mvp/dwg/1) 건축공사/0. PDF 도면/[LS ELECTRIC R-Center 구축] 1. 건축.pdf")
LAB = Path(__file__).parent

with pdfplumber.open(PDF) as pdf:
    p = pdf.pages[61]  # page 62
    w, h = p.width, p.height
    # 타이틀블록 제외: 우하단 30% × 30% 영역 제거
    tb_x_min = w * 0.7
    tb_y_min = h * 0.7

    grid_chars = {"A": [], "B": [], "C": [], "D": [], "5": [], "6": [], "7": []}
    all_single = []
    for ch in p.chars:
        t = ch.get("text", "")
        if len(t) != 1:
            continue
        x, y = ch["x0"], ch["top"]
        # 타이틀블록 영역 제외
        if x >= tb_x_min and y >= tb_y_min:
            continue
        all_single.append({"t": t, "x": round(x, 1), "y": round(y, 1),
                           "size": round(ch.get("size", 0), 1)})
        if t in grid_chars:
            grid_chars[t].append({"x": round(x, 1), "y": round(y, 1),
                                  "size": round(ch.get("size", 0), 1)})

# 그리드 라벨은 보통 (a) 도면 상단·좌측 여백, (b) 큰 폰트 (circled), (c) 특정 Y 또는 X 에 정렬
# 간단 휴리스틱: 폰트 크기 상위 기반 필터
for k in grid_chars:
    chars = grid_chars[k]
    # 크기가 큰 것만 남김 (그리드 라벨은 일반 TEXT 보다 큼)
    if chars:
        max_size = max(c["size"] for c in chars)
        thresh = max_size * 0.9
        grid_chars[k] = [c for c in chars if c["size"] >= thresh]

out = {
    "pdf": str(PDF),
    "page": 62,
    "width_pt": w, "height_pt": h,
    "titleblock_excluded_from": {"x_min": tb_x_min, "y_min": tb_y_min},
    "grid_label_candidates": grid_chars,
    "total_single_chars_in_drawing_area": len(all_single),
}

for k, v in grid_chars.items():
    print(f"  '{k}': {len(v)} candidates  sample={v[:3]}")

(LAB / "07_extract_pdf_grid.out.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote 07_extract_pdf_grid.out.json (total single-chars in drawing area: {len(all_single)})")
