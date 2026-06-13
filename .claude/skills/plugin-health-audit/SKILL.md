---
name: plugin-health-audit
description: >-
  Standing suggestions-only entry point for the al-dev-shared plugin surfaces. Dispatches
  the two-phase internal workflow `/plugin-health-discover` then
  `/plugin-health-report` to dispatch design + quality + naming lenses with a
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

Implemented as a two-phase internal workflow:

- `/plugin-health-discover` — builds file lists, aggregates context, dispatches lenses with per-lens disk streaming, writes findings file
- `/plugin-health-report` — reads findings file, ranks (see its ranking criteria), writes dossier, presents

Read `.claude/knowledge/health-filter-contract.md` first and treat it as the
canonical source of truth for surface values, dimension values, defaults,
findings metadata, legacy `unknown`, and resume mismatch handling.

## Resuming Incomplete Sweeps

If a sweep is interrupted by session limits:

1. **Check existing lens output:**

   ```bash
   ls -1 .dev/plugin-health-lens-*.json | wc -l
   ```

2. **Re-invoke with resume flag:**

   ```bash
   /plugin-health-audit --surface <same-surface> --dimension <same-dimension> --resume
   ```

   The skill detects completed lenses from prior session, skips them, and runs only missing ones.

3. **Final dossier will aggregate all lens results** (prior session + current session)

## Phase 1 — Run discover

Invoke `/plugin-health-discover`, passing through all arguments received:
`/plugin-health-discover [--surface <value>] [--dimension <value>]`

`/plugin-health-discover` writes one findings file per surface to `docs/health/`.
Collect the findings file path(s) it returns.

## Phase 2 — Run report

For each findings file path returned by Phase 1, invoke:
`/plugin-health-report --findings <path>`

`/plugin-health-report` writes the dossier and presents results to the user.
