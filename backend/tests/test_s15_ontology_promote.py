"""단계10 overlay 되돌림 회귀 가드 (지식그래프 트랙으로 방향 수정).

list_equipment 는 순수 큐레이트만 반환한다(추출 태그 승격 없음).
추출 태그의 '설비 노출'은 지식그래프 tag 노드/has_tag 엣지가 담당(kg_store).
"""
import ontology


def test_list_equipment_is_pure_curated(tmp_path, monkeypatch):
    # 미러에 큐레이트 1건만. 추출 태그가 있어도 list_equipment 엔 섞이지 않아야 한다.
    monkeypatch.setenv("XD_UPLOADS_DIR", str(tmp_path))
    import importlib, config
    importlib.reload(config)
    importlib.reload(ontology)
    st = ontology.OntologyStore()
    st.add_equipment("P1", {"equipment_id": "E1", "tag": "MTR-1", "type": "motor"}, ["s1"])
    items = st.list_equipment("P1")
    assert [e["equipment_id"] for e in items] == ["E1"]
    assert all(e.get("origin", "curated") == "curated" for e in items)


def test_extracted_overlay_removed():
    # overlay 기계가 제거됐는지 API 표면으로 확인(회귀 가드).
    assert not hasattr(ontology.OntologyStore, "_extracted_overlay")
    assert not hasattr(ontology, "_norm_tag")
