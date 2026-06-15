# 00 · 개요

## 1. 이 MVP의 가설 한 줄

> **"검색 + PDF 인라인 + 핀 주석 + 설비 역추적" 4요소만 한 화면에서, NAS + 엑셀보다 나은가?**

배경은 이전 프로토타입(`D:\_Project\prototype-도면지식관리\`)의 페르소나 8인 검증에서 **자발적 지불 의사 0명 / 평균 채택 2.3/10**이 나왔고, 통합 결론은 "극도로 좁은 Layer 0 MVP로 축소하라"였다. 그래서 이 MVP는 이전 데모가 갖고 있던 **AI 메타추출·지식그래프·페르소나 4분할·임팩트 그래프·챗 UI 전부를 의식적으로 배제**하고 4요소만 남긴다.

## 2. 기능 한 줄 요약

| # | 기능 | 무엇을 | 어디에 |
|---|---|---|---|
| 1 | 전문 검색 | 제목·스니펫·학제·종류 4필드에 대한 퍼지 검색 | 좌측 상단 `SearchBar` |
| 2 | 학제/종류 필터 | `ELECTRICAL/MECHANICAL/FIRE/FACILITY` × `drawing/manual/spec/code/checklist` | 좌측 리스트 상단 칩 |
| 3 | 도면 뷰어 | react-pdf로 PDF 렌더, `drawing_ref` 있으면 이미지 fallback, zoom/pan | 중앙 패널 |
| 4 | 핀 주석 | 뷰어 클릭 → (x,y 정규화) 좌표에 핀 + 메모/작성자/태그/종류 | 뷰어 오버레이 + 모달 팝오버 |
| 5 | 주석 영속 | `localStorage["mvp-annotations-v1"]` JSON 배열로 저장 | 브라우저 |
| 6 | 주석 리스트 | 전체 주석을 문서별로 그룹핑, 검색, 클릭 시 해당 페이지 점프 | 우측 탭 2 |
| 7 | 설비 역추적 | `CH-001` 등 태그 → 매칭 도면 리스트, 클릭 시 해당 페이지 점프 | 우측 탭 1 |

이외에 **주석 카운터**(헤더 우측 "주석 N건")와 **선택 도면의 필터링된 결과 수**(좌측 하단 "M / 8 건") 두 개의 작은 상태 표시가 있다.

## 3. 화면 구조 (3분할 grid)

```
+----------------- <header> 타이틀 / 주석 카운터 -----------------+
| aside 360px        | main                 | aside 340px        |
|  SearchBar         |  PdfViewer           |  [역추적|주석] 탭  |
|  discipline chips  |   + AnnotationLayer  |   (전환형)         |
|  type chips        |     overlay          |                    |
|  DrawingsList      |                      |                    |
|  count footer      |                      |                    |
+----------------------------------------------------------------+
                         (AnnotationPopover는 중앙 모달로 띄움)
```

Tailwind grid로 `grid-cols-[360px_1fr_340px]` 고정 — **반응형·모바일 대응은 Phase 0에서 일부러 뺐다**. 뷰포트 가정은 1280px 이상.

## 4. 배제된 것 (의식적으로)

전역 소유자 `src/app/page.tsx`에 있는 state는 7개뿐이다.
- `query`, `discipline`, `docType` — 검색/필터
- `selectedId`, `selectedPage` — 뷰어 대상
- `popover` — 주석 모달 모드
- `sidePanel` — `entity | annotations` 탭

여기에 없는 것 = MVP 범위 밖:
- 사용자 인증 / 권한
- 서버 상태 / 업로드 (문서는 JSON 시드만)
- 실시간 동기화 / 다중 사용자
- AI 요약 / 메타 추출
- 지식 그래프 (노드-엣지 시각화)
- 페르소나 4분할 UI
- 챗 인터페이스

이들이 필요해지는 시점은 Layer 1 이후다. Layer 0은 **"이 4요소로도 현업이 쓰는가"**만 본다.

## 5. 다음 단계 문서로

- **데이터 흐름**을 먼저 파악하고 싶다 → [01-architecture.md](./01-architecture.md)
- **내가 수정하려는 기능**만 빠르게 → 02~05 중 해당 문서
- **어떤 단순화가 나중에 문제될까** → [07-quirks-and-todo.md](./07-quirks-and-todo.md)
