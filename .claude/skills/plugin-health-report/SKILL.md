---
name: plugin-health-report
description: >-
  Report phase of the plugin health sweep. Reads a findings file written by
  /plugin-health-discover, filters out stale and disposition-suppressed
  findings, ranks the remainder, writes the dossier, and presents results to
  the user.
  Called by /plugin-health-audit; can also be run standalone against an existing
  findings file to re-rank or reformat without re-dispatching lenses.
argument-hint: "[--findings <path>] [--surface plugin|tooling]"
workflow:
  stage: discover
  invoked-by: both
  repeatable: true
  inputs:
    - docs/health/<date>-<surface>-findings.md
    - docs/health/dispositions.md
  outputs:
    - docs/health/<date>-<surface>-health.md
  next: [record-health-dispositions]
---

# Skill: /plugin-health-report

Report phase of the health sweep. Reads a findings file and writes the dossier.

Read `.claude/knowledge/health-filter-contract.md` first and treat it as the
canonical source of truth for filter metadata, dimension values, dossier
wording, and legacy `unknown` handling. `/plugin-health-report` preserves and
validates upstream dimension metadata; it does not expose a public
`--dimension` argument.

## Phase 0 — Locate findings file

If `--findings <path>` is passed, read that file.

Otherwise, select the most recent findings independently for each requested
surface. Run only the command(s) matching `--surface`; when `--surface` is
omitted, run both:

```bash
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind findings \
  --surface plugin
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind findings \
  --surface tooling
```

If a requested surface returns no path, report: "No `<surface>` findings file
found. Run /plugin-health-audit for that surface first." Skip only that surface.
If neither requested surface returns a path, stop.

## Phase 1 — Parse findings

Read the findings file. Extract each `### <Lens Name> Findings` block.
Parse each finding line: `- **[name]** | [Severity] | [observation] | [fix]`

Before parsing the finding blocks, read and preserve any findings metadata near
the top of the file:

```yaml
---
surface: tooling
dimensions:
  - quality
---
```

Validate that the findings file surface matches the selected surface and that
the concrete `dimensions:` list matches the dispatched lenses present in the
artifact.

**Complexity Outliers exception:** lines from this lens carry an extra
`verdict=[Atomise|Absorb|None]` field between severity and observation.
Parse it. `verdict=None` = monitor-only (no implementation action; exclude
from severity counts, dimension grouping, and top-5). List them in a
one-line "Monitor-only (excluded from counts)" note under Design
suggestions. A Complexity line missing the verdict field is a lens
regression — count it normally but flag as "verdict missing".

Note any "Failed lenses" listed at the foot of the file.

## Phase 1b — Filter and verify findings

Full procedures are in `.claude/knowledge/report-input-gates.md`.

### Recurrence annotation

Look up the previous findings file (`--offset 1`). If none exists, skip
(every finding is new). For each repeat, annotate with `(open since YYYY-MM-DD)`,
carrying forward the date of the **earliest** prior occurrence of that finding. Split the Summary totals:
new vs recurring. See `report-input-gates.md §1b` for the full procedure.

### Staleness spot-check

Apply the staleness spot-check protocol from
`../../knowledge/health-audit-preconditions.md` (see its
"## Staleness spot-check protocol" section) to every High
finding and every top-5 candidate before ranking. Supply `FINDINGS_DATE` from
the findings-file name; for recurring findings also check with `PRIOR_DATE`
from the recurrence step. Label changed subjects `⚠ possibly stale`; verify
before top-5 inclusion; drop non-holding claims under "Stale (dropped)".
See `report-input-gates.md §1c` for the full procedure.

### Disposition suppression

Read `docs/health/dispositions.md` (skip if absent). Apply the four outcomes:
declined/grandfathered → suppress; fixed → re-verify (spot-check then drop or
flag regressed); accepted → keep annotated. See `report-input-gates.md §1d`
for the full suppression rules.

- Append new rows with `scripts/health_disposition_store.py append_row`; never hand-edit `docs/health/dispositions.md`.
- Read `docs/health/dispositions.md` for ordinary suppression and planning checks.
- If a step needs closure chronology, query the history store via `scripts/health_disposition_store.py iter_history_rows`.
- Verification must confirm both artifacts changed together:
  - one history shard appended under `docs/health/dispositions-history/`
  - `docs/health/dispositions.md` regenerated

## Phase 2 — Rank and Write Dossier

Order findings High → Medium → Low, grouped by dimension (design before quality
before naming), then by object (agent before skill). Pick the top 5 ranked actions
for the summary — excluding `verdict=None` findings (Phase 1), applying
the staleness spot-check rule (Phase 1c), and excluding suppressed
dispositions (Phase 1d).

Write `docs/health/YYYY-MM-DD-<surface>-health.md` (substitute today's date and
`plugin`/`tooling` from the findings filename). The dossier must use generic
vocabulary (no harness-specific tokens). Structure:

```markdown
# <Surface> Health — YYYY-MM-DD

surface: tooling
dimensions:
  - quality

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | <n>    | <n>     | <n>    | <n>   |
| Medium   | <n>    | <n>     | <n>    | <n>   |
| Low      | <n>    | <n>     | <n>    | <n>   |

New this sweep: <n> · Recurring from prior sweeps: <n> (annotated inline) ·
Stale (dropped): <n>

Top 5 ranked actions:
1. ...

## Design suggestions

[Atomise / Merge / Trim / Split / Align findings — each: finding | rationale | fix]
_No issues found._  ← if requested and empty
_Not requested in this run._  ← if outside the requested dimensions

## Quality findings

[Bloat / Clarity / Structure / Name-fit / Description — with file:line]
_No issues found._  ← if requested and empty
_Not requested in this run._  ← if outside the requested dimensions

## Naming violations

[actual name/path vs convention-expected — from naming-convention-lens]
_No issues found._  ← if requested and empty
_Not requested in this run._  ← if outside the requested dimensions

## Graph deltas

[orphans, dead links, off-path skills, missing refs — plugin surface only;
 omit this section for the tooling surface]
_No issues found._  ← if requested and empty
_Not requested in this run._  ← if outside the requested dimensions
```

Record any failed lenses at the foot of the Summary section.

## Phase 3 — Present to user

Read `.dev/health-loop-state.md` first (schema:
`.claude/knowledge/health-loop-state-contract.md`). If it exists and its
`next_command` names a *later* loop step (e.g. `/implement-health-plan`), warn
the user that a prior loop is still in flight and unclosed before presenting a
fresh dossier.

Print, per surface: dossier path + severity counts (new vs recurring) + the
top action.
List any failed lenses.

Write `.dev/health-loop-state.md` (schema:
`.claude/knowledge/health-loop-state-contract.md`):

- `stage_completed: plugin-health-report`
- `completed_at:` today's ISO date
- `next_command: /record-health-dispositions`
- `next_inputs:` the dossier path(s) just written, plus
  `docs/health/dispositions.md`
- `fresh_session_recommended: false`
- `note:` recording dispositions is what stops the next sweep from re-ranking
  the same findings as new.

Then tell the user: "Dossier ready. Next in the loop:
`/record-health-dispositions` to triage accept/decline decisions (the pointer
is saved in `.dev/health-loop-state.md`). After that, `/plan-health-findings`
plans the accepted items."
Do not edit any source file.
