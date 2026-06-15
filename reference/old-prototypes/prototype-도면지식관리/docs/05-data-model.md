# 05. 데이터 모델

## 5.1 타입 정의 전체 (`src/lib/types.ts`)

---

### Entity — 설비 마스터

```typescript
interface Entity {
  tag: string;             // 고유 식별자 (예: "CH-001", "CB-B1F-01")
  type: string;            // 설비 유형 (예: "냉동기", "차단기")
  name: string;            // 설비명 (예: "냉동기 1호기")
  description: string;     // 기능 설명
  discipline: Discipline;  // "ELECTRICAL" | "MECHANICAL" | "FIRE" | "FACILITY"
  function_category: string; // 기능 분류 (예: "냉방", "배전")
  status: string;          // 현재 상태 (예: "정상", "점검중") — 자유 텍스트
  main_category: string;   // 대분류
  sub_category: string;    // 소분류
  location: string;        // 위치 (예: "B1 기계실")
  spec_summary: string;    // 사양 요약 (예: "600RT, R-134a")
  source_pages: number[];  // 근거 도면 페이지 번호 배열
  confidence: number;      // AI 추출 신뢰도 (0.0 ~ 1.0)
  hitl_flags: string[];    // AI 검수 필요 항목 목록 (빈 배열 = 플래그 없음)
  notes: string;           // 비고
  last_updated: string;    // 최종 수정일 (ISO 날짜 문자열)
  criticality: Criticality; // "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
}
```

**Phase 0 데이터 현황**:
- 전기: 80건 (실데이터)
- 기계: 25건 (mock)
- 소방: 20건 (mock)
- 총 125건

**알려진 설계 문제**:
- `status` 가 자유 텍스트 → 집계/필터 어려움. 표준 enum 필요.
- `hitl_flags: string[]` 만으로는 "검수 완료" 상태 표현 불가. `verified: boolean` 필드 추가 필요.
- `criticality` 기준이 문서화되지 않음. 누가 어떤 기준으로 할당했는지 불명확.
- 법정 점검 주기(`inspection_cycle`) 필드 없음.
- 설비 담당자(`owner`/`responsible_engineer`) 필드 없음.

---

### Relation — 설비 간 관계

```typescript
interface Relation {
  source: string;           // 출발 설비 태그
  relation: string;         // 관계 유형 (예: "feeds", "controls", "부하", "연결")
  target: string;           // 도착 설비 태그
  evidence_page: number | null; // 근거 도면 페이지 (null = 근거 없음)
  note: string;             // 관계 설명 비고
}
```

**인덱스 빌드** (`data-loader.ts`):
```
downstreamIdx: source → Relation[]   (A에서 흘러가는 것들)
upstreamIdx:   target → Relation[]   (A로 흘러오는 것들)
```

**알려진 설계 문제**:
- `relation` 이 자유 텍스트 → 표준 관계 유형 체계 없음. "feeds"와 "부하"가 같은 의미일 수 있음.
- `evidence_page: null` 이 많으면 관계의 출처 추적 불가.
- 양방향 관계를 양방향 레코드로 저장하는지, 한 방향만 저장하는지 명확하지 않음.

---

### DocSnippet — 문서 스니펫 (RAG)

```typescript
interface DocSnippet {
  doc_id: string;           // 문서 식별자 (예: "DOC-E-001")
  title: string;            // 문서 제목
  type: string;             // 문서 유형 (예: "도면", "시방서", "매뉴얼")
  discipline: Discipline;   // 해당 분야
  page: number;             // 페이지 번호
  snippet: string;          // 추출된 텍스트 단락
  drawing_ref: string | null; // 도면 번호 참조
  last_updated: string;     // 문서 최종 수정일
}
```

**사용처**: `mockApi.ask()` 의 documental/citation 응답에서 근거로 사용

**알려진 설계 문제**:
- 스니펫 전문(full text) 없이 단편적인 텍스트만 저장 → RAG 품질 제한
- 문서 버전(revision) 필드 없음

---

### WikiPage — LLM-Wiki

```typescript
interface WikiPage {
  tag: string;              // 연결된 Entity 태그
  title: string;            // 위키 페이지 제목
  summary: string;          // 설비 요약 (LLM 생성)
  spec: string;             // 사양 상세
  known_issues: string[];   // 알려진 이슈 목록
  linked_documents: string[]; // 연결 문서 id 목록
  last_edited: string;      // 최종 편집일
  editor: string;           // 편집자
}
```

**사용처**: `EntityCard` 위키 탭, `mockApi.ask()` 응답 근거

**알려진 설계 문제**:
- LLM 생성 여부와 인간 검수 여부 구분 필드 없음
- 버전 이력 없음

---

### FloorPlan — 평면도

```typescript
interface FloorPlan {
  plan_id: string;          // 평면도 식별자
  floor: string;            // 층 표시 (예: "B1F")
  image: string;            // 이미지 파일 경로 (현재 미사용)
  width: number;            // SVG 뷰박스 너비
  height: number;           // SVG 뷰박스 높이
  zones: {
    id: string;             // 구역 식별자 (ImpactFloorPlan에서 ImpactNode.tag와 매칭)
    name: string;           // 구역 이름
    polygon: [number, number][]; // 폴리곤 좌표 배열 ([x, y] 쌍)
    color: string;          // 기본 색상 (hex)
  }[];
  equipment_markers: {
    tag: string;            // 설비 태그 (entities.tag와 매칭)
    x: number;              // 마커 중심 x좌표
    y: number;              // 마커 중심 y좌표
    label: string;          // 마커 레이블
  }[];
}
```

**알려진 설계 문제**:
- `ImpactFloorPlan`이 `floorPlans[0]` 고정 사용 → 다층 건물 미지원
- `zones[].id`가 Entity 태그와 다른 네이밍 → 영향도와 평면도 매칭 실패

---

### MaintenanceLog — 정비이력

```typescript
interface MaintenanceLog {
  log_id: string;           // 이력 식별자
  tag: string;              // 해당 설비 태그
  date: string;             // 작업 날짜
  type: string;             // 정비 유형 (예: "예방정비", "고장수리")
  summary: string;          // 작업 요약
  engineer: string;         // 담당 엔지니어 이름
  next_due: string;         // 차기 점검 예정일
}
```

**알려진 설계 문제**:
- `engineer` 가 이름 문자열만 → 연락처, 소속, 위탁업체 여부 없음
- `type` 이 자유 텍스트 → 예방/사후/법정 점검 구분 표준화 필요
- 작업 결과 상태 (`결과: 정상/이상`) 필드 없음
- 소방 법정 점검 기록 요구사항 미반영

---

### Persona — 페르소나 정의

```typescript
interface Persona {
  id: PersonaId;            // "p1-mechanical" | "p2-electrical" | "p3-fire" | "p4-safety"
  code: string;             // 표시 코드 (예: "P-01")
  name: string;             // 이름 (예: "김기계")
  title: string;            // 직책 (예: "기계설비 엔지니어")
  description: string;      // 역할 설명
  discipline_focus: Discipline[]; // 담당 분야
  ux_priorities: string[];  // UX 우선순위 설명
  theme: "mechanical" | "electrical" | "fire" | "safety"; // 테마
  sample_queries: string[]; // 샘플 질문 목록
}
```

---

### ImpactNode — 영향도 분석 노드

```typescript
interface ImpactNode {
  tag: string;              // 설비 태그
  entity: Entity;           // 전체 Entity 객체 (중복 포함)
  depth: number;            // 루트로부터의 깊이
  path: string[];           // 루트 → 현재 노드까지의 태그 배열
  via_relation: string;     // 이 노드로 이어지는 관계명
}
```

---

### AskAnswer — 질의 응답

```typescript
interface AskAnswer {
  intent: "relational" | "documental" | "composite" | "unknown";
  answer_text: string;      // 답변 텍스트
  evidence: AskEvidence[];  // 근거 목록
  confidence: number;       // 신뢰도 (0.0 ~ 1.0)
  hitl_flag: boolean;       // HITL 검수 필요 여부
  structured?: {            // 구조화 데이터 (선택적)
    headers: string[];
    rows: string[][];
  };
}

interface AskEvidence {
  type: "graph" | "document" | "wiki";
  ref: string;              // 참조 식별자
  label: string;            // 표시 레이블
  page?: number;            // 문서 페이지 번호
}
```

---

## 5.2 데이터 파일 현황

| 파일 | 타입 | 건수 | 비고 |
|------|------|------|------|
| `entities.json` | `Entity[]` | ~125 | 전기 80 실데이터 + 기계/소방 mock |
| `relations.json` | `Relation[]` | 미확인 | 상류/하류 관계 |
| `documents.json` | `DocSnippet[]` | 미확인 | RAG 스니펫 |
| `wiki-pages.json` | `WikiPage[]` | 미확인 | 일부만 생성 |
| `floor-plans.json` | `FloorPlan[]` | 1 (B1F) | mock 좌표 |
| `maintenance-logs.json` | `MaintenanceLog[]` | 미확인 | 기계 중심 |
| `personas.json` | `Persona[]` | 4 | 고정 |

---

## 5.3 실운영 전환 시 교체 필요 항목

| 현재 (Phase 0) | 실운영 대안 |
|----------------|-------------|
| JSON 정적 import | REST API / GraphQL / DB 쿼리 |
| `mockApi.ts` delay 시뮬레이션 | 실제 LLM API 연동 (Claude, GPT 등) |
| Fuse.js 클라이언트 검색 | Elasticsearch / pgvector 서버 검색 |
| 하드코딩 즐겨찾기 | 사용자 프로파일 DB |
| 정적 신뢰도 값 | LLM logprob 또는 RAG 점수 기반 계산 |
| mock 평면도 SVG | BIM 연동 또는 실제 CAD 래스터라이즈 |
