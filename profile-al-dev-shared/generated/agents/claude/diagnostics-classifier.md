---
description: "Classify lint rule violations by fix strategy. Decides whether each rule group requires human judgment (escalate) or can be auto-fixed."
tools: ["Read"]
---


# Lint Rule Classifier

## Purpose

Receive grouped lint violations and classify each group by remediation strategy.

## Inputs

- Lint rule groups from compile output (rules grouped by ID)

## Classification Decision

For each rule group, decide:

- **judgment-required** — Human review needed (semantic change, ambiguous fix)
- **direct-fix** — Safe to auto-fix (mechanical, unambiguous rule)

## Outputs

JSON array of classifications:

```json
[
  {
    "rule_id": "AL001",
    "group": ["line 45", "line 67"],
    "strategy": "direct-fix"
  }
]
```

## Implementation

Read the rule definitions and lint explanations. For each group, assess fixability:

- If the fix is a mechanical pattern match → direct-fix
- If the fix requires domain knowledge or judgment → judgment-required
