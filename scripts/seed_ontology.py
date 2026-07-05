"""S10 온톨로지 큐레이트 시드 — LS 청주사업장 전기계통 대표 장비를 TypeDB에 적재·바인딩.

정직 표기: 이 장비들은 **AI 자동추출이 아니라 큐레이트 시드**(온톨로지 구조·시트 바인딩·
AI 그라운딩 실증용). 실제 청주 전기도면(EE-01 단선결선도/분전반 결선도)의 계통을 반영해
큐레이트했다. 각 장비는 실제로 그 장비가 나타나는 EE 도면번호(시트)에 appears_on으로 바인딩.

멱등: 프로젝트 equipment 전량 삭제 후 재적재. 런타임에 8000 store에서 실제 시트를
조회해 EE 번호로 매칭하므로 sheet_id 하드코딩 없음.

사용: XD_ONTOLOGY_DIRECT_TYPEDB=1 backend/.venv/Scripts/python.exe scripts/seed_ontology.py
"""
import os
import sys
from pathlib import Path

# 시드는 TypeDB 권위에 직접 쓴다(서버는 미러 읽기라 이 플래그 없음).
os.environ["XD_ONTOLOGY_DIRECT_TYPEDB"] = "1"
os.environ.setdefault("XD_STORE", "typedb")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from store import get_store  # noqa: E402
from ontology import get_ontology  # noqa: E402

PROJECT = "LS 청주사업장"


# 청주 전기계통 대표 장비(큐레이트). (equipment_id, tag, name, type, status, [EE 도면번호…])
# EE 번호는 그 장비가 실제로 표기되는 단선결선도/결선도 시트.
EQUIPMENT = [
    # ── 22.9kV 수전설비 (U#T동 주변전실: EE-01-001, 002) ──
    ("EQ-INC-229", "INC-22.9kV", "22.9kV 특고압 수전 인입", "incomer", "ACTIVE",
     ["EE-00-003", "EE-01-001"]),
    ("EQ-VCB-229", "VCB-22.9kV", "22.9kV 수전 진공차단기", "breaker", "ACTIVE",
     ["EE-01-001", "EE-01-002"]),
    ("EQ-MTR-229", "MTR-1", "주변압기 22.9kV/6.6kV", "transformer", "ACTIVE",
     ["EE-01-001", "EE-01-002"]),
    # ── 6.6kV 변전설비 (A동/R-Center 변전실: EE-01-003~006) ──
    ("EQ-VCB-66", "VCB-6.6kV", "6.6kV 진공차단기", "breaker", "ACTIVE",
     ["EE-01-003", "EE-01-004", "EE-01-005", "EE-01-006"]),
    ("EQ-TR-A", "TR-A1", "6.6kV/380V 변압기 (A동 지하1층)", "transformer", "ACTIVE",
     ["EE-01-004", "EE-01-005"]),
    ("EQ-TR-R", "TR-R1", "6.6kV/380V 변압기 (R-Center 변전실)", "transformer", "ACTIVE",
     ["EE-01-006"]),
    ("EQ-TR-INV", "TR-INV", "6.6kV 변압기 (인버터 시험센터)", "transformer", "STANDBY",
     ["EE-01-003"]),
    ("EQ-ACB-LV", "ACB-LV", "저압 기중차단기 (ACB)", "breaker", "ACTIVE",
     ["EE-01-004", "EE-01-005", "EE-01-006"]),
    ("EQ-LV-PNL", "LV-MAIN", "저압 주배전반 (380V)", "panel", "ACTIVE",
     ["EE-01-004", "EE-01-005", "EE-01-006"]),
    # ── 동력/생산동력 분전반 (EE-01-012~019) ──
    ("EQ-PNL-PWR", "PP-M", "동력 주분전반", "panel", "ACTIVE",
     ["EE-01-012", "EE-01-013"]),
    ("EQ-PNL-220", "PP-220V", "생산동력 분전반 (3Ø 220V)", "panel", "ACTIVE",
     ["EE-01-014", "EE-01-015"]),
    ("EQ-PNL-380", "PP-380V", "생산동력 분전반 (3Ø 380V)", "panel", "ACTIVE",
     ["EE-01-016", "EE-01-016-1"]),
    ("EQ-PNL-440", "PP-440V", "생산동력 분전반 (3Ø 440V)", "panel", "ACTIVE",
     ["EE-01-017", "EE-01-018", "EE-01-019"]),
    # ── 간선 케이블 ──
    ("EQ-CBL-229", "CBL-22.9kV", "22.9kV 인입 간선 케이블", "cable", "ACTIVE",
     ["EE-00-003", "EE-01-001"]),
    ("EQ-CBL-66", "CBL-6.6kV", "6.6kV 배전 간선 케이블", "cable", "ACTIVE",
     ["EE-01-007", "EE-01-008"]),
]


def _sheet_index(project: str) -> dict:
    """EE 도면번호(파일명 prefix) → 첫 시트 sheet_id 맵. 실제 store 조회."""
    store = get_store()
    drawings = store.list_drawings(project)
    idx = {}
    for f in drawings:
        fn = f.get("filename", "")
        sheets = f.get("sheets") or []
        if not sheets:
            continue
        sid = sheets[0].get("sheet_id")
        # 파일명은 'EE-01-016-1_...' / 'EE-01-016_...' 형태 → prefix로 매칭.
        for code in ("EE-01-016-1", "EE-01-016") + tuple(f"EE-{a:02d}-{b:03d}" for a in range(0, 6) for b in range(1, 25)):
            if fn.startswith(code + "_") or fn.startswith(code + " "):
                idx.setdefault(code, sid)
                break
    return idx


def main():
    ont = get_ontology()
    print(f"ontology backend = {ont.backend}")
    if ont.backend != "typedb":
        print("!! TypeDB 직접연결 실패 — XD_ONTOLOGY_DIRECT_TYPEDB=1 + 컨테이너 확인")
    idx = _sheet_index(PROJECT)
    print(f"시트 인덱스: {len(idx)}개 EE 도면 매칭")

    removed = ont.clear_project(PROJECT)
    print(f"기존 equipment {removed}건 삭제(멱등)")

    n, bound = 0, 0
    missing = set()
    for eid, tag, name, typ, status, codes in EQUIPMENT:
        sheet_ids = []
        for c in codes:
            sid = idx.get(c)
            if sid:
                sheet_ids.append(sid)
            else:
                missing.add(c)
        ont.add_equipment(PROJECT, {
            "equipment_id": eid, "tag": tag, "name": name,
            "type": typ, "status": status, "discipline": "E",
        }, sheet_ids)
        n += 1
        bound += len(sheet_ids)
    print(f"큐레이트 장비 {n}건 적재 · appears_on 바인딩 {bound}건")
    if missing:
        print(f"  (주의: 매칭 실패 EE 번호 {sorted(missing)})")

    got = ont.list_equipment(PROJECT)
    print(f"검증: list_equipment({PROJECT}) = {len(got)}건")
    for e in got[:5]:
        print(f"  {e['tag']:12} {e['name']:34} → 시트 {len(e['sheet_ids'])}개")


if __name__ == "__main__":
    main()
