# 12 · 편의 기능 교집합 선별표 — Foundation 트랙 도입 후보 7개

> **작성 시점**: 2026-04-21 (validated-watching-bunny Phase 0)
> **선행 문서**: [10-note-ux-redesign.md](./10-note-ux-redesign.md), [11-next-session-handoff.md](./11-next-session-handoff.md)
> **원본 조사**: [research/starnote-feature-research.md](./research/starnote-feature-research.md), [research/field-apps-benchmark.md](./research/field-apps-benchmark.md)
> **상위 Plan**: `C:\Users\cruel\.claude\plans\validated-watching-bunny.md`
> **선별 목적**: StarNote 노트앱 정밀 편의 × 현장 앱 제약 대응 UX 교집합에서 Foundation 트랙에 도입할 5~8개 후보 확정.

---

## 1. 교집합 원리

두 조사의 축이 다르다.
- **StarNote 계열**: 노트앱의 **정밀성·정성적 편의** (라쏘, 스탬프, 듀얼 뷰, OCR, 레이어)
- **현장 앱 3종**: 현장의 **즉시성·가혹한 환경 대응** (오프라인, 장갑 탭 타깃, FAB, QR, 고대비)

교집합은 **"정밀 편의를 현장 제약 안에서 작동하게 한 기능"**. 즉 *StarNote의 세밀한 UI를 현장 UX 문법(큰 타깃·한 손·오프라인)으로 재번역한 것*이 진짜 우리에게 유용하다.

---

## 2. 통합 후보 매트릭스 (13개)

| # | 통합 후보 | StarNote 근거 | 현장 근거 | 난이도 | 현재 구조와 충돌 |
|:-:|---|---|---|:-:|:-:|
| **A** | 장갑 대응 탭 타깃 48px + FAB 썸 존 | — | 4, 8, 9 | 하 | 없음 (CSS만) |
| **B** | 이어 읽기(마지막 페이지·줌·스크롤 복원) | 3 | 1(재접속) | 하 | 없음 (useRecentDocs 확장) |
| **C** | 즐겨찾기 아웃라인(페이지 단위 북마크 + 색 태그) | 1, 2 | — | 하 | 없음 (useFavorites 확장) |
| **D** | 설비 태그 콜아웃 자동 하이퍼링크 | — | 5(Fieldwire 킬러) | 중 | **정확 일치** — `doc-entity-links.json` 이미 존재 |
| **E** | 다크 모드 + 고대비 토글 | — | 3, 7 | 중 | Tailwind `dark:` 전환 |
| **F** | 듀얼 페이지 스프레드(평면도+상세도) | 4 | — | 중 | 보존 PdfViewer 외부에서 2개 인스턴스 |
| **G** | 레이어 토글(원본·주석·필기 on/off) | 8 | (Procore 초안/공유 유사) | 하 | AnnotationLayer 상위 `visibility` 토글 |
| **H** | 스탬프(승인·반려·현장확인) | 7 | 9(원탭 마커) | 하 | AnnotationPopover 상위 프리셋 |
| **I** | Pen-only 모드(Pointer Events 필터) | 5 | — | 중 | AnnotationLayer 보존 규칙 |
| **J** | 풀스크린 모드 + 자동 숨김 툴바 | — | 10 | 중 | 레이아웃 래퍼만 |
| **K** | QR로 설비ID 진입 (`/e/[equipmentId]`) | — | 11 | 중 | 라우트 신설 |
| **L** | PWA 오프라인 셸 + IndexedDB + 동기화 큐 | 4 | 1, 2 | **상** | 큰 규모 — 별도 스프린트 |
| **M** | 제스처 2지 팬·핀치 + 3지 undo | (공통) | 4 | 중 | zoom-pan-pinch 있음 |

---

## 3. 선별 기준 3축

1. **난이도 하~중** (Phase 0~1 범위)
2. **두 조사 모두 가리키거나, 한쪽이 킬러로 지목**
3. **보존 6항목·`(s1)`·`(s2)`와 충돌 없음**

---

## 4. Foundation 트랙 도입 **7개 권장안** (확정)

우선순위·의존성 순.

### 🟢 즉시 착수 (난이도 하, 3개)

| 순위 | 후보 | 구현 포인트 | 예상 공수 |
|:-:|---|---|:-:|
| **1** | **A. 탭 타깃 48px + 썸 존 FAB** | 전체 UI 버튼·핀 히트박스 일괄 점검. `::before` 투명 영역 확장. `/foundation/drawings/[id]`에 우하단 FAB("+주석·역추적·공유·전체화면") | 반일 |
| **2** | **B. 이어 읽기 복원** | `useRecentDocs`에 `{page, zoom, scrollX, scrollY}` 추가. 도면 재진입 시 복원 | 반일 |
| **3** | **C. 즐겨찾기 아웃라인 + 색 태그** | `useFavorites`를 `FavoriteEntry[]`로 확장. `/foundation/favorites` 페이지에 색별 그룹 | 1일 |

### 🟡 다음 스프린트 (난이도 중, 3개)

| 순위 | 후보 | 구현 포인트 | 예상 공수 |
|:-:|---|---|:-:|
| **4** | **D. 설비 태그 콜아웃 자동 하이퍼링크** | **우리의 킬러 후보**. `doc-entity-links.json`의 `CH-001` 등 태그를 PDF 오버레이에서 클릭 영역 자동 렌더 → 탭 시 `EntityToDocs` 팝오버. Fieldwire 이식 한국 플랜트 버전 (옵션 1: 칩 강화) | 2일 |
| **5** | **E. 다크 모드 + 고대비** | `prefers-color-scheme` 추종 + 수동 토글. 도면 배경 흰색은 유지(가독), UI 크롬만 dark. 햇빛 현장 대응 | 1일 |
| **6** | **G. 레이어 토글** | 헤더에 3체크박스(원본/주석/설비칩) — 이미 컴포넌트 분리 | 반일 |

### 🟠 그 다음 (난이도 중상, 1개)

| 순위 | 후보 | 구현 포인트 | 예상 공수 |
|:-:|---|---|:-:|
| **7** | **F. 듀얼 페이지 스프레드** | `/foundation/drawings/[id]?compare=doc-004` 쿼리로 좌우 2개 PdfViewerV2 인스턴스. 보존 규칙 준수 | 2일 |

---

## 5. 의도적으로 제외한 것

| 후보 | 제외 사유 |
|---|---|
| H 스탬프 | G·C와 기능 겹침. 먼저 G·C로 효용 측정 후 재검토 |
| I Pen-only 모드 | 현 페르소나 검증에 태블릿 전제 없음. Phase 2 |
| J 풀스크린 자동 숨김 | A의 FAB로 화면 공간 이득 우선 확보 |
| K QR 진입 | 서버 인프라·현장 스티커 운영 필요. S1 MVP 완료 후 |
| L PWA 오프라인 | 가장 중요하나 규모 큼. **별도 스프린트** 편성 권장 |
| M 제스처 undo | AnnotationLayer 보존 규칙 상 건드릴 여지 적음 |

특히 **L(PWA 오프라인)** 은 두 조사 모두 1순위로 지목한 가장 중요한 원칙이지만 단독 스프린트로 분리하는 편이 안전하다. Service Worker·IndexedDB·충돌 해결·캐시 무효화가 한 묶음이라 Foundation 트랙에 끼워넣으면 위험.

---

## 6. 구현 연계

상위 Plan `C:\Users\cruel\.claude\plans\validated-watching-bunny.md` 의 Phase 1~7에 1:1 매핑되어 있다. Phase 구분·변경 파일·재사용 지점·주의사항 전부 plan 파일에 기술.

| 본 문서 순위 | Plan Phase | 커밋 메시지(예정) |
|:-:|:-:|---|
| 1 (A) | Phase 1 | `feat(foundation): A 탭타깃+FAB` |
| 2 (B) | Phase 2 | `feat(foundation): B 이어읽기` |
| 3 (C) | Phase 3 | `feat(foundation): C 즐겨찾기 아웃라인` |
| 4 (D) | Phase 4 | `feat(foundation): D 설비 콜아웃 하이퍼링크` |
| 5 (E) | Phase 5 | `feat(foundation): E 다크모드` |
| 6 (G) | Phase 6 | `feat(foundation): G 레이어 토글` |
| 7 (F) | Phase 7 | `feat(foundation): F 듀얼 스프레드` |

---

## 7. 검증 연계 (Phase 8)

10개 시나리오 수동 체크 + 보존 6항목 회귀 + 스크린샷 10~15장. 본 문서 §4 각 후보 우측에 검증 항목이 1:1로 매핑되어 Plan §Phase 8에 기술되어 있다.
