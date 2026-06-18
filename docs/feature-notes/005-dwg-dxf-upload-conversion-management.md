# 005 - DWG/DXF Upload Conversion Management

## Slice

DWG/DXF upload conversion management planning slice.

This is not ACC #11 viewer implementation. It is the technical/design bridge for the future Autodesk Cloud-like drawing upload workflow.

## Product Decision

The product should eventually support a real drawing-management flow:

```text
DWG intake
-> validation
-> xref/package handling
-> conversion
-> metadata/layout scan
-> sheet/viewable candidate selection
-> viewer surface
-> issue/memo/markup overlays
```

The next implementation should not become overly broad. The immediate purpose is to document what the local DWG/DXF experiment proves, what it does not prove, and what must be decided before product implementation.

## Local Experiment Evidence

Observed local tooling:

- ODA File Converter exists at `C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe`.
- Python exists: `Python 3.12.9`.
- `ezdxf` is installed.
- `fitz` is installed.

`D:\_Project\Data_Knowledge_Studio` was checked for DWG/DXF files and had none by recursive file search. The usable sample files are under this repository's reference old prototype tree.

Read-only reference sample source:

```text
reference/old-prototypes/prototype-도면지식관리-mvp/dwg/
```

Four samples were copied to a repo-outside temp lab and converted to DXF:

| Case | Source type | Input DWG | Output DXF | Result |
|---|---|---:|---:|---|
| ARCH-A03 | architectural floor plan | 11 | 11 | conversion PASS |
| ARCH-A04 | architectural enlarged plan | 11 | 11 | conversion PASS |
| ELEC-EE01 | electrical equipment layout | 3 | 3 | conversion PASS |
| COMM-ET01 | communication equipment plan | 3 | 3 | conversion PASS |

DXF scan with `ezdxf` confirmed that converted artifacts expose useful metadata:

- layout names and entity counts
- layer count
- block count
- modelspace entity count
- top entity types
- top INSERT names
- text samples

Rendering is not proven. A low-DPI PNG render attempt was interrupted because it could run too long. Rendering quality/performance remains a separate viewer-engine risk.

## Official Autodesk Benchmark

Autodesk Platform Services Simple Viewer describes a cloud pattern for uploading, translating, and previewing 3D designs and 2D drawings using Authentication, Data Management, Model Derivative, and Viewer.

Relevant architecture points:

- Data Management/OSS stores uploaded objects and returns URNs.
- Model Derivative starts a translation job and exposes status/manifest.
- Viewer loads translated derivatives in the browser.
- Chrome DevTools/Network inspection can help understand viewer/debug flows, but tokens and account/session data must not be copied into this repository.

Reference URLs:

- https://get-started.aps.autodesk.com/tutorials/simple-viewer/
- https://get-started.aps.autodesk.com/tutorials/simple-viewer/data/
- https://get-started.aps.autodesk.com/tutorials/simple-viewer/viewer/
- https://aps.autodesk.com/developer/overview/viewer-sdk
- https://aps.autodesk.com/developer/overview/model-derivative-api
- https://aps.autodesk.com/blog/fast-debugging-codepen-viewer-and-bim-360-acc-docs

## In Scope

- DUC document traceability with `FR-DUC-*`, `T-DUC-*`, `AC-DUC-*`, `TS-DUC-*`, and `UF-DUC-*`.
- Local drawing intake and validation model.
- DWG to DXF conversion job state model.
- DXF scan summary model.
- Sheet/viewable candidate model.
- Future relation to Build `Sheet` and ACC #11 viewer.
- Future issue/memo/markup overlay slots.
- JSON traceability/progress artifact proposal.

## Out Of Scope

- Real Autodesk/APS account, credentials, developer hub, API calls, or paid usage.
- ODA product adoption, redistribution, or dependency policy.
- Customer/confidential drawing upload or storage.
- Production file retention, DB/API/schema, TypeDB ingestion, auth/RBAC, deployment.
- Claiming DXF render quality or viewer parity.
- Project Admin Task 6 validation or evidence reuse.

## JSON Traceability Proposal

The current canonical planning docs remain Markdown. A future loop can emit JSON for automation:

```json
{
  "slice": "DUC",
  "status": "planning",
  "requirements": ["FR-DUC-001"],
  "tasks": ["T-DUC-001"],
  "acceptance": ["AC-DUC-001"],
  "tests": ["TS-DUC-001"],
  "risks": ["render-quality", "xref-binding", "license-gate"]
}
```

This is a future loop artifact proposal, not a production data contract.

## Next Recommended Slice

Next session should run a formal planning gate for the DUC documents and choose one implementation path:

1. ACC #11 local-only viewer shell first.
2. DUC local conversion-lab management UI first.
3. DUC backend/script adapter first, with no product UI yet.

Do not combine all three in one implementation pass.
