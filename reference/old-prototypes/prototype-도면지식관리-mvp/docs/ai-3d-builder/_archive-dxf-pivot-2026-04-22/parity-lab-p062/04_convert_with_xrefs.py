"""Phase C — step 3 (재시도): xref 폴더 포함 변환.

1차 변환(02_convert_dwg.py) 실패 원인:
- 메인 DXF 의 XR-PLAN·XR-SHEET 등 xref 블록이 empty (xref DWG 미동반)
- modelspace 에 LINE 10 개, XR-PLAN|* 레이어 39 개만 이름으로 존재
- 즉 벽·그리드·타이틀블록이 전부 xref 내부 → 해결 없이는 파리티 불가

대응:
- xref 폴더 전체를 _dwg_in/xref/ 로 복사 (원본 구조 유지)
- ODA recurse=1 로 재변환 → _dxf_out/ 및 _dxf_out/xref/ 양쪽에 DXF 생성
"""
from __future__ import annotations
import json, shutil, subprocess, time
from pathlib import Path

LAB = Path(__file__).parent
SRC_DIR = Path(r"D:/_Project/prototype-도면지식관리-mvp/dwg/1) 건축공사/1. 건축/1. 도면")
DWG_MAIN = SRC_DIR / "A04.01~03 확대평면도.dwg"
XREF_DIR = SRC_DIR / "xref"
DWG_IN = LAB / "_dwg_in"
DXF_OUT = LAB / "_dxf_out"
ODA = Path(r"C:/Program Files/ODA/ODAFileConverter 27.1.0/ODAFileConverter.exe")

# 기존 출력 정리 (재실행 안전)
if DXF_OUT.exists():
    shutil.rmtree(DXF_OUT)
DXF_OUT.mkdir(parents=True)
DWG_IN.mkdir(exist_ok=True)

# xref 폴더 복사 (Thumbs.db·desktop.ini 제외)
dst_xref = DWG_IN / "xref"
if dst_xref.exists():
    shutil.rmtree(dst_xref)
dst_xref.mkdir()
copied = []
for src in XREF_DIR.iterdir():
    if src.suffix.lower() == ".dwg":
        dst = dst_xref / src.name
        shutil.copy2(src, dst)
        copied.append(src.name)
print(f"copied {len(copied)} xref DWGs → {dst_xref}")

# 메인 DWG 재복사 (이미 있어도 overwrite)
main_dst = DWG_IN / DWG_MAIN.name
shutil.copy2(DWG_MAIN, main_dst)
print(f"copied main → {main_dst}")

# ODA 재변환 — recurse=1
cmd = [str(ODA), str(DWG_IN), str(DXF_OUT), "ACAD2018", "DXF", "1", "1", "*.DWG"]
print("cmd:", " ".join(f'"{c}"' if " " in c else c for c in cmd))

t0 = time.time()
res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
elapsed = time.time() - t0
print(f"rc={res.returncode} elapsed={elapsed:.1f}s")

out = {"products": []}
for p in sorted(DXF_OUT.rglob("*.dxf")):
    rel = p.relative_to(DXF_OUT)
    size = p.stat().st_size / 1024
    out["products"].append({"path": str(rel), "size_kb": round(size, 1)})
    print(f"  {rel}  ({size:.1f} KB)")

(LAB / "04_convert_with_xrefs.out.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
