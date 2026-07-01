---
name: commit
description: >-
  Use when ready to commit staged changes — especially after development work
  where scope creep (unapproved field removals, extra file deletions, hallucinated
  changes) may have occurred. Thin front door that chains /commit-preflight
  (analysis and confirmation) then /commit-execute (lint preflight and git execution).
argument-hint: "[optional args]"
---

# Commit

Stages all modified files and creates atomic git commits with descriptive
messages. This is a thin orchestration wrapper over the two-skill commit chain:
`/commit-preflight` (analysis and confirmation) then `/commit-execute` (lint
preflight and git execution).

## Execution

1. Run `/commit-preflight` to analyse staged changes, propose atomic commit
   groups, and collect approval. It writes the approved plan to
   `.dev/commit-preflight.md` and returns; it does not commit anything itself.
2. If preflight was approved, run `/commit-execute` to run lint preflight and
   OOXML validation and perform the git commits from `.dev/commit-preflight.md`.
3. Verify `git status` after completion.

For details on the preflight validation and commit-message formatting
conventions, see the `/commit-preflight` and `/commit-execute` skills.

## Optional Next Steps

After commit completes, your changes are committed to the local branch. You may
optionally continue with:

- **`/document`** — Generate or update relevant documentation (if changes
  include API, workflow, or user-facing updates).
- **`/handoff`** — Prepare a handoff artifact for the next phase (knowledge
  transfer, runbook, or team notes).
- **`/release-notes`** — Write release notes summarizing this change for end
  users (for release-ready commits).
