# 01 — 설계: Insight Bundle 파이프라인 (목업)

## 1. 아키텍처 한 장 요약

```
┌─────────────────────────────────────────────────────────────┐
│  /insight/lab  (3분할)                                      │
│                                                             │
│  ┌────────┐  ┌─────────────────────┐  ┌─────────────────┐   │
│  │ 이벤트  │  │  Insight Bundle 뷰   │  │  Bundle Chat    │   │
│  │ 리스트 │  │                     │  │  (Gemini)       │   │
│  └───┬────┘  │ 통계카드 / 엔티티   │  │                 │   │
│      │       │ 2홉 관계 / 도면카드  │  │ 질문·답변 스트림 │   │
│      ▼       └─────────┬───────────┘  └────────▲────────┘   │
│  GET /api/insight/lab/bundles     POST /api/insight/lab/chat/stream
│              │                                ▲             │
└──────────────┼────────────────────────────────┼─────────────┘
               ▼                                │
   ┌─────────────────────────────┐      ┌───────┴────────┐
   │  bundle-builder.ts          │      │ Gemini 3.1     │
   │  (semantic join + 2-hop)    │◄─────┤ (prompt=Bundle)│
   └────┬───────────────┬────────┘      └────────────────┘
        │               │
        ▼               ▼
  data/insight/     src/lib/ontology/loader.ts
  mock-events.json   (기존 YAML 379개 — 읽기만)
```

## 2. 데이터 모델

### 2.1 `InsightEvent` (`src/lib/insight-mockup/types.ts`)

```ts
export type EventCategory = 'thermal' | 'spc' | 'integrity';
export type EventSeverity = 'CRITICAL' | 'WARNING' | 'NORMAL';

export interface InsightEvent {
  id: string;                      // "evt-001"
  category: EventCategory;         // SLM 3분류 차용
  severity: EventSeverity;
  target_tag: string;              // YAML entity tag (예: "1101", "23C-IAC")
                                   // 빈 문자열이면 의도적 no-match
  target_label: string;            // 화면 표시용 ("SHV 수전 VCB 1101")
  metric: string;                  // "dT/dt" | "z_score" | "frozen_duration_min" ...
  unit: string;                    // "°C/min" | "σ" | "min"
  value: number;
  threshold: number;
  ts: string;                      // ISO8601
  narrative_hint: string;          // 시연용 한 줄 사람 설명
}
```

### 2.2 `InsightBundle` (조립 결과)

```ts
export interface BundleRelated {
  entity: EntityDetail;
  relation: string;           // "feeds" | "connects_to" | "controlled_by" ...
  direction: 'outgoing' | 'incoming';
  hop: 1 | 2;
  via?: string;               // 2홉일 때 경유 태그
}

export interface BundleEvidence {
  doc_id: string;             // data/documents.json과 매칭
  page: number;
  reason: string;
}

export interface InsightBundle {
  event: InsightEvent;
  status: 'matched' | 'no_match';
  entity: EntityDetail | null;          // no_match면 null
  related: BundleRelated[];              // 최대 8개, 2홉까지
  evidence: BundleEvidence[];            // entity.source_pages에서 유도
  semantic_summary: string;              // builder가 한두 문장으로 조립
}
```

## 3. Semantic Join 규칙 (builder 로직)

1. **직접 매칭**: `event.target_tag`로 `getEntityByTag()` 호출.
   - 실패 시 `status: 'no_match'` 반환, `related`·`evidence`는 빈 배열.
2. **1홉 관계 확장**:
   - `entity.relations[]` 중 `from == tag` → outgoing
   - `from != tag && to == tag` → incoming
   - 각 relation의 `to/from`을 태그로 잡아 `getEntityByTag()`로 엔티티 resolve.
3. **2홉 확장**: 1홉 결과 각각의 relations를 한 번 더 따라감.
   - 최대 8개로 컷. `via`에 1홉 태그 기록.
4. **근거 도면**: `entity.source_pages[]`를 `doc_id`와 페어로 변환.
   - `doc_id` 추정은 `src/app/api/chat/stream/route.ts`의 `guessDocId()`와 동일 규칙 재사용 (이식):
     - `_discipline_group` 기계 → `dwg-mech-001`
     - `_discipline_group` 전기단선도 → `dwg-elec-001`
     - `_discipline_group` 전기 → `dwg-elec-003`
     - 그 외 → `doc-001`
5. **`semantic_summary`**: 결정론적 템플릿
   ```
   "{event.severity} — {target_label}에서 {metric}={value}{unit} 관측
    (임계 {threshold}{unit}). 상류 {related[0].entity.name}와 연결됨."
   ```
   값이 없으면 부분만 채움.

## 4. API 스펙

### 4.1 `GET /api/insight/lab/bundles`

**쿼리**: `?id=evt-001` (선택)

**응답** (단건):
```json
{
  "bundle": { ...InsightBundle }
}
```

**응답** (목록, id 없을 때):
```json
{
  "events": [ { id, category, severity, target_label, narrative_hint, ts } ]
}
```

이벤트 요약만 반환해서 리스트 렌더링 가벼움. 상세는 클릭 시 별도 호출.

### 4.2 `POST /api/insight/lab/chat/stream`

**요청**:
```json
{
  "bundle_id": "evt-001",
  "message": "물리적 원인 후보가 뭘까?"
}
```

**응답**: `text/event-stream`. 기존 `/api/chat/stream`과 동일한 SSE 프로토콜.
- `data: {"token": "..."}` 반복
- `data: {"done": true, "evidence": [...]}` 종료

**프롬프트 조립**:

```
[System Instruction — 상수]
당신은 설비 도면·통계 분석 어시스턴트입니다.
아래 Insight Bundle을 근거로만 답변하세요.
추측 시 "확인 권장" 명시. 자동 제어 권고 금지. 한국어로 간결히.

[User Prompt]
<bundle>
event:
  id: evt-001
  category: thermal
  severity: CRITICAL
  target: 1101 (SHV 수전 VCB 패널 1101)
  measured: dT/dt = 4.8 °C/min (threshold 2.0)
  ts: 2026-04-18T14:35:00Z
  hint: "패널 내부 온도 급상승 — 환기 문제 가능성"

entity:
  tag: 1101
  name: SHV 수전 VCB 패널 1101
  discipline: ELECTRICAL
  specs: { vcb_rating: 3P 7.2kV 630A 520MVA, ... }

related (2-hop):
  - 1101 → feeds → TR-001 (1홉)
  - BLK-MOF → feeds → 1101 (1홉, incoming)
  - TR-001 → feeds → 1102 (2홉, via 1101)

evidence:
  - dwg-elec-001 p.5 — 1101 배치도
</bundle>

질문: {message}
```

**모드 분기** (기존 챗 라우트와 동일):
- `NEXT_PUBLIC_LLM_MODE=live` + `GOOGLE_API_KEY` 있을 때: Gemini 스트림
- 그 외: 결정론적 mock 응답 스트림 (사전 작성한 짧은 템플릿)

## 5. 훅 포인트 / 재사용

| 기존 자산 | 용도 | 수정 여부 |
|---|---|---|
| `src/lib/ontology/loader.ts` | `loadAllEntities()`, `getEntityByTag()` | 읽기만 |
| `src/lib/ontology/search.ts` | `searchEntities()` 필요 시 자유 키워드 보조 검색 | 읽기만 |
| `src/app/api/chat/stream/route.ts` | `guessDocId()` 규칙 — 이식 (복제) | 원본 보존 |
| `data/documents.json` | doc_id → drawing_ref 매핑 | 읽기만 |
| `src/components/PdfViewer.tsx` | 증거 카드 클릭 시 점프 대상 | 읽기만 |

## 6. 설계 결정 / 트레이드오프

- **챗 스트림 라우트 분리**: 기존 `/api/chat/stream`을 재활용하지 않고 복제. 이유: Bundle 프롬프트 조립이 단순한 free-text 질문과 달라 분기 증가시 유지 복잡. 시연용 격리 원칙.
- **Bundle on-the-fly 조립**: 사전 저장 파일 두지 않고 요청 시마다 builder 실행. YAML 로더에 캐시가 이미 있어 비용 미미. 데이터 일관성이 더 중요.
- **2홉으로 컷**: 3홉 이상 가면 R-Center 전체 계통이 흘러나와 노이즈. 회의 데모 가독성 우선.
- **no-match 표시**: Bundle 뷰가 "엔티티 찾을 수 없음 — 태그 {tag}"를 렌더하고 챗은 비활성. 한계 숨기지 않음.
- **mock 응답 템플릿**: 3~4개만 준비. 회의 자리가 오프라인/키 없음일 때도 최소 흐름 시연 가능.

## 7. 후속 확장 (지금은 안 함)

- Gemini 응답에서 언급된 태그를 정규식으로 추출해 증거카드 자동 부착
- Bundle → 간이 그래프 시각화 (d3/reactflow)
- 실 통계 수집 경로 (SLM 연결) — 별도 트랙에서 논의
