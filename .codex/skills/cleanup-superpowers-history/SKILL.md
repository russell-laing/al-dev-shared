---
name: cleanup-superpowers-history
description: Use when docs/superpowers/plans, docs/superpowers/specs, or tracked .dev execution artifacts have accumulated historical clutter and the goal is to preserve provenance in a durable summary while safely removing obsolete raw files.
---

# Cleanup Superpowers History

## Overview

Use this when `docs/superpowers/` or tracked `.dev/` execution artifacts have become cluttered with historical files. The rule is: create a durable history surface first, then remove raw artifacts only after external references and tracking policy are verified.

## Workflow

1. Inspect current state before editing:
   - `git ls-files 'docs/superpowers/plans/*.md'`
   - `git ls-files 'docs/superpowers/specs/*.md'`
   - `git ls-files '.dev/*'`
   - `git status --short`
2. Create or refresh durable tracked docs first:
   - `docs/superpowers/history.md` for the historical timeline
   - `docs/superpowers/README.md` for tracking policy and current sources of truth
3. Prefer deterministic inventory over hand-written summary:
   - if a summarizer exists, generate a draft to a temporary path first and diff it before touching `docs/superpowers/history.md`
   - if no summarizer exists, do not automatically turn cleanup into tool-building work; either perform a smaller manual cleanup or split summarizer creation into a separate task
4. Review any draft history for present-tense guidance and rewrite it as historical context only before replacing the durable tracked file.
5. Verify the current tracking policy before editing `.gitignore`:
   - confirm whether the repo currently intends raw plans/specs to remain tracked, become untracked, or move elsewhere
   - change `.gitignore` only if that policy is explicit in current repo docs or the current task
6. For tracked `.dev` artifacts, preserve the active workflow files that are still serving as live state, but move or summarize historical reports before deleting them.
7. Remove raw plans after verifying no tracked docs outside `docs/superpowers/` still reference them.
8. Remove raw specs more conservatively:
   - keep any spec with live external references
   - migrate known references to `docs/superpowers/history.md` or another durable doc before deletion
   - delete only unreferenced or explicitly superseded specs
9. Apply the durable summary update only after the deletion set is proven safe.
10. Run repo validators and re-check tracked `docs/superpowers/`, `.dev/`, and policy files before finishing.

## Cleanup Order

| Artifact type | Default action | Extra guard |
| --- | --- | --- |
| Raw plans | Remove from tracking after history exists | No external references outside `docs/superpowers/` |
| Raw specs | Keep unless clearly superseded or migrated | Migrate or preserve any referenced spec |
| Tracked `.dev/` reports and logs | Remove only after summarizing or relocating durable content | Keep active workflow state and current handoff artifacts |
| `README.md` | Track | Defines future policy |
| `history.md` | Track | Replaces raw-file discoverability |

## Reference Checks

Use commands in this order:

```bash
tmp_history="$(mktemp)"
python3 scripts/summarize_superpowers_history.py --root . --output "$tmp_history"
diff -u docs/superpowers/history.md "$tmp_history" || true
rg -n "will|must|should|source of truth" docs/superpowers/history.md
git check-ignore -v docs/superpowers/plans/example.md docs/superpowers/specs/example.md
git ls-files docs/superpowers
git ls-files '.dev/*'
```

For deletion safety, search for references outside the historical tree before `git rm`:

```bash
for file in $(git ls-files 'docs/superpowers/specs/*.md'); do
  refs=$(rg -l "$file" --glob '!docs/superpowers/history.md' --glob '!docs/superpowers/plans/**' --glob '!docs/superpowers/specs/**' . || true)
  if [ -n "$refs" ]; then
    printf '%s\n%s\n\n' "$file" "$refs"
  fi
done
```

## Required Validation

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
python3 -m unittest scripts.tests.test_summarize_superpowers_history scripts.tests.test_validate_harness_neutrality scripts.tests.test_validate_knowledge_quality -v
git diff --name-status -- docs/superpowers .dev .gitignore
git status --short
```

If the cleanup removed or renamed any tracked historical artifact, re-run a targeted repo-wide `rg` for the old path and confirm no tracked references remain.

If the summarizer test module does not exist yet, treat that as implementation work, not a reason to skip the rest of the safety checks.

## Common Mistakes

- Deleting raw files before `history.md` exists
- Treating raw specs like raw plans; specs need stricter retention rules
- Leaving direct links to deleted raw specs in tracked docs
- Hand-writing the historical summary in a way that will drift on the next cleanup
- Using historical summaries as current implementation guidance
- Writing `history.md` in place before the deletion set has been proven safe
- Changing `.gitignore` because "that is how cleanup usually works" instead of verifying the repo's current policy first
