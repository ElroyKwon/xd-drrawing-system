# UI Spec

## Screens

| ID | Screen | Source evidence |
|---|---|---|
| UI-IS-001 | 허브 레벨 프로젝트 목록 | ACC #6 `Video Screen1781231401038.png` |
| UI-IS-002 | 프로젝트 목록 위 중앙 프로젝트 작성 모달 | ACC #1 `ScreenShot Tool -20260612102152.png` |

## UI-IS-001 Project List

### Layout

- Top product/header band follows the ACC hub-level information hierarchy, adapted to XD product naming when implementation begins.
- Left/top context shows `Hub Admin`.
- Page greeting and tab row include `My Home`, `프로젝트`, `프로젝트 템플릿`; only `프로젝트` tab is active in this slice.
- Primary action `+ 프로젝트 만들기` appears above the project table.
- Search input and filter affordance are aligned to the table toolbar area.
- Table header includes type, name, number, default access, hub, created date, sort affordance, settings affordance.
- Bottom pagination shows visible item count and page controls.

### Components

- Hub header.
- Tab row.
- Primary create button.
- Search input.
- Filter icon button.
- Project table.
- Default access dropdown affordance.
- Sort indicator.
- Settings/column icon button.
- Pagination controls.

### Fields

| Field | Display | Requirement |
|---|---|---|
| typeIcon | Project type icon column | FR-IS-001 |
| name | Project name text, optional secondary address line | FR-IS-001, FR-IS-002 |
| number | Project number | FR-IS-001, FR-IS-002 |
| defaultAccess | Default module, initially `Build` | FR-IS-001 |
| hub | Hub code/name | FR-IS-001 |
| createdAt | Created date/time label | FR-IS-001 |

### Actions

| Action | Result | Requirement | User-flow step |
|---|---|---|---|
| Search by name/number | Filters local mock list | FR-IS-002 | UF-IS-003 |
| Clear search | Restores full local mock list | FR-IS-002 | UF-IS-004 |
| Click `+ 프로젝트 만들기` | Opens modal | FR-IS-003 | UF-IS-005 |
| Click filter affordance | No data mutation; may show inert affordance in this slice | FR-IS-001 | UF-IS-002 |
| Click settings affordance | No data mutation; may show inert affordance in this slice | FR-IS-001 | UF-IS-002 |
| Use pagination controls | Shows stable pagination affordance for mock list | FR-IS-001 | UF-IS-002 |

## UI-IS-002 Project Creation Modal

### Layout

- Modal is centered over a dimmed project list.
- Header contains `프로젝트 작성` title and close button.
- Body uses stacked fields with labels, required mark on `프로젝트 이름`, select affordances, date picker affordances, and two-column date/value groupings where width permits.
- Footer contains `취소` and primary `프로젝트 작성`.

### Fields

| Field | Type | Required | Notes | Requirement |
|---|---|---:|---|---|
| projectName | text | Yes | Required-field validation target | FR-IS-004, FR-IS-005 |
| projectNumber | text | No | Used by list search after create when supplied | FR-IS-004 |
| projectType | select | No | Default can be `지정되지 않음` | FR-IS-004 |
| templateId | select | No | Template management screen is out of scope | FR-IS-004 |
| address | text | No | Supports visible manual-address affordance | FR-IS-004 |
| manualAddress | affordance/toggle | No | Can be non-persistent in this slice | FR-IS-004 |
| timezone | select | No | Default can be `서울` | FR-IS-004 |
| startDate | date input | No | Placeholder `YYYY/MM/DD` | FR-IS-004 |
| endDate | date input | No | Placeholder `YYYY/MM/DD` | FR-IS-004 |
| projectValue | number/text | No | Currency amount | FR-IS-004 |
| currency | select | No | Default can be `USD` to match screenshot | FR-IS-004 |

### Actions

| Action | Result | Requirement | User-flow step |
|---|---|---|---|
| Submit empty name | Shows validation and keeps modal open | FR-IS-005 | UF-IS-007 |
| Submit valid name | Adds one local mock project and closes modal | FR-IS-006 | UF-IS-009, UF-IS-010 |
| Click `취소` | Closes modal without list mutation | FR-IS-007 | UF-IS-012 |
| Click close | Closes modal without list mutation | FR-IS-007 | UF-IS-013 |

## States

- Empty: If the filtered list has no results, show a compact empty state that does not replace the page shell.
- Loading: No async loading is required in this slice; if a future scaffold introduces loading, it must not block local mock rendering.
- Error: No server error state is required because no backend exists.
- Validation: Empty `projectName` blocks submit, highlights the field, and shows a clear required message.
- No-change: Cancel and close must preserve the list length and existing rows.

## Responsive Requirements

- Desktop: Table layout follows ACC #6 with horizontal space for all key columns.
- Tablet/mobile: Controls may stack, and the project table may become a horizontally scrollable table or compact list, but text must not overlap or clip.
- Modal: Width is constrained to viewport, body can scroll if height is insufficient, footer remains reachable.
- Buttons and labels must fit in Korean at supported widths.
