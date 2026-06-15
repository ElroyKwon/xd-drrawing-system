# 03. 화면 목록 및 상세 설명

## 화면 목록

| # | 화면 이름 | URL 패턴 | 주요 컴포넌트 |
|---|-----------|----------|---------------|
| 1 | 메인 랜딩 | `/` | `page.tsx` |
| 2 | 페르소나 대시보드 | `/:persona` | `PersonaShell`, `SearchBar` |
| 3 | 자연어 질의 (Chat) | `/:persona/chat` | `ChatPanel`, `Answer*` |
| 4 | 영향도 분석 | `/:persona/impact` | `ImpactPageView`, `ImpactChain/Graph/FloorPlan/WhatIfControls` |
| 5 | 설비 상세 | `/:persona/entity/:tag` | `EntityCard`, `MiniGraph1Hop`, `DrawingMiniView` |

---

## Screen 1. 메인 랜딩 (`/`)

### 목적
시스템 진입점. 4개 페르소나 중 하나를 선택한다.

### 구성 요소
- **헤더**: "DKS Prototype" 수퍼타이틀, 시스템명, 설명 텍스트
- **페르소나 카드 그리드** (2×2):
  - 분야별 아이콘 (Wrench / Zap / Flame / ShieldCheck)
  - 페르소나 코드, 이름, 직책
  - 시스템 설명
  - 샘플 질문 2개 미리보기
  - 분야별 컬러 테마 (cyan / yellow / red / blue)
- **푸터**: 데이터 출처 안내 문구

### 데이터 의존성
- `personas.json` → `data-loader.getPersona()`

### 주의사항
- `ICONS` 맵이 `PersonaId` 타입과 1:1 매핑. 페르소나 추가 시 동기화 필요.
- 테마 클래스 문자열이 `THEMES` 객체에 하드코딩. Tailwind purge 대상 확인 필요.

---

## Screen 2. 페르소나 대시보드 (`/:persona`)

각 페르소나마다 맞춤 대시보드. 현재 P1(기계)만 고유 구현이고, P2~P4는 범용 구조.

### P1 기계 대시보드 구성
```
[검색창]                    ← SearchBar (MECHANICAL 필터)
[즐겨찾기 섹션]             ← 하드코딩된 5개 태그
  - DisciplineBadge + tag + 이름 + 위치
  - 클릭 → entity/:tag 이동
[다가오는 정비 섹션]        ← maintenanceLogs 날짜 필터
  - tag + 정비 유형 + 예정 날짜
  - 클릭 → entity/:tag 이동
  - 담당자 이름 표시
```

### PersonaShell (공통 래퍼)
모든 페르소나 페이지는 `PersonaShell`로 감싸진다.

```
PersonaShell
  ├── PersonaHeader (상단 고정 바)
  │     ├── "← 페르소나 선택" 뒤로가기
  │     ├── 현재 페르소나 코드 + 이름 + 직책
  │     └── 4개 페르소나 스위처 버튼
  │
  └── PersonaSidebar (좌측 고정, 192px)
        ├── 랜딩 (홈)
        ├── 설비 검색
        ├── 자연어 질의
        └── 영향도 분석
```

### 알려진 문제
- `FAVORITES` 배열이 `p1-mechanical/page.tsx` 에 하드코딩됨. 사용자별 즐겨찾기 불가.
- 정비 날짜 필터 `"2026-04-15" ~ "2026-04-30"` 이 고정값. 매일 날짜가 지나면 항목이 사라진다.
- P2~P4 대시보드에는 고유 컨텐츠가 없음. SearchBar만 존재.

---

## Screen 3. 자연어 질의 (`/:persona/chat`)

### 목적
자연어로 설비 정보를 질의하고 AI(mock) 답변을 받는다.

### 레이아웃
```
[전체 높이 채움 (100vh - 헤더 56px)]
  ┌────────────────────────────────┐
  │  대화 영역 (overflow-y-auto)   │
  │                                │
  │  [첫 진입: 샘플 질문 카드]     │
  │  [질문 버블 (우측 정렬)]       │
  │  [답변 컴포넌트 (좌측)]        │
  └────────────────────────────────┘
  ┌────────────────────────────────┐
  │  [입력창] [전송 버튼]          │ ← border-t 고정
  └────────────────────────────────┘
```

### 답변 모드 (페르소나별 분기)

| 모드 | 페르소나 | 컴포넌트 | 특징 |
|------|----------|----------|------|
| `short` | P1 기계 | `AnswerShort` | 큰 텍스트, 의도 + 신뢰도만 표시 |
| `structured` | P2 전기 | `AnswerStructured` | 관계 테이블 렌더링 (상류/하류 행) |
| `citation` | P3 소방 | `AnswerCitation` | 인용 블록(blockquote) + 빨간 왼쪽 선 |
| `composite` | P4 안전 | `AnswerComposite` | 테이블 + 분석 요약 카드 + **엑셀 내보내기** |

### 공통 하단 요소 (EvidenceFooter)
- 근거 데이터 없을 시: ⚠ amber 경고 박스
- 있을 시: 타입 아이콘(그래프/문서/위키) + 레이블 + 페이지 번호

### mock API 질의 의도 분류 로직
```
query → 정규표현식 키워드 매칭
  ├── "이번 달|전 분야|통합|합계" → composite
  ├── "상류|하류|연결|영향|체인" → relational
  ├── "점검 주기|법|기준|NFPA|절차" → documental(citation)
  └── 나머지 → documental
```

### 주의사항
- `submit(q)` 호출 시 비동기이므로 연속 입력 가능. `busy` 플래그로 이중 전송 방지.
- 의도 분류가 단순 정규식 기반 → 실운영 시 LLM intent classification 필요.

---

## Screen 4. 영향도 분석 (`/:persona/impact`)

### 목적
특정 설비가 정지되었을 때 영향받는 하류/상류 설비를 시각화한다.

### 공통 컨트롤 패널
```
[대상 설비 select]  [방향: 하류/상류/양방향]  [최대 깊이: 1~6]  [분석 실행]
```
- 설비 목록은 페르소나의 `disciplineFilter` 로 필터링
- URL에 `?root=TAG` 로 초기값 전달 가능 (EntityCard에서 연결)
- 분석 완료 후 URL에 `?root=` 파라미터 자동 갱신 (공유 가능)

### 뷰 타입별 상세

#### ImpactChain (P1 기계)
- 수평 스크롤 레이아웃
- depth별 컬럼, 각 컬럼에 노드 카드
- 노드 왼쪽 색 선: CRITICAL=빨강, HIGH=주황, 나머지=회색
- 각 노드: DisciplineBadge + 태그 + 이름 + via_relation

#### ImpactGraph (P2 전기) — React Flow
- 노드: 루트(검정 배경) + 영향 설비(흰 배경, criticality 색 테두리)
- 엣지: 레이블(관계명), 화살표
- depth별 x축 배치 (240px 간격), 같은 depth 노드 y축 분산
- Controls(확대/축소), Background(격자) 기본 탑재
- **주의**: 노드 다수 시 겹침 발생 가능 (자동 레이아웃 없음)

#### ImpactFloorPlan (P3 소방) — SVG
- `floor-plans.json` 의 첫 번째 평면도 사용 (하드코딩)
- Zone 폴리곤: 영향 받으면 컬러, 아니면 회색
- Equipment Marker: 영향 받으면 빨간 원, 아니면 흰 원
- 오버레이 + 우측 영향 항목 리스트
- **주의**: `nodes`의 태그가 `zones[].id` 또는 `equipment_markers[].tag`와 일치해야 시각화됨. 불일치 시 평면도에 아무것도 안 표시됨.

#### WhatIfControls (P4 안전)
복수 설비 동시 정지 시나리오. 상세는 [04-components.md #WhatIfControls](./04-components.md) 참조.

### ImpactList (공통 하단 테이블)
- depth / 태그 / 이름 / 분야 / 중요도 / 관계 / 경로 컬럼
- **엑셀 내보내기**: `xlsx` 라이브러리로 브라우저 다운로드
  - 파일명 형식: `dks-impact-{rootTag}-{timestamp}.xlsx`

---

## Screen 5. 설비 상세 (`/:persona/entity/:tag`)

### 목적
개별 설비의 모든 정보를 한 화면에서 조회한다.

### 레이아웃
```
┌──────────────────────────────────────────────────────┐
│  DisciplineBadge  tag  [HitlFlag]                    │
│  [설비 이름 (large: 3xl / 일반: 2xl)]                │
│  [설명]                                              │
│                                    최종 수정 날짜     │
│                                    ConfidenceMeter   │
│  [영향도 분석 →]  [중요도 뱃지]                       │
└──────────────────────────────────────────────────────┘
┌─────────────────────────┐  ┌──────────────────────┐
│  탭: 속성/관계/정비/위키  │  │  MiniGraph1Hop       │
│                          │  │  DrawingMiniView      │
│  [탭 컨텐츠]             │  │  (showDrawing 시)     │
└─────────────────────────┘  └──────────────────────┘
```

### 탭 상세

#### 속성 탭
키-값 그리드 2컬럼:
- 유형, 기능 분류, 상태, 위치, 카테고리(대/소), 사양, 비고

#### 관계 탭
`MiniGraph1Hop` 컴포넌트 (상류 4개, 하류 6개, 클릭 → 해당 entity 이동)

#### 정비이력 탭
`showMaintenance: true` 인 페르소나에서만 노출 (P1 기계, P4 안전).
- 정비 유형, 날짜, 요약, 담당자, 차기 예정 날짜

#### 위키 탭
LLM-Wiki 존재 시: 제목, 요약, 사양, 알려진 이슈 목록, 편집자/날짜
위키 없을 시: "LLM-Wiki 미생성 (HITL 검수 대기)" 텍스트

### 우측 사이드 패널 (항상 표시)
1. `MiniGraph1Hop` — 1-hop 관계 (탭의 관계와 중복 표시됨)
2. `DrawingMiniView` — 근거 도면 썸네일 (`showDrawing: true` 시)
   - `source_pages[0]` 을 보고 `/drawings/page_XXX.png` 로드
   - 대상 페이지 [3,4,5,10,22,40] 만 파일 존재 → 나머지는 "미복사" 표시

### URL 인코딩
태그에 특수문자(하이픈, 슬래시 등) 포함 시 `encodeURIComponent` 처리됨. EntityCard 내 링크와 page.tsx params 모두 `decodeURIComponent` 쌍.
