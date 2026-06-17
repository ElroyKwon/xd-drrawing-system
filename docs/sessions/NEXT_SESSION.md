# Next Session

## Start Here

```powershell
cd "D:\_Project\xd-drawing-system"
codex
```

Read in order:

1. `AGENTS.md`
2. `docs/sessions/NEXT_SESSION.md`
3. `docs/superpowers/specs/2026-06-17-project-admin-member-access-design.md`
4. `docs/superpowers/plans/2026-06-17-project-admin-member-access.md`
5. `EVIDENCE.md`
6. `PLAN.md`
7. `CHECKS.md`
8. `HUMAN_GATE.md`

## Immediate Resume - 2026-06-17 AI Loop Mode Dispatch Closeout

Current repository state at this handoff:

- Branch: `master`
- Latest committed HEAD at closeout: this docs closeout commit, `docs: close ai loop mode dispatch session`
- First product slice is implemented, verified, and committed.
- Project Admin member-access implementation commits exist through opening Project Admin from the project list.
- The `.ai-loop` runner mode-dispatch changes are committed at `a7125c0`.
- The closeout handoff and partial Project Admin screenshot artifact are committed in this docs closeout commit.
- No `run-next-ai-loop-request.ps1` process is running at closeout.

Working tree at closeout:

- `git status --short --untracked-files=all` is clean.
- `.ai-loop` runtime queue files are ignored by git and therefore do not appear in status.
- Pending inbox requests:
  - `.ai-loop/control/inbox/0007-project-admin-task6-validation-evidence-real-run.request.md`

The next session should start by running the pending validation-evidence real-run request or explicitly deferring Project Admin Task 6.

First actions:

1. Run `git status --short --untracked-files=all`.
2. Read `EVIDENCE.md` section `Session Closeout - AI Loop Mode Dispatch Handoff - 2026-06-17`.
3. Confirm only `.ai-loop/control/inbox/0007-project-admin-task6-validation-evidence-real-run.request.md` is pending.
4. If validating Project Admin Task 6, run `powershell -ExecutionPolicy Bypass -File .\scripts\ai-loop\run-next-ai-loop-request.ps1 -Once` without `-DryRun`.
5. Do not consume `0007` as dry-run; it explicitly requires a real worker run.
6. Keep visual/HTML viewer work text-only unless the user explicitly asks for an HTML viewer.

Product decision carried forward:

- `Project` and `Member` are peer resources.
- A project admin grants a member project-specific access.
- One member can belong to multiple projects with different roles.
- Company information is excluded from this slice.
- The relationship model is `ProjectMemberAccess`.

Implementation-plan clarification:

- For the add-existing-member modal, prefer showing all mock members and validating duplicate access on submit.
- This preserves the duplicate-validation behavior required by the plan and avoids hiding the test path behind disabled options.

Verification to rerun after AI loop mode-dispatch changes or any code/docs changes:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\ai-loop\test-ai-loop-hook.ps1
npm test
npm run build
```

Browser/dev-server verification is not complete for Project Admin Task 6.

## Current Product Baseline

Implemented slice:

- ACC #6 project list
- ACC #1 project creation modal

Current app baseline:

- Vite + React + TypeScript + Vitest app scaffold exists.
- `src/App.tsx` implements a local mock project list and creation modal.
- `src/App.test.tsx` covers list structure, search, modal fields, required-name validation, valid create, cancel, and close no-change behavior.
- Local mock data is not persistent.
- Filter/settings/pagination are layout affordances only in the first slice.
- No DB/API/Auth/Autodesk cloud/paid SDK/customer drawing/deployment/CAD editor work has been introduced.

## AI Loop Runner Boundary

- The current `.ai-loop` runner uses explicit mode dispatch.
- It is an external PowerShell runner around `codex exec`; it is not a full automatic development loop.
- Supported modes:
  - `review-only`: `baseline-review.md`, `read-only`
  - `validation-evidence`: `validation-evidence.md`, `workspace-write`
  - `implementation`: `implementation.md`, `workspace-write`
- `validation-evidence` is for verification/evidence/handoff work such as Project Admin Task 6. Implementation code edits are blocked by default.
- `implementation` requires explicit owned files, blocked boundaries, and verification commands in the request.
- Unknown modes fail before worker launch with `Unsupported mode`.
- Keep `.ai-loop` runtime requests/results/logs/locks out of commits.

One-shot runner command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\ai-loop\run-next-ai-loop-request.ps1 -Once
```

Pending real-run request:

```text
.ai-loop/control/inbox/0007-project-admin-task6-validation-evidence-real-run.request.md
```

Do not use `-DryRun` for 0007. The earlier 0006 request was consumed as dry-run and does not count as validation evidence.

## Human Gate

Before using real Autodesk accounts, paid SDKs, customer drawings, auth, permissions, DB schema, deployment, or destructive data changes, stop and ask.
