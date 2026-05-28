# Artifact Contracts

Shared artifact contract matrix for the main execution skills in `profile-al-dev-shared`.

Use this document when:
- deciding which artifacts a skill may claim as durable output
- resuming a partially completed workflow
- handing work from one skill to another
- deciding whether a final completion or validation claim is supported by current-run evidence

> New skills should be scaffolded from `templates/skill-template/` so this contract is honoured by default.

## Rules

1. Do not name a durable output here unless the current workflow already writes it or the implementation in this repo is being updated in the same change set to write it.
2. If multiple resume artifacts can exist, list them in strict read order.
3. If a downstream workflow depends on a handoff artifact, name the exact file pattern it expects.
4. Final completion, validation, “clean”, or “ready” claims require the success evidence listed for the current skill to exist and be read in the current run.
5. If the required handoff artifact or success evidence is missing, stop and report the missing file instead of guessing.

## Contract Matrix

| Skill | Required inputs | Durable outputs | Resume read order | Handoff artifact | Success evidence |
|------|---|---|---|---|---|
| `al-dev-plan` | user requirement, current repo context, `.dev/` write access | `.dev/*-al-dev-plan-solution-plan.md`, `.dev/progress.md` when checkpointing | `.dev/progress.md`, latest `.dev/*-al-dev-plan-solution-plan.md` | `.dev/*-al-dev-plan-solution-plan.md` | latest solution plan file exists, is non-empty, and was read after write in the current run |
| `al-dev-develop` | latest `.dev/*-al-dev-plan-solution-plan.md` | `.dev/progress.md`, `.dev/*-al-dev-develop-progress.md`, `.dev/*-al-dev-develop-checklist.md`, `.dev/*-al-dev-develop-scope.md`, `.dev/*-al-dev-develop-phase4-handoff.md` | `.dev/progress.md`, latest `.dev/*-al-dev-develop-progress.md`, latest `.dev/*-al-dev-develop-checklist.md`, latest `.dev/*-al-dev-develop-scope.md`, latest solution plan only if the resume pack is missing or contradictory | `.dev/*-al-dev-develop-phase4-handoff.md` | current Phase 4 handoff exists, is non-empty, and was read before telling the user implementation is ready for review |
| `al-dev-review-develop` | latest `.dev/*-al-dev-develop-phase4-handoff.md` | `.dev/*-al-dev-develop-code-review.md`, `.dev/compile-errors.log` when compile verification runs | latest `.dev/*-al-dev-develop-phase4-handoff.md`, latest `.dev/*-al-dev-develop-code-review.md` only for context, never as a substitute for the current handoff | `.dev/*-al-dev-develop-code-review.md` | current Phase 4 handoff artifact has been read, current compile verification result has been read, and current code-review artifact exists and has been read before any clean/ready claim |
| `al-dev-fix` | user bug description, repo context, compile/lint workflow when verification is needed | `.dev/compile-errors.log` when compile verification runs | `.dev/progress.md` only if future resilience work adds it; otherwise resume is request-driven and should not assume durable fix-state artifacts | none | current compile/lint verification output or an explicit bounded verification result has been produced and read before claiming the fix is complete |
| `al-dev-commit` | staged changes, project instructions, optional `.dev/file-sizes.json`, `.dev/compile-errors.log` when AL-affecting | commit-analysis outputs already produced by the workflow, `.dev/compile-errors.log` when Step 4a runs | staged state is authoritative; do not resume from stale commit artifacts without re-reading the staged diff and required context files | commit-ready staged set after the analysis gate; no downstream markdown handoff file | current staged diff has been read, any required compile evidence has been read for the current staged state, and commit-readiness has been confirmed before saying the staged set is ready |
| `al-dev-lint` | current AL project or provided compile log | `.dev/compile-errors.log`, `.dev/*-al-dev-lint-lint-report.md` | provided log path when explicitly supplied, otherwise fresh `.dev/compile-errors.log`, then latest lint report only for context | `.dev/*-al-dev-lint-lint-report.md` | current compile output and current lint report have been read before claiming the project is clean or the lint pass is complete |

## Failure Handling

- Missing required input artifact: stop and report the missing file pattern.
- Missing handoff artifact: refuse the downstream step and name the missing handoff file.
- Missing or stale success evidence: regenerate it when the workflow can, otherwise refuse the final claim.
- Contradictory resume artifacts: stop and ask instead of silently choosing a branch.
