---
name: plugin-health-audit
description: >-
  Standing suggestions-only entry point for the al-dev-shared plugin surfaces. Dispatches
  the two-phase internal workflow `/plugin-health-discover` then
  `/plugin-health-report` across two separate sessions (mandatory fresh-session
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
  next: [plugin-health-discover]
---

# Skill: /plugin-health-audit

Standing suggestions-only entry point. Detects drift across both plugin surfaces and
consolidates suggestions into one ranked dossier per surface. Nothing is
auto-edited — the loop is: `/plugin-health-audit` (detect) → dossier (review) →
`/record-health-dispositions` (record decisions) →
`/plan-health-findings` (rubber-duck accepted items) → plan → execute.

Implemented as a two-phase workflow across two sessions:

- **Session 1 — `/plugin-health-discover`:** builds file lists, aggregates context,
  dispatches lenses, writes findings file, then stops and recommends a fresh session.
- **Session 2 — `/plugin-health-report`:** reads findings file (auto-detected via
  breadcrumb), ranks, writes dossier, presents. Triggered by re-invoking
  `/plugin-health-audit` in a fresh session (Phase 0 detects the breadcrumb).

Read `.claude/knowledge/health-filter-contract.md` first and treat it as the
canonical source of truth for surface values, dimension values, defaults,
findings metadata, legacy `unknown`, and resume mismatch handling.

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md`: before reporting
any phase complete, advancing to the next phase, or updating
`.dev/health-loop-state.md`, emit a phase-proof block (observed command output
or file-existence check) binding to that phase's deliverable. A restated
intention is not proof.

## Resuming Incomplete Sweeps

If a sweep is interrupted by session limits:

1. **Check existing lens output:**

   ```bash
   find .dev -maxdepth 1 -name 'plugin-health-lens-*.json' | wc -l
   ```

2. **Re-invoke with resume flag:**

   ```bash
   /plugin-health-audit --surface <same-surface> --dimension <same-dimension> --resume
   ```

   The skill detects completed lenses from prior session, skips them, and runs only missing ones.

3. **Final dossier will aggregate all lens results** (prior session + current session)

## Phase 0 — Check for discover breadcrumb

Read `.dev/health-loop-state.md` if it exists (schema:
`.claude/knowledge/health-loop-state-contract.md`).

- If `stage_completed = plugin-health-discover`: skip Phase 1. Extract all paths
  from `next_inputs` as the findings file path(s) for Phase 2. Jump to Phase 2.
- If `next_command` names a different, later loop step: warn the user that a prior
  loop is in flight, and ask whether to continue here or follow the pointer.
- If `next_command` is `none`, or the file is absent: proceed to Phase 1 normally.

## Phase 1 — Run discover

Invoke `/plugin-health-discover`, passing through all arguments received:
`/plugin-health-discover [--surface <value>] [--dimension <value>]`

`/plugin-health-discover` writes one findings file per surface to `docs/health/`.
Collect the findings file path(s) it returns.

After `/plugin-health-discover` completes, it writes a fresh-session breadcrumb and
instructs the user to start a new session. **Stop here — do not proceed to Phase 2
in the same session.** Phase 2 is reached only when the user re-invokes
`/plugin-health-audit` in a fresh session and Phase 0 detects the
`plugin-health-discover` breadcrumb.

## Phase 2 — Run report

For each findings file path returned by Phase 1, invoke:
`/plugin-health-report --findings <path>`

`/plugin-health-report` writes the dossier and presents results to the user.
