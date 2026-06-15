# 11 · 다음 세션 핸드오프

> **작성 시점**: 2026-04-21 세션 종료 시점
> **이 문서의 역할**: 다음 Claude 세션이 이 폴더를 cwd로 열고 바로 이어받을 수 있도록 모든 맥락을 한 페이지에 정리.
> **다음 세션 지시**: *"스타노트의 세부 편의 기능을 상세 조사하고, 현장에서 도면을 보는 사용 맥락을 참고해 우리 웹 설계에 도입할 것을 생각하자."*

---

## 0. 지금 즉시 할 것 (다음 세션 첫 5분)

1. `cat docs/search-saas-study/README.md` — 01~11 문서 지도 일독
2. `cat docs/search-saas-study/11-next-session-handoff.md` (이 문서) — 현 상태
3. `cat docs/search-saas-study/10-note-ux-redesign.md §7` — 최근 `/foundation/notebook` 구현 결과
4. `npm run dev` → `/foundation` 열어 SideNav "기본 충실" 섹션 확인 (홈/도면함/최근본/즐겨찾기/설비/내 주석 6개)
5. 사용자 지시 대기 — StarNote 세부 조사 + 현장 맥락 반영 방향

---

## 1. 현 상태 스냅샷 (2026-04-21 기준)

### 1.1 3개 트랙 병존

| 트랙 | 경로 | 상태 | 비고 |
|---|---|---|---|
| **S1 — Layer 0 MVP** | `src/app/(s1)/` | W4-T1 완료 + 채팅UI·YAML 연동 / **W4-T2 대기** | 보존 6항목 소유 |
| **S2 — Insight Lab** | `src/app/(s2)/insight/` | Phase 1 완성 (통계×온톨로지+Gemini) | `llm-client.ts` 기존 타입 에러(내 작업 무관) |
| **S3 — Foundation** | `src/app/(s3)/foundation/` | **오늘 신설** (이 세션) | StarNote DNA 반영 PDF 도면함 |

### 1.2 Foundation 트랙 현재 메뉴 (SideNav "기본 충실")

| 라벨 | 경로 | 설명 |
|---|---|---|
| 홈 | `/foundation` | 대시보드 6위젯 + 스코어카드 |
| **도면함** | `/foundation/notebook` | **3열(TagTree+List+Preview) + 리스트/그리드 토글 + T4 썸네일** |
| 최근 본 | `/foundation/recent` | localStorage LRU 20건 |
| 즐겨찾기 | `/foundation/favorites` | ★ 토글 |
| 설비 | `/foundation/equipment` | 50종 태그 prefix 그룹 + drill-down |
| 내 주석 | `/foundation/notes` | 전체 주석 통합 관리 |

- `/foundation/search`, `/foundation/library` → `/foundation/notebook`으로 **redirect**
- `/foundation/drawings/[id]` → 상세 뷰어 + TextLayer + 연결 설비 칩 + 즐겨찾기 버튼

### 1.3 최근 추가된 주요 파일

```
src/app/(s3)/foundation/notebook/{page, NotebookContent}.tsx   ★ 핵심
src/components/v2/
  ├─ TagTreePanel.tsx          — 좌 트리
  ├─ DocListPanel.tsx          — 중 리스트/그리드 토글
  ├─ DocPreviewPanel.tsx       — 우 프리뷰
  ├─ PdfThumbnail.tsx          — T4 하이브리드 썸네일 (IntersectionObserver 지연)
  ├─ DrawingsListV2.tsx        — (검색 전용, redirect 이후 미사용)
  ├─ MetadataPanelV2.tsx       — 도면 상세 헤더
  ├─ PdfViewerV2.tsx           — TextLayer=true 뷰어
  ├─ FoundationScoreCard.tsx   — 18행 Layer A/C 체크
  └─ DocCard.tsx               — 공용 카드
src/lib/foundation/
  ├─ useRecentDocs.ts          — LRU 20
  └─ useFavorites.ts           — 토글
src/lib/highlight.ts            — splitHighlight
```

### 1.4 공용 수정 사항 (최소)

| 파일 | 변경 | 이유 |
|---|---|---|
| `data/drawings.json` | doc-001~008에 drawing_number·revision·location, dwg-* location 추가 (26건 전체 완비) | F-004 메타 채움 |
| `src/lib/data-loader.ts` | `tagsForDoc`, `tagLinkCounts` export 추가 | 정방향 네비·트리 카운트 |
| `src/lib/nav.ts` | foundation 그룹 6항목 | SideNav |
| `src/components/shell/SideNav.tsx` | foundation 섹션 렌더 | SideNav |

### 1.5 보존 원칙 (여전히 불변)
- **보존 6항목** (PdfViewer pickMode·key / AnnotationLayer pointer-events / AnnotationPopover Escape / annotations-store hydrated / data-loader toUpperCase / TransformWrapper doubleClick)
- `src/app/(s1)/**` 전체 수정 금지
- `src/app/(s2)/insight/**` 전체 수정 금지 (`llm-client.ts` 타입 에러도 손대지 않음)
- `src/components/PdfViewer.tsx`·`AnnotationLayer.tsx`·`AnnotationPopover.tsx`·`annotations-store.ts` 미수정

---

## 2. 연속 조사·설계 문서 (01~10)

| # | 파일 | 핵심 |
|:-:|---|---|
| 01 | `01-saas-search-fundamentals.md` | 일반 검색 SaaS 6블록 + 평가 5축 |
| 02 | `02-drawing-specialized-patterns.md` | 도면 4패턴 (C2S/S2H/영향도/HUD) |
| 03 | `03-technical-options.md` | SVG/BBox/Vision 3옵션 |
| 04 | `04-decisions-for-this-project.md` | 초기 3결정 포인트 |
| 05 | `05-critical-evaluation.md` | 4렌즈 비판 평가 |
| 06 | `06-fundamentals-and-innovation.md` | Layer A/B/C/D 수직 계층 |
| 07 | `07-actual-code-verification.md` | 코드 실제 검증 → Layer A/C 86% |
| 08 | `08-foundation-implementation.md` | 6개 갭 해소 — Layer A/C 100% |
| 09 | `09-menu-architecture-redesign.md` | **실책 인정**: Layer vs IA 혼동, 메뉴 7개 추가 |
| 10 | `10-note-ux-redesign.md` | **PDF 중심 재해석**, StarNote DNA 7개, `/foundation/notebook` 구현 |

---

## 3. 다음 세션 탐구 주제 — StarNote 세부 조사 + 현장 관점

### 3.1 현재까지 반영된 StarNote DNA 7개 (10번 §7.5)
- PDF = 1급 시민
- 썸네일 라이브러리
- 분할 뷰
- PDF 내 + 전체 검색 통합 (부분)
- 주석 오버레이 분리
- 리스트 ↔ 그리드 토글
- 메타 다축 필터/정렬

### 3.2 아직 조사·반영 안 된 StarNote **세부 편의 기능** (조사 필요)

| 그룹 | 후보 기능 |
|---|---|
| 필기·주석 | 펜 종류(만년필·형광펜·볼펜·붓), 압력 감응, 라쏘 선택·복붙·이동, 지우개 모드, 레이어 분리, 스티커·스탬프, 이미지 삽입 |
| 페이지 관리 | 페이지 썸네일 사이드바, 드래그 재배열, 페이지 복제·삭제·병합, 무지/격자/줄/도트 배경, 오픈북 2페이지 뷰 |
| 검색·OCR | 손글씨 텍스트 인식, 한자·외국어 검색, 선택 텍스트 복사, 인용 붙여넣기 |
| 동기화·공유 | 오프라인 저장, 클라우드 싱크, 읽기 링크 공유, 내보내기(PDF/이미지/텍스트) |
| 책갈피·북마크 | 별표·플래그, 카테고리별 색 태그, 최근 읽음 자동 저장 |
| 오디오 | 녹음 + 필기 동기화(특정 순간 탭→재생 위치 이동) |
| 수식·다이어그램 | LaTeX 입력, 도형·연결선 그리기, 자 모드, 스냅 |
| 성능·터치 | 저지연(<20ms) 필기, 손바닥 무시(palm rejection), 제스처(2손가락 뒤로가기·3손가락 선택) |
| 다중 문서 | 노트 2개 동시(split), 탭·창 관리, 두 문서 간 드래그앤드롭 |

→ **다음 세션에서 할 것**: 위 그룹별로 StarNote 실제 UI를 Play Store·App Store·공식 사이트·리뷰에서 심층 조사하여 **"현장 도면에 의미 있는 것"**으로 선별.

### 3.3 현장에서 도면을 보는 맥락 (사용자 지적)

> *"도면을 현장에서 좀 더 많이 보기 때문에 웹을 설계할 때에도 좀 더 참고할 필요가 있을거 같아"*

현장 맥락 공통 제약 (벤치마크: Autodesk Fieldwire, Procore Mobile, Bluebeam Revu iPad, PlanGrid):
- **오프라인**: 현장은 통신 불안정 → 캐시·PWA·오프라인 저장
- **큰 tap target**: 장갑·안전모 환경. 최소 44×44pt
- **햇빛 가독성**: 고대비, 다크 모드, 외광 자동 보정
- **저지연 터치**: 드래그·줌·핀치 지연 < 100ms
- **화면 회전**: 가로·세로 모두 지원
- **원손 사용 최적화**: 안전장갑 낀 상태 한 손 조작
- **QR/NFC로 해당 도면 즉시 열기**: 현장 설비 스티커 스캔
- **음성 메모**: 손 바쁠 때
- **빠른 주석**: 한 번 탭으로 기본 마커 찍기
- **큰 폰트 옵션**: 햇빛 아래 소형 텍스트 가독 저하 대응
- **간섭 없는 배경**: 도면 가독 우선, HUD 최소화
- **위치/사진 첨부**: 현장 위치 메타+카메라 연동

→ **다음 세션에서 할 것**: StarNote 세부 + 현장 제약 교집합에서 **"웹 `/foundation/notebook` + `/foundation/drawings/[id]`에 도입할 5~8개 편의 기능"**을 선별하고 설계.

### 3.4 다음 세션 권장 작업 흐름

1. **§3.2 그룹별 StarNote 심층 조사** (WebSearch + WebFetch, 1~2h)
   - 앱스토어 리뷰, Play Store 스크린샷, 공식 기능 페이지
   - 가능하면 LiquidText·MarginNote·Notability 비교 보조
2. **§3.3 현장 앱 벤치마크** (Fieldwire·Procore Mobile·Bluebeam iPad)
3. **§3.2 ∩ §3.3 교집합 선별표** 작성 (30~40개 후보 → 5~8개 도입 후보)
4. 사용자 확정 후 구현 (컴포넌트·훅 단위로 Foundation 트랙에 추가, 보존 원칙 유지)
5. Chrome 검증 + 스크린샷 + 12번 문서 작성

---

## 4. 데이터·실행 정보

### 4.1 데이터 실태
- `data/drawings.json` 26건 (doc-001~008 + dwg-* 15건 + LSE-*) — 메타 전체 완비
- `data/doc-entity-links.json` 58건 / 태그 50종 / 도면당 평균 2.2건
- `data/annotations.json` 빈 배열 (시드) + localStorage key `mvp-annotations-v1`
- localStorage 신규 2개: `foundation-recent-docs-v1`, `foundation-favorites-v1`

### 4.2 실 PDF 5~8건만 유효
- doc-001~008 중 `real/*.pdf` (elec-sld·elec·mech·fire-mech·fire-elec·arch) → 텍스트 있음
- `dwg-*.pdf`는 대부분 **0 byte 더미**. TextLayer 활성해도 글자 없음
- 현재 뷰어는 이미지 fallback 규칙(`PdfViewer.pickMode` / `PdfViewerV2` 동일) 으로 그림 있는 것은 표시

### 4.3 실행
```bash
cd D:\_Project\prototype-도면지식관리-mvp
npm run dev           # Next.js 14, 기본 3000, 충돌 시 3001/3002 자동
# 현 세션은 localhost:3002에서 실행 중 (세션 종료 시 사용자 수동 종료 권장)
# npm run build       # Insight Lab llm-client.ts 기존 타입 에러로 실패 (내 작업 무관)
```

### 4.4 스크린샷 아카이브
`docs/search-saas-study/screenshots/` 에 `01-foundation-home.png` ~ `23-notebook-search-redirect.png` 저장.

---

## 5. 열려 있는 의사결정 (이월)

| 항목 | 현 상태 | 비고 |
|---|---|---|
| **StarNote 세부 편의 기능 도입** | 조사·선별 예정 | **다음 세션 메인 의제** |
| 현장 맥락(오프라인·터치·햇빛) 반영 | 미시작 | §3.3 |
| 개정 이력·업데이트 피드·업로드 mock·활용 리포트 4메뉴 | 이전 세션에서 제외, 보류 | 재개 여부 미정 |
| Layer D 혁신 트랙 (Click-to-Search / 2-hop 그래프 / 포지셔닝) | 별도 트랙 | 기본 충실 완료 후 결정 |
| 페르소나 재검증 (이전 8인 중 2~3인) | 미시작 | Foundation 트랙을 시연 자산으로 |
| (s2) Insight Lab `llm-client.ts` 타입 에러 | 내 작업 무관 | 별도 소유자 |
| W4-T2 통합 회귀 | 대기 | 상위 plan `rippling-frolicking-lynx.md` |

---

## 6. 참조 경로 (절대경로)

### 핵심 진입
- **CLAUDE.md** (세션 진입점): `D:\_Project\prototype-도면지식관리-mvp\CLAUDE.md`
- **이 핸드오프 문서**: `D:\_Project\prototype-도면지식관리-mvp\docs\search-saas-study\11-next-session-handoff.md`
- **검색 SaaS 스터디 지도**: `D:\_Project\prototype-도면지식관리-mvp\docs\search-saas-study\README.md`

### 4주 업그레이드 (S1 트랙)
- 작업 트래커: `D:\_Project\prototype-도면지식관리-mvp\docs\upgrade-plan\STATUS.md`
- 결정사항: `D:\_Project\prototype-도면지식관리-mvp\docs\upgrade-plan\00-decisions.md`
- 상위 plan: `C:\Users\cruel\.claude\plans\rippling-frolicking-lynx.md`

### Foundation 트랙 (S3) 플랜
- `C:\Users\cruel\.claude\plans\moonlit-gliding-beacon.md` — 최초 Plan (2026-04-21)

### Insight Lab (S2) 문서
- `D:\_Project\prototype-도면지식관리-mvp\docs\insight-mockup\README.md`

### Baseline
- `D:\_Project\prototype-도면지식관리-mvp\docs\baseline-mvp\README.md`

### 스펙 원본
- `docs-표준레이어/07-서비스1-도면관리-상세설계.md` §14 (MVP 범위)
- `docs-표준레이어/08-서비스2-AI인사이트-상세설계.md` §15

---

## 7. 요약 (한 단락)

현재 `(s1)` Layer 0 MVP·`(s2)` Insight Lab과 병렬로 **`(s3)/foundation/` "기본 충실 트랙"**이 구축됐다. Layer A/C 18요건 100% 충족 + 메뉴 IA 7개 + **PDF 중심 StarNote DNA 7개(3열·리스트/그리드·T4 썸네일·태그 트리·프리뷰·즐겨찾기·최근본)를 `/foundation/notebook`에 반영**했다. 기존 `(s1)`·`(s2)`는 무영향, 보존 6항목 불변. 다음 세션은 **StarNote 세부 편의 기능 심층 조사 + 현장 도면 사용 맥락을 교차해 5~8개 도입 후보를 선별·구현**하는 것이 메인 의제다.
