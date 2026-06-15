# 08. 이슈 목록 및 개선 로드맵

> 출처: 현장 전문가 6인 평가 (07-expert-review.md)  
> 기준일: 2026-04-16  
> 최종 수정: 2026-04-16 (개발자·검토 페르소나 7인 교차 검토 후 적용)

---

## 이슈 우선순위 기준

| 등급 | 기준 |
|------|------|
| 🔴 **P0 — 즉시** | 안전사고, 법적 리스크, 데이터 신뢰 손상 |
| 🟠 **P1 — 단기** | 실용성 저해, 데모 품질 문제 |
| 🟡 **P2 — 중기** | 실운영 전환 요구사항 |
| 🟢 **P3 — 장기** | 확장 기능, 고도화 |

---

## P0 — 즉시 수정 필요

---

### ISS-001 HitlFlag 로직 버그 — 미검수 데이터가 "정상"으로 표시됨

**파일**: `src/components/common/HitlFlag.tsx`, `src/components/entity/EntityCard.tsx`

**문제**:
```typescript
// EntityCard.tsx:
<HitlFlag on={entity.hitl_flags.length > 0} />
```
`hitl_flags`가 빈 배열(`[]`)이면 → `on=false` → 경고 뱃지 없음.

그러나 빈 배열의 의미가 두 가지다:
- (a) AI가 검수 필요 항목을 발견하지 못함 (≠ 검수 완료)
- (b) 사람이 검수 완료함

현재 (a)와 (b)를 구분할 방법이 없다.

**영향**: 미검수 데이터를 사용자가 검수 완료 데이터로 오인 → 잘못된 설비 정보 신뢰 → 소방/전기 안전사고 위험

**수정 방향**:
```typescript
// types.ts에 추가:
interface Entity {
  // ... 기존 필드
  verified: boolean;   // 인간 검수 완료 여부 (default: false)
}

// EntityCard에서:
<HitlFlag
  on={entity.hitl_flags.length > 0}
  verified={entity.verified}
/>

// HitlFlag 컴포넌트 확장:
// on=true → "검수 필요" amber
// on=false + verified=false → "미검수" gray
// on=false + verified=true → 뱃지 없음 (정상)
```

---

### ISS-002 소방 페르소나에 정비이력 미표시

**파일**: `src/lib/persona-config.ts`

**문제**:
```typescript
"p3-fire": {
  showMaintenance: false,   // ← 이 설정이 잘못됨
  ...
}
```

소방 법정 점검 이력은 「소방시설 설치 및 관리에 관한 법률」에 따라 기록 의무가 있다.
소방 담당자 화면에서 정비이력이 안 보이는 건 명백한 설계 오류.

**수정**:
```typescript
"p3-fire": {
  showMaintenance: true,    // 소방 법정 점검 기록 표시
  ...
}
```

---

### ISS-003 정비 공문 초안에 면책 경고 및 결재 안내 없음

**파일**: `src/components/impact/WhatIfControls.tsx` — `buildOrderDraft()` 함수

**문제**:
- 버튼 클릭 한 번으로 "담당: 시설안전팀" 명의 공문 텍스트 생성
- 결재 라인 없음 (팀장 승인, 관리자 서명 없음)
- "비상발전기 가동 준비" 항상 자동 삽입
- 정비 시간 "야간 22:00 ~ 익일 06:00" 하드코딩

**수정 방향**:
```typescript
function buildOrderDraft(...): string {
  return `⚠ 이 문서는 AI가 생성한 초안입니다.
실제 사용 전 반드시 담당 팀장의 검토 및 승인이 필요합니다.
본 초안은 법적 효력이 없습니다.
────────────────────────────────
[정비 통보 — 초안 (검토 전)]
...
`;
}
```
추가로 비상발전기 문구는 조건부 삽입으로 변경 필요.

---

### ISS-004 CRITICAL 설비 영향도 조회 시 안전 경고 없음

**파일**: `src/components/shell/ImpactPageView.tsx`

**문제**: 영향도 분석 결과에 "이 정보를 실제 설비 조작에 사용하지 마시오" 경고가 없다.

**수정 방향**: 결과 패널 상단에 경고 배너 추가:
```tsx
{nodes.some(n => n.entity.criticality === "CRITICAL") && (
  <div className="bg-red-50 border border-red-300 rounded p-3 text-sm text-red-800">
    ⚠ CRITICAL 설비가 포함된 영향 분석입니다.
    이 결과는 참고용이며, 실제 설비 조작 전 반드시 현장 확인 및 담당자 승인이 필요합니다.
  </div>
)}
```

---

## P1 — 단기 개선

---

### ISS-005 즐겨찾기 하드코딩

**파일**: `src/app/p1-mechanical/page.tsx`

```typescript
const FAVORITES = ["CH-001", "CH-002", "PCHWP-001", "CRAH-001", "AHU-3F-001"];
```

사용자별로 다르다. 최소한 localStorage 기반 개인화 필요.

---

### ISS-006 정비 날짜 필터 하드코딩

**파일**: `src/app/p1-mechanical/page.tsx`

```typescript
.filter(l => l.next_due >= "2026-04-15" && l.next_due <= "2026-04-30")
```

오늘 날짜 기준 동적 계산으로 변경 필요:
```typescript
const today = new Date().toISOString().slice(0, 10);
const monthEnd = new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0)
  .toISOString().slice(0, 10);
.filter(l => l.next_due >= today && l.next_due <= monthEnd)
```

---

### ISS-007 SearchBar debounce 없음

**파일**: `src/components/shell/SearchBar.tsx`

onChange마다 API 호출. 300ms debounce 추가 필요.

---

### ISS-008 PersonaSidebar 활성 항목 중복

**파일**: `src/components/shell/PersonaSidebar.tsx`

"랜딩"과 "설비 검색"이 동일한 href(`/:persona`)를 가짐 → 둘 다 동시에 active 상태.
"설비 검색"을 별도 경로(`/:persona/search`)로 분리하거나 하나를 제거해야 함.

---

### ISS-009 MiniGraph1Hop이 탭에서도, 사이드 패널에서도 중복 표시

**파일**: `src/components/entity/EntityCard.tsx`

```tsx
{tab === "관계" && <MiniGraph1Hop ... />}  // 탭 내
// ...
<MiniGraph1Hop ... />  // 우측 패널 (항상)
```

우측 패널에 항상 표시되는데 "관계" 탭에도 동일 컴포넌트. 중복 렌더. 탭의 "관계"를 더 확장된 뷰로 차별화하거나 하나를 제거해야 함.

---

### ISS-010 ImpactFloorPlan이 floorPlans[0] 고정 사용

**파일**: `src/components/impact/ImpactFloorPlan.tsx`

```typescript
const plan = floorPlans[0];  // 항상 B1F
```

다층 건물에서 영향받는 설비가 다른 층에 있을 수 있다. 층 선택 드롭다운 필요.

---

### ISS-011 ImpactFloorPlan — 노드 태그와 존 ID 불일치

**파일**: `src/components/impact/ImpactFloorPlan.tsx`

```typescript
const impactedTags = new Set(nodes.map(n => n.tag));
// zones[].id 와 nodes[].tag가 다른 네이밍 → 매칭 실패
```

`zones[].id`가 entity 태그와 다른 체계로 구성되어 있으면 평면도에 아무것도 표시되지 않는다. 매핑 테이블 또는 네이밍 통일 필요.

---

### ISS-012 DrawingMiniView 이미지 페이지 목록 하드코딩

**파일**: `src/components/entity/DrawingMiniView.tsx`

```typescript
const exists = page && [3, 4, 5, 10, 22, 40].includes(page);
```

실제 존재하는 이미지 목록이 코드에 하드코딩. `public/drawings/` 폴더 상태와 동기화 매커니즘 필요.

---

### ISS-013 ConfidenceMeter — 신뢰도 산출 근거 툴팁 없음

**파일**: `src/components/common/ConfidenceMeter.tsx`

"83%" 표시만 있고, 이 값이 어디서 어떻게 나왔는지 설명 없음.
마우스 오버 시 툴팁 추가 필요:
- "AI 문서 추출 정확도 기반"
- "HITL 검수 미완료 감점 적용"
등의 설명.

---

## P2 — 중기 (실운영 전환 전 필수)

---

### ISS-014 인증 및 RBAC 미구현

현재 URL만 알면 누구나 모든 기능 접근. 실운영 전 필수:
- 사용자 인증 (SSO 또는 ID/PW)
- 역할 기반 접근 제어 (RBAC)
  - 일반 사용자: 조회만
  - 엔지니어: 위키 편집, 이력 입력
  - 팀장: 공문 초안 생성
  - 관리자: 데이터 수정, 사용자 관리

---

### ISS-015 정적 JSON → API 교체

현재 빌드 타임 JSON import. 실운영 시:
- REST API 또는 GraphQL
- 실시간 데이터 반영
- 캐시 전략 (SWR, React Query)

---

### ISS-016 Entity에 `verified` 필드 추가

ISS-001의 근본 해결. 검수 완료 상태를 데이터 레벨에서 관리.

```json
{
  "tag": "CH-001",
  "verified": false,
  "verified_by": null,
  "verified_at": null,
  ...
}
```

---

### ISS-017 정비이력 유형 표준화

현재 `type` 이 자유 텍스트. 표준 코드 정의 필요:
- `PM` — 예방정비(Preventive Maintenance)
- `CM` — 사후정비(Corrective Maintenance)
- `IM` — 법정 점검(Inspection Maintenance)
- `OV` — 오버홀(Overhaul)

---

### ISS-018 접근 감사 로그 (Audit Log)

CRITICAL 설비 영향도 조회, 공문 초안 생성 등 주요 액션에 대한 로그:
- 사용자 ID, 타임스탬프, 액션 유형, 대상 태그

---

### ISS-029 도면 리스트 페이지 부재

**출처**: 사용자 인터뷰 2026-04-16 (#2)

**문제**: 업로드된 도면 목록을 한눈에 볼 수 있는 전용 화면이 없음. 현재는 개별 엔티티 상세 페이지에서 연결된 도면을 하나씩만 확인 가능.

**영향**: 도면이 어떤 것들이 있는지 파악하려면 엔티티를 하나씩 열어봐야 함 → 업무 비효율.

**수정 방향**:
- 각 페르소나 하위에 `/drawings` 라우트 추가 (`/p1-mechanical/drawings` 등)
- `data/documents.json` 기반 도면 타입(`type: "drawing"`) 항목 표시
- 학제(`discipline`) 필드로 페르소나별 자동 필터링

**연결 파일**: `src/app/p[N]-xxx/drawings/page.tsx` (신규), `data/documents.json`

---

### ISS-030 도면 상세 좌우 분할뷰 미구현

**출처**: 사용자 인터뷰 2026-04-16 (#2)

**문제**: 도면 목록과 상세 뷰어를 동시에 보는 분할 레이아웃이 없음.

**영향**: 목록 → 상세 → 목록 전환 시 컨텍스트 단절. 빠른 비교 탐색 불가.

**수정 방향**:
- 좌측 50%: 도면 리스트 + 설명
- 우측 50%: 선택한 도면의 썸네일 + `DrawingViewer`(zoom/pan) + 다운로드 버튼
- 클릭 시 URL 변경 없이 state 기반으로 우측 패널 즉시 전환

**연결 파일**: `src/components/shell/DrawingsPageView.tsx` (신규), `src/components/drawing/DrawingsList.tsx` (신규), `src/components/drawing/DrawingDetailPane.tsx` (신규), ISS-012(DrawingMiniView 하드코딩)

---

### ISS-031 리스트→상세 단축 동선 부재

**출처**: 사용자 인터뷰 2026-04-16 (#2)

**문제**: 도면 리스트에서 항목 클릭 시 중간 확인 페이지 없이 바로 상세가 보여야 한다는 요구. 현재 구조에서는 별도 페이지 전환이 발생할 수 있음.

**수정 방향**: ISS-030과 연계하여 분할뷰 state 기반 즉시 전환으로 해결 (별도 라우팅 없이 클릭 즉시 우측 패널 갱신).

**연결 파일**: `src/components/shell/DrawingsPageView.tsx`

---

### ISS-032 원본 파일(DWG/PDF) 다운로드 미지원

**출처**: 사용자 인터뷰 2026-04-16 (#2)

**문제**: 현재 `documents.json`에 파일 URL/타입 정보가 없음. 원본 DWG, PDF 파일 다운로드 기능 미구현.

**영향**: 도면 원본 파일을 얻으려면 시스템 외부에서 별도 탐색 필요.

**수정 방향**:
```typescript
// documents.json 항목에 추가:
{
  "files": [
    { "format": "PDF", "url": "/drawings/sample-elec.pdf", "size_kb": 420 },
    { "format": "DWG", "url": "/drawings/sample-elec.dwg", "size_kb": 310 }
  ],
  "download_enabled": true
}
```
- `DrawingDetailPane` 우측 하단에 다운로드 버튼 배치 (`<a href={url} download>`)
- DWG는 브라우저 직접 렌더 불가 → 다운로드만 제공
- PDF는 `<iframe>` mock 뷰어 제공

**연결 파일**: `data/documents.json`, `src/lib/types.ts`, `src/components/drawing/DrawingDetailPane.tsx` (신규)

---

## P3 — 장기 확장 기능

---

### ISS-019 개인별 즐겨찾기 관리

localStorage → 백엔드 사용자 프로파일 저장

---

### ISS-020 BIM/CAD 연동

- 실제 도면 좌표 기반 평면도 자동 생성
- Autodesk Forge 또는 IFC 파일 파싱

---

### ISS-021 모바일/오프라인 지원

- PWA(Progressive Web App) 구성
- Service Worker로 핵심 데이터 캐싱
- 지하 기계실 WiFi 미지원 환경 대응

---

### ISS-022 법정 점검 스케줄러

- 법정 점검 주기 자동 계산
- 소방청/산업안전보건법 기준 일정 알림

---

### ISS-023 도면 버전 관리

- As-Built, Rev 이력 관리
- 버전 간 변경 설비 diff 표시

---

### ISS-024 복합 재해 시나리오 (What-If 고도화)

- 화재 + 정전 동시 발생
- 지진 시 연쇄 트립 시뮬레이션
- 비상 발전기 가동 시 계통 재구성

---

### ISS-025 실제 LLM 연동

- 의도 분류 → LLM 분류기
- 응답 생성 → RAG + Claude/GPT 생성
- 프롬프트 인젝션 방어 (입력 검증, 출력 필터링)

---

### ISS-033 AI 도곽 삽입·스타일 재도시화

**출처**: 사용자 인터뷰 2026-04-16 (#2)

각 업체가 제출하는 도면은 형식·스타일이 제각각임. 요구사항:
- AI가 도면을 한 장씩 인식해 자사 도곽(title block) 자동 삽입
- 회사 표준 스타일(선 굵기, 폰트, 레이어 규칙 등)로 재도시화

**난이도**: 높음. CAD 도면 파싱 + LLM 비전 + 벡터 재생성 파이프라인 필요.

**현재 처리**: `DrawingDetailPane`에 **비활성 버튼**만 배치해 요구사항 시각화.
- 버튼 텍스트: "AI로 재도시화 — 준비 중"
- 툴팁: "도곽 자동 삽입 / 회사 표준 스타일 재도시화 기능은 연구 단계입니다"

**연결 파일**: `src/components/drawing/DrawingDetailPane.tsx`

---

## 이슈 요약 테이블

| ID | 우선순위 | 분류 | 영향 | 파일 |
|----|----------|------|------|------|
| ISS-001 | 🔴 P0 | 버그 | HitlFlag 로직 오류, 미검수=정상 오인 | HitlFlag.tsx, EntityCard.tsx | ✅ 2026-04-16 |
| ISS-002 | 🔴 P0 | 설계 오류 | 소방 정비이력 미표시 (법적 의무) | persona-config.ts | ✅ 2026-04-16 |
| ISS-003 | 🔴 P0 | 안전 | 공문 초안 면책 경고 없음 | WhatIfControls.tsx | ✅ 2026-04-16 |
| ISS-004 | 🔴 P0 | 안전 | CRITICAL 영향도 분석 시 경고 없음 | ImpactPageView.tsx | ✅ 2026-04-16 |
| ISS-005 | 🟠 P1→P2 | UX | 즐겨찾기 하드코딩 | p1-mechanical/page.tsx | 🕐 **데모 후 결정** |
| ISS-006 | 🟠 P0↑ | 버그 | 정비 날짜 필터 고정값 | p1-mechanical/page.tsx, p4-safety/page.tsx | ✅ 2026-04-16 |
| ISS-007 | 🟠 P1 | 성능 | SearchBar debounce 없음 | SearchBar.tsx | ✅ 2026-04-16 |
| ISS-008 | 🟠 P1 | UX | 사이드바 활성 항목 중복 | PersonaSidebar.tsx | ✅ 2026-04-16 |
| ISS-009 | 🟠 P1→P2 | UX | MiniGraph 중복 렌더 | EntityCard.tsx | 🕐 **데모 후 결정** |
| ISS-010 | 🟠 P1 | 기능 | 평면도 층 고정 | ImpactFloorPlan.tsx | 🕐 **데모 후 결정** |
| ISS-011 | 🟠 P1→P0↑ | 버그 | 평면도 미등록 설비 (PS-3F-001 기존 있음, FZ-3F-002 추가) | entities.json | ✅ 2026-04-16 |
| ISS-012 | 🟠 P1→P2 | 유지보수 | 도면 이미지 목록 하드코딩 | DrawingMiniView.tsx | 🕐 **데모 후 결정** |
| ISS-013 | 🟠 P1 | UX | 신뢰도 근거 툴팁 없음 | ConfidenceMeter.tsx | ✅ 2026-04-16 |
| ISS-014 | 🟡 P2 | 보안 | 인증/RBAC 없음 | (신규 구현) | ⏳ P2 보류 |
| ISS-015 | 🟡 P2 | 인프라 | 정적 JSON → API 교체 | data-loader.ts | ⏳ P2 보류 |
| ISS-016 | 🟡 P2→P0 묶음 | 데이터 | Entity `verified` 필드 없음 | types.ts, entities.json | ✅ 2026-04-16 (ISS-001과 묶음) |
| ISS-017 | 🟡 P2 | 데이터 | 정비이력 유형 자유 텍스트 | types.ts | ⏳ P2 보류 |
| ISS-018 | 🟡 P2 | 보안 | 감사 로그 없음 | (신규 구현) | ⏳ P2 보류 |
| ISS-019 | 🟢 P3 | 기능 | 즐겨찾기 개인화 | (신규 구현) | ⏳ P3 보류 |
| ISS-020 | 🟢 P3 | 기능 | BIM/CAD 연동 | (신규 구현) | ⏳ P3 보류 |
| ISS-021 | 🟢 P3 | 기능 | 모바일/오프라인 지원 | (신규 구현) | ⏳ P3 보류 |
| ISS-022 | 🟢 P3 | 기능 | 법정 점검 스케줄러 | (신규 구현) | ⏳ P3 보류 |
| ISS-023 | 🟢 P3 | 기능 | 도면 버전 관리 | (신규 구현) | ⏳ P3 보류 |
| ISS-024 | 🟢 P3 | 기능 | What-If 복합 재해 시나리오 | (신규 구현) | ⏳ P3 보류 |
| ISS-025 | 🟢 P3 | 인프라 | 실제 LLM 연동 | mockApi.ts → 교체 | ⏳ P3 보류 |
| ISS-026 | 🟠 P1 | UX | Chat 샘플 쿼리 재표시 불가 (Clear 없음) | ChatPanel.tsx | ✅ 2026-04-16 |
| ISS-027 | — | 정보 | P2~P4 대시보드 컨텐츠 없다는 오인 → **이미 구현됨** | p2,p3,p4/page.tsx | ✅ 기존 구현 확인 |
| ISS-028 | 🟠 P1 | 정보보안 | 엑셀 내보내기에 출처·주의 시트 없음 | ImpactList.tsx, AnswerComposite.tsx | ✅ 2026-04-16 |
| ISS-029 | 🟡 P2 | 기능 | 도면 리스트 페이지 부재 | drawings/page.tsx (신규) | ⏳ P2 구현 예정 |
| ISS-030 | 🟡 P2 | UX | 도면 상세 좌우 분할뷰 미구현 | DrawingsPageView.tsx (신규) | ⏳ P2 구현 예정 |
| ISS-031 | 🟡 P2 | UX | 리스트→상세 단축 동선 부재 | DrawingsPageView.tsx | ⏳ P2 구현 예정 |
| ISS-032 | 🟡 P2 | 기능 | 원본 파일(DWG/PDF) 다운로드 미지원 | documents.json, types.ts | ⏳ P2 구현 예정 |
| ISS-033 | 🟢 P3 | 연구 | AI 도곽 삽입·스타일 재도시화 | DrawingDetailPane.tsx (비활성 UI) | ⏳ P3 보류 |

---

## 데모 후 결정 항목 (ISS-005, 009, 010, 012)

> 데모 시 사용자·영업 임원에게 기능을 직접 보여주고 니즈를 확인한 후 결정한다.

| ID | 데모에서 확인할 질문 |
|----|------------------|
| ISS-005 즐겨찾기 개인화 | 담당 설비를 직접 등록·관리하고 싶은가? 몇 개 정도 즐겨찾기가 필요한가? |
| ISS-009 MiniGraph 중복 | 우측 패널 미니 그래프가 따로 유용한가? 탭과 중복으로 느끼는가? |
| ISS-010 평면도 층 선택 | 다층 건물 관리가 필요한가? 층별 분리 vs 전체 통합 중 어느 쪽이 더 실용적인가? |
| ISS-012 도면 이미지 연동 | 실제 도면 이미지(PDF/DWG) 뷰어가 이 시스템 안에 있어야 하는가? 외부 도면 시스템과 연동하는 게 더 나은가? |
