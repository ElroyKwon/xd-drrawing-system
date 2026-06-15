# 정보 검색 SaaS 조사 (도면 도메인 확장)

> **목적**: "정보를 검색·제공하는 SaaS"라면 어떤 기능·UX를 갖춰야 하는가를 일반론→도면 특화→구현 옵션→현 프로젝트 결정 순으로 정리한 **사전 조사 기록**.
>
> **작성 시점**: 2026-04-21
> **출발점**: 사용자와 Gemini 간 대화(SaaS 검색 기능/도면 기반 정보 제공/클릭 인터랙션 4문단) + 현 코드베이스 `(s1)` Layer 0 MVP와 `(s2)/insight/lab` 목업 트랙 검토
> **독립성**: 이 조사는 **현재 진행 중인 4주 업그레이드(S1) 및 Insight Lab(S2) 트랙과 별개**. 새 트랙 `/concept`(가칭 S3)의 착수 여부 결정을 위한 근거 자료.

---

## 핵심 질문 4개

1. 정보 검색 SaaS가 **공통적으로** 갖춰야 하는 기능·평가 기준은? → [01](./01-saas-search-fundamentals.md)
2. **도면**을 주 객체로 할 때 추가되는 UX·패턴은? → [02](./02-drawing-specialized-patterns.md)
3. **도면 위 클릭 이벤트**로 검색 키워드를 연결하는 기술 옵션은? → [03](./03-technical-options.md)
4. **현 프로젝트**에 어떻게 녹일까 — 라우트·데이터·스코프는? → [04](./04-decisions-for-this-project.md)

---

## 문서 지도

| # | 파일 | 한 줄 요약 |
|:-:|------|-----------|
| 01 | [01-saas-search-fundamentals.md](./01-saas-search-fundamentals.md) | 통합 인덱싱·하이브리드·패싯·권한·답변 합성·피드백의 6블록 + 5축 평가 + Glean/Coveo/Algolia 벤치마크 |
| 02 | [02-drawing-specialized-patterns.md](./02-drawing-specialized-patterns.md) | Click-to-Search · Search-to-Highlight · 영향도 2-hop · 맥락형 HUD의 4패턴 + ACC/Bluebeam/Procore/Forge 대조표 |
| 03 | [03-technical-options.md](./03-technical-options.md) | SVG 오버레이(A) · Canvas bbox(B) · 동적 비전 추론(C) 3옵션 + 현 스택 적합도 |
| 04 | [04-decisions-for-this-project.md](./04-decisions-for-this-project.md) | 갭 분석 + 3가지 결정 포인트 옵션 A/B/C + 권장 조합 |
| 05 | [05-critical-evaluation.md](./05-critical-evaluation.md) | 객관·비관·불안정성·혁신성 4렌즈 재평가 + 04 권장안 수정 + "안 만드는 선택지"까지 |
| 06 | [06-fundamentals-and-innovation.md](./06-fundamentals-and-innovation.md) | 4 Layer 수직 재정리 (검색 일반 → 도면 의미 → 도면 기본 → 도면 혁신) + 04 옵션 근거 재조사 + 3갈래 의사결정 |
| 07 | [07-actual-code-verification.md](./07-actual-code-verification.md) | 실제 코드 검증 — 06 판정 정정 (A: 결손 0 / C: 결손 C4 1개). 이미 있는 D 기반 발견 |
| 08 | [08-foundation-implementation.md](./08-foundation-implementation.md) | 기본 충실 트랙 `(s3)/foundation/` 구현 완료 — 6개 갭 전부 해소, Layer A/C 100% |
| 09 | [09-menu-architecture-redesign.md](./09-menu-architecture-redesign.md) | 실책 인정 — Layer A/C는 마이크로, 메뉴 IA는 매크로. 정보 제공 SaaS 기본 메뉴 7개 추가 |
| 10 | [10-note-ux-redesign.md](./10-note-ux-redesign.md) | PDF 중심 노트 앱 스타일 `/foundation/notebook` 통합 — StarNote DNA 7개, 3열+토글+T4 썸네일 |
| 11 | [11-next-session-handoff.md](./11-next-session-handoff.md) | (히스토리) 이전 세션 진입점 — StarNote 세부 조사·현장 맥락 탐구 주제 |
| 12 | [12-convenience-features-shortlist.md](./12-convenience-features-shortlist.md) | 편의 기능 교집합 선별표 — StarNote × 현장 앱 ∩ 7개 확정 |
| 13 | [13-presentation-by-screen.md](./13-presentation-by-screen.md) | **★ 화면별 프레젠테이션 (시연·회의 마스터 자료)** — 공용 셸·Foundation 6화면·비교·참조 트랙·14 UX 맵·시연 동선·한계 |
| 14 | [14-open-issues-and-roadmap.md](./14-open-issues-and-roadmap.md) | 남은 이슈 27건 × 6 카테고리 + 3트랙(A/B/C) 선택지 + 회의 안건 템플릿 |
| **15** | **[15-next-session-handoff.md](./15-next-session-handoff.md)** | **★ 다음 세션 진입점 (목업 종결 시점) — 이번 세션 결과 + 3트랙 의사결정 의제** |

### 원본 조사 자료 (research/)

| 파일 | 내용 |
|---|---|
| [research/starnote-feature-research.md](./research/starnote-feature-research.md) | StarNote + GoodNotes + Notability + MarginNote + Samsung Notes + Xodo + Foxit + Nutrient 9개 그룹 기능 맵 + 웹 도입 상위 15 |
| [research/field-apps-benchmark.md](./research/field-apps-benchmark.md) | Fieldwire + Procore Mobile + Bluebeam Cloud iOS 3종 × 12개 현장 제약 UX 해법 비교 + 상위 원칙 12 |

### 읽는 순서 추천

- **처음 읽는 사람**: README → 06 → **07** → (관심 섹션) 01~05
- **의사결정자**: **07 §6** → 06 §0, §8 → 05
- **구현자**: **07 §6.3, §7** → 06 §Layer D → 03

---

## 핵심 결론 (TL;DR, 06 4 Layer 재정리 반영)

### 4 Layer 계층 (06 §0, **07 검증 반영**)

```
Layer A : 정보 검색 사이트의 보편 기본     — 실제 11요건 중 결손 0 / 약함 2 (정렬·하이라이트)
Layer B : "도면 정보 제공"의 의미          — 도면 = 파일/객체/관계/간연관/이력 5층위
Layer C : 도면 정보 제공의 기본 요건        — 실제 7요건 중 결손 1 (C4 도면 내 텍스트검색) / 약함 1 (C6)
Layer D : 도면 정보 제공의 혁신 방향       — I2/I4/I5 골격 이미 코드에 존재 (HighlightOverlay·딥링크·모바일)
```

### 핵심 메시지 (07 검증 반영 갱신)

> **"기본(C)은 이미 86% 충족이었다. 이전 페르소나 거부는 C의 구멍이 아니라 D 위의 서사·포지셔닝·온톨로지 품질 문제일 가능성이 크다."**
>
> 06은 "D 전에 C를 보라"고 했지만, 실제 코드 검증 결과 C의 진짜 결손은 **C4 하나**(react-pdf의 `renderTextLayer` 비활성). 반나절 작업. 따라서 실제 의사결정의 중심은 **"이미 있는 D 기반(HighlightOverlay·딥링크·모바일) 위에 무엇을 완성할 것인가"**로 이동한다.

### 04 옵션 A/B/C의 근거 (06 §7)

D1·D2·D3의 세 축에서 각각 A/B/C가 나온 건 임의가 아니라 **"시연 설득 / 페르소나 공감 / 서사 구조"**라는 세 설계 관심사의 표현. C/C/C는 개별 선택이 아니라 **"시나리오 중심·경량·페르소나 공감·기존 일관"이라는 하나의 설계 철학의 세 얼굴**. 다른 조합(A/B/A 등)은 이전 프로토타입이 이미 시도하고 실패한 방향.

### 혁신(Layer D)의 진짜 방어 가능한 축

| 방향 | 기술 새로움 | 시장 차별화 | 방어력 |
|---|:---:|:---:|:---:|
| I1 객체-중심(Click) | 낮음 | 낮음 | 낮음 |
| I2 양방향(C2S+S2H) | 낮음 | 중간 | 중간 |
| I3 관계 탐색(2-hop) | 중간 | 중간 | 중상 |
| I4 Asset Timeline+RAG | 높음 | 중상 | 중상 |
| **I5 포지셔닝**(한글·현장·경량) | 낮음 | **높음** | **높음** |

결론: **기술이 아니라 "한국 OT 현장 경량 대안"이라는 서사가 가장 방어 가능**. I1~I4는 이 서사 안에 담겨야 의미가 산다.

---

## 사용자 확정이 필요한 것 (06 §8 반영)

### 3갈래 중 선택 (07 검증 반영)

| 갈래 | 내용 | 07 이후 규모 |
|---|---|---|
| **①** | **Layer C 잔여 결손 해소** — C4(텍스트검색) + A.4 정렬 + A.10 스니펫 하이라이트 | **1일 미만** (06 원안의 5개 → 실제 3개 작은 작업) |
| **②** | **Layer D 확장** — 신규 `(s3)/concept/` 대신 **기존 `/drawings/[id]` 확장 모드** (`?mode=concept`). HighlightOverlay 실제 좌표화, Hotspot/HUD/ImpactGraph 추가 | 중규모, 기존 코드 재활용으로 감소 |
| **③** | **W4-T2 + 페르소나 재검증** — 기본 86% + D 1~2개 상태로 이전 8인 중 2~3인 재시연 | 인터뷰 일정 |

**권장**: **① (먼저, 반나절~1일) + ② (이어서) + ③ (④주차 이후)**. 3갈래가 배타적이 아니라 **순차적 스텝**으로 정리됨.

### ② 선택 시 세부 확정 (07 §6.3 반영)

1. **신규 트랙 방식** = 07 권장 "기존 `/drawings/[id]?mode=concept` 확장" vs 06 원안 "신규 `(s3)/concept/`" 중?
2. **시연 시나리오** = 냉동기 CH-001 장애 / PLC 결선 / 공조 / 소방 중?
3. **진입 토글 위치** = `/drawings/[id]` 헤더 모드 스위치 / SideNav 신규 항목 / 우측 탭 중?

---

## 보존 원칙

- 기존 `(s1)` Layer 0 MVP와 `(s2)/insight/lab`은 **import만 허용**, 수정 불가.
- 보존 6항목(`CLAUDE.md §5.5`, `docs/baseline-mvp/07-quirks-and-todo.md §4`) 불변.
- 신규 코드는 **`src/app/(s3)/concept/`와 `data/concept/`에만**.

---

## 외부 참조 요약

일반 검색 SaaS:
- [Glean — AI enterprise search guide 2025](https://www.glean.com/blog/the-definitive-guide-to-ai-based-enterprise-search-for-2025)
- [Onyx AI — Best Enterprise Search Tools for 2026](https://onyx.app/insights/enterprise-search-tools-2026)
- [UXPin — Advanced Search UX](https://www.uxpin.com/studio/blog/advanced-search-ux/)
- [Techment — RAG in 2026 for Enterprise AI](https://www.techment.com/blogs/rag-in-2026/)

도면 특화 제품 벤치마크:
- [Autodesk Construction Cloud — Drawings](https://construction.autodesk.com/tools/construction-drawing-management/)
- [Bluebeam VisualSearch](https://support.bluebeam.com/revu/features/visual-search-overview.html)
- [Procore — Search Text Within Drawings](https://v2.support.procore.com/product-manuals/drawings-project/tutorials/search-text-within-drawings)
- [Autodesk Platform Services — Viewer SDK](https://aps.autodesk.com/viewer-sdk)

그래프/영향도 시각화:
- [Cambridge Intelligence — Knowledge Graph Visualization](https://cambridge-intelligence.com/use-cases/knowledge-graphs/)
- [Neo4j — Knowledge Graph use case](https://neo4j.com/use-cases/knowledge-graph/)
- [yFiles — Visualizing Knowledge Graphs](https://www.yfiles.com/resources/how-to/guide-to-visualizing-knowledge-graphs)

구현 기술:
- [Nutrient — Complete guide to PDF.js](https://www.nutrient.io/blog/complete-guide-to-pdfjs/)
- [IDR Solutions — PDF to SVG (BuildVu)](https://www.idrsolutions.com/buildvu/)
- [OpenSeadragon](https://openseadragon.github.io/)
