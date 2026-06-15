"""
crop_subfigures.py — 시트 PNG에서 sub-figure 영역을 크롭.

수동 좌표 지정 (현재 p060 전용 하드코딩 + CLI 일반화).
사용:
  python crop_subfigures.py <image> <out_dir> --crop name x y w h [--crop ...]
"""
import argparse
from pathlib import Path
from PIL import Image


P060_PRESETS = [
    # (name, left, top, right, bottom)  -- pixel coords for 6617x4678
    ("p060_pit",    60,  100, 1450, 3050),
    ("p060_main", 1400,   80, 5520, 3950),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("out_dir")
    ap.add_argument("--preset", choices=["p060"], help="pre-defined crop set")
    ap.add_argument("--crop", action="append", nargs=5,
                    metavar=("NAME", "L", "T", "R", "B"),
                    help="custom crop bounds (left top right bottom in pixels)")
    args = ap.parse_args()

    img = Image.open(args.image)
    print(f"입력 이미지: {args.image}  size={img.size}")
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    crops = []
    if args.preset == "p060":
        crops.extend(P060_PRESETS)
    if args.crop:
        for name, l, t, r, b in args.crop:
            crops.append((name, int(l), int(t), int(r), int(b)))

    if not crops:
        print("크롭 좌표 없음. --preset p060 또는 --crop 사용", flush=True)
        return

    for name, l, t, r, b in crops:
        c = img.crop((l, t, r, b))
        out_path = out / f"{name}.png"
        c.save(out_path, "PNG")
        print(f"  {name}.png  ({r-l}x{b-t})  saved")


if __name__ == "__main__":
    main()
