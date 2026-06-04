---
name: analyze-architectural-design
description: >-
  Cross-surface synthesis add-on for the health audit. Reads the latest health
  dossier(s) in docs/health/ and writes a cross-surface synthesis (coupling
  gaps, model-complexity mismatch, shared-pattern coherence) to
  docs/al-dev-plugin-synthesis.md. Run after /plugin-health-audit when you want the
  skill and agent findings tied together. Does not dispatch lenses itself.
  Triggers on: "cross-surface synthesis", "tie the findings together",
  "how do the skill and agent findings relate".
argument-hint: ""
---

# Analyze Architectural Design

A lean post-audit step. `/plugin-health-audit` already dispatches every design,
quality, and naming lens and ranks the results into a dossier per surface. This
skill adds the one thing the per-surface dossiers do not: a **cross-surface
synthesis** that relates the skill-layer findings to the agent-layer findings.

It dispatches no lenses and edits no source. Its only output is the living
synthesis doc `docs/al-dev-plugin-synthesis.md`, overwritten in place each run.

> **Why not `al-dev-plugin-graph.md`?** That file is regenerated wholesale by
> `scripts/generate-plugin-graph.py` (run on every plugin-surface audit and map
> sync), so any hand-written section there is silently clobbered. The synthesis
> gets its own stable living doc instead.

## Phase 0 — Locate the dossiers

```bash
ls -t /Users/russelllaing/al-dev-shared/docs/health/*-health.md 2>/dev/null | head -2
```

If no dossier exists, report: "No health dossier found. Run
`/plugin-health-audit` first." and stop.

## Phase 1 — Extract findings

Read the latest dossier(s). From each, collect:

- **skill-layer findings** — Design suggestions with verbs Atomise, Absorb,
  Connect, Merge, Promote, Move, Extend
- **agent-layer findings** — Design suggestions with verbs Trim, Remodel,
  Split, Inline, Align

## Phase 2 — Cross-surface synthesis

Using the two finding sets, answer:

1. **Coupling gaps** — Are there skill handoffs that no agent is positioned to
   execute? (e.g., a Promote candidate with no matching agent scope)
2. **Model-complexity mismatch** — Do skill complexity tiers align with the
   model assigned to the agents they call?
3. **Shared patterns** — Do Merge or Connect candidates on the skill side
   require corresponding agent Remodel or Align changes to stay coherent?

Write `docs/al-dev-plugin-synthesis.md` (overwrite in place) with a
`## Cross-Surface Synthesis` section, one row per finding:
`[surface] | [finding] | [linked suggestion]`. Use generic vocabulary (no
harness-specific tokens).

## Phase 3 — Present results

1. Print the cross-surface synthesis table.
2. Hand off: "Synthesis written to `docs/al-dev-plugin-synthesis.md`. Run
   `/plan-health-findings` to turn accepted findings into a plan."
