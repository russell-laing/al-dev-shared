---
name: plugin-health-report
description: >-
  Report phase of the plugin health sweep. Reads a findings file written by
  /plugin-health-discover, ranks findings, writes the dossier, and presents
  results to the user.
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
  next: [analyze-architectural-design, record-health-dispositions]
---

# Skill: /plugin-health-report

Report phase of the health sweep. Reads a findings file and writes the dossier.

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
wording). For each repeat:

- Annotate the finding line in the dossier with `(open since YYYY-MM-DD)`.
  Carry the **earliest** known date forward — if the prior dossier already
  dated the finding, reuse that date rather than resetting it.
- If the severity differs from the prior sweep with no change to the
  subject file, append `(was <severity> on <date>)` — severity churn is
  signal about the lens, not about progress.

Recurring findings stay in the dossier and in the severity counts (they are
still open work), but the Summary must split the totals: new vs recurring.

## Phase 1c — Staleness gate (before ranking)

A lens may re-issue an old complaint against text that has already been
fixed, and a findings file goes stale the moment fix commits land. Label
suspect findings before they can be ranked:

For every High finding and every top-5 candidate, resolve the subject to a
file path (skill → `profile-al-dev-shared/skills/<name>/SKILL.md` or
`.claude/skills/<name>/SKILL.md`; agent → the matching `agents/<name>.md`),
then check:

```bash
# FINDINGS_DATE from the findings filename; PRIOR_DATE from Phase 1b
git log --since="$FINDINGS_DATE 00:00" --oneline -- "$SUBJECT_PATH"
```

- Non-empty output → the subject changed **after** the findings were
  generated: label `⚠ possibly stale`.
- For recurring findings, also run with `--since="$PRIOR_DATE 00:00"` — a
  repeat whose subject changed between sweeps may be a lens re-issuing a
  complaint against already-fixed text: label `⚠ possibly stale`.

A labelled finding may enter the top 5 only after reading the live subject
file and confirming the claim still holds; record the spot-check ("verified
against live file [date]") next to the action. If the claim no longer
holds, drop the finding from counts and list it under a "Stale (dropped)"
note instead.

## Phase 1d — Disposition suppression

Read `docs/health/dispositions.md` (skip this phase if absent). Match each
parsed finding against ledger rows by object + issue essence:

- **`declined` / `grandfathered`** → suppress: exclude from severity
  counts, dimension grouping, and top-5. List one line each under a
  "Dispositioned (suppressed)" note at the foot of the dossier. These are
  settled decisions; the dossier must not re-litigate them.
- **`fixed`** → if the lens has re-flagged the same issue, treat the
  finding as suspect: verify against the live subject file (Phase 1c
  protocol). If the claim no longer holds, drop it under "Stale (dropped)";
  if the issue has genuinely regressed, keep it and note "regressed —
  previously fixed in [commit]".
- **`accepted`** → keep, and annotate "(accepted YYYY-MM-DD — awaiting
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
_No issues found._  ← if empty

## Quality findings

[Bloat / Clarity / Structure / Name-fit / Description — with file:line]
_No issues found._  ← if empty

## Naming violations

[actual name/path vs convention-expected — from naming-convention-lens]
_No issues found._  ← if empty

## Graph deltas

[orphans, dead links, off-path skills, missing refs — plugin surface only;
 omit this section for the tooling surface]
_No issues found._  ← if empty
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
