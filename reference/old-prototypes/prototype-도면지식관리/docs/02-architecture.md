# 02. 시스템 아키텍처

## 2.1 디렉터리 구조

```
prototype-도면지식관리/
├── data/                          # 정적 JSON 데이터 (Phase 0 mock)
│   ├── entities.json              # 설비 마스터 (125건: 전기 80 + 기계 25 + 소방 20)
│   ├── relations.json             # 설비 간 관계 (상류/하류/연결 등)
│   ├── documents.json             # 도면·시방서 스니펫 (RAG용)
│   ├── wiki-pages.json            # LLM-Wiki 설비 요약
│   ├── floor-plans.json           # 평면도 존·마커 정보
│   ├── maintenance-logs.json      # 정비이력
│   └── personas.json              # 페르소나 정의 (4명)
│
├── src/
│   ├── app/                       # Next.js App Router 페이지
│   │   ├── page.tsx               # 메인 랜딩 (페르소나 선택)
│   │   ├── layout.tsx             # 루트 레이아웃
│   │   ├── p1-mechanical/
│   │   │   ├── layout.tsx         # PersonaShell 래핑
│   │   │   ├── page.tsx           # 기계 대시보드
│   │   │   ├── chat/page.tsx
│   │   │   ├── impact/page.tsx
│   │   │   └── entity/[tag]/page.tsx
│   │   ├── p2-electrical/         # (p1과 동일 구조)
│   │   ├── p3-fire/               # (p1과 동일 구조)
│   │   └── p4-safety/             # (p1과 동일 구조)
│   │
│   ├── components/
│   │   ├── shell/                 # 전체 레이아웃 쉘
│   │   │   ├── PersonaShell.tsx   # Header + Sidebar 래퍼
│   │   │   ├── PersonaHeader.tsx  # 상단 바 (페르소나 스위처)
│   │   │   ├── PersonaSidebar.tsx # 좌측 네비게이션
│   │   │   ├── SearchBar.tsx      # 설비 검색 입력
│   │   │   ├── ChatPageView.tsx   # Chat 페이지 뷰
│   │   │   ├── EntityPageView.tsx # Entity 상세 뷰
│   │   │   ├── ImpactPageView.tsx # 영향도 분석 뷰
│   │   │   └── EvidenceFooter.tsx # 답변 근거 표시
│   │   │
│   │   ├── chat/                  # 자연어 질의
│   │   │   ├── ChatPanel.tsx      # 대화 컨테이너
│   │   │   ├── AnswerShort.tsx    # 짧은 답변 (P1)
│   │   │   ├── AnswerStructured.tsx # 테이블 답변 (P2)
│   │   │   ├── AnswerCitation.tsx # 원문 인용 (P3)
│   │   │   └── AnswerComposite.tsx # 복합+엑셀 (P4)
│   │   │
│   │   ├── entity/                # 설비 상세
│   │   │   ├── EntityCard.tsx     # 메인 카드 (탭: 속성/관계/정비/위키)
│   │   │   ├── MiniGraph1Hop.tsx  # 1-hop 상류/하류 링크
│   │   │   └── DrawingMiniView.tsx # 근거 도면 썸네일
│   │   │
│   │   ├── impact/                # 영향도 분석
│   │   │   ├── ImpactChain.tsx    # 수평 체인 뷰 (P1)
│   │   │   ├── ImpactGraph.tsx    # React Flow 그래프 (P2)
│   │   │   ├── ImpactFloorPlan.tsx # SVG 평면도 오버레이 (P3)
│   │   │   ├── WhatIfControls.tsx # 복수 정지 시뮬레이션 (P4)
│   │   │   └── ImpactList.tsx     # 테이블 + 엑셀 내보내기
│   │   │
│   │   └── common/
│   │       ├── ConfidenceMeter.tsx # AI 신뢰도 바
│   │       ├── DisciplineBadge.tsx # 분야 색상 뱃지
│   │       └── HitlFlag.tsx        # 검수 필요 경고
│   │
│   └── lib/                       # 비즈니스 로직
│       ├── types.ts               # TypeScript 타입 정의
│       ├── data-loader.ts         # JSON 로드 + 인덱스 빌드
│       ├── search.ts              # Fuse.js 퍼지 검색
│       ├── impact-engine.ts       # BFS 영향도 계산
│       ├── mockApi.ts             # API 추상화 (delay 시뮬레이션)
│       └── persona-config.ts      # 페르소나별 UX 설정
```

---

## 2.2 라우팅 구조

```
/                              → 메인 랜딩 (페르소나 선택)
/p1-mechanical                 → 기계 대시보드 (즐겨찾기 + 정비)
/p1-mechanical/chat            → 자연어 질의 (answerMode: short)
/p1-mechanical/impact          → 영향도 분석 (체인 뷰)
/p1-mechanical/entity/:tag     → 설비 상세 (large, 정비이력 표시)

/p2-electrical                 → 전기 대시보드
/p2-electrical/chat            → 자연어 질의 (answerMode: structured)
/p2-electrical/impact          → 영향도 분석 (React Flow 그래프)
/p2-electrical/entity/:tag     → 설비 상세

/p3-fire                       → 소방 대시보드
/p3-fire/chat                  → 자연어 질의 (answerMode: citation)
/p3-fire/impact                → 영향도 분석 (SVG 평면도 오버레이)
/p3-fire/entity/:tag           → 설비 상세

/p4-safety                     → 안전 대시보드
/p4-safety/chat                → 자연어 질의 (answerMode: composite)
/p4-safety/impact              → What-If 시뮬레이션
/p4-safety/entity/:tag         → 설비 상세
```

**쿼리 파라미터**
- `/impact?root=CH-001` : 영향도 분석 초기 설비 지정

---

## 2.3 데이터 흐름

### 페이지 진입 시 (SSR)
```
Next.js App Router
  → layout.tsx (PersonaShell)
    → data-loader.ts (빌드 타임 JSON import → 메모리 인덱스)
    → 페이지 컴포넌트 (props로 데이터 전달)
```

### 사용자 액션 (Client-side)
```
사용자 입력 (검색 / 질의 / 영향도 실행)
  → mockApi.ts (인위적 delay 100~280ms 시뮬레이션)
    → search.ts / impact-engine.ts / 직접 data-loader 참조
      → React State 업데이트 → 렌더링
```

### 영향도 BFS 흐름
```
impact(rootTag, {direction, maxDepth})
  → getEntity(rootTag)        // 루트 확인
  → BFS 큐 순회
    → getDownstream / getUpstream  // 관계 조회
    → 방문 집합(Set) 중복 제거
    → discipline 필터 적용
  → ImpactNode[] 반환 (depth, path, via_relation 포함)
```

---

## 2.4 페르소나 UX 설정 매트릭스

`src/lib/persona-config.ts`의 `PERSONA_CONFIGS` 객체가 모든 UX 분기를 결정한다.

| 설정 키 | P1 기계 | P2 전기 | P3 소방 | P4 안전 |
|---------|---------|---------|---------|---------|
| `disciplineFilter` | `["MECHANICAL"]` | `["ELECTRICAL"]` | `["FIRE"]` | `null` (전체) |
| `answerMode` | `"short"` | `"structured"` | `"citation"` | `"composite"` |
| `impactView` | `"chain"` | `"graph"` | `"floor"` | `"what-if"` |
| `showMaintenance` | `true` | `false` | `false` | `true` |
| `showDrawing` | `true` | `true` | `false` | `true` |
| `showFloorPlan` | `false` | `false` | `true` | `true` |
| `large` (글씨 크기) | `true` | `false` | `false` | `false` |

---

## 2.5 인덱스 빌드 (data-loader.ts)

서버 시작 시 한 번 실행되어 메모리에 유지된다.

```typescript
// tagIndex: O(1) 태그 조회
const tagIndex = new Map(entities.map(e => [e.tag, e]));

// downstreamIdx: source → Relation[]
// upstreamIdx:   target → Relation[]
for (const r of relations) {
  downstreamIdx.get(r.source)!.push(r);
  upstreamIdx.get(r.target)!.push(r);
}
```

**주의**: 현재 JSON 정적 import 방식이므로 런타임 데이터 변경 불가. 실운영 전환 시 DB 쿼리로 교체 필요.
