---
name: write-superpowers-plan-commentary
description: Use when reviewing docs/superpowers/plans, appending another adversarial pass to existing commentary, or creating a uniquely named grouped findings document without changing the source plan.
---

# Write Superpowers Plan Commentary

## Overview

Create traceable review-only artifacts from live repository evidence. Source
plans and earlier review text are immutable.

## Use When

- The source is under `docs/superpowers/plans/`.
- The user asks for commentary, rubber-ducking, another pass, or consolidation.

Use `review-self-healing-report` for recommendation-heavy reports outside this
directory.

## Artifact Modes

| Request | Output |
| --- | --- |
| First review | `<plan-stem>-commentary.md` |
| Another pass | Append to the same commentary |
| Group/consolidate | `<plan-stem>-consolidated-findings-<timestamp><timezone>.md` |

For unique names use `date '+%Y%m%dT%H%M%S%Z'`, then require `test ! -e`.

## Workflow

1. Read the full plan with line numbers and all existing commentary.
2. Before writing, snapshot ignored inputs with `shasum -a 256`; copy existing
   commentary to `/tmp` when appending or consolidating. `git diff` cannot prove
   an ignored, untracked plan is unchanged.
3. Check live state:

   ```bash
   git status --short
   rg -n "git add|commit|generate|validate|markdownlint|workflow:|KEEP VERBATIM|BEGIN GENERATED|END GENERATED" <plan>
   ```

4. Read exact files behind claims. Reproduce cheap snippets, trace generators,
   and compare staging with the dirty tree.
5. Keep execution-relevant findings only. Use `Valid blocker`,
   `Valid but lower priority`, `Overstated`, `Stale`, or `Unsupported`.
6. Each finding needs source lines, live evidence, execution risk, and a
   concrete correction.

## Repeated Passes

Treat earlier finding blocks as immutable. Compare every candidate against all
prior passes by target, violated contract, failure mode, and correction.

- Same failure with different wording or another example: duplicate; omit it.
- Stronger evidence: preserve the old block; add a labeled addendum if needed.
- Distinct executable failure: append under
  `## Further Findings From <Ordinal> Pass` using the next finding number.
- No novel evidence-backed finding: report that result without inventing one.

After appending, prove the saved commentary snapshot is a byte-identical prefix
of the new file.

## Lossless Consolidation

Create a separate timestamped artifact with source paths, executive assessment,
complete crosswalk, concern groups, and implementation order.

Copy every original finding block exactly once. Preserve its number, title,
classification, source references, evidence, risk, correction, and wording.
Only group headings, crosswalks, and synthesis prose may be new. Do not
paraphrase finding blocks or allow "equivalent formatting."

Parse source and destination by numbered `###` headings and assert:

- identical finding-number sets with no duplicates
- one block per number
- exact title and body equality
- all required finding fields are present

## Validation

```bash
test -f <artifact>
git status --short --ignored=matching -- <plan> <commentary> <artifact>
npx --yes markdownlint-cli2 <artifact>
```

Also compare pre/post hashes for source plan and source commentary, verify the
append-only prefix for later passes, and run the exact-block comparison for a
consolidation. Report unrelated dirty files; never stage, rewrite, or revert
them.

## Scenario Tests

Pressure scenarios live in `tests/scenarios.yaml`. Run RED without this skill,
then GREEN with it, before changing this contract.
