# 07 · 실제 코드 검증 — 06 판정 정정

> **이 문서의 역할**: 06 §Layer A/C 판정은 `src/app/(s1)/page.tsx` 하나만 보고 내린 추정이었다. 사용자 지적에 따라 `(s1)` 전 파일을 읽어 **코드 레벨로 재검증**한 결과를 기록. 인사이트/알람 `(s2)`는 검증에서 제외.
>
> **작성 시점**: 2026-04-21
> **검증 범위**: 홈(`/`), 검색(`/search`), 도면 상세(`/drawings/[id]`) + 공유 컴포넌트·lib

---

## 1. 검증한 파일 (17개)

| 분류 | 파일 | 주요 역할 |
|---|---|---|
| 라우트 | `src/app/layout.tsx` | 루트 html/body |
| 라우트 | `src/app/(s1)/layout.tsx` | `<AppShell>`로 감쌈 |
| 라우트 | `src/app/(s1)/page.tsx` | 홈: 좌 검색·리스트 / 중앙 뷰어 / 우 탭 |
| 라우트 | `src/app/(s1)/search/page.tsx` | Suspense 래퍼 |
| 라우트 | `src/app/(s1)/search/SearchContent.tsx` | **URL 파라미터 기반 검색** (q·discipline·type) |
| 라우트 | `src/app/(s1)/drawings/[id]/page.tsx` | Suspense 래퍼 |
| 라우트 | `src/app/(s1)/drawings/[id]/DrawingContent.tsx` | **도면 상세 + Breadcrumb + MetadataPanel + HighlightOverlay + Mobile 탭** |
| 쉘 | `src/components/shell/AppShell.tsx` | Header + SideNav + main |
| 쉘 | `src/components/shell/Header.tsx` | 로고, 글로벌 검색 플레이스홀더, 알림 벨, 프로필 |
| 쉘 | `src/components/shell/SideNav.tsx` | NAV_ITEMS 기반 도면관리/인사이트/common 그룹 |
| 컴포넌트 | `src/components/SearchBar.tsx` | 입력 아이콘·placeholder·focus 링 |
| 컴포넌트 | `src/components/DrawingsList.tsx` | 학제·종류 칩, 빈상태, 결과 카드 |
| 컴포넌트 | `src/components/PdfViewer.tsx` | **PDF/이미지 분기, 줌, 페이지, 원본 PDF 링크, 오류 카피** |
| 컴포넌트 | `src/components/EntityToDocs.tsx` | 태그→도면 역추적 + 자동완성·빈상태 |
| 컴포넌트 | `src/components/AnnotationList.tsx` | 주석 그룹·검색·빈상태 |
| 컴포넌트 | `src/components/HighlightOverlay.tsx` | **URL highlight 파라미터 → 상단 배너** |
| 컴포넌트 | `src/components/MetadataPanel.tsx` | **도면번호·분야·종류·Rev·위치·최종수정** |
| lib | `src/lib/search.ts` | Fuse (title·snippet·discipline·type·**disciplineKo·drawing_number·location** 가중치) |
| lib | `src/lib/data-loader.ts` | **disciplineKo 파생 필드 주입** |
| lib | `src/lib/types.ts` | **drawing_number·drawing_type·location·revision·download_enabled 필드 존재** |
| lib | `src/lib/nav.ts` | 홈·검색 + 업로드(disabled) + 인사이트 그룹 |

---

## 2. Layer A 11요건 실제 재판정

> 06 §A.5의 판정을 코드와 대조하여 수정한 결과. **06에서 실제보다 박하게 매긴 항목에 ◎를 달고 근거 라인 번호를 표시.**

| # | 요건 | 06 판정 | 07 재판정 | 근거 코드 |
|---|---|:---:|:---:|---|
| 1 | 입력창 | ✅ | ✅ | `SearchBar.tsx` 전체 |
| 2 | 결과 리스트 | ✅ | ✅ | `DrawingsList.tsx` L94-135 |
| 3 | 개별 상세 | ✅ | ✅ | `DrawingContent.tsx` 전체 |
| 4 | 필터·정렬 | △ | △ | 칩 필터는 `DrawingsList.tsx` L51-92 / 정렬 기능 없음 |
| 5 | 출처 표시 | △ | **✅ ◎** | `PdfViewer.tsx` L94-103 **"원본 PDF" 외부 링크** + `MetadataPanel.tsx`(도면번호·Rev·위치) |
| 6 | 체감 지연 | ✅ | ✅ | 로컬 JSON + Fuse |
| 7 | 빈 상태 | ✅ | ✅ | `DrawingsList.tsx` L95-98, `AnnotationList.tsx` L63-68, `EntityToDocs.tsx` L74-81, `PdfViewer.tsx` L108-114 |
| 8 | 오류 상태 | ❌ | **✅ ◎** | `PdfViewer.tsx` L176-180 "PDF를 읽을 수 없습니다" + `DrawingContent.tsx` L60-73 "도면 ID 찾을 수 없음" + 뒤로 버튼 |
| 9 | 정답 우선 노출 | △ | **✅ ◎** | `search.ts` L5-18 Fuse `includeScore:true` + 필드별 weight 튜닝 (title 0.5 / snippet 0.3 / drawing_number 0.2 / disciplineKo 0.15…) |
| 10 | 매칭 근거 | △ | △ | 스니펫 2줄 노출(`DrawingsList.tsx` L120-122) / 키워드 하이라이트는 없음 |
| 11 | 다음 행동 연결 | ❌ | **✅ ◎** | `DrawingContent.tsx` L41-45 `highlight`/`from`/`query_id`/`alarm_id` 쿼리 파라미터 수용 + `Breadcrumb` 복귀 + `EntityToDocs.onOpenDoc` → `/drawings/[id]?page=N` |

### 2.1 Layer A 종합 재판정

| 판정 | 06 | 07 | 변경 |
|---|:---:|:---:|---|
| ✅ 충족 | 6 | **9** | +3 |
| △ 약함 | 3 | 2 | -1 |
| ❌ 결손 | 2 | **0** | -2 |

**결론**: **Layer A는 사실상 결손 없이 모두 충족**. 약한 2개(정렬·키워드 하이라이트)도 품질 개선 범위이지 "있어야 할 게 없다" 수준이 아님.

---

## 3. Layer C 7요건 실제 재판정

| # | 요건 | 06 판정 | 07 재판정 | 근거 코드 |
|---|---|:---:|:---:|---|
| C1 | 도면 검색·리스트 | ✅ | ✅ | 홈 + `/search` 두 곳. URL 파라미터로 상태 공유 (`SearchContent.tsx` L15-30) |
| C2 | 도면 뷰어 | ✅ | ✅ | `PdfViewer.tsx` 전체 (PDF/이미지 분기·줌·페이지) |
| C3 | 도면 메타 | △ | **✅ ◎** | `MetadataPanel.tsx` L15-22 도면번호·분야·종류·Rev·위치·최종수정 **UI 이미 존재**. 값이 undefined면 `filter(Boolean)`로 숨김. **타입(types.ts L20-24)과 렌더 모두 완비**. *값이 비어있다는 현재 데이터 상태는 기능 결손이 아니라 데이터 입력 이슈* |
| C4 | 도면 내 텍스트 검색 | ❌ | ❌ | `PdfViewer.tsx` L193-194 **`renderTextLayer={false}` 의도적 비활성**. react-pdf 기본 제공되지만 껐음. **유일한 명백 결손** |
| C5 | 도면 간 이동 | △ | **✅ ◎** | `EntityToDocs.onOpenDoc` L86-88 → `/drawings/[id]?page=N` / `DrawingContent.tsx` L152 `Breadcrumb` 컨텍스트 복귀 / 콜아웃 자동 하이퍼링크는 없음 |
| C6 | 객체 메타(최소) | △ | △ | `doc-entity-links.json` 1-hop만. 객체 속성 DB 없음 |
| C7 | 원본 접근 | ❌ | **✅ ◎** | `PdfViewer.tsx` L94-103 `<a href={pdfUrl} target="_blank">원본 PDF</a>` **이미 존재** |

### 3.1 Layer C 종합 재판정

| 판정 | 06 | 07 | 변경 |
|---|:---:|:---:|---|
| ✅ 충족 | 5 | **5+1 ◎ = 6** (C7 승격까지 포함 시 6) | 실제로는 C7 승격이므로 **충족 5→6** |
| △ 약함 | 4 | **1** (C6만) | -3 |
| ❌ 결손 | 2 | **1** (C4만) | -1 |

**결론**: **Layer C의 유일한 명백 결손은 C4(도면 내 텍스트 검색)**. 나머지 06이 "약함"으로 매긴 C3·C5는 **UI까지 이미 구현**된 상태로 06이 틀렸음. C6(객체 메타)만 진짜 약함.

---

## 4. 06에서 간과한 "이미 있는 Layer D 기반"

이 부분이 가장 큰 발견. 06은 Layer D를 "앞으로 해야 할 혁신"으로 분류했지만, **코드에는 이미 일부 골격이 있다**.

### 4.1 I2 (Search-to-Highlight) — 골격 30% 존재

- **URL 계약**: `/drawings/[id]?highlight=CH-001`가 이미 정의됨 (`DrawingContent.tsx` L42)
- **렌더 컴포넌트**: `HighlightOverlay` 존재. 다만 현재 렌더 내용은 상단 배너 "🔍 CH-001 강조 중"이 전부 (`HighlightOverlay.tsx` L8-14)
- **갭**: 실제로 도면 위 해당 설비에 **색상·링·펄스** 하이라이트는 안 됨. 좌표 매핑 데이터(hotspots)가 없어서.

### 4.2 I4 (Cross-track Asset Timeline) — 진입 축 존재

- `DrawingContent.tsx` L42-45가 `from`, `query_id`, `alarm_id`를 모두 쿼리로 받음
- `Breadcrumb` 컴포넌트가 복귀 경로 제공
- **갭**: Insight/Alarm 트랙에서 도면으로 들어올 때의 "연관 스토리(타임라인)" 자체는 아직 없음. 하지만 **딥링크 계약은 이미 설치됨**

### 4.3 I5 (현장 포지셔닝) — 모바일 기반 존재

- `AppShell.tsx` L20-41 모바일 드로어 네비
- `DrawingContent.tsx` L156-167 `MobileTabBar` + `useBreakpoint` sm에서 viewer/side 탭 전환
- `Header.tsx` L15-27 햄버거 버튼
- **갭**: 태블릿·폰 실기기 검증, 오프라인, QR 등은 없음. 하지만 **375px 반응형 골격은 완비**

### 4.4 글로벌 검색·알림 축

- `Header.tsx` L36-41 데스크톱 **글로벌 검색 플레이스홀더** (시각만, 기능은 없음)
- L43-53 **알림 벨 + 비판적 알람 뱃지** — 인사이트 트랙의 criticalAlarms 연동
- **갭**: 글로벌 검색은 UI만 있고 동작 없음. 알림은 읽기만.

### 4.5 URL-공유 가능한 검색 상태

- `SearchContent.tsx`는 **검색 상태를 URL 파라미터로 싱크**. 링크 공유 시 그대로 재현 가능.
- **홈의 인라인 검색은 React state**, **/search는 URL state**. 두 방식 병존. — 이 이원화는 의도적이며 06에선 언급 안 했음.

---

## 5. 06에서 잘못 판정한 5건 (정정표)

| # | 06 진술 | 실제 코드 | 정정 |
|---|---|---|---|
| 1 | "A.8 오류 상태 미구현" | PdfViewer·DrawingContent 모두 오류 카피 + 복구 액션 | **결손 아님** |
| 2 | "A.11 다음 행동 연결 없음" | `?highlight=&from=&query_id=`, Breadcrumb, EntityToDocs 링크 | **이미 상당 수준 구현** |
| 3 | "C3 약함(필드 타입만 있고 값 미채움)" | MetadataPanel 실제 렌더 존재. 데이터가 비어있을 뿐 | **기능 충족, 데이터만 부족** |
| 4 | "C5 약함(콜아웃 하이퍼링크 없음)" | EntityToDocs 역추적 + 딥링크 복귀 완비 (콜아웃만 없음) | **충족 수준** |
| 5 | "C7 결손(다운로드 없음)" | 헤더 우상단에 "원본 PDF" 외부 링크 | **완전히 틀림** |

**원인**: 06은 `(s1)/page.tsx` 단일 파일만 읽고 판정했다. 그러나 실제로는 `/search`, `/drawings/[id]`, `MetadataPanel`, `HighlightOverlay`, `Breadcrumb`, `AppShell/Header/SideNav`, `types.ts`, `search.ts`의 개선이 모두 W2~W3 업그레이드 중 이미 들어가 있었음.

---

## 6. 수정된 결론

### 6.1 Layer A·C 실제 완성도

| Layer | 결손 | 약함 | 충족 | 완성도 |
|---|:---:|:---:|:---:|:---:|
| A (일반 검색 11) | 0 | 2 (정렬·하이라이트) | 9 | **82% + 품질축** |
| C (도면 기본 7) | 1 (C4 텍스트 검색) | 1 (C6 객체 메타) | 5+1=6 | **86%** |

**→ 이전 프로토타입의 페르소나 2.3/10은 Layer A·C의 결손이 아니라 다른 축(설득 서사·현장 밀착도·온톨로지)의 문제일 가능성이 크다.** 기본 기능은 이미 충족되어 있기 때문.

### 6.2 "진짜 남은 결손"은 매우 작다

- **C4 도면 내 텍스트 검색**: `PdfViewer.tsx` L193-194의 `renderTextLayer={false}`를 `true`로 바꾸고 pdf.js find controller를 붙이면 됨. **반나절 작업**.
- **A.4 정렬**: `DrawingsList`에 정렬 셀렉트 1개 추가. **한두 시간**.
- **A.10 키워드 하이라이트**: `DrawingsList`의 스니펫에 `<mark>` 렌더. **한 시간**.

### 6.3 "이미 있는 D 기반"을 활용한 신규 트랙 재설계

06이 권장한 "`(s3)/concept/` 신설"은 과한 방향 전환이었음. **기존 `/drawings/[id]`를 확장**하는 쪽이 자연스럽다.

| 06 권장 (신규 `(s3)/concept/`) | 07 수정 권장 (기존 확장) |
|---|---|
| 별도 라우트 생성 | `/drawings/[id]?mode=concept` 토글 도입 |
| `HotspotLayer` 신규 작성 | 기존 `renderOverlay` 슬롯에 `HotspotLayer`를 **AnnotationLayer와 병렬**로 끼움 |
| `HUDPanel` 신규 | MetadataPanel 위에 glass 스타일 HUD 오버레이 추가 |
| `ImpactGraph` 신규 | 기존 사이드 탭에 세 번째 탭 "영향도" 추가 |
| `HighlightOverlay` 무시 | **기존 `HighlightOverlay` 확장** — 배너 → 실제 좌표 기반 링·펄스 |
| 진입 버튼 `(s1)` 사이드바 | 기존 SideNav `NAV_ITEMS`에 "개념 뷰" 항목 하나 또는 `/drawings/[id]` 헤더 토글 |

이 방식은 **보존 6항목을 그대로 유지**하면서, 중복 코드 최소화, 이미 설치된 I2·I4·I5 골격 재활용.

### 6.4 의사결정 3갈래 재제안

| 갈래 | 06 원안 | 07 수정 |
|---|---|---|
| ① Layer C 보강 | C4·C7·C3·C5·C6 | **C4 하나** + A.4 정렬 + A.10 하이라이트 = **1일 미만** |
| ② Layer D 혁신 | 신규 `(s3)/concept/` | **기존 `/drawings/[id]` 확장** — Hotspot + HUD + ImpactGraph. HighlightOverlay를 실제 하이라이트로 완성 |
| ③ 페르소나 재검증 | — | **유효** — 기본이 이미 충족된 상태에서 재검증이 더 의미 있음 |

### 6.5 핵심 메시지 재정립

> **"기본(C)에 구멍이 있어서 페르소나가 거부한 것이 아니다. 기본은 이미 86% 충족이었다. 거부는 기본 위에 쌓인 '서사·포지셔닝·온톨로지 품질'의 문제였을 가능성이 크다."**
>
> 이는 06의 메시지("D 전에 C를 먼저")를 **부정**하는 것이 아니라, **C가 이미 대체로 되어 있으므로 D 중 무엇을 어떻게 얹을지의 판단이 실제 의사결정의 중심**이라는 뜻. C 잔여 결손(C4)은 신규 트랙 여부와 무관하게 메우면 됨.

---

## 7. 다음 작업 제안

1. **C4 해소** (Layer C 완성): `PdfViewer.tsx` L193-194를 `renderTextLayer={true}`로 바꾸고 pdf.js find controller 연결. 반나절.
2. **A 품질 개선** (Layer A 품질축): 정렬 셀렉트 + 스니펫 하이라이트. 반나절.
3. **Layer D 방향 결정**: 06의 "신규 트랙" 대신 **기존 확장**으로 재설계 (§6.3). 결정 후 `/drawings/[id]?mode=concept` 토글 설계 착수.
4. **페르소나 재검증 계획**: W4-T2 완료 시점에 이전 8인 중 2~3인에게 "기본 86% 상태 + D 1~2개 프로토타입" 재시연 인터뷰.

---

## 관련 문서

- 이 검증이 정정하는 원안 → [06-fundamentals-and-innovation.md](./06-fundamentals-and-innovation.md) §C.4, §Layer A 매핑, §D.5
- Layer 계층 정의 자체는 06 유효
- 04의 C/C/C 권장안 → **§6.3 기존 확장** 방식으로 수정 권장
