---
name: superpowers-history-cleanup
description: Use when docs/superpowers/plans, docs/superpowers/specs, or tracked .dev execution artifacts have accumulated historical clutter and the goal is to preserve provenance in a durable summary while safely removing obsolete raw files.
---

# Superpowers History Cleanup

## Overview

Use this when `docs/superpowers/` or tracked `.dev/` execution artifacts have become cluttered with historical files. The rule is: create a durable history surface first, then remove raw artifacts only after external references and tracking policy are verified.

## When to Use

- `docs/superpowers/plans/*.md` or `docs/superpowers/specs/*.md` are still tracked after their active use ended
- Current docs need a low-noise historical index instead of many raw plan/spec files
- A maintainer wants to stop tracking generated scratch artifacts without losing evolution context
- Old specs may still be referenced, so deletion needs a conservative workflow
- Tracked `.dev/` logs, reports, or checkpoints have become historical artifacts and need the same provenance-preserving cleanup treatment

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
   - if a summarizer exists, generate the first draft from tracked plans/specs
   - if no summarizer exists, add one before large cleanup so the history stays repeatable
4. Review the history draft for present-tense guidance and rewrite it as historical context only.
5. Update `.gitignore` so raw `docs/superpowers/plans/` and `docs/superpowers/specs/` stay untracked while `README.md` and `history.md` remain trackable.
6. For tracked `.dev/` artifacts, preserve the active workflow files that are still serving as live state, but move or summarize historical reports before deleting them.
7. Remove raw plans after verifying no tracked docs outside `docs/superpowers/` still reference them.
8. Remove raw specs more conservatively:
   - keep any spec with live external references
   - migrate known references to `docs/superpowers/history.md` or another durable doc before deletion
   - delete only unreferenced or explicitly superseded specs
9. Run repo validators and re-check tracked `docs/superpowers/` and `.dev/` paths before finishing.

## Cleanup Order

| Artifact type | Default action | Extra guard |
|---|---|---|
| Raw plans | Remove from tracking after history exists | No external references outside `docs/superpowers/` |
| Raw specs | Keep unless clearly superseded or migrated | Migrate or preserve any referenced spec |
| Tracked `.dev/` reports and logs | Remove only after summarizing or relocating durable content | Keep active workflow state and current handoff artifacts |
| `README.md` | Track | Defines future policy |
| `history.md` | Track | Replaces raw-file discoverability |

## Reference Checks

Use commands in this order:

```bash
python3 scripts/summarize_superpowers_history.py --root . --output docs/superpowers/history.md
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
git status --short
```

If the summarizer test module does not exist yet, treat that as implementation work, not a reason to skip the rest of the safety checks.

## Common Mistakes

- Deleting raw files before `history.md` exists
- Treating raw specs like raw plans; specs need stricter retention rules
- Leaving direct links to deleted raw specs in tracked docs
- Hand-writing the historical summary in a way that will drift on the next cleanup
- Using historical summaries as current implementation guidance
