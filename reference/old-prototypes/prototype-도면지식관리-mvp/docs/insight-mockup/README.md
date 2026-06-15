# Insight Mockup Lab — 통계 × 온톨로지 결합 시연 목업

> **이 문서는 회의·시연용 별도 기능**이다. 4주 MVP 업그레이드(`docs/upgrade-plan/`)와 독립이며, 기존 코드·데이터는 읽기만 한다. 실제 백엔드 통계 분석(SLM)과는 **연결되지 않는다**.

## 0. 한 줄 요지

> "배터리 시스템에서 통계를 돌려 AI가 해석했던 기존 SLM 파이프라인"의 아이디어만 가져와, **R-Center 기계/전기 도면·온톨로지**를 대상으로 "(가상) 통계 이벤트 + 온톨로지 결합 → Gemini 대화" 흐름을 **단일 화면에서 목업으로 시연**한다.

## 1. 왜 필요한가

- 기존 SLM은 Phase 2(통계) → Phase 3(AI 해석) 직결 구조. 통계 결과 JSON이 의미 맥락 없이 LLM에 투입돼 **고정 텍스트·채널 누락 등 한계**가 관찰됨 (`SLM-개발중-생산된MD/_doc/phase3_insight_improvement_plan.md`).
- 이 레포에는 이미 **YAML 온톨로지 379개 엔티티**(기계 95 + 전기 284)와 이를 검색·주입하는 챗 파이프라인(`src/lib/ontology/`, `src/app/api/chat/stream/`)이 살아 있다.
- 두 자산을 결합하면 "통계 값 → 해당 설비 스펙·관계·도면"까지 자동 맥락화된 답변이 가능함을 **회의 자리에서 시각적으로 증명**하는 것이 이 목업의 목적.

## 2. 전제와 한계 (정직한 면)

| 항목 | 목업에서의 처리 |
|---|---|
| 실 통계 엔진(SLM/Ollama) | ❌ 없음. 가상 이벤트 15~20건 수동 작성 |
| 배터리 도면 | ❌ 없음. R-Center 기계·전기 설비(VCB·Chiller·Air Cooler 등)로 치환 |
| LLM | ✅ 이미 연결된 **Google Gemini** 재사용 (mock 모드 폴백) |
| 온톨로지 | ✅ 현재 YAML 379개 그대로. 신규 작성 없음 |
| 관계 홉 | ✅ 2홉까지 확장 |
| no-match 케이스 | ✅ 일부 이벤트는 의도적으로 엔티티 매칭 실패 — 한계를 숨기지 않음 |

**가져온 것은 "개념"뿐**: (a) thermal / spc / integrity 3분류, (b) CRITICAL / WARNING / NORMAL severity, (c) Insight Bundle(통계+온톨로지 결합 JSON) 아이디어.

## 3. 진입점

- **화면**: `/insight/lab`
- **기존 자산 의존**: `src/lib/ontology/{loader,search}.ts`, `dwg/온톨로지/**/*.yaml`, 기존 `PdfViewer` (도면 점프)

## 4. 파일 지도

```
docs/insight-mockup/
├── README.md                ← 이 파일
├── 01-design.md             ← Phase 1 아키텍처·Bundle v1 스키마·프롬프트
├── 02-scenario.md           ← 회의 시연 스크립트 3~5분
└── 03-rag-integration.md    ← Phase 2 설계: 통계 × 온톨로지 × 문서 RAG

data/insight/
├── mock-events.json         ← 가상 통계 이벤트 15~20건
└── event-entity-map.json    ← (선택) 이벤트 → 엔티티 수동 매핑 보강

src/lib/insight-mockup/
├── types.ts                 ← InsightEvent, InsightBundle
└── bundle-builder.ts        ← 이벤트 + 온톨로지 조인 로직 (2홉)

src/app/api/insight/lab/
├── bundles/route.ts         ← GET: 목록 / 상세
└── chat/stream/route.ts     ← POST: Bundle 컨텍스트 + Gemini 스트림

src/app/(s2)/insight/lab/
├── page.tsx                 ← 3분할 레이아웃
├── EventList.tsx            ← 좌: 이벤트 리스트
├── BundleView.tsx           ← 중: 통계+엔티티+관계+도면
├── BundleChat.tsx           ← 우: Bundle 컨텍스트 챗
└── ImageLightbox.tsx        ← 근거 도면 미리보기 모달 (page_NNN.png 직접 로드)
```

## 5. 시나리오 요약 (자세히는 `02-scenario.md`)

1. `/insight/lab` 진입
2. 왼쪽 이벤트 리스트에서 "VCB 1101 절연저항 이상 (Z=-3.2σ)" 클릭
3. 중앙에 **Insight Bundle** 자동 렌더: 통계 카드 + 엔티티 스펙 + 2홉 관계 그래프 + 근거 도면 썸네일
4. 오른쪽 챗: "물리적 원인 후보?" → Gemini가 Bundle을 근거로 답변
5. 증거 카드 클릭 → 기존 `PdfViewer` 페이지로 점프
6. **한계 시연**: no-match 이벤트 하나 클릭해서 "온톨로지에 엔티티 없음" 표시 확인

## 6. 건드리지 않는 것

- `src/app/api/chat/stream/` (기존 챗 API)
- `src/lib/ontology/*` (온톨로지 로더·검색)
- `src/components/PdfViewer.tsx`, `AnnotationLayer.tsx` 등 보존 6항목
- `data/documents.json`, `data/doc-entity-links.json` (읽기만)
- `docs/upgrade-plan/STATUS.md` 및 W4 작업 흐름

## 7. 관련 문서

- Phase 1 설계 상세: `01-design.md`
- 시연 스크립트: `02-scenario.md`
- Phase 2 확장 설계(RAG 통합): `03-rag-integration.md`
- SLM 개념 원천: `docs-표준레이어/SLM-개발중-생산된MD/_dev/12_종합-인사이트-생성-로직.md`, `_doc/phase3_insight_improvement_plan.md`
- 기존 챗 파이프라인: `src/app/api/chat/stream/route.ts`
- 4주 MVP 플랜 (별개 트랙): `docs/upgrade-plan/README.md`
