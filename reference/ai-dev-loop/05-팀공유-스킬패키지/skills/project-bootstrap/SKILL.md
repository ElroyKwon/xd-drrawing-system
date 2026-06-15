---
name: project-bootstrap
description: Use when starting work in a new or existing development folder, especially before planning or coding, to check project AI instructions, loop documents, skills, verification files, and human approval gates.
---

# Project Bootstrap

## Purpose

Prepare a development folder for agentic work before planning or implementation starts.

## Steps

1. Identify the project root.
2. Check whether these files exist:
   - `CLAUDE.md`
   - `AGENTS.md`
   - `GEMINI.md`
   - `SPEC.md`
   - `PLAN.md`
   - `CHECKS.md`
   - `EVIDENCE.md`
   - `HUMAN_GATE.md`
3. Check for project-local skills:
   - `.claude/skills/*/SKILL.md`
   - `.agents/skills/*/SKILL.md`
4. Read existing instruction files before proposing work.
5. Report missing files as setup gaps.
6. Do not start implementation until the user confirms setup gaps can be ignored or fixed.

## Output

Use this format:

```text
Project root:
Existing instruction files:
Missing instruction files:
Available skills:
Missing recommended skills:
Verification files:
Human approval gates:
Recommended next action:
```

## Human Gate

Never create or modify global files automatically. Recommend the change and wait for approval.
