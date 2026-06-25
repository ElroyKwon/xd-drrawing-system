# S2 — 시트 레지스터 (PDF 페이지 분할 + paperspace DWG 분리)  [STATUS: FROZEN — 2026-06-25 사용자 확인 완료]

> ai-loop 스테이지 계약. `LOOP.md`·`PLAN.md` freeze 결정과 S1(`prompts/01`)·S1.5(`prompts/02`) 결과를 상속한다. 구현 에이전트가 이 텍스트를 그대로 입력받아 자율 실행하고, **별도 검증팀이 아래 Acceptance checklist(C1~C8)로 항목별 채점**한다. 합격을 위해 기준을 도중에 고치지 않는다(기준 변경 = 스코프 변경 = HUMAN_GATE).

## Stage goal / Done-When

업로드된 도면(특히 **멀티페이지 PDF**)이 페이지 단위로 분할돼 **`시트` 목록(`SheetsListView`)에 실데이터로 등록**된다. 정적 시드(`initialSheets` A001/A101…)를 **실데이터로 완전 교체**하고, 시트별 번호·제목·공종·썸네일이 표시되며 검색/필터/정렬이 실동작한다. DWG의 **다중 paperspace 레이아웃은 다중 시트로 분리**된다.

**완료 정의**: 멀티페이지 PDF를 업로드하면 시트 목록에 페이지 수만큼 시트가 실데이터(번호·제목·공종·썸네일)로 뜨고, 검색/필터/정렬·시트 열기(뷰어 연계)가 동작한다.

## Co-design log (2026-06-25 사용자 확정 — freeze된 결정)

- **(Q1) 범위 = 순수 시트 레지스터 + paperspace DWG 분리.** PDF 멀티페이지 분할→시트 목록 실데이터 + 검색/필터/정렬 + DWG 시트(S1/S1.5) 통합 + **DWG 다중 paperspace 레이아웃 분리**. **TypeDB 직접 쿼리화는 S2 범위 밖**(별도 후속).
- **(Q2) 시트 목록 = 실데이터 완전 교체.** 정적 `initialSheets` 제거 → `GET /api/drawings`의 시트로 구성. 빈 프로젝트는 "아직 등록된 시트가 없습니다"(기존 emptyMessage 활용).
- **(Q3) 메타 추출 = 타이틀블록 텍스트 휴리스틱.** PyMuPDF `page.get_text()`로 각 페이지 텍스트에서 **시트번호/제목 패턴 추출**(예: `EE-01-006`, `A101`). 공종은 번호 접두(E/A/M/P/S)→공종코드 매핑. **추출 실패 시 폴백**: 파일명에서 번호 추정 → 그래도 없으면 `Page N`. 추출 규칙·폴백을 EVIDENCE에 기록.
- **(가정) 버전/버전세트 = S3로 연기.** S2는 업로드분을 v1로 등록만. 버전 히스토리·재업로드 버전관리는 S3(파일/버전). PLAN 정합.
- **(가정) paperspace 정직한 범위.** DWG에 **다중 paperspace 레이아웃**이 있으면 각 레이아웃을 시트로 분리 렌더(현재 빈-엔티티 필터로 누락되던 케이스 교정). **빈 paperspace(레이아웃 0)인 DWG는 modelspace 단일 시트 유지** — modelspace를 영역 자동분할하는 것은 타이틀블록/뷰포트 추론이 필요해 과도하므로 S2 범위 밖(한계로 명시). 무성 절단 금지(분리 한 시트/통짜 여부를 EVIDENCE에 로깅).
- **(가정) 테스트 도면.** 멀티페이지 PDF = `제주 장주기 BESS … 전기도면 일식.pdf`(68p, 타이틀블록 보유) 또는 동급. 무거우면 페이지 부분집합으로 시연하고 **EVIDENCE에 처리 페이지 수 기록**(무성 절단 금지). 단일페이지 번호추출 확인용 = 청주 `EE-01-00x_*.pdf`(파일명·타이틀블록에 번호). 다중 paperspace DWG = `reference/` 내 보유분 탐색; 없으면 합성 DXF로 분리 로직 입증 + 한계 기록.

## Instruction (수행 단계)

1. **S2-a 백엔드 시트 메타 추출**: `conversion.py`의 `Sheet`에 `sheet_number`·`sheet_title`·`discipline` 필드 추가. PDF 경로(`render_pdf_sheets`)에서 페이지별 `get_text()` → 시트번호/제목 휴리스틱(정규식 패턴·폴백) 추출. 공종 = 번호 접두 매핑. DWG 경로는 레이아웃명/파일명 기반.
2. **S2-b paperspace 분리 교정**: `render_dxf_sheets`에서 다중 paperspace 레이아웃을 각각 시트로 분리(빈-엔티티 필터가 viewport-only 레이아웃을 잘못 누락하지 않도록 교정). 빈 paperspace는 modelspace 단일 유지(로깅).
3. **S2-c 시트 목록 실데이터화**: `BuildSheetsView`가 `GET /api/drawings`를 조회해 drawings→sheets를 `Sheet[]`로 매핑(번호·제목·공종·imageUrl·fileId·source·version). 정적 `initialSheets` 제거(또는 빈 배열). `SheetsListView`에 실데이터 전달. 로딩/빈 상태 처리.
4. **S2-d 검색/필터/정렬**: `filterSheets`(또는 확장)가 실데이터에서 번호·제목·공종·태그로 동작. 정렬(번호/공종/최신) 실동작. 기존 list/grid 뷰모드 유지.
5. **S2-e 뷰어 연계**: 시트 목록에서 시트 열기 → `SheetViewerShell`(DWG=벡터 기본·PDF=래스터 PNG, S1.5 엔진 토글 계승). FilesView 업로드 경로와 일관.
6. **검증**: 백엔드 pytest(시트 메타 추출·paperspace 분리·PDF 분할), 프론트 test(시트 목록 실데이터 렌더·검색/필터 회귀), `npm run build`·`npm test`·`git diff --check`. 브라우저 멀티페이지 PDF 업로드→시트 목록 N시트→검색/필터→열기 스크린샷.

## Inputs

- 프론트: `src/BuildSheetsView.tsx`(initialSheets 사용처), `src/build/SheetsListView.tsx`, `src/buildSheetsData.ts`(Sheet 타입·filterSheets), `src/build/FilesView.tsx`(업로드 경로), `src/api/drawings.ts`.
- 백엔드: `backend/conversion.py`(`render_pdf_sheets`·`render_dxf_sheets`·`Sheet`), `backend/routes_drawing.py`(list/get), `backend/store.py`.
- 테스트 도면: §Co-design log 가정 절. `reference/`·`D:\_Project` 샘플은 읽기 전용 — 스테이징 복사본으로 업로드.

## Acceptance checklist (검증팀이 항목별 채점 — freeze 후 불변)

- [ ] C1. 멀티페이지 PDF 업로드 시 **페이지 수만큼 시트로 분할** 등록(각 페이지=시트, png + 메타). 처리 페이지 수 EVIDENCE 기록.
- [ ] C2. 타이틀블록 휴리스틱으로 **시트번호·제목·공종 추출**, 실패 시 폴백(파일명→Page N) 동작. 추출/폴백 규칙 EVIDENCE 명시.
- [ ] C3. `시트` 목록이 **실데이터로 완전 교체**(정적 initialSheets 제거). 빈 프로젝트는 빈-상태 메시지. 업로드분이 목록에 실데이터로 표시.
- [ ] C4. 검색/필터/정렬이 **실데이터에서 동작**(번호·제목·공종·태그). list/grid 뷰모드 유지.
- [ ] C5. DWG **다중 paperspace 레이아웃 → 다중 시트 분리**. 빈 paperspace는 modelspace 단일(로깅·한계 명시).
- [ ] C6. 시트 목록에서 시트 열기 → 뷰어 연계(DWG=벡터 기본·PDF=PNG, S1.5 엔진 토글 계승).
- [ ] C7. 백엔드 pytest + 프론트 `npm test` + `npm run build` + `git diff --check` clean.
- [ ] C8. 브라우저 콘솔 0 + 업로드→시트목록 N시트→검색/필터→열기 스크린샷 증거.

## Out of scope (S2에서 의도적으로 하지 않음)

- 버전 히스토리·재업로드 버전관리·버전세트(S3). S2는 v1 등록만.
- 파일/폴더 트리 CRUD·권한(S3).
- 마크업·측정·비교 실연산/영속(S4). 시트 열기까지만.
- 이슈(S5).
- **TypeDB 직접 쿼리화**(JSON 미러 의존 유지, 후속). 
- modelspace 영역 자동 시트분할(타이틀블록/뷰포트 추론 — 과도, 후속).
- 인증/RBAC(S7), AI/온톨로지(S8), APS(전략상 배제).

## Freeze 답 (사용자 확정 시 기입)

1. 범위 = 순수 시트 레지스터 **+ paperspace DWG 분리**(TypeDB 쿼리화 제외).
2. 시트 목록 = **실데이터 완전 교체**(정적 시드 제거).
3. 메타 추출 = **타이틀블록 텍스트 휴리스틱**(+ 파일명/Page N 폴백).

4. (가정 확정) 버전 S3 연기 · 빈-paperspace는 modelspace 단일(한계 명시) · 테스트 PDF=제주 BESS 68p 등 멀티페이지.

→ STATUS: FROZEN. 실행·채점은 이 고정 텍스트 기준. 합격을 위해 기준을 도중에 고치지 않는다(기준 변경 = 스코프 변경 = HUMAN_GATE).
