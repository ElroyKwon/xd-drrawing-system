# 06. Claude API 에이전트 구축 — Phase × Step 실행 계획

> **작성 시점**: 2026-04-21 세션 말미, MVP(Claude Code × Opus 4.7) 1 사이클 성공 직후.
> **전제**: 이번 MVP 는 Claude Code 가 이미 Read/Write/Edit/Bash/Chrome DevTools MCP 를 모두 쥐고 있어 "에이전트처럼" 동작했다. 프로덕션은 **Claude API + 명시적 tool 정의** 기반으로 **동일 능력을 재현**해야 서비스 가능하다.
> **이 문서의 목적**: MVP 에서 실측된 버그·교훈·tool 호출 패턴을 근거로, **각 Phase 가 무엇을 증명하고 어떤 산출을 남기는지** 구체화한다. 새 세션이 이 문서만 보고도 바로 착수 가능하도록.

---

## 0. 전체 로드맵 한눈에

```
Phase 0 ─── MVP 검증 (Claude Code 기반)                   [완료 — 2026-04-21]
                                                 ↓
Phase 1 ─── Tool Surface 구현 (5 개 tool)                [2~3 일]
                                                 ↓
Phase 2 ─── Agent 루프 스켈레톤 (agent.py)              [1~2 일]
                                                 ↓
Phase 3 ─── 시각 디버깅 + Self-critique 강화             [2 일]
                                                 ↓
Phase 4 ─── 다중 시트 확장 + 교차 검증                    [3 일]
                                                 ↓
Phase 5 ─── 프로덕션 이전 (MCP + 모니터링)                [TBD]
```

**Gate 판정 흐름**:
각 Phase 종료 시 `decisions.md` 의 Gate 표가 갱신된다. **Gate 1/5/6 중 하나라도 ❌** 이면 다음 Phase 진입 불가 — 원인 제거 후 재실행.

---

## Phase 0 — MVP 검증 ✅ 완료

### 산출물
- `scripts/test_gemini.py` (fallback 추가), `scripts/build_kb_sheet.py` (신규)
- `knowledge-base/sheets/arch_p062.yml`, `knowledge-base/level-stack.yml`
- `threejs-scene/p062/{index.html, scene.js, kb-loader.js, decisions.md, screenshots/}`
- `05-claude-api-roadmap.md`, 본 문서

### 증명된 것
1. **Claude Opus 4.7 이 도면 KB → Three.js HTML 생성 루프를 자율 수행 가능** (Gate 4·5·6)
2. **Gemini flash-image-preview → flash-preview fallback 로직 동작** (1차 404 → 2차 성공)
3. **consensus_*.json 이 신규 Gemini 재추출보다 3D 에 유리** (항목수·annotations 풍부)
4. **Z축 뒤집힘, translate 중복, 슬래브 투명 등 3D 빌더 고정 버그 3종 확인·해결**

### 증명되지 않은 것 (다음 Phase 로)
- 이 과정이 Claude API tool_use 로 그대로 재현되는가
- 여러 시트에서 일관성 있게 동작하는가
- 피드백 루프가 사람 개입 없이 수렴하는가

---

## Phase 1 — Tool Surface 구현 [2~3 일]

### 목표
MVP 세션에서 Claude Code 가 자동으로 쥐고 있던 능력들을 **명시적 Claude API tool** 로 포장. 5 개 tool 로 충분함을 MVP 에서 확인.

### Step 1.1 `extract_sheet` tool (0.5 일)

**목적**: Gemini 로 도면 1장 → stage-10 구조화 JSON.

**파일**: `scripts/tools/extract_sheet.py`

**함수 시그니처**:
```python
def extract_sheet(
    sheet_id: str,                    # 예: "arch_p062"
    stage: Literal["00", "10"] = "10",
    model: str = "gemini-3.1-flash-image-preview",
    fallback_model: str = "gemini-3.1-flash-preview",
    reference_json: Optional[str] = None,  # 다른 모델 결과 참조
    max_tokens: int = 16000,
) -> dict:
    """
    Returns:
      {
        "output_dir": "outputs/{ts}_{sheet_id}_{tag}/",
        "parsed_json_path": "...",
        "anchored_summary": {"dims_pct": 30.8, ...},
        "model_used": str,
        "fallback_used": bool,
        "elapsed_sec": float,
      }
    """
```

**구현**: 기존 `test_gemini.py` 의 `main()` 을 함수화. argparse 걷어내고 직접 호출 형태로.

**Checkpoint**:
- p062 호출 1회 성공
- 잘못된 모델명 1차 → 2차 fallback 성공
- 반환 dict 의 `output_dir` 실존 검증

**교훈 반영**: MVP §3.1 — "기존 consensus 가 있으면 재추출 skip" 판단을 **tool 사용자(에이전트)** 에게 맡긴다. 이 tool 은 단순 추출기. 조건부 skip 은 시스템 프롬프트에서.

---

### Step 1.2 `build_kb` tool (0.5 일)

**목적**: stage-10 JSON → `knowledge-base/sheets/{sheet_id}.yml` + `level-stack.yml`.

**파일**: `scripts/tools/build_kb.py` (기존 `build_kb_sheet.py` 를 함수화)

**함수 시그니처**:
```python
def build_kb(
    input_json_path: str,
    sheet_id: str,
    source_png: Optional[str] = None,
) -> dict:
    """
    Returns:
      {
        "sheet_yaml_path": "...",
        "level_stack_yaml_path": "...",
        "anchored_counts_by_view": {"v1": {...}, "v2": {...}},
        "grid_validation_issues": list[str],  # y_labels_vs_spacings_ok 등
        "levels_mm": dict,
      }
    """
```

**Checkpoint**:
- consensus_p062.json 입력 시 MVP 와 동일한 YAML 생성 (diff 없음)
- `grid_validation_issues` 에 "y_labels 6개 vs y_spacings 6개 mismatch (예상 5)" 경고 포함

**교훈 반영**: MVP §4.1 의 grid mismatch 는 **에러가 아닌 경고**로 남기고 build 계속 진행. 에이전트가 validation_issues 보고 자율 판단.

---

### Step 1.3 `render_preview` tool (1 일)

**목적**: Three.js HTML + KB → 브라우저 렌더 → screenshot 파일 경로 반환.

**파일**: `scripts/tools/render_preview.py`

**함수 시그니처**:
```python
def render_preview(
    html_path: str,                 # 예: "threejs-scene/p062/index.html"
    screenshot_dir: str,
    views: list[dict] = [           # 카메라 프리셋
        {"name": "iso", "position": [3.5, 1.2, 3.5], "target": [0.5, 0.3, 0.5]},
        {"name": "top", "position": [0.5, 3.0, 0.5], "up": [0, 0, -1]},
        {"name": "southeast", "position": [...], ...},
    ],
    wait_selector: str = "#status",  # "렌더 OK" 나올 때까지 대기
    timeout_ms: int = 15000,
) -> dict:
    """
    Returns:
      {
        "screenshots": [{"name": "iso", "path": "...", "width": 1600, "height": 1000}],
        "console_errors": list[str],
        "scene_bbox": {"min": [...], "max": [...]},  # 자동 dump
        "render_ok": bool,
      }
    """
```

**구현**: `playwright.sync_api` 사용. `page.goto(f"file://{html_path}")` + `page.evaluate("window.__scene.topView()")` + `page.screenshot()`.

**Checkpoint**:
- MVP 와 동일한 view 9 장 screenshot 생성 가능
- `window.__scene` 훅이 없는 경우 graceful fail (에러 메시지만 반환)

**교훈 반영**: MVP §6.3 "시각 디버깅 도구 필수". 자동 bbox dump 포함 → Phase 3 의 `validate_coordinate_system` 기반 데이터.

---

### Step 1.4 `ask_human` + `log_decision` tool (0.5 일)

**목적**: 에이전트가 막혔을 때 사람에게 질문 / 결정을 감사 로그에 남김.

**파일**: `scripts/tools/interaction.py`

**함수 시그니처**:
```python
def ask_human(question: str, context: dict = None) -> str:
    """콜백. 기본 구현은 stdin prompt. 프로덕션에선 Slack/UI 훅."""

def log_decision(
    session_id: str,
    decision: str,
    rationale: str,
    artifacts: list[str] = None,
) -> None:
    """JSONL append 에 session_id 기준 디렉토리에 기록."""
```

**Checkpoint**:
- stdin 콜백으로 질문·응답 1 사이클 성공
- JSONL 로그에 session_id·timestamp·decision 기록 확인

---

### Phase 1 완료 조건
- 5 개 tool 전부 단독 테스트 통과 (`tests/test_tools.py`)
- 각 tool 의 `input_schema` JSON schema 확정 (Anthropic SDK tool 등록용)
- **의도적으로 통합 실행 X** — Phase 2에서 에이전트 루프로 처음 조합

---

## Phase 2 — Agent 루프 스켈레톤 [1~2 일]

### 목표
Claude API `tool_use` 기반 루프 하나가 **p062 MVP와 동등 이상 결과**를 자력 재현.

### Step 2.1 `agent.py` 기본 루프 (0.5 일)

**파일**: `scripts/agent.py`

**구조**:
```python
from anthropic import Anthropic

def run_agent(
    goal: str,
    sheet_id: str,
    session_id: str,
    max_steps: int = 30,
    budget_tokens: int = 500_000,
) -> dict:
    client = Anthropic()
    tools = load_tool_schemas()  # 5개 + text_editor_20250124 + bash_20250124
    messages = [{"role": "user", "content": goal}]
    total_tokens = 0
    for step in range(max_steps):
        resp = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=16000,
            tools=tools,
            messages=messages,
            system=SYSTEM_PROMPT,
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason == "end_turn":
            break
        tool_results = dispatch_tools(resp.content)
        messages.append({"role": "user", "content": tool_results})
        total_tokens += resp.usage.input_tokens + resp.usage.output_tokens
        if total_tokens > budget_tokens:
            break
    return summarize(messages)
```

**Checkpoint**:
- tool 없이 단순 "hello" 호출 성공
- tool_use block 파싱·dispatch 동작
- prompt caching 적용 (system + tools 블록 `cache_control`)

---

### Step 2.2 시스템 프롬프트 확정 (0.5 일)

**파일**: `scripts/prompts/agent-system.md`

**초안 (MVP 교훈 반영)**:
```
당신은 건축 도면을 Three.js 3D 로 재구성하는 에이전트입니다.

## 목표 달성 원칙
1. **KB 먼저 확인** — knowledge-base/sheets/{sheet_id}.yml 이 이미 있으면 재추출 X.
   없으면 extract_sheet → build_kb 순서로 생성.
2. **consensus 우선** — outputs/consensus/ 에 해당 시트 결과가 있으면 extract_sheet 대신 그것을 build_kb 입력으로.
3. **Three.js 좌표계 체크리스트**:
   - ExtrudeGeometry + rotateX(-π/2) 는 y ↔ -z 매핑. Shape 에 그리드 Z 넣을 때 부호 뒤집을 것.
   - polygon/slab(extrude) 와 wall/line(직접 좌표) 이 공존하면 Top 뷰로 bbox dump 해서 좌표계 분리 버그 체크.
   - Shape 에 별도 translate 추가 금지 — ExtrudeGeometry depth 가 이미 bottom=0, top=+depth.
4. **시각 언어 규칙**:
   - 슬래브: 불투명 (바닥 인식)
   - 실: 불투명 바닥 패치 + 반투명 측벽·천장 (내부 가시)
5. **피드백 루프**: render_preview 호출 후 scene_bbox 확인. 
   예상과 다르면 (건물 footprint 이탈, 층 Y 뒤바뀜) 즉시 코드 수정 후 재렌더.
6. **애매하면 ask_human, 단 3회 초과 금지**. 합리적 추정 → log_decision 선호.

## 실패 허용
- polygon_grid 1~2점인 실은 fallback 4m×4m 사각형으로 근사. 사과 금지, log_decision 에만 기록.
- grid y_labels 와 y_spacings 개수 mismatch 는 경고로 진행.

## 종료 조건
- render_preview 가 MVP 와 동등 (층 스택 4개, 실 ≥10개 이름 가시) → 성공
- 또는 max_steps 도달 → 실패 요약 + ask_human
```

**Checkpoint**: 프롬프트 길이 < 1500 tokens (caching 효율)

---

### Step 2.3 p062 단일 재현 테스트 (1 일)

**목표**: `run_agent("arch_p062 를 3D 로 재구성", sheet_id="arch_p062", ...)` 한 번으로 MVP 와 동등 결과.

**비교 기준**:
- 생성된 `threejs-scene/p062/*.js` 가 MVP 버전과 semantically 유사 (diff < 30%)
- screenshot 9장 중 iso·top·southeast 3장이 MVP 와 구조적으로 동일 (실명 라벨 15+, 층 스택 4 가시)
- 실행 로그의 tool 호출 순서:
  ```
  1. bash("ls knowledge-base/sheets/")
  2. (YAML 없음 확인) → bash("ls outputs/consensus/")
  3. (consensus 있음) → build_kb(input=consensus/consensus_p062.json, sheet_id="arch_p062")
  4. str_replace_editor(create threejs-scene/p062/index.html)
  5. str_replace_editor(create scene.js)
  6. str_replace_editor(create kb-loader.js)
  7. render_preview(...) → bbox dump 확인
  8. (문제 발견 시) str_replace_editor(edit scene.js) → render_preview
  9. log_decision("MVP equivalent achieved")
  ```

**Checkpoint**: 총 토큰 < 500k, 비용 < $3, 총 시간 < 30 분

**실패 시나리오 대응**:
- 에이전트가 MVP 의 3가지 버그(translate, Z 뒤집힘, 슬래브 투명) 중 재발 시: 시스템 프롬프트 §3 강화 → 재시도.
- tool 호출 횟수 20 초과: system prompt 에 "KB 이미 있으면 skip" 강조 추가.

---

## Phase 3 — 시각 디버깅 + Self-critique [2 일]

### Step 3.1 `validate_coordinate_system` tool (0.5 일)

**파일**: `scripts/tools/validate_coords.py`

**기능**: render_preview 의 scene_bbox 덤프에서 **좌표계 분리 버그** 자동 감지.

```python
def validate_coordinate_system(scene_bbox_dump: dict) -> dict:
    """
    Returns:
      {"issues": [
         {"severity": "error", "type": "z_axis_split",
          "detail": "rooms z=[-32000,-13000], walls z=[-250,30250] → 부호 분리"},
         {"severity": "warn", "type": "y_stack_inverted", ...},
      ]}
    """
```

**로직**: 같은 view 내 rooms/walls/slabs bbox 의 Z 부호가 일치하는지, Y 값이 층 스택 순서(1FL<2FL<RFL) 인지 등.

**Checkpoint**: MVP 의 4번째 screenshot(`04-fixed-top.png`) 단계 bbox dump 를 입력하면 `z_axis_split` 탐지.

---

### Step 3.2 `render_and_critique` 합성 프롬프트 (0.5 일)

**기능**: render_preview 결과 screenshot 3장 + scene_bbox + 원본 도면 PNG 를 동시에 Claude 에 보내 self-critique 요청.

**프롬프트**:
```
이 3D 렌더(screenshot 3장)와 원본 도면(arch_p062.png) 을 비교하라.
일치점 / 불일치점 / 수정 제안 순으로 답하라.
수정 제안은 파일·라인 단위로 구체적일 것.
```

**Checkpoint**: MVP 에서 사람이 준 2 피드백("바닥 투명", "대각선 확대") 중 하나 이상을 에이전트가 자율 포착.

---

### Step 3.3 실패 모드 카탈로그 (1 일)

**파일**: `docs/ai-3d-builder/failure-modes.md`

**구성**: 에이전트가 재실행마다 만나는 패턴을 카탈로그로 누적.

```yaml
# failure-modes.md
- id: FM-001
  name: "polygon_grid 1점"
  symptom: "실 mesh 가 fallback 4m×4m 로 나옴"
  detection: "scene_bbox dump 에서 room bbox 가 기본 크기"
  fix: "log_decision + expandToQuadIfDegenerate 호출"
  seen_in_sheets: [arch_p062]
  
- id: FM-002
  name: "y_labels vs y_spacings 개수 mismatch"
  ...
```

각 실패 모드에 대응하는 **프롬프트 엣지 케이스 설명** 추가 → 에이전트가 재학습.

---

## Phase 4 — 다중 시트 확장 + 교차 검증 [3 일]

### Step 4.1 arch_p060 (지상1층) 파이프라인 적용 (1 일)

**목표**: 동일한 agent.py 로 sheet_id="arch_p060" 실행. 1FL 실데이터로 MVP 의 placeholder 대체.

**Checkpoint**: Two 시트의 `knowledge-base/sheets/*.yml` 양쪽 존재. `threejs-scene/` 에 p060, p062 각각 디렉토리.

---

### Step 4.2 Cross-sheet consistency check (1 일)

**파일**: `scripts/tools/cross_check.py`

**기능**: p060.yml·p062.yml 비교:
- 그리드 라벨 일치 (5·5B·6·7 동일?)
- 계단 T01 위치가 두 층에서 동일 grid cell?
- level-stack 에서 1FL→2FL = 5500mm 일관?

**Returns**:
```python
{"consistent": bool, "issues": [
  {"type": "grid_mismatch", "p060": [...], "p062": [...]},
  {"type": "vertical_core_drift", "element": "stair_T01", ...},
]}
```

**Checkpoint**: 실제 p060·p062 돌려봤을 때 "grid 동일" 판정 혹은 실데이터 차이 정확히 보고.

---

### Step 4.3 KB index 빌더 (1 일)

**파일**: `scripts/tools/build_kb_index.py`

**출력**:
- `knowledge-base/indexes/floor_to_sheets.yml` (지상1층 → [arch_p060#v1])
- `knowledge-base/indexes/element_cross_refs.yml` (stair T01 → 1F·2F·RF 관통)

**에이전트 사용처**: 시스템 프롬프트에 "건물 전체 3D 를 원하면 먼저 floor_to_sheets.yml 읽어 시트 집합 파악" 지시.

---

## Phase 5 — 프로덕션 이전 [TBD]

### Step 5.1 MCP 서버화
- Step 1 의 5 개 tool 을 FastMCP 서버로 export
- Claude Code(MCP client) 와 Agent SDK 양쪽에서 동일 tool 사용 가능
- Anthropic Agent Skill Kit 레퍼런스

### Step 5.2 비용·토큰 모니터링
- 세션별 JSONL → SQLite 적재
- `/insight/lab` 유사 대시보드 (4주 MVP UI 재사용)
- 알림: 단일 실행이 $5 초과 시 ask_human 강제

### Step 5.3 서비스화
- REST endpoint: POST `/agent/build_3d` with body `{sheet_id, goal}`
- 비동기 작업 큐 (Celery or Arq)
- 인증: 사용자 도면 격리 (tenant 별 api_keys.json)

---

## 전체 체크리스트 (세션 개시 시 자가 진단용)

다음 세션을 여는 Claude 는 아래 순서로 진입:

1. [ ] `cat docs/ai-3d-builder/README.md` — 전체 맥락
2. [ ] `cat docs/ai-3d-builder/04-session-2026-04-21-ultrathink.md §7` — 에이전틱 재설계 배경
3. [ ] `cat docs/ai-3d-builder/threejs-scene/p062/decisions.md` — MVP 버그·교훈
4. [ ] `cat docs/ai-3d-builder/05-claude-api-roadmap.md` — tool mapping·비용
5. [ ] `cat docs/ai-3d-builder/06-agent-implementation-phases.md` (이 문서) — Phase × Step
6. [ ] 사용자에게 "Phase 1 부터 시작?" 확인
7. [ ] 확정 후 Step 1.1 `extract_sheet` 함수화 착수

---

## 가정 · 미결 질문

- **모델 버전**: claude-opus-4-7 지속 사용 vs sonnet-4-6 으로 비용 절감 실험? — Phase 2 Step 2.3 에서 A/B.
- **Gemini 대체**: Gemini 3.1 flash-image-preview 중단되면? — `extract_sheet` 의 `model` 인자로 Claude Sonnet vision 도 시도 가능하도록 설계.
- **로컬 실행 vs 클라우드**: Playwright headless 는 로컬 필수. 클라우드 이전 시 별도 Docker 이미지.
- **MCP vs Agent Skill Kit 우선순위**: 현재는 MCP 가 더 성숙. 하지만 Agent Skill Kit 의 managed-agent 기능이 완성되면 전환 고려.

---

## 참고 링크

- `01-evidence.md` — Vision 모델 정확도 벤치마크
- `02-options.md` — 하이브리드(B)와의 비교
- `04-session-2026-04-21-ultrathink.md` — 에이전틱 재설계 원안
- `05-claude-api-roadmap.md` — 이식 전략 (상위)
- `threejs-scene/p062/decisions.md` — MVP 실측 버그 목록 (필독)
