# 04. 컴포넌트 레퍼런스

## 쉘 컴포넌트

---

### PersonaShell
`src/components/shell/PersonaShell.tsx`

**역할**: 모든 페르소나 페이지의 공통 레이아웃 래퍼.

```typescript
Props:
  personaId: PersonaId       // "p1-mechanical" | "p2-electrical" | "p3-fire" | "p4-safety"
  children: React.ReactNode
```

**동작**:
1. `getPersona(personaId)` → 없으면 `notFound()` (404)
2. `PersonaHeader` + `PersonaSidebar` + `<main>children</main>` 조합
3. `layout.tsx` 에서 호출됨 (각 페르소나 폴더의 layout)

---

### PersonaHeader
`src/components/shell/PersonaHeader.tsx`

**역할**: 최상단 고정 바. 현재 페르소나 정보 + 전환 버튼.

**구성**:
- 좌측: `← 페르소나 선택` 링크(/) + 구분선 + 코드/이름/직책
- 우측: 4개 페르소나 스위처 버튼 (현재 페르소나 = 강조, 나머지 = 회색)
- 테마 색상: `PERSONA_CONFIGS[personaId].themeBg`, `themeBorder`, `themeColor` 적용

---

### PersonaSidebar
`src/components/shell/PersonaSidebar.tsx` (**Client Component**)

**역할**: 좌측 네비게이션 (192px 고정 너비).

**항목**:
```
Home     → /:persona
설비 검색 → /:persona  (동일 — 대시보드의 SearchBar 포커스 의도)
자연어 질의 → /:persona/chat
영향도 분석 → /:persona/impact
```

**Active 판정 로직**:
- `path === ""`(Home/검색): `pathname === /:persona` OR `pathname.startsWith(/:persona/entity)`
- `path !== ""`: `pathname.startsWith(href)`

**주의**: "설비 검색"과 "랜딩"이 같은 href를 가지므로 둘 다 동시에 active 상태가 된다.

---

### SearchBar
`src/components/shell/SearchBar.tsx` (**Client Component**)

```typescript
Props:
  personaId: string
  disciplines?: Discipline[] | null    // null = 전체
  placeholder?: string
```

**동작**:
- 입력 onChange마다 `api.searchEntities(q, { disciplines, limit: 20 })` 호출
- `delay(120ms)` 시뮬레이션 → 실 입력마다 API 호출 (debounce 없음)
- `touched` 상태가 true가 되면 결과 패널 표시 (빈 쿼리도 전체 목록 표시)
- 결과 항목 클릭 → `/:personaId/entity/:tag`

**알려진 문제**: debounce 미구현. 빠른 타이핑 시 과도한 API 호출.

---

### EvidenceFooter
`src/components/shell/EvidenceFooter.tsx`

```typescript
Props:
  evidence: AskEvidence[]
```

**동작**:
- 근거 없음 → amber 경고 박스 ("근거 데이터가 없습니다. HITL 검수 필요")
- 근거 있음 → 타입별 아이콘(Network/FileText/BookOpen) + 레이블 + 페이지번호

---

## Chat 컴포넌트

---

### ChatPanel
`src/components/chat/ChatPanel.tsx` (**Client Component**)

```typescript
Props:
  config: PersonaConfig         // 페르소나별 UX 설정
  sampleQueries: string[]       // 첫 진입 시 샘플 버튼
```

**상태**:
- `turns: Turn[]` — `{q: string, a: AskAnswer | null}` 배열
- `input: string` — 현재 입력값
- `busy: boolean` — API 호출 중 여부

**흐름**:
1. 샘플 버튼 또는 폼 submit → `submit(q)`
2. `turns`에 `{q, a: null}` 추가 → "분석 중..." 스피너
3. `api.ask(q, {disciplines})` 완료 → `turns` 마지막 항목 a 채움
4. `config.answerMode` 에 따라 `renderAnswer()` 분기

---

### AnswerShort
**대상**: P1 기계 (`answerMode: "short"`)

구성: 큰 텍스트(text-lg) + HitlFlag + 의도/신뢰도 + EvidenceFooter

---

### AnswerStructured
**대상**: P2 전기 (`answerMode: "structured"`)

구성: 텍스트 + **관계 테이블** + 신뢰도 + EvidenceFooter

테이블 헤더/행: `answer.structured.headers` / `answer.structured.rows`

---

### AnswerCitation
**대상**: P3 소방 (`answerMode: "citation"`)

구성: "원문 인용 모드" 레이블 + `<blockquote>` (빨간 왼쪽 선) + 신뢰도 + EvidenceFooter

---

### AnswerComposite
**대상**: P4 안전 (`answerMode: "composite"`) (**Client Component**)

구성: 텍스트 + 테이블(좌) + 분석 요약 카드(우) + **엑셀 내보내기 버튼** + 신뢰도 + EvidenceFooter

**엑셀 내보내기**:
```typescript
XLSX.utils.aoa_to_sheet([headers, ...rows])
XLSX.writeFile(wb, `dks-answer-${Date.now()}.xlsx`)
```
의존성: `xlsx` (SheetJS) 패키지

---

## Entity 컴포넌트

---

### EntityCard
`src/components/entity/EntityCard.tsx` (**Client Component**)

```typescript
Props:
  entity: Entity
  personaId: PersonaId
  showMaintenance: boolean    // PERSONA_CONFIGS에서 주입
  showDrawing: boolean
  large: boolean              // P1만 true (글씨 크기 업)
  logs?: MaintenanceLog[]
  wiki?: WikiPage | null
```

**탭 상태**: `useState<Tab>` — 기본값은 `showMaintenance && logs.length` 이면 "정비이력", 아니면 "속성"

**탭 목록**: `["속성", "관계", "정비이력", "위키"]` — "정비이력"은 `showMaintenance` 시에만 렌더

**헤더 영역**:
- DisciplineBadge + 태그 + HitlFlag
- 이름 (large → text-3xl, 일반 → text-2xl)
- 설명
- 최종 수정 날짜 + ConfidenceMeter
- "영향도 분석 →" 버튼 (→ `/:personaId/impact?root=:tag`)
- 중요도 뱃지 (CRITICAL=빨강, HIGH=주황, 나머지=회색)

**우측 패널**: `MiniGraph1Hop` + `DrawingMiniView` (showDrawing 시)

---

### MiniGraph1Hop
`src/components/entity/MiniGraph1Hop.tsx`

```typescript
Props:
  tag: string
  personaId: string
```

**동작**:
- `getUpstream(tag).slice(0,4)` + `getDownstream(tag).slice(0,6)`
- 3컬럼 그리드: [상류 목록] | [현재 노드 박스] | [하류 목록]
- 각 항목 클릭 → 해당 entity 페이지 이동
- 관계명 표시 (opacity 낮춤)

**주의**: 상류 4개, 하류 6개로 잘림. 실제 관계가 많으면 "더보기" 없음.

---

### DrawingMiniView
`src/components/entity/DrawingMiniView.tsx`

```typescript
Props:
  entity: Entity
```

**동작**:
1. `entity.source_pages[0]` 확인
2. 페이지 번호가 `[3, 4, 5, 10, 22, 40]` 중 하나 → `/drawings/page_XXX.png` 이미지 로드
3. 해당 안됨 → "page {N} 미복사" 또는 "원본 도면 미등록" 텍스트

**주의**: 
- 실제 도면 이미지는 `public/drawings/` 폴더에 수동 복사 필요
- `next/image`의 `unoptimized` 플래그 사용 → 최적화 없음

---

## Impact 컴포넌트

---

### ImpactChain
`src/components/impact/ImpactChain.tsx`

```typescript
Props:
  root: string
  nodes: ImpactNode[]
```

**동작**:
- `nodes`를 `depth`별 Map으로 그룹화
- 수평 Flexbox: `[루트 박스] → [depth1 컬럼] → [depth2 컬럼] → ...`
- `overflow-x-auto` (depth 증가 시 가로 스크롤)
- 왼쪽 4px 색상 선: CRITICAL=red-500, HIGH=orange-500, 나머지=slate-300

---

### ImpactGraph
`src/components/impact/ImpactGraph.tsx` (**Client Component**)

의존성: `reactflow`, `reactflow/dist/style.css`

**노드 배치**:
```
position.x = depth * 240
position.y = index * 90 - (같은 depth 노드 수 * 45)  // 중앙 정렬
```

**스타일**:
- 루트: `background: #0f172a` (검정)
- 영향 노드: `border: 2px solid {criticality 색}`
  - CRITICAL: `#dc2626` / HIGH: `#ea580c` / MEDIUM: `#64748b` / LOW: `#94a3b8`

**제약사항**:
- 자동 레이아웃 알고리즘 없음. depth가 같은 노드 간 엣지(cross-depth edge)가 있으면 시각적으로 혼란.
- 노드 라벨이 JSX (inline-style) 방식 → React Flow v12+ 에서 deprecated 될 수 있음.

---

### ImpactFloorPlan
`src/components/impact/ImpactFloorPlan.tsx` (**Client Component**)

**동작**:
1. `floorPlans[0]` 사용 (첫 번째 평면도 하드코딩)
2. `impactedTags = new Set(nodes.map(n => n.tag))`
3. SVG `<polygon>`: zone.id가 impactedTags에 있으면 컬러, 없으면 회색
4. SVG `<circle>`: marker.tag가 impactedTags에 있으면 빨간 원
5. 마우스 오버 → strokeWidth 증가 + opacity 강화
6. 우측 패널: 영향 항목 리스트

**핵심 주의사항**:
- `nodes[].tag` 값이 `zones[].id` 또는 `markers[].tag`와 정확히 일치해야만 평면도에 시각화됨.
- 현재 floor-plans.json의 zone id와 entities.json의 tag가 다른 네이밍 체계 → 대부분 미표시.

---

### WhatIfControls
`src/components/impact/WhatIfControls.tsx` (**Client Component**)

**목적**: 복수의 CRITICAL/HIGH 설비를 "가상 정지"시키고 전체 영향 범위를 계산한다.

**상태**:
```typescript
stopped: string[]           // 정지 가정된 태그 목록
result: {
  impacted: ImpactNode[]
  byDiscipline: Record<Discipline, number>
} | null
```

**흐름**:
1. 체크박스로 CRITICAL/HIGH 설비 복수 선택
2. "What-If 시뮬레이션" 버튼 → `api.whatIf(stopped)`
3. 결과 표시:
   - 좌: 선택 패널 (체크박스 목록)
   - 중: 분야별 집계 (숫자 + DisciplineBadge)
   - 우: 정비 공문 초안 텍스트

**공문 초안 생성 (`buildOrderDraft`)**:
```
[정비 통보 — 초안]
일자: {오늘 날짜}
정비 대상: {선택한 태그들}
정비 시간: 야간 22:00 ~ 익일 06:00 (예정)   ← 하드코딩

영향 분야:
  - 전기: {N}건
  - 기계: {N}건
  - 소방: {N}건

조치 요청:
  1. 영향 부서 사전 통보
  2. 비상발전기 가동 준비               ← 항상 고정 삽입
  3. 작업 종료 후 정상화 확인 보고

담당: 시설안전팀                          ← 하드코딩
```

**주요 이슈**:
- 정비 시간, 담당자, 비상발전기 문구 모두 하드코딩
- 결재 라인 없음 (단순 텍스트 생성)
- 권한 검증 없음

---

### ImpactList
`src/components/impact/ImpactList.tsx` (**Client Component**)

테이블 컬럼: depth / 태그 / 이름 / 분야(DisciplineBadge) / 중요도 / 관계 / 경로

**엑셀 내보내기**:
- 파일명: `dks-impact-{rootTag}-{Date.now()}.xlsx`
- 컬럼: depth, tag, name, discipline, criticality, via, path

---

## 공통 컴포넌트

---

### ConfidenceMeter
`src/components/common/ConfidenceMeter.tsx`

```typescript
Props:
  value: number    // 0.0 ~ 1.0
```

**색상 분기**:
- 80%↑ → `bg-emerald-500` (녹색)
- 60~80% → `bg-amber-500` (노란색)
- 60%↓ → `bg-red-500` (빨간색)

**주의**: 신뢰도 산출 근거가 UI 어디에도 표시되지 않음. 툴팁 없음.

---

### DisciplineBadge
`src/components/common/DisciplineBadge.tsx`

```typescript
Props:
  d: Discipline    // "ELECTRICAL" | "MECHANICAL" | "FIRE" | "FACILITY"
```

색상: 전기=yellow, 기계=cyan, 소방=red, 시설=blue

---

### HitlFlag
`src/components/common/HitlFlag.tsx`

```typescript
Props:
  on: boolean
  label?: string    // 기본값: "HITL 검수 필요"
```

**`on`이 false이면 아무것도 렌더링하지 않는다.**

**핵심 버그**:
```typescript
// EntityCard에서:
<HitlFlag on={entity.hitl_flags.length > 0} />
```
`hitl_flags`가 빈 배열(`[]`)이면 → `on=false` → 뱃지 없음.
그런데 이는 "검수 완료"가 아니라 단순히 "AI가 검수 필요 항목을 발견하지 못했음"일 수 있다.
**별도 `verified: boolean` 필드 없이는 검수 완료/미검수/경고 세 상태를 구분 불가능.**

Chat에서는:
```typescript
<HitlFlag on={answer.hitl_flag} />   // AskAnswer의 hitl_flag boolean
```
