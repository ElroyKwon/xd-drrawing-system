# 07 · 제약 · 트레이드오프 · 미해결

이 문서는 **알면서도 의식적으로 안 한 선택들**과 **아직 결정되지 않은 것들**을 모은다. 자발적 지불 의사 0명이었던 이전 프로토타입을 반면교사 삼아 "덜 만들기"가 가설 검증 속도에 필수적이었다.

## 1. 의식적 제약 (지금은 안 한다)

### 1.1 반응형/모바일
- `grid-cols-[360px_1fr_340px]`로 고정. 1280px 미만에서 깨진다.
- 이유: Phase 0 사용자는 PC에서 검증 예정. 모바일은 "현장에서 태블릿으로"라는 별개 가설이라 Phase 1에서 본다.
- 만약 지금 급하게 대응해야 한다면: 좌/우 aside를 drawer로 전환, `sidePanel` 탭 대신 버튼 토글.

### 1.2 서버/멀티유저
- 주석은 브라우저 로컬. 같은 도면 공유하는 두 사용자가 서로 주석 못 본다.
- 이유: "혼자라도 쓸 가치가 있나"가 Layer 0 질문. 가치 없으면 서버 붙여도 안 쓴다.
- 붙일 때: `useAnnotationsStore`에 `syncToApi` 추가 + optimistic update + 충돌 해결(LWW 또는 CRDT).

### 1.3 AI 메타 추출
- 이전 프로토타입이 갖고 있던 "AI가 스니펫 요약/태그 생성" 전부 배제. 현재 `snippet`/`type`/`discipline`은 **사람이 쓴다**.
- 이유: AI 붙여봐야 가설과 무관하다는 게 이전 페르소나 검증 결론.

### 1.4 지식 그래프 시각화
- 이전 프로토타입의 노드-엣지 화면 전부 제거. `EntityToDocs` 하나가 그 역할을 대신한다.
- 이유: 그래프 시각화는 관리자에게 예뻐 보이지만 현업은 "이거랑 이거 어떻게 연결돼?"만 궁금해한다. 역방향 리스트가 그 답을 더 빨리 준다.

### 1.5 업로드/권한/감사
- 문서는 JSON 시드만. 업로드 UI 없음. 모든 주석은 `author` 자유 문자열.
- ISS-034~036 (업로드/권한) 등은 **Layer 1**로 미뤘다. `D:\_Project\prototype-도면지식관리\docs-시스템분석\06-기능추가-리스트.md` 참조.

### 1.6 i18n
- 한국어 고정. 라벨 하드코딩.
- 이유: 검증 대상이 국내 현업. 다국어는 Layer 2에서도 할지 말지.

## 2. 알려진 버그/한계

### 2.1 한글 학제 검색 작동 안 함
- Fuse 키에 `discipline`을 넣었지만 값이 영어 enum(`ELECTRICAL`)이라 한글 "전기"로는 매칭 안 됨.
- 해결안: `02-search-and-list.md §7` 참조. 파생 필드 추가로 간단히 고침.

### 2.2 CLAUDE.md와 코드 불일치
- `CLAUDE.md §5-1`은 "이미지 fallback 우선"이라고 적혀 있지만 현재 `pickMode`는 PDF 우선.
- 2026-04-17 세션에서 실 PDF 들어오면서 로직이 바뀌었는데 CLAUDE.md가 갱신 안 됨.
- **이 문서(07)를 현재 코드의 정답으로 간주한다**. 시간 될 때 CLAUDE.md 본문 수정.

### 2.3 설비 태그 부분 매칭 불가
- `docsForTag("CH")`는 아무것도 반환 안 함. `"CH-001"`, `"CH-002"`를 같이 보려면 정확한 태그 2번 쳐야 함.
- `EntityToDocs`는 자동완성 `suggestions`로 이 갭을 일부 메우지만, **suggestions가 hits로 바뀌는 건 사용자가 칩을 누를 때뿐**.

### 2.4 동일 태그 다중 페이지 표현 불가
- `DocEntityLink.page`는 단수. 한 태그가 한 도면 안에서 여러 페이지에 있으면 한 페이지만 기록됨.
- 스키마 변경으로 쉽게 해결 가능 (`page?: number[]`).

### 2.5 주석 저장 silent fail
- localStorage quota 초과나 비활성화 상태에서 저장 실패해도 UI 반응 없음.
- 현재 시점에 이게 실제 문제가 될 확률은 낮지만(용량 여유 충분), 실제 배포라면 toast 필요.

### 2.6 zoom 적용 후 빈 영역 클릭 시 주석 좌표
- 현재 `handleSurfaceClick`은 `surfaceRef` div의 rect 기준으로 정규화한다. 이 div는 `<Page>`/`<img>`를 감싸므로 일반적으로 문제 없음.
- 다만 `TransformWrapper`의 panning이 극단적으로 멀어지면 클릭 좌표가 `surfaceRef` 밖이 되어 `x<0 || x>1`로 무시될 수 있다. 정상 동작.

## 3. 미해결 결정 (사용자 확인 필요)

| # | 질문 | 현재 가정 | 필요 시점 |
|---|---|---|---|
| 1 | 모든 `documents.json`에 실 PDF가 붙는가 | `doc-001`,`002`,`003`,`004`,`005`만 실 PDF. 나머지는 더미 가능성 | Phase 0 페르소나 테스트 전 |
| 2 | `drawing_number`, `drawing_type`, `location`, `revision` 필드를 실제 값으로 채울 것인가 | 타입만 있고 값은 undefined | Phase 1 메타 확장 결정 시 |
| 3 | 설비 태그 네이밍 컨벤션 고정 (대문자-숫자 vs 한글 혼용) | 현재 모두 `XX-NNN` 대문자 | 실데이터 수집 시작 전 |
| 4 | 주석 삭제 시 확인 다이얼로그 필요한가 | 없음 (`onDelete` 즉시 실행) | 사용자 실수 리포트 관찰 후 |
| 5 | 모바일 뷰포트(375px)를 Phase 0에 포함할 것인가 | Phase 0 제외 | 페르소나 테스트 설계 단계 |
| 6 | 주석 이미지 첨부 | 미구현 | 현장 주석 요구 빈도 확인 후 |

## 4. 잘못 건드리면 아픈 곳

- **`src/app/page.tsx`의 state 7개**: 더 추가하기 전에 정말 여기 있어야 하는지 반문. 컴포넌트 내부 state로 충분한 경우가 많다.
- **`useAnnotationsStore`의 hydrated 플래그**: 제거하면 첫 렌더에서 빈 배열을 localStorage에 써서 기존 주석을 날린다. 절대 빼지 말 것.
- **`PdfViewer`의 `key={doc.doc_id}-${pageNumber}-${mode}`**: 줌 초기화/상태 리셋을 위한 것. 제거하면 문서 전환 시 이전 문서의 `totalPages`가 남는 등 잔존 상태 버그.
- **`pickMode` 순서**: PDF → 이미지 → empty. 이 순서 바꾸면 실 PDF 있는데도 이미지가 먼저 뜨는 기이한 동작.
- **`TransformWrapper`의 `doubleClick:{disabled:true}`**: 이걸 풀면 주석 생성 더블클릭이 줌으로 흡수될 수 있음.

## 5. Phase 전환 포인트

**Layer 0 → Phase 1 진입 기준 (제안)**:
- 페르소나 3인 이상이 "이 화면이 NAS+엑셀보다 낫다"고 명시
- 자발적 지불 의사 언급 1명 이상
- 현장 주석/역추적 사용 빈도 주당 5회 이상 (실제 사용 로그)

**Phase 1에서 가장 먼저 붙일 것** (우선순위):
1. 서버 저장 + 멀티유저 (주석 공유가 다음 막힘점)
2. 문서 업로드 UI
3. 설비 링크 편집 UI
4. 간단한 권한 (프로젝트별 접근)

## 6. 성능 노트

현재 규모에서 성능 이슈는 없다. 다만 스케일 업 시 터질 자리:

| 자리 | 8건 기준 | 500건 기준 예상 |
|---|---|---|
| `filtered` useMemo | 즉시 | Fuse 인덱스 크면 20~50ms — 여전히 OK |
| `DrawingsList` 렌더 | 즉시 | 가상 스크롤 필요 |
| `AnnotationList` 그룹핑 | 즉시 | 주석 1만 건 이상 시 가상 스크롤 |
| `tagToDocsIdx` 빌드 | 1ms 미만 | 5만 링크면 100ms — 빌드 타임에 pre-compute |
| `PdfViewer` 렌더 | PDF 페이지당 수백ms | 동일 (페이지 단위라 문서 수 무관) |

**가장 먼저 아플 곳**은 `DrawingsList` 무한 리스트. `react-virtuoso` 같은 라이브러리 한 줄 교체면 해결.

## 7. 코드 스멜 체크리스트 (향후 리팩토링 힌트)

- [ ] `src/app/page.tsx`의 `PopoverMode` 타입이 `AnnotationPopover.tsx`에 중복 정의됨 → `types.ts`로 올려 공유
- [ ] `DrawingsList`의 `disciplineLabels`/`disciplineStyles` record가 `EntityToDocs`에도 필요해질 때 중복 방지를 위해 공통 모듈로 분리
- [ ] `pickMode`를 `src/lib/viewer-mode.ts`로 분리하면 테스트 가능
- [ ] `annotations-store.ts`의 `LS_KEY` 상수를 `src/lib/constants.ts`에 모아두면 "mvp-v1 → v2" 마이그레이션 시점에 한 곳만 수정

현재 전부 미진행. 하면 좋지만 가설 검증과 무관해서 **지금은 하지 말 것**.
