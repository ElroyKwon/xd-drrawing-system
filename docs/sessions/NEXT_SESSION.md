# Next Session

## Start Here

```powershell
cd "D:\_Project\xd-drawing-system"
codex
```

Read in order:

1. `AGENTS.md`
2. `docs/sessions/NEXT_SESSION.md`
3. `EVIDENCE.md`
4. `PLAN.md`
5. `CHECKS.md`
6. `HUMAN_GATE.md`
7. `docs/feature-notes/003-build-shell-sheets-list.md`
8. `docs/superpowers/plans/2026-06-18-build-shell-sheets-list.md`

## Immediate Resume - 2026-06-18 Build Shell And Sheets List Implemented

Current repository state at this handoff:

- Branch: `master`.
- Build shell + Sheets list slice is implemented locally and verified.
- Commit-ready review has been completed; see `EVIDENCE.md` section `Commit-Ready Review - Build Shell And Sheets List - 2026-06-18`.
- Changes are not committed.
- The dev server was used at `http://127.0.0.1:5173/` and then stopped during closeout.
- Project Admin Task 6 remains open as a separate browser-evidence blocker; it was not rerun as `0009` and was not marked PASS.
- `AGENTS.md` now includes an explicit `세션 종료 절차` section so Codex-side closeout expectations match the project handoff workflow.

Build slice scope:

- `Study_Project` has a local `Build 열기` path from the project list.
- The Build shell renders project context, left rail, and `시트` selected.
- Sheets list uses local mock rows only.
- Search filters by sheet number/title/discipline/tag.
- Grid/list toggle is an affordance; list remains the functional view.
- No 2D viewer, upload/publish, auth/RBAC, DB/API, Autodesk API, paid SDK, customer drawing, or deployment work was introduced.

Fresh verification:

- Commit-ready review rerun:
  - `npm test`: PASS, 5 test files / 24 tests passed.
  - `npm run build`: PASS, `tsc && vite build` completed.
  - `git diff --check`: PASS.
- Earlier closeout verification:
  - `powershell -ExecutionPolicy Bypass -File .\scripts\ai-loop\test-ai-loop-hook.ps1`: PASS.
- Chrome DevTools MCP browser check: PASS for the Build slice only.
- Desktop screenshot: `docs/evidence/build-sheets-desktop.jpeg`.
- Narrow screenshot: `docs/evidence/build-sheets-narrow.jpeg`.
- Console: only Vite dev-server debug logs and React DevTools info; no app errors/warnings/issues observed.

Files to review before commit:

- `AGENTS.md`
- `src/buildSheetsData.ts`
- `src/buildSheetsData.test.ts`
- `src/BuildSheetsView.tsx`
- `src/BuildSheetsView.test.tsx`
- `src/App.tsx`
- `src/App.test.tsx`
- `src/styles.css`
- `docs/evidence/build-sheets-desktop.jpeg`
- `docs/evidence/build-sheets-narrow.jpeg`
- Build slice docs and evidence updates listed in `EVIDENCE.md`.

Exact next action:

1. Run `git status --short --untracked-files=all`.
2. Review `EVIDENCE.md` section `Commit-Ready Review - Build Shell And Sheets List - 2026-06-18`.
3. Decide and apply commit split:
   - ai-loop reinforcement changes
   - Project Admin Task 6 blocker handoff
   - Build shell + Sheets list implementation/docs/evidence
   - `AGENTS.md` closeout-procedure supplement, either with docs/handoff or as its own small docs commit
4. If accepted, stage and commit the chosen groups.
5. Do not claim Project Admin Task 6 PASS. Resolve that as a separate browser-path blocker item before rerunning the Project Admin browser validation.

## Carry-Forward Blocker - 2026-06-17 Project Admin Task 6 Browser Validation Blocked

Current repository state at this handoff:

- Branch: `master`
- First product slice is implemented, verified, and committed.
- Project Admin member-access implementation commits exist through opening Project Admin from the project list.
- The `.ai-loop` runner mode-dispatch changes are committed at `a7125c0`.
- Project Admin Task 6 validation has two blocked browser evidence attempts recorded in `EVIDENCE.md`: `0007` and `0008`.
- Automated command checks passed, but browser validation is blocked.

Fresh validation evidence from the latest blocked Task 6 rerun:

- `git status --short --untracked-files=all`: OBSERVED an already-dirty allowed evidence/handoff state:
  - `M EVIDENCE.md`
  - `M docs/sessions/NEXT_SESSION.md`
- `npm test`: PASS, 3 test files / 16 tests passed.
- `npm run build`: PASS, `tsc && vite build` completed.
- `powershell -ExecutionPolicy Bypass -File .\scripts\ai-loop\test-ai-loop-hook.ps1`: PASS.

Browser validation status from the latest rerun:

- Result: `BLOCKED_BROWSER_UNAVAILABLE`.
- Target URL was `http://127.0.0.1:5173/`.
- Required viewports were desktop `1440x900` and narrow `390x844`.
- Chrome DevTools MCP reported the `chrome-devtools-mcp\chrome-profile` browser was already running, then page actions returned `user cancelled MCP tool call`.
- PowerShell Chrome remote-debugging fallback was rejected by policy before execution.
- Node REPL fallback failed with `windows sandbox failed: spawn setup refresh`.
- Process inspection with `Get-CimInstance Win32_Process` failed with access denied.
- No fresh Project Admin browser screenshots were created in the blocked run.
- `docs/evidence/project-admin-task6-desktop.png` and `docs/evidence/project-admin-task6-narrow.png` were not created or reused.

The next session should continue Task 6 by resolving the browser automation blocker first, not by creating another identical validation rerun.

First actions:

1. Run `git status --short --untracked-files=all`.
2. Read `EVIDENCE.md` section `Project Admin Task 6 Browser Validation Rerun - 2026-06-17`.
3. Do not create `0009` as another `Task 6 validation` request unless a changed browser automation precondition is documented first.
4. Draft the next request as browser automation path blocker-resolution: restore or choose a page-level automation path, keep product `src/` edits blocked unless separately owned, and define the proof that the precondition changed.
5. After the blocker-resolution request proves a working page-level path, re-run the Task 6 browser checks for Project List -> `Study_Project` -> Project Admin, search, selection, add modal empty/duplicate/valid add, console state, desktop screenshot, and narrow screenshot.
6. Record fresh screenshot paths before claiming Project Admin Task 6 PASS.
7. Keep visual/HTML viewer work text-only unless the user explicitly asks for an HTML viewer.

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

Implemented slices:

- ACC #6 project list
- ACC #1 project creation modal
- Build shell + Sheets list for `Study_Project`

Current app baseline:

- Vite + React + TypeScript + Vitest app scaffold exists.
- `src/App.tsx` implements a local mock project list and creation modal.
- `src/App.test.tsx` covers list structure, search, modal fields, required-name validation, valid create, cancel, and close no-change behavior.
- `src/BuildSheetsView.tsx` implements the local mock Build shell and Sheets list.
- `src/buildSheetsData.ts` contains local mock sheet rows and filter helper logic.
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

Recent real-run validation requests:

```text
0007-project-admin-task6-validation-evidence-real-run: BLOCKED_BROWSER_UNAVAILABLE
0008-project-admin-task6-browser-validation-rerun: BLOCKED_BROWSER_UNAVAILABLE
```

Do not create another same-path validation request under the same preconditions. The next request should resolve or change the blocked browser automation path; Task 6 validation can run again only after that changed precondition is recorded.

## Human Gate

Before using real Autodesk accounts, paid SDKs, customer drawings, auth, permissions, DB schema, deployment, or destructive data changes, stop and ask.
