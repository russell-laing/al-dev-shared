# Correction Patterns

Canonical table of recurring correction patterns found during health-loop plan
review. Referenced by `revise-health-plan` Phase correction-classification.

## Pattern Table

| Review finding | Canonical correction |
|---|---|
| Commit subjects violate convention | `<emoji> type(scope): subject`, full subject ≤72 chars, subject-only (tool project — no body) |
| A task edits the **executor** skill (`implement-health-plan/SKILL.md`) | Move it **last**, add a restart boundary: stop + re-invoke before Phase 2/3 close-back |
| Bare `git status` can't pass in a dirty worktree | Path-scope every check: `git status --short -- <task-paths>`; forbidden scan over added lines only (`git diff --unified=0`) |
| A grep "passes" on pre-existing text | Bound it (frontmatter-only via `awk`, fixed-string `grep -F`, or a strict measurement that exits non-zero) |
| A task changes a skill's first description sentence | Regenerate + stage the derived `docs/maintainer-tooling.md` |
| A task is dropped (re-dispositioned) | Renumber remaining tasks contiguously; update the Goal count and Provenance range |
