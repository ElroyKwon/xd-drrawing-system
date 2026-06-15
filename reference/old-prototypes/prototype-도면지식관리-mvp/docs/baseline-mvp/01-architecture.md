# 01 · 아키텍처

## 1. 한 줄 요약

**Next.js App Router의 단일 클라이언트 컴포넌트(`src/app/page.tsx`)가 모든 state를 소유**하고, 자식들은 props로만 동작한다. 서버는 JSON 시드를 번들에 함께 임포트할 뿐 런타임에 아무것도 하지 않는다.

## 2. 컴포넌트 트리

```
app/layout.tsx
└─ app/page.tsx  ← "use client", 모든 state 소유
   ├─ <header> 타이틀 + 주석 카운터
   ├─ aside(left)
   │   ├─ SearchBar               (query state)
   │   └─ DrawingsList            (discipline/docType/selectedId)
   ├─ main
   │   └─ PdfViewer               (selected doc + pageOverride)
   │       └─ renderOverlay:
   │           └─ AnnotationLayer  (docAnnotations[page])
   ├─ aside(right) — sidePanel 분기
   │   ├─ EntityToDocs            (onOpenDoc → setSelectedId/Page)
   │   └─ AnnotationList          (onOpen → setSelectedId/Page/popover)
   └─ AnnotationPopover            (popover 모드 있을 때 모달)
```

`PdfViewer`만 `dynamic(..., { ssr: false })`로 로드된다 — react-pdf의 `pdfjs`가 브라우저 `Worker`에 의존해서 SSR 불가.

## 3. state 소유 지도

전역 소유자는 **`src/app/page.tsx` 한 곳**. 아래 7개가 전부다.

| state | 초기값 | 쓰는 곳 |
|---|---|---|
| `query: string` | `""` | `SearchBar`, `filtered` 계산 |
| `discipline: Discipline \| "ALL"` | `"ALL"` | 칩 버튼, `filtered` 계산 |
| `docType: string \| "ALL"` | `"ALL"` | 칩 버튼, `filtered` 계산 |
| `selectedId: string \| null` | `null` | `selected` 조회, 뷰어 대상 |
| `selectedPage?: number` | `undefined` | `PdfViewer.pageOverride` |
| `popover: PopoverMode \| null` | `null` | 모달 on/off, 생성/편집 분기 |
| `sidePanel: "entity" \| "annotations"` | `"entity"` | 우측 탭 |

주석 자체는 이 컴포넌트의 state가 아니라 **`useAnnotationsStore()` 훅이 내부적으로 소유**한다(`src/lib/annotations-store.ts`). 훅은 `annotations`, `hydrated`, `addAnnotation`, `updateAnnotation`, `deleteAnnotation`를 반환한다.

## 4. 데이터 흐름 (시나리오 3개 기준)

### A. 검색 → 도면 선택

```
사용자 입력
 → SearchBar onChange → setQuery
 → useMemo filtered:
     searchDocuments(query)        // Fuse.search
       .filter(discipline)         // 직접 배열 필터
       .filter(type)
 → DrawingsList가 filtered를 받아 렌더
 → li 클릭 → onSelect(doc_id) → setSelectedId + setSelectedPage(undefined)
 → selected = documents.find(...)
 → PdfViewer 마운트 (key가 doc_id라 리셋)
```

### B. 주석 생성

```
PdfViewer의 surfaceRef div 클릭 (cursor:crosshair)
 → handleSurfaceClick:
     rect = div.getBoundingClientRect()
     x = (clientX - left) / width    ∈ [0,1]
     y = (clientY - top)  / height   ∈ [0,1]
 → onPageClick(x, y, pageNumber)
 → page.tsx에서 setPopover({ kind:"create", draft:{doc_id,page,x,y} })
 → AnnotationPopover 모달 렌더 (중앙, 배경 dim)
 → 저장:
     addAnnotation({ doc_id, page, x, y, ...payload })
       → id = `ann-${Date.now()}-${rand}`, created_at = ISO
       → setAnnotations([...prev, newAnn])
     useEffect가 hydrated 후 localStorage에 JSON.stringify
 → AnnotationLayer가 다음 렌더에 새 핀을 left=x*W, top=y*H에 그림
```

### C. 설비 역추적

```
EntityToDocs 입력 또는 칩 클릭 → setTag
 → useMemo hits:
     docsForTag(tag)                   // tagToDocsIdx[TAG.toUpperCase()]
       .map(doc => ({ doc, page: pageForDocEntity(doc_id, tag) }))
 → li 클릭 → onOpenDoc(doc_id, page)
 → page.tsx에서 setSelectedId + setSelectedPage(page)
 → PdfViewer가 useEffect([doc.doc_id, pageOverride])로 pageNumber를 갱신
 → 해당 페이지가 react-pdf Document에 렌더됨
```

## 5. 모듈 책임 분리

### `src/lib/` — 순수 로직
- `types.ts` — 타입 정의. **런타임 코드 없음.**
- `data-loader.ts` — JSON 3개 임포트 + `docById`, `tagToDocsIdx`, `allEntityTags`, `docsForTag`, `pageForDocEntity` 파생 인덱스.
- `search.ts` — Fuse.js 인스턴스와 `searchDocuments(query)` 래퍼.
- `annotations-store.ts` — 훅 `useAnnotationsStore`. localStorage I/O 포함.

### `src/components/` — UI, **데이터 접근 금지** 원칙
컴포넌트는 `@/lib/data-loader`에서 파생 인덱스(`docById`, `allEntityTags` 등)만 읽는다. 자신의 state는 **표시 편의를 위한 로컬 state만** 허용한다 (예: `AnnotationList`의 검색 `q`, `EntityToDocs`의 `tag`). 도메인 데이터는 항상 prop/훅으로 주입.

예외: `PdfViewer`가 내부적으로 `pageNumber`/`pdfFailed`/`totalPages`/`surfaceSize`를 갖는다. 이건 뷰어의 렌더링 상태지 도메인 상태가 아니라 내부 유지 OK. 다만 **`pageOverride` prop이 오면 리셋**되게 동기화돼 있다 (`PdfViewer.tsx:45`의 useEffect).

### `src/app/` — 조립 책임
`page.tsx`가 lib과 components를 엮어 화면을 구성한다. **로직은 거의 없다** — 유일한 가공은 `filtered` 계산 3단계와 `docAnnotations.filter(page)` 한 번.

## 6. 번들 관점

- JSON 시드 3개는 빌드 시 번들에 포함된다 (`import ... from "@data/..."`). 서버/클라 모두에서 동일.
- `documents.length === 8`, `docEntityLinks.length === 8` 수준이라 Fuse 인덱스 비용 무시 가능.
- `pdf.worker.min.mjs`는 `public/`에 정적 서빙되고 `pdfjs.GlobalWorkerOptions.workerSrc = "/pdf.worker.min.mjs"`로 런타임에 참조.

## 7. 렌더 트리거 요약

| 트리거 | 다시 렌더되는 것 |
|---|---|
| `query/discipline/docType` 변경 | `DrawingsList` (filtered 재계산) |
| `selectedId` 변경 | `PdfViewer` (key 재마운트 포함) |
| `selectedPage` 변경 | `PdfViewer` 내부 useEffect → `setPageNumber` |
| `annotations` 변경 | 헤더 카운터 + `AnnotationLayer` + `AnnotationList` |
| `popover` 변경 | `AnnotationPopover` on/off |
| `sidePanel` 변경 | 우측 탭 전체 교체 |

이 이상 복잡하지 않다 — 전역 state 머신이나 reducer는 일부러 넣지 않았다.
