# Step 1 — Document Identification

## 목적 (단 하나)

이 PDF 페이지가 **무엇인지 · 몇 개 뷰를 담고 있는지** 안다.

## 입력

- PNG 파일 경로 (400dpi, `_png_dpi400/arch_p*.png`)

## 산출 스키마

```json
{
  "sheet_id": "arch_p060",
  "png_path": "dwg/.../arch_p060.png",
  "discipline": "architectural",
  "view_type": "enlarged_plan",
  "is_3d_candidate": true,
  "sheet_number": "A04.01",
  "sheet_title": "확대평면도-1 (PIT, 지상1층)",
  "project": "LS Electric R-Center 구축",
  "scale_primary": "1:100",
  "date": "2024.05",
  "revision": null,
  "views": [
    {"view_id": "v1", "floor": "PIT", "region_bbox_px": [320, 480, 2800, 3200]},
    {"view_id": "v2", "floor": "지상1층", "region_bbox_px": [3200, 480, 2900, 3200]}
  ],
  "language": "ko",
  "confidence": 0.95
}
```

## 세부 유연 구현 옵션

### 옵션 A — 단일 호출
- 1 Gemini/Claude 호출로 전부
- 빠르고 싸지만 다중 뷰 detect 정확도 떨어질 수 있음

### 옵션 B — 2단계
- 호출 1: 분류만 (discipline/view_type/is_3d_candidate/confidence)
- 호출 2: is_3d_candidate=true 인 경우만 타이틀블록·뷰 분리 상세
- 비용 절감 (비 3D 시트는 1 호출로 종료)

### 옵션 C — 3단계
- 호출 1: 분류
- 호출 2: 타이틀블록 (sheet_number·title·scale 등)
- 호출 3: 뷰 분리 (bbox 검출)
- 최고 정확도, 최고 비용

**권장 시작**: 옵션 B (기존 `00-standard-classifier.md` 프롬프트 기반)

## 검수 게이트

- `confidence ≥ 0.8`
- `is_3d_candidate=false` → Step 2~4 건너뜀 (해당 시트 MVP 범위 밖)
- `views[]` 가 비면 자동 fallback: 시트 전체를 v1 으로

## 캐시

- `cache/step1/{sheet_id}.json`
- 동일 시트 재호출 시 캐시 사용 (Step 3 때 다른 entity_type 진입 시 재호출 불필요)

## 프롬프트 참조

- 기반: `docs/ai-3d-builder/prompts/00-standard-classifier.md` (read-only, 복제해서 `prompts/step1-identify.md` 로)
- 개선: `views[]` 필드 추가 — 다중 뷰 bbox 검출 지시

## 실패 모드

- confidence < 0.8 → `log_failure` + human notify
- `is_3d_candidate=null` → 재시도 1회, 여전히 null 이면 skip
- JSON 파싱 실패 → `try_parse_json` 로 복구, 실패 시 raw text 로그
