"""Phase C — step 4: xref DXF 들의 실제 기하 + 메인의 INSERT 배치 파악.

목표:
  (a) XR-SHEET.dxf 에서 "A04.03" TEXT 위치 찾기 → 타이틀블록의 sheet 좌표
  (b) 메인 DXF 에서 XR-SHEET INSERT 의 삽입점 → 메인 좌표계의 A04.03 영역
  (c) XR-PLAN.dxf 의 modelspace 엔티티 타입/레이어 분포 → 벽·그리드 유무
  (d) 메인 DXF 에서 XR-PLAN INSERT 의 삽입점·스케일·회전 → 기하 변환 식
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

import ezdxf

LAB = Path(__file__).parent
DXF_OUT = LAB / "_dxf_out"
MAIN = DXF_OUT / "A04.01~03 확대평면도.dxf"
XR_SHEET = DXF_OUT / "xref" / "XR-SHEET.dxf"
XR_PLAN = DXF_OUT / "xref" / "XR-PLAN.dxf"

out = {}

def entity_text(ent):
    if ent.dxftype() == 'TEXT':
        return ent.dxf.text
    if ent.dxftype() == 'MTEXT':
        return ent.text
    return None

# --- (a) XR-SHEET 의 TEXT 인덱스 ---
print(f"== XR-SHEET.dxf ({XR_SHEET.stat().st_size/1024:.1f} KB) ==")
sheet_doc = ezdxf.readfile(XR_SHEET)
msp = sheet_doc.modelspace()
sheet_hits = []
targets = ["A04.01", "A04.02", "A04.03", "확대평면도-1", "확대평면도-2", "확대평면도-3"]
all_text_positions = []
for ent in msp:
    t = entity_text(ent)
    if not t:
        continue
    try:
        pos = tuple(float(x) for x in ent.dxf.insert[:2])
    except Exception:
        pos = None
    all_text_positions.append({"text": t[:80], "pos": pos, "layer": ent.dxf.layer})
    for target in targets:
        if target in t:
            sheet_hits.append({"target": target, "text": t[:80], "pos": pos, "layer": ent.dxf.layer})

print(f"  total TEXT/MTEXT: {len(all_text_positions)}")
print(f"  hits for sheet numbers:")
for h in sheet_hits:
    print(f"    [{h['target']}] pos={h['pos']} layer={h['layer']!r} text={h['text']!r}")

# 블록 내부도 탐색 (타이틀블록 TEXT는 블록 안에 있을 가능성 매우 큼)
print(f"\n  searching inside BLOCKS of XR-SHEET...")
block_hits = []
for blk in sheet_doc.blocks:
    if blk.name.startswith('*'):
        continue
    for ent in blk:
        t = entity_text(ent)
        if not t:
            continue
        for target in targets:
            if target in t:
                try:
                    pos = tuple(float(x) for x in ent.dxf.insert[:2])
                except Exception:
                    pos = None
                block_hits.append({"block": blk.name, "target": target, "text": t[:80], "pos_in_block": pos})
print(f"  block hits: {len(block_hits)}")
for h in block_hits[:20]:
    print(f"    [{h['target']}] block={h['block']!r} pos={h['pos_in_block']} text={h['text']!r}")

out["xr_sheet"] = {
    "total_text_entities_in_msp": len(all_text_positions),
    "msp_sheet_hits": sheet_hits,
    "block_sheet_hits": block_hits,
    "sample_text_positions_first20": all_text_positions[:20],
}

# --- (b) 메인 DXF 의 XR-SHEET INSERT 찾기 ---
print(f"\n== MAIN.dxf — INSERT 분석 ==")
main_doc = ezdxf.readfile(MAIN)
main_msp = main_doc.modelspace()
inserts = []
for ent in main_msp.query('INSERT'):
    inserts.append({
        "name": ent.dxf.name,
        "insert_xy": tuple(float(x) for x in ent.dxf.insert[:2]),
        "xscale": ent.dxf.xscale,
        "yscale": ent.dxf.yscale,
        "rotation": ent.dxf.rotation,
        "layer": ent.dxf.layer,
    })
insert_name_counter = Counter(i["name"] for i in inserts)
print(f"  INSERTs in modelspace: {len(inserts)}")
print(f"  top names:")
for n, c in insert_name_counter.most_common(15):
    print(f"    {n!r:40s} {c}")
xref_inserts = [i for i in inserts if i["name"].startswith("XR-") or i["name"] == "xr-key"]
print(f"  xref INSERTs: {len(xref_inserts)}")
for i in xref_inserts:
    print(f"    {i}")

out["main_inserts"] = {
    "total": len(inserts),
    "by_name": dict(insert_name_counter.most_common()),
    "xref_inserts": xref_inserts,
}

# --- (c) XR-PLAN modelspace 통계 ---
print(f"\n== XR-PLAN.dxf ({XR_PLAN.stat().st_size/1024/1024:.1f} MB) ==")
plan_doc = ezdxf.readfile(XR_PLAN)
plan_msp = plan_doc.modelspace()

# 범위 계산 (extmin/extmax)
try:
    extmin = plan_doc.header.get('$EXTMIN', (0, 0, 0))
    extmax = plan_doc.header.get('$EXTMAX', (0, 0, 0))
    print(f"  EXTMIN/EXTMAX: {extmin} → {extmax}")
    out["xr_plan_extents"] = {"extmin": list(extmin[:2]), "extmax": list(extmax[:2])}
except Exception as e:
    print(f"  extents error: {e}")

plan_type_counter = Counter()
plan_layer_counter = Counter()
n = 0
for ent in plan_msp:
    plan_type_counter[ent.dxftype()] += 1
    plan_layer_counter[ent.dxf.layer] += 1
    n += 1
    if n > 200000:
        break
print(f"  total entities scanned: {n}")
print(f"  by type (top 10):")
for t, c in plan_type_counter.most_common(10):
    print(f"    {t:12s} {c}")
print(f"  by layer (top 20):")
for l, c in plan_layer_counter.most_common(20):
    print(f"    {l!r:40s} {c}")

out["xr_plan"] = {
    "n_entities": n,
    "by_type_top10": dict(plan_type_counter.most_common(10)),
    "by_layer_top20": dict(plan_layer_counter.most_common(20)),
}

# --- (d) XR-PLAN 에서 "A04.03"·"지상2층"·"옥탑" 키워드 검색 ---
print(f"\n== XR-PLAN TEXT search ==")
plan_targets = ["A04.03", "지상2층", "지상 2층", "옥탑", "RF", "2FL", "확대평면도"]
plan_hits = {t: [] for t in plan_targets}
for ent in plan_msp:
    t = entity_text(ent)
    if not t:
        continue
    for target in plan_targets:
        if target in t:
            try:
                pos = tuple(float(x) for x in ent.dxf.insert[:2])
            except Exception:
                pos = None
            plan_hits[target].append({"text": t[:80], "pos": pos, "layer": ent.dxf.layer})
for tgt, lst in plan_hits.items():
    if lst:
        print(f"  '{tgt}': {len(lst)} hits")
        for h in lst[:3]:
            print(f"     {h}")
out["xr_plan_text_hits"] = plan_hits

(LAB / "05_scan_xrefs.out.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote {LAB / '05_scan_xrefs.out.json'}")
