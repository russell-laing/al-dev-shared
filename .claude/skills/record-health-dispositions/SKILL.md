---
name: record-health-dispositions
description: >-
  Disposition phase of the health-audit loop. Walks the open findings in the
  latest health dossier(s), collects an accept / decline / grandfather /
  fixed decision per finding at a user gate, and appends correctly formatted
  rows to docs/health/dispositions.md. Run after /plugin-health-audit and
  before /plan-health-findings. Triggers on: "record dispositions",
  "disposition the findings", "accept decline health findings", "triage the
  dossier", "record health decisions".
argument-hint: "[--surface plugin|tooling|both] [--top]"
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

## Phase 0 — Parse arguments and locate inputs

- `--surface` ∈ `plugin` | `tooling` | `both` (default `both`)
- `--top` — disposition only the entries in the dossier's "Top N ranked
  actions" list

Locate the latest dossier per requested surface:

```bash
ls -t docs/health/*-plugin-health.md 2>/dev/null | head -1
ls -t docs/health/*-tooling-health.md 2>/dev/null | head -1
```

If no dossier exists for a requested surface, report "No `<surface>` dossier
found — run /plugin-health-audit first." and skip that surface.

If `docs/health/dispositions.md` does not exist, create it first with the
canonical header (title, purpose sentence naming this skill as producer and
`/plugin-health-report` + `/plan-health-findings` as consumers, the four
ledger rules, and the empty five-column table) by copying the header block
from the live ledger's git history — or, if no history exists, the rules
listed under "Re-litigation guard" and "Append rows" below.

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
finding that already matches a ledger row by **object + issue essence**
(not exact wording — lenses rephrase between sweeps).

Report before the gate: "N open findings; M already dispositioned
(skipped)."

## Phase 2 — Disposition gate

Present the worklist in dossier rank order (top actions first, then
High → Medium → Low). For each finding show: object, severity, one-line
issue, proposed fix. Collect one decision per finding from the user:

- `accepted` — to be implemented; note may name the intended change
- `declined` — requires a reason (recorded in Evidence / note)
- `grandfathered` — deliberate or settled; requires a reason
- `fixed` — requires a commit hash or "verified against live file `<date>`"
- `skip` — leave undispositioned this round (no row written)

Batch decisions are fine ("accept 1-3, decline 4 because X"). Never invent
a decision: every non-skip row needs explicit user input.

**Contradictory-batch guard:** before writing any row from a batched response,
check whether the same object + issue essence appears twice with different
decisions in the current batch. If it does, stop and ask the user to resolve the
conflict first. Do not append a partial batch.

**Re-litigation guard:** if a decision contradicts an existing `declined`
or `grandfathered` row for the same object + issue essence, refuse to
append a new row. Per the ledger rules, the existing row must be edited
first — name the conflicting row and stop on that finding only.

## Phase 3 — Append rows

Append one row per non-skip decision at the bottom of the table, in the
existing format:

```markdown
| <object> | <issue essence — short, rephrase-tolerant> | <disposition> | <today's date> | <evidence / reason> |
```

- Date is today's real date in ISO format — never a literal placeholder.
- Append-only: never reorder or rewrite existing rows.

## Phase 4 — Verify and hand off

1. Run `git diff --stat docs/health/dispositions.md` — confirm the only
   change is appended rows and the appended row count equals the non-skip
   decision count.
2. Scan the appended rows for unfinished-work markers (to-do markers,
   unrendered date placeholders).
3. Summarize: accepted / declined / grandfathered / fixed counts, plus how
   many findings remain undispositioned.
4. If at least one row is `accepted`, offer: "Run `/plan-health-findings`
   on the accepted items now?"

Do not edit any plugin source file from this skill. Committing the ledger
change is left to the user's normal commit flow.

## Closure write-back rule (binding on fix sessions)

Any session that resolves an `accepted` row must close the ledger in the same
session. Use `.claude/knowledge/ledger-closure-protocol.md` for the background
and full rule set.

- Uncommitted accepted row → flip it in place to `fixed`.
- Committed accepted row → append a later `fixed` row with the resolving commit
  and `closes row N`.
- After the source change, run `python3 scripts/check_ledger_staleness.py` to
  confirm the row no longer appears as effectively open.
