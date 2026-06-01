---
name: analyze-architectural-design
description: >-
  USE WHEN the user wants cross-surface architectural coherence analysis covering
  both skills and agents together — including "architectural review of skills and
  agents", "design review for the plugin", "should skills be split or merged?",
  "plugin has grown" / "feels bloated", or "cross-surface design analysis".
  Runs /analyze-skill-design then /analyze-agent-design sequentially and produces
  a synthesized cross-surface view. Distinct from /plugin-health-audit (holistic
  quality/naming/drift sweep); this skill focuses solely on structural coherence
  and fit between the skill and agent layers.
argument-hint: "[--skill-only | --agent-only]"
---

# Analyze Architectural Design

## Overview

Sequential skill-then-agent analysis followed by mandatory synthesis. Scope is
inferred before any dispatch; question type determines routing; prior health
findings are used as pre-scoping input to avoid re-discovering known issues.

## Step 0 — Scope Inference (before any dispatch)

Determine analysis scope from the user's request and any `--skill-only` or
`--agent-only` argument:

- `--skill-only` → run Phase 1 only, skip Phase 2, produce skill output only
- `--agent-only` → run Phase 2 only, skip Phase 1, produce agent output only
- No argument → check whether user named a specific skill or agent:
  - If user named a specific skill (`al-dev-develop`, etc.) → auto-infer `--skill-only`, confirm with user before dispatching
  - If user named a specific agent (`al-dev-developer`, etc.) → auto-infer `--agent-only`, confirm with user before dispatching
  - Otherwise → run both phases and Phase 3 synthesis (default)

**Do not dispatch any sub-skill until scope is confirmed.**

## Step 1 — Prior-Run Awareness

Before dispatching, check for recent plugin-health-audit findings:

```bash
ls -t docs/health/*-health.md 2>/dev/null | head -2
```

If a dossier exists dated within the last 7 days, skim its Observations section.
Carry any confirmed architectural findings forward as **pre-scoped context** to
pass to sub-skills — do not re-discover what is already known.

## Step 2 — Skill Architecture Analysis

If scope includes skills: invoke `/analyze-skill-design`.

This writes findings to `docs/al-dev-plugin-map.md` and returns candidate
lists (Connect/Promote, Atomise/Absorb, Merge, Extend).

Capture the returned candidate list as `skill_candidates` for Phase 3.

## Step 3 — Agent Architecture Analysis

If scope includes agents: invoke `/analyze-agent-design`.

This writes findings to `docs/al-dev-agent-map.md` and returns candidate
lists (Trim, Remodel, Split, Inline, Align).

Capture the returned candidate list as `agent_candidates` for Phase 3.

## Step 4 — Cross-Surface Synthesis

**This step is mandatory when both phases ran.** Do not skip it.

Using `skill_candidates` and `agent_candidates`, answer:

1. **Coupling gaps** — Are there skill handoffs that no agent is positioned to
   execute? (e.g., a Promote candidate with no matching agent scope)
2. **Model-complexity mismatch** — Do skill complexity tiers align with the
   model assigned to the agents they call?
3. **Shared patterns** — Do Merge or Connect candidates on the skill side
   require corresponding agent Remodel or Align changes to stay coherent?

Write a `## Cross-Surface Synthesis` section to `docs/al-dev-plugin-graph.md`
with one row per finding: `[surface] | [finding] | [linked suggestion]`.

## Step 5 — Regenerate Diagrams

After all analyses are complete and findings are written to docs/, regenerate the Mermaid
diagrams to reflect the updated map content:

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate-map-doc-sections.py
```

This regenerates:
- Layer 1 lifecycle diagrams in `docs/al-dev-skills-map.md`
- Layer 2 per-skill drilldowns with Phase<N> nodes
- Agent catalog and dependency graphs in `docs/al-dev-agent-map.md`

If the script exits non-zero, report the error but continue to Step 6 (results presentation).

## Step 6 — Present Results

1. Print the skill suggestions summary (one line each, highest-leverage marked).
2. Print the agent suggestions summary (one line each, highest-leverage marked).
3. Print the cross-surface synthesis table.
4. Confirm: "Diagrams regenerated."
5. Ask: "Would you like to act on any of these now?"
