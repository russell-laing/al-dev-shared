---
name: commit
description: >-
  Use when ready to commit staged changes — especially after development work
  where scope creep (unapproved field removals, extra file deletions, hallucinated
  changes) may have occurred. Chains /commit-preflight (analysis and
  confirmation) then /commit-execute (lint preflight and git execution).
argument-hint: "[optional args]"
---

# Commit

Stages all modified files and creates a git commit with a descriptive message. Combines the preflight check (/commit-preflight) and execution (/commit-execute) in a single workflow.

## Execution

1. Run `/commit-preflight` to validate the commit context and prepare staging
2. If preflight passes, run `/commit-execute` to perform the actual commit
3. Verify git status after completion

This is a thin orchestration wrapper. For details on the preflight validation and commit-message formatting conventions, see `/commit-preflight` and `/commit-execute` skills.

## Optional Next Steps

After commit completes, your changes are committed to the local branch. You may optionally continue with:

- **`/document`** — Generate or update relevant documentation (if changes include API, workflow, or user-facing updates)
- **`/handoff`** — Prepare a handoff artifact for the next phase (knowledge transfer, runbook, or team notes)
- **`/release-notes`** — Write release notes summarizing this change for end users (for release-ready commits)

All three steps read `.dev/commit-artifacts/` as context. See the skill descriptions for details on when each step applies.
