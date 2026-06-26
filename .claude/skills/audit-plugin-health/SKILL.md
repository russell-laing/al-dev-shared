---
name: audit-plugin-health
description: >-
  Standing suggestions-only entry point for the al-dev-shared plugin surfaces. Dispatches
  the two-phase internal workflow `/discover-plugin-health` then
  `/report-plugin-health` across two separate sessions (mandatory fresh session
  boundary between discover and report) to dispatch design + quality + naming lenses with a
  per-surface file list, rank findings, and write one dossier per surface to
  docs/health/. Never auto-edits source — all outputs are read-only observations. Supports
  --resume to continue an interrupted sweep. Triggers on:
  "plugin health", "health sweep", "audit the plugin", "check plugin health".
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|naming|all] [--resume]"
workflow:
  stage: discover
  invoked-by: user
  repeatable: true
  inputs:
    - docs/al-dev-skills-map.md
    - docs/al-dev-agent-map.md
  next: [discover-plugin-health]
---

# Skill: /audit-plugin-health

Standing suggestions-only entry point. Detects drift across both plugin surfaces and
consolidates suggestions into one ranked dossier per surface. Nothing is
auto-edited — the loop is: `/audit-plugin-health` (detect) → dossier (review) →
`/record-plugin-dispositions` (record decisions) →
`/plan-plugin-findings` (rubber-duck accepted items) → plan → execute.

Implemented as a two-phase workflow across two sessions:

- **Session 1 — `/discover-plugin-health`:** builds file lists, aggregates context,
  dispatches lenses, writes findings file, then stops and recommends a fresh session.
- **Session 2 — `/report-plugin-health`:** reads findings file (auto-detected via
  breadcrumb), ranks, writes dossier, presents. Triggered by re-invoking
  `/audit-plugin-health` in a fresh session (Phase 0 detects the breadcrumb).

Read `.claude/knowledge/health-filter-contract.md` first and treat it as the
canonical source of truth for surface values, dimension values, defaults,
findings metadata, legacy `unknown`, and resume mismatch handling.

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md` — emit a phase-proof block at each phase boundary before reporting completion or updating `.dev/health-loop-state.md`.

## Resuming Incomplete Sweeps

If a sweep is interrupted by session limits:

1. **Check existing lens output:**

   ```bash
   find .dev -maxdepth 1 -name 'plugin-health-lens-*.json' | wc -l
   ```

2. **Re-invoke with resume flag:**

   ```bash
   /audit-plugin-health --surface <same-surface> --dimension <same-dimension> --resume
   ```

   The skill detects completed lenses from prior session, skips them, and runs only missing ones.

3. **Final dossier will aggregate all lens results** (prior session + current session)

## Phase 0 — Check for discover breadcrumb

Read `.dev/health-loop-state.md` if it exists (schema:
`.claude/knowledge/health-loop-state-contract.md`).

- If `stage_completed = discover-plugin-health`: skip Phase 1. Extract all paths
  from `next_inputs` as the findings file path(s) for Phase 2. Jump to Phase 2.
- If `next_command` names a different, later loop step: warn the user that a prior
  loop is in flight, and ask whether to continue here or follow the pointer.
- If `next_command` is `none`, or the file is absent: proceed to Phase 1 normally.

## Phase 1 — Run discover

Invoke `/discover-plugin-health`, passing through all arguments received:
`/discover-plugin-health [--surface <value>] [--dimension <value>]`

`/discover-plugin-health` writes one findings file per surface to `docs/health/`.
Collect the findings file path(s) it returns.

After `/discover-plugin-health` completes, it writes a fresh session breadcrumb and
instructs the user to start a new session. **Stop here — do not proceed to Phase 2
in the same session.** Phase 2 is reached only when the user re-invokes
`/audit-plugin-health` in a fresh session and Phase 0 detects the
`discover-plugin-health` breadcrumb.

## Phase 2 — Run report

For each findings file path returned by Phase 1, invoke:
`/report-plugin-health --findings <path>`

`/report-plugin-health` writes the dossier and presents results to the user.
