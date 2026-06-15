# 화면 · Insight Lab 화면 3 · AI 답변 상세 (알람 분석 + 멀티턴 대화)

**경로**: `/insight/answers/[id]` (쿼리스트링 `?alarm_id=...` 선택적)
**소속 트랙**: Insight Lab (서비스 2 · AI 인사이트)
**화면 분류**: 좌우 2분할 · 스트리밍 분석 + 대화 병행

---

## 1. 화면 개요

![알람 분석 상세 · 좌측 AI 분석 + 우측 챗](../screenshots/il-answers-detail.png)

이 화면은 알람(또는 임의 질의)에 대해 AI가 실시간 **1차 분석 카드**를 생성하고, 그 옆에서 사용자가 **멀티턴 대화**로 꼬리 질문을 이어갈 수 있도록 좌우 2분할된 워크스페이스입니다. 알람 목록(화면 2)에서 "AI에게 물어보기"를 누르면 도달합니다.

좌측은 **스트리밍 마크다운 답변 + 근거 도면·문서 카드 + 구조화 분석 패널 + 후속 질문 제안** 의 4-부 구성으로, 한 번에 모든 맥락을 조망하도록 설계되어 있습니다. 우측은 **챗 말풍선형 인터페이스**로 후속 질문을 받아 SSE 스트리밍으로 답변합니다. 좌측의 "후속 질문 제안" 칩을 클릭하면 **우측 채팅창에 자동 전송**되어 두 패널이 하나의 연결된 작업 공간으로 동작합니다.

이 화면의 핵심 철학: **분석 결과는 읽는 것, 대화는 이어가는 것**. 좌측은 정제된 보고서, 우측은 즉석 토론의 장으로 역할을 분리했습니다.

---

## 2. 레이아웃 구조

```
┌───────────────────────────────────────────────────────────────────┐
│  ← 알람 목록 │ 냉수 펌프 1호기 출구 고온           CHWP-001       │  ← 브레드크럼
├───────────────────────────────┬───────────────────────────────────┤
│                                │                                   │
│  좌측 · 58%                    │  우측 · 42%                       │
│  (스크롤 가능 · bg-slate-50)   │  (ChatPanel · bg-slate-50)        │
│                                │                                   │
│  ┌─ AI 분석 답변 ────────────┐│  ┌─ AI 대화 ────────────────────┐ │
│  │ AI 알람 이름 · queryId    ││  │ 분석 결과를 근거로 추가 질문 │ │
│  │          [분석 중…/완료]   ││  ├───────────────────────────────┤ │
│  └───────────────────────────┘│  │                               │ │
│                                │  │ (빈 상태: 후속 질문 클릭 안내)│ │
│  ┌─ AnswerText ──────────────┐│  │                               │ │
│  │ 마크다운 스트리밍 +       ││  │  [user 버블 ─ 우측]           │ │
│  │ 깜빡이 캐럿               ││  │  [AI 버블 ─ 좌측, 마크다운]   │ │
│  └───────────────────────────┘│  │  [스트리밍 캐럿]              │ │
│                                │  │                               │ │
│  ┌─ EvidenceList ────────────┐│  ├───────────────────────────────┤ │
│  │ 근거 도면·문서 카드       ││  │ textarea + 전송 버튼          │ │
│  └───────────────────────────┘│  └───────────────────────────────┘ │
│                                │                                   │
│  ┌─ StructuredPanel ─────────┐│                                   │
│  │ 구조화 분석 (원인·조치)   ││                                   │
│  └───────────────────────────┘│                                   │
│                                │                                   │
│  ┌─ FollowUpSuggestions ─────┐│                                   │
│  │ 후속 질문 제안 (chip)     ││  ←── (우측 챗에 자동 전송)         │
│  └───────────────────────────┘│                                   │
└───────────────────────────────┴───────────────────────────────────┘
```

| 영역 | 너비 | 역할 |
|---|---|---|
| 상단 브레드크럼 | 풀폭, ~48px | 알람 목록 복귀 + 알람 이름·설비 태그 |
| 좌측 답변 | 58% | AnswerCard (헤더·답변·근거·구조화·후속) 세로 스택 |
| 우측 챗 | 42% | ChatPanel (말풍선·스트리밍·입력창) |

양측 모두 독립 스크롤. 브레드크럼은 shrink-0으로 고정.

---

## 3. UX 상세 설명

### 3.1 상단 브레드크럼

- 좌측: "← 알람 목록" 텍스트 링크 (`text-xs text-slate-400`, hover 시 slate-700)
- 파이프 구분자(`|`)와 함께 **알람 이름** 노출 (`text-xs font-medium`)
- 우측 끝(`ml-auto`): 설비 태그 monospace 회색 표시 (`VCB-001` 같은)
- 배경 `bg-white/80 backdrop-blur-sm`으로 **스크롤 컨텐츠 위에 떠 있는 느낌**
- `alarm_id` 쿼리 없이 진입한 경우 알람 관련 표시는 생략 (알람 이름·태그 숨김)

### 3.2 좌측 패널 — AnswerCard 5-부 구성

#### 3.2.1 QueryHeader
- AI 아바타 (`bg-slate-800` 원, "AI" 흰 글씨)
- "AI 분석 답변" 타이틀 + 메타(`{알람 이름} · {queryId monospace}`)
- **우측 상단 상태 표시**:
  - `streaming`: 펄스 emerald 도트 + "분석 중…"
  - `done`: 초록 "완료"
  - `error`: amber "부분 수신" (부분 스트림이라도 보존)

#### 3.2.2 AnswerText
- `rounded-xl border bg-white` 카드 안에 **ReactMarkdown + remarkGfm**으로 렌더
- 스트리밍 중에는 `h-4 w-0.5 animate-pulse bg-slate-400` **캐럿**이 끝에 깜빡임
- 에러 시 `bg-amber-50 text-amber-700` 경고 박스가 본문 아래 추가

#### 3.2.3 EvidenceList (근거 도면·문서)
- 수신한 `evidence[]`를 그리드로 렌더
- 각 카드: 썸네일 + 타입 배지(도면/매뉴얼/시방) + 태그 + 관련도(%) + snippet + "도면 열기 →"
- 클릭 시 해당 도면의 특정 페이지로 직결 (`/drawings/{doc_id}?page=N`)

#### 3.2.4 StructuredPanel (구조화 분석)
- 답변과 별도로 **JSON 구조 데이터**가 오면 렌더: 원인 후보 리스트 · 점검 체크리스트 · 조치 절차 등
- `bg-slate-50` 패널로 시각적으로 본문과 구분

#### 3.2.5 FollowUpSuggestions (후속 질문 제안)
- 답변 완료 시 3~5개의 **후속 질문 칩** 수신
- 각 칩 클릭 시 **우측 ChatPanel로 자동 전송** — `onFollowUpSelect(q)` → `setPendingQuestion(q)` → ChatPanel `useEffect`가 감지해 `sendMessage` 호출
- 좌우 패널이 이 prop 하나로 연결되어 있음이 핵심 설계

### 3.3 스트리밍 메커니즘

- 진입 즉시 `fetch('/api/insights/ask/stream', { body: { alarmId } })` POST
- `text/event-stream` 응답을 `getReader()` + `TextDecoder`로 파싱
- 각 `data: {...}` 라인이 `{ token }`, `{ done, evidence, structured, followups }`, `{ error }` 중 하나
- `AbortController`로 페이지 이탈 시 정리 (cleanup)
- 토큰 단위로 `setText((prev) => prev + chunk.token)` 누적 → 타자기 효과

### 3.4 우측 패널 — ChatPanel

- 상단 헤더: "AI 대화" + "분석 결과를 근거로 추가 질문하세요"
- 메시지 영역:
  - 빈 상태: 중앙 정렬 "좌측 분석 결과의 후속 질문을 클릭하거나 직접 질문을 입력하세요" 2줄 안내
  - user 메시지: 우측 정렬, `bg-slate-800` 검정 버블, 흰 글씨, `rounded-br-sm`로 꼬리
  - assistant 메시지: 좌측 정렬, AI 아바타 + 흰 카드 버블, 마크다운 렌더, 스트리밍 중 깜빡이 캐럿
  - 새 메시지 도착 시 `scrollIntoView({ behavior: "smooth" })`로 자동 스크롤
- 입력창: `rows={2}` textarea + 전송 버튼
  - Enter 전송 / Shift+Enter 줄바꿈
  - 스트리밍 중에는 `disabled`로 이중 전송 방지
- API 엔드포인트: `/api/insights/chat/stream` (SSE, history와 contextSummary 동반)

### 3.5 좌→우 연결 흐름 (핵심)

1. 좌측 FollowUpSuggestions에서 칩 클릭
2. `AnswerPageClient`의 `setPendingQuestion(q)` 실행 (상태 승급)
3. ChatPanel의 `useEffect([pendingQuestion])`가 감지 → `sendMessage(q)` + `onPendingConsumed()`
4. 우측 입력창이 자동으로 질문 전송, 스트리밍 답변 수신

이 설계로 **"답변 읽기 → 꼬리 질문 이어가기"가 같은 화면 안에서 원클릭으로 연결**됩니다.

---

## 4. 이 UX가 만드는 효과

| UX 결정 | 사용 경험에서의 변화 |
|---|---|
| 좌우 2분할 고정 | 답변(참조 자료)과 대화(작업 공간)이 동시에 보임 — 스크롤로 사라지지 않음 |
| SSE 토큰 스트리밍 | "지금 AI가 생각하고 있다"는 감각 — 빈 화면 대기의 불안 제거 |
| 깜빡이 캐럿 | 스트리밍이 시각적으로 살아있음을 명시 |
| 근거 카드를 답변 아래 분리 | 주장(답변)과 근거(도면)이 시각적으로 구분되어 **검증 가능성** 강조 |
| 근거 카드의 관련도 % | AI가 얼마나 확신하는지 숫자로 제시 — 인간 판단의 보조 |
| 후속 질문이 **우측으로 자동 흘러가는** 설계 | "이어서 물어볼 게 있을까?" 고민 없이 칩 하나로 대화 확장 |
| 우측 챗 빈 상태의 2줄 안내 | 첫 방문 시 "여긴 뭐 하는 곳?" 혼란 방지 |
| 좌우 독립 스크롤 | 답변의 아래쪽(근거·구조화)을 보면서 대화 위쪽을 참조 가능 |
| 에러 시 "부분 수신" 상태 유지 | 네트워크 불안정에도 받은 만큼은 살려 재시도 유도 |
| `queryId` monospace 표시 | 버그·피드백 시 식별자로 사용 가능 (운영 편의) |

---

## 5. 사용자 동작 흐름

| # | 액션 | 결과 | UX 의도 |
|---|---|---|---|
| 1 | 알람 드로어의 "AI에게 물어보기" 클릭 | `/insight/answers/{queryId}?alarm_id={id}` 진입 | 알람 → AI로 의도 전환 |
| 2 | 진입 즉시 | 좌측 QueryHeader가 "분석 중…", AnswerText 토큰 스트리밍 시작 | 로딩 시간이 **보이는** UX |
| 3 | 토큰이 차오르는 동안 브레드크럼 확인 | 알람 이름·설비 태그가 상단에 상주 | 맥락이 사라지지 않음 |
| 4 | 스트리밍 완료 (`done`) | 근거 카드, 구조화 패널, 후속 질문 칩이 순서대로 나타남 | 정보 계층이 시간으로 전개 |
| 5 | 근거 카드 "도면 열기 →" 클릭 | `/drawings/{doc_id}?page=N` 새 맥락으로 이동 | 답변 → 원자료 검증 직통 |
| 6 | 후속 질문 칩 "응축 압력 초과 시 조치는?" 클릭 | 우측 ChatPanel에 자동 전송, 스트리밍 답변 | 대화 흐름이 끊기지 않음 |
| 7 | 우측 입력창에 직접 질문 타이핑 + Enter | user 버블 + AI 버블이 스트리밍 | 자유 추가 질의 |
| 8 | 우측 대화 여러 턴 진행 | history가 서버로 전달되어 맥락 유지 | 멀티턴 일관성 확보 |
| 9 | 브레드크럼 "← 알람 목록" 클릭 | 알람 리스트로 복귀, AbortController cleanup | 이탈 경로 명확 |

---

## 6. 데이터·API 의존성

### 원천 데이터
- `data/insight/alarms-fixed.json` — 알람 정보 조회 (`alarmById` 인덱스)
- `src/lib/insight/mock-responses.ts` — mock 답변 템플릿 + evidence + structured + followups

### 참조하는 lib
- `@/lib/insight/data-loader` — `alarmById`
- `@/lib/insight/types` — `Evidence`
- `@/lib/insight/mock-responses` — `MockResponse` 타입
- `@/lib/insight/llm-client` — `ChatMessage` 타입 (history 전송용)

### 사용하는 컴포넌트
- `@/components/insight/AnswerCard` — 좌측 전체 (5-부 구조)
- `@/components/insight/EvidenceList` — 근거 카드 그리드
- `@/components/insight/StructuredPanel` — 구조화 분석
- `@/components/insight/FollowUpSuggestions` — 후속 질문 칩
- `@/components/insight/ChatPanel` — 우측 전체

### API 엔드포인트
- `POST /api/insights/ask/stream` — 좌측 AnswerCard 스트리밍 (alarmId → SSE)
- `POST /api/insights/chat/stream` — 우측 ChatPanel 스트리밍 (question + history → SSE)

### 실제 LLM 호출 여부
**모드 전환**. `NEXT_PUBLIC_LLM_MODE=live` 환경 변수 + `GOOGLE_API_KEY` 설정 시 Gemini 호출, 아니면 mock 응답 스트리밍. 에러 시 mock 폴백.

### 상태 소유
- `AnswerPageClient.tsx`가 `pendingQuestion` 상태 소유 — 좌→우 연결의 핵심 pivot
- 좌측 `AnswerCard`와 우측 `ChatPanel`은 각자 자기 스트리밍 상태를 독립 관리

---

## 7. 이 화면이 기여하는 서비스 측면

| DKS 서비스 측면 | 이 화면이 맡는 역할 |
|---|---|
| **이상 원인 분석 자동화** (서비스 2 핵심) | 알람 진입 즉시 원인·조치를 스트리밍 답변으로 제시 |
| **근거 기반 AI (Retrieval-Augmented)** | 답변에 도면·매뉴얼·시방 근거 카드를 동반해 검증 가능성 확보 |
| **도면 역참조** | 근거 카드의 "도면 열기 →"가 서비스 1(PDF 뷰어)로 깊은 링크 — 서비스 간 경계 해소 |
| **멀티턴 대화형 AI** | 우측 ChatPanel이 history 전달로 대화 맥락 유지 — 단발 질의 이상의 깊이 |
| **구조화 인사이트 + 자연어 답변의 결합** | Markdown 자연어 + JSON 구조 패널을 동시 제공 — 읽기용과 참조용 분리 |
| **실시간 스트리밍 UX** | SSE 토큰 단위 전송으로 첫 글자 지연(TTFT) 최소화 |

**이 화면이 해결하지 않는 것**: 알람이 없는 **탐색적 자유 질의**는 화면 4(`/insight/chat`)의 영역. 보고서 작성은 `/insight/reports`. 이 화면은 "알람에서 출발한 원인 규명"에 특화.

---

## 8. 의견 수렴 포인트

### 스스로 본 보완 포인트

- **좌측 스크롤과 우측 스크롤의 분리**가 어색할 수 있음 — 좌측 답변이 길어지면 근거 카드를 보기 위해 아래로 내려가야 함. Sticky toc(목차) 검토 필요
- **근거 카드의 썸네일**: 일부는 fallback 아이콘만 표시. 실 도면 이미지가 들어오면 설득력 상승
- **우측 ChatPanel 입력창이 좌측 스트리밍 중에도 활성**: 동시 스트림이 두 개 일어나도 UI는 견디지만, 사용자 멘털 모델에는 혼란이 있을 수 있음
- **`contextSummary` prop 미사용**: `ChatPanel`이 받는 `contextSummary`는 이 화면에서는 넘기지 않음 — 좌측 분석 요약을 우측 대화에 자동 주입하면 더 똑똑해질 수 있음
- **후속 질문이 같은 답변에 고정**: 대화가 이어져도 좌측 후속 질문은 초기 답변의 것만 유지 — 마지막 대화에서의 follow-up을 좌측에도 반영하려면 추가 설계 필요
- **모바일**: 2분할(58:42)이 협소한 화면에서 둘 다 좁아짐. 모바일에서는 탭 전환(분석|대화) 제안
- **답변 저장·공유 부재**: 답변 URL은 queryId로 유일하지만 실제 저장은 안 됨. 재방문 시 다시 스트리밍

### 이해관계자 의견 기록란

<!-- 아래에 자유롭게 덧붙여 주십시오. 형식: `- **YYYY-MM-DD · 이름**: 의견` -->

-

---

## 9. 파일 레퍼런스

| 유형 | 경로 |
|---|---|
| 페이지 진입점 | `src/app/(s2)/insight/answers/[id]/page.tsx` |
| 클라이언트 컨테이너 | `src/app/(s2)/insight/answers/[id]/AnswerPageClient.tsx` |
| 좌측 답변 카드 | `src/components/insight/AnswerCard.tsx` |
| 근거 리스트 | `src/components/insight/EvidenceList.tsx` |
| 구조화 패널 | `src/components/insight/StructuredPanel.tsx` |
| 후속 질문 칩 | `src/components/insight/FollowUpSuggestions.tsx` |
| 우측 챗 패널 | `src/components/insight/ChatPanel.tsx` |
| 분석 스트리밍 API | `src/app/api/insights/ask/stream/route.ts` |
| 대화 스트리밍 API | `src/app/api/insights/chat/stream/route.ts` |
| Mock 응답 | `src/lib/insight/mock-responses.ts` |
| LLM 클라이언트 타입 | `src/lib/insight/llm-client.ts` |
| 데이터 로더 | `src/lib/insight/data-loader.ts` |

**관련 화면**: [화면 1 · 인사이트 홈](./01-hub.md) · [화면 2 · 알람 목록](./02-alarms.md) · [화면 4 · AI 자유 질의](./04-chat.md)
