# StarNote / 노트앱 PDF 편의 기능 심층 조사

> **작성 시점**: 2026-04-21 (validated-watching-bunny Phase 0)
> **목적**: 도면 지식관리 웹 MVP `/foundation/notebook` 및 `/foundation/drawings/[id]`에 반영할 세부 편의 기능의 후보군 도출.
> **조사 대상**: StarNote(Onyx 계열, v1.3.4 기준), GoodNotes 6, Notability, MarginNote 4, Samsung Notes, Xodo/Foxit, Nutrient Web SDK
> **조사 방법**: 공식 도움말·앱스토어 기능 페이지·사용자 리뷰·기술 블로그 본문 — 2026년 4월 기준 최신

---

## 0. 이미 반영된 StarNote DNA 7개 (2026-04-21 notebook 구현)

| # | 기능 | 반영 위치 |
|:-:|---|---|
| 1 | PDF = 1급 시민 | 전체 트랙 |
| 2 | 썸네일 라이브러리 | `DocListPanel` 그리드 뷰 + `PdfThumbnail` |
| 3 | 분할 뷰 | 3열 Notebook + 2열 Drawing 상세 |
| 4 | PDF 내 + 전체 검색 통합(부분) | `SearchBar` + PdfViewerV2 TextLayer |
| 5 | 주석 오버레이 분리 | `AnnotationLayer` + `HighlightOverlay` |
| 6 | 리스트 ↔ 그리드 토글 | `DocListPanel` |
| 7 | 메타 다축 필터/정렬 | `TagTreePanel` + URL 쿼리 |

---

## 1. 필기·주석 그룹

| 기능 | 대표 구현 | 웹 난이도 |
|---|---|:-:|
| 펜 종류(만년필·형광펜·볼펜·붓) | StarNote "Ink Engine" 4종 프리셋 + 색·두께 슬라이더, 압력 감응 | 중 |
| 라쏘 선택→복사·이동 | GoodNotes 6: 사각/자유 라쏘 전환, 선택 후 드래그로 페이지 넘어 이동, Cut/Copy/Duplicate 메뉴 | 중 |
| 지우개(스트로크 vs 픽셀) | GoodNotes: 스트로크 단위(한 획 통째) + 영역 지우개 + "Highlighter only" 옵션 | 하 |
| 레이어 분리 | Xodo/Foxit SDK: annotation을 `Layer` 속성에 귀속, 토글 on/off | 하(SVG 오버레이로 이미 분리) |
| 스탬프·스티커·이미지 삽입 | Foxit: Dynamic Stamp(이름·일시 자동), Xodo: 사용자 PNG 등록 후 탭으로 스탬핑 | 하 |

**설명**: 스트로크는 점 배열을 SVG `<path>`로 저장하는 구조가 일반적. 압력 감응은 Pointer Events API `pressure` 필드로 획 두께를 가변 처리. StarNote는 "proprietary Ink Engine"을 내세워 저지연·보간·잉크흐름을 구현. 현장에서는 붓 필기보다는 **형광펜+볼펜 2종**이면 충분.

---

## 2. 페이지 관리 그룹

| 기능 | 대표 구현 | 웹 난이도 |
|---|---|:-:|
| 페이지 썸네일 사이드바 | GoodNotes: 좌상단 4칸 아이콘 → 썸네일 그리드, 북마크/플래그 필터 | 하 |
| 드래그 재배열/복제/삭제 | GoodNotes: 썸네일 long-press→lift 애니메이션 후 드롭, `...` 메뉴에 Duplicate | 중 |
| 배경 템플릿(무지·격자·줄·도트) | GoodNotes: 페이지별 Change Template, 사용자 PDF 템플릿 업로드 | 하 |
| 듀얼 페이지 스프레드 | Nutrient SDK `LayoutMode.DOUBLE`, AUTO(가로모드 자동 2열), pdf.js는 `pagesPerSpread=2` 커스텀 | 중 |

**설명**: 도면 업무에서는 "평면도+상세도" 나란히 보기가 듀얼 스프레드와 정확히 맞물림. pdf.js는 공식 듀얼뷰가 없고 flexbox로 두 페이지 나열 + 스크롤 동기화 구현이 필요(GitHub issue #590, #2376).

---

## 3. 검색·OCR 그룹

| 기능 | 대표 구현 | 웹 난이도 |
|---|---|:-:|
| 손글씨 텍스트 인식/검색 | GoodNotes: 필기 OCR 내장 인덱스, 문서 내 손글씨까지 검색, "Edit Handwriting Mode" | 상 |
| 한자·외국어 OCR | MarginNote 4 Pro: ABBYY Mobile Capture 엔진, on-device OCR | 중 |
| 선택 텍스트 복사·인용 | MarginNote: excerpt→자동 인용블록 생성, 원문 페이지 백링크 자동 | 중 |
| Tesseract.js v6 브라우저 OCR | 100+언어 WASM, PDF→canvas→`recognize()`, bbox 반환으로 검색 하이라이트 가능 | 중 |

**설명**: 현장 도면은 **인쇄문자 OCR**이 주. Tesseract.js v6는 메모리 누수 개선·속도 향상. 문서 업로드 시 백그라운드로 페이지 캔버스→OCR→인덱스 캐시 저장 패턴 권장.

---

## 4. 동기화·공유 그룹

| 기능 | 대표 구현 | 웹 난이도 |
|---|---|:-:|
| 오프라인 저장 | GoodNotes/Notability: 로컬 DB + 클라우드 sync | 중(IndexedDB) |
| 클라우드 싱크 | Notability Cloud / Goodnotes Cloud: iOS·Android·Win·Web 다기기 sync | 상 |
| 읽기 공유 링크 | GoodNotes: "Send Link"로 브라우저에서 view/comment | 중 |
| 내보내기(PDF·이미지·텍스트) | 양쪽 모두 기본 제공, 주석 flatten 옵션 | 하 |

---

## 5. 책갈피·북마크 그룹

| 기능 | 대표 구현 | 웹 난이도 |
|---|---|:-:|
| 별표/플래그 | GoodNotes: 상단 Star 아이콘 토글, Favorites 탭 집약 | 하 |
| 색 카테고리 태그 | Xodo: 북마크에 색상 할당 | 하 |
| 커스텀 아웃라인 | GoodNotes "Custom Outline": 페이지 `...`→Add to outline→제목 입력, 독립 목차 생성 | 하 |
| 이어 읽기(마지막 위치) | GoodNotes: 문서 재진입 시 마지막 페이지 자동 복원 | 하 |

---

## 6. 오디오 그룹

| 기능 | 대표 구현 | 웹 난이도 |
|---|---|:-:|
| 녹음+필기 동기화 | Notability: 재생 중 필기된 단어/스케치 탭→해당 시점 오디오 재생, 필기가 시간순으로 애니메이트 | 상 |
| 오디오 트랜스크립트 | Notability(2023.10~): 타임스탬프 텍스트 자동 생성, 복사 가능 | 중 |

**설명**: 현장 순찰 시 "이 핀의 설명을 녹음" 유스케이스가 있다면 가치 큼. 스트로크마다 `timestamp` 필드 추가만 하면 구현 기반은 마련됨.

---

## 7. 수식·다이어그램 그룹

| 기능 | 대표 구현 | 웹 난이도 |
|---|---|:-:|
| 손글씨 수식→LaTeX | Notability: handwriting→rendered math, 우클릭 LaTeX 편집 | 상 |
| 도형 인식(스냅) | Notability: 원·사각·화살표 자동 보정, 정렬 가이드 스냅 | 중 |
| 자(ruler)·각도기 | GoodNotes/Notability: 가상 자를 화면에 올려 직선만 수용 | 중 |

---

## 8. 성능·터치 그룹

| 기능 | 대표 구현 | 웹 난이도 |
|---|---|:-:|
| 저지연 필기(<20ms) | Android Jetpack Compose "Low-latency graphics + motion prediction", iPad ProMotion 120Hz | 상(웹은 RAF 한계) |
| 팜 리젝션 | Samsung Notes: "strict palm rejection"=펜 전용 입력 모드, Pointer Events `pointerType==='pen'` 필터 | 중 |
| 제스처 | GoodNotes: 2지 스크롤/줌, 3지 실행취소, 4지 탭 전환 | 중 |

**설명**: 웹에서 완전한 <20ms는 불가능하나, `pointerrawupdate` + OffscreenCanvas로 체감 충분히 낮출 수 있음. `pointerType === 'pen'`만 허용하는 "Pen-only mode" 토글이 실전 최선.

---

## 9. 다중 문서 그룹

| 기능 | 대표 구현 | 웹 난이도 |
|---|---|:-:|
| 분할 뷰(문서 2개) | GoodNotes 5.3+: 탭을 화면 끝으로 드래그→새 창, 독립 스크롤, 같은 문서 page 1과 48 동시 | 중 |
| 탭 관리 | GoodNotes: Android/Win 탭바 정식 지원, 세션 복원 | 하 |
| 드래그앤드롭 간 교환 | GoodNotes: 두 창 간 이미지·텍스트·스트로크 드래그 | 중 |

---

## 10. 웹 도입 상위 15개 후보 (난이도 낮음~중 + 현장 유용성 높음)

| # | 후보 | 난이도 | 도면 도메인 가치 |
|:-:|---|:-:|---|
| 1 | 커스텀 아웃라인(페이지 즐겨찾기 목차) — GoodNotes식 | 하 | 리뷰·승인 흐름 |
| 2 | 별표/플래그 + 색 태그 | 하 | 즉시 식별 |
| 3 | 이어 읽기(마지막 페이지 복원) | 하 | 재방문 컨텍스트 |
| 4 | 듀얼 페이지 스프레드(평면도+상세도) | 중 | **도면 업무 궁합 최상** |
| 5 | Pen-only 모드(Pointer Events 필터) | 중 | 태블릿 현장 오필기 방지 |
| 6 | 라쏘 선택→이동/복제 | 중 | 핀·스트로크 단위 |
| 7 | 스탬프(승인·반려·현장확인) | 하 | 자동 일시/작성자 |
| 8 | 레이어 토글(원본·주석·필기 on/off) | 하 | 이미 구조 분리 |
| 9 | 페이지 썸네일 사이드바+드래그 재배열 | 중 | 다중 페이지 도면세트 |
| 10 | Tesseract.js v6 백그라운드 OCR | 중 | 인쇄 도면 텍스트 색인 |
| 11 | 읽기 공유 링크(토큰 URL) | 중 | 현장↔본사 |
| 12 | 내보내기 PDF(주석 flatten) | 중 | 보고서 |
| 13 | 제스처 2지 팬·핀치 + 3지 undo | 중 | 현장 터치 |
| 14 | 음성 메모(핀당 MP3 첨부) | 중 | 현장 손 바쁠 때 |
| 15 | 같은 PDF 두 페이지 동시 창 | 중 | 참조·상세 대조 |

현장 도면 맥락에서 1~5번은 즉시 Foundation 트랙 편입 후보, 6~10번은 Phase 1, 11~15번은 Phase 2 검토 권장.

---

## 출처

- [StarNote Product Hunt](https://www.producthunt.com/products/starnote)
- [StarNote: Handwriting & PDF — MWM review](https://spark.mwm.ai/en/apps/starnote-handwriting-pdf/6751570915)
- [GoodNotes — Lasso Tool](https://support.goodnotes.com/hc/en-us/articles/10779390143247-Select-content-with-the-Lasso-Tool)
- [GoodNotes — Edit Handwriting Mode](https://support.goodnotes.com/hc/en-us/articles/10779382123919-Reflow-your-handwriting-with-Edit-Handwriting-Mode)
- [GoodNotes — Reordering pages](https://support.goodnotes.com/hc/en-us/articles/7353718659343-Reordering-pages-in-a-document)
- [GoodNotes — Change page template](https://support.goodnotes.com/hc/en-us/articles/7353743758991-Change-a-page-s-template-in-Goodnotes)
- [GoodNotes — Multiple Windows on iPadOS](https://support.goodnotes.com/hc/en-us/articles/7353757107215-Open-Goodnotes-in-multiple-windows-on-iPadOS)
- [GoodNotes — Bookmarks & Custom Outlines](https://support.goodnotes.com/hc/en-us/articles/10110283690511-Using-Bookmarks-and-Favorite-Items)
- [GoodNotes — Share link collaboration](https://support.goodnotes.com/hc/en-us/articles/7353695997839-Share-a-document-for-collaboration)
- [Notability — Recording and Playing Audio](https://support.gingerlabs.com/hc/en-us/articles/206060617-Recording-and-Playing-Audio)
- [Notability — Audio Transcripts (2023)](https://blog.notability.com/post/introducing-audio-transcripts-2)
- [Notability — Handwriting and Math Conversion](https://support.gingerlabs.com/hc/en-us/articles/360003878731-Handwriting-and-Math-Conversion)
- [MarginNote 4 — App Store](https://apps.apple.com/us/app/marginnote-4-ai-notes-mindmap/id1531657269)
- [Foxit PDF SDK for Web — Annotations](https://developers.foxit.com/developer-hub/document/pdf-sdk-web-annotations/)
- [Xodo — Rubber Stamp Annotation](https://feedback.xodo.com/support/solutions/articles/35000251491-rubber-stamp-annotation-pdf-editor-pdf-studio-user-guide)
- [Nutrient — Two-page spread with PDF.js](https://www.nutrient.io/blog/implement-pdf-viewer-pdf-js/)
- [pdf.js Issue #590 — Two-page view](https://github.com/mozilla/pdf.js/issues/590)
- [Tesseract.js 공식](https://tesseract.projectnaptha.com/)
- [Simon Willison — OCR PDFs in browser](https://simonwillison.net/2024/Mar/30/ocr-pdfs-images/)
- [Android Developers — Advanced stylus features](https://developer.android.com/develop/ui/compose/touch-input/stylus-input/advanced-stylus-features)
