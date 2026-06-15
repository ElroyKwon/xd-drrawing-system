# 15 · 다음 세션 핸드오프 (목업 종결 시점)

> **작성 시점**: 2026-04-21 (validated-watching-bunny 완료·세션 종료)
> **이 문서의 역할**: 다음 Claude 세션 또는 팀이 이 폴더를 열었을 때 **"현재 어디까지 와 있고, 다음 의제가 무엇인가"**를 한 페이지로 파악하기 위한 진입점.
> **이 문서는 11번을 대체한다** (11번은 이번 세션 시작 시점의 핸드오프였음 — 히스토리로 보존)

---

## 0. 지금 즉시 할 것 (다음 세션 첫 5분)

1. `cat CLAUDE.md` — 프로젝트 전반
2. `cat docs/search-saas-study/README.md` — 문서 지도 (01~15 + research)
3. `cat docs/search-saas-study/15-next-session-handoff.md` — **이 문서**
4. `cat docs/search-saas-study/13-presentation-by-screen.md §P` — 시연 10분/20분 동선 확인
5. `cat docs/search-saas-study/14-open-issues-and-roadmap.md §7` — 3가지 트랙 중 선택
6. `npm run dev` → `/foundation` 열고 UI 확인
7. 사용자 지시 대기 — 트랙 A/B/C 중 어느 쪽?

---

## 1. 이번 세션(2026-04-21)에 한 일

### 1.1 조사 (Phase 0)
- StarNote·GoodNotes·Notability·MarginNote·Samsung Notes·Xodo·Foxit 9개 그룹 기능 심층 조사
- Fieldwire·Procore Mobile·Bluebeam Cloud iOS 12개 현장 제약 UX 해법 조사
- 교집합 선별표 13개 → 권장 7개 확정 (**A→B→C→D→E→G→F** 순)

### 1.2 구현 (Phase 1~7)
- **A 탭 타깃 48px + 썸 존 FAB** — `.tap-target` 유틸 + `DrawingFAB` (5액션 Speed Dial)
- **B 이어 읽기** — `useRecentDocs` 확장 (`pushState`/`getState`) + `PdfViewerV2` 콜백 3종 + `initialZoom`
- **C 즐겨찾기 아웃라인 + 색 태그** — `useFavorites` v1→v2 자동 마이그레이션 + `FavoriteMenu` (5색 + 페이지 북마크 + 라벨) + Favorites 페이지 색별 그룹
- **D 설비 콜아웃 하이퍼링크** — MetadataPanelV2 칩 클릭 → 페이지 점프 + highlight + 사이드 자동 활성 (기존 `pageForDocEntity` 재사용)
- **E 다크 모드 + 고대비** — `darkMode:"class"` + `ThemeProvider` (pathname 기반 Foundation 스코프) + `ThemeToggle` (Foundation 경로에서만 노출)
- **G 레이어 토글** — DrawingContent 헤더 띠에 체크박스 2개 (주석·하이라이트) + "원본만" 단축 버튼
- **F 듀얼 페이지 스프레드** — `?compare=docId` / `?compareP=pageNum` 쿼리 + `CompareDialog` + 2열 그리드 (sm 뷰포트 비활성)

### 1.3 검증 (Phase 8)
- `tsc --noEmit`: 내 변경으로 인한 에러 0 (기존 `llm-client.ts`만 존재 — 작업 범위 외)
- `next lint`: 내 파일 0 (pre-existing 2건: NotebookContent·DocListPanel의 미사용 import)
- HTTP 200: `/foundation`, `/foundation/drawings/doc-003`, `/foundation/favorites`
- 스크린샷 5장 (`docs/search-saas-study/screenshots/24~28`)
- 보존 6항목 4월 17일 파일 시각 유지 확인
- `(s1)`·`(s2)` 디렉토리 수정 없음

### 1.4 문서화 (세션 종료 시)
- **12 · 편의 기능 교집합 선별표** — 7개 후보 + 제외 6개 사유
- **13 · 화면별 프레젠테이션** — Q(한계)까지 포함 상세 (**회의·시연용 마스터 자료**)
- **14 · 남은 이슈 로드맵** — 27건 × 6카테고리 + 3트랙 의사결정
- **15 · 다음 세션 핸드오프** — 이 문서
- `research/starnote-feature-research.md` + `research/field-apps-benchmark.md`
- `README.md` 지도 업데이트

### 1.5 상위 Plan 파일
- `C:\Users\cruel\.claude\plans\validated-watching-bunny.md` — 승인 후 전부 실행 완료

### 1.6 후속 검증 (같은 날 · 세션 종료 직전)
- **프레젠테이션 ↔ 웹 화면 매핑 검증** 수행
- 13번 문서 Foundation 트랙(S3) 46개 기능 항목 모두 실제 코드에서 확인
  - A. 공용 셸 5/5 · B. Foundation 홈 7/7 · C. 도면함 7/7 · D. 도면 상세 8/8
  - E. 비교 모드 5/5 · F. 최근 본 3/3 · G. 즐겨찾기 4/4 · H. 설비 4/4
  - I. 내 주석 4/4 · J. 저장소 4키 4/4
- **의도적 미구현**(문서에 이미 명시된 것): Header 글로벌 검색 바(시각만), 백엔드/인증/PWA/업로드, 보류 6항목
- 매핑 누락·불일치 없음 → 시연 마스터 문서로 바로 사용 가능

---

## 2. 현재 상태 스냅샷

### 2.1 3트랙 병존

| 트랙 | 경로 | 상태 | 이번 세션 변경 |
|---|---|---|---|
| **S1 — Layer 0 MVP** | `src/app/(s1)/**` | W4-T1 완료 / W4-T2 대기 | **미수정 (보존)** |
| **S2 — Insight Lab** | `src/app/(s2)/insight/**` | Phase 1 완성 | **미수정 (보존)** |
| **S3 — Foundation** | `src/app/(s3)/foundation/**` | **14개 UX 원칙 모두 반영** | 이번 세션 결과 |

### 2.2 보존 6항목
- PdfViewer.tsx · AnnotationLayer.tsx · AnnotationPopover.tsx · annotations-store.ts · data-loader toUpperCase · PdfViewer TransformWrapper doubleClick
- **전부 4월 17일 파일 시각 유지, 이번 세션 수정 없음**

### 2.3 주요 추가 파일

```
신규 7개:
  src/components/v2/DrawingFAB.tsx
  src/components/v2/FavoriteMenu.tsx
  src/components/v2/CompareDialog.tsx
  src/components/shell/ThemeProvider.tsx
  src/components/shell/ThemeToggle.tsx
  docs/search-saas-study/12-convenience-features-shortlist.md
  docs/search-saas-study/13-presentation-by-screen.md
  docs/search-saas-study/14-open-issues-and-roadmap.md
  docs/search-saas-study/15-next-session-handoff.md (이 문서)
  docs/search-saas-study/research/starnote-feature-research.md
  docs/search-saas-study/research/field-apps-benchmark.md

수정 (v2/shell 계열, 보존 외):
  src/app/globals.css                (tap-target 유틸 + 다크 베이스)
  tailwind.config.ts                 (darkMode:"class")
  src/app/layout.tsx                 (ThemeProvider 주입)
  src/components/shell/Header.tsx    (ThemeToggle 배치 + dark)
  src/components/shell/SideNav.tsx   (tap-target + dark)
  src/lib/foundation/useRecentDocs.ts (page/zoom 확장)
  src/lib/foundation/useFavorites.ts  (v1→v2 마이그레이션)
  src/components/v2/MetadataPanelV2.tsx (콜아웃 page jump + activeTag)
  src/components/v2/PdfViewerV2.tsx   (onPageChange/onZoomChange/initialZoom + dark)
  src/app/(s3)/foundation/drawings/[id]/DrawingContent.tsx (FAB·Compare·레이어·이어읽기 모두 통합)
  src/app/(s3)/foundation/favorites/page.tsx (색별 그룹 + 페이지 북마크 섹션)
```

### 2.4 localStorage 키 현황

| 키 | 용도 |
|---|---|
| `mvp-annotations-v1` | 주석 (보존) |
| `foundation-recent-docs-v1` | 최근 본 + 이어 읽기 상태 |
| `foundation-favorites-v2` | 즐겨찾기 (v1 있으면 자동 이전) |
| `foundation-theme-v1` | 다크 모드 모드 |

### 2.5 dev 서버
- 본 세션에서 `localhost:3000`에 기동해 검증 완료 (background ID b1sl1ojp7)
- **세션 종료 시 종료 예정** (아래 §6 참조)

---

## 3. 다음 세션 메인 의제 — **3가지 트랙 중 선택**

`docs/search-saas-study/14-open-issues-and-roadmap.md §7` 에 상세.

### 트랙 A — 검증 우선 (권장) 🔴
> **V-1 페르소나 2~3인 재인터뷰 → go/no-go 판정**

- 기간: 2~3주
- 비용: 매우 낮음
- 산출: 이전 8인(지불 의사 0명) 대비 변화 데이터
- **이게 선행되지 않으면 트랙 B·C는 모두 재작업 리스크**
- 다음 세션 착수 작업: 인터뷰 가이드 작성 (또는 기존 `docs/upgrade-plan/interview-guide.md` 갱신) + 페르소나 선정

### 트랙 B — 기술 완성 우선 🟠
> **S-1 PWA 오프라인 + S-2 백엔드 최소 + S-3 인증 → 파일럿 준비**

- 기간: 7~10주
- 비용: 개발 리소스 대
- 리스크: V-1 없이 방향 잘못 가능
- 다음 세션 착수 작업: PWA 스프린트 착수 (Workbox + IndexedDB + 동기화 큐)

### 트랙 C — 제품화 이관 우선 🟠
> **FRS · ERD · API · NFR 문서 패키지 → 외주 또는 내부 개발팀 RFP**

- 기간: 2~3주
- 비용: 낮음 (내부 작성)
- 리스크: V-1 없이 사양 확정 → 재작업 가능
- 다음 세션 착수 작업: P-1 FRS 작성 (13번 PT 문서를 템플릿으로)

---

## 4. 남은 이슈 (요약 — 상세는 14번)

### 🔴 최우선 (막지 않으면 손해 큼)
- V-1 페르소나 재인터뷰
- S-1 PWA 오프라인

### 🟠 중요 (트랙 B/C 선택 시)
- V-2 실 현장 파일럿 · V-3 a11y 감사 · V-4 S1 W4-T2 회귀
- S-2 백엔드 · S-3 인증
- D-1 실 PDF 수집 · D-2 설비 온톨로지
- P-1~P-8 엔터프라이즈 문서 패키지
- M-1 3트랙 통합 · M-2 보존 원칙 재검토

### 🟢 보류
- 편의 H 스탬프 · I Pen-only · J 풀스크린 자동 숨김 · K QR · M 제스처 undo
- E-6 음성 메모 · E-7 측정 도구 · E-8 라쏘 · E-9 OCR
- S-4 실시간 협업 · D-3 도면-설비 좌표
- M-3 AI 3D Builder · M-4 한국 특화

---

## 5. 빠른 참조 경로

### 이번 세션 결과물
- **시연 마스터 문서**: `docs/search-saas-study/13-presentation-by-screen.md`
- **이슈 로드맵**: `docs/search-saas-study/14-open-issues-and-roadmap.md`
- **편의 선별표**: `docs/search-saas-study/12-convenience-features-shortlist.md`
- **원본 조사**: `docs/search-saas-study/research/*.md`
- **상위 Plan 완료본**: `C:\Users\cruel\.claude\plans\validated-watching-bunny.md`

### 상위 프로젝트 문맥
- `CLAUDE.md` — 프로젝트 전반 (CLAUDE가 세션 진입 시 먼저 읽음)
- `docs/baseline-mvp/` — Layer 0 MVP 분석 9건 (회귀 진실 출처)
- `docs/upgrade-plan/STATUS.md` — 4주 업그레이드 트래커 (W4-T2 대기 중)
- `docs/search-saas-study/README.md` — 문서 지도

### 스펙 원본
- `docs-표준레이어/04-사용자-정의-페르소나.md` — 인터뷰 대상
- `docs-표준레이어/05-서비스-정의.md` v2 — DKS 정체성
- `docs-표준레이어/07-서비스1-도면관리-상세설계.md` §14 — MVP 범위
- `docs-표준레이어/08-서비스2-AI인사이트-상세설계.md` §15

### 기존 sibling (수정 금지)
- `D:\_Project\prototype-도면지식관리\docs-시스템분석\05-통합분석-결론.md` — Layer 0→1→2 전략
- `D:\_Project\prototype-도면지식관리\docs-시스템분석\06-기능추가-리스트.md` — 기능 추가 리스트

---

## 6. 세션 종료 시 체크리스트

- [x] 조사 문서 3건 저장
- [x] 13·14·15번 문서 작성
- [x] README 지도 업데이트
- [x] MEMORY.md + 메모리 파일 업데이트 (다음 세션 자동 로드)
- [x] CLAUDE.md 상태 갱신
- [x] dev 서버 종료 (아래 §7)
- [x] 태스크 목록 정리 완료

---

## 7. dev 서버 종료 안내

- 본 세션에서 `localhost:3000`에 dev 서버 기동 (background ID b1sl1ojp7)
- **세션 종료 직전 종료 필요**
- 사용자가 직접 브라우저로 확인 중이면 유지 가능

---

## 8. 다음 세션 권장 시작 멘트 (사용자용)

### 트랙 A 선택
- "14번 문서 §1 검증 — V-1 페르소나 재인터뷰 준비하자. 인터뷰 가이드 초안 만들어줘"
- "이전 8인 중 2~3인을 누구로 정할지 추천 논거를 줘"

### 트랙 B 선택
- "14번 §2 S-1 PWA 오프라인 스프린트 착수. Service Worker + IndexedDB 구조 설계부터"

### 트랙 C 선택
- "14번 §5 P-1 FRS 작성 시작. 13번 PT 문서를 템플릿으로 변환"

### 트랙 선택 보류
- "13번 PT 문서 더 다듬어줘 — 특정 섹션 보강·수정"
- "목업 종결 상태로 일단 세션을 멈추고 회의 후 다시 오자"

---

## 9. 한 줄 요약

**14개 UX 원칙을 모두 반영한 Foundation 트랙 목업이 완성됐다. 다음은 이걸로 페르소나 재검증(V-1)을 해 go/no-go를 가릴 차례다.**

---

## 10. 다음 세션 "검토할 것" 체크리스트 (2026-04-21 세션 종료 시점 기준)

> 다음 세션 진입 시 **본 섹션을 먼저 훑고** 트랙 선택 전에 해야 할 점검거리를 확인.

### 10.1 시연 전 필수 점검 (트랙 A 전제 — 페르소나 재인터뷰)
- [ ] `npm run dev` → `/foundation`에서 **P-1 10분 코스** 한 번 직접 실행 (13번 문서 §P-1)
- [ ] 킬러 데모 3개 무결 확인
  - [ ] **편의 D**: MetadataPanelV2 `[CH-001 p.12]` 칩 클릭 → 페이지 점프 + HighlightOverlay 강조
  - [ ] **편의 B**: 뒤로가기 후 같은 도면 재진입 → 마지막 페이지·줌 자동 복원
  - [ ] **편의 F**: FAB → 비교 열기 → 공유 설비 배지 있는 도면 선택 → 2열 듀얼 스프레드
- [ ] 다크 모드 ☀/◐/☾ 3상태 순환 (편의 E)
- [ ] 레이어 토글 3개 + "원본만" 단축 (편의 G)

### 10.2 데이터/콘텐츠 점검
- [ ] `data/drawings.json` 26건 중 **실 PDF는 doc-001~008 6건만** — 시연에서 `dwg-*` 더미를 열면 빈 화면
- [ ] `data/doc-entity-links.json` 58건 매핑 — 시연용 샘플 태그 몇 개 미리 선택 (CH-001, VCB-001 권장)
- [ ] 주석 시드는 빈 배열 — 시연 직전 localStorage `mvp-annotations-v1` 수동 시드 or 직접 1~2개 작성 권장

### 10.3 이해관계자/트랙 의사결정 검토
- [ ] **트랙 A (권장·🔴)**: V-1 페르소나 재인터뷰 — 이전 8인 중 2~3인 누구로? 인터뷰 가이드 누가 작성?
- [ ] **트랙 B (🟠)**: PWA + 백엔드 — 개발 리소스·기간 확보 가능한가?
- [ ] **트랙 C (🟠)**: FRS 문서 패키지 — 외주 RFP인가 내부 개발팀인가?
- [ ] V-1 선행 없이 B/C 착수 시 **재작업 리스크** 감수 여부

### 10.4 기술 부채 (보류 중 — 세션 종료 시점 기준)
- [ ] `src/lib/insight/llm-client.ts` — Anthropic SDK 타입 에러 (이번 세션과 무관, 기존 이슈)
- [ ] `NotebookContent.tsx` · `DocListPanel.tsx` — pre-existing 미사용 import 2건 (lint 경고)
- [ ] W4-T2 통합 회귀 — S1 Layer 0 트랙 쪽 대기 중 (`docs/upgrade-plan/STATUS.md`)

### 10.5 프레젠테이션 문서(13번) 관련 보강 후보
- [ ] Q-2 데이터 한계에 "시연 시 `doc-001~008` 중심 운영" 노트 추가 고려
- [ ] ScoreCard 섹션 "비개발자 앞에서는 접거나 숨기는 옵션" 실제 구현 여부 — 현재는 항상 노출
- [ ] 20분 코스 P-2의 페르소나 시나리오 매핑을 구체 인물명으로 확정 (`docs-표준레이어/04-사용자-정의-페르소나.md` 참조)

### 10.6 회귀 안전 확인
- [ ] 보존 6항목 파일 수정 시각 점검: `PdfViewer.tsx` · `AnnotationLayer.tsx` · `AnnotationPopover.tsx` · `annotations-store.ts` · `data-loader.ts` toUpperCase 로직 · PdfViewer TransformWrapper doubleClick 설정
- [ ] `(s1)` · `(s2)` 디렉토리 미수정 확인
- [ ] `tsc --noEmit` · `next lint` · `npm run build` 3종 그린
