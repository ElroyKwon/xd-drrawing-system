# 04. 2026-04-21 세션 — 실측·재설계 (Ultrathink)

> **핵심 반전**: 이 세션의 전반부는 "pipeline 최적화"였다. 후반부 사용자 질문으로 근본 프레임이 잘못됐음을 확인 — **3D 생성은 pipeline 문제가 아니라 agentic 시스템 문제**. 다음 세션부터는 agentic 관점으로 재출발.

---

## 0. 이 세션이 끝난 시점 상태 (다음 세션 시작 앞)

- **진행된 것**: baseline(2시트 × 2모델) + B/C/D/A 4개 treatment 실측 + 정량 비교 매트릭스 완성
- **드러난 것**: "많이 추출"은 3D에 무의미. 앵커율이 진짜 지표. 단일 파이프라인 접근의 한계 명확.
- **패러다임 전환**: linear pipeline → agentic system (사용자 지시, 이 문서에서 다룸)
- **다음 세션 첫 행위**: 이 문서 § 7 "다음 세션 권장 경로" 읽고 진입

---

## 1. 오늘 실행한 실험 매트릭스

2장의 시트 (`arch_p060` = 지상1층+PIT 확대평면도, `arch_p062` = 지상2층+옥탑) × 6 treatment.

### Treatment 정의

| 약칭 | 뜻 | 구현 |
|---|---|---|
| Baseline Opus | 단일 호출, 전체 이미지 → 전체 schema | `test_advisor.py --mode opus` |
| Baseline Gemini | 단일 호출, Gemini 3.1 flash-image-preview | `test_gemini.py` |
| B (hop2) | Gemini가 Opus 결과를 `--reference`로 받아 정정 → 그 결과를 다시 Opus가 `--reference`로 받아 정정 (round-trip) | `test_advisor.py --reference` (이 세션에서 추가) |
| D (Multistage) | stage-10을 4개 서브프롬프트(grid/rooms/dimensions/objects)로 분리, 병렬 호출, 병합 | `test_multistage.py` |
| C (Consensus) | Opus baseline + Gemini baseline JSON을 union merge (이름 키, 그리드 완전성 기반) | `test_consensus.py` |
| A (Critique) | D 결과를 Canvas로 렌더 → 원본 + 렌더 PNG + JSON을 Opus에 보내 정정 요청 | `test_critique.py` |

### 정량 결과

#### p060 (지상1층 + PIT 확대평면도)

| Treatment | views | rooms | walls | cols | dims | 앵커 | % 앵커 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline Opus | 2 | 9 | 7 | 0 | 48 | 17 | 35% |
| Baseline Gemini | 2 | 7 | 12 | 20 | 47 | 47 | **100%** |
| B hop2 | 2 | 9 | 11 | 0 | 79 | 18 | 23% |
| D Multistage | 2 | 9 | 19 | 16 | **119** | 15 | 13% |
| C Consensus | 2 | **10** | 16 | 20 | 89 | **63** | 71% |
| A Critique | 2 | 9 | 0 | 0 | 24 | 19 | 79% |

#### p062 (지상2층 + 옥탑 확대평면도)

| Treatment | views | rooms | walls | cols | dims | 앵커 | % 앵커 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline Opus | 2 | **22** | 8 | 0 | 49 | 20 | 41% |
| Baseline Gemini | 2 | 14 | 8 | 24 | 80 | 20 | 25% |
| B hop2 | 2 | 19 | 8 | 0 | 66 | 20 | 30% |
| D Multistage | 2 | 15 | 10 | 26 | 88 | 13 | 15% |
| C Consensus | 2 | 21 | **12** | 24 | **110** | **40** | 36% |
| A Critique | 2 | 15 | 12 | 26 | 88 | 20 | 23% |

### 관찰

1. **Gemini는 앵커율↑, 항목수↓. Opus는 반대**. 상호 보완 관계 존재 → C(consensus)가 양 지표 모두 상위권.
2. **D Multistage는 양이 최다지만 앵커율 최저**. 4개 서브프롬프트가 독립적으로 이미지만 보기 때문에 grid 맥락 공유 실패. 4-stage chaining이었으면 다른 결과였을 것.
3. **A Critique는 pruning-biased**. "이미지2와 다른 부분 교정" 지시를 "확신 없으면 제거"로 해석. coverage 손실.
4. **B round-trip 미미**. Gemini ref hop1에서 추가된 것들이 Opus ref hop2에서 일부 제거됨. 2모델 ping-pong이 단순 합의보다 수렴에 약함.

### 폐기된 실험

- **크롭 실험 (B 원안)**: `crop_subfigures.py`로 p060을 `p060_pit` + `p060_main`으로 사전 분할 후 각각 추출 → 크롭 경계가 p060 실제 레이아웃(수평 3분할: 타이틀블록/PIT 평면/본 평면)과 안 맞아 오히려 품질 저하. `_crops/p060_*.png`는 유지하되 B는 round-trip으로 재정의.

---

## 2. 실측에서 드러난 정량 지표의 함정

### 앵커율이 진짜 품질 지표

치수 119개 뽑아도 87%가 `{text: "4500", from_grid: null, to_grid: null}`이면 3D 렌더러가 그릴 수 없다 — "어디 사이" 정보가 없어 좌표 계산 불가. 반면 앵커된 치수 40개는 모두 그릴 수 있다.

따라서:
- **카운트 지표**: rooms/walls/dims 총량
- **품질 지표**: `grid-anchored %` (즉, polygon_grid가 valid labels로 채워진 실, path_grid가 valid labels로 채워진 벽, from/to_grid가 채워진 치수)

이 세션까지 썼던 final_report.html은 카운트 중심. **다음 세션의 리포트에서는 anchored count를 primary metric으로**.

### "실 수 22개"가 좋은 신호가 아닐 수도 있음

p062 Baseline Opus가 실 22개를 뽑았는데, 같은 도면에서 Gemini는 14개. 22 - 14 = 8이 다 진짜 실인지, Opus의 환각인지 확인 안 함. **ground truth 부재**가 구조적 한계. 다음 세션에서 한 시트라도 수작업 정답 JSON을 만들어야 precision/recall 측정 가능.

---

## 3. 사용자 질문으로 드러난 근본 프레임 오류

세션 중반, 사용자 질문 요지:

> "2D 그림이 3D 그림을 그리는데 정확하게 도움이 되도록 가야하는 방향이잖아. 그렇게 하기 위해서 어떻게 해야하는데?"
> "결국 몇장에 같은 영역을 보여주는지?"
> "도면 여러 장을 받아서 ai-api가 **코딩까지** 해줘야 하는 상황이란 말이지"
> "전체적인 작성 방법에 대해서 플로우는 생각하면서 하는거야?"
> "이미지 분석, 코딩 모두 ai-api를 사용해서 **에이전틱 기법으로 우리가 제공하는 tool을 자유롭게 쓰면서** 보도록 해줘야 한다는거지"
> "각 이미지를 그림을 그리기 위해 최적의 프롬프트로 **최대한 많은 자료를 수집해놓고** 에이전틱하게 ai가 첫장을 그리는데 관련 **yaml 파일들을 보면서 wiki 데이터처럼 활용**해서 몇 장을 더 보겠다, 더 코딩하겠다 등의 **판단과 코딩**이 되도록 해줘야 한다"

### 이게 왜 중요한가

내가 제안했던 "Grid-locked 순차 추출 파이프라인"은:
- 미리 정해진 4단계를 경직되게 실행
- 각 단계 입출력이 고정
- 사람이 쓴 코드가 AI를 지시함

사용자가 말한 건:
- **AI 자체가 에이전트**. 목표("이 건물 3D 만들어라") 받고 **스스로 플래닝**
- 주어진 툴(이미지 상세 조사, KB 쿼리, 코드 작성·실행)을 재량껏 호출
- **시트 1장 보고 "이거 부족해, 2F 단면도 더 봐야 해" 판단하고 다른 시트 요청**
- 사전 추출된 YAML wiki를 context로 참조 (모든 이미지 re-process 안 함)
- 코딩도 AI가 — Three.js 모듈 직접 작성·실행·수정

이는 pipeline이 아니라 **agentic system**의 설계 문제. Claude Agent SDK / MCP / tool use의 영역.

### 파이프라인 vs 에이전틱 — 이 프로젝트에 주는 영향

| 항목 | Pipeline (기존) | Agentic (재설계) |
|---|---|---|
| 추출 전략 | 고정 (grid→rooms→dims→objects) | 가변 (에이전트가 "지금 필요한 건" 판단) |
| 시트 순서 | 미리 정한 순서로 전부 처리 | "먼저 plan 보고, 필요하면 section 불러" |
| 검증 | 사후 stats | 즉시 (에이전트가 `cross_check` 툴 호출) |
| 코드 생성 | 결정론 generator 스크립트 | 에이전트가 Three.js 코드 직접 작성 |
| 사람 개입 | 실험 실행자 | 에이전트가 `ask_human` 호출할 때만 |
| 재사용성 | 스크립트별 one-off | KB + 툴이 세션 간 축적 |

---

## 4. Agentic 재설계 — 4개 레이어

### Layer 1: Knowledge Base (사전 추출된 wiki)

**목적**: 에이전트가 이미지 하나하나 re-process 안 하고 "이 도면에 뭐 있는지" 즉시 조회.

**구성**:
```
knowledge-base/
  sheets/
    arch_p060.yml         # 시트 메타 + 추출된 feature 요약
    arch_p062.yml
    ...
  indexes/
    floor_to_sheets.yml   # "지상2층" → [arch_p062#v1, arch_p103#v2, ...]
    symbol_to_sheets.yml  # "계단 T01" → [sheets that mention]
    grid_to_sheets.yml    # 그리드 라벨 공유 시트 군집
    datum_to_sheets.yml   # FL±0 = EL+94.20 설정한 시트
    drawing_stack.yml     # 층 스택 순서 + FL 좌표
  cross_refs/
    vertical_cores.yml    # 층 간 관통 코어 일관성 체크 결과
    grid_consistency.yml  # 층 간 그리드 일치 여부
```

**시트 YAML 예시** (`arch_p060.yml`):
```yaml
sheet_id: arch_p060
sheet_number: A04.01
source_png: dwg/1) 건축공사/0. PDF 도면/_png_dpi400/arch_p060.png
discipline: architectural
views:
  - view_id: v1
    view_label: 지상1층 확대평면도-1
    view_scale: "1:200"
    floor: 지상1층
    fl_mm: 94200        # annotations_ko 파싱: "1FL±0 FH+94.20"
    grid:
      x_labels: [5, 5B, 6, 7]
      x_spacings_mm: [8125, 2875, 10000]
      y_labels: [A, B, B1, B2, C, D]
      y_spacings_mm: [13000, 6950, 4100, null, 5950, 13000]
      total_x_mm: 21000  # 검증: sum(x_spacings) == 21000?
      grid_valid: true
    anchored_counts:
      rooms: 6
      walls: 4
      dims: 47
    raw_counts:
      rooms: 10
      walls: 16
      dims: 89
    cores:
      - {type: stair, at: [[5,B1],[5B,B2]], penetrates_up: unknown}
    voids: []
    annotations_ko: ["1FL±0 FH+94.20", ...]
  - view_id: v2
    ...
extraction_runs:
  - ts: 2026-04-21_10:00
    method: baseline_opus
    path: outputs/2026-04-21_100010_arch_p060_opus
    global_confidence: 0.65
  - ts: 2026-04-21_11:24
    method: consensus_opus_gemini
    path: outputs/consensus/consensus_p060.json
    global_confidence: 0.7   # best-so-far
```

**빌더**: `scripts/build_kb.py` — 기존 outputs/ 디렉토리 긁어서 위 YAML 자동 생성.

### Layer 2: Tool Surface (에이전트 호출용)

최소 툴셋 (Python 함수 또는 MCP 서버로 제공):

```python
# 조회 도구
list_sheets(filter: {floor?, discipline?, view_type?}) -> list[SheetSummary]
read_sheet(sheet_id: str) -> SheetFull  # YAML 전체
get_cross_refs(element_id: str) -> list[SheetRef]  # 이 코어가 몇 층에 있는지

# 이미지 상세 조사 (lazy — 호출 시점에 Opus/Gemini 호출)
zoom_region(sheet_id: str, region: {bbox_px | grid_range}, focus: str) -> dict
  # 예: "p060 메인평면 구석 4개 실의 문 위치만 상세 추출"
  # AI가 이 툴 쓰면 새 Opus call 발생

# 검증
cross_check(claim: str, sheet_ids: list[str]) -> {verified: bool, evidence: list}
  # "1F에서 계단 위치가 2F와 일치하는가?"

validate_grid(sheet_id: str, view_id: str) -> {valid: bool, issues: list}
  # sum(spacings) == total_dim 검증

# 코드 작성 · 실행
write_code(path: str, content: str)
run_python(path: str) -> {stdout, stderr, exit_code}
run_tsc(path: str) -> {errors: list}
render_preview(html_path: str) -> screenshot_png_path  # Chrome DevTools 자동

# 상호작용
ask_human(question: str, context: dict) -> str  # 애매한 결정만
log_decision(decision: str, rationale: str)
```

**구현 선택지**:
- (A) Python 함수 + 에이전트가 `code_execution` tool로 호출 → 간단
- (B) MCP 서버 (FastMCP 등) → 재사용성, Claude Code 외 환경에서도 쓸 수 있음
- (C) Claude Agent SDK custom tools → 가장 정석

### Layer 3: Agent Runtime

**시스템 프롬프트 (초안)**:
```
너는 건축 도면을 읽어 Three.js 3D 모델을 만드는 에이전트다.

목표: {building_name}의 {scope}를 3D로 재구성하라.
예: "프로젝트 S동의 지상1~2층 + 옥탑 매싱 3D"

자원:
- knowledge-base/ 에 사전 추출된 시트 요약이 있다 (list_sheets, read_sheet로 조회)
- 필요시 zoom_region으로 특정 영역 상세 추출 (비용 발생)
- 코드를 write_code / run_* 로 작성·실행하여 검증할 수 있다
- 애매하면 ask_human

작업 원칙:
1. 먼저 list_sheets로 어떤 시트가 있는지 파악
2. 층 스택 / 그리드 일관성 validate_grid + cross_check로 확인
3. 불확실하면 zoom_region. 여전히 애매하면 ask_human.
4. 3D 코드는 점진적으로. 매 단계 render_preview로 시각 확인.
5. 의사결정은 log_decision으로 남길 것.

출력물:
- 최종 Three.js HTML (threejs-scene/index.html)
- 결정 로그 (threejs-scene/decisions.md)
- KB 업데이트 사항 (새로 발견한 사실들)
```

**실행 방식 (선택지)**:
- (a) Claude Code를 그대로 에이전트로 사용 — 이 세션처럼. 단점: 사람이 승인·프롬프트
- (b) Anthropic Agents API / Agent SDK 기반 별도 세션 — 자율 실행, 비용 관리 용이
- (c) 두 층: 큰 결정은 사람 세션, 자잘한 실행은 하위 agent SDK 호출

### Layer 4: Feedback Loop

- 에이전트가 Three.js 생성 → `render_preview` → 스크린샷 → **자기 자신에게** 비판 요청
- "내가 만든 3D가 원본 도면과 다른 점은?" → 교정 사이클
- 종료 조건: 에이전트가 "충분하다" 판단 또는 사람이 정지

---

## 5. 이 세션에서 유산으로 남는 artifact

### 유지할 스크립트 (재사용 가능)

| 파일 | 역할 | 다음 세션 쓸모 |
|---|---|---|
| `scripts/test_advisor.py` | Opus/Haiku/Advisor 단일 호출. `--reference` 추가됨 | Agentic 툴 `zoom_region`의 기본 호출 엔진 |
| `scripts/test_gemini.py` | Gemini 호출. `--reference` 기본 지원 | Agentic 툴의 백업 모델 |
| `scripts/test_multistage.py` | 4단 병렬 | 버리고 대신 chained 버전 재작성 예정 |
| `scripts/test_consensus.py` | JSON union merge | KB 병합 로직의 기초 |
| `scripts/test_critique.py` | Render-and-Critique | Layer 4 피드백 루프의 원형 |
| `scripts/build_viewer.py` | 단일 시트 viewer (원본+Canvas) | validation 툴에서 재사용 |
| `scripts/build_viewer_multi.py` | 다중 시트 비교 viewer | 동일 |
| `scripts/build_canvas_only.py` | Canvas-only 렌더 (critique 입력용) | `render_preview` 툴의 기초 |
| `scripts/build_final_report.py` | 매트릭스 비교 리포트 | 재사용 low, 실험별 one-off |
| `scripts/crop_subfigures.py` | PNG 크롭 | `zoom_region` 툴의 이미지 전처리 |

### 추출 결과물 (outputs/)

- 12 디렉토리 (p060/p062 × 6 treatment)
- `consensus/consensus_p060.json`, `consensus_p062.json`
- `critique/p060_critiqued/`, `p062_critiqued/`
- `final_report.html` — 비교 매트릭스 (Chrome에서 열어볼 것)
- `crop_check.html`, `multi_p060_crops_*.html` — 폐기 실험 흔적

### 프롬프트

- `prompts/00-standard-classifier.md` — 시트 분류 (discipline + view_type)
- `prompts/10-architectural-plan.md` — 건축 평면도 추출 스키마

**다음 세션에서 추가할 것**:
- `prompts/11-grid-locked.md` — 그리드만 먼저 뽑는 좁은 프롬프트
- `prompts/12-slab-polygon.md` — 층 외곽 폴리곤 전용
- `prompts/13-cores-and-voids.md` — 수직 관통 요소 전용
- `prompts/20-critique-additive.md` — 삭제 금지, 추가·정정만 하는 critique 프롬프트

---

## 6. 데이터셋 — 아직 확인 안 한 것

`dwg/1) 건축공사/0. PDF 도면/_png_dpi400/` 에 존재하는 페이지:

- arch_p001 ~ p005 (확인 안 함 — 타이틀? 색인?)
- arch_p060 ~ p064 (평면도 블록)
- arch_p118 ~ p122 (미확인 — 아마 입면도/단면도)

**다음 세션 1번 작업**: 이 모든 페이지 stage-00 classifier로 돌려 KB 기본 라벨 부착. 
- 입면도 / 단면도 / 상세도 / 색인 / 일반도 등 식별
- 입면도·단면도가 있으면 **층 FH·슬라브 두께·지붕 형상**이 그 안에 있음 → 3D 완성도 급증

`dwg/1) 전기공사/`, `dwg/2) 통신공사/` 는 일단 건축만 잡는 동안 후순위.

---

## 7. 다음 세션 권장 경로

### 첫 30분 (궤도 진입)
1. `cat docs/ai-3d-builder/04-session-2026-04-21-ultrathink.md` — 이 문서
2. `cat docs/ai-3d-builder/02-options.md` — 아키텍처 A/B/C 선택지 (이번 ultrathink 이후 맥락에서 재검토)
3. 사용자 합의: "agentic 아키텍처 Phase 1 착수"를 확정할지, 아니면 `_png_dpi400/` 데이터셋 먼저 훑을지

### 권장 순서 (2~3 세션 분량)

**Session N+1 (Knowledge Base 재료)**
- [ ] `_png_dpi400/` 전체 stage-00 classifier 일괄 (25~30장)
- [ ] 입면도·단면도 존재 여부 확인
- [ ] stage-10 프롬프트 재설계 → grid/slab/cores만 뽑는 좁은 버전 (11·12·13)
- [ ] annotation 파서 (FL·FH 숫자 추출) 작성
- [ ] 결과물 YAML화 (Layer 1 sheets/)

**Session N+2 (Knowledge Base 인덱스 + Tool 정의)**
- [ ] 교차 인덱스 빌더 (floor/symbol/grid/datum)
- [ ] 층간 일관성 체커 (cross_refs/)
- [ ] 툴 API 스펙 확정 (Python 함수 시그니처)
- [ ] 최소 툴셋 구현 (list_sheets, read_sheet, validate_grid, cross_check)

**Session N+3 (Agent 시범 실행)**
- [ ] 시스템 프롬프트 완성
- [ ] Claude Code에서 수동으로 에이전트 시뮬레이션 (툴 호출 → 결과 → 다음 판단)
- [ ] 최소 3D 산출 (슬라브 + 코어만, 내부 decoration 없음)
- [ ] render_preview로 확인

**Session N+4 이후**
- 필요시 Agent SDK로 마이그레이션
- 내부 decoration 추가
- 전체 건물 스택 확장

### 열린 질문 (사용자 결정 필요)

1. **에이전트 런타임**: Claude Code 안에서 수동 시뮬레이션으로 시작할까, 처음부터 Agent SDK?
2. **비용 관리**: 한 3D 산출당 얼마까지 허용? (Opus + Gemini 섞어 쓰면 $10~30 예상)
3. **Ground truth**: 수작업 정답 JSON을 어느 시트에 만들까? (p060 추천 — 크지 않음)
4. **Tool surface 공개 범위**: MCP 서버로 만들어 Claude Code 외에서도 쓸 수 있게 할지, 아니면 이 프로젝트 내부용만?
5. **실패 처리**: 에이전트가 "이 시트는 못 읽겠다" 판정 시 어떻게? 사람에게 에스컬레이션? Skip?

---

## 8. 이 세션의 잘못된 프레임 (기록용 — 반복 금지)

후세 Claude가 다시 이 실수 안 하도록:

1. ❌ **"파이프라인 최적화로 3D 품질 올리기"** — 이게 3D-builder의 방향이 아니다.
2. ❌ **"stage-10 스키마에 모든 것을 넣기"** — 3D가 필요로 하는 건 그 중 일부. 나머지는 장식.
3. ❌ **"추출 수량 많으면 좋다"** — 앵커율 없으면 무의미.
4. ❌ **"사람이 파이프라인을 orchestrate"** — AI가 에이전트로서 orchestrate 해야 한다 (사용자 원안).
5. ❌ **"크롭해서 좁게 보기"** — 크롭 경계를 사람이 하드코딩하면 도면 레이아웃 안 맞는다. 에이전트가 `zoom_region` 동적으로 호출하게 해야.

---

## 9. 이 세션에서 확립된 긍정적 교훈

1. **Opus와 Gemini는 상호보완**. Consensus가 단순 union인데도 둘 단독보다 상위. 에이전트 툴은 두 모델 다 제공할 것.
2. **앵커율이 KPI**. 카운트보다 우선.
3. **Render-and-Critique 개념은 유효**, 프롬프트가 문제. "ADD-only" 버전으로 재시도 가치.
4. **참조주입(`--reference`) 기법은 쓸 만함**, 특히 Gemini가 Opus 결과 정정하는 방향 (hop1). Opus → Gemini → Opus 전체 round-trip은 효과 미미.
5. **Canvas 렌더러는 에이전트의 눈이 된다**. build_canvas_only.py가 Layer 4 피드백 루프의 핵심 부품.

---

## 부록 A: 오늘 실행한 커맨드 로그 (요약)

```bash
# 1. --reference 추가 후
python scripts/test_gemini.py <p060.png> --reference <opus_baseline_p060.json>  # hop1
python scripts/test_gemini.py <p062.png> --reference <opus_baseline_p062.json>  # hop1
python scripts/test_advisor.py <p060.png> --mode opus --reference <gemini_ref.json> --tag-suffix _ref_hop2  # hop2
python scripts/test_advisor.py <p062.png> --mode opus --reference <gemini_ref.json> --tag-suffix _ref_hop2  # hop2

# 2. Multistage
python scripts/test_multistage.py <p060.png> --mode opus
python scripts/test_multistage.py <p062.png> --mode opus

# 3. Consensus (API 호출 없음, 순수 merge)
python scripts/test_consensus.py <opus_baseline_p060.json> <gemini_baseline_p060.json> consensus/consensus_p060.json
python scripts/test_consensus.py <opus_baseline_p062.json> <gemini_baseline_p062.json> consensus/consensus_p062.json

# 4. Critique
python scripts/build_canvas_only.py <multistage_p060.json> critique/p060_rendered.html
# Chrome으로 screenshot → p060_rendered.png
python scripts/test_critique.py <p060.png> critique/p060_rendered.png <multistage_p060.json> critique/p060_critiqued

# 5. 최종 리포트
python scripts/build_final_report.py outputs/final_report.html
```

## 10. 2D 용도 vs 3D 용도 — 정보 요구가 다르다 (세션 말미 핵심 추가)

오늘 실측으로 확인된 것: 같은 시트에서 **2D 용도로 필요한 정보**와 **3D 용도로 필요한 정보**는 상당 부분 겹치지 않는다. 에이전트가 도구를 쓸 때 목적에 따라 호출이 달라져야 한다.

### 10.1 2D 용도 (도면 자체를 디지털화 / 검색 / 보존)

목표: "이 시트가 뭘 말하는지 구조화된 데이터로 읽어내기". 검색·라벨링·주석·레거시 재활용.

| 필요한 것 | 현재 추출 상태 | 주 모델 |
|---|---|---|
| 실명 + 실번호 (텍스트 라벨) | 양호 (14~22개 per view) | Opus |
| 실의 대략적 위치 (셀 단위) | 양호 | Opus |
| 치수 텍스트 값 (mm) | 많음 (48~119개) | Opus / Gemini |
| 주석 텍스트 (`annotations_ko`) | 양호 | Opus |
| 기호 식별 (계단·EV·PS·void) | 양호 | Gemini (기둥·shaft 탐지 우수) |
| 시트번호 / 도면번호 | 양호 | 둘 다 |
| 도면유형 분류 | stage-00 classifier로 해결됨 | — |

**관측**: 2D 디지털화에는 **지금 파이프라인(baseline + consensus)이 거의 충분**. 앵커율 낮아도 텍스트 라벨링 용도면 무관.

### 10.2 3D 용도 (기하학적 복원)

목표: "이 시트의 정보로 3D 메쉬를 생성". 좌표계 + 폴리곤 + 수직 관통체 + Z 스택.

| 필요한 것 | 현재 추출 상태 | 주 모델 |
|---|---|---|
| **그리드 (라벨 + mm 간격)** — 모든 좌표의 기준 | 부분적. 앵커율 13~100% 들쭉날쭉 | **Gemini** (p060에서 100% 앵커) |
| **층 외곽 폴리곤** — 슬라브 footprint | **추출 안 함** (별도 프롬프트 필요) | 미정 |
| **FL mm 좌표** — Z 스택용 | `annotations_ko`에 텍스트로만 (`FH+94.20`) — 파싱 미적용 | Opus (텍스트 정확도↑) |
| **FFH (층간 높이)** — 두 FL의 차 | 계산 로직 없음 | 계산만 |
| **코어 폴리곤 (계단·EV·PS·void)** — 수직 관통 | 일부 추출, 층간 일관성 검증 없음 | Gemini (기호 탐지) |
| **슬라브 두께·지붕 형상** | **단면도·입면도 필요** (평면도에 없음) | 별도 시트 필요 |
| **그리드 일관성 (층간)** — 같은 건물은 같은 그리드 | 검증 없음 | 계산만 |

**관측**: 3D에는 **좁은 고품질** 추출이 필수. 현재 넓고 얕은 추출은 3D 용도로 거의 무용.

### 10.3 두 용도의 도구 분리

에이전트 툴 설계 시 둘을 섞지 말 것:

```python
# 2D 용도 툴 (범용 추출)
extract_sheet_comprehensive(sheet_id) -> full_schema  # 현재 stage-10

# 3D 용도 툴 (좁고 정확)
extract_grid_only(sheet_id, view_id) -> grid_with_validation
extract_slab_polygon(sheet_id, view_id) -> closed_polygon
extract_cores(sheet_id, view_id) -> list[core]
extract_voids(sheet_id, view_id) -> list[void]
parse_fl_from_annotations(sheet_id) -> fl_mm
```

2D 용도 호출 한 번으로 3D까지 해결하려 하지 말 것. 목적별로 프롬프트·검증·파서를 분리해야 각 용도에서 90%+ 정확도 확보 가능.

---

## 11. 다중 시트 종합 전략 — 한 장으로 안 되는 것을 풀기

한 장의 평면도만으로는 3D를 만들 수 없다. 다음이 평면도 **혼자서는 주지 않는** 정보:

| 정보 | 어느 시트가 주는가 |
|---|---|
| 슬라브 두께 | 단면도 / 상세도 |
| 지붕 형상·경사·파라펫 | 옥탑 평면도 + 단면도 |
| 외벽 재료·마감 | 입면도 + 상세도 |
| 창호 높이·크기 | 창호표 + 입면도 |
| 천장고 | 단면도 / RCP (반자평면도) |
| 기초 관계 | 기초 평면도 + 단면도 |
| 설비 위치 | 설비 평면도 (별도 discipline) |

### 11.1 시트 간 관계 카탈로그

한 층(예: 지상2층)을 3D로 만들려면 **여러 시트가 동일 영역을 다른 각도·축척으로** 보여준다:

```
지상2층 3D를 위해 참조할 시트들:
├─ arch_p062 (지상2층 확대평면도)    ← 평면 좌표·실 배치
├─ arch_p???  (2층 천장평면도 RCP)    ← 천장고
├─ arch_p???  (단면도 A-A')           ← 슬라브 두께, FFH 확인
├─ arch_p???  (입면도)                ← 외벽, 창호 개구부
├─ elec_p???  (2층 전기 평면도)       ← 조명·콘센트 (3D decoration 원하면)
└─ comm_p???  (2층 통신 평면도)       ← 통신 단말 위치
```

**현재 KB 기준**: `arch_p060` (지상1층+PIT), `arch_p062` (지상2층+옥탑) 만 확보. 나머지는 `_png_dpi400/`에 있을 수 있으나 미확인. **다음 세션 최우선 = 시트 전수조사**.

### 11.2 다중 시트 종합 — 에이전트 관점 실행

에이전트가 "지상2층 3D 만들어라"를 받으면:

```
step 1: list_sheets(floor="지상2층")
   → [arch_p062, arch_p???(2F RCP), arch_p???(section through 2F)...]

step 2: read_sheet(arch_p062) — 평면 좌표 획득
step 3: read_sheet(section) — FFH, 슬라브 두께
step 4: parse_fl_from_annotations(arch_p062) → 99700 mm
step 5: cross_check(
   claim="지상2층 FL = 99700mm",
   sheet_ids=[arch_p060, arch_p062, section])
   → verified (1F 94200 + FFH 5500 = 2F 99700)

step 6: 모든 정보로 3D 코드 생성
step 7: render_preview → 자가 비판 → 수정 → 종료
```

**핵심 디자인**: "이 정보는 어느 시트에서 올 수 있는가"의 맵을 **KB 인덱스로 미리 만든다**. 에이전트는 그 인덱스 보고 최소 시트만 조회.

### 11.3 시트 간 불일치 대응

실세계 도면은 시트 간 불일치가 흔하다:
- 평면도의 벽 위치 ≠ 단면도의 벽 위치 (개정판 차이)
- 한 시트는 FH+94.20, 다른 시트는 FH+94.00 (실수)
- 그리드 라벨 숫자 뒤바뀜

에이전트 정책:
1. `cross_check` 로 검출되면 `log_decision`에 불일치 기록
2. 우선순위 규칙: 평면도 > 단면도 > 입면도 (3D 좌표는 평면이 표준)
3. 중대 불일치면 `ask_human` — 사람 개입
4. 경미한 불일치면 다수결 (3시트 중 2시트 일치하는 값 채택)

### 11.4 KB 인덱스 설계 (구체)

```yaml
# knowledge-base/indexes/floor_to_sheets.yml
지상1층:
  plan: [arch_p060#v1]
  rcp: []                          # 아직 식별 안 됨
  sections_through: []             # 단면도 A-A'이 1F 가로지르는지 미확인
  elevations: []

지상2층:
  plan: [arch_p062#v1]
  rcp: []
  sections_through: []
  elevations: []

PIT:
  plan: [arch_p060#v2]

옥탑:
  plan: [arch_p062#v2]

# knowledge-base/indexes/element_cross_refs.yml
stair_T01:                          # 에이전트가 명명
  appears_in:
    - {sheet: arch_p060#v1, grid: [[5,B1],[5B,B2]], floor: 지상1층}
    - {sheet: arch_p062#v1, grid: [[5,B1],[5B,B2]], floor: 지상2층}
    - {sheet: arch_p062#v2, grid: [[5,B1],[5B,B2]], floor: 옥탑}
  vertical_consistency: verified
  penetrates_floors: [1, 2, R]

# knowledge-base/indexes/datum_consistency.yml
datums:
  GL: EL+94.00
  1FL: EL+94.20
  2FL: EL+99.70
  RFL: EL+104.20
derived_ffh:
  "1F→2F": 5500    # 99700-94200
  "2F→RF": 4500    # 104200-99700
evidence_sheets: [arch_p062#v2_annotations]   # 여기서 datum 텍스트 뽑음
```

이 인덱스가 있으면 에이전트는 이미지를 다시 볼 필요 없이 "지상2층 FL이 몇인지" 즉답 가능.

---

## 12. 결론 — "2D→3D"는 에이전트 × 여러 시트 × KB

세 문장 요약:

1. **도구는 목적별 분리**: 2D 디지털화 툴과 3D 재구성 툴은 프롬프트·검증 로직이 달라야 한다. 한 번에 다 하려 하지 말 것.
2. **한 시트의 정보로는 3D 안 된다**: 최소 평면+단면+입면 셋이 필요. 지금 KB는 평면뿐 → 데이터셋 전수조사가 Phase 1의 실제 시작점.
3. **에이전트가 KB 인덱스를 보고 "어느 시트에서 뭘 가져올지" 스스로 계획**. 사람이 파이프라인을 orchestrate하지 않는다. 에이전트가 `list_sheets → read_sheet → cross_check → zoom_region → write_code → render_preview → critique` 루프를 자율 실행.

## 부록 B: 이 문서가 커버하지 않는 것

- Three.js 코드 아키텍처 (컴포넌트 구조, 머티리얼, 라이팅) — Agent가 결정
- 특정 도면 해석의 디테일 (예: "이 기호는 뭐야?") — KB에 편입되면 거기 문서화
- 비용 견적 — 실측 필요 (에이전트 1회 실행 = ?)
- 실패 모드 카탈로그 — 에이전트 시범 실행 후 수집
