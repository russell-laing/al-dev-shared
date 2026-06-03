---
name: docs-health-cleanup
description: Use when docs/health has accumulated dated health reports, findings files, or current-session aliases and the goal is to reduce clutter without deleting live evidence, rewriting point-in-time records, or trusting stale recommendations.
---

# Docs Health Cleanup

## Overview

Use this when `docs/health/` has become noisy with dated audit artifacts. The rule is: verify which files are still live workflow inputs or active reference points, preserve point-in-time evidence as written, then remove or consolidate only the historical clutter.

## Workflow

1. Inspect the live surface before deciding what is historical:
   - `git status --short docs/health`
   - `find docs/health -maxdepth 1 -type f | sort`
   - `git ls-files 'docs/health/*.md'`
2. Classify each file before editing anything:
   - dated dossier: `docs/health/YYYY-MM-DD-*-health.md`
   - raw findings companion: `docs/health/YYYY-MM-DD-*-findings.md`
   - current alias: files such as `*-current.md`
   - active draft: uncommitted or same-session files still being edited
3. Verify whether a file is still referenced elsewhere:
   - search the repo broadly, not only `docs/` subtrees
   - prefer repo-wide `rg` with explicit excludes over a hand-picked directory list
4. Re-check same-day claims against live repo state before treating any report as cleanup-ready:
   - use `self-healing-report-review` style verification for counts, rankings, and "already fixed" claims
   - if a report is still the basis for an active plan or follow-up patch, keep it
5. Handle `*-current.md` aliases conservatively:
   - keep them while downstream plans, notes, or docs still reference them
   - if replacing them, move downstream references first
   - do not delete an alias only because a newer dated dossier exists
6. Preserve historical dossiers as point-in-time artifacts:
   - do not rewrite old findings to match the current repo
   - if an old report needs interpretation, add a newer follow-up artifact instead of mutating history
7. Remove only files that are both historical and unreferenced:
   - stale raw findings companions whose conclusions are captured by the paired health dossier
   - superseded aliases with no remaining references
   - abandoned drafts or partial outputs that were never adopted and are not cited
8. Finish with a narrow validation pass on the remaining `docs/health/` surface and the exact tracked-path diff.

## Cleanup Order

| Artifact type | Default action | Extra guard |
|---|---|---|
| Dated `*-health.md` dossier | Keep | Point-in-time record; do not rewrite for current truth |
| Dated `*-findings.md` companion | Remove only if redundant and unreferenced | Confirm the paired dossier or later plan preserves the needed evidence |
| `*-current.md` alias | Keep until references move | Search downstream docs and plans first |
| Same-day draft with local edits | Keep | Treat as active work, not cleanup fodder |
| Untracked abandoned output | Remove only if clearly unused | Check `git status --short` and repo references first |

## Reference Checks

Use commands in this order:

```bash
git status --short docs/health
find docs/health -maxdepth 1 -type f | sort
git ls-files 'docs/health/*.md'
rg -n "docs/health/[0-9]{4}-[0-9]{2}-[0-9]{2}.*\\.md|docs/health/.*-current\\.md" . \
  --glob '!docs/health/**' \
  --glob '!.git/**'
```

For dated findings files, check whether they still add unique evidence beyond the paired dossier:

```bash
for file in docs/health/*-findings.md; do
  base="${file%-findings.md}"
  for candidate in "${base}-health.md" "${base}-plugin-health.md" "${base}-tooling-health.md" "${base}-both-health.md"; do
    if [ -f "$candidate" ]; then
      printf '%s -> %s\n' "$file" "$candidate"
    fi
  done
done
```

## Required Validation

```bash
git diff --name-status -- docs/health
git status --short docs/health
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

If the cleanup removed or renamed a file that other tracked content referenced, re-run a targeted repo-wide `rg` for the old path and confirm no tracked references remain.

## Common Mistakes

- Deleting `*-current.md` aliases before moving downstream references
- "Refreshing" an old health report by editing the historical file in place
- Treating same-day findings as stale without checking whether a current plan still cites them
- Removing dirty-worktree drafts together with historical clutter in one sweep
- Deleting a findings companion before checking whether the paired dossier actually preserved its actionable evidence
- Searching only a few familiar directories and missing root-level docs, scripts, or tests that still cite the old path
