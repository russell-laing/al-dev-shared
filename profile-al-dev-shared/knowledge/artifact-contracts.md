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
| `al-dev-ticket` | Freshdesk ticket ID or URL, `.dev/` write access | `.dev/*-al-dev-ticket-ticket-context.md` (metadata), `.dev/ticket-context.md` (summary context), `.dev/ticket-reply.md` (drafted reply, optional) | `.dev/*-al-dev-ticket-ticket-context.md` (latest) | `.dev/*-al-dev-ticket-ticket-context.md` | latest ticket context file exists, is non-empty, contains ticket metadata section (ID, status, priority, summary), and was read after write in the current run |
| `al-dev-interview` | user interview transcript or interaction logs, `.dev/` write access | `.dev/*-al-dev-interview-notes.md` (raw Q&A), `.dev/*-al-dev-interview-requirements.md` (formal requirements with REQ/ACC/RISK/DEP tokens) | `.dev/*-al-dev-interview-notes.md` (context), then latest `.dev/*-al-dev-interview-requirements.md` (authoritative) | `.dev/*-al-dev-interview-requirements.md` | latest requirements file exists, is non-empty, contains at least one REQ token (REQ:REQ-*), and was read after write in the current run |
| `al-dev-explore` | user exploration request, repo context, `.dev/` write access | `.dev/*-al-dev-explore-findings.md` (structured exploration findings with file paths, code snippets, architectural patterns), optional updated `.dev/project-context.md` | `.dev/*-al-dev-explore-findings.md` (latest) | `.dev/*-al-dev-explore-findings.md` | latest findings file exists, is non-empty, contains at least ANSWER and FILES sections (structured findings format), and was read after write in the current run |
| `al-dev-plan-preflight` | user requirement or prior exploration findings, `.dev/` write access | `.dev/preflight-context.md` (context block consumed by al-dev-plan), `.dev/progress.md` when checkpointing | `.dev/progress.md`, then `.dev/preflight-context.md` | `.dev/preflight-context.md` | preflight context file exists, is non-empty, contains PREFLIGHT_CONTEXT schema fields (phase, requirements, scope, architect_model, user_context), and was read after write in the current run |
| `al-dev-plan` | user requirement, current repo context, `.dev/` write access; optional: `.dev/preflight-context.md` (written by `al-dev-plan-preflight` — enables Phase 0 Mode A/B resume); optional tributary findings consumed as Phase 0 context: `.dev/*-al-dev-explore-findings.md` (from /al-dev-explore), `.dev/*-al-dev-interview-requirements.md` (from /al-dev-interview), and findings files from /al-dev-perf or /al-dev-investigate | `.dev/*-al-dev-plan-solution-plan.md`, `.dev/progress.md` when checkpointing | `.dev/progress.md`, latest `.dev/*-al-dev-plan-solution-plan.md` | `.dev/*-al-dev-plan-solution-plan.md` | latest solution plan file exists, is non-empty, and was read after write in the current run |
| `al-dev-develop-orchestrate` | latest `.dev/*-al-dev-plan-solution-plan.md` | `.dev/progress.md`, `.dev/*-al-dev-develop-progress.md`, `.dev/*-al-dev-develop-checklist.md`, `.dev/*-al-dev-develop-scope.md`, `.dev/*-al-dev-develop-phase4-handoff.md` | `.dev/progress.md`, latest `.dev/*-al-dev-develop-progress.md`, latest `.dev/*-al-dev-develop-checklist.md`, latest `.dev/*-al-dev-develop-scope.md`, latest solution plan only if the resume pack is missing or contradictory | `.dev/*-al-dev-develop-phase4-handoff.md` | current Phase 4 handoff exists, is non-empty, and was read before telling the user implementation is ready for review |
| `al-dev-review-develop` | latest `.dev/*-plugin-review-preflight.md`, latest `.dev/*-al-dev-develop-phase4-handoff.md` | `.dev/*-plugin-review-preflight.md`, `.dev/*-al-dev-develop-code-review.md`, `.dev/compile-errors.log` when compile verification runs | latest `.dev/*-plugin-review-preflight.md`, latest `.dev/*-al-dev-develop-phase4-handoff.md`, latest `.dev/*-al-dev-develop-code-review.md` only for context, never as a substitute for the current preflight or handoff | `.dev/*-al-dev-develop-code-review.md` | current review-preflight context has been read, current Phase 4 handoff artifact has been read, current compile verification result has been read, and current code-review artifact exists and has been read before any clean/ready claim |
| `al-dev-fix` | user bug description, repo context, compile/lint workflow when verification is needed | `.dev/compile-errors.log` when compile verification runs | request-driven only; do not assume durable fix-state resume artifacts | none | current compile/lint verification output or an explicit bounded verification result has been produced and read before claiming the fix is complete |
| `al-dev-commit` | staged changes, project instructions, optional `.dev/file-sizes.json`, `.dev/compile-errors.log` when AL-affecting | commit-analysis outputs already produced by the workflow, `.dev/compile-errors.log` when Step 4a runs | staged state is authoritative; do not resume from stale commit artifacts without re-reading the staged diff and required context files | commit-ready staged set after the analysis gate; no downstream markdown handoff file | current staged diff has been read, any required compile evidence has been read for the current staged state, and commit-readiness has been confirmed before saying the staged set is ready |
| `al-dev-lint` | current AL project or provided compile log | `.dev/compile-errors.log`, `.dev/*-al-dev-lint-lint-report.md` | provided log path when explicitly supplied, otherwise fresh `.dev/compile-errors.log`, then latest lint report only for context | `.dev/*-al-dev-lint-lint-report.md` | current compile output and current lint report have been read before claiming the project is clean or the lint pass is complete |

## Failure Handling

- Missing required input artifact: stop and report the missing file pattern.
- Missing handoff artifact: refuse the downstream step and name the missing handoff file.
- Missing or stale success evidence: regenerate it when the workflow can, otherwise refuse the final claim.
- Contradictory resume artifacts: stop and ask instead of silently choosing a branch.
