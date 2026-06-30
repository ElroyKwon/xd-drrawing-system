# S5 — 이슈 영속 + 뷰어 핀 연계  [STATUS: FROZEN 2026-06-29]

> ai-loop 스테이지 계약. `LOOP.md`·`PLAN.md` freeze 결정과 S1(`prompts/01`)·S1.5(`prompts/02`)·S2(`prompts/03`)·S3(`prompts/04`)·S4(`prompts/05`)·S2.5(`prompts/06`) 결과를 상속한다. 구현 에이전트가 이 텍스트를 그대로 입력받아 자율 실행하고, **별도 검증팀이 아래 Acceptance checklist(H1~H13)로 항목별 채점**한다. 합격을 위해 기준을 도중에 고치지 않는다(기준 변경 = 스코프 변경 = HUMAN_GATE).

## Stage goal / Done-When

ACC 벤치마크 **§H 이슈**를 **실동작+영속**시킨다. 정적/no-op인 `IssuesView`(하드코딩 이슈행 1개 + onClose-only 작성 모달)와 `IssueAddPanel`(정적 `issueCategories` count)을 실데이터·영속으로 교체하고, 2D 뷰어에 **이슈 핀**을 실제로 찍어 도면 위치에 이슈를 연계한다. LOOP.md Done-When "**H 이슈: 이슈 생성/조회/상태변경이 영속. 뷰어 핀 좌표가 시트에 연계.**"를 충족한다.

세 축:
1. **이슈 영속** — 독립 `Issue` 엔티티를 `DrawingStore`에 신설(Json·TypeDB 양 백엔드, S4 마크업/측정 미러 패턴 계승). 생성/조회/상태변경/삭제 CRUD. 프로젝트 전역 이슈 목록(`IssuesView`)이 실데이터로 동작.
2. **뷰어 핀 연계** — 마크업 도구레일의 "이슈 핀" 도구로 벡터/래스터 캔버스에 핀을 찍어 이슈를 생성하고, 핀 좌표를 S4 `coord_space`(DXF=world, PDF=image)로 영속해 새로고침/줌 후에도 시트에 고정 렌더된다. 핀은 **선택적**(핀 없는 전역 이슈도 허용).
3. **양방향 연계** — IssuesView/IssueAddPanel 목록에서 이슈 클릭 시 해당 시트·핀 좌표로 뷰어가 점프(딥링크). 뷰어 핀 클릭 시 이슈 상세 표시.

**완료 정의**: (a) IssuesView에서 실제 도면을 보고 만든 운영자 이슈를 작성→목록에 실데이터로 표시→상태를 열림→진행중→답변됨→닫힘으로 전이→새로고침 복원. (b) 뷰어에서 이슈 핀 도구로 DXF 시트의 특정 위치에 핀을 찍어 이슈 생성→새로고침하면 world 좌표로 복원·줌해도 고정. PDF 시트는 정규화 좌표(image)로 핀. (c) 목록에서 핀 있는 이슈 클릭→해당 시트가 열리고 핀으로 뷰어 점프. 콘솔 0.

## 2026-06-29 user correction 계승 (S4와 동일 — 반드시 실행 전 반영)

- 웹 화면은 DWG/PDF 원본을 직접 수정하는 도구가 아니라, 운영자가 현장 불일치·검토 의견·수정 요청·조치 상태를 도면 위치에 남기고 CAD/문서 담당자가 나중에 원본을 일괄 수정할 근거를 모으는 도면관리 업무공간이다.
- S5 증거는 generic seed(`문 출입 방향 확인` 같은 하드코딩, 무의미한 테스트 좌표)만 보여주면 **불합격**이다. 구현 에이전트는 local backend로 실제 렌더된 시트 이미지/DXF 벡터 시트를 최소 1개 이상 열어 화면 내용을 확인하고, 그 도면에서 읽히는 실제 위치·설비/구역·문제 유형에 맞춘 이슈/핀 예시를 만들어야 한다.
- 예시 문구는 운영자 관점이어야 한다. 예: "현장 패널 번호와 도면 표기가 다름 — CAD 확인 요청", "배선 경로 도면과 현장 상이", "설비 위치 변경 확인 후 도면 수정 요청", "구역명/장비 태그 식별 불명확". 나중에 CAD 수정 요청 묶음으로 전달 가능한 기록이어야 한다.

## Co-design log (2026-06-29 사용자 확정 — AskUserQuestion 4결정 freeze)

- **(Q1) 데이터 모델 = 독립 Issue 엔티티.** store에 `Issue`를 마크업과 별개 엔티티로 신설. 핀은 이슈에 내장(`sheet_id`+`pin{point, coord_space}`). 마크업 인프라 재활용(kind 확장)도, 마크업 참조(markup_id)도 아닌 독립 모델 — IssuesView(프로젝트 전역)와 뷰어 핀(시트 컨텍스트)을 둘 다 자연스럽게 지원하고 ACC 이슈 모델에 충실. → 마크업↔이슈 직접 참조 연계는 범위 외(후속).
- **(Q2) 상태·메타 = ACC식 충실.** 상태 머신 `열림`→`진행중`→`답변됨`→`닫힘`(+삭제됨 soft delete). 메타: `type`(설계 검토·현장 확인·간섭·품질·협의 등), `assignee`(담당자), `category`(clash/quality/coordination — IssueAddPanel 카테고리), `title`, `description`, `author`, `created_at`, `updated_at`. `IssueAddPanel`의 `issueCategories` count는 정적 상수 제거 → 실집계(카테고리별 열린 이슈 수).
- **(Q3) 연계 범위 = 양방향(점프 포함).** 뷰어 핀 생성 + IssuesView/IssueAddPanel 실데이터 목록 + **목록 항목 클릭 시 해당 시트·핀 좌표로 뷰어 점프(딥링크)**. 뷰어 핀 클릭 시 이슈 상세. 완전한 워크플로.
- **(Q4) 핀 = 선택적 + S4 좌표계 계승.** 핀 좌표는 S4 `coord_space`(DXF=`world`, PDF/래스터=`image` 정규화 [0,1]) 그대로 계승, VectorCanvas world↔screen 변환 재사용. **핀 없는 전역 이슈도 허용**(IssuesView에서 위치 없이 작성 가능). 핀 있으면 시트에 고정 렌더.
- **(가정) 영속 = DrawingStore 확장.** S4 마크업/측정 미러 패턴 계승 — `JsonDrawingStore`(`_issues.json`) + `TypeDBDrawingStore`(JSON 미러 의존, 직접쿼리화 후속). TypeDB 스키마(`schema/04-drawings.tql`)에 `issue` entity 추가(Study_TypeDB 계승). 이슈는 `file_id` 스코프(프로젝트 전역 목록은 전체 file_id across), 핀은 `(file_id, sheet_id)` + 좌표.
- **(가정) 이슈 핀 도구 실연결.** `MarkupToolRail`에 이미 있는 "이슈 핀" 도구(UI만 존재)를 실동작화. 핀 찍기 → 이슈 생성 인라인 폼/패널 → POST. `VectorCanvas`/`MarkupCanvas`에 `drawIssuePin` 렌더 추가.
- **(가정) 테스트 도면.** 뷰어 핀은 S1~S4에서 검증된 DXF 벡터 시트 + PDF 시트로 입증. 실제 렌더 내용을 보고 운영자 이슈 작성. 처리 결과를 EVIDENCE에 기록(무성 절단 금지).

## Instruction (수행 단계)

1. **S5-a 백엔드 영속 모델**: `store.py` `DrawingStore`에 이슈 CRUD 추가 — `add_issue(meta)`/`list_issues(file_id=None, status=None)`/`get_issue(issue_id)`/`update_issue(issue_id, **fields)`/`delete_issue(issue_id)`(soft delete → status="삭제됨"). Json·TypeDB 두 구현(TypeDB는 S4처럼 `_MIRROR` 위임). issue 메타: `issue_id`·`file_id`·`sheet_id`(nullable)·`title`·`type`·`status`·`category`·`assignee`·`author`·`description`·`pin`(nullable: `{point:[x,y], coord_space:"world"|"image"}`)·`created_at`·`updated_at`. 상태 전이 검증(허용 집합). `schema/04-drawings.tql`에 `issue` entity 추가.
2. **S5-b 백엔드 라우트**: 신규 `routes_issue.py`(또는 routes 확장) — `GET /api/drawings/issues`(전역 목록, `status`/`file_id`/`category` 필터)·`GET /api/drawings/{file_id}/issues`(파일 스코프)·`POST /api/drawings/{file_id}/issues`·`PATCH /api/drawings/issues/{issue_id}`(상태/속성 변경)·`DELETE /api/drawings/issues/{issue_id}`. `GET /api/drawings/issues/categories`(또는 목록 응답에 집계 포함) — 카테고리별 열린 이슈 count 실집계. 에러계약(404/400) S1~S4 일관. 핀 좌표 검증(coord_space 허용, world=실수 좌표, image=[0,1] 범위).
3. **S5-c 프론트 API 클라이언트**: `src/api/drawings.ts`에 `Issue` 타입 + `listIssues(filters?)`·`listFileIssues(fileId, sheetId?)`·`createIssue(fileId, input)`·`updateIssue(issueId, patch)`·`deleteIssue(issueId)`·`issueCategoryCounts()` 추가(S4 markup API 패턴 계승).
4. **S5-d IssuesView 실데이터**: `IssuesView.tsx` 전면 실연결 — 마운트 시 `listIssues` 로드, 열린/삭제됨 필터 실동작, 검색 실동작, 작성 모달 submit → `createIssue` 영속(정적 행·no-op 제거). 이슈 인스펙터 실데이터(유형·위치·상태·담당자), 상태 변경 드롭다운/버튼 → `updateIssue` 영속. **핀 있는 이슈 클릭 → 해당 시트 뷰어로 점프(딥링크)**.
5. **S5-e IssueAddPanel 실집계**: `IssueAddPanel.tsx` 카테고리 count를 `issueCategoryCounts()` 실데이터로. 검색 입력 실연결. 카테고리 선택 시 뷰어 핀 도구 컨텍스트(선택 카테고리가 새 이슈 기본값).
6. **S5-f 뷰어 이슈 핀 생성**: `MarkupToolRail`의 "이슈 핀" 도구 실동작화 — 선택 후 캔버스 클릭 → 핀 위치 확정 → 인라인 이슈 작성(제목·유형·담당자·카테고리, S4 좌표계로 핀 좌표 산출) → `createIssue` 영속. `SheetViewerShell` 상태/배선.
7. **S5-g 뷰어 이슈 핀 렌더+복원**: `VectorCanvas.tsx`에 `drawIssuePin`(world↔screen 변환 재사용, 핀 마커+번호/상태색) 추가, `MarkupCanvas.tsx`에 정규화 좌표 핀 렌더. 시트 진입 시 `listFileIssues(fileId, sheetId)` 로드 → 핀 복원(줌/핏에도 고정). 핀 클릭 → 이슈 상세(좌측 이슈 탭/인스펙터).
8. **S5-h 양방향 점프**: IssuesView/IssueAddPanel 목록 → 시트+핀 좌표로 뷰어 라우팅(딥링크). 뷰어 진입 시 대상 핀 하이라이트/포커스.
9. **검증**: 백엔드 pytest(이슈 CRUD·상태 전이 검증·핀 좌표 검증·카테고리 집계·전역/파일 스코프 목록·soft delete·traversal/에러계약), 프론트 test(IssuesView 실데이터·작성→영속·상태변경·핀 생성→복원·카테고리 집계·회귀), `npm run build`·`npm test`·`git diff --check`. 브라우저 e2e(IssuesView: 운영자 이슈 작성→목록→상태전이→복원 / 뷰어: 이슈 핀 찍기→새로고침 복원→줌 고정→목록 클릭 점프 / PDF: image 좌표 핀) 스크린샷, 콘솔 0.

## Inputs

- 프론트: `src/build/IssuesView.tsx`(전역 이슈 화면), `src/build/viewer/IssueAddPanel.tsx`(좌측 이슈 탭), `src/build/viewer/viewerData.ts`(`IssueCategory`·`issueCategories` 정적시드·`MarkupTool` "이슈 핀"), `src/build/viewer/MarkupToolRail.tsx`("이슈 핀" 도구 UI), `src/build/viewer/VectorCanvas.tsx`(world↔screen 변환·`drawMarkup`→`drawIssuePin` 추가), `src/build/viewer/MarkupCanvas.tsx`(정규화 핀), `src/build/SheetViewerShell.tsx`(상태·배선·딥링크), `src/api/drawings.ts`(Issue API 확장).
- 백엔드: `backend/store.py`(`DrawingStore`·Json·TypeDB 이슈 CRUD), 신규 `backend/routes_issue.py`(또는 routes_drawing/markup 확장), `backend/main.py`(라우트 등록), `backend/schema/04-drawings.tql`(issue entity).
- 스펙: `docs/Screenshot_Feature_Catalog.md` §H 이슈, `docs/buildout-loop/LOOP.md` Done-When "H 이슈". S4 마크업 영속 패턴(`prompts/05`) 참고.
- 테스트 도면: S1~S4 검증 DXF/PDF 시트(실척 좌표·실 렌더). 운영자 이슈는 실제 렌더 내용 기반.

## Acceptance checklist (검증팀이 항목별 채점 — freeze 후 불변)

- [ ] H1. **이슈 생성 영속**: IssuesView 작성 모달 + 뷰어 핀 도구 둘 다 실제 `POST`로 이슈를 생성·영속. no-op(onClose-only) 제거.
- [ ] H2. **이슈 조회/목록 실데이터**: IssuesView가 `listIssues` 실데이터로 목록 표시. 열린/삭제됨 필터·검색 실동작. 하드코딩 행 제거.
- [ ] H3. **상태 변경 영속**: 이슈 상태를 열림→진행중→답변됨→닫힘으로 전이하고 `updateIssue`로 영속, 새로고침 복원. 허용되지 않은 전이 거부.
- [ ] H4. **뷰어 핀 생성(world)**: 마크업 도구레일 "이슈 핀" 도구로 DXF 벡터 시트의 특정 위치 클릭 → 이슈+핀 생성. 핀 좌표 = S4 world 좌표.
- [ ] H5. **핀 렌더+복원(고정)**: 핀이 VectorCanvas에 렌더되고 새로고침/재진입 시 복원. world 좌표라 줌/핏 변경에도 도면에 고정. 핀 클릭 → 이슈 상세.
- [ ] H6. **양방향 점프(딥링크)**: IssuesView/IssueAddPanel 목록에서 핀 있는 이슈 클릭 → 해당 시트가 열리고 핀 좌표로 뷰어 점프·하이라이트.
- [ ] H7. **핀 선택적(전역 이슈)**: 핀 없는 이슈를 IssuesView에서 위치 없이 작성·영속 가능. 핀 없는 이슈는 뷰어에 핀 없이 목록만.
- [ ] H8. **메타 충실(ACC식)**: 유형·담당자·카테고리·상태 4종 실데이터. `IssueAddPanel` 카테고리 count가 정적 상수 아닌 실집계(카테고리별 열린 이슈 수).
- [ ] H9. **백엔드 영속 모델**: `store.py` 이슈 CRUD(Json·TypeDB 양 백엔드), `schema/04-drawings.tql` issue entity 추가. soft delete, 상태/핀 좌표 검증. 전역·파일 스코프 목록.
- [ ] H10. **PDF 핀(정규화)**: PDF/래스터 시트에서도 이슈 핀이 정규화 이미지 좌표(coord_space=image, [0,1])로 생성·영속·복원.
- [ ] H11. **테스트 게이트**: 백엔드 pytest + 프론트 `npm test` + `npm run build` + `git diff --check` clean. 이슈 CRUD·상태 전이·핀 좌표·카테고리 집계 커버.
- [ ] H12. **브라우저 e2e + 콘솔 0**: IssuesView(작성→목록→상태전이→복원) + 뷰어(핀 찍기→복원→줌 고정→목록 점프) + PDF(image 핀) end-to-end 스크린샷, 콘솔 에러 0.
- [ ] H13. **실제 도면 기반 운영자 이슈 사례**: 증거 스크린샷의 이슈/핀은 실제 렌더된 도면 이미지/벡터 시트를 보고 만든 운영자 사례(위치·설비/구역·문제 유형 일치). generic seed·무의미 테스트 좌표·도면 무관 텍스트면 불합격.

## Out of scope (S5에서 의도적으로 하지 않음)

- **마크업↔이슈 직접 참조 연계(issue가 특정 마크업 엔티티를 참조)** — 독립 Issue 엔티티 모델 채택. 핀은 이슈 내장 좌표. 마크업-이슈 객체 연결은 후속.
- **이슈 첨부파일·댓글 스레드·@멘션·알림** — ACC 이슈의 협업 기능은 후속. S5는 생성/조회/상태/핀까지.
- **이슈 권한·작성자 enforcement** — 인증/RBAC는 S7. author/assignee 메타는 표시까지.
- **PDF/래스터 측정 연계, 수동 캘리브레이션** — S4 범위(이미 처리). 변경 없음.
- **Build 홈 위젯의 이슈 집계·전역 검색** — S6. S5는 IssuesView 자체 목록·검색까지.
- TypeDB 직접 쿼리화(JSON 미러 의존 유지), AI/온톨로지(S8), APS(전략상 배제).

## Freeze 답 (사용자 확정 — AskUserQuestion 2026-06-29)

1. 데이터 모델 = **독립 Issue 엔티티**(마크업과 별개, 핀 내장).
2. 상태·메타 = **ACC식 충실**(상태 4종 + 유형·담당자·카테고리, 카테고리 count 실집계).
3. 연계 범위 = **양방향**(뷰어 핀 생성 + 목록 실데이터 + 목록→뷰어 점프 딥링크).
4. 핀 = **선택적 + S4 좌표계 계승**(DXF world / PDF image, 핀 없는 전역 이슈 허용).

→ STATUS: FROZEN(2026-06-29). 실행·채점은 이 고정 텍스트 기준. 합격을 위해 기준을 도중에 고치지 않는다(기준 변경 = 스코프 변경 = HUMAN_GATE).
