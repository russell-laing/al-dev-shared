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
| **Optional inputs** | `.dev/plan-critique-*.md` (written by /al-dev-plan-with-critics, when present) — critic findings to surface at the approval gate |
| **Durable outputs** | None — user approval is the terminal output |
| **Resume read order** | Locate latest `.dev/*-al-dev-plan-solution-plan.md` |
| **Success evidence** | User selects Approve before this skill exits |

## Phase 1 — Locate solution plan

```bash
ls -t .dev/*-al-dev-plan-solution-plan.md 2>/dev/null | head -1
```

If no solution plan found: stop and report "No solution plan found in .dev/. Run /al-dev-plan first."

Store the path as `PLAN_FILE`.

Also locate the latest critic findings, if present:

```bash
CRITIQUE=$(ls -t .dev/plan-critique-*.md 2>/dev/null | head -1)
```

If `$CRITIQUE` is non-empty, read it and carry its findings into the approval summary (Phase 3). If absent, continue silently — critic findings are optional (the plan may not have run /al-dev-plan-with-critics).

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
- **"No REQ tokens found" in validator output** (the requirements file
  has no `### REQ-NNN:` headings; traceability cannot be checked):
  1. Open the requirements file (`$REQ`)
  2. Scan for numbered items — lines starting with `1.`, `2.`, etc.,
     or headings using `### 1.` / `### 2.` style
  3. If numbered items exist: add `### REQ-NNN:` prefixes to each item
     in sequence, save the file, then re-run the validator
  4. If the requirements file is absent, empty, or has no numbered
     items: escalate to the user — the requirements file needs
     structural repair before traceability can be verified
- Untraced requirements (REQ-NNN tokens exist in the requirements file
  but are not referenced in the plan): add `REQ-NNN` mentions to the
  plan tasks whose description, acceptance criteria, or named BC objects
  overlap with the requirement's subject text

If an issue cannot be auto-fixed, present it to the user (escalate to the
architects for refinement, or approve with documented risk) before claiming the
plan is ready. Escalate → re-dispatch the architects with feedback at the
Phase 3 gate; or approve-with-risk → document the risk in the approval summary
and continue to Phase 3.

## Phase 2.5: Scenario-Coverage Probe

The validator checks structural completeness, not scenario completeness. Before
the approval gate, confirm the plan's tasks cover the requirement's main
scenarios:

1. From the requirements file `$REQ` (located in Phase 2), extract the top 2–3
   trigger scenarios — the numbered items (`1.`, `2.`, …) or `### REQ-NNN:`
   headings that describe what the user must be able to do.
2. For each extracted scenario, find a plan task whose title, description, or
   named BC objects implement it (match on subject text, not exact wording).
3. If every scenario maps to a named task, note "Scenario coverage: complete"
   and continue to Phase 3. If any scenario has no task, surface the gap
   explicitly in the Phase 3 approval summary under a "Scenario coverage gaps"
   heading **before** the USER_GATE, so the user weighs it before approving.

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

- When a plan-critique file was loaded in Phase 1, list its open critic findings under a "Critic findings" heading in the approval summary so the user weighs them before approving.

USER_GATE — ask the user with options:

- Approve - Proceed to development
- Refine - Adjust plan (what needs changing?)
- Review Alternatives - Show me other architect approaches
- Stop - Cancel planning

If user selects "Refine", spawn architects again with the
user's feedback.
