---
name: planning-gate
description: Use before implementation when a feature, product slice, UI screen, PRD, technical plan, data model, task list, acceptance criteria, or test scenario is being reviewed, especially before coding or when a prior gate gave a temporary pass.
---

# Planning Gate

## Purpose

Prevent implementation from starting while the plan, requirements, UI, data model, tasks, and tests are inconsistent.

This gate must distinguish a real document loop pass from a thin-slice temporary pass. A feature note can help, but it does not replace the design-document set unless the exception is explicit.

## Required Inputs

Look for these files first:

- `SPEC.md`
- `PLAN.md`
- `CHECKS.md`
- `HUMAN_GATE.md`
- `docs/PRD.md`
- `docs/TRD.md`
- `docs/UI_Spec.md`
- `docs/Data_Model.md`
- `docs/Task_List.md`
- `docs/Acceptance_Criteria.md`
- `docs/Test_Scenarios.md`

Recommended when UI or multi-step workflow exists:

- `docs/Design_Map.md`
- `docs/User_Flow.md`
- `docs/Planning_Gate_Checklist.md`

Use the files that exist. Report missing files.

If the 7 core design documents are missing, the default result is `FAIL`. The only exception is a deliberately accepted thin slice, which must be reported as `SLICE-ONLY PASS`, not `PASS`.

## Checks

1. The 7 core design documents exist or the report explicitly qualifies the result as `SLICE-ONLY PASS`.
2. Every PRD feature maps to at least one task in `Task_List.md`.
3. Every PRD feature maps to at least one acceptance criterion in `Acceptance_Criteria.md`.
4. Every PRD feature maps to at least one test or manual scenario in `Test_Scenarios.md`.
5. Every visible UI action maps to a user-flow step when `User_Flow.md` exists or UI is in scope.
6. Every visible UI field/action is represented in `UI_Spec.md`.
7. The data model supports create, read, update, delete, and undo flows when required.
8. Completion criteria are pass/fail, not vague.
9. Risky items are listed in `HUMAN_GATE.md`.
10. Any omitted document has a written reason and replacement location.

## Thin Slice Exception

Use `SLICE-ONLY PASS` only when all of these are true:

- the user explicitly accepts a small experiment or temporary slice
- no authentication, authorization, database schema, external API, paid SDK, customer data, or deployment is involved
- missing documents are listed by name
- replacement documents are listed by path
- the report says implementation may proceed only for that narrow slice

Do not use normal `PASS` for a thin slice.

## Output

```text
Planning Gate Result: PASS/SLICE-ONLY PASS/FAIL

Missing files:
Temporary-slice status:
Documents used as replacements:
Feature-to-task gaps:
Feature-to-acceptance gaps:
Feature-to-test gaps:
UI/user-flow gaps:
UI/spec gaps:
Data model gaps:
Ambiguous completion criteria:
Human approval items:
Required fixes before implementation:
```

## Rule

If the result is `FAIL`, do not start implementation. Explain what must be fixed first.

If the result is `SLICE-ONLY PASS`, state the exact slice boundary and warn that this is not a full loop pass.

If the feature is more than a very small experiment and the core documents are missing, recommend running `feature-docs-scaffold` before this gate.
