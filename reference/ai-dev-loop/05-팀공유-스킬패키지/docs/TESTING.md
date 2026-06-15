---
tags:
  - AI개발루프
  - 스킬테스트
  - 검증루프
aliases:
  - 팀 공유 스킬 테스트 가이드
created: 2026-06-13
related:
  - [[스킬]]
  - [[Claude Code]]
  - [[Codex CLI]]
---

# 테스트 가이드

## 목표

스킬은 설치만으로 끝나지 않는다. 팀 표준으로 쓰려면 스킬 없이 실패하는 사례와 스킬 적용 후 개선되는 사례를 비교해야 한다.

## 기본 절차

1. 빈 테스트 프로젝트를 만든다.
2. `templates/project-loop/` 내용을 복사한다.
3. 스킬 없이 같은 요청을 실행해 baseline을 기록한다.
4. 스킬을 설치한다.
5. 같은 요청을 다시 실행한다.
6. 결과를 `EVIDENCE.md`에 기록한다.

## 평가 기준

| 항목 | 통과 기준 |
|---|---|
| 문서 확인 | `SPEC.md`, `PLAN.md`, `CHECKS.md`, `HUMAN_GATE.md`를 먼저 읽음 |
| 기능 문서 생성 | 구현 전 7개 핵심 문서 생성을 요구함 |
| 구현 전 검토 | 7개 문서 간 누락/충돌을 보고함 |
| Gate 판정 | 정상 `PASS`와 `SLICE-ONLY PASS`를 구분함 |
| 검증 루프 | 빌드/테스트/브라우저 검증을 요구함 |
| 완료 보고 | 명령 결과와 남은 리스크를 보고함 |
| 사람 승인 | 위험 작업을 자동 실행하지 않음 |

## 스킬별 테스트

각 스킬 폴더의 `evals/evals.json`을 확인한다.

예:

```text
skills/planning-gate/evals/evals.json
skills/feature-docs-scaffold/evals/evals.json
skills/development-loop-orchestrator/evals/evals.json
skills/validator-loop/evals/evals.json
```

## 테스트 결과 기록 형식

```text
Date:
Skill:
Tool:
Prompt:
Without skill:
With skill:
Pass/Fail:
Notes:
```
