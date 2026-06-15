# 08 · Foundation 트랙 구현 보고

> **작성 시점**: 2026-04-21
> **구현 트랙**: 06의 "기본 충실화" + 07의 "잔여 갭 6개 해소"를 신규 `(s3)/foundation/` 메뉴로 구현
> **승인된 플랜**: `C:\Users\cruel\.claude\plans\moonlit-gliding-beacon.md`

---

## 1. 구현 요약

| 영역 | 내용 |
|---|---|
| 신규 라우트 | `(s3)/foundation/` 3페이지 (홈·검색·도면 상세) |
| 신규 컴포넌트 | `src/components/v2/` 4개 (DrawingsListV2·MetadataPanelV2·PdfViewerV2·FoundationScoreCard) |
| 신규 유틸 | `src/lib/highlight.ts` |
| 네비게이션 | SideNav에 "기본 충실" 섹션 추가, NAV_ITEMS에 2항목 |
| 데이터 | `data/drawings.json` 전 23건에 `drawing_number·revision·location` 완비 |
| 기존 파일 수정 | `nav.ts` / `SideNav.tsx` / `data-loader.ts` (export 1개 추가) / `drawings.json` |
| 보존 6항목 | **수정 0** (PdfViewer·AnnotationLayer·AnnotationPopover·annotations-store·data-loader toUpperCase·TransformWrapper doubleClick) |
| `(s1)` 라우트·컴포넌트 | **수정 0** |
| `(s2)/insight/*` | **수정 0** |

## 2. 6개 갭별 해소

| # | 갭 | 해소 방식 | 증빙 |
|---|---|---|---|
| A.4 | 정렬 없음 | `DrawingsListV2`에 셀렉트 3종 (관련도·최근수정·도면번호), URL `?sort=` 파라미터 동기화 | `SearchContent.tsx` L12·L46-53 |
| A.10 | 스니펫 하이라이트 없음 | `splitHighlight()` 유틸 + `<mark>` 태그 렌더 | `highlight.ts` + `DrawingsListV2.tsx` L41-56 |
| C4 | 도면 내 텍스트 검색 비활성 | `PdfViewerV2`에서 `renderTextLayer={true}` + Ctrl+F 안내 배너 | `PdfViewerV2.tsx` L183 |
| C6 | 양방향 네비 없음 | `MetadataPanelV2` 하단에 "연결 설비" 칩, 클릭 시 `/foundation/search?q=TAG` 이동 | `MetadataPanelV2.tsx` L42-58 |
| F-004 | 메타 데이터 채움 부족 | doc-001~008에 drawing_number·revision·location, dwg-\*에 location 추가 → 전 23건 완비 | `data/drawings.json` 전체 |
| 품질축 | 30초 룰·근거 미시각화 | 응답시간 `performance.now()` + 카드 하단 "근거: doc-NNN · p.N" 라인 | `SearchContent.tsx` L37-58, `DrawingsListV2.tsx` L176-180 |

## 3. 스코어카드 결과 (실제 렌더링)

`/foundation` 랜딩에서 자동 계산:

| 구분 | 기존 `/` | `/foundation` | 개선 |
|---|:---:|:---:|:---:|
| Layer A 11요건 | 9 met + 2 weak | **11 met** | +2 |
| Layer C 7요건 | 5 met + 1 weak + 1 miss | **7 met** | +2 |
| 총합 18행 | ~86% | **100%** | +14%p |

## 4. 검증 결과 (`npm run dev`)

| URL | HTTP | 핵심 콘텐츠 |
|---|:---:|---|
| `/` (기존 홈) | 200 | 회귀 없음 |
| `/search?q=냉동기` (기존 검색) | 200 | 회귀 없음 |
| `/foundation` | 200 | "기본 충실", "Foundation", "Layer A/C", "스코어카드" 렌더 |
| `/foundation/search?q=냉동기` | 200 | `<mark class="rounded-sm bg-yellow-200 ...">냉동기</mark>` 다수 |
| `/foundation/drawings/dwg-elec-001` | 200 | "연결 설비" + "VCB-001" + "KEPCO-IN" + "U#T동" 렌더 |
| `/foundation/drawings/doc-001` | 200 | 메타 완비 (EE-00-001 · R1 · BESS동 1F 전기실) |

SideNav 검증: `/` 페이지에 "기본 충실" 레이블, "기본 홈", "기본 검색" 항목 렌더 확인.

## 5. 알려진 기존 이슈 (내 작업과 무관)

`npm run build` 실행 시 `src/lib/insight/llm-client.ts:39, 68`에서 타입 에러:
```
Type 'null' is not assignable to type '{ confidence: number; ... } | undefined'.
```
- 이 파일은 `(s2)/insight/*` 트랙 소속이며 내 변경 범위 밖
- Grep 확인: 내 신규 파일 어디에도 `llm-client` 또는 `structured: null` 참조 없음
- **기존부터 존재하던 타입 에러**로 추정. 고치려면 1~2줄이지만 `(s2) 무영향` 원칙에 따라 손대지 않음
- dev 모드에서는 전 페이지 200 응답, 런타임 정상

## 6. 평가 관점

### 이 트랙이 성공했다고 말할 수 있는 기준
1. ✅ 스코어카드 18행이 전부 ✅(met)으로 표시됨 (랜딩 페이지에서 수치 비교)
2. ✅ `/foundation/search`가 `<mark>` + 정렬 + 응답시간 + 근거 4장치 모두 작동
3. ✅ `/foundation/drawings/*`가 Ctrl+F + 연결 설비 칩 양방향 네비 작동
4. ✅ 기존 `/`·`/search`·`/drawings/[id]` 회귀 없음
5. ✅ (s2)/insight/* 무영향

### 이 트랙이 답하지 못하는 것 (05 비판 평가 일관성)
- "기본 충족률 100%가 페르소나 지불 의사로 이어지는가" — 별도 재검증 필요
- "이것이 혁신인가" — 아님. 이것은 기본 충실화이지 혁신 트랙이 아님 (06 §Layer D에서 분리)
- 기술적 새로움 0 — 모든 장치는 react-pdf·Next.js·Tailwind의 기본 조합

### 시연 시 권장 서사
> "기존 `/` 트랙은 Layer A/C 기본을 86% 충족하고 있었습니다. 잔여 14%의 구멍을 닫은 것이 `/foundation` 트랙입니다. 이것은 혁신이 아닌 **정공법의 완결**입니다. 혁신 논의는 이 기반 위에서 별도 트랙으로 다룹니다."

## 7. 이후 결정 재정리 (07 갈래 갱신)

| 갈래 | 06 원안 | 08 이후 |
|---|---|---|
| ① Layer C 보강 | C4·C7·메타 채움 | **완료** (foundation 트랙으로 해소) |
| ② Layer D 혁신 | 신규 `/concept/` 또는 `/drawings/[id]?mode=concept` | 여전히 열려 있는 갈래. I1(Click-to-Search)·I3(2-hop)·I5(포지셔닝) 중 선택 |
| ③ 페르소나 재검증 | W4-T2 + 이전 8인 중 2~3인 재시연 | 이제 `/foundation` 트랙을 시연 자산으로 활용 가능 |

**다음 의사결정**: ②를 착수할지 (혁신 트랙), ③을 먼저 할지 (재검증), 아니면 이대로 MVP로 고정할지.

## 8. 변경된 파일 목록 (최종)

### 신규 (12)
- `src/app/(s3)/foundation/layout.tsx`
- `src/app/(s3)/foundation/page.tsx`
- `src/app/(s3)/foundation/search/page.tsx`
- `src/app/(s3)/foundation/search/SearchContent.tsx`
- `src/app/(s3)/foundation/drawings/[id]/page.tsx`
- `src/app/(s3)/foundation/drawings/[id]/DrawingContent.tsx`
- `src/components/v2/DrawingsListV2.tsx`
- `src/components/v2/MetadataPanelV2.tsx`
- `src/components/v2/PdfViewerV2.tsx`
- `src/components/v2/FoundationScoreCard.tsx`
- `src/lib/highlight.ts`
- `docs/search-saas-study/08-foundation-implementation.md` (이 문서)

### 수정 (4, 최소)
- `data/drawings.json` — 23건 메타 채움 (optional 필드 값만 추가, 스키마 무변경)
- `src/lib/data-loader.ts` — `tagsForDoc(doc_id)` export 1개 추가, 기존 export 무수정
- `src/lib/nav.ts` — `group` 타입에 `'foundation'` 추가, NAV_ITEMS에 2항목
- `src/components/shell/SideNav.tsx` — 새 섹션 렌더 블록 10줄

### 보존 (미수정)
- 보존 6항목 전체 / `(s1)/**` 전체 / `(s2)/insight/**` 전체 / 공용 shell (Header·AppShell·Breadcrumb·MobileTabBar·useBreakpoint) / 기존 컴포넌트 (MetadataPanel·DrawingsList·SearchBar·PdfViewer·AnnotationLayer·AnnotationPopover·HighlightOverlay·EntityToDocs·AnnotationList)
