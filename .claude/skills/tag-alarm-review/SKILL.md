---
name: tag-alarm-review
description: Use when reviewing PLC, HMI, XD-HUB, EMS, BMS, EPMS, historian, tag lists, alarm lists, alarm levels, messages, mail flags, or field-system CSV/Excel mapping data.
---

# Tag Alarm Review

## Purpose

Review industrial tag and alarm data for missing alarm levels, invalid levels, missing messages, historian gaps, and human review items.

## Inputs

Accept CSV, Excel, Markdown tables, or copied tag lists.

Common fields:

- tag name
- address
- alarm level
- alarm message
- historian enabled
- mail enabled
- equipment
- unit

## Review Rules

1. Alarm level must be 1, 2, 3, or 4.
2. Level 1 is for fire, safety, emergency stop, or critical shutdown.
3. Level 2 is for serious equipment failure.
4. Level 3 is for general equipment alarms.
5. Level 4 is for state-change or low-severity events.
6. Missing messages must be reported.
7. Important tags without historian storage must be reported.
8. Do not auto-change field data without human approval.

## Output

```text
Summary:
Missing alarm levels:
Invalid alarm levels:
Missing messages:
Historian review targets:
Mail flag review targets:
Possible duplicates:
Human review required:
Auto-fix candidates:
```

## Human Gate

Field data, alarm level policies, and customer-facing report values require human approval before final change.
