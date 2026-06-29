"""시트 비교 픽셀 diff (S4-c, §G).

같은 version_set의 두 버전 시트 PNG를 동일 해상도로 정규화한 뒤 픽셀 단위로
비교해 변경 영역 마스크 PNG를 만든다. 마스크는 변경 픽셀만 자홍색으로 칠하고
나머지는 투명해, 프론트가 현재 시트 위에 토글로 겹쳐 변경부를 강조할 수 있다.

클라이언트 색상 오버레이(이전=빨강/현재=파랑)와 별개의 백엔드 트랙이다.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# 그레이스케일 차이가 이 값을 넘으면 "변경"으로 본다(렌더 안티앨리어싱 노이즈 흡수).
_DIFF_THRESHOLD = 40
# 변경 픽셀 강조색(RGBA). 자홍색은 흑백 도면 위에서 잘 보인다.
_HILITE = (217, 35, 42, 200)


def compute_diff(png_a: str, png_b: str, out_path: str) -> dict:
    """두 PNG를 비교해 변경 마스크 PNG를 out_path에 저장. 변경 통계 dict 반환."""
    from PIL import Image, ImageChops

    with Image.open(png_a) as ia, Image.open(png_b) as ib:
        # 동일 캔버스로 정규화: B를 A 크기로 리샘플(버전 간 DPI/여백 차이 흡수).
        base = ia.convert("L")
        comp = ib.convert("L")
        if comp.size != base.size:
            comp = comp.resize(base.size, Image.BILINEAR)

        diff = ImageChops.difference(base, comp)
        # threshold → 1bit 마스크(변경=255).
        mask = diff.point(lambda p: 255 if p >= _DIFF_THRESHOLD else 0)
        bbox = mask.getbbox()  # 변경 영역 경계(없으면 None)

        width, height = base.size
        total = width * height
        # 변경 픽셀 수: 히스토그램의 255 빈.
        changed = mask.histogram()[255]

        # 변경 픽셀만 강조색, 나머지 투명한 RGBA 마스크 생성.
        out = Image.new("RGBA", base.size, (0, 0, 0, 0))
        solid = Image.new("RGBA", base.size, _HILITE)
        out.paste(solid, (0, 0), mask)
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        out.save(out_path)

    ratio = (changed / total) if total else 0.0
    return {
        "width": width,
        "height": height,
        "changed_pixels": changed,
        "total_pixels": total,
        "changed_ratio": round(ratio, 6),
        "changed_bbox": list(bbox) if bbox else None,
    }
