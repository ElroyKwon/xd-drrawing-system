---
tags:
  - AI개발루프
  - 세션인수인계
  - 중요세션
  - 다음작업
aliases:
  - AI 개발 루프 다음 세션
  - 개발 AI 세팅 중요 세션
created: 2026-06-13
related:
  - [[Claude Code]]
  - [[Codex CLI]]
  - [[Gemini CLI]]
  - [[Antigravity]]
  - [[Warp]]
---

# 다음 세션 인수인계

## 현재 결론

영상식 [[인공지능]] 개발 루프를 그대로 따라 하기 전에, 먼저 로컬에서 재현 가능한 구조를 확정했다.

1차 실행 조합:

```text
[[Warp]] 4페인
Pane 1: [[Claude Code]] - 오케스트레이터 / 구현
Pane 2: [[Codex CLI]] / GPT - 검증자 / 코드리뷰 / 실패 리포트
Pane 3: [[Gemini CLI]] - 보조 검토자 / 긴 문맥 / 대안 검토
Pane 4: PowerShell - npm, test, dev server, git
```

2차 후보:

```text
[[Antigravity]]
VibeLabs 클로드 랩스 스킬팩
Warp Tab Config 또는 Launch Configuration
psmux 또는 tmux형 멀티플렉서
```

2026-06-13 세션 종료 기준 최신 판단:

```text
현재 상태는 "영상 따라하기 준비 완료"가 아니라
"영상식 루프를 재현하기 위한 1차 로컬 뼈대 준비 완료"다.
```

다음 핵심은 질문형 런처에 `plan-only / planning-gate / build-loop / validation-loop / review-only` 실행 모드 선택을 추가하고, 선택된 모드에 따라 `AI_LOOP_SESSION.md`의 시작 프롬프트를 다르게 생성하는 것이다.

## 준비 완료된 것

- 3개 영상/텍스트 입력 자료 수집 완료
- 분석 전용 폴더 생성 완료
- 공식 문서 기준 1차 도구 검증 완료
- 로컬 설치 상태 확인 완료
  - `claude` 있음
  - `codex` 있음
  - `gemini` 있음
  - `warp` 있음
  - `antigravity` 없음
- API 키 없이 계정 로그인 중심으로 가능한 범위 정리 완료
- Claude / GPT-Codex / Gemini / Antigravity 역할 분담 정리 완료
- AI 개발 환경 Git 관리 방향 정리 완료
- 이슈 백로그 생성 완료
- 팀 공유 스킬 패키지 생성 완료
- 개인용 Warp Tab Config 런처 초안 생성 완료
- 질문형 모델 선택 런처 `start-ai-loop-wizard.ps1` 생성 완료
- 영상 시작 질문 흐름 재검토 문서 생성 완료
- `D:\_Project\ai-dev-settings` 개인 AI 개발 설정 저장소 생성 완료
- `D:\_Project\ai-dev-settings\scripts\start-ai-loop.ps1 -ProjectPath D:\_Project -Preview` 검증 완료
- `05-팀공유-스킬패키지/scripts/verify-skill-package.ps1` 검증 완료

## 아직 준비 완료가 아닌 것

다음 항목은 아직 실제 완료가 아니다.

- 영상/VibeLabs 스킬팩 설치
- `/socrates`, `/stargate`, `/harness`, `/auto-orchestrate` 등 영상 스킬 사용 준비
- 직접 제작 스킬의 실제 글로벌 설치
- `planning-gate`, `validator-loop`, `evidence-report` 실사용 검증
- 글로벌 `CLAUDE.md`, 글로벌 `AGENTS.md` 수정
- 다른 컴퓨터 복원용 설치 스크립트 작성
- Warp 4페인 실습 실행
- Warp Tab Config 실제 `-Open` 실행 검증
- 질문형 런처로 Claude/Codex/Gemini 모델 선택 후 4페인 생성 검증
- 소크라테스 대체 스킬 `socratic-planning` 제작
- 브라우저/E2E 하네스 템플릿 작성
- 에이전트 간 파일 기반 inbox/outbox 메시지 라우팅 설계

정정:

- `05-팀공유-스킬패키지/skills/` 아래에는 설치 가능한 `SKILL.md` 초안이 생성되었다.
- 다만 baseline/with-skill 비교 테스트를 완료하지 않았으므로 “팀 표준 검증 완료 스킬”은 아니다.

## 중요한 판단

### 홈 폴더 Git 관리

`C:\Users\cruel` 전체를 GitHub로 관리하지 않는다.

대신 아래 같은 private Git 저장소를 만든다.

```text
D:\_Project\ai-dev-settings
```

Git에는 안전한 원본 설정만 넣고, 실제 홈 폴더에는 설치 스크립트로 복사한다.

### 스킬 상태

현재 영상에 나온 스킬들은 로컬에 설치되어 있지 않다.

현재 만든 것은 설치 가능한 `SKILL.md` 초안과 evals가 포함된 스킬 패키지다. 다만 실제 글로벌 설치와 baseline/with-skill 비교 검증은 아직 끝나지 않았다.

### Warp 페인 제어

AI 모델이 Warp UI를 마음대로 분할/리사이즈할 수는 없다.

사람이 단축키로 구성하거나, Warp Tab Config/Launch Configuration, Antigravity, VibeLabs 하네스 같은 별도 도구가 필요하다.

## 다음 작업 순서

1. `D:\_Project\ai-dev-settings\scripts\start-ai-loop-wizard.ps1`에 실행 모드 선택 추가
2. 실행 모드별 `AI_LOOP_SESSION.md` 시작 프롬프트 분기
3. `socratic-planning` 대체 스킬 제작
4. 브라우저/E2E 하네스 템플릿 추가
5. 현재 글로벌 설정 백업 스크립트 실행
6. 스킬 패키지를 글로벌 Claude/Codex 위치에 설치
7. 빈 테스트 프로젝트에서 `planning-gate` 실사용 검증
8. `calendar-loop-demo` 프로젝트 생성
9. Warp 4페인 실제 `-Open` 실행 검증
10. 성공한 규칙만 글로벌 `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` 템플릿에 반영

추가 진입점:

```text
AI개발루프-스킬학습/05-팀공유-스킬패키지/README.md
```

팀원 공유, 다른 PC 설치, 스킬 테스트는 이 폴더를 기준으로 진행한다.

개인용 자동 터미널 실행은 아래 문서를 기준으로 진행한다.

```text
AI개발루프-스킬학습/01-분석노트/07-Warp-자동실행-개인설정.md
```

실행 명령:

```powershell
powershell -ExecutionPolicy Bypass -File D:\_Project\ai-dev-settings\scripts\start-ai-loop-wizard.ps1
```

## 바로 열어야 할 문서

다음 세션은 이 순서로 보면 된다.

1. `AI개발루프-스킬학습/01-분석노트/08-영상-재검토-시작질문흐름-준비대조.md`
2. `D:\_Project\ai-dev-settings\issues\BACKLOG.md`
3. `D:\_Project\ai-dev-settings\scripts\start-ai-loop-wizard.ps1`
4. `AI개발루프-스킬학습/03-에이전트-규칙-반영/04-초기세팅-스킬-설계.md`
5. `AI개발루프-스킬학습/05-팀공유-스킬패키지/README.md`

## 현재 답변 기준

“준비됐어?”에 대한 답은 다음이다.

```text
정리/판단/다음 실행 설계/개인 설정 저장소/질문형 런처 초안은 준비됨.
실제 스킬 설치, 실사용 검증, Warp 실제 4페인 Open, 브라우저/E2E 하네스는 아직 완료 전.
다음 단계는 질문형 런처에 루프 실행 모드 선택을 추가하고 빈 프로젝트에서 Planning Gate를 검증하는 것이다.
```
