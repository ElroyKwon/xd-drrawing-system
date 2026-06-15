# 02 · 도면 기반 검색·인터랙션 특화 패턴

> **문서 성격**: 01의 일반 검색 SaaS 기능을 전제로, **도면이 주 객체**일 때 추가되는 UX·기능 블록을 정리. Autodesk Construction Cloud, Bluebeam Revu, Procore Drawings, Autodesk Forge Viewer 사례 대조.

---

## 1. 현업이 도면을 "언제·왜" 여는가 (요구의 원천)

Gemini 가이드를 바탕으로 현장 관찰과 교차 확인한 결과:

| 시점 | 상황 | 핵심 질문 |
|---|---|---|
| **장애/알람 발생** | 특정 장비에 경보 | "이 장비 뭐랑 연결돼 있고, 후단에 뭐가 죽나?" |
| **시운전·결선 검증** | PLC 포트·접점 매핑 확인 | "논리 로직과 물리 결선이 맞나?" |
| **설비 증설/개조** | ESS·공조기 추가 | "기존 전력망·통신망 여유 있나? 간섭 있나?" |
| **계획 정비/LOTO** | 차단·격리 범위 산정 | "이거 내리면 어디까지 영향?" |
| **신규 투입 교육** | 현장 구조 파악 | "이 설비가 어디 있고 무엇과 엮이나?" |

공통 주어는 **"영향도(impact)와 종속성(dependency)"**. 따라서 도면 검색은 "찾기"가 아니라 **"관계 탐색"**이 본질 과업이다. 01의 5축(정확도·속도·가독성·출처·피드백)에 **공간 인지**와 **관계 탐색** 두 축이 추가되는 이유.

---

## 2. 핵심 패턴 4종

### 2.1 Click-to-Search (도면 → 정보)

뷰어에서 설비 아이콘·텍스트·심볼을 **클릭**하면 검색창 입력 없이도 해당 객체의 사양·매뉴얼·과거 장애·실시간 데이터가 패널에 뜬다.

- **Autodesk Forge Viewer**: `dbId` 기반 선택 → `getProperties()`로 속성을 Property Panel에 표시. SDK가 기본 제공.
- **Autodesk Construction Cloud (ACC) Docs**: 2D 시트 업로드 시 **콜아웃 자동 하이퍼링크**. 확대도·상세도 콜아웃을 클릭하면 해당 시트로 점프.
- **Bluebeam Revu — VisualSearch**: 도면 내 특정 심볼(VAV, 서모스탯, 장비 태그)을 시각적으로 검색 → 일괄 하이라이트/하이퍼링크.

**시사점**: "클릭 = 쿼리" 개념은 엔터프라이즈 BIM/시공 제품군에서 이미 기본값. 우리가 `(s1)` 홈에 넣을 때는 최소한 "클릭 → 좌측 패널에 속성 + 연결 문서 리스트"의 패턴을 맞춰야 한다.

### 2.2 Search-to-Highlight (정보 → 도면)

검색창에 태그·알람·키워드를 치면 **뷰어에서 해당 위치가 하이라이트**되고, 연결된 하위 설비까지 색으로 물들며 공간 위치를 즉시 알 수 있다.

- **Bluebeam VisualSearch** — 한 번 찾으면 모든 인스턴스에 **일괄 액션**(하이라이트/하이퍼링크) 적용.
- **Procore Drawings** — 벡터 PDF 내 텍스트 검색. 다만 마크업 내부 텍스트는 검색 대상이 아니라는 **한계**가 있고, 이건 우리 시스템이 차별화 포인트로 삼을 여지가 있다 (마크업까지 인덱싱).
- **ACC Docs**: 속성·커스텀 태그·파일 타입·날짜 다중 패싯 필터.

**시사점**: 검색 → 하이라이트는 "연결된 하위도 같이 물들이기"까지 해줘야 의미가 있다. 단건 하이라이트는 이미 Acrobat이 한다.

### 2.3 영향도·종속성 역추적 (Graph Traversal)

"차단기 X를 내리면 어느 장비들이 꺼지나?" 질문은 관계 DB에서는 JOIN을 N회 반복해야 하지만, **그래프 DB**에서는 한 번의 traversal로 해결된다.

- LPG(Labeled Property Graph), RDF, Neo4j, Amazon Neptune 등의 벤더 레퍼런스가 공통적으로 "upstream/downstream 영향도"를 핵심 유스케이스로 든다.
- 시각화 UX: **centrality**로 허브 장비 강조, **shortest path**로 "장애 경로" 계산, **force-directed layout** 또는 **sankey** 다이어그램.
- 키 UX: 도면 위에 겹쳐 띄우지 말고 **우측 패널**이나 별도 탭으로. 도면과 그래프를 동시에 보여주면 인지 과부하.

**현 프로젝트**: `EntityToDocs`가 최소 버전의 역추적(태그→문서). 그래프까지는 아니고 "조인된 테이블"에 가깝다. 신규 트랙에서는 **"태그 → 문서 → 관련 태그 2-hop"**까지 확장하는 것이 명확한 차별점.

### 2.4 맥락형 HUD / 오버레이

도면을 가리지 않고 정보를 제공하는 방법론.

- **반투명 사이드 슬라이드 패널** (왼쪽/오른쪽)
- **글래스모피즘 플로팅 카드** — 클릭 지점 근처에 말풍선
- **상태 배지** — 설비 위에 작은 색상 점 (정상/경보/점검중)
- **레이어 토글** — 전력/통신/기계/소방 계통 ON/OFF
- **줌-연동 세부도** — 확대 수준에 따라 표시하는 정보 밀도 조절 (LoD)

**실패 패턴**: 모달을 도면 중앙에 띄우는 것. 공간 인지가 끊겨서 "어디 얘기하던 거였지?"가 된다.

---

## 3. 벤치마크 대조표

| 제품 | Click-to-Search | Search-to-Highlight | 영향도/그래프 | 레이어 제어 | 모바일 |
|---|:---:|:---:|:---:|:---:|:---:|
| Autodesk ACC Docs | ◎ (콜아웃 자동 링크) | ○ (시트 검색·필터) | △ (연결 Asset) | ○ | ○ |
| Autodesk Forge Viewer SDK | ◎ (dbId + Property Panel) | ○ (isolate/highlight API) | △ (직접 구현) | ◎ | ○ |
| Bluebeam Revu | ○ (하이퍼링크 수동 배치) | ◎ (VisualSearch 일괄) | ✕ | ○ | ○ |
| Procore Drawings | △ (마크업 링크) | △ (벡터 텍스트만) | ✕ | ○ | ◎ |
| Neo4j Bloom / yFiles | — | — | ◎ (전용) | — | — |
| **현 `(s1)` 홈** | ✕ | ✕ | △ (EntityToDocs) | ✕ | ✕ |
| **제안 신규 트랙** | ◎ 목표 | ◎ 목표 | ○ (2-hop) | △ (계통 토글) | △ |

범례: ◎ 대표 기능 · ○ 지원 · △ 부분 · ✕ 없음

---

## 4. 도면 검색에만 있는 평가 축 2개

01의 5축(정확도·속도·가독성·출처·피드백)에 추가되는 축:

| 축 | 측정 지표 |
|---|---|
| **공간 인지성** | 검색 후 해당 객체를 화면에 띄우기까지 조작 수(줌/이동/클릭) |
| **관계 탐색 완결성** | "영향 받는 하위 설비" 질문에 Top-N이 몇 초 안에 나오나 |

공간 인지성이 높다는 건 "이게 **어디**에 있는지 뇌에 그림으로 남느냐"의 문제다. 텍스트 리스트로만 응답하면 0점에 가깝다.

---

## 5. 도면 데이터를 "검색 가능"하게 만드는 파이프라인

도면은 이미지/벡터/메타데이터/BIM 모델까지 다형태라, 인덱싱 전 단계가 복잡하다.

```
[DWG/DXF/PDF/이미지]
      │
      ▼
[Vision AI + OCR] ── 객체·텍스트·좌표 추출
      │
      ▼
[정규화 & 태그 매핑] ── BOM·Asset 레지스트리와 매칭
      │
      ├──► [Vector Index]     (의미 검색)
      ├──► [Keyword Index]    (태그/번호 정확 매칭)
      └──► [Graph DB]         (연결성/영향도)
                │
                ▼
         [Hybrid Query Orchestrator]
                │
                ▼
         [UI: Viewer + Chat + Panels]
```

MVP 단계에선 **수동 YAML/JSON 시드** (현 프로젝트 방식)가 합리적. Vision AI 파이프라인은 Layer 1~2.

---

## 6. 이 문서의 결론

도면 기반 검색 SaaS는 **"클릭과 검색이 상호 호출되고, 결과가 공간과 관계로 확장되는"** 구조여야 한다. 구체적으로는:

1. **Click-to-Search**: 도면 객체 클릭 → 속성 + 연결 문서 패널
2. **Search-to-Highlight**: 검색 → 뷰어 하이라이트 + 영향 범위 동시 표현
3. **2-hop 이상 관계 탐색**: 태그 → 문서 → 관련 태그 (현 `EntityToDocs`의 확장)
4. **HUD/오버레이**: 도면을 가리지 않는 맥락형 정보 제공

다음 문서에서 이 중 1번(클릭 이벤트)의 **구현 방식 3종**을 비교한다 → [03-technical-options.md](./03-technical-options.md).

---

## 참고

- [Construction Drawings Software — Autodesk Forma/ACC](https://construction.autodesk.com/tools/construction-drawing-management/)
- [Autodesk ACC Docs Search Functionality — Man and Machine](https://www.manandmachine.co.uk/autodesk-construction-cloud-autodesk-docs-search-functionality/)
- [How to do Hyperlinks in BIM 360 Docs — IMAGINiT](https://resources.imaginit.com/autodesk-construction-cloud/how-to-do-hyperlinks-in-bim-360-docs)
- [VisualSearch overview — Bluebeam](https://support.bluebeam.com/revu/features/visual-search-overview.html)
- [Bluebeam Revu Hyperlink Tool — Novedge](https://novedge.com/blogs/design-news/bluebeam-tip-utilize-bluebeam-revus-hyperlink-tool-to-enhance-pdf-navigation-and-user-experience)
- [Search Text Within Drawings — Procore](https://v2.support.procore.com/product-manuals/drawings-project/tutorials/search-text-within-drawings)
- [Viewer SDK — Autodesk Platform Services](https://aps.autodesk.com/viewer-sdk)
- [Model Summary Panel — Forge Tutorials](https://forge-tutorials.autodesk.io/tutorials/dashboard/panel/)
- [Knowledge Graph Visualization — Cambridge Intelligence](https://cambridge-intelligence.com/use-cases/knowledge-graphs/)
- [Knowledge Graph — Neo4j](https://neo4j.com/use-cases/knowledge-graph/)
- [Graph and AI — Amazon Neptune](https://aws.amazon.com/neptune/knowledge-graphs-on-aws/)
- [Guide to Visualizing Knowledge Graphs — yFiles](https://www.yfiles.com/resources/how-to/guide-to-visualizing-knowledge-graphs)
