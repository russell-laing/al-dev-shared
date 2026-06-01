---
name: plugin-health-report
description: >-
  Report phase of the plugin health sweep. Reads a findings file written by
  /plugin-health-discover, ranks findings, writes the dossier, optionally
  refreshes the dependency graph, and presents results to the user.
  Called by /plugin-health-audit; can also be run standalone against an existing
  findings file to re-rank or reformat without re-dispatching lenses.
argument-hint: "[--findings <path>] [--surface plugin|tooling]"
---

# Skill: /plugin-health-report

Report phase of the health sweep. Reads a findings file and writes the dossier.

## Phase 0 — Locate findings file

If `--findings <path>` is passed, read that file.

Otherwise, find the most recent findings file for each surface requested:
```bash
ls -t /Users/russelllaing/al-dev-shared/docs/health/*-findings.md 2>/dev/null | head -2
```

If no findings file exists, report: "No findings file found. Run /plugin-health-audit first." and stop.

## Phase 1 — Parse findings

Read the findings file. Extract each `### <Lens Name> Findings` block.
Parse each finding line: `- **[name]** | [Severity] | [observation] | [fix]`

Note any "Failed lenses" listed at the foot of the file.

## Phase 2 - Rank and Write Dossier

Order findings High → Medium → Low, grouped by dimension (design before quality
before naming), then by object (agent before skill). Pick the top 5 ranked actions
for the summary.

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

## Phase 3 — Refresh dependency graph (plugin surface only)

If the findings file is for the plugin surface, run:

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate-plugin-graph.py
```

The generator writes `docs/al-dev-plugin-graph.md` and exits 0 even on parse errors.

## Phase 4 — Present to user

Print, per surface: dossier path + severity counts + the top action.
List any failed lenses.
Ask: "Review the dossier and run `/al-dev-map-suggestions-verify` on the items you accept?"
Do not edit any source file.
