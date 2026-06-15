---
name: validator-loop
description: Use when work is claimed to be done, before final reports, before PRs, after implementation, or when tests/build/browser behavior must prove completion with repeatable evidence.
---

# Validator Loop

## Purpose

Verify completed work with evidence instead of accepting an agent's completion claim.

## Required Inputs

Read available files:

- `SPEC.md`
- `PLAN.md`
- `CHECKS.md`
- `EVIDENCE.md`
- `HUMAN_GATE.md`
- project test files
- package scripts

## Verification Loop

1. Identify required commands from `CHECKS.md` or project scripts.
2. Run or request the smallest relevant checks first.
3. If a check fails, record:
   - failure item
   - command
   - reproduction
   - expected behavior
   - actual behavior
   - likely owner
   - next verification command
4. Do not mark complete while any required check fails.
5. Update `EVIDENCE.md` with results.

## Output

```text
Validation Result: PASS/FAIL/BLOCKED

Commands run:
Passing checks:
Failing checks:
Manual scenarios:
Evidence updated:
Remaining risks:
Human approval items:
Next action:
```

## Rule

The phrase "looks good" is not evidence. Use commands, screenshots, browser checks, or documented manual scenarios.
