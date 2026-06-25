"""S2 시트 메타 휴리스틱 회귀: 번호/제목/공종 추출 + 폴백 + PDF 페이지 분할 메타."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/

import ezdxf  # noqa: E402

import sheet_meta as sm  # noqa: E402
from conversion import render_dxf_sheets, render_pdf_sheets  # noqa: E402


def test_filename_matches_page_high_confidence():
    # 페이지 텍스트의 번호가 파일명 접두와 일치 → filename+page(고신뢰), 공종 E
    m = sm.extract_sheet_meta("...\nEE-01-006\n변전실 단선결선도\n", "EE-01-006_변전설비.pdf", 0)
    assert m["number"] == "EE-01-006"
    assert m["discipline_code"] == "E"
    assert m["meta_source"] == "filename+page"


def test_title_block_label_extraction():
    m = sm.extract_sheet_meta("DWG. NO\nE-205\nsomething", "scan.pdf", 3)
    assert m["number"] == "E-205"
    assert m["meta_source"] == "title-block"
    assert m["discipline_code"] == "E"


def test_label_prefers_real_drawing_number_over_equipment_tag():
    """라벨 근처에 장비태그(TR-005)와 진짜 도면번호(M-201)가 함께 있으면 도면번호를 채택."""
    m = sm.extract_sheet_meta("SHEET NO\nTR-005\nM-201", "bundle.pdf", 2)
    assert m["number"] == "M-201"
    assert m["discipline_code"] == "M"
    assert m["meta_source"] == "title-block"


def test_filename_fallback_when_no_page_number():
    m = sm.extract_sheet_meta("그림만 있고 번호 텍스트 없음", "M-310_HVAC.pdf", 1)
    assert m["number"] == "M-310"
    assert m["discipline_code"] == "M"
    assert m["meta_source"] == "filename"


def test_page_index_fallback_and_discipline_not_misclassified():
    # 번호 없음 + 파일명도 번호 없음 → Page N, 공종은 '기타'('Page'를 P로 오분류 금지)
    m = sm.extract_sheet_meta("도면 텍스트", "전기도면_묶음.pdf", 4)
    assert m["number"] == "Page 5"
    assert m["discipline_code"] == "G"
    assert m["meta_source"] == "page-index"


def test_discipline_mapping():
    assert sm._discipline("A101")[0] == "A"
    assert sm._discipline("S-201")[0] == "S"
    assert sm._discipline("P-12")[0] == "P"
    assert sm._discipline("ZZ-99")[0] == "G"


def test_pdf_split_attaches_meta(tmp_path):
    import fitz

    pdf = tmp_path / "EE-01-006_test.pdf"
    doc = fitz.open()
    for n in range(2):
        page = doc.new_page()
        page.insert_text((72, 72), f"EE-01-006 page {n}")
    doc.save(str(pdf))
    doc.close()

    sheets, scan = render_pdf_sheets(str(pdf), "fid", str(tmp_path), filename="EE-01-006_test.pdf", dpi=72)
    assert scan["pages"] == 2
    assert len(sheets) == 2
    assert all(s.source == "pdf-page" for s in sheets)
    # 메타가 시트에 붙어야 한다
    assert sheets[0].sheet_number == "EE-01-006"
    assert sheets[0].discipline_code == "E"
    assert sheets[0].sheet_title  # 비어있지 않음


def test_multi_paperspace_splits_into_sheets(tmp_path):
    """C5: 다중 paperspace 레이아웃 → 다중 시트 분리(viewport/엔티티 있는 레이아웃)."""
    doc = ezdxf.new("R2018")
    doc.modelspace().add_line((0, 0), (10, 10))
    doc.layout("Layout1").add_line((0, 0), (100, 0))
    doc.layouts.new("Layout2").add_circle((50, 50), 25)
    dxf = str(tmp_path / "multi.dxf")
    doc.saveas(dxf)

    sheets, scan = render_dxf_sheets(dxf, "fid", str(tmp_path), filename="S-201_구조도.dwg")
    assert len(sheets) == 2
    assert {s.sheet_name for s in sheets} == {"Layout1", "Layout2"}
    assert all(s.source == "paperspace" for s in sheets)
    assert all(s.discipline_code == "S" for s in sheets)  # 파일명 S-201 → 구조


def test_empty_paperspace_falls_back_to_modelspace(tmp_path):
    """빈 paperspace DWG는 modelspace 단일 시트(한계 — 자동분할 범위 밖)."""
    doc = ezdxf.new("R2018")
    doc.modelspace().add_line((0, 0), (50, 50))
    dxf = str(tmp_path / "msp_only.dxf")
    doc.saveas(dxf)

    sheets, scan = render_dxf_sheets(dxf, "fid", str(tmp_path), filename="A-100.dwg")
    assert len(sheets) == 1
    assert sheets[0].source == "modelspace"
