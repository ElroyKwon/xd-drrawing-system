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

## UI-PA-001 Project Admin Member Access

### Screen

| ID | Screen | Source evidence |
|---|---|---|
| UI-PA-001 | Project Admin 구성원 access view for `Study_Project` | ACC #2 `ScreenShot Tool -20260612102437.png`; ACC #3 `Video Screen1781227558018.png` |

### Layout

- Project/Admin context shows `Project Admin` and `Study_Project`.
- Left rail shows Project Admin navigation with `구성원` selected.
- Any `회사` rail label is only non-selected navigation context; company information and company management are excluded from this slice.
- Main panel heading is `구성원`.
- Main action is `구성원 추가`.
- Toolbar contains `내보내기`, search, filter affordance, and column/settings affordance.
- Member access table columns are `이름`, `이메일`, `전화`, `상태`, `역할`, `추가된 일시`.
- Right inspector shows selected member identity and project-specific role/status.

### Fields

| Field | Display | Requirement |
|---|---|---|
| projectName | `Study_Project` context label | FR-PA-001 |
| name | Member name | FR-PA-002, FR-PA-003, FR-PA-004 |
| email | Member email | FR-PA-002, FR-PA-003, FR-PA-004 |
| phone | Member phone | FR-PA-002, FR-PA-004 |
| status | Project access status, e.g. `활성`, `대기` | FR-PA-002, FR-PA-004 |
| role | Project-specific role, one of `관리자`, `편집자`, `뷰어` | FR-PA-004, FR-PA-008 |
| addedAt | Project access added date/time | FR-PA-002 |

### Actions

| Action | Result | Requirement | User-flow step |
|---|---|---|---|
| Enter Project Admin from `Study_Project` | Opens Project Admin member access view | FR-PA-001 | UF-PA-001 |
| Search by name/email | Filters project-access member rows | FR-PA-003 | UF-PA-003 |
| Clear search | Restores current project access rows | FR-PA-003 | UF-PA-004 |
| Select member row | Updates right inspector | FR-PA-004 | UF-PA-005 |
| Click `구성원 추가` | Opens add-existing-member modal | FR-PA-005 | UF-PA-006 |
| Submit with no member | Shows `구성원을 선택하세요.` and keeps modal open | FR-PA-006 | UF-PA-008 |
| Submit duplicate member | Shows `이미 이 프로젝트에 추가된 구성원입니다.` and keeps modal open | FR-PA-007 | UF-PA-009 |
| Submit valid member + role | Adds one local access row and closes modal | FR-PA-008 | UF-PA-010 |
| Cancel/close add modal | Closes modal without data mutation | FR-PA-005 | UF-PA-012 |

### Add Existing Member Modal

- Title: `구성원 추가`.
- Fields: existing member selector and role selector.
- Role choices: `관리자`, `편집자`, `뷰어`.
- Buttons: `취소`, `추가`, close icon.
- Validation messages must be exactly:
  - `구성원을 선택하세요.`
  - `이미 이 프로젝트에 추가된 구성원입니다.`

### Project Admin States

- Empty selection validation: Add submit is blocked until a member is chosen.
- Duplicate validation: Same `projectId` + `memberId` cannot be added twice.
- Empty search result: show stable table shell or compact empty row without mutating state.
- Server error: Not required because this slice has no backend.
- Company scope: no company fields, company details, or company management actions are shown; this covers FR-PA-009.

## UI-BS-001 Build Shell And Sheets List

### Screen

| ID | Screen | Source evidence |
|---|---|---|
| UI-BS-001 | Build shell with `시트` list for `Study_Project` | ACC #8 `Video Screen1781231464329.png`; ACC #10 `Video Screen1781231492911.png` |

### Layout

- Top Build header shows module label `Build`, project context `Study_Project`, trial/banner affordance, help, and user menu.
- Left rail shows `홈`, `시트`, `파일`, `이슈`, `양식`, `사진`; bottom items show `구성원`, `브리지`, `설정`.
- `시트` is selected.
- Main content title is `시트`.
- Toolbar contains `내보내기`, search/filter control, list/grid view toggle.
- Table columns show checkbox, thumbnail/number/title group, version chip, version set, discipline, tag, last updater, and row menu.
- Footer shows item count and pagination affordance.

### Fields

| Field | Display | Requirement |
|---|---|---|
| projectName | `Study_Project` context label | FR-BS-001, FR-BS-002 |
| sheetThumbnail | small drawing-preview placeholder | FR-BS-004 |
| number | sheet number such as `A001` | FR-BS-003, FR-BS-004, FR-BS-005 |
| title | sheet title under number | FR-BS-004, FR-BS-005 |
| version | compact version chip such as `1` | FR-BS-004 |
| versionSet | `Addendum 1` | FR-BS-004 |
| disciplineLabel | `A (건축)`, `E (전기)`, `M (기계)`, `P (배관)` | FR-BS-004, FR-BS-005 |
| tag | `architectural`, `electrical`, `mechanical`, `plumbing` | FR-BS-004, FR-BS-005 |
| lastUpdatedBy | local mock updater display | FR-BS-004 |

### Actions

| Action | Result | Requirement | User-flow step |
|---|---|---|---|
| Enter Build from `Study_Project` | Opens Build sheets view | FR-BS-001 | UF-BS-001 |
| Click `시트` rail item | Keeps sheets list selected | FR-BS-002 | UF-BS-002 |
| Search by number/title/discipline/tag | Filters local mock sheets | FR-BS-005 | UF-BS-003 |
| Clear search | Restores all local mock sheets | FR-BS-005 | UF-BS-004 |
| Toggle list/grid | Updates selected view affordance; table remains functional list | FR-BS-006 | UF-BS-005 |
| Click export/filter/row menu/pagination | No data mutation; local affordance only | FR-BS-007 | UF-BS-006 |
| Back to project list | Returns to hub project list | FR-BS-001 | UF-BS-007 |

### Build Sheets States

- Empty search result: keep the table shell and show a compact empty row.
- Loading: not required because data is local mock state.
- Server error: not required because this slice has no backend.
- Viewer state: not required; selecting a sheet does not open a 2D viewer in this slice.
- Responsive: desktop shows full shell/table; narrow widths keep rail usable and table horizontally scrollable without clipped labels.

## UI-SV-001 2D Sheet Viewer First Slice

### Screen

| ID | Screen | Source evidence |
|---|---|---|
| UI-SV-001 | 2D sheet viewer shell for selected local sheet | ACC #11 `Video Screen1781231512247.png`; ACC #12/#13 markup panel; ACC #16 issues panel |

### Layout

- Viewer opens from the Build `시트` list for a selected local mock sheet.
- Top context shows project name, sheet number, sheet title, and a return-to-sheets action.
- Central canvas area shows a static sheet render surface, not a parsed drawing file.
- Right vertical tool rail shows select, move, text, shape, pen, measurement, stamp, and color affordances.
- Bottom center controls show pan, fit, zoom out/in, fullscreen, compare, and measure affordances.
- Left panel can switch between `마크업` and `이슈`; both show empty states in this first slice.
- Optional bottom filmstrip shows local sheet navigation context without loading external assets.

### Fields

| Field | Display | Requirement |
|---|---|---|
| projectName | `Study_Project` context label | FR-SV-001, FR-SV-002 |
| sheetNumber | selected sheet number such as `A001` | FR-SV-002 |
| sheetTitle | selected sheet title | FR-SV-002 |
| staticSheetRender | local static sheet render surface | FR-SV-003 |
| selectedTool | active right-rail tool state | FR-SV-004 |
| zoomLevel | local zoom/fit affordance label or state | FR-SV-005 |
| panelTab | `마크업` or `이슈` | FR-SV-006 |
| equipmentEntityIdSlot | reserved hidden/local data slot | FR-SV-008 |

### Actions

| Action | Result | Requirement | User-flow step |
|---|---|---|---|
| Open selected sheet | Shows viewer shell for that local sheet | FR-SV-001 | UF-SV-001 |
| Return to sheets list | Returns to Build `시트` list | FR-SV-001 | UF-SV-007 |
| Select a right-rail tool | Updates selected local affordance only | FR-SV-004 | UF-SV-003 |
| Use bottom controls | Updates local affordance state only | FR-SV-005 | UF-SV-004 |
| Switch markup/issues tab | Shows the selected empty panel state | FR-SV-006 | UF-SV-005 |
| Select sheet from filmstrip | Changes selected local sheet if implemented | FR-SV-007 | UF-SV-006 |

### Viewer States

- Empty markup panel: show no saved markups and a non-persistent prompt to use tools later.
- Empty issues panel: show no issue pins/list because issue creation is out of scope.
- Loading: not required because the static sheet render is local.
- Server error: not required because no backend exists.
- Engine unavailable: not applicable because no real viewer engine is used.
- Integration boundary: `FR-SV-009` keeps real viewer engine adoption, customer drawings, upload/publish, persisted markup/issues, DB/API/TypeDB, Autodesk, paid SDK, auth/RBAC, CAD editor behavior, and deployment outside this UI slice.
- Responsive: desktop prioritizes full viewer layout; narrow widths keep context, static sheet surface, and essential controls reachable without overlapping text.

## UI-DUC-001 DWG/DXF Upload Conversion Management

### Screen

| ID | Screen | Source evidence |
|---|---|---|
| UI-DUC-001 | Drawing upload/conversion management queue | Local DWG/DXF experiment; APS Simple Viewer upload/status pattern |

### Layout

- Screen is a management work surface, not a marketing/landing page.
- Header shows project context `Study_Project`, module context `시트`, and a planning badge such as `DUC`.
- Primary area contains an intake queue table with source file name, discipline, size, xref policy, validation status, conversion status, scan status, and render-risk status.
- Secondary detail panel shows selected job details: input DWG count, output DXF count, layouts, layer/block/entity counts, top INSERT names, text samples, and messages.
- A future artifact section shows derived artifacts such as DXF and scan JSON as metadata rows only; no real repository storage is implied.
- Viewer integration section shows future relation to Build `Sheet` and ACC #11 viewer without opening a real drawing file.
- Issue/memo/markup overlay section is a reserved future slot only.

### Fields

| Field | Display | Requirement |
|---|---|---|
| sourceName | DWG/DXF source file name | FR-DUC-001, FR-DUC-002 |
| discipline | Architecture/electrical/communication/etc. | FR-DUC-002 |
| fileSize | Size in bytes or MB | FR-DUC-002 |
| xrefPolicy | `folder-copied`, `nearby-xr-files`, `missing`, or `none` | FR-DUC-002 |
| conversionStatus | queued/converting/converted/scanned/failed/render-risk | FR-DUC-003, FR-DUC-006 |
| inputDwgCount | Count of staged DWG files | FR-DUC-003 |
| outputDxfCount | Count of converted DXF files | FR-DUC-003 |
| layouts | DXF layout names and entity counts | FR-DUC-004, FR-DUC-005 |
| entitySummary | top entity types, INSERT names, text samples | FR-DUC-004 |
| viewableCandidate | layout/modelspace/title/manual candidate label | FR-DUC-005, FR-DUC-007 |
| jsonTraceability | future JSON progress/traceability artifact preview | FR-DUC-010 |

### Actions

| Action | Result | Requirement | User-flow step |
|---|---|---|---|
| Add local sample candidate | Adds a local/reference sample row in planning UI only | FR-DUC-001 | UF-DUC-001 |
| Validate sample | Updates validation metadata and xref policy | FR-DUC-002 | UF-DUC-002 |
| Start conversion job | Creates a queued/converting job in future implementation | FR-DUC-003 | UF-DUC-003 |
| Scan DXF summary | Populates scan summary fields | FR-DUC-004 | UF-DUC-004 |
| Review sheet/viewable candidates | Shows candidate rows without requiring viewer render | FR-DUC-005 | UF-DUC-005 |
| Mark render risk | Keeps rendering separate from conversion/scanning | FR-DUC-006 | UF-DUC-006 |
| Link future sheet/viewer target | Reserves relation to Build `Sheet` and ACC #11 viewer | FR-DUC-007 | UF-DUC-007 |
| Review overlay slots | Shows future issue/memo/markup overlay slots only | FR-DUC-008 | UF-DUC-008 |
| Review APS/DevTools notes | Opens documentation/research notes, not credentials | FR-DUC-009 | UF-DUC-009 |
| Export/inspect JSON proposal | Shows future traceability shape only | FR-DUC-010 | UF-DUC-010 |

### DUC States

- Empty: no drawing candidates selected.
- Validated: metadata is known and conversion can be queued in a future implementation.
- Blocked: missing xrefs, unsupported file, or gated scope.
- Converted: DXF artifact exists in an approved local/scratch context.
- Scanned: scan summary exists.
- Render-risk: conversion/scan succeeded but visual rendering is slow, incomplete, or unverified.
- HUMAN_GATE: real APS, paid SDK adoption, customer drawing upload/storage, DB/API/TypeDB, auth/RBAC, deployment, and token capture are not allowed without approval.
