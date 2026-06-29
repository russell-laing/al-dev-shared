---
name: analyze-skill-design
description: >-
  Analyze profile-al-dev-shared plugin architecture for improvement opportunities,
  then write concrete Atomise / Connect / Merge / Promote suggestions to the
  Observations section of docs/skills-map.md. Use whenever you want
  strategic recommendations for making the plugin easier to maintain or more
  composable — including when someone asks "should these skills be merged?",
  "what patterns could be shared?", "is this skill doing too much?", "how can
  we simplify the plugin?", or "what's missing from the plugin?". Run after
  /review-skill-map so the map is accurate before analysis begins.
  Triggers on: "analyze skill design", "suggest skill improvements",
  "atomise skill", "merge agents", "skill architecture review",
  "optimize skill design", "skill improvement suggestions".
argument-hint: "[focus: atomise|connect|merge|all]"
---

# Skill: /analyze-skill-design

Strategic analysis of the al-dev plugin architecture. Reads the current plugin
map, applies four analytical lenses, and writes concrete improvement suggestions
to the `## Observations` section of `docs/skills-map.md`.

Run `/review-skill-map` first if the map may be out of date.

---

## Phase 1 — Discovery

Invoke `/discover-skill-design`. Pass the focus argument if one was supplied.

Receive from `/discover-skill-design`:
- **working_lists**: `agent_usage_counts`, `phase_counts`, `handoff_chains`,
  `no_agent_skills`, `preplanning_tributaries`, `layer1_diagram_content`
- **candidate_lists**: Connect/Promote, Atomise/Absorb, Merge, Extend,
  Diagram/labelling gaps

---

## Phase 2 — Aggregate Findings (in parallel from Phase 1 dispatch)

Collect all returned findings blocks from the parallel lens dispatch. Parse each line:
`- **[subject]** | [Severity] | [observation] | [fix]`

Group by lens type to produce candidate lists for Phase 4:
- **Connect/Promote candidates** — from Shared Execution Backbone findings
- **Atomise/Absorb candidates** — from Complexity Outliers findings
- **Merge candidates** — from Near-Duplicate Shapes findings
- **Extend candidates** — from Handoff Chain Gaps findings
- **Diagram/labelling gaps** — from Pre-planning Skills findings

Keep the raw findings lines — they form the basis of Phase 4 suggestions.

---

## Phase 3 — Draft Suggestions, Inventory Tables, Diagram and Map

Invoke `/draft-map-suggestions --type skill`. Pass as context:
- The candidate lists from Phase 2 (Connect/Promote, Atomise/Absorb, Merge, Extend candidates with raw finding lines)
- The working lists from Phase 1 (agent usage counts, phase counts, file handoff chains,
  no-agent skills, pre-planning tributaries, Layer 1 diagram content)

`/draft-map-suggestions` handles: drafting suggestions, completing inventory tables,
dispatching the diagram generator, selecting the highest-leverage suggestion, and
writing to `docs/skills-map.md`.

---

## Phase 4 — Present to User

After `/draft-map-suggestions` completes and both files are written:

1. Print a one-line summary per suggestion (type + subject).
2. `/draft-map-suggestions` owns highest-leverage selection; preserve its
   `← highest leverage` marker rather than re-scoring here.
3. Print: `Workflow diagram written to docs/workflow-diagrams.md`
4. Ask: "Would you like to act on any of these now?"
