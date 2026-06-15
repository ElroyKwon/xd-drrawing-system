---
tags:
  - AI개발루프
  - 팀공유
  - 스킬패키지
  - 설치가이드
aliases:
  - AI 개발 루프 팀 공유 스킬 패키지
  - 팀용 AI 스킬팩
created: 2026-06-13
related:
  - [[Claude Code]]
  - [[Codex CLI]]
  - [[Gemini CLI]]
  - [[스킬]]
---

# 팀 공유 스킬 패키지

## 목적

이 폴더는 팀원이 복사하거나 공유받아, 다른 컴퓨터의 [[인공지능]] 개발 에이전트가 읽고 필요한 [[스킬]]을 등록/테스트할 수 있게 만든 패키지다.

지원 대상:

- [[Claude Code]]
- [[Codex CLI]]
- [[Gemini CLI]] 프로젝트 지침
- Windows / [[Warp]] 기반 개발 폴더

## 현재 상태

이 패키지는 `검증 가능한 배포 후보`다.

포함된 `SKILL.md` 파일은 설치 가능한 형식으로 작성되어 있지만, 팀 표준으로 확정하기 전에는 `evals` 시나리오와 빈 테스트 프로젝트에서 반드시 검증해야 한다.

## 폴더 구조

| 경로 | 용도 |
|---|---|
| `skills/` | Claude/Codex에 설치할 스킬 후보 |
| `skills/*/evals/evals.json` | 스킬별 테스트 프롬프트 |
| `templates/project-loop/` | 새 개발 프로젝트에 복사할 기본 AI 지침/루프 문서 |
| `scripts/install-skills-windows.ps1` | 스킬 설치 스크립트 |
| `scripts/verify-skill-package.ps1` | 패키지 구조 검증 스크립트 |
| `docs/INSTALL.md` | 설치 가이드 |
| `docs/TESTING.md` | 테스트 가이드 |
| `docs/REGISTRY.md` | 스킬 목록과 사용 시점 |

## 빠른 시작

미리보기:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-skills-windows.ps1
```

설치:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-skills-windows.ps1 -Apply
```

검증:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify-skill-package.ps1
```

## 중요한 원칙

1. 회사/고객 프로젝트에 바로 적용하지 말고 빈 테스트 프로젝트에서 먼저 검증한다.
2. 스킬이 자동으로 항상 선택된다고 가정하지 않는다.
3. 프로젝트 `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`에 스킬 사용 기준을 함께 둔다.
4. 스킬 적용 후 `EVIDENCE.md`에 어떤 검증을 했는지 기록한다.
5. 글로벌 설정과 프로젝트 설정을 섞지 않는다.
6. 기능 구현 전 `feature-docs-scaffold`와 `planning-gate`를 통과시킨다.
7. `SLICE-ONLY PASS`는 정식 문서 루프 통과가 아니므로 범위를 명시한다.
