# User Flow

## Primary Flow

1. `UF-IS-001` User opens the hub-level project list.
2. `UF-IS-002` User reviews existing local mock projects, table columns, default access, and pagination affordance.
3. `UF-IS-003` User enters a project name or project number in the search input.
4. `UF-IS-004` User clears the search and sees the full local mock list again.
5. `UF-IS-005` User clicks `+ 프로젝트 만들기`.
6. `UF-IS-006` System opens the centered `프로젝트 작성` modal over the list.
7. `UF-IS-008` User enters a project name and optional metadata.
8. `UF-IS-009` User clicks `프로젝트 작성`.
9. `UF-IS-010` System adds one local mock project to the list and closes the modal.

## Validation Flow

1. `UF-IS-005` User clicks `+ 프로젝트 만들기`.
2. `UF-IS-006` System opens the centered `프로젝트 작성` modal.
3. `UF-IS-007` User clicks `프로젝트 작성` while project name is empty.
4. System shows required-field validation, keeps the modal open, and does not add a project.
5. User enters a valid project name and submits again.
6. System follows `UF-IS-010`.

## Cancel / No-Change Flow

1. `UF-IS-005` User clicks `+ 프로젝트 만들기`.
2. `UF-IS-006` System opens the centered `프로젝트 작성` modal.
3. `UF-IS-012` User clicks `취소`.
4. System closes the modal and leaves the project list count unchanged.
5. User reopens the modal.
6. `UF-IS-013` User clicks the close button.
7. System closes the modal and leaves the project list count unchanged.

## Out Of Scope Flows

- User does not log in.
- User does not manage project members, companies, roles, or permissions.
- User does not manage templates beyond selecting a visible modal option.
- User does not enter the Build module, sheets list, 2D viewer, markup, issue, file, or photo screens.
- User does not upload, view, edit, or delete customer drawings.
- User does not sync with Autodesk cloud or any external API.
