# 05. Claude API 이식 로드맵 (프로덕션 경로)

> **상태**: 설계 문서. MVP(Claude Code를 에이전트로 사용)에서 Gate 1·4·5·6이 모두 pass 판정된 후 진행 판단.
>
> **범위**: 이 문서는 **설계만** 담는다. 실 구현은 별도 세션에서, 아래 "이식 조건" 이 충족되었을 때.

---

## 왜 이식이 필요한가

MVP는 Claude Code 세션(Opus 4.7, 1M ctx) 자체를 에이전트로 사용한다. 단점:

1. **자동화 불가** — 사용자가 매 턴 Claude Code를 실행·관찰해야 함. 서비스화하면 사용자가 매번 Claude Code를 열 수 없다.
2. **비용·토큰 가시성 부족** — 세션 단위 합계만 보임. 건별(도면 1건당) 비용 측정이 어렵다.
3. **로깅·재현성** — 대화 스레드가 곧 로그. 프로덕션에서는 구조화된 감사 로그가 필요하다.
4. **툴 경계 모호** — Claude Code의 내장 툴(Read/Write/Bash/Edit/Glob/Grep/Chrome DevTools MCP) 전부 노출. 프로덕션 에이전트는 **필요한 툴만** 선별 노출해 사고 반경 제한.

Claude API + Agent SDK로 이식하면 위 네 가지가 해결된다. 대신 **툴 정의·프롬프트 설계·루프 제어**를 직접 써야 한다.

---

## 이식 시점 (Go / No-Go)

MVP 완료 후 `threejs-scene/p062/decisions.md` 의 Gate 판정을 본다.

| 조건 | 판정 | 조치 |
|---|---|---|
| Gate 1·5·6 모두 ✅ | Go | Agent SDK 이식 개시 |
| Gate 1 ⚠️/❌ | No-Go | 추출 파이프라인(좁은 프롬프트 체인, consensus 전략) 먼저 보강 |
| Gate 5 ⚠️/❌ | No-Go | Three.js 빌더를 Claude Code가 아닌 **결정론 스크립트(02 Option B)** 로 전환. 이식 불필요. |
| Gate 6 ⚠️/❌ | Hold | 피드백 루프가 미작동이면 사람 검수 단계를 에이전트 루프 중간에 끼워 넣는 하이브리드 |

---

## Tool Surface 매핑

MVP 세션에서 실제로 사용된 동작을 Claude API 기반 Agent SDK의 툴로 매핑한다.

| MVP 동작 (Claude Code) | 프로덕션 (Anthropic SDK) | 구현 |
|---|---|---|
| Read / Write / Edit | `text_editor_20250124` 내장 tool | Anthropic SDK가 제공. `tool_use` block으로 호출 |
| Bash (`python scripts/*.py`) | `bash_20250124` 내장 tool | 동일 |
| Glob / Grep | custom tool `list_files`, `grep_files` | Python `pathlib`/`re` wrap |
| Gemini API 호출 (`test_gemini.py`) | custom tool `extract_sheet` | `google-genai` SDK wrap. 파라미터: sheet_id, stage, fallback_model |
| build_kb_sheet 실행 | custom tool `build_kb` | 기존 Python 스크립트를 함수로 리팩터 후 직접 호출 |
| Chrome DevTools MCP `navigate_page`·`take_screenshot` | custom tool `render_preview` | Playwright 기반 headless Chromium |
| 사용자 문답 | custom tool `ask_human` | 콜백 함수로 구현 (배포 시 Slack/UI 통합) |
| 세션 상태·결정 로그 | custom tool `log_decision` | JSONL 파일 append |

**핵심 원칙**: 툴은 **현재 MVP 세션에서 실제로 호출된 것만** 정의한다. 가상 툴은 추가하지 않는다.

---

## Agent 루프 Pseudocode

```python
# Python (Anthropic SDK 기반)
from anthropic import Anthropic

client = Anthropic()
conversation = [{"role": "user", "content": SYSTEM_GOAL}]

tools = [
    {"type": "text_editor_20250124", "name": "str_replace_editor"},
    {"type": "bash_20250124", "name": "bash"},
    {"name": "extract_sheet", "description": "...", "input_schema": {...}},
    {"name": "build_kb", "description": "...", "input_schema": {...}},
    {"name": "render_preview", "description": "...", "input_schema": {...}},
    {"name": "ask_human", "description": "...", "input_schema": {...}},
    {"name": "log_decision", "description": "...", "input_schema": {...}},
]

for step in range(MAX_STEPS):  # 50 정도
    resp = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=tools,
        messages=conversation,
        system=SYSTEM_PROMPT,
    )
    conversation.append({"role": "assistant", "content": resp.content})

    if resp.stop_reason == "end_turn":
        break

    tool_results = []
    for block in resp.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)  # dispatch to handler
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result),
            })
    conversation.append({"role": "user", "content": tool_results})

    # 예산 체크
    total_tokens = sum(t.usage.input_tokens + t.usage.output_tokens for t in ...)
    if total_tokens > BUDGET_TOKENS:
        ask_human("예산 초과: 계속할까?")
```

**Prompt caching**: `system` 블록 + 초기 few-shot 예시는 `cache_control: {"type": "ephemeral"}` 로 캐시. 툴 정의도 캐시. 재호출마다 90%+ 할인.

---

## 시스템 프롬프트 초안

```
당신은 건축 도면을 읽어 Three.js 3D 를 생성하는 에이전트입니다.

## 목표
사용자가 지정한 시트(예: arch_p062) 의 도면 정보를 최대한 3D 로 재구성합니다.

## 가용 자원
- knowledge-base/sheets/*.yml: 시트 요약 (extract_sheet 로 새로 만들거나 갱신)
- knowledge-base/level-stack.yml: 층 mm 좌표
- outputs/*/stage-10-parsed.json: 과거 추출 결과
- threejs-scene/{sheet_id}/: 3D 산출 디렉토리

## 작업 원칙
1. 먼저 KB 를 확인 (list_files → str_replace_editor 로 읽기). 이미 있으면 재추출 안 함.
2. KB 부족 시 extract_sheet 호출. 1차 gemini-3.1-flash-image-preview, 실패 시 자동 fallback.
3. Three.js 코드는 점진적으로 작성·렌더·확인. 매 수정 후 render_preview → 원본과 비교.
4. 그리드 매칭 안 되는 요소는 누락 허용 (polygon_grid 2점 이하). log_decision 으로 이유 기록.
5. 애매하면 ask_human. 너무 자주 묻지 말 것 — 합리적 추정으로 진행.

## 종료 조건
- render_preview 결과가 원본 도면과 "주요 실·층 스택·외곽" 일치 판단 시.
- 또는 MAX_STEPS 도달.

## 출력 계약
- threejs-scene/{sheet_id}/index.html: 자립 실행 (file:// 외 로드는 js-yaml CDN, three.js CDN).
- threejs-scene/{sheet_id}/decisions.md: 결정 로그.
- knowledge-base/ 아래 파생물 업데이트.
```

---

## 예상 비용 (MVP 1건 기준 추정)

| 항목 | 단가 (현 가격) | 예상 사용 | 비용 |
|---|---|---|---|
| Gemini 3.1 flash-image-preview 추출 × 1~3회 | $0.00125/1k in, $0.005/1k out | 1.5k in, 4k out | ≈$0.02/회 × 3 = $0.06 |
| Claude Opus 4.7 Agent 루프 (10~30 turn) | $15/M in, $75/M out | 100k in (캐시 90% 할인), 20k out | ≈$0.15 + $1.5 = $1.65 |
| Prompt cache 기여 | 캐시 적중률 70% 가정 | | 절감 반영됨 |
| **합계 1회 MVP 실행** | | | **$1.5~3** |

주의:
- 실측 아님. 루프 턴 수가 관건. MVP 세션에서 로그 수집 후 재계산.
- 한 건물 전체(15 시트)면 곱절. 비용 상한 `BUDGET_TOKENS` 필수.

---

## 이식 단계 (MVP 성공 판정 후)

1. **툴 정의 확정** (0.5일)
   - MVP 세션에서 사용된 Read/Write/Bash 패턴을 로그로 추출 (별도 후속 세션에서 `.claude` 로그 파싱).
   - 위 "Tool Surface 매핑" 표를 기준으로 JSON schema 작성.

2. **`agent.py` 스켈레톤** (0.5일)
   - 위 pseudocode를 실행 가능 Python 으로. `docs/ai-3d-builder/scripts/agent.py`.
   - 외부 의존: `anthropic`, `google-genai`, `playwright`, `pyyaml`.

3. **시스템 프롬프트 1회차 실측** (0.5일)
   - p062 로 Agent 실행. 로그 수집. 예산·턴·성공 여부.
   - 결과가 MVP(Claude Code)와 **동등 이상** 이면 이식 성공.

4. **확장** (1~2일)
   - 다른 시트(p060, p061 등)로 일반화.
   - MCP 서버화(선택): `extract_sheet`·`render_preview` 를 외부 MCP 서버로 빼서 Claude Code·Agent SDK 양쪽에서 쓰도록.

5. **모니터링·감사** (0.5일)
   - JSONL 로그를 보기 편한 UI(예: /insight/lab 유사) 로 시각화.

---

## 이식하지 않는 것 (의식적 비이식)

- **전체 자율성** — `ask_human` 은 유지. 100% 자율 에이전트는 서비스 품질 보장 불가.
- **멀티 에이전트** — orchestrator + worker 분할은 현 단계에서 과잉. 필요 시 후속.
- **DB/스토리지 의존** — KB 는 YAML 파일 유지. DB 필요성 생기면 그때.
- **실시간 협업** — 여러 사용자 동시 편집은 범위 밖.

---

## 참고 · 관련 문서

- `04-session-2026-04-21-ultrathink.md` §4 "Agentic 재설계 — 4개 레이어"
- `01-evidence.md` — Vision 모델 정확도 근거
- `02-options.md` — 하이브리드(B) 와의 비교
- MVP 결과: `threejs-scene/p062/decisions.md` (작성 예정)
