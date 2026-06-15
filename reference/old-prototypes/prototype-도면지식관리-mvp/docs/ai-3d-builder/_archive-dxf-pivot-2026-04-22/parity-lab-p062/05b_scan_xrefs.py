"""Phase C — step 4 (수정): Vec3 slicing 버그 + ATTRIB/block 재귀 추가."""
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

TARGETS = ["A04.01", "A04.02", "A04.03", "확대평면도-1", "확대평면도-2", "확대평면도-3",
           "지상2층", "옥탑", "지상1층", "PIT"]

def xy(vec):
    try:
        return (float(vec.x), float(vec.y))
    except Exception:
        try:
            return (float(vec[0]), float(vec[1]))
        except Exception:
            return None

def entity_text(ent):
    if ent.dxftype() == 'TEXT':
        return ent.dxf.text
    if ent.dxftype() == 'MTEXT':
        return ent.text
    return None

def scan_recursive(doc, container, container_label, hits):
    """TEXT/MTEXT + INSERT 의 ATTRIB + 블록 참조까지 재귀 검색."""
    for ent in container:
        et = ent.dxftype()
        if et in ('TEXT', 'MTEXT'):
            t = entity_text(ent)
            if not t: continue
            for tgt in TARGETS:
                if tgt in t:
                    pos = xy(ent.dxf.insert) if hasattr(ent.dxf, 'insert') else None
                    hits.append({
                        "target": tgt, "where": container_label, "dxftype": et,
                        "text": t[:80], "pos": pos, "layer": ent.dxf.layer
                    })
        elif et == 'INSERT':
            # ATTRIB 검사
            try:
                for attrib in ent.attribs:
                    at = attrib.dxf.text
                    for tgt in TARGETS:
                        if tgt in at:
                            pos = xy(ent.dxf.insert)
                            hits.append({
                                "target": tgt, "where": container_label, "dxftype": "ATTRIB",
                                "text": at[:80], "insert_pos": pos, "block_ref": ent.dxf.name,
                                "tag": attrib.dxf.tag,
                            })
            except Exception:
                pass

def scan_blocks(doc, label_prefix, hits):
    for blk in doc.blocks:
        if blk.name.startswith('*'):
            continue
        scan_recursive(doc, blk, f"{label_prefix}:block[{blk.name}]", hits)

out = {}

# --- MAIN: modelspace + 블록 재귀 + ATTRIB ---
print("== MAIN DXF ==")
main_doc = ezdxf.readfile(MAIN)
main_hits = []
scan_recursive(main_doc, main_doc.modelspace(), "MAIN:msp", main_hits)
scan_blocks(main_doc, "MAIN", main_hits)
print(f"  hits: {len(main_hits)}")
for h in main_hits[:30]:
    print(f"    {h}")
out["main_hits"] = main_hits

# INSERT 목록
inserts = []
for ent in main_doc.modelspace().query('INSERT'):
    inserts.append({
        "name": ent.dxf.name,
        "insert_xy": xy(ent.dxf.insert),
        "xscale": ent.dxf.xscale, "yscale": ent.dxf.yscale,
        "rotation": ent.dxf.rotation, "layer": ent.dxf.layer,
        "n_attribs": len(list(ent.attribs)),
    })
insert_name_counter = Counter(i["name"] for i in inserts)
xref_inserts = [i for i in inserts if i["name"].startswith("XR-") or i["name"].lower() == "xr-key"]
print(f"\n  INSERTs: {len(inserts)}; xref INSERTs: {len(xref_inserts)}")
print(f"  top names:")
for n, c in insert_name_counter.most_common(10):
    print(f"    {n!r:40s} {c}")
print(f"  xref insert positions:")
for i in xref_inserts:
    print(f"    {i}")
out["main_inserts"] = {"all": inserts, "xref_inserts": xref_inserts, "by_name": dict(insert_name_counter)}

# dwgtitle 블록 모든 INSERT 위치 (도면번호 오버레이 후보)
dwgtitle_inserts = [i for i in inserts if i["name"].lower() == "dwgtitle"]
print(f"\n  dwgtitle INSERTs: {len(dwgtitle_inserts)}")
for i in dwgtitle_inserts:
    print(f"    {i}")
out["dwgtitle_inserts"] = dwgtitle_inserts

# --- XR-SHEET 블록 재귀 검색 ---
print("\n== XR-SHEET.dxf ==")
sheet_doc = ezdxf.readfile(XR_SHEET)
sheet_hits = []
scan_recursive(sheet_doc, sheet_doc.modelspace(), "XR-SHEET:msp", sheet_hits)
scan_blocks(sheet_doc, "XR-SHEET", sheet_hits)
print(f"  hits: {len(sheet_hits)}")
for h in sheet_hits[:20]:
    print(f"    {h}")
out["xr_sheet_hits"] = sheet_hits

# --- XR-PLAN 기본 통계 + TEXT 검색 ---
print("\n== XR-PLAN.dxf ==")
plan_doc = ezdxf.readfile(XR_PLAN)
plan_msp = plan_doc.modelspace()
extmin = plan_doc.header.get('$EXTMIN', (0, 0, 0))
extmax = plan_doc.header.get('$EXTMAX', (0, 0, 0))
print(f"  EXTMIN: {tuple(extmin)[:2]}  EXTMAX: {tuple(extmax)[:2]}")
out["xr_plan_extents"] = {"extmin": list(tuple(extmin))[:2], "extmax": list(tuple(extmax))[:2]}

plan_type = Counter(); plan_layer = Counter()
n = 0
for ent in plan_msp:
    plan_type[ent.dxftype()] += 1
    plan_layer[ent.dxf.layer] += 1
    n += 1
print(f"  total msp entities: {n}")
print("  by type (top 10):")
for t, c in plan_type.most_common(10):
    print(f"    {t:12s} {c}")
print("  by layer (top 15):")
for l, c in plan_layer.most_common(15):
    print(f"    {l!r:40s} {c}")
out["xr_plan_stats"] = {"n": n, "by_type": dict(plan_type.most_common()), "by_layer_top30": dict(plan_layer.most_common(30))}

# XR-PLAN TEXT 검색 (해당 면적의 어느 부분이 지상2층인지)
plan_hits = []
scan_recursive(plan_doc, plan_msp, "XR-PLAN:msp", plan_hits)
print(f"\n  XR-PLAN msp TEXT hits: {len(plan_hits)}")
for h in plan_hits[:20]:
    print(f"    {h}")
out["xr_plan_hits"] = plan_hits

(LAB / "05b_scan_xrefs.out.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote 05b_scan_xrefs.out.json")
