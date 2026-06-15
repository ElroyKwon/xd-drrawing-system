# Claude 작업 지침

Codex와 동일하게 한국어를 기본으로 사용한다.

세션 시작 시 다음 파일을 먼저 확인한다.

1. `README.md`
2. `SPEC.md`
3. `PLAN.md`
4. `CHECKS.md`
5. `HUMAN_GATE.md`
6. `docs/sessions/NEXT_SESSION.md`

이 프로젝트는 `xd-drawing-system`이며, ACC Build 화면을 참고해 XD 도면관리 시스템을 기능 단위로 개발한다.

UI/UX 판단은 `reference/acc-screenshots/`와 `reference/acc-analysis/`를 우선한다.

권장 루프:

1. `development-loop-orchestrator`
2. `project-bootstrap`
3. `feature-docs-scaffold`
4. `planning-gate`
5. 구현
6. `validator-loop`
7. `evidence-report`

`SLICE-ONLY PASS`는 정식 문서 루프 PASS가 아니다.

완료 보고에는 반드시 다음을 포함한다.

- 변경 파일
- 실행한 검증
- 실패 또는 미실행 검증
- 다음 작업

`reference/` 자료는 원본 참고용이므로 수정하지 않는다.
