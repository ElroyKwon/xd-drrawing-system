# 10 · 노트 앱 스타일 리빌드 — 할 일 정리 & UX 분석

> **작성 시점**: 2026-04-21 (사용자 지시: "스타노트 같은 노트 앱 분석 후 검색을 노트 목록처럼 보이게 리빌드")
> **지시 범위**: (1) 할 일 정리 / (2) 인기 노트 앱(StarNote 등) UX 분석 / (3) 기본 기능 충실화를 위한 리빌드

---

## 1. 할 일 정리 (현 시점)

### 1.1 완료된 작업 (01~09)
- ✅ Layer A/C 마이크로 요건 100% 충족 (08)
- ✅ 메뉴 IA 매크로 구조 — 7개 메뉴 `(s3)/foundation/` 추가 (09)
- ✅ localStorage 훅 2개 (최근본/즐겨찾기)
- ✅ 스코어카드·대시보드·라이브러리·설비 카탈로그·내 주석 구현
- ✅ 기존 `(s1)`·`(s2)` 무영향 유지

### 1.2 이번 세션 신규 작업 (사용자 지시)
- **T-N1**: StarNote + 현대 노트 앱(Notion/Apple Notes/Bear/Obsidian) UX 분석 → §2
- **T-N2**: 노트 앱 스타일 레이아웃 설계 (리스트 + 프리뷰) → §4
- **T-N3**: `/foundation/search` 리빌드 (설계 확정 후)
- **T-N4**: 라이브러리도 노트 앱 스타일 반영 여부 결정
- **T-N5**: 썸네일/프리뷰 컴포넌트 (도면 PDF 첫 페이지 미니 뷰어 또는 이미지 fallback)
- **T-N6**: 회귀 검증 + 스크린샷 + 완료 보고

### 1.3 이전에 사용자 선택으로 제외되었지만 여전히 대기 중
- 업데이트 피드 메뉴
- 개정 이력 메뉴 (revision 기반 시간축)
- 업로드 mock UI
- 활용 리포트 (localStorage 통계)

### 1.4 혁신 트랙 (별도, 현 트랙 아님)
- Layer D — Click-to-Search / Search-to-Highlight 좌표 기반 / 2-hop 그래프 / 포지셔닝 혁신
- 기본 충실 완료 후 별도 의사결정

### 1.5 프로젝트 전체 관점의 남은 큰 축
- **페르소나 재검증** (이전 8인 중 2~3인 — Foundation 트랙을 시연 자산으로)
- **(s2) Insight Lab 빌드 에러** (내 작업 무관, 손대기 애매)
- **실 도면 데이터 확장** — 청주 Phase 0 실 데이터 수신 여부

---

## 2. 노트 앱 UX 분석

### 2.1 StarNote (사용자 지정 벤치마크)

**사용자 ultrathink 피드백 (2026-04-21)**: *"우리도 도면을 PDF로 제공하고, 스타노트도 PDF 지원 기능으로 인기다"* — 즉 StarNote는 "노트 앱"의 표층이 아니라 **"PDF를 1급 시민으로 다루는 워크플로우"** 의 성공 사례. 우리 프로젝트와 **축이 직접 겹친다**.

**StarNote의 PDF 중심 특징**:
- **PDF import** + 손글씨 주석 + 하이라이트 + 텍스트박스 직접 기입
- **분할 뷰** — PDF 읽기 + 노트 필기 **동시** (split view)
- **주변 여백 조정** — PDF 원본 밖에 추가 주석 공간
- **폴더 + 태그 + 전역 검색** — PDF 다수를 한 라이브러리에서 관리
- **PDF·PPT·DOC·EPUB·MOBI 모두 import** — 문서 포맷 중립
- **Outline 네비게이션** — 긴 PDF 내 섹션 점프
- **PDF + 손글씨 별도 레이어** 저장 (원본 보존)
- **클라우드 싱크** — 기기 간 PDF + 주석 동기화
- 크로스 플랫폼: iOS·Android·Windows·갤럭시탭

**도면 SaaS 직접 적용 매핑**:
| StarNote | 우리 프로젝트 |
|---|---|
| PDF = 노트 단위 | 도면 PDF = 카드 단위 ✅ |
| 썸네일 라이브러리 | `drawing_ref`/PDF 첫 페이지 렌더 필요 ❌ |
| 폴더 = 과목/프로젝트 | 학제·위치·프로젝트 ✅ (필터 형태) |
| 태그 | 설비 태그 (`doc-entity-links.json`) ✅ |
| 분할 뷰 (목록+본문) | 현재 클릭 시 별도 페이지 ❌ |
| PDF 내 + 전체 검색 | 텍스트 검색은 되나 UI 통합 ❌ |
| 주석 오버레이 (레이어 분리) | AnnotationLayer ✅ |
| Outline 목차 | 없음 ❌ |

### 2.1bis 참조 앱 추가 — LiquidText · MarginNote 4

사용자 지적이 "PDF 중심"인 만큼 같은 계보의 참조를 넓힌다.

**LiquidText** (PDF 리서치 전용):
- 대시보드 **리스트 ↔ 그리드 뷰 토글** + 이름·날짜 정렬
- 무한 워크스페이스 — 여러 PDF 한 프로젝트
- 심플 UX 중시

**MarginNote 4** (PDF 학습/연구 도구):
- 3 섹션 분할 — **Document** (원본) / **Study** (워크스페이스+마인드맵) / **Review** (카드)
- 복잡하지만 "문서→지식→복습" 흐름을 명시적으로 분리
- AI 노트·마인드맵

**Notability** (PDF 필기 대중):
- 노트 목록 썸네일 카드
- iPad에서 분할 뷰
- 필기·오디오 녹음

### 2.2 Apple Notes
- iPad에서 **3열**: 사이드바(폴더) + 목록 + 프리뷰
- iPhone에서 **2열 stack**: 목록 → 탭하면 프리뷰 전체화면
- 목록 카드: 제목 + 본문 스니펫 2줄 + 수정 시각 + 미니 썸네일(이미지/그림 있을 때)

### 2.3 Bear
- 좌측 사이드바: 태그 트리 (중첩 `#tag/sub`)
- 가운데 목록: 제목 + 스니펫 3줄 + 태그 칩 + 수정일
- 우측 에디터: 마크다운
- **#태그 클릭 = 즉시 필터링**

### 2.4 Notion
- 좌측 워크스페이스 트리
- 데이터베이스 뷰 다양 (테이블/리스트/보드/갤러리/캘린더/타임라인)
- 갤러리 뷰에 커버 이미지

### 2.5 Obsidian
- 좌측 파일 트리 + 태그 패널
- 가운데 에디터 탭
- 우측 백링크·그래프

### 2.6 공통 패턴 (5개 앱 교집합)

| 요소 | 공통 패턴 |
|---|---|
| **레이아웃** | 2열 또는 3열, 데스크톱 3열 + 모바일 2열 Stack |
| **좌측 사이드바** | 폴더/태그/즐겨찾기 트리, 검색창 상단 |
| **중앙 목록** | 제목 + 스니펫 + 메타(수정일·태그 칩) + 썸네일 or 미니 프리뷰 |
| **우측** | 선택 항목 프리뷰 (읽기 모드) 또는 에디터 |
| **정렬** | 수정일 / 제목 / 생성일 |
| **뷰 토글** | 리스트 ↔ 갤러리(썸네일 카드) |
| **선택 상태** | 목록에서 선택 항목 하이라이트, 동일 뷰에 프리뷰 업데이트 |
| **빈 상태** | 대형 아이콘 + 안내 + CTA |

### 2.7 PDF 중심 노트 앱의 7개 공통 DNA (재정리)

사용자 피드백을 중심축으로 StarNote·LiquidText·MarginNote·Notability·Bear·Apple Notes의 공통 DNA 추출:

1. **PDF(또는 노트)가 "파일"이 아니라 "라이브러리 카드"** — 최상위 시민
2. **썸네일 라이브러리** — 첫 페이지 미리보기 또는 커버로 시각 탐색
3. **분할 뷰(목록 + 본문 동시)** — 클릭 후 페이지 이동 없이 즉시 프리뷰
4. **PDF 내 + 전체 검색 통합** — 한 검색창에서 양쪽 결과 병렬 표시
5. **주석은 원본과 분리된 오버레이** — 원본 PDF 손상 없이 기록
6. **리스트 ↔ 그리드 뷰 토글** — 상황별 인지 부하 조절
7. **메타 다축 정렬/필터** — 폴더·태그·날짜·제목 혼합

---

## 3. 현 `/foundation/search`·`/foundation/library`와의 갭 (PDF 중심 재해석)

| 7개 DNA | 우리 현재 | 갭 |
|---|---|---|
| PDF = 1급 시민 | 도면이 이미 PDF ✅ | — |
| 썸네일 라이브러리 | DocCard에 썸네일 없음 ❌ | **썸네일 렌더 필요** |
| 분할 뷰 (목록+본문) | 클릭 → 페이지 이동 ❌ | **인라인 프리뷰 필요** |
| PDF 내 + 전체 검색 통합 | TextLayer 활성만, UI 분리 △ | 결과 목록 UI 필요 |
| 주석 오버레이 분리 | AnnotationLayer ✅ | — |
| 리스트 ↔ 그리드 토글 | 없음 ❌ | **토글 필요** |
| 메타 다축 정렬/필터 | 학제·종류·위치·정렬 ✅ | — |

**결론**: 현재는 "파일 검색 사이트" 단계에 머물러 있음. StarNote 수준의 **"PDF 도면 라이브러리 + 분할 뷰어"**로 가려면 **썸네일 + 인라인 프리뷰 + 뷰 토글 + PDF 내 검색 UI** 4축을 더해야 함.

→ **핵심 리빌드 방향**: **"StarNote 스타일 PDF 도면함"** 한 화면에 라이브러리 + 뷰어 통합.

---

## 4. 리빌드 설계 후보 4안 (PDF 중심 재구성)

모든 안은 **"검색과 라이브러리를 통합한 하나의 도면함"** 전제 — StarNote가 검색/라이브러리를 분리하지 않듯.

### 4.1 안 A — 2열 (Apple Notes·Bear)
```
┌──────────────────┬─────────────────────────────┐
│ [검색창]          │ [선택 도면 제목]              │
│ [학제·종류·정렬]  │ [도면번호·Rev·위치]           │
├──────────────────┤─────────────────────────────│
│ ▷ 카드 A 썸네일    │                             │
│   제목·스니펫      │  [PDF 첫 페이지 미니 뷰어]   │
│   #VCB #CH        │                             │
├──────────────────┤ [연결 설비 칩 · 주석 N건]    │
│ ▶ 카드 B (선택)   │                             │
│   …               │ [↗ 전체 뷰어로 열기]          │
└──────────────────┴─────────────────────────────┘
```
- 목록 380px + 프리뷰 나머지
- 심플, 모바일 친화
- **리스트/그리드 토글 없음**

### 4.2 안 B — 3열 (Apple Notes iPad · StarNote)
```
┌────────┬──────────────────┬─────────────────┐
│ 학제·  │ [검색창]           │ [선택한 도면]     │
│ 위치   │ [정렬]             │ [메타]           │
│ 태그   │                   │                 │
│ 트리   │ ▷ 카드 A 썸네일    │ [PDF 첫 페이지]  │
│        │ ▶ 카드 B (선택)    │                 │
│ #VCB   │ ▷ 카드 C           │ [연결 설비 칩]   │
│ #CH    │                   │ [주석 N건]       │
│ 전기   │                   │                 │
│ 기계   │                   │ [↗ 전체 뷰어]    │
└────────┴──────────────────┴─────────────────┘
```
- 사이드바 200px + 목록 320px + 프리뷰 나머지
- 트리에서 태그 클릭 = 즉시 필터
- 모바일은 탭 스택으로 degrade

### 4.3 안 C — 3열 + 리스트/그리드 토글 (StarNote 最 근접) ⭐
- 안 B + **상단 뷰 토글** `리스트 · 그리드(썸네일 카드 3×N)`
- 그리드 전환 시: 목록 열 확장(프리뷰 접힘) + 썸네일 카드 3xN 표시
- 다시 리스트 전환 시: 목록 좁아지고 프리뷰 재등장
- StarNote·LiquidText 공통 패턴

### 4.4 안 D — MarginNote 스타일 3섹션 (연구/학습 지향)
```
[ Document | Study | Review ]  ← 상단 탭
Document: 위 안 B와 동일
Study:    도면 1개 + 주석/태그 마인드맵
Review:   주석 플래시카드
```
- 학습·연구 특화라 과한 편. 참고용으로만 기록.

### 4.5 썸네일 렌더 전략 4가지

StarNote는 PDF 첫 페이지를 썸네일로 쓴다. 우리에게 선택지:

| 전략 | 설명 | 속도 | 정확도 | 복잡도 |
|---|---|:---:|:---:|:---:|
| **T1** | `drawing_ref` 이미지 우선, 없으면 회색 placeholder + 제목 오버레이 | 즉시 | 중 | 낮 |
| **T2** | `react-pdf`로 PDF 첫 페이지 `width=160` 미니 렌더 (모든 카드가 PDF 로딩) | 느림 | 고 | 중 |
| **T3** | 빌드 시 사전 이미지 생성(`pdf-poppler` 등), `public/thumbs/` 서빙 | 즉시 | 고 | 고(파이프라인) |
| **T4** | **T1 우선 + T2 폴백** — 이미지 있으면 그걸, 없으면 PDF 미니 렌더 | 혼합 | 고 | 중 |

**권장**: **T4** — `drawing_ref`가 있는 8건은 즉시 표시, `dwg-*` 15건은 PDF 첫 페이지를 지연 렌더(Intersection Observer로 화면에 들어올 때만).

---

## 5. 결정 필요한 것 (PDF 중심 재조정)

1. **레이아웃 안** = A(2열) / B(3열) / **C(3열 + 토글 — StarNote 최근접)** / D(3섹션) 중?
2. **통합 방식** =
   (a) 기존 `/foundation/search`와 `/foundation/library`를 하나의 신규 **"도면함"** 메뉴로 통합 (권장)
   (b) `/foundation/search`만 리빌드, 라이브러리는 그대로
   (c) 새 라우트 `/foundation/notebook` 신설, 나머지 유지
3. **썸네일 전략** = T1 / T2 / T3 / **T4 (권장)** 중?
4. **PDF 내 검색 결과 UI 추가 여부** = (있음 — 전체 검색과 별도 탭) / (없음 — Ctrl+F만)
5. **모바일 처리** = 탭 스택(목록↔프리뷰 전환) / 생략(모바일에선 기존 카드 리스트)

## 6. 작업량 추정

| 안 | 신규 코드 | 추정 |
|---|---|---|
| A (2열) | SearchContent 재작성 + `DocPreviewPanel.tsx` + `PdfThumbnail.tsx` | 4~5h |
| B (3열) | A + `TagTreePanel.tsx` | 6~7h |
| **C (3열+토글)** ⭐ | B + `ViewModeToggle` + `ThumbnailGrid` 모드 | 8~9h (**1일**) |
| D (3섹션) | C + Study/Review 섹션 | 과대 (이번 스코프 제외) |

---

## 7. 구현 결과 (2026-04-21)

사용자 선택 **C(3열+토글) / 통합 / T4**로 구현·검증 완료.

### 7.1 신규 라우트 & 컴포넌트
- `src/app/(s3)/foundation/notebook/page.tsx` + `NotebookContent.tsx` — 3열 통합
- `src/components/v2/TagTreePanel.tsx` — 좌측 트리 (학제·위치·태그 prefix 그룹)
- `src/components/v2/DocListPanel.tsx` — 중앙 목록 (리스트 ↔ 그리드 토글)
- `src/components/v2/DocPreviewPanel.tsx` — 우측 프리뷰 (썸네일 + 메타 + 연결 설비 + 주석 + 전체뷰어)
- `src/components/v2/PdfThumbnail.tsx` — T4 하이브리드 썸네일 (IntersectionObserver 지연 로딩)

### 7.2 리다이렉트
- `/foundation/search?q=…` → `/foundation/notebook?q=…` (파라미터 보존)
- `/foundation/library` → `/foundation/notebook`
- 기존 링크 호환 유지, 사이드바는 1개 "도면함" 메뉴로 정리

### 7.3 추가 변경
- `src/lib/data-loader.ts` — `tagLinkCounts` export 추가 (prefix별 태그 카운트)
- `src/lib/nav.ts` — 검색·라이브러리 2개 → "도면함" 1개로
- `src/app/(s3)/foundation/page.tsx` — "검색으로 시작 →" → "도면함 열기 →"로 CTA 갱신
- `src/app/(s3)/foundation/drawings/[id]/DrawingContent.tsx` — 헤더 링크 "도면함"으로

### 7.4 검증 결과 (Chrome, localhost:3002)
- 콘솔 에러 **0**
- 스크린샷 `screenshots/20~23.png`:
  - `20-notebook-list.png` — 3열 리스트 뷰, 선택 프리뷰
  - `21-notebook-grid.png` — 그리드 토글, 썸네일 카드
  - `22-notebook-tag-vcb001.png` — 태그 `VCB-001` 필터 → 2건 + 활성 필터 칩
  - `23-notebook-search-redirect.png` — `/foundation/search?q=냉동기` → 자동 리다이렉트 → 결과 2건 + 하이라이트 + 프리뷰
- 기존 `(s1)` 및 `(s2)` 무영향 유지

### 7.5 확인된 StarNote DNA 반영 7개
| StarNote DNA | 우리 구현 |
|---|---|
| PDF = 1급 시민 | 도면 카드가 썸네일 중심 |
| 썸네일 라이브러리 | PdfThumbnail (이미지 + PDF 첫 페이지) |
| 분할 뷰 (목록+본문) | 3열 (Tag+List+Preview) |
| PDF 내 + 전체 검색 통합 | 검색바 + 도면 상세 TextLayer (Ctrl+F) |
| 주석 오버레이 분리 | AnnotationLayer + 프리뷰에 주석 수 배지 |
| 리스트 ↔ 그리드 토글 | ☰/▦ 토글 (URL `?view=`) |
| 메타 다축 정렬/필터 | 학제·위치·태그·정렬·검색어 동시 |

---

## 8. 외부 참조

- [StarNote Play Store](https://play.google.com/store/apps/details?id=com.onyx.galaxy.global.note)
- [StarNote App Store (KR)](https://apps.apple.com/kr/app/starnote-%EC%86%90%EA%B8%80-%EB%B0%8F-pdf/id6751570915)
- [Apple Notes — Three-column view on iPad](https://discussions.apple.com/thread/255802131)
- [Bear app](https://bear.app/faq/how-to-use-tables-in-bear/)
- [Best Note-Taking Apps 2026 — Toolradar](https://toolradar.com/guides/best-note-taking-apps)
- [Notion vs Obsidian vs Apple Notes 2026](https://themodernobserver.com/tech/notion-vs-obsidian-vs-apple-notes-2026)
