---
name: plugin-health
description: >-
  Suggestions-only health sweep of the al-dev-shared plugin surfaces. Dispatches
  design + quality + naming lenses with a per-surface file list, ranks findings,
  and writes one dossier per surface to docs/health/. Always refreshes the
  dependency graph for the plugin surface. Never auto-edits source. Triggers on:
  "plugin health", "health sweep", "audit the plugin", "check plugin health".
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|all]"
---

# Skill: /plugin-health

Standing self-healing entry point. Detects drift across both plugin surfaces and
consolidates suggestions into one ranked dossier per surface. Nothing is
auto-edited — the loop is: `/plugin-health` (detect) → dossier (review) →
`/plan-map-changes` (rubber-duck accepted items) → plan → execute.

Implemented as two sub-skills:
- `/plugin-health-discover` — builds file lists, aggregates context, dispatches lenses, writes findings file
- `/plugin-health-report` — reads findings file, ranks, writes dossier, refreshes graph, presents

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
