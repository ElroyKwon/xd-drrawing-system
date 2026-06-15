# 01. 리서치 근거 (Evidence)

2026-04-21 웹 리서치 1차. 모든 수치·주장은 출처 링크 포함. 링크 없는 문장은 추론임을 명시.

---

## 1.1 Vision LLM의 엔지니어링 도면 정확도

### 직접 벤치마크 결과

출처: [Businessware Technologies, 2025](https://www.businesswaretech.com/blog/benchmark-testing-ai-models-on-engineering-drawings)
방법: 10장 엔지니어링 도면, 도면당 17~58개 치수. 9개 필드(view name, dimension type, nominal value, tolerance 등) 수동 검증.

| 모델 | 정확도 |
|---|---|
| **Gemini Pro** | **~80%** |
| Gemini Flash | ~77% |
| **Claude Opus** | **~40%** |
| GPT-4o Mini | ~39.6% |
| GPT-o3 | ~20% |
| Qwen VL Plus | ~8% |

### Claude의 실패 패턴 (직접 인용)

1. **Section misassignment**: "occasionally misassign[ed] dimensions to the wrong sections"
2. **View detection weakness**: "weaker performance in associating each dimension with its correct drawing section"
3. **Complex tolerance handling**: "performance degraded significantly on dense annotations and tolerance zones"

### 해당 연구의 개선 권고

- **Model ensemble**: 여러 모델 출력 결합
- **Iterative inference**: 같은 모델, 프롬프트 변주로 여러 번 실행하여 누락 보완

### 사용자 시나리오에 대한 함의

사용자가 요청한 "평면·정면·측면·단면·위에서·아래서 뷰를 순차로 주며 누적" 시나리오는 Claude의 **가장 약한 실패 모드(뷰 간 치수 오배정)**를 정면으로 건드린다. Gemini Pro가 이 작업에서는 **2배 정확**.

> **주의**: 위 벤치마크는 **기계 도면(mechanical)**을 대상으로 했다. **건축 도면** 전용 벤치마크는 2026-04 기준 공개된 것을 찾지 못함. 건축 도면은 표기 밀도가 낮아 조금 더 나을 수도, 다중 뷰 참조가 많아 더 나쁠 수도 있음. **직접 측정 필요**.

---

## 1.2 Claude Opus 4.7의 개선

출처: [LLM-stats Opus 4.7 launch notes](https://llm-stats.com/blog/research/claude-opus-4-7-launch)

- 고해상도 이미지 지원: long edge **최대 2576px** (이전 1568px)
- 이미지당 토큰: **최대 ~4784** (이전 ~1600, 약 3배)
- 복잡한 다이어그램 성능(CharXiv-R): 68.7% → **82.1%**

**해석**: Opus 4.7에서 도면 읽기 성능이 꽤 향상됐을 **가능성**이 있다. 다만 CharXiv-R은 과학 차트 이해 벤치마크이지 **엔지니어링 도면은 아님**. 위 40% 숫자가 Opus 4.7에서도 유지되는지는 **재측정 필요**.

---

## 1.3 2D 다중 뷰 → 3D 복원 — 고전 문제

출처:
- [3D Solid Reconstruction from 2D Orthographic Views (IntechOpen, 2020)](https://www.intechopen.com/chapters/72385)
- [Automatic Reconstruction of 3D Models from 2D Drawings: A State-of-the-Art Review (MDPI, 2024)](https://www.mdpi.com/2673-4117/5/2/42)
- [PlankAssembly (ICCV 2023)](https://openaccess.thecvf.com/content/ICCV2023/papers/Hu_PlankAssembly_Robust_3D_Reconstruction_from_Three_Orthographic_Views_with_Learnt_ICCV_2023_paper.pdf)
- [2D CAD → 3D Parametric Models: Vision-Language Approach (arxiv 2412.11892, 2024)](https://arxiv.org/html/2412.11892v1)

### 확인된 사실

- **1970년대부터 연구된 고전 문제**. 이론은 성숙. 핵심 알고리즘: 뷰 간 엣지 매칭 → 루프 검출 → 면 클러스터링 → 솔리드 복원
- 전통 방법은 **"정확히 3개 축정렬 뷰"**(front, top, side)를 전제. 실도면은 이 조건을 거의 충족 못 함
- 최신 학습 기반(PlankAssembly 등)도 여전히 3뷰 전제가 기본 셋업
- **건축에 특화된 접근**은 평면도(floor plan)를 가장 포괄적 문서로 다루고, 단면·입면은 높이 정보 보완 용도로 사용 → [Automatic layer classification, 2019](https://www.sciencedirect.com/science/article/abs/pii/S0926580519303735)

### 함의

- "LLM이 알아서 3D로 만들어준다"는 매직은 **학계에서도 달성된 바 없음**
- 잘 정의된 입력(그리드 라벨, 척도, 기준점)이 있으면 **결정론 알고리즘으로 풀 수 있음** — 즉, 핵심 어려움은 **추출(extraction)**이지 3D 변환 자체가 아님
- LLM을 쓰더라도 **"도면 → 구조화 데이터 추출"에만 사용**하고 **3D 조립은 결정론 코드**가 맞음

---

## 1.4 상용 AI 도면→BIM 도구 현황 (2026)

출처:
- [Plans2BIM 홈페이지](https://plans2bim.com/)
- [WiseBIM AI for Revit](https://apps.autodesk.com/RVT/en/Detail/Index?id=7792821748025964445)
- [archBIM.cloud, 2026](https://archbim.cloud/en/blog/ai-creates-bim-from-paper-drawings-2026)
- [AEC Magazine: Higharc](https://aecmag.com/ai/higharc-ai-delivers-3d-bim-model-from-2d-sketch/)
- [Snaptrude 2026 리뷰](https://www.snaptrude.com/blog/top-18-ai-tools-for-architects-in-2026)

### 주요 도구

| 도구 | 입력 | 출력 | 다중 뷰? | 비고 |
|---|---|---|---|---|
| Plans2BIM | PDF/PNG/JPEG | IFC, DXF, CSV | **평면만** | 벽·문·창·공간·슬라브 검출 |
| WiseBIM AI | DWG/DXF/PDF/JPEG/TIFF/PNG | Revit | 불명확 | Autodesk 공식 앱 |
| archBIM.cloud DBAL-YOLO | 종이 도면 스캔 | 3D BIM | 불명확 | 2026-02 "검출 98.8%" 주장 |
| Higharc AI | 2D sketch | 3D BIM | 스케치 기반 | 베타 |
| Snaptrude, Qonic, Augmenta, Arcol, Motif | 다양 | BIM | 제품별 | AI-native BIM 플랫폼 |

### 업계 현실

archBIM.cloud 블로그 표현 그대로: **"2026년 하이브리드 워크플로: AI가 60~80%, 사람이 검증·완성"**.

### 함의

- **"Claude가 전부 한다"**는 접근은 상용 시장에도 없음 — 전용 CV 모델 + 사람 루프가 표준
- 만약 진지하게 서비스화할 거면, **"AI만"이 아니라 "AI + 사람 확인 UI"**가 기본 골격
- 기존 상용 도구의 API 사용이 경쟁력 있을 수 있음 (직접 재구현보다)

---

## 1.5 Claude API 비용·토큰 실측 (2026-04)

출처: [Claude API Pricing 2026](https://platform.claude.com/docs/en/about-claude/pricing), [Pricing breakdown](https://nicolalazzari.ai/articles/claude-api-pricing-breakdown-2026), [Vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)

### 이미지 토큰 계산

- 공식: `width × height / 750` tokens (근사)
- Opus 4.7 이전 모델: 이미지당 **최대 ~1600 tokens**
- Opus 4.7 고해상도(2576px long edge): **최대 ~4784 tokens**

### 모델 가격

| 모델 | Input ($/M) | Output ($/M) |
|---|---|---|
| Opus 4.6 | $5 | $25 |
| **Sonnet 4.6** | **$3** | **$15** |
| Haiku 4.5 | $1 | $5 |

Opus 4.7 구체 가격은 출처에서 직접 확인 필요 — Opus 4.6과 유사 또는 약간 상향 추정.

### Prompt Caching

- **Cache read**: base input의 **10%** (90% 할인)
- **Cache write** (5분 TTL): base input의 **125%**
- **Cache write** (1시간 TTL): base input의 **200%**
- 손익분기: **cache 읽기 1회**만 넘어도 5분 캐시는 이득

### 20장 누적 시나리오의 대략 비용 (Sonnet 가정, 캐시 사용)

가정:
- 이미지 20장 × 평균 2000 tokens = 40k
- 누적 HTML/상태 JSON: 턴 20에서 약 30k tokens
- 시스템 프롬프트: 2k (캐시 적용)
- 출력: 턴당 평균 4k × 20 = 80k

러프 계산:
- 캐시 미적용 input: 누적하면 200~400k
- 캐시 활용 시 실효 input: 80~150k × $3/M = **$0.3~0.5**
- Output: 80k × $15/M = **$1.2**
- **합계 ~$1.5~2 / 1회 실행** (Sonnet)

Opus는 대략 **3~4배 ($6~8)**.

**주의**: 비용은 더 이상 병목이 아님. 병목은 **정확도**.

---

## 1.6 LLM 다중 턴 코드 생성의 일관성

출처:
- [LoCoBench-Agent (arxiv 2511.13998, 2025)](https://arxiv.org/html/2511.13998)
- [LongBench v2](https://longbench2.github.io/)

### 확인된 사실

- 다중 턴에서 "architectural consistency 유지"는 **여전히 연구 중인 도전 과제**
- LoCoBench-Agent는 8000개 시나리오, 10개 언어, 1M 토큰까지 평가 — **다중 턴 일관성이 별도 평가 차원으로 존재한다는 사실 자체**가 이것이 자동 해결된 문제가 아님을 보여줌
- Three.js 특화 벤치마크는 **없음** (검색 범위 내)

### 함의

- 20턴 누적 Three.js 코드 생성이 좌표 일관성을 유지할지는 **선행 연구로 보증되지 않음**
- 경험적으로 측정해야 함 — 즉 실험이 필요

---

## 1.7 이 리서치가 **확인 못한** 것들 (실험 필요)

| 미확정 항목 | 해결 방법 |
|---|---|
| Claude Opus 4.7이 한국 건축 도면에서 어느 정도 정확한가 | 직접 측정 (03 문서 실험) |
| 20턴 누적에서 좌표 드리프트가 실제로 얼마나 발생하는가 | 직접 측정 |
| Gemini 2.x Pro로 추출 + Claude로 코드생성 하이브리드의 실효 정확도 | 직접 측정 |
| 한국어로 쓰여진 도면 범례·치수를 Vision LLM이 얼마나 잘 읽는가 | 직접 측정 |
| Plans2BIM 등 상용 도구 API를 외부에서 호출 가능한지 / 가격 | 직접 문의 |

→ `03-smallest-experiment.md`에서 **최소한으로 이걸 푸는 실험**을 설계함.
