# S8 — XD 도면 어시스턴트 (AI 챗) 설계 + 로드맵  [STATUS: v2 — 백엔드 계약 FROZEN · 프론트/온톨로지 검수 게이트(§9, HUMAN_GATE)]

> ⚠️ **2026-07-01 4렌즈 설계 검수 완료 — §9 참조.** 백엔드 격리(별도 8001·import0·diff0)·OPEN-1(a)는 검증됨. 그러나 (1) 온톨로지 바인딩 산출물 실종=**GATE-1**, (2) 프론트 "BuildShell 단일 접점"은 허상(실제 App.tsx+BuildSheetsView.tsx)=**GATE-2**, (3) owner 프라이버시 한계=**GATE-3** → `HUMAN_GATE.md` 세션12 결정 전까지 프론트/온톨로지 부분은 미확정. §9가 아래 본문의 상충 서술(BuildShell·`/api/files`)을 정정·우선한다.

> buildout-loop의 AI 단계(S8) 설계. LOOP.md Done-When "XD 고유(온톨로지) + AI 분석"의 구체화.
> **v1(초안)은 통합형**이었으나, 사용자 지시로 **완전 격리형 사이드카(sidecar)** 로 재설계(v2, 2026-07-01).
> **AI(LLM) = HUMAN_GATE.** 이 문서는 공동설계로 8개 결정을 확정한 상태이며, 승인 후 per-milestone 메타프롬프트(`prompts/10~`)를 FROZEN하고 구현에 들어간다.

## 0. 확정 결정 (공동설계)

### 0-A. 핵심 4결정 (2026-07-01, 유지)
1. **그라운딩 = Tool-use(함수 호출).** LLM이 큐레이션된 **읽기 전용** 함수를 호출해 실데이터로 답한다. 환각 없이 프로젝트 실데이터에 그라운딩. (RAG·Text-to-TypeQL 배제.)
2. **제공자 = 둘 다(기본 로컬 전환).** provider 추상화로 로컬(Ollama)+클라우드(GPT·Gemini·Claude) 지원. **기본 = 로컬(반출 0)**, 클라우드는 **대화별 opt-in + egress 동의 게이트**(HUMAN_GATE).
3. **대화 저장 = 프로젝트별 + 사용자별.** 각 대화는 `(현재 사용자, 현재 프로젝트)`에 귀속. current_user/project는 **8000 `/api/auth/me`·프로젝트 API를 HTTP로 조회**해 계승.
4. **v1 범위 = 읽기 Q&A + 딥링크.** 조회·검색·요약 + 답변 속 UI 딥링크. **쓰기/액션(이슈 생성·마크업 등)은 후속(S9).**

### 0-B. 격리 4결정 (2026-07-01 v2, 신규 — "기존과 별개로 동작")
5. **백엔드 = 별도 프로세스/포트(8001).** AI 챗은 독립 FastAPI 앱으로 기동(기본 `127.0.0.1:8001`). 기존 8000은 **데이터 소스로만** 참조. 프로세스·포트·배포·기동 스크립트 전부 분리. 8001을 죽여도 8000 본체는 완전 정상.
6. **데이터 접근 = 8000 공개 HTTP API만.** 오케스트레이터의 툴은 8000의 공개 REST(`/api/search`·`/api/drawings`·`/api/issues`·`/api/files`…)를 **일반 클라이언트처럼 read-only 호출**. 기존 backend 모듈(`store.py` 등) **import 0줄**. 앱을 외부 데이터원처럼 취급.
7. **프론트 = 격리 폴더 + 셸 1곳 마운트 + 킬스위치.** `src/ai/` 독립. **유일한 기존-파일 접점 = `BuildShell`**(flag 가드 마운트 1줄 + 딥링크 이벤트 브리지 리스너). **기존 뷰(Sheets/Issues/Files) 무수정.** feature flag로 완전 on/off, `src/ai/`+BuildShell 2줄 제거 시 기존과 100% 동일.
8. **완료 기준 = 강한 격리 불변식(킬스위치 검증).** AI를 꺼도/지워도 기존이 바이트 동일하게 동작함을 **acceptance 항목으로 강제**(§1 e~g). "별개 동작"을 채점 가능한 기준으로 못박음.

### 0-C. 확정된 결정 (2026-07-01 승인)
- **OPEN-1 — 장비/온톨로지 그라운딩 깊이 → (a) 순수 클라이언트 확정.** v1 그라운딩 = 8000이 이미 노출한 공개 API(시트 제목/공종/타이틀블록·이슈 텍스트·파일/폴더·검색)만. "변전실 장비" 류는 **텍스트 검색으로 근사**, 진짜 장비-엔티티 그래프 Q&A는 **v1 범위 밖**(§8 Out of scope, S8.5 이후 8000 온톨로지 read 라우트 신설 시 후속). **결과: 8000 완전 무수정, 결정8 불변식 그대로 유지**(신규 라우트 0).

## 1. 목표 / Done-When

우측 도킹형 대화 어시스턴트로, 어느 화면에서든 열려 **프로젝트 실데이터(8000 공개 API)에 그라운딩된** 자연어 Q&A를 제공한다. 기존 대화를 이어가거나 새로 시작할 수 있고, 대화는 사용자·프로젝트별로 영속한다. **그리고 이 전체가 기존 앱과 완전히 분리되어, 꺼도/지워도 기존 동작에 무영향이다.**

**완료 정의(v1)**
- **(a)** 우측 패널을 열면 현재 프로젝트의 내 대화 목록이 뜨고, 선택해 이어가거나 "새 대화"를 시작한다.
- **(b)** "이 프로젝트에 전기 도면 몇 장이야?" / "EE-01-006 이슈 보여줘" / "plan 관련 파일" 같은 질문에 **실데이터(8000 공개 API) 기반**으로 답하고, 답변 속 시트/이슈/파일이 **딥링크**로 클릭 이동한다. *(장비-그래프 Q&A는 OPEN-1 (a) 기준 v1 범위 밖.)*
- **(c)** 기본은 로컬 LLM(반출 0). 클라우드 선택 시 egress 동의 후 동작.
- **(d)** 대화·메시지가 새로고침에도 복원. 콘솔 0.
- **(e) [격리]** AI flag **OFF** 시 기존 `npm run build`·`npm test` **98**·backend `pytest` **78**이 그대로 GREEN, 기존 backend `routes_*`·`store.py`·`_*.json` **git diff = 0**.
- **(f) [격리]** 8001 프로세스 정지/삭제 시 기존 8000 앱이 완전 정상(무의존).
- **(g) [격리]** 8001 코드가 기존 backend 모듈을 **import하지 않음**(정적 grep 확인). 데이터는 8000 공개 HTTP만.

> (a)~(d) = **제품(product)** Done-When, (e)~(g) = **격리(product이자 검증 가능)** Done-When. 프로세스 Done-When(3렌즈·reconcile 수행)은 PROGRESS.md에서 별도 추적.

## 2. 아키텍처 — 격리형 사이드카

```
┌─ 프론트 (하나의 SPA) ───────────────────────────────────────────┐
│  기존 Build 앱 뷰 (Sheets/Issues/Files…)  ── src/build/* (무수정) │
│  src/ai/  ★신규 격리                                             │
│    ChatDrawer/  api/chat.ts (AI_BASE=8001)                       │
│  BuildShell.tsx ── 유일 접점: <ChatDrawer flag/> + 딥링크 브리지  │
└──────────────┬──────────────────────────┬──────────────────────┘
   HTTP 8000   │ (기존 데이터)             │ HTTP 8001 (챗 SSE)
               ▼                          ▼
┌─ 8000 기존 앱 (무수정) ─┐   ┌─ 8001 AI 챗 앱 ★신규 독립 프로세스 ─┐
│ FastAPI + store.py     │   │ backend/ai/  (기존 import 0)         │
│ routes_search/drawing/ │◄──┤  main_ai.py       FastAPI 앱        │
│ issue/files/auth       │HTTP│  routes_chat.py   대화·메시지·SSE   │
│ _*.json / TypeDB       │read│  chat.py          tool-use 루프     │
└────────────────────────┘only│  tools.py         8000 HTTP 클라이언트│
                              │  providers/{ollama,openai,          │
                              │             gemini,claude,mock}.py  │
                              │  ai_store.py      _ai_data/*.json   │
                              │  tests/                             │
                              └─────────────────────────────────────┘
```

### 계층 ① 제공자 추상화 (`backend/ai/providers/`)
- 통합 인터페이스: `chat(messages, tools, model_cfg) -> stream[{delta|tool_call|usage}]`. 툴 호출 포맷을 제공자별 API로 매핑.
- 어댑터: `OllamaProvider`(로컬 기본), `OpenAIProvider`, `GeminiProvider`, `ClaudeProvider`, **`MockProvider`**(결정적 테스트용). 모델 레지스트리(provider→model_id·capabilities·needs_key·egress).
- **egress 게이트**: 클라우드 provider 선택 = 도면 데이터 외부 전송 → 대화별 1회 동의 + API 키(8001 로컬 `.env`) 필요. 미동의/키 없음 → 차단·안내. 로컬은 무조건 허용.
- 모델 ID는 구현 시점 레지스트리로 핀. API 키는 **8001 전용 `.env`**(커밋 금지). 8000은 키를 모른다.

### 계층 ② 대화 영속 (`backend/ai/ai_store.py`, 자체 저장소)
- **기존 DrawingStore와 무관한 독립 스토어.** 저장 위치 `backend/ai/_ai_data/`(기존 `_*.json` 불변).
- `conversation`: `conversation_id, project_name, member_id(owner), title, provider, model_id, egress_ok, created_at, updated_at`.
- `message`: `message_id, conversation_id, role[user|assistant|tool|system], content, tool_calls?, tool_results?, usage?, created_at`.
- JSON SoT(`_conversations.json`/`_messages.json`). 목록 필터 = `(project_name, member_id)`. 제목 = 첫 사용자 메시지 요약(또는 LLM 짧은 제목).
- **격리 불변식**: owner(member_id)는 8000 `/api/auth/me` 응답에서 취득. 사용자 A는 B의 대화를 못 본다(8001이 scope 강제). TypeDB 미러는 두지 않음(완전 분리).

### 계층 ③ AI 오케스트레이션 (`backend/ai/chat.py`)
- Tool-use 루프: (1) 히스토리+시스템프롬프트+툴정의 로드 → (2) provider.chat 스트리밍 → (3) 툴 호출 요청 시 **읽기전용** 실행(=8000 HTTP GET)→결과 주입→반복(최대 N=5) → (4) 최종 답 스트림·영속.
- 시스템 프롬프트: "너는 XD 도면관리 어시스턴트. 답은 반드시 툴 결과에 근거하고, 시트/이슈/파일은 `[[type:id]]` 형태로 인용해 딥링크되게 하라. 모르면 모른다고 하라."

### 계층 ③' 툴 카탈로그 = 8000 HTTP 클라이언트 (`backend/ai/tools.py`, 읽기 전용)
> 각 툴은 **8000 공개 API를 GET**해 구조화 JSON + 안정 ID(딥링크용)를 반환. 기존 backend 함수 직접호출 **없음**.
- `get_project_summary(project)` — `/api/drawings`+`/api/issues` 집계(챗측 계산, homeStats 로직 이식이 아니라 응답 집계).
- `search(project, query)` — `GET /api/search` 교차 검색.
- `list_sheets(project, discipline?)` · `get_sheet(sheet_id)` — `GET /api/drawings`(+타이틀블록/공종).
- `list_issues(project, status?, category?)` · `get_issue(issue_id)` — `GET /api/issues`.
- `list_files(project, folder?)` — `GET /api/files`(폴더/버전).
- *(OPEN-1 (b) 채택 시)* `query_ontology(...)` — `GET /api/ontology` 신설분 질의.
- httpx 클라이언트 1개(베이스 URL = `XD_BACKEND_BASE`, 기본 8000), 타임아웃·에러 우아 처리.

### 계층 ④ 챗 UI (`src/ai/`, 우측 도킹)
- `ChatDrawer` — 우측 도킹·토글·전 화면. **`BuildShell`에서 flag(`VITE_AI_CHAT` 등) 가드로 1곳 마운트.** flag off면 렌더 0.
- `ConversationList` — 현재 프로젝트의 내 대화 목록·선택·"새 대화".
- `ChatThread` — 메시지 스트림(markdown·스트리밍·툴 진행 "도면 조회 중…")·**딥링크 칩**.
- `ChatComposer` — 입력·**제공자/모델 선택기**(클라우드엔 egress 배지)·전송.
- `src/ai/api/chat.ts` — `AI_BASE=http://127.0.0.1:8001`. 대화/메시지/스트림 API.
- **딥링크 브리지**: 칩 클릭 → `window.dispatchEvent(CustomEvent('xd:navigate',{detail:{type,id}}))`. **`BuildShell`이 이 이벤트를 구독**해 기존 네비게이션(openSheet/이슈탭/폴더)을 호출. → 기존 뷰 파일 무수정, 접점은 BuildShell 하나.

### 재사용 vs 신규 (격리 원칙)
- **신규(격리)**: `backend/ai/*` 전부, `src/ai/*` 전부, 8001 기동 스크립트, `_ai_data/`, 8001 `.env`.
- **기존 접점(최소 2곳)**: `BuildShell.tsx`(flag 마운트 1줄 + 이벤트 브리지 리스너). 그 외 기존 파일 **무수정**.
- **읽기 전용 소비**: 8000 공개 REST. 기존 라우트/스토어 **코드 무수정**.

## 3. 데이터 흐름
사용자 입력 → (프론트 8001) `POST /api/conversations/{id}/messages`(SSE) → 오케스트레이터가 히스토리+시스템+툴 로드 → provider 스트리밍 → 툴 호출을 **8000 HTTP GET**으로 실행 → 최종 답 스트림→UI, 8001 로컬 영속 → 딥링크 칩 → 클릭 시 `xd:navigate` 이벤트 → BuildShell이 기존 네비게이션 호출.

## 4. API 계약 (8001 `routes_chat.py`, 전부 신규)
- `GET  /api/conversations?project_name=` — 현재 사용자·프로젝트 스코프 목록.
- `POST /api/conversations` — 신규(project+user). user는 8001이 8000 `/api/auth/me`로 확인.
- `GET  /api/conversations/{id}` — 메시지.
- `POST /api/conversations/{id}/messages` — 전송(SSE 스트림 응답).
- `PATCH /api/conversations/{id}` — 제목·모델·egress 변경. `DELETE` — 삭제.
- `GET  /api/chat/models` — 가용 provider/model + needs_key·egress 플래그.
- `GET  /api/chat/health` — 8001 헬스 + 8000 연결성.
- **8000은 신규 라우트 0**(OPEN-1 (a)). (b) 채택 시에만 8000에 read-only `/api/ontology` 1개.

## 5. 위험 / 전제 (정직한 표기)
- **OPEN-1(장비 그래프)**: §0-C. (a) 기본 시 장비-엔티티 Q&A는 텍스트 검색 근사·진짜 그래프는 v1 밖.
- **교차 프로세스 지연/장애**: 8001→8000 HTTP 왕복 = 툴당 네트워크 홉. 타임아웃·재시도·8000 다운 시 우아한 안내 필요(로컬호스트라 지연 미미).
- **인증 전파**: 8001이 8000 `/api/auth/me`로 현재 사용자 판정. S7이 로컬 모의(쿠키/세션 단순)라 8001↔8000 사용자 일관성 확인 필요(같은 브라우저 세션 or 헤더 전달).
- **데이터 반출(HUMAN_GATE)**: 클라우드 provider = 외부 전송. 기본 로컬로 완화, 클라우드 opt-in은 명시 동의. API 키는 8001 `.env`(커밋 금지).
- **스트리밍 중단 시 부분 영속**, **툴 반복 상한(N=5)**, **로컬 LLM 미가동 우아 안내**.

## 6. 테스트 전략
- **백엔드(8001)**: 대화/메시지 CRUD·스코프 격리(A≠B)·**MockProvider로 오케스트레이션 루프**(결정적)·툴 실행 그라운딩(8000을 **httpx mock/respx로 스텁**해 결정적)·provider 어댑터(목 HTTP)·egress 게이트. `backend/ai/tests/`(기존 pytest와 분리).
- **프론트**: ChatDrawer 렌더·목록/선택/새대화·메시지 전송(목)·**딥링크 칩→`xd:navigate` 이벤트**·모델 선택 egress 배지. `src/ai/` 테스트.
- **격리 불변식(신규·핵심)**: (e) flag OFF 빌드·기존 98/78 GREEN·기존 파일 git diff=0 확인. (f) 8001 미기동 시 8000 e2e 정상. (g) `grep`으로 `backend/ai/`가 기존 backend import 0 정적 확인.
- **e2e**: 8000+8001 동시 기동 → 드로어 열기→새 대화→"시트 몇 장?"→집계 답변→딥링크 클릭 이동. 콘솔 0. + **킬스위치 리허설**(flag off → 기존 화면 무변화, 8001 종료 → 기존 정상).

## 7. 로드맵 (phased milestones, 사이드카 개정)

| 단계 | 내용 | 산출·검증 |
|---|---|---|
| **S8.0** | **데이터 표면 확정 + 8001 부트스트랩.** 8000 공개 API로 어떤 질문을 그라운딩할지 매핑, OPEN-1 확정. 독립 FastAPI(8001) 스켈레톤 + httpx 8000 클라이언트 + `/api/chat/health` + 기동 스크립트. **8000 무수정.** | 8000↔8001 연결 스모크·health |
| **S8.1** | **대화 영속(ai_store) + 제공자 추상화(로컬).** `_ai_data` CRUD + 스코프 격리 + provider 인터페이스 + Ollama + **MockProvider**로 오케스트레이션 골격. | pytest CRUD·격리·목 루프 |
| **S8.2** | **Tool-use 오케스트레이션 + 툴 카탈로그(8000 HTTP 클라이언트).** 읽기 툴 6~8종 + tool-use 루프 + 그라운딩 시스템 프롬프트. 8000은 respx 스텁. | 실질의 답변·그라운딩 pytest |
| **S8.3** | **`src/ai` 챗 드로어 UI + SSE + BuildShell 마운트/브리지 + 킬스위치 flag.** Drawer/List/Thread/Composer + 이어가기/새 대화 + 스트리밍 + flag on/off. | 프론트 test·e2e·**flag off 무변화** |
| **S8.4** | **딥링크 브리지 + 모델 선택 + 클라우드 egress 게이트.** `xd:navigate` 칩 + provider/model 선택 + egress 동의 + GPT/Gemini/Claude 어댑터. | e2e 딥링크·egress 게이트 |
| **S8.5** | **검증/폴리시.** 독립 3렌즈 + reconcile + **킬스위치 불변식 검증(e~g)**. | S8 DONE |
| **(S9)** | **후속: 액션/에이전트**(챗에서 이슈 생성·마크업 등, S7 RBAC 강제 + 사용자 확인). 8001→8000 쓰기 API 필요 = 별도 스코프. | 별도 스테이지 |

각 S8.x 진입 시 `prompts/10~`에 per-stage 메타프롬프트를 공동설계·FROZEN하고 구현 → 별도 검증팀 채점(ai-loop 표준).

## 8. Out of scope (v1 의도적 제외)
- 쓰기/액션(이슈·마크업 생성) = S9. 다중 사용자 공유 대화·조직 SSO·클라우드 키 로테이션. 음성·도면 이미지 이해(멀티모달). 임베딩/벡터스토어(RAG 미채택). 실제 인증(S7 로컬 모의 유지).
- **장비-엔티티 온톨로지 그래프 Q&A**(OPEN-1 (a) 기본 시) — 8000 온톨로지 read 라우트 신설 후 후속.
- **8001→8000 공유 배포/역프록시 통합** — v1은 로컬 2프로세스로 충분.

## 9. 설계 검수 결과 (2026-07-01, 세션11 — 독립 4렌즈)

> 구현 전 설계 산출물을 4개 독립 렌즈로 적대 검수. **이 절이 위 본문의 상충 서술을 정정·우선한다.** 상세·등급은 `EVIDENCE.md` "S8 설계 검수" 블록, 미결 결정은 `HUMAN_GATE.md`.

### 검증된 부분 (진행 가능)
- **백엔드 격리** = 실검증 가능·건전. 별도 8001·`import 0`(K6 grep)·기존 tracked 코드 `diff=0`(K7)·킬스위치(f) 모두 객관 채점 가능. 렌즈3이 코드로 확인: `/api/auth/me`(전역 current_user·세션 불요)·`/api/search`(딥링크 ID)·`/api/drawings`(시트번호/공종)·GET 무가드(403 위험0)·CORS 서버간 무관 → **8000 완전 무수정(OPEN-1 a) 실현 가능.**
- **S8.0 부트스트랩** = 아무 산출물도 foreclose하지 않고 병행 착수 가능. `prompts/10`은 검수 교정(health↔시트수·스모크 전제·K7·CORS·경로) 반영 후 실행·채점 가능.
- **OPEN-1(a) Q&A 축소** = 헤더/§0-C에 승인일과 함께 정직히 기록(조용한 축소 아님).

### 정정 (사실 오류 — 본문 우선)
- **BuildShell 허상**: 본문(§0-B·§2 계층④·§7)이 "유일 접점 `BuildShell.tsx`"라 했으나 **그 파일은 없다.** 실제 셸=`App.tsx`, Build 뷰·네비 상태(`openSheet`/`searchOpenIssue`/`searchOpenFolder`)=`BuildSheetsView.tsx` private useState. 딥링크 브리지는 이 실파일들에 재기술해야 함(참고: `GlobalSearch`가 이미 props 딥링크 패턴). → **아키텍처 재설계 = GATE-2**, S8.3 공동설계 시 확정.
- **`/api/files` 부재**: 본문(§2 계층③'·§4)의 `list_files → GET /api/files`는 틀림. 실제 = `GET /api/drawings`(파일/도면) + `GET /api/folders`(폴더). **S8.2에서 `list_files`를 이 두 라우트 조합으로 재기술.** (S8.0 무관 — 대표 툴 2종에 `list_files` 없음.)
- **owner-scoping 문구 하향**: "사용자 A는 B의 대화를 못 본다(scope 강제)"는 과장. S7 `current_user`는 세션 없는 전역 가변 → 표시용이며 프라이버시/보안 경계 아님. → **GATE-3**, S8.1에서 owner를 전송 시점 컨텍스트로 고정 + 레이스 테스트.

### 후속 스테이지 FROZEN 전 반드시 접을 항목 (늦게 발견 금지)
- **S8.1**: `ai_store` 원자적 write(temp+rename) + 동시 append 회귀 테스트(S1 "JSON store race" 전례). owner 전송시점 고정(GATE-3).
- **S8.2**: 그라운딩 **골든 이밸**(질문→기대 딥링크 ID) + **환각 적대 테스트**(없는 엔티티→"없음" 강제) — MockProvider/respx는 배관만 검증, 환각 미검. `list_files` 경로 교정.
- **S8.3**: 챗 UI a11y(스트리밍 ARIA live region·focus trap·키보드·ESC) + 프론트 격리 채점(flag off 스냅샷 무변화 + `src/build/**`가 `src/ai/**` import 0 = K6 프론트 미러) + GATE-2 아키텍처.
- **S8.4**: egress **감사 로그**(무엇을·언제 반출) + 비게이트(딥링크·모델선택)와 HUMAN_GATE(클라우드 egress·LLM 어댑터) **하위 스테이지 분리**.
- **검증팀**: 표준 3렌즈(백엔드 적대/프론트 a11y/Done-When)에 **4번째 = 그라운딩/환각 적대자** 추가(AI 고유 리스크 담당).

### 미결 게이트 (HUMAN_GATE.md, 세션12 결정)
- **GATE-1 [BLOCKER]**: 온톨로지 바인딩(equipmentEntityId·analysis_result 계승, LOOP.md L34 "핵심 차별화") product Done-When이 S8 재설계로 담당 스테이지 없이 이탈 → 폐기/S10 연기/S8 재편입 3지. **이 결정 전엔 S8 DONE 경로 없음.** (EVIDENCE reconcile = NARROWED/DEFERRED 기록됨.)
- **GATE-2**: 프론트 접점 아키텍처(BuildShell 허상·"어느 화면에서든" vs 단일 마운트 모순·flag-off 채점).
- **GATE-3**: 대화 owner 프라이버시 한계.

---
> **승인 절차**: 백엔드 계약·S8.0은 FROZEN(검수 반영)으로 착수 가능. 프론트/온톨로지는 GATE-1/2/3 결정 후 확정. S8.0 메타프롬프트=`prompts/10`(교정 FROZEN).
