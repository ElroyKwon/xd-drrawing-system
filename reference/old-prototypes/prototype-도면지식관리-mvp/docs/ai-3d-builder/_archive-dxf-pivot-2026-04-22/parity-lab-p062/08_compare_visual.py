"""Phase F — 시각 비교: 3장 나란히 + 기본 지표.

렌더 완료 후 실행.
Inputs:
  renders/main_msp.png       — MAIN DXF (주석/타이틀블록, xref 벽 없음 예상)
  renders/xr_plan_msp.png    — XR-PLAN DXF (벽·그리드 본체, A04.01~03 모든 층 포함)
  renders/supply_p62_400dpi.png — 공급 PDF page 62 (A04.03 = 지상2층+옥탑)

Outputs:
  renders/comparison_3panel.png — 세 이미지 나란히 (수동 검토용)
  08_compare.out.json — 기본 stats + 시각 비교를 위한 메타
"""
from __future__ import annotations
import json
from pathlib import Path

from PIL import Image

LAB = Path(__file__).parent
R = LAB / "renders"

panels = {
    "main_msp": R / "main_msp.png",
    "xr_plan_msp": R / "xr_plan_msp.png",
    "supply_p62": R / "supply_p62_400dpi.png",
}

info = {}
for name, p in panels.items():
    if not p.exists():
        info[name] = {"missing": True}
        continue
    im = Image.open(p)
    info[name] = {"size": im.size, "mode": im.mode, "file_kb": round(p.stat().st_size/1024, 1)}

# 3-panel 조합 (세로 방향)
target_w = 1200  # 최종 합성 이미지 너비
panels_images = []
for name, p in panels.items():
    if not p.exists(): continue
    im = Image.open(p).convert("RGB")
    ratio = target_w / im.width
    new_size = (target_w, int(im.height * ratio))
    im_resized = im.resize(new_size, Image.LANCZOS)
    panels_images.append((name, im_resized))

if panels_images:
    total_h = sum(im.height for _, im in panels_images) + 40 * len(panels_images)
    combo = Image.new("RGB", (target_w, total_h), (240, 240, 240))
    y = 0
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(combo)
    for name, im in panels_images:
        draw.text((10, y + 5), name, fill=(30, 30, 30))
        y += 40
        combo.paste(im, (0, y))
        y += im.height
    out_path = R / "comparison_3panel.png"
    combo.save(out_path, optimize=True)
    info["comparison_3panel"] = {"path": str(out_path.relative_to(LAB)), "size_kb": round(out_path.stat().st_size/1024, 1)}

(LAB / "08_compare.out.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
for k, v in info.items():
    print(f"  {k}: {v}")
