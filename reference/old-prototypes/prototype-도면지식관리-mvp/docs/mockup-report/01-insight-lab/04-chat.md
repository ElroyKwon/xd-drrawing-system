# 화면 · Insight Lab 화면 4 · AI 자유 질의 (챗)

**경로**: `/insight/chat`
**소속 트랙**: Insight Lab (서비스 2 · AI 인사이트)
**화면 분류**: 단일 컬럼 챗 인터페이스 + 근거 카드 · SSE 스트리밍

---

## 1. 화면 개요

![AI 자유 질의 · 빈 상태 (제안 질문 5개)](../screenshots/il-chat-empty.png)

이 화면은 알람·보고서 같은 **진입 맥락 없이** 사용자가 처음부터 자유롭게 AI에게 설비·도면에 대해 질문할 수 있는 단일 컬럼 챗 화면입니다. 좌우 분할이 아니라 **중앙 단일 컬럼**(`max-w-3xl mx-auto`)에 메시지를 쌓아가는 전형적인 챗봇 레이아웃이지만, AI의 답변마다 **근거 도면·문서 카드**와 **후속 질문 칩**이 함께 붙습니다.

빈 상태에서는 **AI 로고 + "AI 도면 질의" + 추천 질문 5개**가 중앙에 정렬되어 "뭘 물어봐야 하지?"를 해소합니다. 메시지를 보내면 SSE 스트리밍으로 토큰이 타자기처럼 채워지고, 완료 후 근거 카드와 후속 질문 칩이 아래에 붙습니다. 후속 질문 칩 클릭은 즉시 다음 턴으로 이어집니다.

화면 3(답변 상세)이 **알람으로부터 깊이 들어간 분석**이라면, 이 화면은 **플랫하게 자유롭게 물어보는** 공간입니다. "냉동기 CH-001 정상 운전 기준은?" 같은 사용자-발원(user-originated) 질의가 주 용도입니다.

---

## 2. 레이아웃 구조

```
┌───────────────────────────────────────────────────────────────────┐
│  AI 도면 질의                                     [새 대화 버튼]   │  ← Header
│  도면·매뉴얼 기반 답변 · 근거 문서 링크 제공                      │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│            ┌────────────┐                                         │
│            │  AI 로고   │        ← 빈 상태 (EmptyState)            │
│            └────────────┘                                         │
│          AI 도면 질의                                              │
│          설비·도면에 대해 자유롭게 질문하세요                       │
│                                                                    │
│          추천 질문                                                 │
│          ┌──────────────────────────────────────┐                 │
│          │ 냉동기 CH-001 정상 운전 기준은?      │                 │
│          │ 22.9kV 수전설비 VCB-001 ...          │                 │
│          │ 스프링클러 누수 ...                   │                 │
│          │ TR-001 변압기 ...                     │                 │
│          │ 전체 도면 목록을 보여줘                │                 │
│          └──────────────────────────────────────┘                 │
│                                                                    │
│  ── 메시지가 쌓일 때 ──                                           │
│                                    ┌── user 버블 (검정, 우측) ──┐│
│                                    │ 냉동기 CH-001 ...            ││
│                                    └──────────────────────────────┘│
│                                                                    │
│  [AI] ┌── AI 버블 ─ 마크다운 ──────────────────┐                 │
│       │ (스트리밍 토큰 + 깜빡이 캐럿)          │                 │
│       └─────────────────────────────────────────┘                 │
│                                                                    │
│       근거 도면·문서                                               │
│       ┌─ evidence ─┐ ┌─ evidence ─┐                              │
│       │ 썸네일·제목│ │ 썸네일·제목│                              │
│       │ 관련도 95% │ │ 관련도 91% │                              │
│       │ [도면 열기]│ │ [도면 열기]│                              │
│       └────────────┘ └────────────┘                              │
│                                                                    │
│       후속 질문                                                    │
│       [ chip ] [ chip ] [ chip ]                                  │
│                                                                    │
├───────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────┐  ┌──────┐   │
│  │ 도면·설비에 대해 질문하세요… (Enter 전송)       │  │ ▶   │   │
│  └────────────────────────────────────────────────┘  └──────┘   │
└───────────────────────────────────────────────────────────────────┘
```

| 영역 | 역할 |
|---|---|
| Header | 타이틀 + 부제 + (메시지 있을 때만) "새 대화" 리셋 버튼 |
| Messages | `max-w-3xl mx-auto` 중앙 컬럼, 위→아래 시간순, 자동 스크롤 |
| EmptyState | 첫 진입 시 로고 + 추천 질문 5개, 첫 메시지 전송 시 사라짐 |
| Input bar | textarea(rows=2) + 전송 버튼, 하단 고정, shrink-0 |

---

## 3. UX 상세 설명

### 3.1 Header

- 좌측: "AI 도면 질의" (`text-sm font-semibold`) + "도면·매뉴얼 기반 답변 · 근거 문서 링크 제공" 부제
- 우측: **"새 대화" 버튼** — `messages.length > 0`일 때만 표시. 클릭 시 `setMessages([])`로 전체 초기화
- 헤더는 `border-b border-slate-200 bg-white shrink-0` — 스크롤 시 상단 고정되지만 sticky는 없음 (flex 레이아웃)

### 3.2 Empty State (빈 상태)

- `messages.length === 0` 조건부 렌더
- 상단: `h-14 w-14` 검정 라운드 박스 안에 채팅 말풍선 아이콘
- 중앙: "AI 도면 질의" 굵은 라벨 + "설비·도면에 대해 자유롭게 질문하세요" 부제
- 하단: "추천 질문" 작은 대문자 라벨 + 5개 질문 버튼
- 각 질문 버튼: `rounded-xl border bg-white` 카드 형태, hover 시 `border-slate-400 bg-slate-50`
- 클릭 즉시 해당 질문으로 `send(q)` 실행 — **빈 입력창 부담 없이** 바로 대화 시작

### 3.3 추천 질문 5개 (하드코딩)

```
냉동기 CH-001 정상 운전 기준은?
22.9kV 수전설비 VCB-001 보호계전기 확인 방법은?
스프링클러 누수 발생 시 즉각 조치 절차는?
TR-001 변압기 권선 온도 이상 시 어떻게 하나?
전체 도면 목록을 보여줘
```

서로 다른 공종(기계·전기·소방·전기·메타)과 서로 다른 질문 성격(기준·절차·조치·매핑·메타)을 커버하도록 **의도적으로 다양화**되어 있습니다.

### 3.4 Message 구조

각 메시지는 로컬 `Message` 인터페이스:
```typescript
{ id, role: 'user'|'ai', text, evidence?, followups?, streaming? }
```

- **user 버블**: `justify-end`, `bg-slate-800 text-white`, `rounded-2xl rounded-tr-sm`로 우측 꼬리
- **AI 버블**: 좌측, AI 아바타(검정 원 "AI") + 흰 카드
  - 본문: `ReactMarkdown` + `remarkGfm` (테이블·체크리스트·코드블록 지원)
  - 스트리밍 중: `h-4 w-0.5 animate-pulse bg-slate-400` 깜빡이 캐럿
- AI 버블 아래 `space-y-3`로:
  - `근거 도면·문서` 라벨 + `EvidenceCard` 그리드 (sm:2열)
  - `후속 질문` 라벨 + `followups` 칩 (flex-wrap)

### 3.5 EvidenceCard (인라인 컴포넌트)

- 좌측 `h-14 w-14` 썸네일 박스
  - `docById[doc_id].drawing_ref`가 있으면 `/drawings/{ref}`를 `<Image>` (`next/image`, `unoptimized`)
  - 없으면 문서 아이콘 SVG fallback
- 우측 본문:
  - 상단 배지 줄: 타입 배지(`도면`/`매뉴얼`/`시방`, 파란 배경) + 태그 배지(`CH-001` 등, 회색) + 관련도(`관련도 95%`)
  - 제목 1줄 + snippet 2줄 clamp
  - 하단: "도면 열기 →" 파란 링크 (`/drawings/{doc_id}?page={page}`)

### 3.6 Follow-up 칩

- `rounded-full border px-3 py-1.5 text-xs` pill 형태
- 클릭 시 `onFollowup(q)` → `send(q)` → 새 user 메시지로 전송
- `flex-wrap gap-2`로 자동 줄바꿈

### 3.7 Input Bar

- `textarea`: `rows={2} resize-none rounded-xl border bg-slate-50`
  - Focus 시 `border-slate-400 bg-white`로 살짝 활성
  - 스트리밍 중(`busy`) disabled, 전송 후 `setTimeout(() => textareaRef.current?.focus(), 50)` 자동 재포커스
- 전송 버튼: `h-11 w-11 rounded-xl bg-slate-800` 정사각형, 비행기 아이콘
- 단축키:
  - `Enter`: 전송
  - `Shift+Enter`: 줄바꿈
- 입력이 비었거나 busy면 전송 버튼 `disabled` (opacity-40)

### 3.8 SSE 스트리밍 (핵심 기술)

엔드포인트: `POST /api/chat/stream`, body `{ message }`

```
fetch → res.body.getReader() → TextDecoder 루프
    ↓
버퍼에서 line 단위 파싱 ("data: {...}")
    ↓
chunk.token → setMessages로 AI 메시지의 text 누적
chunk.done → evidence, followups 수신 + streaming=false
chunk.error → 에러 메시지 표시
```

특징:
- 스트리밍 중 `busy=true`로 **이중 전송 차단**
- catch 블록에서 부분 수신된 text 보존 + "오류가 발생했습니다." 폴백
- `bottomRef.current?.scrollIntoView({ behavior: "smooth" })`로 새 메시지 올 때마다 자동 스크롤
- `messages` 의존성 `useEffect`로 구현

### 3.9 서버 측 모드 (route.ts)

- `NEXT_PUBLIC_LLM_MODE === 'live'` + `GOOGLE_API_KEY` 있으면: **Gemini 호출**
  - YAML 온톨로지에서 관련 엔티티 검색(`searchEntities`)
  - 온톨로지 컨텍스트 + mock evidence 결합해 프롬프트 생성
  - Gemini `generateContentStream` 토큰 단위 yield
  - 완료 시 온톨로지 기반 evidence + mock evidence 중복 제거 후 전송
- 아니면: **mock 스트림** (35ms 간격 토큰)
- 에러 시 mock 폴백 — 항상 **뭔가는 보이게**

---

## 4. 이 UX가 만드는 효과

| UX 결정 | 사용 경험에서의 변화 |
|---|---|
| EmptyState의 추천 질문 5개 | 빈 입력창 공포 제거 — 클릭 한 번으로 대화 시작 가능 |
| 추천 질문의 공종 다양화 | "이 AI가 뭘 할 수 있나" 폭을 한눈에 전시 |
| SSE 토큰 스트리밍 + 깜빡이 캐럿 | AI가 "지금 생각 중"이라는 시각 신호 — 긴 답변 대기의 불안 해소 |
| Markdown + GFM 렌더링 | 표·체크리스트·코드블록·강조로 **기술 답변의 구조**를 살림 |
| 근거 카드를 AI 버블 아래 별도 블록 | 주장(답변)과 근거(도면)이 시각적으로 분리되어 검증 가능성 강조 |
| 근거 카드의 썸네일 | 텍스트뿐인 다른 챗봇 대비 **도면 썸네일**이 신뢰도와 "실물감" 제공 |
| 후속 질문 칩의 인라인 배치 | 대화가 끝난 지점에 "다음 질문"이 대기 — 세션 연장 자연스러움 |
| "새 대화" 버튼 조건부 | 빈 상태에선 숨겨서 시선을 방해 않고, 필요할 때만 나타남 |
| `max-w-3xl mx-auto` 중앙 컬럼 | 넓은 모니터에서도 한 줄 길이가 가독성 범위 — "읽기 전용" 품질 |
| Enter/Shift+Enter 구분 | 전송과 줄바꿈이 명확히 분리 — 긴 질문 작성도 편리 |
| 전송 후 자동 포커스 복귀 | 연속 질문 시 마우스 이동 없이 계속 타이핑 |

---

## 5. 사용자 동작 흐름

| # | 액션 | 결과 | UX 의도 |
|---|---|---|---|
| 1 | `/insight/chat` 진입 | EmptyState 표시: AI 로고 + 추천 질문 5개 | "뭐 물어봐야 하지?" 해소 |
| 2 | 추천 질문 중 "냉동기 CH-001..." 클릭 | 즉시 `send()` 호출, user 버블 + 빈 AI 버블 생성, EmptyState 사라짐 | 원클릭 진입 |
| 3 | 스트리밍 시작 | AI 버블에 토큰이 타자기처럼 채워짐, 끝에 깜빡이 캐럿 | 살아있는 응답 |
| 4 | 스트리밍 완료 | 캐럿 사라짐, 아래에 근거 카드 + 후속 질문 칩 등장 | 정보 계층 확장 |
| 5 | 근거 카드 "도면 열기 →" 클릭 | `/drawings/{doc_id}?page=N` 새 맥락 진입 | AI 답변 → 원자료 검증 직통 |
| 6 | 후속 질문 칩 클릭 | 새 user 메시지로 자동 전송, 또 다른 AI 버블 스트리밍 | 자연스러운 꼬리 대화 |
| 7 | 하단 textarea에 직접 질문 + Enter | user 버블 + AI 스트리밍 | 자유 질의 |
| 8 | Shift+Enter | 줄바꿈 (전송 안 됨) | 긴 질문 작성 |
| 9 | 헤더 "새 대화" 클릭 | 전체 messages 초기화, EmptyState 복귀 | 세션 리셋 |
| 10 | 네트워크 오류 발생 | "오류가 발생했습니다." 메시지로 streaming=false 전환, 부분 수신은 보존 | 안전한 실패 |

---

## 6. 데이터·API 의존성

### 원천 데이터
- `data/documents.json` — `docById[doc_id]`로 썸네일(`drawing_ref`)·제목 조회
- `data/ontology/*.yaml` (live 모드 시) — 엔티티 검색용 온톨로지

### 참조하는 lib
- `@/lib/data-loader` — `docById` (문서 ID → DocSnippet 인덱스)
- `@/lib/insight/chat-mock` — `ChatEvidence` 타입 + mock 응답 생성 + 토크나이저
- `@/lib/ontology/search` (live 모드) — `searchEntities`, `buildOntologyContext`

### API 엔드포인트
- `POST /api/chat/stream` — SSE 엔드포인트
  - body: `{ message: string }`
  - response: `text/event-stream` (`data: {...}` 라인 시퀀스)
  - chunks: `{ token }`, `{ done, evidence, followups }`, `{ error }`

### 인라인 컴포넌트 (이 파일 내부 정의)
- `EmptyState` — 추천 질문 5개 렌더
- `ChatBubble` — user/AI 분기 렌더
- `EvidenceCard` — 근거 카드 (썸네일 + 메타 + 링크)

### 외부 컴포넌트/라이브러리
- `ReactMarkdown` + `remark-gfm` — 답변 마크다운 렌더
- `next/image` — 썸네일 렌더 (`unoptimized`)
- `next/link` — 도면 링크

### 실제 LLM 호출 여부
**환경 변수로 분기**. 기본은 mock. `NEXT_PUBLIC_LLM_MODE=live` + `GOOGLE_API_KEY` 설정 시 Gemini 호출 (`streamGemini`). 에러 시 mock 폴백.

### 상태 소유
- 모든 상태가 이 페이지 내부 `useState` 3개: `messages`, `input`, `busy`
- `useRef` 2개: `bottomRef` (자동 스크롤), `textareaRef` (재포커스)
- 화면 외부로 상태가 새어나가지 않음 — **완전 독립적인 챗 세션**

---

## 7. 이 화면이 기여하는 서비스 측면

| DKS 서비스 측면 | 이 화면이 맡는 역할 |
|---|---|
| **자연어 도면 질의** (서비스 2의 얼굴) | 알람·보고서 같은 구조화 진입 없이 **자유 발상 질문**을 받는 창구 |
| **Retrieval-Augmented Generation** | YAML 온톨로지(라이브) + mock evidence로 답변에 근거를 동반 |
| **공종 통합 Q&A** | 전기·기계·소방·메타 질문을 한 창구에서 받아 내부 검색·온톨로지로 분기 |
| **도면 심층 연결** | 답변 근거 카드의 "도면 열기 →"가 서비스 1 PDF 뷰어로 페이지 단위 직결 |
| **AI 체험의 진입 장벽 제거** | EmptyState의 추천 질문 5개가 **첫 질문 1초**를 가능케 함 |
| **실시간 스트리밍 UX** | SSE 토큰 전송으로 긴 답변도 첫 글자 지연 최소화 |
| **모드 전환 아키텍처** | mock/live 환경 변수 전환으로 **데모와 실 서비스 양립** |

**이 화면이 해결하지 않는 것**:
- **알람 맥락의 구조화 분석**은 화면 3(답변 상세)의 영역 — 이 화면은 진입 컨텍스트가 없는 자유 질의
- **대화 이력 저장·공유**는 없음 — 새로고침하면 세션이 사라짐
- **파일 업로드·이미지 첨부**는 없음 — 텍스트 대화만

---

## 8. 의견 수렴 포인트

### 스스로 본 보완 포인트

- **대화 이력 비영속**: 새로고침하면 전부 날아감. localStorage 저장 또는 서버 persistence 필요
- **추천 질문 5개 하드코딩**: 코드에 상수로 박혀 있어 관리가 어렵고, 사용자별 맞춤 추천 불가
- **이전 턴 history가 서버로 전달되지 않음**: `/api/chat/stream`이 `{ message }` 단건만 받음. **멀티턴 맥락이 서버에서 유실** — 화면 3의 ChatPanel과 달리 단발 Q&A만 제대로 됨
- **에러 UI가 빈약**: "오류가 발생했습니다." 한 줄로 끝 — 재시도 버튼·상세 에러 표시 없음
- **근거 카드 클릭 시 새 탭 여부 불명**: 같은 탭에서 이동 — 대화 맥락을 잃을 수 있음. `target="_blank"` 고려
- **모바일 반응형 미검증**: `max-w-3xl`이 작은 화면에서 자연스럽지만 입력창·카드 그리드가 좁아짐
- **접근성**: 스크린리더용 live region, 메시지 alt 텍스트 등 미비
- **후속 질문과 추천 질문의 중복**: 추천 질문은 static, 후속 질문은 AI 생성이지만 UI가 비슷함. 어느 쪽이 무엇인지 사용자 혼란 가능
- **취소(stop) 버튼 부재**: 스트리밍이 길어져도 중단 불가 (`AbortController`가 클라이언트엔 없음)

### 이해관계자 의견 기록란

<!-- 아래에 자유롭게 덧붙여 주십시오. 형식: `- **YYYY-MM-DD · 이름**: 의견` -->

-

---

## 9. 파일 레퍼런스

| 유형 | 경로 |
|---|---|
| 페이지 (모든 로직 포함, ~180줄) | `src/app/(s2)/insight/chat/page.tsx` |
| SSE API 엔드포인트 | `src/app/api/chat/stream/route.ts` |
| Mock 응답 + 토크나이저 | `src/lib/insight/chat-mock.ts` |
| 데이터 로더 (`docById`) | `src/lib/data-loader.ts` |
| 온톨로지 검색 (live 모드) | `src/lib/ontology/search.ts` |
| 문서 타입 | `src/lib/types.ts` |
| 전역 스타일 | `src/app/globals.css` |
| 상위 레이아웃 | `src/app/(s2)/layout.tsx` |

**관련 화면**: [화면 1 · 인사이트 홈](./01-hub.md) · [화면 2 · 알람 목록](./02-alarms.md) · [화면 3 · AI 답변 상세](./03-answers-detail.md)
