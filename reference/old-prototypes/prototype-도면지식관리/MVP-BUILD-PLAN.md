# Layer 0 MVP 신규 구축 플랜 — 다음 세션 실행용

> 작성일: 2026-04-17
> 승인 상태: 사용자 승인 완료
> 실행 위치: **`D:\_Project\` 에서 Claude를 실행**해야 sibling 디렉토리 생성 가능

---

## 다음 세션 Claude를 위한 지시

1. **cwd 확인**: 현재 작업 디렉토리가 `D:\_Project\` 인지 확인. 만약 `prototype-도면지식관리` 안이면 사용자에게 알리고 한 단계 위로 올라가서 재시작 권장.
2. **참고 자료**:
   - 기존 분석: `D:\_Project\prototype-도면지식관리\docs-시스템분석\05-통합분석-결론.md` (Layer 0→1→2 전략)
   - 기능 스펙: `D:\_Project\prototype-도면지식관리\docs-시스템분석\06-기능추가-리스트.md` (ISS-034~036 상세)
   - 재사용 데이터: `D:\_Project\prototype-도면지식관리\data\documents.json` (그대로 복사 + 필드 확장)
   - 재사용 타입: `D:\_Project\prototype-도면지식관리\src\lib\types.ts` (`DocSnippet` 차용)
3. **신규 디렉토리**: `D:\_Project\prototype-도면지식관리-mvp\`
4. **기존 프로젝트 변경 금지** (보존하여 비교 가능 상태 유지)

---

## Context

**왜 새로 짓는가.** 기존 `D:\_Project\prototype-도면지식관리\`는 "AI 엔진 + 지식 그래프 + 페르소나 4분할 + 임팩트 분석 + 챗 패널"을 모두 갖춘 데모인데, 8인 페르소나 분석(`docs-시스템분석/04`) 결과 자발적 지불 의사 0명, 평균 채택 점수 2.3/10. 통합 결론(`05`)은 **"극도로 좁게 잡은 Layer 0 MVP"** 를 권한다.

기존 위에 ISS-034~036(주석/검색/PDF뷰어)을 점진 추가하는 길도 있으나, 페르소나 분할·임팩트 그래프·챗 UI가 시야에 같이 보이면 검토자가 "Layer 0 가설"을 깨끗이 평가할 수 없다. **검토 목적은 내부 방향성 판단** — 즉, 새 가설을 오염되지 않은 형태로 보고 결정해야 한다.

따라서 **신규 sibling 디렉토리에 Layer 0만 따로 구축**한다. 기존 프로젝트는 그대로 보존(비교용).

---

## 결과물 정의 (Layer 0 MVP, 극도로 좁게)

검토자가 한 화면에서 "이게 NAS+엑셀보다 나은 한 가지인가?"를 즉시 판단할 수 있어야 한다.

| 화면 | 기능 | 페르소나 근거 |
|---|---|---|
| 단일 페이지 (좌: 리스트 + 검색, 우: 뷰어 + 주석) | 도면 검색 → 클릭 → PDF 인라인 → 핀 메모 | 김현수+박정민 공통 |
| 설비 역추적 패널 | 설비 태그 입력 → 그 설비가 나오는 도면 | 엑셀에서 가장 어려운 것 (05 §6) |

**페르소나 분할 없음. 임팩트 그래프 없음. 챗 패널 없음. 4개 라우트 없음.**

---

## 위치 & 스택

```
D:\_Project\
├── prototype-도면지식관리\        ← 기존, 보존
└── prototype-도면지식관리-mvp\    ← 신규 (이 플랜)
```

| 항목 | 선택 | 이유 |
|---|---|---|
| 프레임워크 | Next.js 14 App Router | 파일 라우팅 + API Route(향후 업로드) 무료, 기존 학습곡선 재사용 |
| PDF 뷰어 | `react-pdf` (pdf.js) | 핀 오버레이 통합 가능. iframe은 주석 불가 |
| 줌/팬 | `react-zoom-pan-pinch` | 검증된 선택, 기존과 동일 |
| 검색 | `Fuse.js` | 기존과 동일 |
| UI | Tailwind CSS | 기존과 동일 |
| 데이터 | 정적 JSON (Phase 0) | API/DB는 ISS-037(업로드)에서 도입 |

**의존성 최소화**: reactflow, xlsx 등은 가져오지 않는다.

---

## 데이터 — 기존 스키마 부분 재사용

기존 `data/documents.json`과 `src/lib/types.ts`의 `DocSnippet`은 거의 그대로 쓸 수 있다 (제목·학제·snippet·files 구조 유효).

### 신규 MVP 데이터 파일

```
prototype-도면지식관리-mvp/data/
├── documents.json   ← 기존에서 복사 + 다음 필드 추가
│                       drawing_number?, drawing_type?, location?, revision?
├── annotations.json ← 신규 (ISS-034 핵심)
└── doc-entity-links.json ← 신규 (설비↔도면 양방향, ISS-040 최소형)
```

### 신규 타입 (`src/lib/types.ts`)

```ts
interface Annotation {
  id: string;
  doc_id: string;
  page: number;
  x: number;          // 0-1 정규화
  y: number;          // 0-1 정규화
  text: string;
  author: string;
  created_at: string;
  tags?: string[];
  type: "info" | "warning" | "field-note";
}

interface DocEntityLink {
  doc_id: string;
  entity_tag: string;
  page?: number;
}
```

`Entity`/`Relation`/`FloorPlan`/`MaintenanceLog`/`WikiPage`/`Persona`는 **가져오지 않는다** (Layer 1+ 용).

---

## 컴포넌트 구조

```
prototype-도면지식관리-mvp/src/
├── app/
│   ├── layout.tsx        ← 최소 (헤더만)
│   ├── page.tsx          ← 메인 (리스트 + 뷰어 분할)
│   └── globals.css
├── components/
│   ├── SearchBar.tsx           ← 도면 통합 검색 (Fuse.js)
│   ├── DrawingsList.tsx        ← 기존 포팅 + 필터 칩(학제/도면종류)
│   ├── PdfViewer.tsx           ← 신규 (react-pdf)
│   ├── AnnotationLayer.tsx     ← 신규 (핀 오버레이)
│   ├── AnnotationPopover.tsx   ← 신규 (메모 입력/조회)
│   ├── AnnotationList.tsx      ← 신규 (전체 주석 패널)
│   └── EntityToDocs.tsx        ← 신규 (설비 태그 → 도면 역추적)
└── lib/
    ├── types.ts          ← 위 정의
    ├── data-loader.ts    ← documents/annotations/links + tagToDocsIdx
    └── search.ts         ← Fuse 인스턴스 (documents 대상)
```

### 핵심 파일 설계

**`PdfViewer.tsx`**
- `react-pdf`의 `<Document>` + `<Page>` 사용
- 페이지 네비게이션(이전/다음, 번호 입력)
- `react-zoom-pan-pinch`로 감싸 줌/팬
- 자식으로 `AnnotationLayer` 받음 (페이지 좌표계 위에 절대 위치)

**`AnnotationLayer.tsx`**
- 현재 페이지 주석을 정규화 좌표 → 픽셀 변환해 핀 렌더
- 빈 공간 클릭 → 새 주석 생성 좌표 콜백
- 핀 클릭 → `AnnotationPopover` 열기

**`data-loader.ts`**
- `documents.json`, `annotations.json`, `doc-entity-links.json` 로드
- 인덱스 빌드: `tagToDocsIdx: Record<entity_tag, doc_id[]>`
- 주석 CRUD는 Phase 0에서 localStorage 영속화 (JSON은 시드 데이터)

---

## 만들지 않는 것 (의식적 배제)

- 페르소나별 라우트 (p1~p4)
- 임팩트 그래프, ImpactChain, ImpactFloorPlan, WhatIfControls
- 챗 패널, AnswerComposite/Citation/Short/Structured
- 엔티티 상세 카드, MiniGraph1Hop
- 위키 페이지, 정비 로그 UI
- AI 보조(메타 추출, 관계 추론) — Layer 2

각각이 빠진 이유는 "Layer 0 가설 검증과 무관" 한 줄로 충분.

---

## 단계별 구현 순서

| 단계 | 작업 | 검증 가능한 것 |
|---|---|---|
| 1 | 디렉토리 부트스트랩 (`create-next-app` 기반, Tailwind, react-pdf 설치) + 기존 documents.json 복사 | `npm run dev` 부팅 |
| 2 | DrawingsList + SearchBar + 기본 분할뷰 | 기존 도면 12건 검색·선택 |
| 3 | PdfViewer (react-pdf) — 주석 없이 페이지/줌만 | PDF 인라인 표시 |
| 4 | AnnotationLayer + Popover + localStorage 저장 | 핀 찍고 메모 → 새로고침 후 유지 |
| 5 | EntityToDocs 패널 (`tagToDocsIdx` 기반) | "CH-001 입력 → 관련 도면 N건" |
| 6 | AnnotationList 사이드 패널 | 전체 주석 일괄 조회 |

**완료 기준**: 한 화면에서 (검색 → PDF 열기 → 핀 메모 → 설비 역추적) 4개 액션을 끊김 없이 수행.

---

## Verification

- `npm run dev` → http://localhost:3000 (단일 라우트)
- 시나리오 A — 도면 검색: 검색바에 "냉동기" → 결과 N건 → 클릭 → PDF 인라인 표시
- 시나리오 B — 주석: PDF 위 클릭 → 메모 입력 → 저장 → 새로고침 → 핀 유지
- 시나리오 C — 설비 역추적: EntityToDocs에 "CH-001" → 매칭 도면 리스트 → 클릭 시 해당 도면 열림
- 시나리오 D — 모바일 폭(375px): 분할뷰 → 탭 전환 (선택, ISS-039 부분 충족)
- 기존 프로젝트 `D:\_Project\prototype-도면지식관리\`는 일체 변경 없음 (확인: `git status` 또는 파일 수정시각 비교)

---

## 미해결 / 검토 후 결정

1. **PDF 실파일** — `public/drawings/*.pdf`가 더미 빈 파일. 실 도면 1~3장이 있어야 검증 의미. 다음 세션에서 사용자에게 실 도면 제공 가능 여부 질문.
2. **주석 데이터 영속성** — Phase 0은 localStorage. 검토 후 다음 단계에서 API+DB 전환.
3. **모바일 시나리오** — Layer 0 진입점으로 모바일이 강한 후보(05 §6). MVP에 포함할지, Phase 1로 미룰지 검토 시 결정.
