---
tags:
  - AI개발루프
  - 설치가이드
  - 스킬설치
aliases:
  - 팀 공유 스킬 설치 가이드
created: 2026-06-13
related:
  - [[Claude Code]]
  - [[Codex CLI]]
  - [[스킬]]
---

# 설치 가이드

## 설치 대상 경로

### Claude Code

```text
%USERPROFILE%\.claude\skills\<skill-name>\SKILL.md
```

### Codex CLI

```text
%USERPROFILE%\.agents\skills\<skill-name>\SKILL.md
%USERPROFILE%\.codex\skills\<skill-name>\SKILL.md
```

이 패키지의 설치 스크립트는 기본적으로 `.claude`, `.agents`, `.codex` 세 위치를 모두 미리보기/설치 대상으로 삼는다.

## 설치 전 확인

```powershell
claude --version
codex --version
```

선택:

```powershell
gemini --version
```

## 미리보기

패키지 루트에서 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-skills-windows.ps1
```

이 명령은 실제 파일을 복사하지 않고 무엇을 복사할지 보여준다.

## 실제 설치

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-skills-windows.ps1 -Apply
```

## 설치 후 확인

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify-skill-package.ps1
```

Claude Code와 Codex CLI를 재시작한 뒤 스킬이 인식되는지 확인한다.

## 주의

- 이 패키지는 로그인 토큰이나 API 키를 포함하지 않는다.
- 외부 스킬팩과 충돌하는 이름이 있으면 설치 전 이름을 조정한다.
- 이미 같은 이름의 스킬이 있으면 덮어쓸 수 있으므로 먼저 백업한다.
