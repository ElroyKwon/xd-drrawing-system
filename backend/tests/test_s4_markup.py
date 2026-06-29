"""S4: 마크업/측정 영속 CRUD + 단위 추출 + 비교 픽셀 diff 회귀."""
import asyncio
import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/

import config  # noqa: E402


def _fresh_store(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "UPLOADS_DIR", tmp_path)
    import store as store_mod
    importlib.reload(store_mod)
    return store_mod, store_mod.JsonDrawingStore()


def _png(path, size, color):
    from PIL import Image
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(str(path))
    return str(path)


def _drawing_with_sheet(tmp_path, file_id, sheet_id, png_color=(255, 255, 255),
                        size=(64, 64), vset=None, vno=1):
    png = _png(tmp_path / "P" / file_id / "sheets" / f"{sheet_id}.png", size, png_color)
    return {
        "file_id": file_id,
        "filename": f"{file_id}.dwg",
        "file_path": str(tmp_path / "P" / file_id / "original.dwg"),
        "file_format": "dwg",
        "file_size": 10,
        "upload_date": f"2026-06-29T00:00:0{vno}",
        "project_name": "P",
        "version": str(vno),
        "version_set_id": vset or file_id,
        "version_no": vno,
        "is_latest": True,
        "conversion_status": "completed",
        "sheets": [{"sheet_id": sheet_id, "sheet_name": "S", "sheet_index": 0, "png_path": png}],
    }


# --- store: 마크업 CRUD + 스코프 ---

def test_markup_crud_and_scope(tmp_path, monkeypatch):
    _, s = _fresh_store(tmp_path, monkeypatch)
    s.add_markup({"markup_id": "m1", "file_id": "F", "sheet_id": "S1", "kind": "도형",
                  "coord_space": "world", "geometry": [[0, 0], [10, 10]], "style": {},
                  "text": "", "created_at": "2026-06-29T00:00:01"})
    s.add_markup({"markup_id": "m2", "file_id": "F", "sheet_id": "S2", "kind": "텍스트",
                  "coord_space": "world", "geometry": [[1, 1]], "style": {},
                  "text": "패널 확인", "created_at": "2026-06-29T00:00:02"})
    # 스코프: (file_id, sheet_id)로만 조회
    assert [m["markup_id"] for m in s.list_markups("F", "S1")] == ["m1"]
    assert [m["markup_id"] for m in s.list_markups("F", "S2")] == ["m2"]
    assert s.list_markups("F", "S3") == []
    # update: 허용 필드만, 스코프 키 불변
    updated = s.update_markup("m1", geometry=[[0, 0], [20, 20]], text="수정", file_id="HACK")
    assert updated["geometry"] == [[0, 0], [20, 20]]
    assert updated["text"] == "수정"
    assert updated["file_id"] == "F"  # 스코프 키는 갱신되지 않음
    assert s.update_markup("ghost", text="x") is None
    # delete
    assert s.delete_markup("m1") is True
    assert s.list_markups("F", "S1") == []
    assert s.delete_markup("m1") is False


def test_measurement_crud_and_scope(tmp_path, monkeypatch):
    _, s = _fresh_store(tmp_path, monkeypatch)
    s.add_measurement({"measurement_id": "ms1", "file_id": "F", "sheet_id": "S1", "type": "선형",
                       "geometry": [[0, 0], [3000, 0]], "value": 3.0, "unit": "m",
                       "created_at": "2026-06-29T00:00:01"})
    s.add_measurement({"measurement_id": "ms2", "file_id": "F", "sheet_id": "S2", "type": "다각형 면적",
                       "geometry": [[0, 0], [10, 0], [10, 10]], "value": 50.0, "unit": "㎡",
                       "created_at": "2026-06-29T00:00:02"})
    assert [m["measurement_id"] for m in s.list_measurements("F", "S1")] == ["ms1"]
    assert s.list_measurements("F", "S2")[0]["value"] == 50.0
    assert s.delete_measurement("ms1") is True
    assert s.list_measurements("F", "S1") == []
    assert s.delete_measurement("ms1") is False


def test_markup_measurement_index_isolated(tmp_path, monkeypatch):
    """마크업/측정 인덱스는 도면 인덱스(_index.json)와 분리돼 서로 오염되지 않는다."""
    store_mod, s = _fresh_store(tmp_path, monkeypatch)
    s.add_markup({"markup_id": "m1", "file_id": "F", "sheet_id": "S", "kind": "펜",
                  "coord_space": "world", "geometry": [[0, 0]], "style": {}, "text": "",
                  "created_at": "t"})
    # 도면 인덱스는 비어 있어야 한다
    assert s.list_drawings("P") == []
    assert (tmp_path / "_markups.json").exists()


# --- routes: 마크업 검증 ---

def _reload_routes(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "UPLOADS_DIR", tmp_path)
    monkeypatch.setattr(config, "STORE_BACKEND", "json")
    import store as store_mod
    importlib.reload(store_mod)
    import routes_drawing
    importlib.reload(routes_drawing)
    import routes_markup as rm
    importlib.reload(rm)
    return rm


def test_markup_route_create_list_patch_delete(tmp_path, monkeypatch):
    rm = _reload_routes(tmp_path, monkeypatch)
    s = rm.get_store()
    s.add_drawing(_drawing_with_sheet(tmp_path, "F", "F_sheet_001"))
    # 생성
    created = asyncio.run(rm.create_markup("F", rm.MarkupCreate(
        sheet_id="F_sheet_001", kind="클라우드", coord_space="world",
        geometry=[[10, 10], [50, 30]], style={"color": "#e8590c", "width": 2}, text="배선 경로 확인")))
    mid = created["markup_id"]
    assert created["author"] == "사용자"
    # 목록
    rows = asyncio.run(rm.list_markups("F", "F_sheet_001"))
    assert [r["markup_id"] for r in rows] == [mid]
    # 수정
    patched = asyncio.run(rm.patch_markup("F", mid, rm.MarkupPatch(text="배선 경로 확인 후 CAD 수정 요청")))
    assert patched["text"].endswith("CAD 수정 요청")
    # 삭제
    assert asyncio.run(rm.delete_markup("F", mid))["deleted"] == mid
    assert asyncio.run(rm.list_markups("F", "F_sheet_001")) == []


def test_markup_route_validation(tmp_path, monkeypatch):
    rm = _reload_routes(tmp_path, monkeypatch)
    from fastapi import HTTPException
    s = rm.get_store()
    s.add_drawing(_drawing_with_sheet(tmp_path, "F", "F_sheet_001"))
    # 없는 도면 → 404
    with pytest.raises(HTTPException) as e1:
        asyncio.run(rm.create_markup("ghost", rm.MarkupCreate(sheet_id="x", kind="도형", geometry=[[0, 0]])))
    assert e1.value.status_code == 404
    # 없는 시트 → 404
    with pytest.raises(HTTPException) as e2:
        asyncio.run(rm.create_markup("F", rm.MarkupCreate(sheet_id="nope", kind="도형", geometry=[[0, 0]])))
    assert e2.value.status_code == 404
    # 알 수 없는 종류 → 400
    with pytest.raises(HTTPException) as e3:
        asyncio.run(rm.create_markup("F", rm.MarkupCreate(sheet_id="F_sheet_001", kind="UFO", geometry=[[0, 0]])))
    assert e3.value.status_code == 400
    # 빈 geometry → 400
    with pytest.raises(HTTPException) as e4:
        asyncio.run(rm.create_markup("F", rm.MarkupCreate(sheet_id="F_sheet_001", kind="도형", geometry=[])))
    assert e4.value.status_code == 400
    # 잘못된 coord_space → 400
    with pytest.raises(HTTPException) as e5:
        asyncio.run(rm.create_markup("F", rm.MarkupCreate(
            sheet_id="F_sheet_001", kind="도형", coord_space="moon", geometry=[[0, 0]])))
    assert e5.value.status_code == 400
    # 없는 마크업 patch/delete → 404
    with pytest.raises(HTTPException) as e6:
        asyncio.run(rm.patch_markup("F", "ghost", rm.MarkupPatch(text="x")))
    assert e6.value.status_code == 404


def test_measurement_route_create_and_validation(tmp_path, monkeypatch):
    rm = _reload_routes(tmp_path, monkeypatch)
    from fastapi import HTTPException
    s = rm.get_store()
    s.add_drawing(_drawing_with_sheet(tmp_path, "F", "F_sheet_001"))
    created = asyncio.run(rm.create_measurement("F", rm.MeasurementCreate(
        sheet_id="F_sheet_001", type="선형", geometry=[[0, 0], [3000, 0]], value=3.0, unit="m")))
    assert created["value"] == 3.0
    assert asyncio.run(rm.list_measurements("F", "F_sheet_001"))[0]["measurement_id"] == created["measurement_id"]
    # 알 수 없는 측정 종류 → 400
    with pytest.raises(HTTPException) as e1:
        asyncio.run(rm.create_measurement("F", rm.MeasurementCreate(
            sheet_id="F_sheet_001", type="부피", geometry=[[0, 0], [1, 1]], value=1)))
    assert e1.value.status_code == 400
    # 삭제
    assert asyncio.run(rm.delete_measurement("F", created["measurement_id"]))["deleted"]


# --- compute_diff (PIL) ---

def test_compute_diff_identical_and_changed(tmp_path):
    import compare
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    out = tmp_path / "mask.png"
    _png(a, (40, 40), (255, 255, 255))
    _png(b, (40, 40), (255, 255, 255))
    same = compare.compute_diff(str(a), str(b), str(out))
    assert same["changed_pixels"] == 0
    assert same["changed_ratio"] == 0.0
    assert same["changed_bbox"] is None
    assert out.exists()
    # 절반을 검게: 변경 픽셀이 절반가량
    from PIL import Image
    img = Image.new("RGB", (40, 40), (255, 255, 255))
    for y in range(40):
        for x in range(20):
            img.putpixel((x, y), (0, 0, 0))
    img.save(str(b))
    diff = compare.compute_diff(str(a), str(b), str(out))
    assert diff["changed_pixels"] == 20 * 40
    assert 0.49 < diff["changed_ratio"] < 0.51
    assert diff["changed_bbox"] is not None


def test_compute_diff_resizes_mismatched(tmp_path):
    """버전 간 해상도가 달라도 B를 A 크기로 정규화해 비교한다."""
    import compare
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    _png(a, (60, 60), (255, 255, 255))
    _png(b, (30, 30), (255, 255, 255))  # 다른 해상도, 같은 색
    res = compare.compute_diff(str(a), str(b), str(tmp_path / "m.png"))
    assert res["width"] == 60 and res["height"] == 60
    assert res["changed_pixels"] == 0  # 리샘플 후 동일색 → 변경 0


# --- compare 라우트 ---

def test_compare_route_same_versionset(tmp_path, monkeypatch):
    rm = _reload_routes(tmp_path, monkeypatch)
    s = rm.get_store()
    s.add_drawing(_drawing_with_sheet(tmp_path, "v1", "v1_s", png_color=(255, 255, 255), vset="setZ", vno=1))
    s.add_version("setZ", _drawing_with_sheet(tmp_path, "v2", "v2_s", png_color=(0, 0, 0), vset="setZ", vno=2))
    res = asyncio.run(rm.compare_versions("v1", against="v2"))
    assert res["changed_ratio"] > 0.9  # 흰 vs 검 → 거의 전부 변경
    assert res["mask_url"] and res["mask_url"].startswith("/files/")
    assert res["png_a_url"] and res["png_b_url"]


def test_compare_route_rejects_cross_versionset_and_missing(tmp_path, monkeypatch):
    rm = _reload_routes(tmp_path, monkeypatch)
    from fastapi import HTTPException
    s = rm.get_store()
    s.add_drawing(_drawing_with_sheet(tmp_path, "a", "a_s", vset="setA"))
    s.add_drawing(_drawing_with_sheet(tmp_path, "b", "b_s", vset="setB"))
    # 다른 version_set → 400
    with pytest.raises(HTTPException) as e1:
        asyncio.run(rm.compare_versions("a", against="b"))
    assert e1.value.status_code == 400
    # 없는 against → 404
    with pytest.raises(HTTPException) as e2:
        asyncio.run(rm.compare_versions("a", against="ghost"))
    assert e2.value.status_code == 404
    # 시트 인덱스 범위 초과 → 400
    with pytest.raises(HTTPException) as e3:
        asyncio.run(rm.compare_versions("a", against="a", sheet_index=5))
    assert e3.value.status_code == 400


# --- units 추출 ---

def test_vector_units_extraction(tmp_path):
    import ezdxf
    import vector
    doc = ezdxf.new()
    doc.header["$INSUNITS"] = 4  # mm
    msp = doc.modelspace()
    msp.add_line((0, 0), (1000, 0))
    msp.add_line((0, 0), (0, 500))
    dxf = tmp_path / "u.dxf"
    doc.saveas(str(dxf))
    data = vector.extract_vector(str(dxf))
    assert data["units"]["insunits"] == 4
    assert data["units"]["name"] == "mm"
    assert data["units"]["to_meter"] == 0.001


def test_vector_units_unknown(tmp_path):
    """단위 미상(INSUNITS=0)은 unknown + to_meter=None(무성 가정 금지)."""
    import ezdxf
    import vector
    doc = ezdxf.new()
    doc.header["$INSUNITS"] = 0
    doc.modelspace().add_line((0, 0), (1, 1))
    dxf = tmp_path / "u0.dxf"
    doc.saveas(str(dxf))
    data = vector.extract_vector(str(dxf))
    assert data["units"]["name"] == "unknown"
    assert data["units"]["to_meter"] is None
