# SESSION HANDOFF — 2026-04-22

> **다음 세션이 가장 먼저 읽을 파일**. 본 세션 결과와 트랙 분기 결정, 신규 MVP 진입 경로를 담음.

---

## 한 줄 요약

이번 세션 전반부에 이전 트랙(`docs/ai-3d-builder/`) 의 5 Stage 파이프라인을 Agent SDK 로 완성 실행. **후반부에 사용자 지시로 트랙 분기** — `docs/3d-vision-mvp/` 신규 MVP 를 설계하고 scaffolding 완료. 다음 세션부터 신규 트랙에서 구현 시작.

**중요 지시사항**:
- 입력은 PDF 부터 (DWG/DXF 루트 금지)
- 목표는 3D 모델링만 (온톨로지 아님)
- 엔티티 누적 확장 (실→설비→층외곽→...)
- 검수 → 추가 루프가 본질

---

## 본 세션에서 한 일

### Part 1 — 이전 트랙 완성 (`docs/ai-3d-builder/`)

플랜: `C:/Users/cruel/.claude/plans/sprightly-churning-umbrella.md`

- Stage 0: DXF 산출물 137MB 아카이브
- Stage 1: 15 시트 분류 (Gemini) → classifications.json · 3D 후보 7 시트
- Stage 2+3: 공간·뷰타입 인덱스 → floor_to_sheets.yml 등 3종
- Stage 4: 모델링 순서 DAG → modeling_order.yml (queue 7, blocked 3)
- Stage 5: Agent SDK 10 tool + runner + system_prompt, **3회 자율 실행** (smoke·Run A·Run B)
- Run A: 4 시트 KB 신규 구축 (앵커율 대부분 100%)
- Run B: generate_threejs 성공, render_preview 실패 (playwright 32-bit 빌드 오류), Agent 자율 복구
- level-stack merge 버그 수정, kb-loader ES module 전환
- 토큰 ~58k Anthropic + Gemini 4회 ≈ $1.3

### Part 2 — 트랙 분기 결정 및 격리

사용자 피드백:
1. "DWG 로 하려고 했던 모든 내용을 완전히 별개로"
2. "AI 가 한 번에 이미지 분석 못한다 — 큰 step 과 그 안의 세부 유연, 각 step 별 정확한 목적"
3. "지금은 실만 하되 추후 설비·층외곽을 단계별로 추가할 수 있게. 모델링 → 검수 → 추가 루프"
4. "**온톨로지는 필요 없다 — 3D 모델링만 목적**"

**격리 작업**:
- `parity-lab/p062/` 전체(18MB) → `_archive-dxf-pivot-2026-04-22/parity-lab-p062/`
- 실수로 만들어진 빈 중첩 폴더 `docs/` 제거
- 아카이브 총 154MB

**신규 MVP scaffolding**:
```
docs/3d-vision-mvp/                [신규]
├── README.md
├── 00-approach.md                  (4 Step 설계)
├── 01-entity-roadmap.md            (실→설비→층외곽→벽·코어→단면)
├── _inputs_ref.md                  (입력 경로)
├── steps/
│   ├── step1-identify.md           (문서 식별)
│   ├── step2-coordinates.md        (grid + FL)
│   ├── step3-entities.md           (타입 파라미터)
│   └── step4-3d-and-review.md     (씬 누적 + 검수 게이트)
├── prompts/                        (다음 세션)
├── scripts/                        (다음 세션)
└── scene/                          (다음 세션)
```

---

## 현재 상태 지도

```
docs/
├── 3d-vision-mvp/                       ★ 다음 세션 시작점
│   └── (설계 문서 8 파일, prompts·scripts·scene 비어있음)
├── ai-3d-builder/                       ◐ 이전 트랙, read-only 보존
│   ├── (이전 Phase 1~2 산출물 전체 유지)
│   ├── agent/runs/20260422_*              (3 세션)
│   ├── threejs-scene/p062/                (2026-04-21 MVP)
│   ├── threejs-scene/full-building/       (2026-04-22 Agent 산출)
│   └── _archive-dxf-pivot-2026-04-22/     (154MB DXF+parity 격리)
└── upgrade-plan/                        (DKS 4주 MVP, 본 세션 미접촉)
```

## 다음 세션 진입 경로

### 1. 오리엔테이션 (5분)
1. `cat docs/3d-vision-mvp/README.md`
2. `cat docs/3d-vision-mvp/00-approach.md`
3. `cat docs/3d-vision-mvp/steps/step1-identify.md`

### 2. 첫 구현 작업 (1~2시간)
1. **PDF→PNG 변환기** 복제
   - 원본: `_archive-dxf-pivot-2026-04-22/parity-lab-p062/scripts/06_render_and_pdf.py`
   - 신규: `docs/3d-vision-mvp/scripts/00_pdf_to_png.py`
   - 400dpi, 페이지 단위, `_png_dpi400/` 에 이미 있으면 skip
2. **Step 1 프롬프트** `prompts/step1-identify.md` 작성
   - 기반: `docs/ai-3d-builder/prompts/00-standard-classifier.md` (read-only 복제)
   - 개선: `views[]` 필드 추가 (다중 뷰 bbox 검출)
3. **Step 1 스크립트** `scripts/step1_identify.py` 실행 → 3 시트 (arch_p060/p061/p062) 캐시 생성

### 3. 캐싱 구조
```
docs/3d-vision-mvp/cache/
├── step1/{sheet_id}.json
├── step2/{sheet_id}_{view_id}.json
└── step3/{sheet_id}_{view_id}_{entity_type}.json
```

### 4. 검수 게이트 준비
- Step 4 에서 사용자가 브라우저로 확인할 `scene/index.html` 스켈레톤 먼저 만들어두기

---

## 메모리 반영 사항

신규:
- `feedback_3d_not_ontology.md` — 3D 모델링만 목적
- `feedback_pdf_not_dwg.md` — PDF 부터 시작 (Part 1 종료 시 추가됨)

갱신:
- `project_ai_3d_builder_track.md` — 이전 트랙 완성 + 신규 트랙 분기 기록
- `project_parity_experiment.md` — DXF 경로 종료·아카이브
- `MEMORY.md` — 인덱스 동기화

---

## 열린 이슈 · 추후 결정

### 이전 트랙 미완 (우선순위 낮음 — 사용자가 재개 요구 시)
1. `render_preview` Puppeteer 이식 (Node v24 확인됨)
2. 단면도 전용 프롬프트
3. p121/p122 elevation 오분류 재분류

### 신규 트랙 결정 필요 (다음 세션 초입)
1. 모델 선택 — Step 1~3 각각 Gemini vs Claude vs Consensus 초안?
2. 캐시 전략 — SQLite vs JSON 파일?
3. scene/index.html 스타일 — p062 MVP 스타일 그대로 vs 새로 설계?
4. 검수 서명 방식 — 파일 수동 편집 vs 별도 툴?

### 환경
- 32-bit Python 환경 주의 (playwright 같은 C++ 빌드 의존성 실패)
- Gemini API · Anthropic API 키는 `api_keys.json` 에 이미 설정됨
- Node v24 사용 가능

---

## 체크리스트 (다음 세션 초입)

- [ ] `docs/3d-vision-mvp/README.md` + `00-approach.md` 읽기
- [ ] `MEMORY.md` 자동 로드 확인 (feedback_3d_not_ontology · feedback_pdf_not_dwg 반영)
- [ ] 이전 트랙 `threejs-scene/full-building/index.html` 은 참고용으로만 브라우저에서 확인 가능
- [ ] 사용자에게 "`docs/3d-vision-mvp/scripts/00_pdf_to_png.py` 부터 만들까요?" 로 시작 제안
- [ ] 사용자 승인 시 Step 1 프롬프트·스크립트 구현 진입
