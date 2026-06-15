# 09 · 메뉴 정보구조(IA) 재설계 — 내 실책 인정과 재구성

> **작성 시점**: 2026-04-21 (Foundation 트랙 구현 직후)
> **트리거**: 사용자 지적 — "홈·검색 두 개로 끝나나? 정보 제공 SaaS로서 기본 메뉴 구조가 너무 부실하지 않나?"

---

## 0. 무엇을 놓쳤나 — 마이크로 요건과 매크로 IA의 혼동

01~08의 조사·구현은 모두 **"한 화면(검색 결과) 안의 요건"**을 다뤘다:

- **Layer A 11요건** = 입력창·결과 리스트·필터·정렬·하이라이트·응답시간·빈상태·오류상태 → **검색 페이지 내부**의 micro-requirement
- **Layer C 7요건** = 도면 검색·뷰어·메타·텍스트검색·간 이동·객체 메타·원본접근 → **도면 관련 기능**의 micro-requirement

그런데 **"정보 제공 SaaS"의 메뉴 구조는 전혀 다른 층위**다:

- **Macro IA (Information Architecture)** = 사이트 전체에 어떤 "페이지·섹션"들이 있어야 사용자가 정보 세계를 탐색·수집·관리할 수 있는가
- 홈·검색·도면상세 **3개**만으로는 "검색 전용 페이지"일 뿐 **"정보 제공 서비스"가 아님**
- 사용자는 항상 검색어를 들고 오지 않는다. 브라우징·북마크·최근본·알림이 없으면 그냥 "검색창 달린 뷰어"

내가 Layer A/C만으로 "86→100%"를 달성했다고 자평한 것은 **IA 층을 완전히 빼먹은 상태에서의 점수**였다. 사용자 지적이 정확하다.

---

## 1. 정보 제공 SaaS의 메뉴 IA — 업계 공통 패턴

여러 선도 제품의 메뉴 구조를 병렬 대조하면 **8~10개의 반복 패턴**이 있다:

### 1.1 벤치마크 테이블

| 메뉴 요소 | Glean | Confluence | Notion | Google Drive | SharePoint |
|---|:---:|:---:|:---:|:---:|:---:|
| Home / Dashboard (개인화 피드) | ◎ | ◎ | ◎ | ○ | ◎ |
| Search (검색) | ◎ | ◎ | ◎ | ◎ | ◎ |
| Library / Browse (카테고리 탐색) | ○ | ◎ | ◎ (Workspace) | ◎ | ◎ |
| Recent (최근 본) | ◎ | ◎ | ◎ | ◎ | ◎ |
| Favorites / Starred (즐겨찾기) | ◎ | ◎ | ◎ | ◎ | ◎ |
| My Stuff (내 주석·내 작성) | ○ | ◎ | ◎ | ◎ | ◎ |
| Activity / Updates (피드·알림) | ◎ | ◎ | ◎ | ○ | ◎ |
| Shared / Team (공유 공간) | ○ | ◎ | ◎ | ◎ | ◎ |
| Upload / Create | — | ◎ | ◎ | ◎ | ◎ |
| Analytics / Reports | ◎ | ◎ | ○ | — | ◎ |
| Settings | ◎ | ◎ | ◎ | ◎ | ◎ |

범례: ◎ 1급 메뉴 · ○ 부분/하위 · — 없음

**가장 강한 공통분모 9개**:
1. Home · 2. Search · 3. Browse · 4. Recent · 5. Favorites · 6. My Stuff · 7. Activity · 8. Upload · 9. Settings

### 1.2 왜 이 9개가 반복되나

정보 제공 SaaS는 사용자가 정보를 **다섯 가지 방식으로 접근**한다는 가정 위에 세워진다:

| 접근 방식 | 대응 메뉴 |
|---|---|
| ① 목적지가 분명 → 쿼리로 직행 | Search |
| ② 무엇이 있는지 몰라서 둘러봄 | Library / Browse |
| ③ 이미 봤던 것으로 돌아감 | Recent |
| ④ 자주 쓰는 것으로 빨리 감 | Favorites |
| ⑤ 새로 올라온 것·변경된 것이 궁금 | Activity / Updates |

추가로 **사용자가 만들고 관리하는 것들**:
- 내가 쓴 메모/주석/마크업 → My Stuff
- 내가 공유한 것·팀과 공유된 것 → Shared
- 내가 올리는 것 → Upload

**홈·검색만 있는 구조는 ①만 지원**. 나머지 ②~⑤를 통째로 놓친 것.

---

## 2. 도면 정보 SaaS의 메뉴 IA 특화 — 업계 벤치마크

Autodesk Construction Cloud, Procore, Bluebeam Studio, Revizto 등의 메뉴 구조:

### 2.1 도면 특화 반복 패턴

| 메뉴 요소 | ACC | Procore | Bluebeam Studio | Revizto |
|---|:---:|:---:|:---:|:---:|
| Project Home (프로젝트 대시보드) | ◎ | ◎ | ○ | ◎ |
| Drawings (도면 라이브러리) | ◎ | ◎ | ◎ (Studio Sessions) | ◎ |
| Sheets / Revisions (개정 이력) | ◎ | ◎ | ○ | ◎ |
| Equipment / Assets (설비 목록) | ◎ | ○ | — | ○ |
| Markups (주석/마크업) | ◎ | ◎ | ◎ | ◎ |
| Issues / RFI (질문·이슈) | ◎ | ◎ | — | ◎ |
| Submittals / Transmittals | ◎ | ◎ | — | — |
| Members / Permissions | ◎ | ◎ | ◎ | ◎ |
| Reports / Insights | ◎ | ◎ | ○ | ◎ |
| Files (도면 외 문서) | ◎ | ◎ | ○ | ○ |

### 2.2 "도면 정보 제공"에서 절대 빠질 수 없는 매크로 메뉴 5개

MVP 스코프에서도 최소한 있어야 하는 도메인 특화 메뉴:
1. **도면 라이브러리** — 학제·층·건물·종류로 브라우징
2. **설비 카탈로그** — 태그 중심 탐색 (EntityToDocs 확장)
3. **개정 이력** — revision/last_updated 기반 시간축
4. **주석 모음** — 전체 주석 관리 (도면 상세 탭이 아니라 독립 섹션)
5. **업데이트 피드** — 최근 수정된 도면 알림

---

## 3. 내 현 구조 진단 — 심각한 IA 결핍

### 3.1 현 (s1) 메뉴
```
도면관리: 홈 · 검색 · 업로드(disabled)
인사이트: 인사이트 · 알람 · 보고서
기본 충실: 기본 홈 · 기본 검색
설정(disabled)
```

### 3.2 IA 요건 대비 매핑

| IA 일반 요건 | (s1) | (s3)/foundation | 상태 |
|---|:---:|:---:|:---:|
| Home | ✅ (검색 홈 겸용) | ✅ (스코어카드 랜딩) | 형식적으로 있음 |
| Search | ✅ | ✅ | — |
| Library / Browse | ❌ | ❌ | **결손** |
| Recent | ❌ | ❌ | **결손** |
| Favorites | ❌ | ❌ | **결손** |
| My Stuff (주석) | △ 사이드 탭 | △ 사이드 탭 | 메뉴 승격 필요 |
| Activity / Updates | ❌ | ❌ | **결손** |
| Upload | ❌ disabled | ❌ | **결손** |

| 도면 특화 요건 | (s1) | (s3)/foundation | 상태 |
|---|:---:|:---:|:---:|
| Drawings Library | △ 검색 리스트 겸용 | △ | 독립 메뉴 없음 |
| Equipment Catalog | △ 사이드 탭 | △ 사이드 탭 | 메뉴 승격 필요 |
| Revisions | ❌ | ❌ | 데이터는 있으나 UI 없음 |
| Markups / Notes | △ 사이드 탭 | △ 사이드 탭 | 위와 동일 |
| Reports / Insights | ✅ (s2) 별도 트랙 | — | 이건 예외 케이스 |

**진단**: 9개 일반 IA 요건 중 **결손 4 + 승격 필요 1**. 도면 특화 5개 중 **독립 없음 4**.

**Layer A/C는 100%지만 IA는 40% 수준**이다.

---

## 4. Foundation 트랙 재구성 제안

### 4.1 목표
Foundation 트랙을 "검색 품질 3페이지"에서 **"정보 제공 SaaS로서 완결된 메뉴 구조"**로 확장. 기존 08에서 만든 홈·검색·도면상세는 유지하되, 주변 메뉴 7~9개를 **"기본 메뉴 구조의 일부"**로 함께 신설.

### 4.2 제안 메뉴 11개 (네비게이션 순서)

#### 섹션 A. 일반 정보 제공 축
| # | 라벨 | 경로 | 내용 | 구현 가능도 |
|:-:|---|---|---|:---:|
| 1 | **홈** | `/foundation` | 개인화 대시보드(아래 §4.3 상세) | ◎ |
| 2 | **검색** | `/foundation/search` | 기존 구현 유지 | ◎ |
| 3 | **라이브러리** | `/foundation/library` | 학제·종류·공간 패싯 브라우징 (쿼리 없이) | ◎ |
| 4 | **최근 본** | `/foundation/recent` | localStorage 기반 20개 | ◎ |
| 5 | **즐겨찾기** | `/foundation/favorites` | localStorage 기반 pinned docs | ◎ |
| 6 | **업데이트** | `/foundation/updates` | last_updated 기준 최근 수정 피드 | ◎ |

#### 섹션 B. 도면 도메인 축
| # | 라벨 | 경로 | 내용 | 구현 가능도 |
|:-:|---|---|---|:---:|
| 7 | **설비 카탈로그** | `/foundation/equipment` | 25개 태그 카탈로그 + 각 태그로 drill-down | ◎ |
| 8 | **개정 이력** | `/foundation/revisions` | revision·last_updated 기반 시간축 | ◎ |
| 9 | **내 주석** | `/foundation/notes` | localStorage 전체 주석 통합 관리 (AnnotationList 재활용) | ◎ |

#### 섹션 C. 운영·Placeholder
| # | 라벨 | 경로 | 내용 | 구현 가능도 |
|:-:|---|---|---|:---:|
| 10 | **업로드** | `/foundation/upload` | Mock UI (드래그앤드롭 + 메타 입력 — 실제 저장 없음) | △ mock |
| 11 | **활용 리포트** | `/foundation/reports` | 조회 횟수·많이 본 도면·최근 검색어 (localStorage 추적) | ○ 부분 |

범례: ◎ 전면 동작 · ○ 부분 동작 · △ mock UI

### 4.3 홈 대시보드 위젯 (§4.2의 #1 상세)

기존 08 스코어카드 1개만으로는 "검색 전용 사이트 랜딩"에 머무른다. 진짜 홈은 **위젯 6개**:

1. **최근 본 도면** (localStorage 기반, 상위 5건)
2. **즐겨찾기** (localStorage 기반, 상위 5건)
3. **최근 업데이트** (last_updated DESC, 5건)
4. **설비 태그 빠른 진입** (25개 중 주요 10개)
5. **학제별 도면 수** (막대 or 도넛 — 23건을 ELEC/MECH/FIRE/FACILITY로)
6. **스코어카드** (기존 08 — 하단으로 이동)

### 4.4 localStorage hook 2개 신규

- `useRecentDocs()` — 도면 상세 진입 시 push, 20건 LRU
- `useFavorites()` — 도면 헤더에 "★ 즐겨찾기" 버튼 추가, 토글

이 두 훅을 도면 상세(`DrawingContent.tsx`)에서 side effect로 연동. **기존 (s1) 상세에는 넣지 않음** (foundation 트랙에서만).

---

## 5. 왜 이것이 혁신이 아니고 "기본"인가

명확히 해두자. 이 11개 메뉴는 **Notion·Confluence·SharePoint·ACC·Procore 누구나 가진 것**이다. 이것이 없으면 그냥 "검색창 달린 PDF 뷰어"이지 SaaS가 아니다.

- **혁신 트랙(Layer D)과 구분**: 포지셔닝 혁신 / Click-to-Search / 2-hop 그래프 등은 별도 트랙. 이번은 IA 기본 완성.
- **사용자 지적의 무게**: "기본 메뉴 구조가 너무 부실" → 정확. 07의 "기본 86% 충족"은 화면 내부만 봤던 착시.

---

## 6. 구현 영향 범위

### 6.1 보존·무영향 유지
- (s1)/(s2) 트랙 **여전히 무영향**
- 보존 6항목 **여전히 불변**

### 6.2 Foundation 트랙 확장
- 새 라우트 8개 추가 (library, recent, favorites, updates, equipment, revisions, notes, upload, reports)
- `src/lib/foundation/` 디렉토리에 localStorage 훅 2개 (`useRecentDocs`·`useFavorites`)
- `(s3)/foundation/page.tsx` 랜딩을 6개 위젯으로 재구성 (기존 스코어카드는 유지)
- `nav.ts`·`SideNav.tsx` 메뉴 항목 9개 추가

### 6.3 작업량 추정 (업데이트)

| 섹션 | 소요 |
|---|---|
| 라이브러리 (DrawingsList 패싯 재활용) | 1h |
| 최근 본 + 즐겨찾기 (hook 2 + 페이지 2) | 1.5h |
| 업데이트 피드 | 0.5h |
| 설비 카탈로그 (EntityToDocs 확장) | 1h |
| 개정 이력 | 0.5h |
| 내 주석 (AnnotationList 재활용) | 0.5h |
| 업로드 mock UI | 0.5h |
| 활용 리포트 (localStorage 통계) | 1h |
| 홈 대시보드 위젯 6개 | 2h |
| nav/SideNav 확장 | 0.5h |
| 검증 + 회귀 | 1h |
| **총** | **약 10h (1.5일)** |

---

## 7. 다음 결정 — 사용자 확인 필요

| 질문 | 옵션 |
|---|---|
| 제안 11개 메뉴 전체를 구현? | A. 11개 전부 / B. 핵심 7~8개만 / C. 3~4개 랜덤 / D. 다른 구성 |
| 기존 `(s1)` 메뉴는 그대로? | A. 유지 (기존 3개만) / B. `(s1)`에도 library/recent/favorites 동일 추가 |
| 랜딩(`/foundation`)의 스코어카드는? | A. 홈 위젯 아래로 이동 / B. 별도 `/foundation/scorecard` 분리 / C. 삭제 |

권장안: **11개 전부 / (s1) 그대로 유지 / 스코어카드는 홈 위젯 하단으로**. 이유는 "IA 완결성 시연 + 기존 회귀 방지 + 평가 자산 보존".

---

## 8. 요약

**나의 실책**: Layer A/C(마이크로 요건)를 100% 채우고 "기본 완성"이라고 자평했으나, **매크로 IA** 차원에서는 40% 수준이었다. 정보 제공 SaaS는 홈·검색만으로 성립하지 않는다.

**재구성 방향**: Foundation 트랙에 11개 메뉴를 추가하여 업계 표준 IA를 완성. 기존 (s1)과 격리 유지. 추정 1.5일.

**핵심 메시지**: 이번에도 **"혁신이 아니라 기본"**이다. Glean·Notion·ACC·Procore 누구나 가진 메뉴 구조를 채울 뿐. 이것이 없으면 SaaS가 아니다.

---

## 9. 구현 결과 (2026-04-21)

사용자 선택 "핵심 7개 / (s1) 그대로 유지 / 스코어카드 하단 이동" 기준으로 실제 구현·브라우저 검증 완료.

### 9.1 추가된 메뉴 7개

SideNav "기본 충실" 섹션:

| # | 라벨 | 경로 | 구현 |
|:-:|---|---|---|
| 1 | 홈 | `/foundation` | 대시보드 위젯 6종 (최근 본·즐겨찾기·최근 업데이트·학제별 막대·태그 빠른 진입·스코어카드) |
| 2 | 검색 | `/foundation/search` | 기존 08 유지 (하이라이트·정렬·응답시간·근거) |
| 3 | 라이브러리 | `/foundation/library` | 학제·종류·위치 3축 패싯 + 26개 도면 그리드 |
| 4 | 최근 본 | `/foundation/recent` | localStorage LRU 20건 + 상대시간 표시 + "전체 지우기" |
| 5 | 즐겨찾기 | `/foundation/favorites` | localStorage + 도면 상세 ★ 토글 연동 |
| 6 | 설비 | `/foundation/equipment` | 50종 태그 prefix 그룹핑 + 우측 drill-down + `?highlight=` 딥링크 |
| 7 | 내 주석 | `/foundation/notes` | `AnnotationList` 통합판 (문서별 그룹 + 검색 + 삭제) |

### 9.2 도면 상세 확장

- 헤더에 `← Foundation / 검색 / 라이브러리` 복귀 내비 추가
- **☆ 즐겨찾기 버튼** 추가 (토글, localStorage 자동 반영)
- 진입 시 `useRecentDocs.push()` 자동 호출 → 홈 위젯 즉시 업데이트

### 9.3 신규 파일 (15)

```
src/lib/foundation/useRecentDocs.ts
src/lib/foundation/useFavorites.ts
src/components/v2/DocCard.tsx
src/app/(s3)/foundation/page.tsx                    (기존 랜딩 → 대시보드 재작성)
src/app/(s3)/foundation/library/page.tsx
src/app/(s3)/foundation/recent/page.tsx
src/app/(s3)/foundation/favorites/page.tsx
src/app/(s3)/foundation/equipment/page.tsx
src/app/(s3)/foundation/notes/page.tsx
```

### 9.4 수정 파일 (3)

- `src/lib/nav.ts` — foundation 그룹 항목 5개 추가 (기존 2→7)
- `src/app/(s3)/foundation/drawings/[id]/DrawingContent.tsx` — useRecentDocs + useFavorites 훅 연동, 헤더 확장
- `src/app/(s3)/foundation/search/SearchContent.tsx` — hydration warning fix (`suppressHydrationWarning`)

### 9.5 브라우저 검증 (Chrome)

- 콘솔 에러 **0**
- 확인 경로: `/foundation` → `/foundation/library` → `/foundation/equipment` → VCB-001 drill-down → `/foundation/drawings/dwg-elec-001?highlight=VCB-001` → 즐겨찾기 토글 → `/foundation` (위젯 업데이트 확인) → `/foundation/notes` → `/` (기존 (s1) 회귀 확인)
- 스크린샷: `docs/search-saas-study/screenshots/10~17.png` 8장
- 기존 (s1) **무영향 확인**

### 9.6 핵심 증거

- **localStorage 훅 실작동**: dwg-elec-001 방문 → 즐겨찾기 토글 → 홈 대시보드 리로드 → 양쪽 위젯 모두 즉시 반영
- **TextLayer**: PDF 본문 단어("22.9kV", "VCB", "KEPCO" 등) DOM에 파싱되어 Ctrl+F 가능 상태
- **Equipment drill-down**: VCB-001 클릭 → 연결 도면 2건 노출, 링크에 `?highlight=VCB-001` 자동 주입
- **스코어카드 + 대시보드 공존**: 홈에 6개 위젯 + 하단 스코어카드 18행 표시

### 9.7 남은 한계 (솔직한 평가)

- **업로드·개정이력·활용리포트·업데이트 피드** 4개 메뉴는 사용자 선택에 따라 이번 번들에서 제외. 여전히 정보 제공 SaaS로서 "있으면 더 좋을" 것들.
- **Insight Lab(s2) 빌드 에러** 여전히 존재. 내 작업과 무관. dev 모드에서는 영향 없음.
- 이것은 **혁신이 아니라 IA 기본의 완결**. 혁신 논의(Layer D)는 별도 트랙에서.
