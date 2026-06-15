# docs — 도면지식관리 Layer 0 MVP 상세 설명서

이 폴더는 현재 구현된 MVP의 **기능·아키텍처·데이터 스키마·제약**을 설명한다. `CLAUDE.md`가 "세션 진입 가이드(무엇이 되어 있는가)"라면, 여기는 "각 기능이 내부적으로 어떻게 동작하는가"를 담는다.

읽는 순서는 목적에 따라 다르다.

| 목적 | 권장 순서 |
|---|---|
| 처음 프로젝트를 이해하고 싶다 | 00 → 01 → 02 → 03 → 04 → 05 |
| 특정 기능만 수정한다 | 해당 기능 문서만 (02~05 중 하나) + 06 (스키마) |
| 버그·의도된 트레이드오프 파악 | 07 |

## 목차

- [00-overview.md](./00-overview.md) — Layer 0 가설 · 기능 한 줄 요약 · 화면 구조
- [01-architecture.md](./01-architecture.md) — 컴포넌트 트리 · state 소유 · 데이터 흐름
- [02-search-and-list.md](./02-search-and-list.md) — `SearchBar` · `DrawingsList` · Fuse.js 가중치
- [03-viewer.md](./03-viewer.md) — `PdfViewer` · PDF/이미지 분기 (`pickMode`) · 정규화 좌표
- [04-annotations.md](./04-annotations.md) — `AnnotationLayer` · `AnnotationPopover` · `useAnnotationsStore` · `AnnotationList`
- [05-entity-traceback.md](./05-entity-traceback.md) — `EntityToDocs` · `tagToDocsIdx` · 페이지 점프 규약
- [06-data-schemas.md](./06-data-schemas.md) — `types.ts` · 세 개의 JSON 시드 파일 구조
- [07-quirks-and-todo.md](./07-quirks-and-todo.md) — 의식적 제약 · 미해결 결정 · 실 PDF 전환 시 영향

## 이 문서들이 다루지 않는 것

- **왜 Layer 0으로 좁혔는가의 배경** → `D:\_Project\prototype-도면지식관리\docs-시스템분석\05-통합분석-결론.md`
- **빌드/검증 스크립트 세부** → `D:\_Project\prototype-도면지식관리\MVP-BUILD-PLAN.md`
- **페르소나 분석 원본** → `D:\_Project\prototype-도면지식관리\docs-시스템분석\04-*.md`

## 문서 규약

- 파일/줄 참조는 `src/components/PdfViewer.tsx:29` 형태로 표기한다. 에디터에서 바로 점프 가능.
- 타입 정의 인용은 `src/lib/types.ts`의 실제 코드와 동기화돼 있어야 한다. 타입이 바뀌면 06 문서를 즉시 수정.
- 스크린샷은 `tmp/scenario-*.png`에 있고 문서에서 직접 참조하지 않는다 (경로가 개발 환경 의존적).
