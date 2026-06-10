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
Parse it. Findings with `verdict=None` are monitor-only. **Monitor-only
(operative definition):** an observation worth tracking but carrying no
implementation action — the lens looked and concluded the current state is
acceptable or expected. Excluded so the severity counts measure actionable
findings only: exclude them from the severity counts, the dimension
grouping, and top-5 eligibility in Phase 2. List them in a one-line "Monitor-only (excluded from counts)" note
under Design suggestions instead. A Complexity line missing the verdict
field entirely is a lens regression — count it normally but flag it in the
dossier as "verdict missing".

Note any "Failed lenses" listed at the foot of the file.

## Phase 1b — Recurrence annotation

Sweeps have no memory by default, so open findings are re-discovered and
re-ranked as new every run. Annotate repeats instead.

Locate the previous findings file for the same surface:

```bash
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind findings \
  --surface <surface> \
  --offset 1
```

If none exists, skip this phase (every finding is new). Otherwise, for each
parsed finding, check whether the same object with substantially the same
issue appears in the previous findings file (match on substance, not
wording — i.e. the same object with the same observable finding, even if rephrased). For each repeat:

- Annotate the finding line in the dossier with `(open since YYYY-MM-DD)`.
  Carry the **earliest** known date forward — if the prior dossier already
  dated the finding, reuse that date rather than resetting it.
- If the severity differs from the prior sweep with no change to the
  subject file, append `(was <severity> on <date>)` — severity churn is
  signal about the lens, not about progress.

Recurring findings stay in the dossier and in the severity counts (they are
still open work), but the Summary must split the totals: new vs recurring.

## Phase 1c — Staleness gate (before ranking)

Apply the **staleness spot-check protocol** from
`../../knowledge/health-audit-preconditions.md` to every High finding and every
top-5 candidate before ranking. Resolve the subject to its file path (skill →
`profile-al-dev-shared/skills/<name>/SKILL.md` or `.claude/skills/<name>/SKILL.md`;
agent → the matching `agents/<name>.md`), then run the protocol's `git log --since`
check, supplying `FINDINGS_DATE` (from this skill's findings-file name) in place of
the protocol's generic `DOSSIER_DATE` boundary — and, for recurring findings, again
with `PRIOR_DATE` from Phase 1b, since a repeat whose
subject changed between sweeps may be a lens re-issuing a complaint against
already-fixed text. Label any whose subject changed `⚠ possibly stale`.

A labelled finding may enter the top 5 only after reading the live subject file
and confirming the claim still holds; record the spot-check ("verified against
live file [date]") next to the action. If the claim no longer holds, drop the
finding from counts and list it under a "Stale (dropped)" note instead.

## Phase 1d — Disposition suppression

Read `docs/health/dispositions.md` (skip this phase if absent). Match each parsed
finding against ledger rows by object + issue essence, then apply the
**disposition suppression rules** from
`../../knowledge/health-audit-preconditions.md`:

- **`declined` / `grandfathered`** → suppress (exclude from severity counts,
  dimension grouping, and top-5); list one line each under a
  "Dispositioned (suppressed)" note at the foot of the dossier.
- **`fixed`** → treat a re-flagged finding as suspect and verify it against the
  live subject file (Phase 1c spot-check); drop it under "Stale (dropped)" if the
  claim no longer holds, or keep it with a "regressed — previously fixed in
  [commit]" note if it genuinely regressed.
- **`accepted`** → keep, annotated "(accepted YYYY-MM-DD — awaiting
  implementation)".

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

Print, per surface: dossier path + severity counts (new vs recurring) + the
top action.
List any failed lenses.
Ask: "Review the dossier, record accept/decline decisions via
`/record-health-dispositions` (or directly in
`docs/health/dispositions.md`), then run `/plan-health-findings` on the
accepted items?" — recording dispositions is what stops the next sweep from
re-ranking the same findings as new.
Do not edit any source file.
