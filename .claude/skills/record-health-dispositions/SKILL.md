---
name: record-health-dispositions
description: >-
  Disposition phase of the health-audit loop. Walks the open findings in the
  latest health dossier(s), collects an accept / decline / grandfather / fixed / skip decision per finding
  at a user gate (recorded as `accepted`, `declined`, `grandfathered`, `fixed`, or
  omitted for `skip`), and appends correctly formatted
  rows to docs/health/dispositions.md, creating
  that ledger with a canonical header if it is absent. Run after /plugin-health-audit and
  before /plan-health-findings. Triggers on: "record dispositions",
  "disposition the findings", "accept decline health findings", "triage the
  dossier", "record health decisions".
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|naming|all] [--top]"
workflow:
  stage: decide
  invoked-by: user
  repeatable: true
  inputs:
    - docs/health/<date>-<surface>-health.md
    - docs/health/dispositions.md
  outputs:
    - docs/health/dispositions.md
  next: [plan-health-findings]
---

# Record Health Dispositions

Closes the gap between `/plugin-health-audit` (which writes dossiers) and
`/plan-health-findings` (which plans only `accepted` ledger rows). The only
output of this skill is appended rows in `docs/health/dispositions.md` — it
never edits plugin source.

Loop position:

`/plugin-health-audit` → dossier → `/record-health-dispositions` →
`/plan-health-findings` → plan → execute

Read `.claude/knowledge/health-filter-contract.md` first and treat it as the
canonical source of truth for surface values, dimension values, ledger schema,
legacy `unknown`, and migration expectations.

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md`: before reporting
any phase complete, advancing to the next phase, or updating
`.dev/health-loop-state.md`, emit a phase-proof block (observed command output
or file-existence check) binding to that phase's deliverable. A restated
intention is not proof.

## Phase 0 — Parse arguments and locate inputs

Check `.dev/health-loop-state.md` for resume context; adoption rules are in
`.claude/knowledge/health-disposition-rules.md` § Loop-State Adoption. If no
valid resume pointer exists, locate the latest dossier per surface with
`select_health_artifacts.py --directory docs/health --kind health`.

| Argument | Default | Behaviour |
|---|---|---|
| `--surface <value>` | from loop-state or `both` | Filter findings to this surface |
| `--dimension <value>` | from loop-state or `all` | Filter findings to this dimension |
| `--top` | off | Disposition only the dossier's "Top N ranked actions" entries |

If no dossier exists for a requested surface, report "No `<surface>` dossier
found — run /plugin-health-audit first." and skip that surface.

If `docs/health/dispositions.md` does not exist, create it first with the
canonical header (title, purpose sentence, four ledger rules, empty table)
from the live ledger's git history or the rules in
`.claude/knowledge/health-disposition-rules.md`.

## Phase 1 — Collect open findings

Read each located dossier. Collect findings from exactly these sections
(the same parse `/plan-health-findings` Phase 1 uses):

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

With `--top`, restrict the worklist to the dossier's "Top N ranked
actions" entries.

Then read `docs/health/dispositions.md` and drop from the worklist every
finding that already matches a ledger row by **surface + dimension + object +
issue essence**
(not exact wording — lenses rephrase between sweeps).

Declined, grandfathered, and fixed findings are closed: skip them entirely (no row, no re-litigation).
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

## Phase 3 — Append rows

Append one row per non-skip decision at the bottom of the table, using the
eight-column schema (canonical column order):

1. `ID` · 2. `Surface` · 3. `Dimension` · 4. `Object` · 5. `Finding` ·
6. `Disposition` · 7. `Date` · 8. `Evidence / note`

```markdown
| <id> | <surface> | <dimension> | <object> | <finding — short, rephrase-tolerant> | <disposition> | <today's date> | <evidence / note> |
```

- Date is today's real date in ISO format — never a literal placeholder.
- Append-only: never reorder or rewrite existing rows.
- For legacy rows whose provenance is not yet proven, `unknown` is permitted
  until the migration audit is cleaned up.
- Append new rows with `scripts/health_disposition_store.py append_row`; never hand-edit `docs/health/dispositions.md`.
- Read `docs/health/dispositions.md` for ordinary suppression and planning checks.
- If a step needs closure chronology, query the history store via `scripts/health_disposition_store.py iter_history_rows`.
- Verification must confirm both artifacts changed together:
  - one history shard appended under `docs/health/dispositions-history/`
  - `docs/health/dispositions.md` regenerated

Any session that resolves an `accepted` row must apply the **closure write-back
rule** in the same session. Full procedure in
`.claude/knowledge/health-disposition-rules.md` § Closure Write-Back Rule.

## Phase 4 — Verify and hand off

1. Run `git diff --stat docs/health/dispositions.md` — confirm the only
   change is appended rows and the appended row count equals the non-skip
   decision count.
2. Scan the appended rows for unfinished-work markers (to-do markers,
   unrendered date placeholders).
3. Summarize: accepted / declined / grandfathered / fixed counts, plus how
   many findings remain undispositioned.
4. **Backlog guard.** Run
   `python3 scripts/health_disposition_store.py list-open --status accepted`
   and note the total count and the oldest `date` among the returned rows. If
   the count is non-trivial (≥ 10), emit:

   > ⚠ N open `accepted` rows (oldest `<date>`) — including rows from earlier
   > sweeps the dossier no longer surfaces. Run `/plan-health-findings
   > --backlog` to drain the full backlog, not just this round's rows.

   This is informational and never blocks.
5. If at least one row is `accepted`, write `.dev/health-loop-state.md`
   (schema: `.claude/knowledge/health-loop-state-contract.md`):

   - `stage_completed: record-health-dispositions`
   - `completed_at:` today's ISO date
   - `next_command: /plan-health-findings`
   - `next_inputs: docs/health/dispositions.md` plus the dossier path(s)
   - `fresh_session_recommended: false`
   - `note:` plan the `accepted` rows. When the backlog guard fired (step 4),
     add `run with --backlog to drain all N open accepted rows, not only this
     dossier's`.

   Then tell the user: "Recorded N accepted rows. Next in the loop:
   `/plan-health-findings` (pointer saved in `.dev/health-loop-state.md`)" — and
   when the backlog guard fired, add: "consider `--backlog` to drain the full
   open backlog." If no row is `accepted`, do not write the breadcrumb; report
   that there is nothing to plan.

Do not edit any plugin source file from this skill. Committing the ledger
change is left to the user's normal commit flow.
