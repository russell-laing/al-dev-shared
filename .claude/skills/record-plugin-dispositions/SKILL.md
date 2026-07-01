---
name: record-plugin-dispositions
description: >-
  Disposition phase of the health-audit loop. Walks the open findings in the
  latest health dossier(s), collects an accept / decline / grandfather / fixed / skip decision per finding
  at a user gate (recorded as `accepted`, `declined`, `grandfathered`, `fixed`, or
  omitted for `skip`), and appends JSONL disposition events through
  scripts/health_disposition_store.py append_event, followed by regenerate to
  update the generated Markdown views. Run after /audit-plugin-health and
  before /plan-plugin-findings. Triggers on: "record dispositions",
  "disposition the findings", "accept decline health findings", "triage the
  dossier", "record health decisions".
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|naming|all] [--top]"
workflow:
  stage: decide
  invoked-by: user
  repeatable: true
  inputs:
    - docs/health/<date>-<surface>-health.md
    - docs/health/dispositions-open.md
    - .dev/health-loop-state.md
  outputs:
    - docs/health/dispositions-events/<year>/<year>-<month>.jsonl
    - .dev/health-loop-state.md
  next: [plan-plugin-findings]
---

# Record Health Dispositions

Closes the gap between `/audit-plugin-health` (which writes dossiers) and
`/plan-plugin-findings` (which plans only `accepted` ledger rows).

The output is JSONL disposition events appended through
`scripts/health_disposition_store.py append_event`, followed by
`scripts/health_disposition_store.py regenerate`. The generated Markdown views
are read artifacts, not edit targets. This skill never edits plugin source.

Loop position:

`/audit-plugin-health` → dossier → `/record-plugin-dispositions` →
`/plan-plugin-findings` → plan → execute

Read `.claude/knowledge/health-filter-contract.md` first and treat it as the
canonical source of truth for surface values, dimension values, ledger schema,
legacy `unknown`, and migration expectations.

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md` — emit a phase-proof block at each phase boundary before reporting completion or updating `.dev/health-loop-state.md`.

## Phase 0 — Parse arguments and locate inputs

Check `.dev/health-loop-state.md` for resume context; adoption rules are in
`.claude/knowledge/health-disposition-rules.md` § Loop-State Adoption. If no
valid resume pointer exists, locate the latest dossier per surface with
`scripts/select_health_artifacts.py --directory docs/health --kind health`.

| Argument | Default | Behaviour |
|---|---|---|
| `--surface <value>` | from loop-state or `both` | Filter findings to this surface |
| `--dimension <value>` | from loop-state or `all` | Filter findings to this dimension |
| `--top` | off | Disposition only the dossier's "Top N ranked actions" entries |

If no dossier exists for a requested surface, report "No `<surface>` dossier
found — run /audit-plugin-health first." and skip that surface.

Read `docs/health/dispositions-index.json` (if present) for a quick count of
open accepted events. Read `docs/health/dispositions-open.md` to see the
current open accepted event list.

## Phase 1 — Collect open findings

Read each located dossier. Collect findings from exactly these sections
(the same parse `/plan-plugin-findings` Phase 1 uses):

- `## Design suggestions`
- `## Quality findings`
- `## Naming violations`

Skip `_No issues found._` sections, findings marked `← implemented` or
`← completed`, and anything listed under "Stale (dropped)", "Dispositioned
(suppressed)", or "Monitor-only" notes — those are already closed or
excluded by the report phase. (These markers — `← implemented`,
`← completed`, `← already implemented` — are legacy inline dossier annotations
the parser still accepts for compatibility; treat all three as "skip, already
closed".)

Examples of marked finding lines in a live dossier (skip these without recording a disposition):

```markdown
Trim — quality-skill-lens-bloat — Remove the redundant phase summary block ← implemented
Split — plan-plugin-findings — Separate Phase 1 filter logic into a sub-skill ← completed
Inline — design-agent-lens-usage-patterns — Fold into the caller skill body ← already implemented
```

With `--top`, restrict the worklist to the dossier's "Top N ranked
actions" entries.

Then read `docs/health/dispositions-open.md` and drop from the worklist every
finding that already matches an event by **surface + dimension + object +
issue essence**
(not exact wording — lenses rephrase between sweeps).

Declined, grandfathered, and fixed events are closed: skip them entirely (no new event, no re-litigation).
Keep only undispositioned and accepted findings in this round's worklist.

Report before the gate: "N open findings; M already dispositioned
(skipped)."

## Phase 2 — Disposition gate

Present the worklist in dossier rank order (top actions first, then
High → Medium → Low). For each finding show: object, severity, one-line
issue, proposed fix. Collect one decision per finding from the user:

- `accepted` — to be implemented; note may name the intended change
- `declined` — requires a reason (recorded in Evidence / note)
- `grandfather` (as a disposition choice) — deliberate or settled; requires a reason (recorded ledger value: `grandfathered`)
- `fixed` — requires a commit hash or "verified against live file `<date>`" (recorded ledger value: `fixed`)
- `skip` — leave undispositioned this round (no row written)

Batch decisions are fine when the user groups them explicitly; one justification
per batch suffices (not per row within the batch), but the justification must
cover all rows in the batch — a justification that applies only to a subset of
the batch is not accepted. Never invent a decision: every non-skip row needs
explicit user input. A batch grouping findings with different root causes or
contexts is contradictory — reject it and require separate decisions. Apply the
**contradictory-batch guard** and the
**re-litigation guard** as defined in
`.claude/knowledge/health-disposition-rules.md`.

For example, a single batch that groups a model-fit finding on
`al-dev-general-code-reviewer` with a glob-mismatch finding on the unrelated
`al-dev-handoff` skill is contradictory — the two findings share no root cause
or context, so one justification cannot cover both. Reject it and take a
separate decision per finding.

## Phase 3 — Append events

- Append one JSONL event per decision with `append_event`.
- Run `scripts/health_disposition_store.py regenerate`.
- Read `docs/health/dispositions-index.json` to report total events and open accepted count.
- Read `docs/health/dispositions-open.md` only when open accepted rows need to be listed.

For each non-skip decision, call `scripts/health_disposition_store.py append_event`
with the required fields: `surface`, `dimension`, `object`, `finding`,
`disposition`, `date` (today's real ISO date — never a literal placeholder),
`evidence`, and `source`. The event store auto-allocates an `event_id`; do not
invent one. After all decisions are appended, run
`scripts/health_disposition_store.py regenerate` once to update the generated views.

Any session that resolves an `accepted` row must apply the **closure write-back
rule** in the same session. Full procedure in
`.claude/knowledge/health-disposition-rules.md` § Closure Write-Back Rule.

## Phase 4 — Verify and hand off

1. Run `python3 scripts/health_disposition_store.py regenerate` (if not already
   done in Phase 3) and confirm the generated views updated. Read
   `docs/health/dispositions-index.json` to verify the event count increased by
   the non-skip decision count.
2. Scan the appended rows for unfinished-work markers (to-do markers,
   unrendered date placeholders).
3. Summarize: accepted / declined / grandfathered / fixed counts, plus how
   many findings remain undispositioned.
4. **Backlog guard.** Run
   `python3 scripts/health_disposition_store.py list-open --status accepted`
   and note the total count T and the oldest `date` among the returned rows.
   If T exceeds the number of `accepted` decisions recorded in Phase 3 of
   this session (call that N), the difference represents rows from earlier
   sweeps that `/plan-plugin-findings` would otherwise miss without `--backlog`.
   In that case, emit:

   > ⚠ T open `accepted` rows (oldest `<date>`) — including rows from earlier
   > sweeps the dossier no longer surfaces. Run `/plan-plugin-findings
   > --backlog` to drain the full backlog, not just this round's rows.

   If T equals N (all open accepted rows are from this session), skip the
   recommendation — there is no older backlog to drain.

   This check is informational and never blocks.
5. If at least one row is `accepted`, write `.dev/health-loop-state.md`
   (schema: `.claude/knowledge/health-loop-state-contract.md`):

   - `stage_completed: record-plugin-dispositions`
   - `completed_at:` today's ISO date
   - `next_command: /plan-plugin-findings`
   - `next_inputs: docs/health/dispositions-open.md` plus the dossier path(s)
   - `fresh_session_recommended: false`
   - `note:` plan the `accepted` rows. When the backlog guard fired (step 4
     — T > N), add `run with --backlog to drain all T open accepted rows,
     not only this dossier's N`.

   Then tell the user: "Recorded N accepted rows. Next in the loop:
   `/plan-plugin-findings` (pointer saved in `.dev/health-loop-state.md`)" — and
   when the backlog guard fired (T > N), add: "consider `--backlog` to drain
   the full open backlog." If no row is `accepted`, do not write the breadcrumb; report
   that there is nothing to plan.

Do not edit any plugin source file from this skill. Committing the ledger
change is left to the user's normal commit flow.
