---
name: fix-knowledge-quality
description: >-
  Reads HIGH-severity knowledge quality tasks from the fix-task block produced
  by /audit-knowledge-quality, presents the HIGH-only task list, and
  conditionally dispatches one `al-dev-docs-writer` agent per issue when the
  user approves (or when --auto-fix is passed). Scope: HIGH severity only;
  execution is user-gated. A mandatory neutrality gate validates any
  shared-surface edits and blocks completion if forbidden harness tokens are
  found. Run /audit-knowledge-quality first if no audit file
  exists. Triggers on: "fix knowledge quality", "fix knowledge issues",
  "implement knowledge fixes", "address high knowledge findings".
argument-hint: "[--auto-fix]"
workflow:
  stage: derive
  invoked-by: user
  repeatable: true
  inputs:
    - docs/al-dev-knowledge-quality.md
  outputs:
    - profile-al-dev-shared/knowledge/
  next: [validate-plugin-neutrality]
---

# Fix Knowledge Quality

Converts HIGH-severity knowledge quality findings into actionable tasks and
optionally dispatches fix agents.

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md` — emit a phase-proof block at each phase boundary before reporting completion or updating `.dev/health-loop-state.md`.

## Dispatch policy

This skill's agent dispatch follows `../../knowledge/dispatch-fallback-contract.md`:
declare the preferred path (the `Agent` tool), run preflight (tool available,
arguments valid against the receiving contract), fall back deterministically on
failure, and log `preferred → outcome → fallback → reason`.

## Phase 0 — Locate audit file

```bash
ls -t /Users/russelllaing/al-dev-shared/docs/al-dev-knowledge-quality.md 2>/dev/null | head -1
```

If no file found: stop and report:

> No knowledge quality audit found. Run `/audit-knowledge-quality` first.

## Phase 1 — Parse HIGH findings

Read `docs/al-dev-knowledge-quality.md`. Locate the `## High-Priority Fix Tasks`
YAML block.

If the block is absent: stop and report:

> Audit file exists but has no structured task block. Re-run `/audit-knowledge-quality`
> to regenerate with the current format.

The `## High-Priority Fix Tasks` block is **valid** when it is that named block
containing a `tasks:` list with at least one entry, and each entry carries its
required fields (`file`, `issue_type`, `description`, `suggested_action`). If the
block is present but malformed — missing the `tasks:` list, empty, or with
entries missing required fields — treat it as **corrupted** and stop and report
with the same message as an absent block (re-run `/audit-knowledge-quality` to
regenerate).

If the block is present and valid, continue with the parsing steps below (still
within Phase 1).

Parse each task entry:

- `file`: path to the knowledge file with the issue
- `issue_type`: THIN, NO-CODE, or DEAD-REF
- `description`: one-line description
- `suggested_action`: what to do

Present parsed tasks to the user:

> Found {N} HIGH-severity knowledge issues:
>
> 1. [{issue_type}] `{file}` — {description}
>    Action: {suggested_action}
> ...

## Phase 2 — Choose execution mode

If `--auto-fix` was not passed, present the following prompt:

> How do you want to fix these issues?
>
> 1. Show task list only — I will fix them manually
> 2. Auto-fix — dispatch one fix agent per issue

If `--auto-fix` was passed at invocation, skip the prompt above and proceed
directly to Phase 3.

If [1]: print task list and exit.

If [2] (or --auto-fix passed): proceed to Phase 3.

## Phase 3 — Dispatch fix agents (auto-fix mode)

Before dispatching: confirm the dispatch template file exists.

```bash
ls .claude/knowledge/fix-knowledge-quality-dispatch.md
```

If absent, stop and restore it: `git checkout HEAD -- .claude/knowledge/fix-knowledge-quality-dispatch.md`

For each HIGH task, dispatch one `al-dev-shared:al-dev-docs-writer` agent
(`al-dev-shared:` is the plugin namespace prefix; see CLAUDE.md — Agent File
Format). Use the dispatch template in
`.claude/knowledge/fix-knowledge-quality-dispatch.md`, substituting `{file}`,
`{issue_type}`, `{description}`, `{suggested_action}` from the parsed task.

Wait for all agents to complete. Present each agent's summary.

## Phase 4 — Validate neutrality, then post-fix options

**Mandatory neutrality gate.** If any file edited in this run is under
`profile-al-dev-shared/`, automatically invoke `/validate-plugin-neutrality` (or run
`scripts/validate_harness_neutrality.py` directly) before offering any further choice.
If it reports forbidden harness tokens, surface them and stop — the fixes are not
complete until neutrality passes. If no shared file was edited, note "no shared-surface
edits — neutrality check not required" and continue.

Only after the neutrality result is known, ask:

> Neutrality: <passed | not required>. Choose a next step:
>
> 1. Re-run `/audit-knowledge-quality` to verify the fixes
> 2. Done — no further action

If [1]: invoke `/audit-knowledge-quality`.
If [2]: stop.
