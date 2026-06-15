"""ISS-3D-007: xref DXF 의 modelspace 엔티티를 MAIN DXF 의 동일 이름 BLOCK 에 주입.

배경:
- ODA 로 xref 동반 변환은 성공했으나, MAIN DXF 의 `blocks['XR-PLAN']` 등 xref
  블록은 **빈 참조** (entities=0). ezdxf 가 자동 resolve 하지 않음.
- 해결: `ezdxf.addons.importer.Importer.import_entities(src_msp, target_block)` 로
  xref DXF 의 msp 엔티티를 MAIN DXF 의 동일 이름 BLOCK 에 수동 주입.

산출물:
- `_dxf_out/A04.01~03 확대평면도_bound.dxf`  (바인딩된 MAIN DXF)
- `09_xref_bind.out.json`  (주입 결과 리포트)
"""
from __future__ import annotations
import json
import traceback
from pathlib import Path
from typing import Any

import ezdxf
from ezdxf.addons.importer import Importer

LAB = Path(__file__).parent
DXF_OUT = LAB / "_dxf_out"
MAIN = DXF_OUT / "A04.01~03 확대평면도.dxf"
XREF_DIR = DXF_OUT / "xref"
OUT_MAIN = DXF_OUT / "A04.01~03 확대평면도_bound.dxf"

# xref DXF 파일명 → MAIN blocks 에 등록된 BLOCK 이름 후보
# MAIN 의 실제 block 이름을 동적으로 조회해서 매칭함 (대소문자·확장자 차이 흡수)
XREF_FILES = [
    "XR-PLAN.dxf",
    "XR-SHEET.dxf",
    "XR-ELEV.dxf",
    "XR-SECTION.dxf",
    "XR-SPLAN.dxf",
    "XR-SSECTION.dxf",
    "XR-SITE PLAN.dxf",
    "XR-현황측량도.dxf",
    "XR-확대배치도.dxf",
    "xr-key.dxf",
]


def find_matching_block_name(main_doc, xref_stem: str) -> str | None:
    """MAIN 의 blocks 중에서 xref 파일 stem 과 매칭되는 블록 이름을 찾는다.

    AutoCAD 는 xref 블록을 파일명 기반으로 BLOCK 에 등록하나, 접두사·확장자
    포함 여부·대소문자가 변형될 수 있다. 가능한 후보:
      - exact: "XR-PLAN"
      - dollar sign: "XR-PLAN$0$SOMETHING"
      - 전체 파일명: "XR-PLAN.DWG"
      - 소문자 변형
    """
    target_variants = {
        xref_stem,
        xref_stem.upper(),
        xref_stem.lower(),
    }

    # blocks 이름 전체 iterate
    candidates = []
    for blk in main_doc.blocks:
        name = blk.name
        if name in target_variants:
            return name
        # dollar-sign 접두사 (XCLIP 복사본 등) 는 원본 찾을 때 제외
        if "$" in name:
            continue
        # case-insensitive 비교
        name_upper = name.upper()
        if name_upper == xref_stem.upper():
            return name
        # 파일명 일부 포함 케이스
        if xref_stem.upper() in name_upper and not name.startswith("*"):
            candidates.append(name)

    if candidates:
        # 가장 짧은 (정확한) 이름 우선
        return min(candidates, key=len)
    return None


def count_entities(layout) -> dict[str, int]:
    """layout 의 엔티티를 DXFTYPE 별로 집계."""
    counts: dict[str, int] = {}
    for entity in layout:
        t = entity.dxftype()
        counts[t] = counts.get(t, 0) + 1
    counts["_total"] = sum(v for k, v in counts.items() if not k.startswith("_"))
    return counts


def bind_xref_to_block(main_doc, xref_path: Path) -> dict[str, Any]:
    """xref_path 의 modelspace 엔티티를 MAIN 의 동일 이름 BLOCK 에 주입.

    Returns: 결과 딕셔너리 (status / block_name / before / after / error)
    """
    stem = xref_path.stem  # "XR-PLAN"
    result: dict[str, Any] = {
        "xref_file": xref_path.name,
        "xref_size_kb": round(xref_path.stat().st_size / 1024, 1),
    }

    block_name = find_matching_block_name(main_doc, stem)
    if block_name is None:
        result["status"] = "no_matching_block"
        return result

    result["block_name"] = block_name
    target_block = main_doc.blocks[block_name]

    # before: 현재 블록의 엔티티 수
    before = count_entities(target_block)
    result["before"] = before

    try:
        src_doc = ezdxf.readfile(xref_path)
    except Exception as e:
        result["status"] = "readfile_failed"
        result["error"] = f"{type(e).__name__}: {e}"
        return result

    src_msp = src_doc.modelspace()
    src_msp_counts = count_entities(src_msp)
    result["src_msp"] = src_msp_counts

    try:
        importer = Importer(src_doc, main_doc)
        # xref 의 msp 엔티티를 target block 에 주입
        importer.import_entities(list(src_msp), target_layout=target_block)
        # 리소스 (레이어·라인타입·스타일) 병합
        importer.finalize()
    except Exception as e:
        result["status"] = "import_failed"
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()
        return result

    after = count_entities(target_block)
    result["after"] = after
    result["added_total"] = after["_total"] - before["_total"]
    result["status"] = "ok" if result["added_total"] > 0 else "no_entities_added"
    return result


def main():
    report: dict[str, Any] = {
        "main_dxf": str(MAIN),
        "output_dxf": str(OUT_MAIN),
    }

    if not MAIN.exists():
        report["fatal"] = f"MAIN not found: {MAIN}"
        (LAB / "09_xref_bind.out.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("FATAL: MAIN DXF not found")
        return

    print(f"== loading MAIN: {MAIN.name} ==")
    main_doc = ezdxf.readfile(MAIN)

    # 사전: MAIN 의 모든 XR- 관련 block 이름 수집
    main_blocks = []
    for blk in main_doc.blocks:
        if "XR" in blk.name.upper() or blk.name.startswith("xr"):
            cnt = sum(1 for _ in blk)
            main_blocks.append({"name": blk.name, "entity_count": cnt})
    report["main_xr_blocks_before"] = main_blocks
    print(f"  MAIN has {len(main_blocks)} XR-related blocks")

    # 각 xref 주입
    results = []
    for xref_file in XREF_FILES:
        xref_path = XREF_DIR / xref_file
        if not xref_path.exists():
            results.append({"xref_file": xref_file, "status": "file_missing"})
            print(f"  SKIP (missing): {xref_file}")
            continue
        print(f"  binding: {xref_file}")
        r = bind_xref_to_block(main_doc, xref_path)
        results.append(r)
        print(
            f"    -> status={r.get('status')} "
            f"block={r.get('block_name')} "
            f"added={r.get('added_total')}"
        )

    report["results"] = results

    # 저장
    try:
        main_doc.saveas(OUT_MAIN)
        report["output_size_kb"] = round(OUT_MAIN.stat().st_size / 1024, 1)
        print(f"\n== saved: {OUT_MAIN.name} ({report['output_size_kb']} KB) ==")
    except Exception as e:
        report["save_error"] = f"{type(e).__name__}: {e}"
        report["save_traceback"] = traceback.format_exc()
        print(f"\nSAVE FAILED: {e}")

    # after 전체 스캔
    after_blocks = []
    try:
        bound_doc = ezdxf.readfile(OUT_MAIN) if OUT_MAIN.exists() else main_doc
        for blk in bound_doc.blocks:
            if "XR" in blk.name.upper() or blk.name.startswith("xr"):
                cnt = sum(1 for _ in blk)
                after_blocks.append({"name": blk.name, "entity_count": cnt})
    except Exception as e:
        report["rescan_error"] = f"{type(e).__name__}: {e}"
    report["main_xr_blocks_after"] = after_blocks

    (LAB / "09_xref_bind.out.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\nwrote 09_xref_bind.out.json")


if __name__ == "__main__":
    main()
