# Project Checks

## Setup Checks

```powershell
Test-Path -LiteralPath "D:\_Project\xd-drawing-system"
Test-Path -LiteralPath "D:\_Project\xd-drawing-system\reference\acc-screenshots\_ACC-Build-화면분석-재현설계.md"
Test-Path -LiteralPath "D:\_Project\xd-drawing-system\reference\dks-design-docs\도면관리시스템_상세설계\00_개요-PMO\README.md"
Test-Path -LiteralPath "D:\_Project\xd-drawing-system\.agents\skills\project-bootstrap\SKILL.md"
Get-ChildItem -File -LiteralPath "D:\_Project\xd-drawing-system\reference\acc-screenshots" | Measure-Object
Get-ChildItem -Recurse -File -LiteralPath "D:\_Project\xd-drawing-system\reference\dks-design-docs\도면관리시스템_상세설계" | Measure-Object
```

## Future App Checks

These commands are placeholders for the first app implementation. Do not claim them as passing until a package exists.

```powershell
npm install
npm run build
npm test
```

## Manual Checks For UI Work

- Compare implemented screen against the matching files in `reference/acc-screenshots/`.
- Check that button text and labels fit on desktop and mobile widths.
- Check browser console errors.
- Record screenshot evidence when a UI slice is implemented.

## Manual Checks For Initial Setup Slice

Reference screenshots:

- `reference/acc-screenshots/ScreenShot Tool -20260612102152.png`
- `reference/acc-screenshots/Video Screen1781231401038.png`

Pass/fail checks:

- Project list screen shows the ACC #6 structure: hub header, `프로젝트` tab, `+ 프로젝트 만들기`, project table, search box, filter affordance, column/settings affordance, and pagination.
- Project table includes at least these columns: 유형, 이름, 번호, 기본 액세스, 허브, 작성 날짜.
- Search filters mock projects by project name or project number and can return to the full list when cleared.
- `+ 프로젝트 만들기` opens a centered `프로젝트 작성` modal over the project list.
- Modal contains the ACC #1 fields: 프로젝트 이름, 프로젝트 번호, 프로젝트 유형, 템플릿, 주소, 시간대, 시작일, 종료일, 프로젝트 값, 통화.
- Submitting with an empty 프로젝트 이름 shows a required-field validation state and does not add a project.
- Submitting with a valid 프로젝트 이름 adds one local mock project row and closes the modal.
- `취소` and close dismiss the modal without adding a project.
- No external Autodesk account, API, paid SDK, database, customer drawing, or deployment action is required.
- Browser console has no errors during open, validation, create, cancel, search, and close flows.
- Desktop and mobile widths do not show overlapping text, clipped button labels, or broken modal layout.
