# W2 — 라우트 분해 + URL 규약 + AnswerCard (~36h)

> **선행**: W1 전체 완료
> **후행**: W3 전체

---

## W2-T1. `/search` `/drawings/[id]` 라우트 분해 + URL 규약 (~12h)

### 선행
W1-T4 (disciplineKo), W1-T5 (AppShell)

### 신규 파일
- `src/app/(s1)/search/page.tsx` — FilterBar + SearchBar + DrawingsList 래퍼
- `src/app/(s1)/drawings/[id]/page.tsx` — PdfViewer + MetadataPanel + RelatedEntitiesSidebar + AnnotationList + URL 파라미터 파서
- `src/components/MetadataPanel.tsx` — 도면번호·discipline·location·revision·last_updated
- `src/components/HighlightOverlay.tsx` — highlight 태그 시각화 (renderOverlay slot에 합성)
- `src/components/shell/Breadcrumb.tsx` — `?from=insight` 시 "← 인사이트로" 노출

### URL 규약 (스펙 §14.9 정확 준수)
```
/drawings/{doc_id}?page={n}&highlight={tag}&from=insight&query_id={id}
```

| 파라미터 | 처리 |
|---------|------|
| `doc_id` | 필수, 라우트 segment |
| `page` | `pageOverride` prop으로 PdfViewer에 |
| `highlight` | `renderOverlay`에서 HighlightOverlay 합성 |
| `from=insight` | Breadcrumb 노출 |
| `query_id` | Breadcrumb 클릭 시 `/insight/answers/{query_id}` 복귀 |

### 보존 6항목 격리 (필수)
- **PdfViewer 0 변경**. HighlightOverlay는 `renderOverlay` slot 합성:
  ```tsx
  renderOverlay={(s) => (
    <>
      <AnnotationLayer annotations={...} ... />
      <HighlightOverlay highlight={tag} surface={s} />
    </>
  )}
  ```
- HighlightOverlay도 `pointer-events-none` + 버튼 `pointer-events-auto` 패턴 복사

### 완료 기준
1. `/search?q=전기` → 9건 결과
2. 결과 클릭 → `/drawings/dwg-elec-001` 이동, PDF 렌더, MetadataPanel 표시
3. URL 직접 `/drawings/dwg-elec-001?page=3&highlight=VCB-001&from=insight&query_id=test` → 페이지 3 + VCB-001 강조 + Breadcrumb "← 인사이트로"
4. 주석 핀 찍기 → 새로고침 → 핀 유지 (LS 영속 회귀 0)
5. `npx tsc --noEmit` 통과

### 위험
- `useSearchParams` 사용 시 `<Suspense>` boundary 필요 (App Router)
- URL의 한글 highlight 태그 → URLSearchParams 자동 디코딩

---

## W2-T2. Insight 라우트 + 알람 패널 (~8h)

### 선행
W1-T5, W1-T3

### 신규 파일
- `src/app/(s2)/insight/page.tsx` — 홈 (RecentAlarmsWidget·RecentQueriesWidget·SuggestedQuestions placeholder)
- `src/app/(s2)/insight/alarms/page.tsx` — AlarmList + AlarmDetailDrawer
- `src/app/(s2)/insight/chat/page.tsx` — NaturalQueryInput + ConversationThread 스텁
- `src/app/(s2)/insight/answers/[id]/page.tsx` — AnswerPage 스텁
- `src/components/insight/AlarmList.tsx`
- `src/components/insight/AlarmDetailDrawer.tsx`
- `src/components/insight/AskAIButton.tsx`
- `src/lib/insight/types.ts` — AlarmEvent, InsightQuery, InsightAnswer, Evidence (스펙 §4.1)
- `src/lib/insight/data-loader.ts`
- `data/insight/alarms-fixed.json` (10건 가상)
- `data/insight/queries-examples.json` (20건)

### 가상 알람 10건 가이드
- 5 critical + 4 warning + 1 info
- 페르소나 시나리오 1·3·8 각 1건씩 매핑
- equipment_tag는 W1-T3 수동 매핑 풀과 동일 (VCB-001, AHU-3F-01, CHWP-001 등)

### 알람 샘플
```json
{
  "id": "alarm-001",
  "alarm_code": "CHW-T-HI-007",
  "alarm_name": "냉수 펌프 1호기 출구 고온",
  "equipment_tag": "CHWP-001",
  "severity": "critical",
  "triggered_at": "2026-04-17T02:14:00Z",
  "value": 15.3,
  "threshold": 12.0,
  "source_system": "bms"
}
```

### 완료 기준
1. `/insight/alarms` → 10건 리스트, severity 색상 (rose/amber/sky) 정확
2. row 클릭 → AlarmDetailDrawer 우측 슬라이드 (속성·threshold)
3. `[AI 물어보기]` 클릭 → `/insight/answers/<생성 id>`로 이동 (W2-T3에서 채움)

### 위험
- `useSearchParams` Suspense — Insight 라우트도 동일 처리

---

## W2-T3. AnswerCard + LLM 모킹 + SSE (~12h)

### 선행
W2-T2

### 신규 파일
- `src/components/insight/AnswerCard.tsx` — 5섹션 (QueryHeader · AnswerText · EvidenceList · StructuredPanel · FollowUpSuggestions)
- `src/components/insight/EvidenceList.tsx` — Evidence type별 분기
- `src/components/insight/StructuredPanel.tsx`
- `src/components/insight/FollowUpSuggestions.tsx`
- `src/lib/insight/llm-client.ts` — entry, mode 분기
- `src/lib/insight/mock-responses.ts` — 10 알람 × 1 답변 = 10 fixed JSON
- `src/lib/insight/url-builder.ts` — Evidence → `/drawings/...` URL (단위 테스트 가능)
- `src/app/api/insights/ask/stream/route.ts` — SSE Route Handler
- `src/app/api/insights/alarm/[id]/route.ts`
- `src/__tests__/url-builder.test.ts` — 단위 5 케이스

### url-builder.ts 시그니처
```ts
export function buildEvidenceUrl(
  ev: Evidence,
  queryId: string
): string | null {
  if (ev.type === "drawing_page") {
    const m = ev.reference.match(/^(.+?)\s*p\.(\d+)$/);
    if (!m) return null;
    const docId = lookupDocIdByDrawingNumber(m[1]);
    const page = m[2];
    const params = new URLSearchParams({
      page,
      from: "insight",
      query_id: queryId,
    });
    if (ev.tag) params.set("highlight", ev.tag);
    return `/drawings/${docId}?${params.toString()}`;
  }
  // ... other types
}
```

### llm-client.askInsight 시그니처
```ts
export async function* askInsight(
  query: InsightQuery,
  ctx?: { alarm?: AlarmEvent }
): AsyncIterable<string> {
  if (process.env.NEXT_PUBLIC_LLM_MODE === "mock") {
    const mockResp = mockResponses[query.context.alarm_id ?? "default"];
    for (const tok of tokenize(mockResp.answer_text)) {
      await sleep(50);
      yield tok;
    }
    return;
  }
  // mode=live는 W2-T4에서 채움
}
```

### 모킹 응답 형식 (스펙 §6.2)
```json
{
  "success": true,
  "data": {
    "answer_text": "...",
    "structured": {...},
    "evidence": [
      {
        "type": "drawing_page",
        "reference": "EE-01-001 p.1",
        "tag": "VCB-001",
        "snippet": "...",
        "link": "",  // url-builder가 채움
        "relevance_score": 0.92
      }
    ],
    "dual_engine": {...}
  },
  "meta": {...}
}
```

### 완료 기준
1. AlarmList → AskAIButton → AnswerPage → 토큰 스트리밍 첫 글자 <500ms (mock 50ms)
2. EvidenceList의 첫 항목 (drawing_page) 클릭 → 정확히 `/drawings/dwg-xxx?page=N&highlight=TAG&from=insight&query_id=...` 이동
3. 도면에서 Breadcrumb "← 인사이트로" 클릭 → 원 답변으로 복귀
4. SSE 끊김 (서버 재시작) 시 graceful — 마지막 도착 토큰만 보임
5. `vitest run` url-builder.test.ts 5 케이스 통과

### 위험
- SSE Route Handler에서 ReadableStream 생성 — Edge Runtime 권장 (Node Runtime은 close 이벤트 비표준)
- react-markdown + `[[VCB-001]]` 자동 링크 변환은 remark plugin 또는 정규식 후처리

---

## W2-T4. LLM 게이트 + Sonnet/Haiku 1차 (~4h)

### 선행
W2-T3

### 수정 파일
- `src/lib/insight/llm-client.ts` — `NEXT_PUBLIC_LLM_MODE` 분기 (mock/live), 모델 환경변수
- `.env.local` — 사용자 자체 작성

### 신규 파일
- `src/lib/insight/prompts/report-daily.ts`
- `src/lib/insight/prompts/alarm-context.ts`

### 프롬프트 핵심 룰 (스펙 §15.12)
- "근거 병기 강제" — 답변 텍스트에 `[근거: <reference>]` 인라인 표기
- "신뢰도 명시" — 0~1 numeric 출력
- "모르면 모른다" — confidence < 0.5 시 "확실치 않음. 담당자 확인 권장"
- "AI는 읽기 전용" — 자동 제어·쓰기 금지

### 완료 기준
1. `.env.local`에서 `NEXT_PUBLIC_LLM_MODE=live`로 변경 → 알람 답변이 실 Haiku 응답
2. mock 복귀 시 fixed JSON 응답
3. live 모드 evidence 필드 비어있으면 console.warn (가벼운 가드)
4. `npm run dev` 양 모드 모두 부팅

### 위험
- ANTHROPIC_API_KEY 누락 시 명확한 에러 메시지
- Edge Runtime에서 Anthropic SDK 사용 가능 여부 확인 — Node Runtime fallback 필요 시 route별 분리
