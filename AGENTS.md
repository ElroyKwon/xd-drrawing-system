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

## 사람 승인 게이트

`HUMAN_GATE.md`에 있는 항목은 자동으로 넘기지 않는다. 특히 인증, 권한, DB 스키마, 고객 데이터, 삭제, 배포 관련 변경은 먼저 확인한다.
