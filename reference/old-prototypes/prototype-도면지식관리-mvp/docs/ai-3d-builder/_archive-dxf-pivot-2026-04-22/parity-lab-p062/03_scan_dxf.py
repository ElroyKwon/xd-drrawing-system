"""Phase C — step 2: DXF 열고 layout/layer/entity 스캔, A04.03 타이틀블록 찾기.

목표:
  1. layout 목록
  2. 레이어 사전 (이름·색·lineweight)
  3. 블록 참조 목록
  4. TEXT/MTEXT 엔티티에서 "A04.03" 검색 → 위치 좌표
  5. paper space layout 의 VIEWPORT 엔티티 조사 (Alignment 단서)
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

import ezdxf

LAB = Path(__file__).parent
DXF = LAB / "_dxf_out" / "A04.01~03 확대평면도.dxf"
assert DXF.exists(), DXF

doc = ezdxf.readfile(DXF)
print(f"DXF version: {doc.dxfversion}  encoding: {doc.encoding}")

out = {"dxf": str(DXF), "dxf_version": doc.dxfversion, "encoding": doc.encoding}

# layouts
layouts = []
for name in doc.layout_names():
    lo = doc.layout(name)
    layouts.append({
        "name": name,
        "is_modelspace": lo.is_modelspace if hasattr(lo, 'is_modelspace') else (name == 'Model'),
        "n_entities": len(list(lo)),
    })
out["layouts"] = layouts
print(f"\n== layouts ({len(layouts)}) ==")
for lo in layouts:
    tag = "MODEL" if lo["is_modelspace"] else "PAPER"
    print(f"  [{tag}] {lo['name']!r}: {lo['n_entities']} entities")

# layers
layer_list = []
for layer in doc.layers:
    layer_list.append({
        "name": layer.dxf.name,
        "color": layer.dxf.color,
        "linetype": layer.dxf.linetype,
        "lineweight": getattr(layer.dxf, 'lineweight', None),
        "is_off": layer.is_off(),
        "is_frozen": layer.is_frozen(),
    })
out["layers"] = {"count": len(layer_list), "list": layer_list}
print(f"\n== layers ({len(layer_list)}) ==")
for l in layer_list[:15]:
    print(f"  {l['name']!r:30s} color={l['color']}  off={l['is_off']}  freeze={l['is_frozen']}")
if len(layer_list) > 15:
    print(f"  ... and {len(layer_list) - 15} more")

# block definitions (xref 포함)
blocks_info = []
for blk in doc.blocks:
    n_ent = len(list(blk))
    is_xref = blk.block.dxf.flags & 4 != 0 if blk.block else False
    blocks_info.append({"name": blk.name, "n_entities": n_ent, "is_xref_like": is_xref})
out["blocks"] = {"count": len(blocks_info), "sample": blocks_info[:20]}
print(f"\n== blocks ({len(blocks_info)}) == (first 20)")
for b in blocks_info[:20]:
    print(f"  {b['name']!r:40s} ents={b['n_entities']}  xref?={b['is_xref_like']}")

# search "A04.03" in TEXT/MTEXT across all layouts
def text_of(ent):
    if ent.dxftype() == 'TEXT':
        return ent.dxf.text
    if ent.dxftype() == 'MTEXT':
        return ent.text
    return None

targets = ["A04.03", "A04.02", "A04.01", "확대평면도"]
hits = {t: [] for t in targets}
for lo_name in doc.layout_names():
    lo = doc.layout(lo_name)
    for ent in lo:
        t = text_of(ent)
        if not t:
            continue
        for target in targets:
            if target in t:
                # 위치
                pos = None
                try:
                    if ent.dxftype() == 'TEXT':
                        pos = tuple(ent.dxf.insert[:2])
                    elif ent.dxftype() == 'MTEXT':
                        pos = tuple(ent.dxf.insert[:2])
                except Exception:
                    pass
                hits[target].append({
                    "layout": lo_name,
                    "dxftype": ent.dxftype(),
                    "text_snip": t[:120],
                    "insert_xy": pos,
                    "layer": ent.dxf.layer,
                })
out["text_hits"] = hits
print(f"\n== text hits ==")
for t, lst in hits.items():
    print(f"  '{t}': {len(lst)} occurrences")
    for h in lst[:5]:
        print(f"     layout={h['layout']!r} layer={h['layer']!r} pos={h['insert_xy']}  snip={h['text_snip']!r}")

# VIEWPORT in paper-space layouts
vp_info = []
for lo_name in doc.layout_names():
    lo = doc.layout(lo_name)
    if lo.is_modelspace if hasattr(lo, 'is_modelspace') else (lo_name == 'Model'):
        continue
    for ent in lo.query('VIEWPORT'):
        try:
            vp_info.append({
                "layout": lo_name,
                "center_xy_paper": tuple(ent.dxf.center[:2]),
                "width_paper": ent.dxf.width,
                "height_paper": ent.dxf.height,
                "view_center_model_xy": tuple(ent.dxf.view_center_point[:2]) if hasattr(ent.dxf, 'view_center_point') else None,
                "view_height_model": getattr(ent.dxf, 'view_height', None),
                "status": getattr(ent.dxf, 'status', None),
            })
        except Exception as e:
            vp_info.append({"layout": lo_name, "error": str(e)})
out["viewports"] = vp_info
print(f"\n== viewports ({len(vp_info)}) ==")
for v in vp_info:
    print(f"  {v}")

# entity type distribution (MODEL space only — 기하 위치)
msp = doc.modelspace()
type_counter = Counter(e.dxftype() for e in msp)
layer_counter = Counter(e.dxf.layer for e in msp)
out["modelspace_stats"] = {
    "n_entities": sum(type_counter.values()),
    "by_type": dict(type_counter.most_common()),
    "by_layer_top20": dict(layer_counter.most_common(20)),
}
print(f"\n== modelspace entity types ==")
for t, c in type_counter.most_common(15):
    print(f"  {t:12s} {c}")
print(f"\n== modelspace top layers ==")
for l, c in layer_counter.most_common(15):
    print(f"  {l!r:40s} {c}")

(LAB / "03_scan_dxf.out.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nwrote {LAB / '03_scan_dxf.out.json'}")
