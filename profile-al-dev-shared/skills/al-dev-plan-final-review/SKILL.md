---
name: al-dev-plan-final-review
description: >-
  Validates and presents an al-dev-plan solution plan for user approval before
  implementation begins. Runs validate-plan.py against the latest solution plan,
  presents results, and gates approval. Called by /al-dev-plan after Phase 5;
  can also be run standalone to re-validate an existing plan.
  Triggers on: "validate the plan", "approve the plan", "review the solution
  plan", "plan final review".
argument-hint: ""
---

# AL Dev Plan — Final Review

Validation and user approval gate for the solution plan written by /al-dev-plan.

## Artifact Contract

| | |
|---|---|
| **Required inputs** | `.dev/*-al-dev-plan-solution-plan.md` (written by /al-dev-plan Phase 5) |
| **Durable outputs** | None — user approval is the terminal output |
| **Resume read order** | Locate latest `.dev/*-al-dev-plan-solution-plan.md` |
| **Success evidence** | User selects Approve before this skill exits |

## Phase 1 — Locate solution plan

```bash
ls -t .dev/*-al-dev-plan-solution-plan.md 2>/dev/null | head -1
```

If no solution plan found: stop and report "No solution plan found in .dev/. Run /al-dev-plan first."

Store the path as `PLAN_FILE`.

## Phase 2: Validate the Plan

After writing the solution plan file, run the validator:

```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-plan/validate-plan.py"
REQ=$(ls .dev/*-al-dev-interview-requirements.md 2>/dev/null \
  | sort | tail -1)
PLAN=$(ls .dev/*-al-dev-plan-solution-plan.md 2>/dev/null \
  | sort | tail -1)
[ -f "$VALIDATOR" ] && [ -n "$REQ" ] && [ -n "$PLAN" ] && \
  python3 "$VALIDATOR" "$PLAN" "$REQ" \
  || echo "Validator not found or files missing — skipping"
```

The script auto-detects files in the same directory.

Fix any issues the validator reports before presenting to the
user. Common issues:

- Missing required sections (add them)
- Duplicate object IDs (reconcile from architect merge)
- Untraced requirements (add REQ-NNN references to plan)

If an issue cannot be auto-fixed, present it to the user (escalate to the
architects for refinement, or approve with documented risk) before claiming the
plan is ready.

## Phase 3: Present to User for Approval

Present your synthesized plan:

```text
Solution plan complete -> .dev/$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md

Key decisions:
- [Major design decisions with rationale]
- [Key objects: 3-5 most important ones]
- [BC integration approach]

Evaluated [N] competing approaches:
- Approach A: [1 sentence pro/con]
- Approach B: [1 sentence pro/con] <- Selected
- Approach C: [1 sentence pro/con]

Selected Approach [X] because [key rationale].

Ready to proceed to development?
```

USER_GATE — ask the user with options:

- Approve - Proceed to development
- Refine - Adjust plan (what needs changing?)
- Review Alternatives - Show me other architect approaches
- Stop - Cancel planning

If user selects "Refine", spawn architects again with the
user's feedback.
