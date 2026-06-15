# 03 · 뷰어 (PdfViewer)

중앙 패널. 문서 하나를 선택했을 때 보여주는 단일 컴포넌트 `src/components/PdfViewer.tsx` (237줄).

## 1. 세 모드: `"pdf" | "image" | "empty"`

```ts
function pickMode(doc: DocSnippet, pdfFailed: boolean): Mode {
  const hasImage = Boolean(doc.drawing_ref);
  const hasPdf   = Boolean(doc.files?.some((f) => f.format === "PDF"));
  if (hasPdf && !pdfFailed) return "pdf";
  if (hasImage)             return "image";
  return "empty";
}
```

우선순위는 **PDF → 이미지 → 빈 상태**다.

- `pdfFailed`는 `<Document onLoadError>` 콜백으로 세팅된다. 한 번 실패하면 같은 세션에서 이미지로 폴백.
- `CLAUDE.md`에 "이미지 fallback 우선"이라 적혀 있지만 **현재 코드는 PDF 우선**이다. 2026-04-17 세션에서 실 PDF(`mech.pdf`)가 들어오면서 로직이 바뀌었고 `CLAUDE.md`가 아직 갱신 안 됨 (07에 기록). 이 문서가 현재 동작의 정답.
- `"empty"`: `"표시할 파일이 없습니다."` 대시 박스.

## 2. 레이아웃 (상→하 3단)

```
┌─ 상단 바: 제목 · type · p.N · last_updated ───┬─ 페이지 네비 + 원본PDF 링크 ─┐
├─ 줌 바: "PDF 뷰어" / "이미지 뷰어"            │ [−] [+] [리셋]               │
└─ 본문: TransformWrapper(재zoom-pan-pinch) 안 ─────────────────────────────────┘
          └─ surfaceRef div (cursor:crosshair) ← 클릭 수집
              ├─ <Document><Page/></Document>  (mode=pdf)
              ├─ <img>                         (mode=image)
              └─ renderOverlay({...})          ← AnnotationLayer 이 자리
```

- `TransformWrapper`는 `react-zoom-pan-pinch`. `minScale=0.4, maxScale=6, wheel.step=0.2`, 더블클릭 확대 비활성.
- `key={`${doc.doc_id}-${pageNumber}-${mode}`}`: doc 또는 page 또는 mode가 바뀌면 wrapper가 리마운트돼 zoom이 초기화됨.

## 3. 페이지 네비게이션

- **PDF 모드만** 표시 (이미지 모드는 단일 페이지 개념이 없어서 숨김).
- `totalPages`는 `<Document onLoadSuccess={(info) => setTotalPages(info.numPages)}>`로 받는다.
- `pageNumber` 초기값은 `pageOverride ?? 1`. `useEffect([doc.doc_id, pageOverride])`로 prop이 바뀌면 동기화.
- `‹` / `›` 버튼, 가운데 `{pageNumber} / {totalPages}` 표시. `disabled={pageNumber <= 1}` 등으로 경계 방어.

## 4. "원본 PDF" 링크

`doc.files`에 PDF가 있으면 우측 상단에 링크. `target="_blank" rel="noopener noreferrer"`로 새 탭 열기. 현재 `documents.json`의 `mech.pdf`가 53페이지 실 PDF라 클릭하면 브라우저 기본 PDF 뷰어로 열린다.

## 5. 줌/팬 제어

```tsx
<TransformWrapper ...>
  {({ zoomIn, zoomOut, resetTransform }) => (
    ...
    <button onClick={() => zoomOut()}>−</button>
    <button onClick={() => zoomIn()}>+</button>
    <button onClick={() => resetTransform()}>리셋</button>
    ...
  )}
</TransformWrapper>
```

휠 스크롤로도 줌됨. 드래그로 팬. `TransformComponent`에 `wrapperClass="!h-full !w-full"`, `contentClass="!flex !items-start !justify-center !p-6"` — Tailwind important prefix(`!`)로 라이브러리 기본 스타일 덮어쓰기.

## 6. 좌표 정규화 (0~1)

뷰어가 주석과 맞물리는 핵심.

```tsx
const handleSurfaceClick = (e: React.MouseEvent<HTMLDivElement>) => {
  if (!onPageClick) return;
  const rect = e.currentTarget.getBoundingClientRect();
  const x = (e.clientX - rect.left) / rect.width;   // ∈ [0,1]
  const y = (e.clientY - rect.top)  / rect.height;  // ∈ [0,1]
  if (x < 0 || x > 1 || y < 0 || y > 1) return;     // 경계 밖 무시
  onPageClick(x, y, pageNumber);
};
```

**왜 정규화?** PDF나 이미지가 줌/리사이즈돼도 주석 핀은 같은 상대 위치에 머물러야 한다. pixel 좌표로 저장하면 창 크기 바뀔 때 어긋남.

동일한 원리가 `AnnotationLayer`에서 역방향으로:
```tsx
const left = a.x * width;    // 정규화 → 픽셀
const top  = a.y * height;
```

**주의**: `rect`는 `surfaceRef` div의 rect다. 이 div는 PDF Page 또는 `<img>`를 감싸고 있다. 줌이 적용된 후의 rect라 **`react-zoom-pan-pinch`의 scale은 rect에 이미 반영**되어 정규화 값이 여전히 논리 좌표로 일관된다. 수동 좌표 변환 불필요.

## 7. `surfaceSize` 추적

```tsx
const [surfaceSize, setSurfaceSize] = useState({ width: 0, height: 0 });
```

`<Page onRenderSuccess>` 또는 `<img onLoad>`에서 `surfaceRef.current.clientWidth/Height`를 읽어 저장. `renderOverlay`에 전달되는 `renderedWidth/Height`가 이 값이다. `AnnotationLayer`는 이 크기를 받아 핀 좌표를 계산한다.

`surfaceSize.width > 0`이 되어야 오버레이가 그려짐 (`PdfViewer.tsx:217`).

## 8. `renderOverlay` 확장 포인트

```tsx
interface Props {
  doc: DocSnippet;
  pageOverride?: number;
  renderOverlay?: (surface: ViewerSurface) => React.ReactNode;
  onPageClick?: (xNorm: number, yNorm: number, pageNumber: number) => void;
}
interface ViewerSurface {
  mode: Mode;
  pageNumber: number;
  totalPages: number;
  renderedWidth: number;
  renderedHeight: number;
}
```

현재는 `AnnotationLayer`가 유일한 오버레이지만, 같은 슬롯에 **설비 심볼 하이라이트**, **검색어 박스**, **측정 도구** 등을 얹을 수 있다. 컨벤션은 동일하게 정규화 좌표 사용.

## 9. react-pdf 세팅

```tsx
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = "/pdf.worker.min.mjs";
```

- **워커는 로컬 서빙**: CDN이 아니라 `public/pdf.worker.min.mjs`를 직접 가져간다. 폐쇄망에서도 작동.
- **textLayer / annotationLayer 비활성**: `<Page renderTextLayer={false} renderAnnotationLayer={false}>`. 우리는 자체 주석을 얹으므로 pdfjs 기본 레이어 불필요. 성능 이득도 있음.
- **dynamic import**: `page.tsx`에서 `dynamic(() => import("@/components/PdfViewer"), { ssr: false })`. Next 서버 렌더 시 뷰어는 skeleton만.

## 10. 에러 상태

```tsx
<Document
  file={pdfUrl}
  onLoadError={() => setPdfFailed(true)}
  loading={<div>...PDF 로딩…</div>}
  error={<div>PDF를 읽을 수 없습니다. (시드 PDF는 더미 파일)</div>}
>
```

- **로딩 중**: 450×600 회색 박스 + "PDF 로딩…".
- **실패**: 같은 박스에 붉은 글씨. `pdfFailed` 플래그가 세팅되면 다음 렌더에서 `pickMode`가 이미지로 폴백. 이 시나리오는 `doc.drawing_ref`가 있을 때만 의미 있음 — 없으면 `empty`.

## 11. 모바일/작은 뷰포트

- `<Page width={Math.min(900, surfaceSize.width || 900)}>` — 최대 900px. 모바일이면 `surfaceSize.width`가 더 작을 테지만, 중앙 main 폭 자체가 `1fr`이라 1280 미만 뷰포트에서는 레이아웃 깨짐. **Phase 0에서 모바일은 제외됨.**

## 12. 수정 가이드

- **핀을 찍지 못하게** → `onPageClick`를 prop에서 제거. cursor도 `"default"`로 돌아감.
- **페이지 직접 입력(1→53 점프)** → `pageNumber` 상태에 `<input type="number">` 하나 추가.
- **검색어 박스 표시** → `renderOverlay`에 추가 prop 전달해서 `<AnnotationLayer>`와 나란히 렌더.
- **DWG(AutoCAD) 지원** → `pickMode`에 모드 추가 + 별도 컴포넌트. 현재 DWG 렌더링 라이브러리는 상용이라 경제성 판단 필요.
