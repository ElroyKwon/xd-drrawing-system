# 04 · 핀 주석

**Layer 0에서 가장 덩치 큰 기능.** 4개 파일이 맞물린다.

| 파일 | 역할 |
|---|---|
| `src/components/AnnotationLayer.tsx` | 뷰어 위에 핀(작은 원) 렌더 |
| `src/components/AnnotationPopover.tsx` | 중앙 모달: 생성/편집 폼 |
| `src/lib/annotations-store.ts` | 훅 + localStorage 영속 |
| `src/components/AnnotationList.tsx` | 우측 탭: 전체 주석 브라우저 |

## 1. 데이터 모델

```ts
// src/lib/types.ts
export type AnnotationKind = "info" | "warning" | "field-note";

export interface Annotation {
  id: string;            // "ann-{timestamp}-{rand5}"
  doc_id: string;        // 연결 문서
  page: number;          // PDF 페이지(1-based), 이미지는 1 고정
  x: number;             // 0~1 정규화 X
  y: number;             // 0~1 정규화 Y
  text: string;          // 메모 본문
  author: string;        // 작성자 (빈 값이면 "익명")
  created_at: string;    // ISO 8601
  tags?: string[];       // ["정비","안전"] 등
  type: AnnotationKind;  // info | warning | field-note
}
```

**불변성 규칙**: `id / doc_id / page`는 생성 후 수정 불가. `updateAnnotation(id, patch)`의 patch 타입은 `Partial<Omit<Annotation, "id" | "doc_id" | "page">>`로 컴파일러가 강제한다. 이유: 핀을 다른 도면으로 옮기거나 페이지 이동시키는 건 새 핀 생성이 더 명확해서.

**수정 가능 필드**: `x, y, text, author, tags, type, created_at`. (팝오버에서는 text/author/type/tags만 편집. x/y는 건드리지 않음.)

## 2. 저장소: `useAnnotationsStore`

`src/lib/annotations-store.ts`, 74줄.

### 초기화 순서
```ts
const [annotations, setAnnotations] = useState<Annotation[]>(seedAnnotations);
const [hydrated, setHydrated]      = useState(false);

useEffect(() => {
  const fromLs = loadFromStorage();
  if (fromLs) setAnnotations(fromLs);
  setHydrated(true);
}, []);
```

1. **첫 렌더**: `seedAnnotations`(= `data/annotations.json`, 현재 빈 배열)로 시작. 서버 HTML도 이 값을 가정해 렌더하므로 hydration mismatch 없음.
2. **클라 마운트 후**: localStorage `mvp-annotations-v1`을 읽어 존재하면 덮어씀.
3. `hydrated` 플래그가 true로 바뀐다.

### 저장 타이밍
```ts
useEffect(() => {
  if (hydrated) saveToStorage(annotations);
}, [annotations, hydrated]);
```

`hydrated === false` 동안에는 저장하지 않는다. 이유: 마운트 직후 `seedAnnotations` → `fromLs` 덮어쓰기 사이에 짧게 seed 값으로 저장되는 걸 막기 위함.

### API
```ts
addAnnotation(a: Omit<Annotation, "id" | "created_at">): Annotation
updateAnnotation(id, patch: Partial<Omit<Annotation, "id" | "doc_id" | "page">>): void
deleteAnnotation(id): void
```

모두 `useCallback`으로 메모이즈. `addAnnotation`은 새로 만든 annotation을 리턴(현재 사용처는 없지만 리턴 유지).

### localStorage 에러 처리
`loadFromStorage`는 `JSON.parse` 실패, `!Array.isArray`, 전체 try-catch로 방어. `saveToStorage`는 quota/권한 문제를 조용히 무시. 즉, **privacy 모드나 용량 초과 시에도 앱은 죽지 않지만 영속 실패는 silent**. 프로덕션이면 toast로 알려야 함.

### 키 네이밍
`"mvp-annotations-v1"`. 포맷 변경 시 `-v2`로 올려 마이그레이션 윈도우 확보. 현재는 포맷 안정.

## 3. AnnotationLayer — 오버레이 렌더

```tsx
<div className="pointer-events-none absolute inset-0" style={{ width, height }}>
  {annotations.map((a) => (
    <button
      onClick={(e) => { e.stopPropagation(); onPinClick(a.id); }}
      className="pointer-events-auto absolute -translate-x-1/2 -translate-y-full ..."
      style={{ left: a.x * width, top: a.y * height, width: 16, height: 16 }}
    />
  ))}
</div>
```

주요 설계:
- **바깥 div는 `pointer-events-none`**, 개별 핀 버튼만 `pointer-events-auto`. 덕분에 핀 사이 공간을 클릭하면 이벤트가 `surfaceRef`까지 내려가서 **새 핀 생성**으로 이어진다.
- `-translate-x-1/2 -translate-y-full`: 핀의 "꽂힌 지점"이 버튼의 하단 중앙이 되게. 지도 마커 관례.
- **type별 색**: info=sky, warning=amber, field-note=emerald. `pinStyles` record.
- **활성 핀(`activeId === a.id`)**: `scale-125 ring-[6px]`로 두드러지게.
- **접근성**: `<span className="sr-only">{a.text}</span>`로 스크린리더가 메모 내용을 읽는다. `title={a.text}`로 호버 툴팁도.

`onPinClick(a.id)` 수신 측(`page.tsx:120`)은 팝오버를 "edit" 모드로 열어준다.

## 4. AnnotationPopover — 생성/편집 폼

`src/components/AnnotationPopover.tsx` (180줄). 모드 두 개.

```ts
type Mode =
  | { kind: "create"; draft: DraftInput }      // 뷰어 클릭에서 진입
  | { kind: "edit"; annotation: Annotation };  // 핀 클릭 또는 리스트에서 진입
```

### 레이아웃
```
┌─ 주석 추가 / 주석 편집          ✕ 닫기 ┐
│ p.1 (40.0%, 34.9%)                     │
├────────────────────────────────────────┤
│ 종류  [정보] [주의] [현장메모]         │
│ 메모  [textarea rows=4]                │
│ 작성자 [input]     태그 [input]        │
├────────────────────────────────────────┤
│ [삭제]              [취소] [저장]      │  (삭제는 edit 모드에서만)
└────────────────────────────────────────┘
```

- 중앙 모달, 배경 `bg-slate-900/30` dim. `fixed inset-0 z-40`.
- `Escape` 키로 닫기 (`useEffect`로 window keydown 리스너).
- 모달 본체 onClick `stopPropagation`해서 바깥 클릭으로는 닫지 않음 — 사용자가 실수로 폼 내용 잃는 거 방지.
- `text.trim()` 비어있으면 저장 버튼 `disabled`.
- 작성자 빈 값이면 서버 저장 시 `"익명"`으로 대체.
- 태그: 쉼표 split → trim → 빈 문자열 제거.

### initial 값
```ts
const initial = mode.kind === "edit"
  ? { text, author, type, tags: tags.join(", ") }
  : { text: "", author: "", type: "info", tags: "" };
```

`useState(initial.xxx)`로 각 필드 초기화. **mode가 바뀌어도 팝오버는 unmount/remount 되므로** state는 자연스럽게 리셋됨 (부모에서 `popover` prop이 null이 됐다가 새 값으로 교체되기 때문).

## 5. AnnotationList — 우측 탭

`src/components/AnnotationList.tsx` (129줄). 모든 주석을 문서별로 그룹핑해 보여준다.

### 필터링
```tsx
const filtered = useMemo(() => {
  const needle = q.trim().toLowerCase();
  if (!needle) return annotations;
  return annotations.filter((a) => {
    const docTitle = docById[a.doc_id]?.title.toLowerCase() ?? "";
    return (
      a.text.toLowerCase().includes(needle) ||
      a.author.toLowerCase().includes(needle) ||
      docTitle.includes(needle) ||
      a.tags?.some((t) => t.toLowerCase().includes(needle))
    );
  });
}, [annotations, q]);
```

검색 대상: 메모 본문, 작성자, 문서 제목, 태그. **단순 `includes` — Fuse.js 안 씀**. 주석 수는 보통 수십~수백 수준이라 충분.

### 그룹핑
```tsx
const byDoc = useMemo(() => {
  const groups: Record<string, Annotation[]> = {};
  for (const a of filtered) {
    if (!groups[a.doc_id]) groups[a.doc_id] = [];
    groups[a.doc_id].push(a);
  }
  return Object.entries(groups);  // [[docId, [a,a,...]], ...]
}, [filtered]);
```

문서별로 sticky 헤더(`sticky top-0 bg-slate-50`) + 그 아래 주석들.

### 항목 UI
- 좌측: type 색 점 하나.
- 가운데 클릭 영역: 메모(2줄 clamp) + 메타(`p.N · author · tags`).
- 우측: `✕` 삭제 버튼 (hover 시 rose 강조).

클릭 → `onOpen(doc_id, page, annotation_id)` → `page.tsx`에서:
```tsx
setSelectedId(docId);
setSelectedPage(page);
const ann = annotations.find((a) => a.id === annotationId);
if (ann) setPopover({ kind: "edit", annotation: ann });
```
즉 **해당 도면/페이지로 점프 + 편집 팝오버 자동 열림**.

### 하단 카운터
`"{filtered.length} / {annotations.length} 건"`.

## 6. 생성 흐름 전체 (시퀀스 다이어그램 축약)

```
user clicks PdfViewer surface
 → PdfViewer.handleSurfaceClick: (x,y) 정규화
 → onPageClick(x,y,page) callback
 → page.tsx: setPopover({kind:"create", draft:{doc_id,page,x,y}})
 → AnnotationPopover renders

user fills text/author/type/tags → clicks 저장
 → AnnotationPopover.handleSave:
     onSave({ text, author, type, tags })
 → page.tsx: addAnnotation({ doc_id, page, x, y, ...payload })
 → useAnnotationsStore:
     id 생성, created_at 세팅 → setAnnotations(prev + newAnn)
 → setPopover(null)  // 모달 닫힘
 → useEffect([annotations, hydrated]): saveToStorage
 → AnnotationLayer 재렌더: 새 핀 그림
 → 헤더 카운터 업데이트
 → (AnnotationList 탭이 활성이면) 리스트에도 즉시 추가
```

## 7. 편집 흐름

```
user clicks 핀 또는 AnnotationList 항목
 → setPopover({kind:"edit", annotation})
 → 팝오버가 initial = annotation 값으로 렌더

user 수정 → 저장
 → onSave → updateAnnotation(id, patch)
 → setPopover(null)

또는 삭제
 → onDelete() → deleteAnnotation(id) + setPopover(null)
```

## 8. 영속 경계

- **브라우저 기반**: 다른 기기에서 열면 주석 없음. 현재 MVP 가설 검증에 서버 필요 없음.
- **localStorage 용량**: 주석 하나 평균 ~200 bytes 잡으면 ~5MB 한계 내 2만 건 수용 가능. Layer 0에서 문제 없음.
- **초기화**: 개발자도구 → Application → Local Storage → `mvp-annotations-v1` 삭제. 또는 콘솔에 `localStorage.removeItem("mvp-annotations-v1")`.

## 9. 확장 포인트

| 요구 | 수정 위치 |
|---|---|
| 주석에 이미지 첨부 | `Annotation` 타입 + 팝오버 + 레이어(썸네일) |
| 주석 정렬(날짜순/타입순) | `AnnotationList`에 sort dropdown |
| 범위 주석(사각형 박스) | 새 타입 `"range"` + 좌표 2쌍 + 레이어에서 `<div>` 박스 |
| 서버 저장 | `useAnnotationsStore`에 `saveToApi` 추가, optimistic update |
| 다중 사용자 | 충돌 해결(LWW 타임스탬프) + 사용자 ID 필드 |
| @mention | 메모 파서 + 사용자 목록 data-loader |

## 10. 트러블슈팅

- **핀이 안 보임**: `surfaceSize.width === 0`일 수 있음 (`PdfViewer.tsx:217` 가드). onLoad/onRenderSuccess 콜백이 실행됐는지 확인.
- **새로고침 시 주석 사라짐**: localStorage 비활성화 또는 privacy 모드. DevTools Application 탭에서 `mvp-annotations-v1` 존재 확인.
- **주석이 엉뚱한 위치에 찍힘**: `rect.width === 0`인 상태에서 클릭. TransformWrapper가 재마운트되는 순간 짧게 발생 가능.
- **팝오버가 두 개 뜸**: 있을 수 없음 — popover state는 단일. 재현되면 버그.
