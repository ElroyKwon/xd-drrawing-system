# Design Map

## Source Evidence

| Evidence | Used for |
|---|---|
| `reference/acc-screenshots/ScreenShot Tool -20260612102152.png` | Project creation modal layout, labels, field order, required mark, footer buttons. |
| `reference/acc-screenshots/Video Screen1781231401038.png` | Project list screen, tab structure, create CTA, table columns, search/filter/settings/pagination. |
| `reference/acc-analysis/_ACC-Build-화면분석-재현설계.md` #1 | Modal field inventory and reproduction notes. |
| `reference/acc-analysis/_ACC-Build-화면분석-재현설계.md` #6 | Project list component inventory and reproduction notes. |
| `docs/feature-notes/001-initial-setup.md` | Slice boundary, user flow, local mock model. |
| `HUMAN_GATE.md` | External integration and risky-change boundaries. |

## Feature To UI Map

| Requirement ID | UI element | User action |
|---|---|---|
| FR-IS-001 | Project tab, project table, default access cell, pagination | User reviews existing projects. |
| FR-IS-002 | Search input | User searches by project name or number and clears search. |
| FR-IS-003 | `+ 프로젝트 만들기` CTA, modal overlay | User opens project creation. |
| FR-IS-004 | Modal form fields | User enters optional project metadata. |
| FR-IS-005 | Project name field validation | User attempts empty submit. |
| FR-IS-006 | Primary `프로젝트 작성` button | User creates a local mock project. |
| FR-IS-007 | `취소` and close button | User dismisses without changes. |
| FR-IS-008 | Responsive list/modal layout | User uses the flow at desktop and mobile widths. |
| FR-IS-009 | Local-only runtime boundary | User completes flow without external accounts or services. |

## ACC To XD Adaptation

- ACC visual hierarchy is the benchmark; XD naming and product context can replace Autodesk brand details during implementation.
- Autodesk cross-sell products shown in ACC screenshots are not functional requirements for this slice.
- `Build` as default access may remain as a benchmark label in mock data until XD module naming is decided.
- Template selection is represented only as a modal field; template management remains out of scope.
