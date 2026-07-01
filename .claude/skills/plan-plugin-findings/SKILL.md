---
name: plan-plugin-findings
description: >-
  Phase 4-5 planning portion of health-finding planning. Reads verified findings checkpoint
  (output from plan-plugin-findings-verify), writes implementation plan using superpowers:writing-plans,
  and hands off to /implement-plugin-health. Assumes Phase 1-3 verification is complete.
argument-hint: "(no arguments; reads .dev/plan-plugin-findings-verify-checkpoint.jsonl)"
workflow:
  stage: decide
  invoked-by: user
  repeatable: true
  inputs:
    - .dev/plan-plugin-findings-verify-checkpoint.jsonl
    - docs/health/dispositions-open.md
    - .dev/health-loop-state.md
  outputs:
    - docs/superpowers/plans/<date>-<topic>.md
    - .dev/health-loop-state.md
  next: [implement-plugin-health]
---

# Plan Health Findings — Writing Phase

Reads verified findings checkpoint from plan-plugin-findings-verify and converts it into
an implementation plan. Invokes superpowers:writing-plans to write verified plan tasks,
then hands off to /implement-plugin-health for execution and ledger closure.

---

## Maintainer Contracts

Apply `../../knowledge/phase-proof-contract.md` at every phase boundary before
reporting completion or updating `.dev/health-loop-state.md`.

Apply `../../knowledge/dispatch-fallback-contract.md` before every agent
dispatch. Declare the preferred path, run preflight, fall back
deterministically, and log `preferred → outcome → fallback → reason`.

## Prerequisites

- `.dev/plan-plugin-findings-verify-checkpoint.jsonl` exists with verified findings from plan-plugin-findings-verify
- `.dev/health-loop-state.md` confirms the previous stage is `plan-plugin-findings-verify`
- At least one verified finding in the checkpoint has a `proceed` or `modify` verdict

---

## Phase 0: Read verification checkpoint

Read `.dev/plan-plugin-findings-verify-checkpoint.jsonl` line by line. Each line is a JSON object with:

```json
{
  "object": "skill-or-agent-name",
  "surface": "plugin|tooling",
  "dimension": "design|quality|naming",
  "finding": "the finding description",
  "verdict": "proceed|skip|modify",
  "reason": "rubber-duck verdict reason",
  "plan_anchor": "where in the code the fix applies",
  "fix_scope_delta": "scope impact (e.g., +1 skill, model change, 0)",
  "event_id": "disp_YYYYMMDD_NNNNNN"
}
```

If the checkpoint file does not exist or is empty, stop and run `/plan-plugin-findings-verify` first.

Also read `.dev/health-loop-state.md` to confirm the previous stage is `plan-plugin-findings-verify` and the checkpoint path matches.

Collect all findings with verdict `proceed` or `modify` (skip `skip` verdicts; they are handled by plan-plugin-findings-verify). If no `proceed` or `modify` findings remain, stop with: "No verified findings ready for planning; all findings were skipped."

---

## Phase 1: Write the Implementation Plan

After all suggestions are rubber-ducked, invoke:

**REQUIRED SUB-SKILL: Use superpowers:writing-plans**

Pass as context to writing-plans all items listed in
`.claude/knowledge/health-plan-context-template.md`.

> **Survival caveat:** After writing-plans completes, run
> `grep -c "closes_event_ids:" <plan-path>` and confirm the count equals the number
> of plan tasks. A count of 0 means the sub-skill dropped the field — fix manually by adding a
> `closes_event_ids:` block as the final item inside each task's verification block
> (after the verification steps — not in the task title or header) before handoff.

- **Pre-empt the known correction patterns.** Before finalizing, consult
  `.claude/knowledge/correction-patterns.md` and author every task so no row applies
  to it. `revise-plugin-plan` checks the same list — anything you author cleanly here is
  one defect the reviewer does not have to send back. The recurring author-side defects
  this gate exists to prevent:
  - **Value-sensitive verification.** Every task's verification grep MUST fail on the
    pre-edit file — assert the new value with a fixed-string `grep -F`, and where the old
    value is known, assert its absence too. A whole-file presence grep that already matches
    the untouched file is not acceptance evidence (`/implement-plugin-health` would mark the
    task verified even if the edit was skipped).
  - **Task-specific commit scopes.** Use `type(<edited-component>)` matching the edited
    skill/agent/directory name (e.g. `fix(al-dev-investigate)`, `chore(generated-agents)`),
    never a generic `type(plugin)`. Subject ≤72 characters, subject-only (tool repo).
  - **Shared-surface validation gate.** When the plan edits `profile-al-dev-shared/` files,
    add a validation-gate task (after the last source edit and any projection regen, before
    ledger close-back) chaining the repo's shared-surface validators with `&&`; it closes no
    events (`closes_event_ids: []`).

    **For agent or script edits, regenerate projections first, then test:**

    ```bash
    python3 scripts/generate-projections.py --agents .claude/agents/verify-health-finding.md
    pytest tests/test_verify_health_finding.py -v
    ```

    **Libexpat fallback (Python 3.13 macOS):**

    ```bash
    python3 -c "
    import importlib.util
    spec = importlib.util.spec_from_file_location('mod', 'tests/test_verify_health_finding.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print('PASS')
    "
    ```

- **Spec-only tasks must not earn closure.** When a rubber-duck `modify` verdict reduces
  a finding's scope to "write prerequisite documentation only" (the task body explicitly
  defers the behavior change to a future plan), the task must carry `closes_event_ids: []`
  with a note that the accepted event stays open for that future plan. Do not assign the
  accepted `event_id` to a spec-only task — `implement-plugin-health` would falsely mark it
  `fixed` even though the underlying behavior change has not occurred.

- **Suppress your Execution Handoff.** Do not present the "Subagent-Driven / Inline" prompt
  or ask "Which approach?" — the health loop overrides those endings. After writing-plans
  completes, this skill's Phase 2 routes execution to `/implement-plugin-health` so the
  ledger entries are properly closed. Writing-plans' own endings bypass that ledger close-back.

Plan saves to:
`docs/superpowers/plans/YYYY-MM-DD-<surface>-<short-label>.md`

---

## Phase 2: Hand off to implement (overrides the writing-plans Execution Handoff)

`superpowers:writing-plans` ends with its own **Execution Handoff** offering
"Subagent-Driven" or "Inline" execution. **Those endings do not apply in the
health loop** — executing the plan through them skips `/implement-plugin-health`
Phase 4, so the `closes_event_ids:` events are never written `fixed` and the loop
never closes. Phase 4 already instructed `writing-plans` to suppress that
handoff; this phase is the authoritative ending. If the "Which approach?"
prompt appeared anyway, do **not** answer it — supersede it by running the
steps below.

1. **Confirm the plan carries `closes_event_ids:`** — `grep -c "closes_event_ids:" <plan-path>`.
   If the count is 0, the survival caveat in Phase 1 was violated; fix the plan
   before handing off.

2. **Commit-subject length check.** Verify all commit subjects are ≤72 characters (`revise-plugin-plan`
   catches violations too, but catching them here is cheaper):

   ```bash
   PLAN=<plan-path>
   grep -oE 'git commit -m "[^"]+"' "$PLAN" | sed -E 's/^git commit -m "//; s/"$//' > /tmp/subjects
   while IFS= read -r s; do n=$(printf '%s' "$s" | wc -m); [ "$n" -gt 72 ] && echo "OVER 72 ($n): $s"; done < /tmp/subjects
   ```

   Any printed line is a violation. Fix the subject in the plan before handing off.
   Character count, not bytes — one emoji counts as one character.

3. **Coverage reconciliation (mandatory gate).** Every accepted event in
   `docs/health/dispositions-open.md` must be resolved **exactly once** across
   `(plan-task closes_event_ids)` ∪ `(decline/grandfather ledger tasks)` — none
   missing, none in both. Compute it explicitly and state the arithmetic in the
   handoff summary (e.g. "15 plan events + 1 grandfathered + 3 declined = 19
   total"). If any accepted event is in neither, the plan has a coverage hole
   (typically a refuted skip with no decline task); fix it before handing off.
   This mirrors `revise-plugin-plan` Phase 4 so the two skills stay in sync.

4. **Write `.dev/health-loop-state.md`** (schema:
   `.claude/knowledge/health-loop-state-contract.md`):

   - `stage_completed: plan-plugin-findings`
   - `completed_at:` today's ISO date
   - `next_command: /implement-plugin-health --plan <plan-path>`
   - `next_inputs:` the `<plan-path>` plus `docs/health/dispositions-open.md`
   - `fresh_session_recommended: true`
   - `note:` run `/implement-plugin-health` to execute AND close the ledger; do
     NOT use the writing-plans Subagent-Driven/Inline options — they skip
     ledger close-back.

5. **Stop and hand off (do not auto-execute).** Tell the user: "Plan written to
   `<plan-path>` with `closes_event_ids:` for ledger close-back. This transition is
   context-heavy — start a **fresh session** and run
   `/implement-plugin-health --plan <plan-path>` to execute the plan and close the
   ledger. (Ignore the writing-plans Subagent-Driven/Inline prompt — it bypasses
   ledger close-back.) The pointer is saved in `.dev/health-loop-state.md`."
   Do not invoke `superpowers:subagent-driven-development` or
   `superpowers:executing-plans` from this skill.
