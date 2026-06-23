# LOOP — 외관(appearance) 완성 루프 (supervisor contract)

> ai-loop 스킬용 감독 계약. 다음 세션은 `ai-loop` 스킬을 장착하고 이 파일 + `PROGRESS.md`를 먼저 읽어 **재시작이 아니라 이어받기**로 진행한다.

## Goal

ACC(Autodesk Construction Cloud / Forma) 벤치마크 화면의 **외관**을, 이미 존재하는 로컬 셸들을 끌어올려 **카탈로그(`docs/Screenshot_Feature_Catalog.md`) 구조 수준으로 완성**한다. "없는 화면 만들기"가 아니라 "기존 셸을 카탈로그가 기록한 영역·컨트롤·빈상태·탭 수준으로 채우기"가 핵심.

## Loop type

**FULL loop** — 다화면·다마일스톤, 충실도 기준에 실제 판단이 걸림. Phase 0(소크라테스)는 PRD `Full ACC Visible Surface Coverage Addendum`(FR-FS-001~017)이 이미 스펙이므로 생략. 세 가지 핵심 결정은 아래에서 freeze됨.

## Frozen decisions (2026-06-23 사용자 확정)

1. **충실도 기준 = 카탈로그 구조 완성.** 각 화면이 카탈로그에 기록된 영역·컨트롤·빈상태·탭을 모두 갖춘다. ACC 레이아웃/정보구조는 재현하되 **픽셀 단위 완벽(색·간격·폰트 일치)은 목표 아님.**
2. **검증 = 구조 체크리스트 + 브라우저 스크린샷.** 별도 검증팀이 마일스톤 메타프롬프트의 acceptance 체크리스트를 항목별로 채점하고, 실제 브라우저 렌더 스크린샷을 카탈로그 원본과 육안 대조한다. `npm test`·`npm run build`도 must-pass.
3. **실행 예산 = 마일스톤마다 체크인.** 한 마일스톤(메타프롬프트 공동설계→구현→검증→기록)을 끝내면 멈추고 사용자에게 보고한 뒤 다음 마일스톤 진행.

## Done-When (product)

- [ ] FR-FS-001 My Home: 할당·프로젝트(지도)·책갈피·최근항목 + 온보딩 배너 영역이 카탈로그 수준.
- [ ] FR-FS-002 프로젝트 템플릿: 샘플 템플릿 갤러리 + 허브 템플릿 목록/빈상태 + 작성 2단계 모달.
- [ ] FR-FS-004 Project Admin 측면 네비(회사·브리지·액티비티·알림·위치·설정)가 각각 구분된 화면.
- [ ] 템플릿 상세(템플릿 설정: 구성·템플릿 구성원 / 프로젝트 설정: 프로젝트 구성원·회사·알림 매트릭스) 셸 — Project Admin 셸 재사용.
- [ ] FR-FS-005 Build 홈: 개요/종합 탭 + 진행률·빠른링크·날씨·작업·Bridge·최근작업 위젯 + 종합 분석 차트 카드.
- [ ] FR-FS-006 Build 시트: 번호+썸네일·버전·버전세트·공종·태그·최종수정자 컬럼 + 검색/필터·보기토글·행 메뉴.
- [ ] FR-FS-007~010 2D 뷰어: 마크업 도구군(텍스트·도형·클라우드·폴리라인·다각형 + 속성 패널 + 마크업 로그), 측정/축척 교정, 시트 비교(모달+결과 오버레이), 이슈 연계, 하단 컨트롤·툴레일·필름스트립.
- [ ] FR-FS-011 Build 파일: 폴더 트리 + 업로드 모달 + 파일 테이블 컬럼 + 검색/필터 + 빈/샘플 상태.
- [ ] FR-FS-012 Build 이슈: 목록 툴바 + 이슈 작성 모달 + 인스펙터 + 샘플/빈 상태.
- [ ] FR-FS-013 Build 양식: 로컬 placeholder(원본 캡처 부재 명시).
- [ ] FR-FS-014 Build 사진: 앨범/갤러리/맵 탭 + 앨범 트리 + 빈 갤러리.
- [ ] FR-FS-015 Build 구성원·브리지·설정: 구분된 관리 화면.
- [ ] FR-FS-016 Hub vs Project Admin vs Build 레벨 분리 유지.
- [ ] FR-LC-001~003: FHD/4K/macOS 무파손(가로 클리핑·겹침·폰트 폴백 파손 없음), 신규 화면 포함.

각 항목은 Phase 6.5에서 신선한 비평가가 MET / NARROWED / UNMET + 증거등급으로 reconcile. NARROWED/UNMET는 DONE 차단 → `HUMAN_GATE.md`.

## Stop conditions

- 모든 Done-When 항목 MET + must-pass 게이트 PASS → DONE.
- 또는 HUMAN_GATE 항목 발생 → 정지·보고.
- 또는 한 마일스톤 종료 → 체크인 정지(예산 규칙).

## Human gates (절대 자율 진행 금지 — AGENTS.md)

마크업/이슈/파일 **영속화**, 실제 파일 업로드/저장/삭제, 실제 시트 비교 diff 연산, real viewer engine, DWG→웹 렌더, Autodesk/APS·유료 SDK, DB/API/TypeDB, auth/RBAC, 배포. 외관 루프는 이 모든 것을 **affordance(빈 셸/모달/플레이스홀더)** 로만 표현한다.

## Spec source (중복 생성 금지 — 기존 문서 재사용)

- 스펙: `docs/PRD.md` (FR-FS-001~017, FR-LC-001~003)
- 백로그 SoT: `docs/Screenshot_Feature_Catalog.md`
- 원본 캡처: `스크린샷/` (53장, git 추적)
- 마일스톤: `docs/appearance-loop/PLAN.md`
- 게이트/검증: `docs/appearance-loop/CHECKS.md`
- 진행상태: `docs/appearance-loop/PROGRESS.md`
- 스테이지 메타프롬프트: `docs/appearance-loop/prompts/<stage>.md` (다음 세션이 마일스톤별로 생성)
