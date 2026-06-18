# Codex 작업 지침

## 언어

- 기본 응답은 한국어로 한다.
- 기술명, API명, 파일명은 원문을 유지한다.

## 프로젝트 정체성

- 이 프로젝트는 `xd-drawing-system`이다.
- Autodesk 제품을 그대로 납품하는 것이 아니라, XD 시스템군 안에서 ACC Build 수준의 도면관리 UX를 재현하고 XD 고유 기능을 붙이는 프로젝트다.
- UI/UX 판단은 직접 접속보다 `reference/acc-screenshots`의 저장 스크린샷과 `reference/acc-analysis/_ACC-Build-화면분석-재현설계.md`를 우선 근거로 삼는다.

## 세션 진입 순서

1. `README.md`
2. `SPEC.md`
3. `PLAN.md`
4. `CHECKS.md`
5. `HUMAN_GATE.md`
6. `docs/sessions/NEXT_SESSION.md`
7. `reference/README.md`

## 참고자료 우선순위

1. `reference/acc-screenshots/`
2. `reference/acc-analysis/_ACC-Build-화면분석-재현설계.md`
3. `reference/dks-design-docs/도면관리시스템_상세설계/00_개요-PMO/README.md`
4. `reference/dks-design-docs/도면관리시스템_상세설계/05_프론트엔드-UIUX/README.md`
5. `reference/dks-design-docs/도면관리시스템_상세설계/12_개발준비-기술스택/12-1_기술스택ADR.md`
6. `reference/old-prototypes/`
7. `reference/ai-dev-loop/`

## 개발 방식

- 한 번에 전체 시스템을 만들지 않는다.
- 기능 하나를 정하고, 그 기능의 스크린샷 근거를 확인한 뒤 구현한다.
- 각 기능은 `docs/feature-notes/`에 짧은 기록을 남긴다.
- `SPEC.md`, `PLAN.md`, `CHECKS.md`, `EVIDENCE.md`를 기능 단위로 갱신한다.
- 구현 전에는 `development-loop-orchestrator`로 현재 단계를 확인한다.
- 새 기능은 `feature-docs-scaffold`로 7개 핵심 문서를 만든 뒤 `planning-gate`를 통과해야 한다.
- `SLICE-ONLY PASS`는 정식 문서 루프 PASS가 아니며, 구현 범위를 명확히 제한할 때만 사용한다.

## 보존 원칙

- `reference/` 아래 자료는 원본 참고용이다. 수정하지 말고 필요한 내용은 `docs/`로 정리해 사용한다.
- 기존 프로젝트 `D:\_Project\prototype-도면지식관리`와 `D:\_Project\prototype-도면지식관리-mvp`는 수정하지 않는다.
- 무거운 산출물(`node_modules`, `.next`, 빌드 캐시)을 reference로 추가하지 않는다.

## 검증 원칙

- 완료 보고 전 `CHECKS.md`에 있는 확인을 실행한다.
- 실행 결과는 `EVIDENCE.md`에 기록한다.
- 브라우저 확인이 필요한 경우에는 가능하면 스크린샷과 콘솔 에러 상태를 함께 남긴다.

## 세션 종료 절차

사용자가 `세션 종료`를 요청하면 구현을 새로 확장하지 말고 closeout/handoff 작업으로 전환한다.

1. `git status --short --untracked-files=all`로 dirty 파일을 확인하고, 기존 변경과 이번 세션 변경을 분리해 기록한다.
2. `PLAN.md`, `CHECKS.md`, `EVIDENCE.md`, `docs/sessions/NEXT_SESSION.md`를 현재 상태에 맞게 갱신한다.
3. `CHECKS.md` 기준의 검증을 실행하고 결과를 `EVIDENCE.md`에 남긴다. 실행하지 못한 검증은 이유와 남은 증거 요구사항을 적는다.
4. 브라우저 검증이 필요한 작업은 fresh interaction, console state, screenshot path가 없으면 PASS로 쓰지 않는다.
5. 남아 있는 blocker, human gate, 다음 세션의 첫 명령과 읽을 파일을 `docs/sessions/NEXT_SESSION.md`에 명시한다.
6. 사용자가 명시적으로 요청하지 않으면 commit/push하지 않는다.

완료 보고에는 다음을 포함한다.

- 현재 stage
- dirty 파일 분류
- 변경 파일
- 실행한 검증과 결과
- 실패 또는 미실행 검증
- blocker와 human gate 상태
- 다음 세션이 이어갈 정확한 next action

## 사람 승인 게이트

`HUMAN_GATE.md`에 있는 항목은 자동으로 넘기지 않는다. 특히 인증, 권한, DB 스키마, 고객 데이터, 삭제, 배포 관련 변경은 먼저 확인한다.
