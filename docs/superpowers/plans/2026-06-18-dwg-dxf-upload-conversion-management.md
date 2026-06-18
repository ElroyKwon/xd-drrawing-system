# DWG/DXF Upload Conversion Management Plan

> **For agentic workers:** This is a planning and handoff document. It does not authorize implementation by itself.

## Goal

Prepare the next session to decide and execute the first safe slice toward Autodesk Cloud-like drawing upload:

```text
DWG intake -> validation -> conversion -> scan -> sheet/viewable candidate -> viewer/overlay integration
```

## Current Verified Facts

- Repository branch is `master`.
- Prior ACC #11 planning handoff is committed at `a927459 docs: record acc viewer planning handoff`.
- Local ODA File Converter is installed.
- Python has `ezdxf` and `fitz`.
- `D:\_Project\Data_Knowledge_Studio` currently has no DWG/DXF files by recursive search.
- Usable DWG samples live under `reference/old-prototypes/prototype-도면지식관리-mvp/dwg/`.
- Four representative DWG cases were copied to `%TEMP%` and converted to DXF.
- DXF scan metadata extraction is practical.
- DXF rendering quality/performance remains unproven and risky.

## Key Separation

Do not mix these tracks:

- `SV`: ACC #11 local-only viewer shell/static sheet render.
- `DUC`: DWG/DXF upload conversion management.
- `Task 6`: Project Admin browser evidence blocker, still `BLOCKED_BROWSER_UNAVAILABLE`.

## Candidate Next Implementation Paths

### Option A: ACC #11 Local Viewer Shell First

Use the existing implementation plan:

- `docs/superpowers/plans/2026-06-18-2d-sheet-viewer-implementation.md`

Best when the next goal is visual UX continuity: sheet list -> viewer -> panel/tool affordances.

### Option B: DUC Local Conversion-Lab Management UI First

Implement a local UI over mock conversion results:

- intake queue
- validation status
- conversion job status
- scan summary
- render-risk state
- future sheet/viewer relation
- no real conversion execution inside app

Best when the next goal is product workflow clarity without license/runtime risk.

### Option C: DUC Script Adapter First

Implement repo-owned scripts and tests for normalized conversion/scan output:

- no product UI
- no customer drawings
- output outside repo or ignored scratch only
- JSON summary generation for a selected sample

Best when the next goal is proving automation repeatability.

## Recommended Next Session Decision

Start with a formal DUC planning gate. Then choose Option B or Option C before implementing. Do not start with real APS/Autodesk integration.

Recommended first implementation if DUC is selected:

- Option B if the user wants product screens first.
- Option C if the user wants conversion reliability first.

## HUMAN_GATE Items

Stop before:

- APS credentials, developer hub, app registration, Data Management, Model Derivative, or Viewer API calls.
- Product dependency adoption for ODA, APS Viewer, Model Derivative, LibreDWG, or other conversion/viewer engines.
- Customer/confidential drawing files.
- DB/API/schema, TypeDB ingestion, auth/RBAC, deployment.
- Capturing/storing browser tokens or account payloads from DevTools.

## Exact Next Prompt

```text
$ai-loop-orchestrator
---
Goal:
Run the formal planning gate for the DUC DWG/DXF Upload Conversion Management slice and choose the first implementation path.

Must read:
- AGENTS.md
- README.md
- SPEC.md
- PLAN.md
- CHECKS.md
- HUMAN_GATE.md
- EVIDENCE.md
- docs/sessions/NEXT_SESSION.md
- docs/feature-notes/005-dwg-dxf-upload-conversion-management.md
- docs/superpowers/plans/2026-06-18-dwg-dxf-upload-conversion-management.md
- docs/PRD.md
- docs/TRD.md
- docs/UI_Spec.md
- docs/Data_Model.md
- docs/Task_List.md
- docs/Acceptance_Criteria.md
- docs/Test_Scenarios.md
- docs/Design_Map.md
- docs/User_Flow.md
- docs/Planning_Gate_Checklist.md

Must first:
1. Run git status --short --untracked-files=all.
2. Confirm Project Admin Task 6 remains BLOCKED_BROWSER_UNAVAILABLE.
3. Confirm no 0009 request is created.
4. Confirm ACC #11 SV scope and DUC scope remain separate.

Decision required:
- Option A: ACC #11 local viewer shell first.
- Option B: DUC local conversion-lab management UI first.
- Option C: DUC script adapter / JSON scan output first.

Forbidden until HUMAN_GATE:
- APS credentials/API calls
- paid SDK or ODA product adoption
- customer drawing files
- DB/API/schema
- TypeDB ingestion/frontend wiring
- auth/RBAC
- deployment
- Project Admin Task 6 PASS changes
```
