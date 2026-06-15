# Inputs — 입력 경로 참조 (read-only)

## 원본 PDF (입력의 진리)

**단일 진입점**: `dwg/1) 건축공사/0. PDF 도면/` 안의 통합 PDF 파일.

- 전체: 122 페이지, 38.85MB
- 벡터 + 텍스트 레이어 포함 (pdfplumber 로 타이틀블록 파싱 가능)

## 이미 렌더된 400dpi PNG (참조 가능)

`dwg/1) 건축공사/0. PDF 도면/_png_dpi400/` — 15 장:
- arch_p001~005 (표지·목록·일반)
- arch_p060~064 (확대평면도·계단실 평면/단면)
- arch_p118~122 (일람표·무창층 검토)

**정책**:
- 이 디렉토리는 **read-only** — 새 MVP 에서 다시 렌더링하지 않음 (시간 절약)
- 필요 시 `parity-lab/p062/scripts/06_render_and_pdf.py` 패턴으로 추가 페이지 렌더 (단, 해당 스크립트는 `_archive-dxf-pivot-2026-04-22/parity-lab-p062/scripts/` 에 있음 — 실행은 새 MVP 의 `scripts/00_pdf_to_png.py` 로 복제해서)

## 설비 참조 데이터 (v2 equipment 타입용)

`data/doc-entity-links.json` — 8 개 설비 (CH-001, VCB-001 등) ↔ 도면 매핑.
- Step 3 equipment 추출 결과와 교차검증 소스

## 건물 기본 정보

- **프로젝트**: LS Electric R-Center 구축
- **층 구성**: PIT(지하공간) · 지상1층 · 지상2층 · 옥탑(RF)
- **설계**: 가운건축
- **축척**: 평면 1:100, 계단실 1:50

## 절대 건드리지 않는 것

- `docs/ai-3d-builder/` 전체 — 이전 트랙, 비교용 보존
- `docs/ai-3d-builder/knowledge-base/sheets/arch_p062.yml` — 이전 MVP 의 KB (참조만)
- `docs/ai-3d-builder/threejs-scene/p062/` — 이전 MVP 의 씬 (비교 기준)
- `src/`, `data/`, `public/drawings/` — 4주 DKS MVP (완전 무관)
- `_archive-dxf-pivot-2026-04-22/` — DWG/DXF 실험물 (종료 처리됨)

## 산출 목적지

- `docs/3d-vision-mvp/cache/` — step 별 JSON (이후 생성)
- `docs/3d-vision-mvp/scene/` — Three.js 씬 (이후 생성)
- `docs/3d-vision-mvp/scene/review-{type}.md` — 검수 기록
