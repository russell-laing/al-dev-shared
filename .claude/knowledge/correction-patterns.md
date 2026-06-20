# Correction Patterns

Canonical table of recurring correction patterns found during health-loop plan
review. Referenced by `revise-health-plan` Phase correction-classification.

## Pattern Table

| Review finding | Canonical correction |
|---|---|
| Commit subjects violate convention | `<emoji> type(scope): subject`, full subject ≤72 chars, subject-only (tool project — no body) |
| A task edits the **executor** skill (`implement-health-plan/SKILL.md`) | Move it **last**, add a restart boundary: stop + re-invoke before Phase 2/3 close-back |
| Bare `git status` can't pass in a dirty worktree | Path-scope every check: `git status --short -- <task-paths>`; forbidden scan over added lines only (`git diff --unified=0`) |
| A task uses `git add -u` or `git add <dir>` in a dirty worktree | Path-scope staging to the exact task paths; for `docs/health/` ledger tasks add a Step 0 that commits any pre-existing dirty health files first, so a later `git add docs/health/` only stages this task's regenerated output. Author Step 0 in the fail-loud conditional form (`if ! git diff --quiet -- <paths> …; then git add …; git commit …; fi`) — never `git add … && git commit … \|\| echo`, whose `\|\| echo` masks genuine commit failures |
| A grep "passes" on pre-existing text | Bound it (frontmatter-only via `awk`, fixed-string `grep -F`, or a strict measurement that exits non-zero) |
| A `… \| grep <id>` check whose success is "no output" | Inverts the exit code — `grep` exits non-zero on no match, so the success case reads as a failed step. Invert it: `if … \| grep -q <id>; then echo "ERROR: still present"; exit 1; fi` |
| A conditional task branch is only partially implemented (e.g. "use `-compare` if materially different" but only the default branch has steps) | Resolve the fork at plan time (rubber-duck has the live evidence) or surface it at the revise user gate; the chosen branch must have its full steps spelled out — no unimplemented branches left in the task |
| A task changes a skill's first description sentence | Regenerate + stage the derived `docs/maintainer-tooling.md` |
| A task is dropped (re-dispositioned) | Renumber remaining tasks contiguously; update the Goal count and Provenance range |
| Spec content uses `YYYY-MM-DD` as path-pattern placeholders (e.g., in JSON schema examples) — the plan's own forbidden-pattern scan then catches these intentional examples | Replace `YYYY-MM-DD` with `<date>` in the spec content's path-pattern examples |
| A plan edits shared-surface files (`profile-al-dev-shared/`) and closes ledger events on task-local `grep`/`wc` checks alone, never running the repo's shared-surface validators | Add a validation-gate task after the last source edit (and any projection regen), before ledger close-back: chain `validate_harness_neutrality.py`, `validate-lens-agents.py`, `validate-knowledge-quality.py`, `scripts/tests/test_generate_agent_projections.py` with `&&` so any failure halts the plan; the task closes no events (`closes_event_ids: []`) |
