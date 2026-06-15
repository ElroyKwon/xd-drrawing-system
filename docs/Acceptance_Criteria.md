# Acceptance Criteria

| AC ID | Requirement ID | Pass/fail criterion |
|---|---|---|
| AC-IS-001 | FR-IS-001 | PASS if the project list screen visibly includes the `프로젝트` tab, `+ 프로젝트 만들기`, project table, columns for 유형/이름/번호/기본 액세스/허브/작성 날짜, settings affordance, and pagination. FAIL if any required list structure is absent. |
| AC-IS-002 | FR-IS-002 | PASS if searching by an existing project name or number narrows the list and clearing the query restores all mock projects. FAIL if search mutates data or cannot restore the full list. |
| AC-IS-003 | FR-IS-003 | PASS if clicking `+ 프로젝트 만들기` opens a centered `프로젝트 작성` modal over the project list. FAIL if it navigates away or opens an unrelated screen. |
| AC-IS-004 | FR-IS-004 | PASS if the modal shows project name, project number, project type, template, address/manual-address affordance, timezone, start date, end date, project value, and currency fields. FAIL if any required field is missing. |
| AC-IS-005 | FR-IS-005 | PASS if submitting with an empty project name shows a required-field validation state, keeps the modal open, and does not add a project. FAIL if a project is created or the validation is invisible. |
| AC-IS-006 | FR-IS-006 | PASS if submitting with a valid project name adds exactly one local mock project row and closes the modal. FAIL if zero or multiple rows are added, or the modal remains open after successful create. |
| AC-IS-007 | FR-IS-007 | PASS if `취소` and close both dismiss the modal and leave the project list count unchanged. FAIL if either action creates, deletes, or changes a row. |
| AC-IS-008 | FR-IS-008 | PASS if desktop and mobile checks show no overlapping text, clipped button labels, broken modal layout, or browser console errors during open, validation, create, cancel, search, and close flows. FAIL if any listed issue appears. |
| AC-IS-009 | FR-IS-009 | PASS if the slice can run without auth, DB, API, Autodesk account, paid SDK, customer drawing, or deployment. FAIL if implementation requires any gated external dependency. |

## Human Approval Criteria

- PASS for planning only if all `HUMAN_GATE.md` risky items remain out of scope.
- FAIL or stop before implementation if a task introduces auth, permission, DB schema, customer data, Autodesk cloud/API, paid SDK, deletion of reference data, or deployment.
