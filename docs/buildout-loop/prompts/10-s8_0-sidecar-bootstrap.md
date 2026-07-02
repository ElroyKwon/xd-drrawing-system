# S8.0 — AI 챗 사이드카 부트스트랩 (8001 독립 프로세스 + 8000 HTTP 데이터 경로)  [STATUS: FROZEN 2026-07-01 · 검수 교정 반영 (4렌즈, 세션11)]

> ai-loop 스테이지 계약. `docs/buildout-loop/S8-ai-chat-design.md`(v2 격리형 FROZEN, 9결정)와 S1~S7(`prompts/01`~`09`) 결과를 상속한다. 구현 에이전트가 이 텍스트를 그대로 입력받아 자율 실행하고, **별도 검증팀이 아래 Acceptance checklist(K1~K10)로 항목별 채점**한다. 합격을 위해 기준을 도중에 고치지 않는다(기준 변경 = 스코프 변경 = HUMAN_GATE).

## Stage goal / Done-When

S8(AI 챗 어시스턴트)의 **토대**를 놓는다. 기존 8000 앱을 **한 줄도 건드리지 않고**, `backend/ai/`에 **독립 FastAPI 프로세스(8001)** 를 세워, 8001이 8000의 **공개 HTTP API만**으로 프로젝트 실데이터를 읽을 수 있음을 **라이브로 증명**한다. 이 스테이지의 산출물은 챗 기능이 아니라 **격리된 사이드카 골격 + 검증된 교차-프로세스 데이터 경로 + 격리 불변식 자동 검사**다. 설계 v2 §7 로드맵 S8.0, Done-When (e)(f)(g)(격리 불변식)의 토대.

**완료 정의(S8.0)**:
- (a) `backend/ai/.venv`(자체) + `backend/ai/requirements.txt`(자체, fastapi·uvicorn·httpx·pytest·respx)로 독립 FastAPI 앱이 `127.0.0.1:8001`에 기동된다. 기동 명령/스크립트 문서화.
- (b) **8001은 8000 없이도 기동된다**(lazy 클라이언트). `GET /api/chat/health`가 8001 자체 상태 + **8000 연결성**(도달 가능/현재 사용자)을 보고한다. 8000 다운이면 degraded로 정직하게 응답(크래시 없음).
- (c) **라이브 데이터 경로 증명**: 8000 HTTP 클라이언트 래퍼 + 대표 읽기툴 2종(`search`, `list_sheets`)이 **실제 8000에 GET**해 그라운딩 데이터(예: 프로젝트 시트 수, 검색 결과)를 반환함을 스모크로 확인. (전체 툴 카탈로그는 S8.2.)
- (d) **격리 불변식 자동 검사**: (g) `backend/ai/`가 기존 backend 모듈(`store`, `routes_*`, `auth`, `conversion`, `vector` 등)을 **import하지 않음**을 정적으로 검사하는 pytest. (e) 기존 backend `routes_*`·`store.py`·`_*.json`이 **git diff = 0**. (f) 8001 미기동 상태에서 기존 8000 앱은 완전 정상(무의존, 문서로 확인).
- (e) 8001 자체 pytest(`backend/ai/tests/`, 기존 78 pytest와 분리)가 GREEN. 기존 build·npm test 98·backend pytest 78 회귀 0.

## Co-design log (2026-07-01 사용자 확정 — AskUserQuestion 2결정 freeze)

- **(Q1) 의존성/venv = 자체 venv + 자체 requirements.** `backend/ai/.venv` + `backend/ai/requirements.txt`. 기존 `backend/.venv`와 완전 분리(기존 dep 침범 0). 사용자는 venv 2개 관리. → dep도 '별개 관리'.
- **(Q2) 데이터 경로 증명 = 스켈레톤 + 라이브 데이터 스모크.** 8001 앱 + httpx 클라이언트 래퍼 + `health` + 대표 읽기툴 2종(`search`·`list_sheets`)을 실제 8000에 GET해 end-to-end 그라운딩 경로를 S8.0에서 증명(사이드카 최대 리스크 조기 해소). 전체 툴 카탈로그(6~8종)는 S8.2.
- **(상속) OPEN-1 = (a) 순수 클라이언트.** 8000 신규 라우트 0. 8000 완전 무수정.
- **(가정) 현재 사용자 전파.** S7 `current_user`는 8000 서버 전역 영속(`/api/auth/me`, 쿠키/세션 아님) → 8001은 `GET /api/auth/me`로 전역 현재 사용자를 그대로 취득(별도 세션 전파 불요). 대화 owner 귀속은 S8.1.
- **(가정) 프로젝트 컨텍스트.** health/스모크는 기본 프로젝트(기존 시드 `Study_Project` 등 실 존재 프로젝트)로 확인. 하드코딩 더미 금지 — 8000이 실제로 반환하는 프로젝트/시트.

## Instruction (수행 단계)

1. **S8.0-a 패키지 골격**: `backend/ai/` 신설 — `main_ai.py`(FastAPI 앱), `__init__.py`, `requirements.txt`(fastapi·uvicorn[standard]·httpx·pytest·respx), `.gitignore`(`.venv/`, `_ai_data/`), 짧은 `README.md`(기동법). 자체 venv 생성 후 설치. **기존 `backend/*` 무수정.** CORS는 **8001 자체 상수**로 `http://127.0.0.1:5173`·`5174`·`http://localhost:5173`·`5174`만 허용(격리상 `backend.config` import 금지). S8.0엔 프론트 소비자가 없어 최소 설정만(실사용은 S8.3).
2. **S8.0-b 8000 HTTP 클라이언트**: `backend/ai/client.py` — httpx 기반 read-only 클라이언트. 베이스 URL = 환경변수 `XD_BACKEND_BASE`(기본 `http://127.0.0.1:8000`). 타임아웃·연결 실패 우아 처리(예외→구조화 에러). **lazy**(모듈 import 시 8000에 연결하지 않음). `get_me()`·`get(path, params)` 저수준 + 재사용.
3. **S8.0-c 대표 읽기툴 2종**: `backend/ai/tools.py` — `search(project, query)`(→ `GET /api/search`), `list_sheets(project, discipline=None)`(→ `GET /api/drawings` + 시트 매핑). 각 툴은 구조화 JSON + 안정 ID(딥링크용) 반환. **기존 backend 함수 직접호출 금지, 오직 HTTP.** (나머지 툴은 S8.2 — 여기선 2종만.)
4. **S8.0-d health 엔드포인트**: `backend/ai/routes_health.py`(또는 main_ai 내) — `GET /api/chat/health` → `{ ok, backend_8000: {reachable, current_user?}, checks: {...} }`. 8000 도달 시 현재 사용자 포함, 미도달 시 `reachable:false`로 degraded(200, 크래시 없음). **health는 연결성·현재 사용자만 보고한다 — 시트 수 등 그라운딩 데이터는 툴(S8.0-c)이 반환하며 health 스키마에 넣지 않는다.**
5. **S8.0-e 기동 스크립트/문서**: `backend/ai/run.ps1`(또는 문서화된 명령) — `backend/ai/.venv/Scripts/python.exe -m uvicorn main_ai:app --host 127.0.0.1 --port 8001`. `docs/buildout-loop/PROGRESS.md` 재기동 절차에 8001 항목 추가(8000과 별개 프로세스).
6. **S8.0-f 격리 불변식 테스트**: `backend/ai/tests/test_isolation.py` — (g) `backend/ai/` 소스에 `import store`/`from routes_`/`import auth`/`import conversion`/`import vector` 등 기존 backend 모듈 참조가 0임을 AST 또는 텍스트 스캔으로 검사. (필요 시) 8001 앱이 8000 모듈 없이 import·기동됨을 확인.
7. **S8.0-g 라이브 스모크 + 단위 테스트**: `backend/ai/tests/test_smoke.py` — respx로 8000을 스텁해 `client`·`tools.search`·`tools.list_sheets`·`health` 결정적 단위 테스트(8000 다운 degraded 포함). **별도로**, 8000 실기동 시 라이브 스모크로 **`tools.list_sheets`가 실제 시트 수를 반환**함을 e2e 1회 입증(health는 연결성만). **전제: 대상 프로젝트(`Study_Project` 등)에 최소 1개 도면이 업로드된 상태 — 시드는 도면/시트를 심지 않으므로 없으면 `reference/`의 샘플 도면 1건을 8000에 업로드 후 측정. 시트 0장도 실값으로 인정(8000이 반환한 값과 일치하면 합격; 하드코딩 카운트만 불합격).** 증거 캡처.
8. **검증**: `backend/ai/.venv` pytest(`backend/ai/tests/`) GREEN. 기존 게이트 회귀 0 — `npm run build`·`npm test`(98)·`backend/.venv` `pytest`(78)·`git diff --check`. **기존 코드 무수정 확인**: `git status`가 신규 `backend/ai/`만 표시 + `git diff --stat -- backend/routes_*.py backend/store.py backend/main.py backend/auth.py` 공백(런타임 상태파일 `backend/uploads/_*.json`은 untracked → diff 대상 아님). 라이브: 8000+8001 동시 기동 → `curl/브라우저 GET /api/chat/health`가 8000 도달·현재 사용자 반환 + `tools.list_sheets` 실 시트 수 반환, 8000 정지 시 8001 degraded 응답(크래시 없음) 캡처. 8001 미기동 시 기존 8000 e2e 정상 캡처.

## Inputs

- 신규(격리): `backend/ai/`(main_ai·client·tools·routes_health·requirements·run.ps1·README·tests), `backend/ai/.venv`, `backend/ai/_ai_data/`(이 스테이지엔 미사용, .gitignore).
- 읽기 전용 소비(무수정): 8000 공개 API — `GET /api/auth/me`, `GET /api/search?project_name=&q=`, `GET /api/drawings?project_name=`. (계약은 기존 `backend/routes_auth.py`·`routes_search.py`·`routes_drawing.py` 응답 형태 참조 — **호출만, 수정 금지**.)
- 스펙: `docs/buildout-loop/S8-ai-chat-design.md`(v2 §2 아키텍처·§4 API·§7 로드맵 S8.0·Done-When e~g).
- 재기동: `PROGRESS.md` 세션6 블록(8000/프론트 기동) + 본 스테이지에서 추가하는 8001 절차.

## Acceptance checklist (검증팀이 항목별 채점 — freeze 후 불변)

- [ ] K1. **독립 기동**: `backend/ai/.venv` + 자체 `requirements.txt`로 FastAPI 앱이 `127.0.0.1:8001` 기동. 기동 명령/스크립트 문서화. 기존 `backend/.venv` 무변화.
- [ ] K2. **8000 무의존 부팅**: 8001은 8000이 꺼져 있어도 import·기동된다(lazy 클라이언트). 모듈 import 시 8000 연결 시도 없음.
- [ ] K3. **health 정직 보고**: `GET /api/chat/health` → 8001 상태 + 8000 도달성. 8000 도달 시 현재 사용자 포함, 미도달 시 degraded(200, 크래시 없음).
- [ ] K4. **8000 HTTP 클라이언트**: `client.py` httpx read-only, 베이스 URL 환경변수(`XD_BACKEND_BASE` 기본 8000), 타임아웃·실패 우아 처리.
- [ ] K5. **라이브 데이터 경로 증명(핵심)**: `tools.search`·`tools.list_sheets`가 실제 8000에 GET해 그라운딩 데이터 반환. 라이브 스모크로 **툴이(health 아님) 실제 시트 수·검색 결과**를 반환함을 입증. **전제: 대상 프로젝트에 최소 1개 도면 업로드(없으면 `reference/` 샘플 1건 업로드 후 측정). 8000 반환값과 일치하면 합격 — 0장도 실값, 하드코딩 카운트만 불합격.**
- [ ] K6. **격리 불변식 (g) — import 0**: `backend/ai/` 소스가 기존 backend 모듈(`store`/`routes_*`/`auth`/`conversion`/`vector` 등)을 import하지 않음을 자동 검사(pytest)로 강제. GREEN.
- [ ] K7. **격리 불변식 (e) — 기존 코드 무수정**: 기존 backend **tracked** 코드(`routes_*.py`·`store.py`·`main.py`·`auth.py`)가 이 스테이지 변경으로 **git diff = 0**(`git diff --stat --` 공백, `git status`는 `backend/ai/` 신규만). 런타임 상태파일 `backend/uploads/_*.json`은 untracked라 diff 대상 아님(문서 갱신 외 코드 무수정만 검사).
- [ ] K8. **격리 불변식 (f) — 8000 무영향**: 8001 미기동 상태에서 기존 8000 앱(업로드→시트→뷰어)이 완전 정상. 증거 캡처.
- [ ] K9. **자체 테스트 분리 + 회귀 0**: `backend/ai/tests/` pytest GREEN(respx 결정적 단위 + degraded). 기존 `npm run build`·`npm test`(98)·`backend/.venv` pytest(78) **회귀 0**, `git diff --check` clean.
- [ ] K10. **실데이터 기반**: 스모크가 실 존재 프로젝트(시드 `Study_Project` 등)에서 8000이 실제로 반환한 시트/검색 결과 기반. generic 더미·하드코딩 카운트면 불합격(시트 0장은 실값으로 인정).

## Out of scope (S8.0에서 의도적으로 하지 않음)

- **대화/메시지 영속(ai_store)·provider 추상화·오케스트레이션 루프** = S8.1.
- **전체 툴 카탈로그(get_project_summary·get_sheet·list_issues·get_issue·list_files)** = S8.2. S8.0은 대표 2종(search·list_sheets)만.
- **프론트 챗 UI(src/ai)·SSE·BuildShell 마운트·딥링크 브리지·킬스위치 flag** = S8.3~S8.4.
- **클라우드 provider·egress 게이트·API 키** = S8.4.
- **장비-엔티티 온톨로지 그래프 질의**(OPEN-1 (a) — v1 밖) · 8000 신규 라우트(무수정 유지).
- **인증 세션/쿠키 전파**(S7 전역 current_user로 충분) · 프로젝트 단위 데이터 격리 강제.

## Freeze 답 (사용자 확정 — AskUserQuestion 2026-07-01)

1. 의존성/venv = **자체 venv + 자체 requirements**(`backend/ai/.venv`, 기존 backend dep 침범 0).
2. 데이터 경로 증명 = **스켈레톤 + 라이브 데이터 스모크**(search·list_sheets 실 8000 GET, 리스크 조기 해소). 전체 툴은 S8.2.
3. (상속) OPEN-1 = **(a) 순수 클라이언트**, 8000 완전 무수정.

**검수 교정 (2026-07-01 세션11, 4렌즈 — 기준 완화 아님, 모호성 제거·사실 정정)**: ① health↔"시트 수" 3자 모순 → 툴이 시트 수, health는 연결성만으로 단일화(완료정의 c·S8.0-d·-g·K5). ② 라이브 스모크 재현 — 시드는 시트 미포함 → "최소 1도면 업로드 전제, 0장도 실값" 명시(S8.0-g·K5·K10). ③ K7 `_*.json`은 untracked 공허 → tracked 코드 무수정으로 정정 + diff 명령 구체화. ④ CORS origin 8001 자체 상수 하드코딩(backend.config import 금지). ⑤ PROGRESS 경로 = `docs/buildout-loop/`. (근거: `EVIDENCE.md` S8 설계 검수 블록.)

→ STATUS: FROZEN(2026-07-01, 검수 교정 반영). 실행·채점은 이 고정 텍스트 기준. 합격을 위해 기준을 도중에 고치지 않는다(기준 변경 = 스코프 변경 = HUMAN_GATE).
