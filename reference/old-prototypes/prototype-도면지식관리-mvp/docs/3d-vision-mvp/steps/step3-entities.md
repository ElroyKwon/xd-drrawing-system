# Step 3 — Entity Extraction (타입 파라미터)

## 목적

지정된 타입의 공간 객체를 추출한다. 타입은 파라미터 — 1차는 `room`, 이후 `equipment`, `slab`, `wall`, `core` 등.

## 1차 MVP 타입: `room`

### 입력
- Step 1 산출 (view 메타)
- Step 2 산출 (grid, 필수)
- view crop PNG

### 산출 스키마 (room)
```json
{
  "sheet_id": "arch_p060",
  "view_id": "v2",
  "entity_type": "room",
  "items": [
    {
      "id": "R-1F-001",
      "name": "회의실",
      "number": null,
      "grid_anchor": ["5", "A"],
      "polygon_grid": [["5","A"],["5B","A"],["5B","B"],["5","B"]],
      "polygon_source": "vision",
      "confidence": 0.9
    },
    {
      "id": "R-1F-002",
      "name": "복도",
      "grid_anchor": ["5B", "B"],
      "polygon_grid": [["5B","A"],["6","A"],["6","B"],["5B","B"]],
      "polygon_source": "vision",
      "confidence": 0.85
    }
  ],
  "stats": {
    "total": 8,
    "anchored": 7,
    "anchor_rate": 0.875,
    "fallback_used": 1
  }
}
```

### 세부 유연 구현

**옵션 A — 단일 호출로 이름+위치+polygon**
- 2026-04-21 실측: Gemini p060 100% 앵커, p062 25% (시트별 격차 큼)

**옵션 B — 2단계 (coarse → fine)** ★권장
- 호출 1: 이름 + grid_anchor (가장 가까운 grid cell) — 간단, 정확
- 호출 2: 각 room id 에 대해 polygon_grid fine-tune
- polygon 이 실제 실 경계와 일치하도록

**옵션 C — Consensus**
- Gemini + Claude 양측 호출 후 union merge (2026-04-21 방식)
- 비용 2배, 앵커율 약간 향상

**폴리곤 실패 처리**:
- polygon_grid 가 1~2 점이면 `expandToQuadIfDegenerate` 로 fallback 4m×4m 또는 grid_anchor 기준 최소 사각형 생성
- `polygon_source: "fallback"` 로 표시

### 검수 게이트 (자동)

- `stats.anchor_rate ≥ 0.7` (폴리곤이 grid 안에 들어간 비율)
- 각 item 의 `polygon_grid` 꼭짓점이 Step 2 grid 범위 안에 존재
- 미통과 → Step 4 의 사람 검수로 넘김 (수동 결정)

---

## v2 이후 타입 확장

### `equipment`
```json
{"entity_type": "equipment", "items": [
  {"id": "CH-001", "type": "chiller", "grid_anchor": ["6","B"],
   "footprint_mm": [3000, 2000], "height_mm": 1800,
   "linked_doc": "doc-003"}
]}
```
- 외부 참조: `data/doc-entity-links.json`

### `slab`
```json
{"entity_type": "slab", "items": [
  {"id": "SLAB-1F", "floor": "지상1층",
   "polygon_grid": [...], "thickness_mm": 250}
]}
```

### `wall`
```json
{"entity_type": "wall", "items": [
  {"id": "W-001", "path_grid": [["5","A"],["7","A"]], "thickness_mm": 200}
]}
```

각 타입에 **전용 프롬프트** `prompts/step3-{type}.md` 를 작성하여 목적 집중.

## 캐시

- `cache/step3/{sheet_id}_{view_id}_{entity_type}.json`
- 같은 view 에서 다른 타입 추출 시 독립 캐시

## 프롬프트 계획

- `prompts/step3-room-coarse.md` (옵션 B 호출 1)
- `prompts/step3-room-polygon.md` (옵션 B 호출 2)
- v2 진입 시 `prompts/step3-equipment.md`, ...

## 실패 모드

- anchor_rate < 0.3 → **블로킹**. Step 2 grid 품질 의심 → Step 2 재호출.
- 특정 item polygon 0점 → skip (items 에서 제거, stats 에 기록)
- Vision 응답 JSON 파싱 실패 → 재시도 1회, 실패 시 해당 view skip
