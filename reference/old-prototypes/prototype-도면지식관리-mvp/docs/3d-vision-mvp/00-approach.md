# 00 — Approach: 4 Step + 누적 확장 설계

## 왜 Step 을 쪼개는가

2026-04-21 실측 결과(`docs/ai-3d-builder/04-session-2026-04-21-ultrathink.md` §10):
- **한 번에 grid + rooms + walls + dims + annotations 전부 뽑는 프롬프트**는 앵커율 13~41% (Opus 기준).
- **Gemini 는 앵커율 우수(최대 100%) 하나 항목 수 적음**. 서로 상호보완.
- **좁은 목적 · 좁은 프롬프트**가 앵커율 90%+ 의 필수 조건.

따라서 AI 호출을 **목적 단위로 분리**. 단, 13개처럼 기계적으로 쪼개지 않고, **큰 목적 4 step** + **세부는 실제 구현 가능성에 따라 유연 조정**.

---

## Step 1 — Document Identification

**목적 (단 하나)**: 이 시트가 무엇이고, 몇 개 뷰를 담고 있는지 안다.

**입력**: PDF 한 페이지 → 400dpi PNG

**산출** (JSON):
```json
{
  "sheet_id": "arch_p060",
  "discipline": "architectural",
  "view_type": "enlarged_plan",
  "is_3d_candidate": true,
  "sheet_number": "A04.01",
  "sheet_title": "확대평면도-1 (PIT, 지상1층)",
  "scale_primary": "1:100",
  "views": [
    {"view_id": "v1", "floor": "PIT", "region_bbox_px": [x,y,w,h]},
    {"view_id": "v2", "floor": "지상1층", "region_bbox_px": [x,y,w,h]}
  ],
  "confidence": 0.95
}
```

**세부 유연**:
- 단일 호출로 전부 vs 2호출(분류 + 타이틀블록) 분리
- 다중 뷰 감지되면 각 view 를 crop 해서 Step 2 이후 입력에 사용
- 모델 선택: Gemini flash-image (저렴), Claude Opus Vision (정확도↑)

**검수 게이트**:
- `confidence ≥ 0.8`
- `is_3d_candidate = false` 면 해당 시트는 이번 MVP 범위 제외

---

## Step 2 — Coordinate System

**목적 (단 하나)**: 이 도면의 grid 와 FL(층고)을 mm 단위로 안다.

**입력**: Step 1 의 view crop PNG + view 메타

**산출** (JSON):
```json
{
  "view_id": "v1",
  "grid": {
    "x_labels": ["5","5B","6","7"],
    "y_labels": ["A","B","B1","B2","C","D"],
    "x_spacings_mm": [8125, 2875, 10000],
    "y_spacings_mm": [13000, 6950, 4100, null, 5950],
    "total_x_mm": 21000,
    "total_y_mm": 30000,
    "validated": true,
    "issues": []
  },
  "level": {
    "fl_name": "1FL",
    "fl_mm": 94200,
    "ffh_upward_mm": 5500
  }
}
```

**세부 유연**:
- grid 실패 시: 치수선 영역만 crop 해서 Gemini 에 재호출
- level: annotations 텍스트에서 regex 파싱 or Vision 호출
- `sum(x_spacings) == total_x` 자동 검증, mismatch 시 재시도

**검수 게이트**:
- `validated = true` (sum check + labels_count = spacings+1)
- 미통과 시 Step 3 진입 금지 → ask_human 또는 log_decision(스킵)

---

## Step 3 — Entity Extraction (타입 파라미터)

**목적**: 지정된 타입의 공간 객체를 추출한다.

**타입** (1차=room, 순차 확장):
- `room` — 실 (이번 MVP 타겟)
- `equipment` — 설비 (v2)
- `slab` — 층 외곽 (v2)
- `wall`, `core`, `door`, `column` — v3+

**입력**: Step 1 의 view crop + Step 2 의 grid

**산출** (JSON, 타입별 스키마):
```json
{
  "view_id": "v1",
  "entity_type": "room",
  "items": [
    {
      "id": "R-1F-001",
      "name": "회의실",
      "grid_anchor": ["5", "A"],
      "polygon_grid": [["5","A"],["5B","A"],["5B","B"],["5","B"]],
      "confidence": 0.9
    }
  ],
  "stats": {"total": 8, "anchored": 7, "anchor_rate": 0.875}
}
```

**세부 유연**:
- 단일 호출 vs 2단계 (이름·위치 coarse → polygon fine)
- polygon 앵커 실패 시 `expandToQuadIfDegenerate` 로 fallback 4m×4m
- 타입별 전용 프롬프트 `prompts/step3-{type}.md`

**검수 게이트**:
- `anchor_rate ≥ 0.7`
- 각 item 이 Step 2 grid 범위 안에 있는지 자동 검증

---

## Step 4 — 3D 생성 + 검수

**목적**: Step 3 산출을 Three.js 씬에 **누적 추가**하고, 사람이 검수한다.

**입력**: Step 3 의 entities[] + Step 2 의 grid + Step 1 의 view 메타

**산출**:
- `scene/{entity_type}.js` — 해당 타입만 담당하는 ES module
- `scene/index.html` — 누적된 모든 타입을 로드하는 뷰어
- `scene/review-{entity_type}.md` — 사람 검수 기록

**세부 유연**:
- 동일 `scene/index.html` 에 타입이 추가될 때마다 import 만 늘어남
- Step 4 내부에서 BUG-A/B/C 방지 코드 재사용 (`docs/ai-3d-builder/threejs-scene/p062/decisions.md` §2 참조, read-only)

**검수 게이트** (★ 본질):
- 사람이 브라우저로 씬을 확인
- OK → `review-{entity_type}.md` 에 서명 → 다음 타입으로 진행 허용
- NG → 어떤 엔티티가 잘못됐는지 로그 → Step 3 재호출 (해당 타입만 재추출)

---

## 누적 확장 동작

```
세션 N: Step 1~4 (entity_type=room) → scene/rooms.js 추가 + 검수
세션 N+1: Step 3~4 (entity_type=equipment) → scene/equipment.js 추가 + 검수
세션 N+2: Step 3~4 (entity_type=slab) → scene/slab.js 추가 + 검수
...
```

Step 1~2 결과는 **시트별로 캐싱**. 같은 시트에서 새 엔티티 타입 추출할 때 Step 1~2 재호출 불필요.

캐시 구조:
```
cache/
├── step1/{sheet_id}.json
├── step2/{sheet_id}.json
└── step3/{sheet_id}_{entity_type}.json
```

---

## 검수 게이트의 자동화 vs 수동

- **자동 검수** (Step 2 validated, Step 3 anchor_rate) → 통과 못 하면 다음 step 진입 금지
- **수동 검수** (Step 4 사람 확인) → 씬 시각 확인 + 서명. 이건 자동화 불가능, 본질적으로 사람 판단.

이 혼합이 "검수 → 추가" 루프의 핵심.

---

## 다음 세션에서 구현 순서 제안

1. `scripts/00_pdf_to_png.py` — `parity-lab` 의 06_render_and_pdf.py 패턴 재구성 (400dpi, 원본 PDF 에서 시작)
2. `scripts/step1_identify.py` + `prompts/step1.md`
3. `scripts/step2_coordinates.py` + `prompts/step2-grid.md`, `prompts/step2-level.md`
4. `scripts/step3_entities.py` + `prompts/step3-room.md`
5. `scripts/step4_scene.py` (room 타입) + `scene/index.html` skeleton
6. arch_p060/p061/p062#v1 3 시트로 room 추출·씬 생성·검수
7. 검수 통과 후 equipment 확장 (v2)
