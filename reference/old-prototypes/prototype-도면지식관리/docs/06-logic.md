# 06. 핵심 로직

## 6.1 데이터 로더 (`src/lib/data-loader.ts`)

### 빌드 시점 인덱스 생성

```typescript
// 1. JSON → TypeScript 배열 (정적 import, 타입 단언)
export const entities: Entity[] = entitiesJson as Entity[];
export const relations: Relation[] = relationsJson as Relation[];
// ... (documents, wikiPages, floorPlans, maintenanceLogs, personas)

// 2. O(1) 태그 조회 인덱스
const tagIndex = new Map(entities.map(e => [e.tag, e]));

// 3. 양방향 관계 인덱스
const upstreamIdx   = new Map<string, Relation[]>();  // target → relations
const downstreamIdx = new Map<string, Relation[]>();  // source → relations
for (const r of relations) {
  // r.source → [r, ...] (하류 방향)
  // r.target → [r, ...] (상류 방향)
}
```

### 제공 함수

| 함수 | 설명 | 복잡도 |
|------|------|--------|
| `getEntity(tag)` | 태그로 Entity 반환 | O(1) |
| `getDownstream(tag)` | 하류 Relation[] | O(1) |
| `getUpstream(tag)` | 상류 Relation[] | O(1) |
| `getWikiByTag(tag)` | WikiPage 반환 | O(n) — `find` |
| `getLogsByTag(tag)` | MaintenanceLog[] | O(n) — `filter` |
| `getDocumentsByDiscipline(d)` | DocSnippet[] | O(n) — `filter` |
| `getPersona(id)` | Persona 반환 | O(n) — `find` |

**성능 주의**: `getWikiByTag`, `getLogsByTag`, `getPersona`는 배열 순회. 데이터 증가 시 Map 인덱스로 전환 필요.

---

## 6.2 퍼지 검색 (`src/lib/search.ts`)

### Fuse.js 설정

```typescript
const fuse = new Fuse(entities, {
  keys: [
    { name: "tag",         weight: 0.5  },  // 태그가 가장 중요
    { name: "name",        weight: 0.2  },  // 이름
    { name: "type",        weight: 0.15 },  // 유형
    { name: "description", weight: 0.1  },  // 설명
    { name: "location",    weight: 0.05 },  // 위치
  ],
  threshold: 0.4,         // 0=완전일치, 1=모두매칭. 0.4는 약간 느슨한 매칭
  minMatchCharLength: 1,  // 1글자부터 매칭
  ignoreLocation: true,   // 문자열 위치 무관 (전체 텍스트 검색)
});
```

### 검색 함수

```typescript
function search(query, opts?: { disciplines?, limit? }): Entity[]
```

1. 쿼리 빈 문자열 → 전체 반환 (discipline 필터 적용, limit 30)
2. 쿼리 있음 → `fuse.search(query)` → discipline 필터 → limit 적용

**알려진 한계**:
- 한국어 형태소 분석 없음 (예: "냉동기" vs "냉동기들" 검색 차이 없음)
- 태그 완전일치와 이름 부분일치 점수 혼재
- mock API에서 실패 시 토큰 분리 재시도:
  ```typescript
  const tokens = q.split(/\s+/).filter(t => t.length >= 2);
  for (const t of tokens) {
    const partial = search(t, ...);
    if (partial.length) { hits = partial; break; }
  }
  ```

---

## 6.3 영향도 엔진 (`src/lib/impact-engine.ts`)

### `computeImpact` — BFS 그래프 탐색

```typescript
function computeImpact(rootTag: string, opts: ImpactOptions): ImpactNode[]

interface ImpactOptions {
  direction: "downstream" | "upstream" | "both";
  maxDepth: number;       // 1~6 (UI 기본값 4)
  disciplines?: Discipline[];
}
```

**알고리즘 흐름**:
```
초기화:
  visited = Set { rootTag }
  queue = [{ tag: rootTag, depth: 0, path: [rootTag], via_relation: "root" }]
  result = []

BFS 루프:
  cur = queue.shift()
  if cur.depth >= maxDepth → continue (깊이 제한)

  neighbors = []
  if downstream: getDownstream(cur.tag) → { rel, tag: r.target }
  if upstream:   getUpstream(cur.tag)   → { rel: "← "+r.relation, tag: r.source }

  for each neighbor:
    if visited → skip
    if discipline 미포함 → skip
    entity 없음 → skip
    visited.add(tag)
    node = { tag, entity, depth: cur.depth+1, path: [...cur.path, tag], via_relation: rel }
    result.push(node)
    queue.push(node)

return result
```

**특성**:
- 루트 노드 자신은 결과에 포함되지 않음
- 방향이 "both"이면 상류 관계에 `← ` 접두사가 붙음 (화면에 그대로 표시됨)
- 싸이클 방지: `visited` Set으로 처리 (재방문 없음)

**복잡도**: O(V + E) — V=설비 수, E=관계 수

---

### `whatIfDisable` — 복수 설비 동시 정지 시뮬레이션

```typescript
function whatIfDisable(stoppedTags: string[]): {
  impacted: ImpactNode[];
  byDiscipline: Record<Discipline, number>;
}
```

**흐름**:
```
seen = Set(stoppedTags)   // 정지된 설비 자신도 중복 제거 대상

for each stoppedTag:
  downstream = computeImpact(stoppedTag, { direction: "downstream", maxDepth: 6 })
  for each node in downstream:
    if !seen.has(node.tag):
      seen.add(node.tag)
      allImpacted.push(node)

byDiscipline = 분야별 카운트
```

**한계**:
- 각 정지 설비의 하류만 계산 → 상류 영향 미계산
- maxDepth: 6 고정 (사용자 조정 불가)
- 정지 설비들 사이의 내부 연결(A→B 둘 다 정지 시 B의 하류가 중복 계산될 수 있음)
- 연쇄 정지 효과 없음 (A 정지 → B 자동 정지 → C 연쇄 정지 불가)

---

## 6.4 mock API (`src/lib/mockApi.ts`)

### 지연 시뮬레이션

```typescript
const delay = (ms: number) => new Promise(r => setTimeout(r, ms));
```

| 함수 | 지연(ms) | 실제 동작 |
|------|---------|-----------|
| `searchEntities` | 120 | `search()` 호출 |
| `getEntity` | 100 | `tagIndex.get()` |
| `getNeighbors` | 120 | `getUpstream` + `getDownstream` |
| `getWiki` | 80 | `getWikiByTag()` |
| `getLogs` | 80 | `getLogsByTag()` |
| `getDocuments` | 80 | `documents.filter()` |
| `impact` | 180 | `computeImpact()` |
| `whatIf` | 220 | `whatIfDisable()` |
| `ask` | 280 | 의도 분류 + 데이터 조합 |

모든 반환값은 `JSON.parse(JSON.stringify(v))` — 깊은 복사(참조 공유 방지).

---

### `api.ask()` — 의도 분류 및 응답 생성

**의도 분류 (정규식 기반 heuristic)**:

```typescript
isComposite  = /(이번 달|전 분야|통합|모든|합계|집계)/.test(lower)
isRelational = /(상류|하류|연결|뒤|앞|위|아래|영향|체인|부하|회로|계통|feeds?|연결된|소속|어디)/.test(lower)
isCitation   = /(점검 주기|법|기준|nfpa|시방|매뉴얼|절차)/.test(lower)
```

우선순위: composite > relational > citation > documental

**엔티티 매칭 흐름**:
```
1. search(q, {disciplines, limit:5}) → hits
2. hits 없으면 토큰 분리 재시도 (2글자↑ 토큰)
```

**응답 생성 분기**:

| 분기 | 조건 | 응답 |
|------|------|------|
| 정비이력 | `/(정비|이력|점검 일정|차기)/` 키워드 | 마지막 정비이력 텍스트 |
| relational | hits 있고 intent=relational | 상류/하류 관계 테이블 |
| composite | intent=composite | 분야별 entity 집계 테이블 |
| documental | 문서 스니펫 매칭 | 스니펫 텍스트 + 문서 근거 |
| fallback | hits 있고 위 해당 없음 | wiki 또는 entity 설명 |
| unknown | 아무것도 없음 | "관련 데이터를 찾을 수 없습니다" |

**실운영 시 교체 필요**:
- 의도 분류 → LLM 분류기
- 엔티티 매칭 → 벡터 유사도 검색
- 응답 생성 → RAG + LLM 생성

---

## 6.5 페르소나 설정 (`src/lib/persona-config.ts`)

`PERSONA_CONFIGS` 객체가 모든 UX 분기를 단일 위치에서 관리한다.

```typescript
const PERSONA_CONFIGS: Record<PersonaId, PersonaConfig> = {
  "p1-mechanical": {
    disciplineFilter: ["MECHANICAL"],
    answerMode: "short",
    impactView: "chain",
    showMaintenance: true,
    showDrawing: true,
    showFloorPlan: false,
    large: true,
    themeColor: "text-persona-mechanical-700",
    // ...
  },
  // p2, p3, p4 ...
}
```

**사용 패턴**:
```typescript
// ImpactPageView.tsx
const cfg = PERSONA_CONFIGS[personaId];
if (cfg.impactView === "what-if") { return <WhatIfControls /> }
// ...
if (cfg.impactView === "chain") { return <ImpactChain /> }
```

이 패턴 덕분에 새 페르소나 추가 시 `PERSONA_CONFIGS` 한 곳만 수정하면 된다.

**Tailwind 커스텀 컬러**:
`tailwind.config.ts` 에 `persona-mechanical`, `persona-electrical`, `persona-fire`, `persona-safety` 컬러 팔레트가 정의되어 있어야 한다 (파일 확인 필요).
