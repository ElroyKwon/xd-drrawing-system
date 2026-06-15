---
tags:
  - AI개발루프
  - 스킬목록
  - 팀공유
aliases:
  - 팀 공유 스킬 레지스트리
created: 2026-06-13
related:
  - [[스킬]]
  - [[Claude Code]]
  - [[Codex CLI]]
---

# 스킬 레지스트리

## 포함 스킬

| 스킬 | 목적 | 사용 시점 |
|---|---|---|
| `project-bootstrap` | 프로젝트 시작 전 AI 루프 문서와 설정 확인 | 새 개발 폴더 시작 |
| `feature-docs-scaffold` | 기능 시작 전 7개 핵심 설계 문서 생성/정렬 | 새 기능 또는 화면 slice 시작 |
| `planning-gate` | 구현 전 문서 간 누락/충돌 검토 | PRD, 화면 명세, 작업 목록 작성 후 |
| `development-loop-orchestrator` | 현재 단계 판단 후 다음 스킬 선택 | 여러 터미널/세션 사이에서 루프 재진입 |
| `validator-loop` | 구현 후 빌드/테스트/동작 검증 | 완료 전, PR 전, 세션 종료 전 |
| `evidence-report` | 완료 증거와 남은 리스크 정리 | 최종 보고, 인수인계 |
| `tag-alarm-review` | 태그/알람/히스토리안 등록 상태 검토 | 현장/PLC/HMI/XD-HUB 자료 검토 |

## 자동 호출 유도 문장

프로젝트 `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`에는 아래 기준을 둔다.

```text
작업을 시작하기 전에 현재 요청에 맞는 로컬 스킬을 먼저 확인한다.
기획/구현 전에는 project-bootstrap, feature-docs-scaffold, planning-gate를 고려한다.
현재 단계가 애매하면 development-loop-orchestrator로 다음 스킬을 결정한다.
검증/완료 전에는 validator-loop를 고려한다.
최종 보고/세션 종료 전에는 evidence-report를 고려한다.
태그/알람/히스토리안 자료 검토에는 tag-alarm-review를 고려한다.
사용자가 스킬 이름을 직접 말하지 않아도 필요한 스킬을 선택해 사용한다.
```

## 주의

스킬 자동 선택은 보장되지 않는다. 각 도구에서 실제 호출 여부를 확인해야 한다.
