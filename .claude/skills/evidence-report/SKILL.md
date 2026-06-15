---
name: evidence-report
description: Use for final reports, handoffs, session closeout, PR summaries, or completion claims where implementation evidence, checks, risks, and human approval items must be summarized clearly.
---

# Evidence Report

## Purpose

Produce a concise, evidence-based closeout that separates completed work from unverified claims.

## Inputs

Read:

- `EVIDENCE.md`
- `CHECKS.md`
- `PLAN.md`
- `HUMAN_GATE.md`
- git diff or changed files when available

## Report Format

```text
Result:
Changed files:
Implemented items:
Verification evidence:
Not run / unavailable checks:
Known risks:
Human approval items:
Next recommended step:
```

## Rules

- Do not hide failed checks.
- Do not describe unchecked work as complete.
- Keep the report short enough to act on.
- If evidence is missing, say exactly what is missing.
