"""Paper space layout 탐사 — AutoCAD plot 과 동등한 경로 여부 확인.

가설: MAIN DXF 의 평면 기하는 modelspace 에 XCLIP + 음의 y 위치로 배치돼 있고,
paper space layout 의 viewport 가 sheet 영역에 투영하여 plot 됨. 즉 **paper space
를 렌더해야 공급 PDF 와 같은 결과**가 나올 것.
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

import ezdxf

LAB = Path(__file__).parent
DXF_OUT = LAB / "_dxf_out"
MAIN_BOUND = DXF_OUT / "A04.01~03 확대평면도_bound.dxf"


def main():
    doc = ezdxf.readfile(MAIN_BOUND)
    report = {}

    # 모든 layout 나열
    layout_names = doc.layouts.names()
    report["layout_names"] = list(layout_names)

    layouts_info = {}
    for name in layout_names:
        layout = doc.layouts.get(name)
        is_modelspace = name == "Model"
        counts = defaultdict(int)
        viewports = []
        for e in layout:
            counts[e.dxftype()] += 1
            if e.dxftype() == "VIEWPORT":
                try:
                    vp = {
                        "center": (float(e.dxf.center.x), float(e.dxf.center.y)),
                        "width": float(e.dxf.width),
                        "height": float(e.dxf.height),
                    }
                    if e.dxf.hasattr("view_target_point"):
                        tp = e.dxf.view_target_point
                        vp["view_target"] = (float(tp.x), float(tp.y), float(tp.z))
                    if e.dxf.hasattr("view_direction_vector"):
                        vd = e.dxf.view_direction_vector
                        vp["view_direction"] = (float(vd.x), float(vd.y), float(vd.z))
                    if e.dxf.hasattr("view_height"):
                        vp["view_height"] = float(e.dxf.view_height)
                    if e.dxf.hasattr("view_center_point"):
                        vc = e.dxf.view_center_point
                        vp["view_center"] = (float(vc.x), float(vc.y))
                    viewports.append(vp)
                except Exception as ex:
                    viewports.append({"error": str(ex)})
        layouts_info[name] = {
            "is_modelspace": is_modelspace,
            "entity_counts": dict(counts),
            "total": sum(counts.values()),
            "viewports": viewports,
        }

    report["layouts"] = layouts_info

    (LAB / "13_probe_paperspace.out.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("wrote 13_probe_paperspace.out.json")
    print(f"\nlayouts: {layout_names}")
    for name, info in layouts_info.items():
        print(f"\n[{name}] total={info['total']}, types={info['entity_counts']}")
        if info["viewports"]:
            for i, vp in enumerate(info["viewports"]):
                print(f"  VP#{i}: {vp}")


if __name__ == "__main__":
    main()
