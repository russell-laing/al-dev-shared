---
name: write-superpowers-plan-commentary
description: Use when creating or appending review-only commentary for docs/superpowers/plans after rubber-ducking implementation risks, fixes, improvements, staging commands, generated artifacts, or verification claims.
---

# Write Superpowers Plan Commentary

Write paired commentary for a Superpowers plan after checking live repo state.
Commentary is review-only unless the user explicitly asks to patch the plan.

## Use When

- Source is under `docs/superpowers/plans/`.
- User says `rubber duck`, `commentary`, `improvements`, `fixes`, `another
  pass`, or names an existing `*-commentary.md` file.
- Goal is catching implementation blockers, misleading verification,
  staging/commit risks, generated-artifact gaps, or stale claims.

For broad recommendation-heavy reports outside `docs/superpowers/plans/`, prefer
`review-self-healing-report`.

## Path Rule

If the user gives only `docs/superpowers/plans/YYYY-MM-DD-topic.md`, write:

```text
docs/superpowers/plans/YYYY-MM-DD-topic-commentary.md
```

If the commentary exists, append a clearly labeled further-findings section.
Do not replace earlier findings unless asked.

## Workflow

1. Read the full source plan with line numbers and read existing commentary.
2. Check live repo state before judging claims:

   ```bash
   git status --short
   rg -n "git add|commit|generate|validate|markdownlint|workflow:|KEEP VERBATIM|BEGIN GENERATED|END GENERATED" docs/superpowers/plans/<plan>.md
   ```

3. Read exact files behind plan claims. For code snippets, run cheap syntax or
   reproduction checks in `/tmp` when practical. For commit tasks, compare
   planned `git add` commands with the dirty tree and generated outputs.
4. Classify only findings that matter for execution:
   - `Valid blocker`
   - `Valid but lower priority`
   - `Overstated`
   - `Stale`
   - `Unsupported`
5. For each finding, include source line refs, live evidence, execution risk,
   and the concrete correction.
6. Keep the source plan untouched unless explicitly asked to edit it.

## Commentary Shape

New files start with `# Rubber-Duck Commentary: <Plan Title>`, the source plan
path, a review-only note, then `## Findings`. Repeat passes append `## Further
Findings From Second Pass` or a later pass number.

## Friction Guards

| Friction | Guard |
| --- | --- |
| `docs/superpowers/plans/` is ignored, so `git status --short <file>` may be silent. | Verify with `test -f` or `ls`, then use `git status --short --ignored=matching <commentary>`. |
| Same-day plans contain unverified claims. | Re-run cheap live checks; mark unverified claims as `Overstated` or `Unsupported`. |
| Repeat passes can erase earlier review context. | Append a new section and preserve prior findings. |
| Staging commands can sweep unrelated work. | Check `git status --short` and require exact-path staging in the recommendation. |
| Generated artifacts are easy to omit from commits. | Trace each generator in the plan to the files it writes and compare with planned `git add`. |
| Verification snippets may not prove what they claim. | Check command ordering, cached-vs-working-tree diff usage, expected stdout, and failure modes. |

## Validation

Before reporting completion:

```bash
rg -n "Valid blocker|Valid but lower priority|Overstated|Stale|Unsupported|Further Findings" <commentary>
git diff -- <source-plan>
test -f <commentary>
git status --short --ignored=matching <commentary>
```

Report if the source plan diff is non-empty. Mention unrelated dirty files
briefly; do not stage or revert them.

## Scenario Tests

Pressure scenarios live in `tests/scenarios.yaml`; use them when changing this
skill.
