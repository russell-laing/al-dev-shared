---
audience: functional
description: >-
  Business analyst / consultant — workflows, validation rules,
  plain language, reduced RTM. Used by al-dev-docs-writer
  when AUDIENCE=functional.
---

# Feature: [Feature Name] — Functional Overview

**Audience:** Business Analyst / Consultant
**Status:** [DEFINED / IN-PROGRESS / IMPLEMENTED / VERIFIED]
**Version:** [Plugin version or release tag]

## Business Purpose

[2-3 sentences. What business problem does this feature solve?
Who benefits? What was the limitation before?]

## Functional Scope

**Included:**

- [What this feature covers — in business terms]
- [Each bullet is one functional area or user capability]

**Not included:**

- [What is explicitly out of scope]

## Workflows

### [Workflow Name]

[1-2 sentences describing what this workflow achieves.]

1. [Business step 1 — what the user does (REQ-NNN if traceability is needed)]
2. [Business step 2]
3. [System validates/processes — what happens automatically]
4. [Outcome — what the user sees or receives]

[Optional for major workflows only.]

```mermaid
flowchart TD
    A[Start workflow] --> B[User action]
    B --> C{System validates}
    C -->|Valid| D[Outcome A]
    C -->|Invalid| E[Error shown to user]
```

[Repeat this section for each major workflow. Inline requirement references
should stay in plain language, following the functional-audience RTM rules.]

## Validation Rules

The following rules are enforced automatically by the system:

1. [Rule in plain language —
   e.g. "A credit limit must be zero or greater"]
2. [Rule 2]
3. [Rule 3]

## Integration with Other Processes

| Process | How It Connects |
| --- | --- |
| [Sales Order Processing] | [Business-process touchpoint only; avoid object or code references] |
| [Finance / Ledger] | [Business impact at this integration point] |

## Requirements Traceability

[Reduced RTM table generated from the latest
`*-al-dev-interview-requirements.md` REQ tokens — columns: ID, Status,
Requirement only. No Type, Priority, or Acceptance Criteria columns.
Requirement text stays in plain language with no code references.]

| ID | Status | Requirement |
| --- | --- | --- |
| REQ-001 | VERIFIED | [Plain-language requirement description] |
