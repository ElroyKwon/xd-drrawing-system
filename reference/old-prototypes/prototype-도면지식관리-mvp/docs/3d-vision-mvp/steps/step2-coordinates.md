# Step 2 — Coordinate System

## 목적 (단 하나)

이 도면(view)의 **그리드**와 **층고(FL)** 를 mm 단위로 수립한다.

## 입력

- Step 1 산출 (view 메타, region_bbox_px)
- view crop PNG

## 산출 스키마

```json
{
  "sheet_id": "arch_p060",
  "view_id": "v1",
  "grid": {
    "x_labels": ["5", "5B", "6", "7"],
    "y_labels": ["A", "B", "B1", "B2", "C", "D"],
    "x_spacings_mm": [8125, 2875, 10000],
    "y_spacings_mm": [13000, 6950, 4100, null, 5950],
    "total_x_mm": 21000,
    "total_y_mm": 30000,
    "validated": true,
    "issues": ["y_spacings 4번째 null — B2→C 구간 치수 미표기"]
  },
  "level": {
    "fl_name": "1FL",
    "fl_mm": 94200,
    "base_datum": "GL±0=EL+94.00",
    "ffh_upward_mm": 5500,
    "source_annotations": ["1FL±0 FH+94.20", "2FL±0=1FL+5,500=EL+99.70"]
  }
}
```

## 세부 유연 구현 옵션

### 2.1 Grid 추출

**옵션 A — 단일 호출로 labels + spacings 동시**
- 한 번에 뽑음. 2026-04-21 실측: Gemini p060 anchor 100%, p062 anchor 25% (변동 큼)

**옵션 B — labels 먼저 · spacings 다음 (권장)**
- 호출 1: labels 만 (x/y 라벨 문자열)
- 호출 2: spacings 만 (치수선 읽기 전용 프롬프트)
- 검증 쉬움 (labels_count = spacings+1 자동 체크)

**옵션 C — labels → spacings → 누락된 span crop 재호출**
- spacings 에 null 있으면 해당 구간만 crop 해서 재질의
- 최고 정확도

### 2.2 Level 추출

**옵션 A — annotations 파싱 (text regex, 기존 `parse_level_stack` 로직)**
- Vision 호출 없음, 싸고 빠름
- 전제: Step 1 or 새 호출로 `annotations_ko` 먼저 추출

**옵션 B — Vision 호출 전용**
- 레벨 마크가 복잡한 시트에서 regex 실패 가능성

**권장**: A 먼저 → 실패 시 B

## 검수 게이트 (자동)

- `grid.validated = true` 조건:
  - `len(x_labels) == len(x_spacings_mm) + 1`
  - `len(y_labels) == len(y_spacings_mm) + 1`
  - `sum(x_spacings_mm) == total_x_mm` (null 제외 sum 허용 오차 ±50mm)
- 미통과 시 `issues[]` 에 기록 + Step 3 진입 여부 결정 (수동)

## 캐시

- `cache/step2/{sheet_id}_{view_id}.json`

## 실패 모드

- grid 라벨 수 mismatch → issues 에 기록, Step 3 진입 허용 (fallback 사용)
- level 텍스트 완전 누락 → `fl_mm = null`, Step 4 에서 기본값 사용
- spacings 전부 null → **블로킹** (Step 3 진입 금지, ask_human)

## 프롬프트 계획

새로 작성 (기존에 없음):
- `prompts/step2-grid-labels.md` (2.1 옵션 B 전반부)
- `prompts/step2-grid-spacings.md` (2.1 옵션 B 후반부)
- `prompts/step2-level.md` (2.2 옵션 B — text 파싱 실패 시 fallback 전용)
