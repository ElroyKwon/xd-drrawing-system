# 지식그래프 데이터 트랙 (Stage 1) 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 설비 `appears_on` 공존으로 `relates_to(track=llm)` 후보를 실공급해 `relates_to(llm)=0` 어휘 벽을 해소한다.

**Architecture:** 관계 생성기(`MockExtractProvider.analyze`, 8002 사이드카)의 입력을 *시트 추출태그 공출현* → *설비 공존*으로 교체하고, 반환 식별자를 **설비 tag**로 해 build의 `tag_to_eq`(설비 큐레이트태그)와 어휘를 일치시킨다. build는 slim_eq에 `sheet_ids`만 추가(1줄), 매핑·저장·⑥ write-back·읽기 API는 무변경. 공존 관계는 항상 track=llm(미검증 점선)이며 ⑥ write-back으로 사람이 confirm/reject 한다.

**Tech Stack:** Python(FastAPI 8002 사이드카·pytest), 기존 `backend/extract/provider.py`·`scripts/build_knowledge_graph.py`.

**FROZEN 스펙:** `docs/superpowers/specs/2026-07-10-kg-data-track-design.md`

**회귀 기준선(사수):** 백엔드 KG 43 green · 8002 extract 8 · AI 50 · 프론트 vitest 135 · build GREEN.

**확정 파라미터:** `MAX_EQ_PER_SHEET=12` · `MIN_SHARED_SHEETS=1` · confidence `BASE=0.3, STEP=0.1, CAP=0.65`.

---

## 파일 구조

| 파일 | 책임 | 변경 |
|---|---|---|
| `backend/extract/provider.py` | `MockExtractProvider.analyze` — 설비 공존 관계 생성(egress 0) | 재작성 + 상수 5개 |
| `backend/extract/test_extract.py` | 공존 로직 단위 테스트 | 기존 공출현 테스트 → 설비 공존으로 갱신 |
| `scripts/build_knowledge_graph.py` | `_call_analyze` slim_eq에 `sheet_ids` 추가(변경점 1) | 1줄 |
| `backend/tests/test_kg_build.py` | slim_eq payload 가드 + 공존→설비 매핑 e2e | 테스트 2개 추가 |

> `backend/extract/main_extract.py`(AnalyzeRequest)는 `equipment: list[dict]` 자유필드라 **무변경**. build 매핑(`tag_to_eq`)·⑥ write-back·읽기 API도 **무변경**.

---

### Task 1: 설비 공존 관계 생성 (`MockExtractProvider.analyze`)

**Files:**
- Modify: `backend/extract/provider.py` (상수 추가 + `MockExtractProvider.analyze` 재작성, 현재 77~92행)
- Test: `backend/extract/test_extract.py` (기존 `test_analyze_mock_cooccurrence_relations`, 93행~ 갱신)

- [ ] **Step 1: 실패 테스트 작성 (기존 공출현 테스트를 설비 공존으로 교체)**

`backend/extract/test_extract.py`의 `test_analyze_mock_cooccurrence_relations`를 아래로 교체:

```python
def test_analyze_mock_equipment_cooccurrence():
    """설비 appears_on 공존 → relates_to(설비 tag). 시트태그가 아니라 설비 sheet_ids 가 소스."""
    c = client()
    body = {"equipment": [
        {"tag": "VCB-1", "type": "VCB", "sheet_ids": ["s1", "s2"]},
        {"tag": "TR-1", "type": "TR", "sheet_ids": ["s1"]},
        {"tag": "MTR-9", "type": "MTR", "sheet_ids": ["s9"]},  # 고립(공존 없음)
    ], "sheets": []}
    r = c.post("/analyze", json=body)
    assert r.status_code == 200
    data = r.json()
    pairs = {(x["src_tag"], x["dst_tag"]) for x in data["relations"]}
    assert ("TR-1", "VCB-1") in pairs          # s1 공존, 무방향 정렬(TR-1 < VCB-1)
    assert not any("MTR-9" in p for p in pairs)  # 고립 설비는 관계 없음
    assert all(x["relation"] == "relates_to" for x in data["relations"])
    assert all(x["confidence"] < 0.7 for x in data["relations"])  # 항상 미검증(CAP<0.7)
    # 반환 식별자는 설비 tag(build tag_to_eq 와 동일 어휘)여야 매핑 성공.
    assert all(x["src_tag"] and x["dst_tag"] for x in data["relations"])
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend/extract && ../.venv/Scripts/python.exe -m pytest test_extract.py::test_analyze_mock_equipment_cooccurrence -v`
Expected: FAIL (현재 analyze는 sheets 공출현 기반이라 `("TR-1","VCB-1")` 미생성 — assert 실패)

- [ ] **Step 3: 최소 구현 — analyze 재작성**

`backend/extract/provider.py`의 `_MOCK_CONF = 0.65` 아래에 상수 추가:

```python
# 설비 공존 관계(Stage 1) 파라미터 — FROZEN 스펙 2026-07-10 §4.
_MAX_EQ_PER_SHEET = 12   # 시트당 설비 상한(폭발 가드, 현 데이터 무발동)
_MIN_SHARED_SHEETS = 1   # 최소 공유 시트(1=후보 주도, 큐레이트 위임)
_CO_BASE, _CO_STEP, _CO_CAP = 0.3, 0.1, 0.65  # confidence: 공유 수 스케일, CAP<0.7(항상 미검증)
```

`MockExtractProvider.analyze`(현재 77~92행) 전체를 교체:

```python
    def analyze(self, equipment: list, sheets: list) -> dict:
        """설비 appears_on 공존 관계(egress 0). 같은 시트에 등장하는 설비쌍 → relates_to(track=llm 후보).

        어휘 벽 우회: 반환 src_tag/dst_tag = **설비 tag**(build tag_to_eq 와 동일 어휘).
        입력은 equipment[].sheet_ids(공존 소스). `sheets` 는 시그니처 유지용(Stage 1 미사용).
        필터: 시트당 설비 > MAX 스킵 · 공유 시트 < MIN 드롭. confidence CAP<0.7(항상 미검증).
        """
        sheet_to_tags: dict = {}
        for e in equipment:
            tag = e.get("tag")
            if not tag:
                continue
            for sid in (e.get("sheet_ids") or []):
                sheet_to_tags.setdefault(sid, set()).add(tag)
        pair_shared: dict = {}
        skipped_sheets = 0
        for sid, tags in sheet_to_tags.items():
            if len(tags) > _MAX_EQ_PER_SHEET:
                skipped_sheets += 1
                continue
            st = sorted(tags)
            for i in range(len(st)):
                for j in range(i + 1, len(st)):
                    pair_shared[(st[i], st[j])] = pair_shared.get((st[i], st[j]), 0) + 1
        relations = []
        dropped = 0
        for (a, b), shared in sorted(pair_shared.items()):
            if shared < _MIN_SHARED_SHEETS:
                dropped += 1
                continue
            conf = round(min(_CO_BASE + _CO_STEP * shared, _CO_CAP), 2)
            relations.append({
                "src_tag": a, "dst_tag": b, "relation": "relates_to",
                "confidence": conf,
                "evidence": f"설비 공존 시트 {shared}개",
            })
        # silent-cap 금지(스펙 §5): 규모를 로그로 명시.
        logger.info("analyze(설비공존): 후보 %d · 스킵시트 %d · 드롭 %d",
                    len(relations), skipped_sheets, dropped)
        return {"relations": relations, "notes": []}
```

- [ ] **Step 4: 테스트 통과 확인 + 8002 전체 회귀**

Run: `cd backend/extract && ../.venv/Scripts/python.exe -m pytest test_extract.py -v`
Expected: PASS (신규 공존 테스트 + 나머지 7개, 총 8 green — 기존 공출현 테스트는 교체됨)

- [ ] **Step 5: 커밋**

```bash
git add backend/extract/provider.py backend/extract/test_extract.py
git commit -m "feat(kg): Stage1 설비 공존 관계 생성 — analyze 를 시트태그 공출현→설비 appears_on 공존으로"
```

---

### Task 2: build slim_eq에 sheet_ids 전달 (변경점 1)

**Files:**
- Modify: `scripts/build_knowledge_graph.py:77` (`_call_analyze`의 slim_eq)
- Test: `backend/tests/test_kg_build.py` (테스트 1개 추가)

- [ ] **Step 1: 실패 테스트 작성**

`backend/tests/test_kg_build.py` 끝에 추가:

```python
def test_call_analyze_forwards_sheet_ids(build_mod, monkeypatch):
    """slim_eq 가 sheet_ids 를 8002 로 넘겨야 provider 가 공존을 계산할 수 있다(변경점 1)."""
    b = build_mod
    captured = {}
    monkeypatch.setattr(b, "_post",
                        lambda url, body: (captured.update(body), {"relations": [], "notes": []})[1])
    b._call_analyze(
        [{"tag": "MTR-1", "type": "motor", "sheet_ids": ["s1", "s2"]}], [])
    assert captured["equipment"][0]["sheet_ids"] == ["s1", "s2"]
    assert captured["equipment"][0]["tag"] == "MTR-1"
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_kg_build.py::test_call_analyze_forwards_sheet_ids -v`
Expected: FAIL with `KeyError: 'sheet_ids'` (현재 slim_eq는 tag·type만)

- [ ] **Step 3: 최소 구현**

`scripts/build_knowledge_graph.py:77`의 slim_eq 한 줄을 교체:

```python
    slim_eq = [{"tag": e.get("tag"), "type": e.get("type"),
                "sheet_ids": e.get("sheet_ids") or []} for e in equipment]
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_kg_build.py -v`
Expected: PASS (신규 1 + 기존 3 = 4 green)

- [ ] **Step 5: 커밋**

```bash
git add scripts/build_knowledge_graph.py backend/tests/test_kg_build.py
git commit -m "feat(kg): build slim_eq 에 sheet_ids 전달 — provider 공존 계산 입력"
```

---

### Task 3: 공존 관계 → 설비 매핑 e2e (어휘 벽 해소 검증)

**Files:**
- Test: `backend/tests/test_kg_build.py` (테스트 1개 추가)

- [ ] **Step 1: 실패 테스트 작성 — 실제 provider 를 통과시켜 relates_to(llm) > 0**

`backend/tests/test_kg_build.py` 끝에 추가:

```python
def test_coexistence_relations_map_to_equipment(build_mod, monkeypatch):
    """설비 공존 → 설비 tag 반환 → build tag_to_eq 매핑 성공 → relates_to(llm) > 0.
    _call_analyze 를 실제 MockExtractProvider 로 스텁해 어휘 매핑을 end-to-end 검증(8002 없이)."""
    b = build_mod
    monkeypatch.setattr(b, "_fetch_equipment", lambda p: [
        {"equipment_id": "E1", "tag": "MTR-1", "type": "motor", "sheet_ids": ["s1", "s2"]},
        {"equipment_id": "E2", "tag": "VCB-1", "type": "breaker", "sheet_ids": ["s1"]}])
    for fn in ("_fetch_sheets", "_fetch_issues", "_fetch_tasks", "_fetch_files"):
        monkeypatch.setattr(b, fn, lambda p: [])
    from extract.provider import MockExtractProvider
    prov = MockExtractProvider()
    monkeypatch.setattr(b, "_call_analyze", lambda eq, sh: prov.analyze(eq, sh))
    g = b.build_graph("P1", built_at="2026-07-09T00:00:00")
    rels = [e for e in g["edges"] if e["type"] == "relates_to"]
    assert len(rels) >= 1                       # 어휘 벽 해소 — 0 이 아님
    assert rels[0]["track"] == "llm"            # 항상 미검증(⑥ write-back 대상)
    assert {rels[0]["src"], rels[0]["dst"]} == {"eq:E1", "eq:E2"}  # 설비 노드로 매핑
    import kg_store
    assert kg_store.check_integrity(g) == []    # 무결성 위반 0
```

> `from extract.provider import MockExtractProvider` — build 테스트는 `backend/`를 cwd로 실행하므로 `extract` 패키지가 import 경로에 있다(기존 conftest 확인). 실패 시 `sys.path`에 `backend` 추가로 보정.

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_kg_build.py::test_coexistence_relations_map_to_equipment -v`
Expected: PASS 예상 (Task 1·2 완료 후면 통과) — 만약 import 에러면 Step 3 보정. 논리 회귀 검출용 가드 테스트.

- [ ] **Step 3: (필요 시) import 경로 보정**

import 에러 시 테스트 상단에 추가:

```python
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # backend/
```

- [ ] **Step 4: 전체 KG 회귀 확인**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/ -k kg -v`
Expected: PASS (KG 43 + 신규 → all green)

- [ ] **Step 5: 커밋**

```bash
git add backend/tests/test_kg_build.py
git commit -m "test(kg): 공존→설비 매핑 e2e — relates_to(llm)>0 어휘 벽 해소 가드"
```

---

### Task 4: 실 청주 데이터 빌드 스모크 (실행 검증)

**Files:** (코드 변경 없음 — 실 데이터 빌드·육안)

- [ ] **Step 1: 8000 + 8002 별도 포트 기동**

```bash
# 8000 백엔드 (별도 포트 예시 — 다른 세션과 비충돌)
cd backend && XD_STORE=json .venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8010 &
# 8002 extract 사이드카 (mock, egress 0)
cd backend/extract && ../.venv/Scripts/python.exe -m uvicorn main_extract:app --host 127.0.0.1 --port 8012 &
```

- [ ] **Step 2: 실 빌드 실행 (8000·8002 포트 환경변수 주입)**

Run:
```bash
cd "D:/_Project/xd-drawing-system" && \
XD_BACKEND_BASE=http://127.0.0.1:8010 XD_EXTRACT_BASE=http://127.0.0.1:8012 \
./backend/.venv/Scripts/python.exe scripts/build_knowledge_graph.py "LS 청주사업장"
```
> ⚠️ build 스크립트가 8000/8002 base를 어떤 환경변수로 읽는지 확인(`scripts/build_knowledge_graph.py` 상단 `_get`/`_EXTRACT`). 실제 변수명에 맞춰 주입.

- [ ] **Step 3: relates_to(llm) > 0 실측**

Run:
```bash
./backend/.venv/Scripts/python.exe -c "
import json
d=json.load(open('backend/uploads/_knowledge_graph.json',encoding='utf-8'))
g=d['graphs']['LS 청주사업장']
rel=[e for e in g['edges'] if e['type']=='relates_to' and e['track']=='llm']
print('relates_to(llm):', len(rel), '(기대 16쌍 근처)')
for e in rel[:5]: print(' ', e['src'],'-',e['dst'],e.get('evidence'))
"
```
Expected: `relates_to(llm): 16` 근처 (실 공존 후보). **세션30 `relates_to(llm)=0` 지표 해소.**

- [ ] **Step 4: 브라우저 육안 (선택)**

세션31 절차 재현: 프론트 5174 기동 → 지식그래프 탭 → 점선(공존 relates_to) 다수 확인 → 하나 클릭 → confirm(승격)/reject 큐레이션. 시드 없이 실데이터.

- [ ] **Step 5: 서버 내림 + 스냅샷 원복 판단**

실 빌드 결과 스냅샷(`backend/uploads/`, gitignore)은 커밋 무영향. 필요 시 세션 종료 시 원복. 서버 프로세스 종료.

---

## Self-Review

**1. 스펙 커버리지:**
- §0 어휘 벽 우회 → Task 1(설비 tag 반환)·Task 3(매핑 e2e). ✅
- §3 알고리즘(공존·필터·confidence) → Task 1. ✅
- §4 필터 파라미터(MAX=12·MIN=1·CAP) → Task 1 상수. ✅
- §5 silent-cap 금지 로그 → Task 1 `logger.info`. ✅
- §6 build 연동(slim_eq sheet_ids) → Task 2. ✅
- §9 HARD 불변식(멱등·egress0·track=llm·매핑무변경·회귀0) → Task 1~3 + 기준선 게이트. ✅
- §12 테스트 전략(provider·build·통합) → Task 1~4. ✅
- **미커버**: §7 시드 스크립트 "보존"(O3) = 파일 삭제 안 함 = 무작업. ✅ (변경 불요)

**2. 플레이스홀더:** 없음. 전 스텝 실제 코드·명령·기대출력 명시.

**3. 타입/이름 일관성:** `MockExtractProvider.analyze`·`_call_analyze`·`sheet_ids`·`src_tag/dst_tag`·`relates_to`·`track=llm`·`tag_to_eq` — Task 간 일치. 상수명 `_MAX_EQ_PER_SHEET`/`_MIN_SHARED_SHEETS`/`_CO_*` Task 1 내 정의·사용 일치.

**주의(구현자):** Task 4의 build 스크립트 포트 환경변수명은 실제 코드(`_get`/`_EXTRACT` 정의부)를 먼저 확인하고 맞춘다 — 기본이 8000/8002 하드코딩이면 그 값을 별도 포트로 바꾸거나 기본 포트로 기동.
