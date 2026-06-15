# Next Session

## Start Here

```powershell
cd "D:\_Project\xd-drawing-system"
codex
```

Read in order:

1. `AGENTS.md`
2. `README.md`
3. `SPEC.md`
4. `PLAN.md`
5. `CHECKS.md`
6. `HUMAN_GATE.md`
7. `reference/README.md`

## Current State

Project setup is complete. No application code exists yet.

User's long-term goal is not just to create a skill collection. The goal is to build and test a low-intervention AI development loop where one main orchestrator can drive sub-skills for design, planning gate, implementation, validation, evidence, and iteration.

Goal anchor:

```text
G:\내 드라이브\_Obsidian\지식관리\AI개발루프-스킬학습\_GOAL-ANCHOR.md
```

The project contains:

- ACC Build screenshots and screen analysis
- DKS drawing-management design documents
- Autodesk Cloud / APS research
- Cheongju FMS reference material
- Previous prototype documentation and data
- AI development loop templates and local skills

## Recommended First Work

Next work: 스킬 보강 후 초기 설정 slice 재진입.

Do not start implementation yet.

The selected first slice is limited to:

1. ACC #1 `프로젝트 작성 모달`
2. ACC #6 `프로젝트 목록`

Current planning status:

- `docs/feature-notes/001-initial-setup.md` exists.
- `SPEC.md`, `PLAN.md`, and `CHECKS.md` were updated for this slice.
- The planning-gate result is only a feature-note-based temporary pass.
- It has not yet satisfied the original AI development loop's seven-document standard.

Recommended next steps:

1. Run `development-loop-orchestrator` against the current project files.
2. Run `feature-docs-scaffold` for the initial setup slice.
3. Create or update the seven core docs:
   - `docs/PRD.md`
   - `docs/TRD.md`
   - `docs/UI_Spec.md`
   - `docs/Data_Model.md`
   - `docs/Task_List.md`
   - `docs/Acceptance_Criteria.md`
   - `docs/Test_Scenarios.md`
4. Run the enhanced `planning-gate`.
5. Only then decide whether to scaffold app code.

Local skills now expected:

- `project-bootstrap`
- `feature-docs-scaffold`
- `planning-gate`
- `development-loop-orchestrator`
- `validator-loop`
- `evidence-report`
- `tag-alarm-review`

Local skill path status:

- `.agents/skills/<skill>/SKILL.md` and `.claude/skills/<skill>/SKILL.md` were refreshed from the AI loop package on 2026-06-15.
- Duplicate nested skill directories were removed.
- `planning-gate` now includes `SLICE-ONLY PASS` at the top-level local skill path.

## Key Product Boundary

This is not a CAD editor.

The first product direction is:

- project setup
- members/companies/roles
- sheets
- 2D viewer
- markup overlay
- issue pins and inspector
- future entity ID binding

## Human Gate

Before using real Autodesk accounts, paid SDKs, customer drawings, auth, permissions, DB schema, or deployment, stop and ask.
