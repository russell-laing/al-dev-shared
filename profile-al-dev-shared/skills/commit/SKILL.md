---
name: commit
description: >-
  Use when ready to commit staged changes — especially after development work
  where scope creep (unapproved field removals, extra file deletions, hallucinated
  changes) may have occurred. Chains /commit-preflight (analysis and
  confirmation) then /commit-execute (lint preflight and git execution).
argument-hint: "[optional args]"
---

# `/commit` — Atomic Commit Workflow

Thin orchestrator for the two-phase commit workflow:

- **Phase A** — `/commit-preflight`: validates the staged set, dispatches
  analysis and message-drafting agents, collects user confirmation, and persists
  the approved plan to `.dev/commit-preflight.md`.
- **Phase B** — `/commit-execute`: loads the approved plan, runs lint
  preflight and OOXML validation, dispatches the execution agent, handles hook
  failures via the classifier + fixer recovery pipeline, and summarises results.

You never run `git commit` yourself — always delegate to `/commit-execute`.

---

## Intent Preflight

Before proceeding, apply the canonical intent-preflight check from `knowledge/commit-intent-preflight.md`.

---

## Artifact Contract

This skill is governed by `knowledge/artifact-contracts.md`.

Do not claim the commit is complete or the staged set is ready until the success evidence named in `knowledge/artifact-contracts.md` for this skill has been produced and read in the current run.

---

## Phase A — Analysis and Confirmation

Use the Skill tool to invoke `/commit-preflight` with `$ARGUMENTS` (pass the user's original typed arguments verbatim).

Wait for the preflight skill to complete. If the preflight exits early due to any
of the following, stop here and do not proceed to Phase B:

- **Empty staged set** — tell the user to stage changes with `git add` then re-run
- **File integrity failure** — report the failed file name and line-count collapse
- **Compile errors** — report that staged AL changes have errors; link to the log
- **User cancellation at any confirmation gate** — leave staged files unchanged

---

## Phase B — Execution

After `/commit-preflight` completes, verify the approved plan was written:

```bash
ls -la .dev/commit-preflight.md 2>/dev/null
wc -l .dev/commit-preflight.md 2>/dev/null
```

If the file exists and is non-empty: use the Skill tool to invoke
`/commit-execute` with no arguments.

If the file is missing or empty: stop. Tell the user: "No approved commit plan
found in `.dev/commit-preflight.md`. Re-run `/commit` to restart the full
workflow, or run `/commit-preflight` manually then `/commit-execute`."

## Optional Next Steps

After commit completes, you can optionally:

- **Release notes:** Run `/release-notes` to auto-generate changelog from commits
- **Handoff documentation:** Run `/handoff` to create handoff summary for downstream teams
- **Code documentation:** Run `/document` to update inline docs and generate API reference
