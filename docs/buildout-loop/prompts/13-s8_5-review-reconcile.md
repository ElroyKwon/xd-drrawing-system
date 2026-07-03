# S8.5 — 독립 3렌즈 검수 + S8 Done-When reconcile  [STATUS: FROZEN 2026-07-03 · 2결정(AFK 자율=추천안)]

> ai-loop 스테이지 계약(검수/reconcile 스테이지). S8.0~S8.4 결과를 상속. **구현자(나)는 채점하지 않는다** — 별도 독립 검증자 3렌즈가 적대적으로 채점하고, 신선 비평가가 Done-When을 reconcile한다. 이 스테이지가 닫는 부채: R1(S8.1/8.3 독립 3렌즈 미실시)·R7(owner 레이스 테스트). 통과 시 **S8 DONE 선언**.

## Stage goal / Done-When

S8(AI 사이드카 챗)의 **독립 검증을 완결**하고, LOOP.md의 S8 product Done-When을 문자 그대로 reconcile해 **S8 DONE 게이트**를 통과한다.

**완료 정의(S8.5)**:
- (a) **독립 3렌즈 검수 실행**(별도 에이전트, 적대적 = 결함 탐색): 렌즈1 백엔드 적대 · 렌즈2 프론트/a11y · 렌즈3 Done-When 비평. 각 렌즈는 반례 우선.
- (b) **발견 결함 처분**: BLOCKER·MAJOR는 수리 + 회귀 재검증(차단선). MINOR는 PROGRESS 부채로 기록(후속). 코드 수리 시 격리 불변식·회귀 0 유지.
- (c) **S8 Done-When reconcile**: 신선 비평가가 LOOP.md S8 product Done-When을 MET/NARROWED/UNMET + 증거등급(device/emulated/synthetic/static)으로 판정. NARROWED/UNMET는 DONE 차단 → HUMAN_GATE.
- (d) **S8 DONE 선언 or 게이트**: BLOCKER/MAJOR 0 + reconcile 전항목 MET → S8 DONE. 아니면 정지·보고.

## Co-design log (2026-07-03 — AskUserQuestion 60s 무응답 → CLAUDE.md 자율=추천안 freeze)

- **(Q1) 렌즈 범위 = 미검증분 집중(S8.1·8.3·8.4)**. S8.0(K1~K10)·S8.2(L1~L10)는 이미 독립검증 완료 → 재검수 생략(중복 공수 회피). 3렌즈는 **독립검증 이월분(S8.1 두뇌·영속, S8.3 드로어 UI, S8.4 egress)**에 집중. **단 reconcile(c)은 S8 전체**(S8.0~8.4가 종합적으로 Done-When을 충족하는가).
- **(Q2) DONE 차단선 = BLOCKER+MAJOR 차단, MINOR 부채기록**. 치명·중대 결함만 수리 후 DONE, 사소결함은 후속. appearance-loop 선례 계승. (전량수리 옵션 미채택 — 시간 대비 실익.)

## Instruction (수행 단계)

1. **렌즈 3종 병렬 실행**(각각 독립 general-purpose 에이전트, 파일 수정 금지·읽기/실행/라이브만):
   - **렌즈1 백엔드 적대**: 격리 불변식(backend.* import 0 — `backend/ai/tests/test_isolation.py`·Grep, 8000 tracked diff 0), 툴 HTTP 매핑 정확성(7종 `tools.py`가 실 8000 GET, 하드코딩 0), **프롬프트 인젝션**(사용자 메시지가 시스템 프롬프트/툴선택을 전복하는가), egress 킬스위치·감사 무결(S8.4), provider mock=egress0, `ai_store` 원자적write·동시성(R7 owner 전환-중-전송 레이스 포함). 대상: `backend/ai/*.py`.
   - **렌즈2 프론트/a11y**: 드로어 격리(`src/ai/**`가 앱 모듈 미의존·`src/build`→`src/ai` 단일 접점 grep), 킬스위치 `VITE_AI_ENABLED`, a11y(드로어 focus 관리·ESC·`aria-live` live region·버블 역할), 마크다운 안전 렌더러(`src/ai/markdown.tsx` `dangerouslySetInnerHTML` 미사용), 딥링크 브리지(`xd:navigate`) 안전성. 대상: `src/ai/**`, 마운트 `src/BuildSheetsView.tsx`.
   - **렌즈3 Done-When 비평**: LOOP.md의 S8 관련 product Done-When(`AI 사이드카 챗` 항목)만 받아, EVIDENCE.md(S8.0·8.2·8.4 블록)·PROGRESS를 근거로 각 요소를 MET/NARROWED/UNMET+증거등급 판정. **침묵 좁힘**(Done-When을 몰래 축소해 통과시킨 흔적)을 특히 색출.
2. **결함 취합·처분**: 3렌즈 반환을 BLOCKER/MAJOR/MINOR로 분류. BLOCKER·MAJOR는 근본원인 수리(`systematic-debugging`) + 회귀 재검증(사이드카 pytest·backend pytest·vitest·build·격리). MINOR는 PROGRESS 부채 목록.
3. **S8 Done-When reconcile**(신선 비평가 = 렌즈3 산출 채택 or 별도 1인): S8 product Done-When 각 요소에 MET/NARROWED/UNMET+등급. NARROWED/UNMET → HUMAN_GATE.md.
4. **EVIDENCE.md S8.5 블록**: 3렌즈 판정·발견결함·수리·reconcile 표. **S8 DONE 선언 or 차단 사유** 명시.
5. **커밋**: 수리분 + 문서. (push는 별도 게이트.)

## Inputs (참고 컨텍스트)

- 검수 대상 코드 지도: 백엔드 `backend/ai/`(main_ai·client·tools·agent·provider·ai_store·routes_chat·routes_egress·egress·health·eval). 프론트 `src/ai/`(aiClient·ChatDrawer·markdown·chat.css), 마운트 `src/BuildSheetsView.tsx`.
- 상속 증거: `EVIDENCE.md` S8.0(K1~10)·S8.2(L1~10)·S8.4(M1~10) 블록, `PROGRESS.md` 세션14~17.
- 격리 불변식: backend.* import 0, `src/ai`→앱모듈 미의존, `src/build`→`src/ai` 단일 접점.
- 라이브: 8000·8001 기동 중. ⚠️ egress mock 모드로 검증하면 과금 0(openai 강제 검증은 최소 1회).
- S8 product Done-When(LOOP.md): "AI 사이드카 챗 — 격리 8001 사이드카가 8000 공개 HTTP만으로 프로젝트 실데이터를 그라운딩해 실 LLM(gpt-5.5) Q&A." (온톨로지는 S10 NARROWED — S8 제외.)

## Acceptance checklist (별도 검증팀/신선 비평가가 항목별 채점 — freeze)

- **N1** — 렌즈1(백엔드 적대) 실행됨, 격리·툴경로·프롬프트인젝션·egress·ai_store 각각 반례 시도한 근거 반환.
- **N2** — 렌즈2(프론트/a11y) 실행됨, 드로어 격리·킬스위치·a11y·마크다운 안전·딥링크 각각 확인 근거 반환.
- **N3** — 렌즈3(Done-When 비평) 실행됨, S8 product Done-When 각 요소 MET/NARROWED/UNMET+증거등급, 침묵 좁힘 색출.
- **N4** — 발견 BLOCKER·MAJOR **전량 수리 + 회귀 재검증**(사이드카 pytest·backend pytest·vitest·build·격리 diff0 GREEN). MINOR는 PROGRESS 부채기록.
- **N5** — S8 Done-When reconcile 완료: 각 요소 판정+등급 기록, NARROWED/UNMET는 HUMAN_GATE로 라우팅.
- **N6** — EVIDENCE.md S8.5 블록에 3렌즈·결함·수리·reconcile·**S8 DONE 선언(or 차단사유)** 기록.
- **N7** — 회귀 0·격리 불변식 유지(수리 후에도). 8000 tracked diff 0.

## Out of scope (의도적으로 하지 않음)

- **S8.0·S8.2 3렌즈 재검수** — 이미 독립검증 완료(Q1). reconcile에서만 종합.
- **S10 온톨로지** — S8 Done-When에서 NARROWED로 이미 분리(LOOP.md). S8.5는 AI 챗만.
- **신규 기능·툴 추가** — 검수/수리 스테이지. 기능 확장은 후속.
- **push** — 별도 게이트(사용자 결정).
- **MINOR 결함 수리** — 부채기록만(Q2). 후속.
