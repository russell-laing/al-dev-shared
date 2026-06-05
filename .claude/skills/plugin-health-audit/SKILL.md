---
name: plugin-health-audit
description: >-
  Suggestions-only health sweep of the al-dev-shared plugin surfaces. Dispatches
  design + quality + naming lenses with a per-surface file list, ranks findings,
  and writes one dossier per surface to docs/health/. Always refreshes the
  dependency graph for the plugin surface. Never auto-edits source. Triggers on:
  "plugin health", "health sweep", "audit the plugin", "check plugin health".
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|all] [--resume]"
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

Implemented as two sub-skills:

- `/plugin-health-discover` — builds file lists, aggregates context, dispatches lenses with per-lens disk streaming, writes findings file
- `/plugin-health-report` — reads findings file, ranks, writes dossier, refreshes graph, presents

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

`/plugin-health-report` writes the dossier, refreshes the graph (plugin surface only),
and presents results to the user.
