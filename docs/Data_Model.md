# Data Model

## Entities

```text
Project
- id: string
- typeIcon: string
- name: string
- number: string
- projectType: string
- templateId: string | null
- address: string
- manualAddress: boolean
- timezone: string
- startDate: string | null
- endDate: string | null
- projectValue: string
- currency: string
- defaultAccess: string
- hub: string
- createdAt: string
```

## Required Fields

| Field | Required for create? | Used in list? | Notes |
|---|---:|---:|---|
| id | Yes | Yes | Generated locally in implementation. |
| name | Yes | Yes | Required validation field. |
| number | No | Yes | Search target when provided. |
| typeIcon | No | Yes | Can use a default project icon. |
| projectType | No | No | Modal metadata only in this slice. |
| templateId | No | No | Template management is out of scope. |
| address | No | Optional | Can appear as secondary text under name. |
| manualAddress | No | No | Supports modal affordance. |
| timezone | No | No | Default `서울`. |
| startDate | No | No | Stored as local string if entered. |
| endDate | No | No | Stored as local string if entered. |
| projectValue | No | No | Stored as local string if entered. |
| currency | No | No | Default `USD`. |
| defaultAccess | No | Yes | Default `Build`. |
| hub | No | Yes | Default mock hub such as `TEST-`. |
| createdAt | Yes | Yes | Generated locally at create time. |

## CRUD Expectations

| Operation | Required? | Notes |
|---|---:|---|
| Create | Yes | Valid modal submit appends one local mock `Project`. |
| Read | Yes | Project list renders local mock projects and created projects. |
| Update | No | No edit screen or inline edit in this slice. |
| Delete | No | No destructive action in this slice. |
| Undo | No | Cancel/close is a no-change flow, not an undo flow. |

## Search Expectations

- Search target fields: `name`, `number`.
- Search is local and case-insensitive when implementation language permits.
- Clearing search restores the full local mock list.
- Empty result displays an empty state without mutating data.

## Persistence Boundary

- Data is local mock state only.
- No DB schema is introduced.
- No API contract is introduced.
- No customer data is used.
- No Autodesk cloud data is read or written.

## Requirement Mapping

| Requirement ID | Data support |
|---|---|
| FR-IS-001 | `Project` list display fields. |
| FR-IS-002 | `name`, `number` search fields. |
| FR-IS-003 | Modal visibility state; no persistent entity. |
| FR-IS-004 | Modal metadata fields in `Project`. |
| FR-IS-005 | `name` required validation. |
| FR-IS-006 | Local create append operation. |
| FR-IS-007 | No mutation on cancel/close. |
| FR-IS-008 | Data does not drive layout overflow; long text must be handled by UI. |
| FR-IS-009 | Local-only persistence boundary. |
