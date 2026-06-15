"""Phase C — step 1: DWG → DXF 변환 (ODA File Converter CLI).

- 입력: A04.01~03 확대평면도.dwg (3 layouts 예상: A04.01/A04.02/A04.03)
- 출력: parity-lab/p062/_dxf_out/*.dxf
- 근거: Phase B 에서 page 62 = A04.03 = 확대평면도-3 확정.

ODA CLI 인자: inputFolder outputFolder outputVersion outputFormat recurse audit [inputFilter]
"""
from __future__ import annotations
import json, shutil, subprocess, time
from pathlib import Path

LAB = Path(r"D:/_Project/prototype-도면지식관리-mvp/docs/ai-3d-builder/parity-lab/p062")
DWG_SRC = Path(r"D:/_Project/prototype-도면지식관리-mvp/dwg/1) 건축공사/1. 건축/1. 도면/A04.01~03 확대평면도.dwg")
DWG_IN = LAB / "_dwg_in"
DXF_OUT = LAB / "_dxf_out"
ODA = Path(r"C:/Program Files/ODA/ODAFileConverter 27.1.0/ODAFileConverter.exe")

DWG_IN.mkdir(exist_ok=True)
DXF_OUT.mkdir(exist_ok=True)

assert DWG_SRC.exists(), f"missing: {DWG_SRC}"
assert ODA.exists(), f"ODA not at: {ODA}"

dst = DWG_IN / DWG_SRC.name
if not dst.exists():
    shutil.copy2(DWG_SRC, dst)
    print(f"copied → {dst}")
else:
    print(f"exists → {dst}")

# ODA File Converter CLI
cmd = [
    str(ODA),
    str(DWG_IN),     # input folder
    str(DXF_OUT),    # output folder
    "ACAD2018",      # output version
    "DXF",           # output format
    "0",             # recurse subfolders (0=no)
    "1",             # audit (1=yes)
    "*.DWG",         # input filter
]
print("cmd:", " ".join(f'"{c}"' if " " in c else c for c in cmd))

t0 = time.time()
try:
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    elapsed = time.time() - t0
    print(f"rc={res.returncode}  elapsed={elapsed:.1f}s")
    if res.stdout:
        print("stdout:", res.stdout[:500])
    if res.stderr:
        print("stderr:", res.stderr[:500])
except subprocess.TimeoutExpired:
    elapsed = time.time() - t0
    print(f"TIMEOUT after {elapsed:.1f}s")

# 결과 확인
out = {"dwg_src": str(DWG_SRC), "dwg_copied_to": str(dst), "dxf_out_dir": str(DXF_OUT), "products": []}
for p in sorted(DXF_OUT.rglob("*")):
    if p.is_file():
        info = {"path": str(p.relative_to(DXF_OUT)), "size_kb": round(p.stat().st_size / 1024, 1)}
        out["products"].append(info)
        print(f"  product: {p.name} ({info['size_kb']} KB)")

(LAB / "02_convert_dwg.out.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
