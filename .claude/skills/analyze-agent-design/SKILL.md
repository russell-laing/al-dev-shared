---
name: analyze-agent-design
description: >-
  Analyze profile-al-dev-shared agents for design quality and write
  concrete Trim / Remodel / Split / Inline / Align suggestions to the
  Observations section of docs/al-dev-agent-map.md. Use whenever you want
  strategic recommendations for making agents leaner, better-modelled, or
  better-documented — including when someone asks "is this agent doing too
  much?", "what tools does this agent not need?", "are any agents over-
  allocated on model?", or "how can we improve agent quality?". Run after
  /review-agent-map so the map is accurate before analysis begins.
  Triggers on: "analyze agent design", "agent quality review",
  "review agent quality", "agent improvement suggestions".
argument-hint: "[focus: trim|remodel|split|inline|align|all]"
---

# Skill: /analyze-agent-design

Strategic analysis of al-dev agent files. Reads the current agent map,
applies five analytical lenses, and writes concrete improvement suggestions
to the `## Observations` section of `docs/al-dev-agent-map.md`.

Run `/review-agent-map` first if the map may be out of date.

---

## Phase 1 — Discovery

Invoke `/discover-agent-design`. Pass the focus argument if one was supplied.

Receive from `/discover-agent-design`:
- **working_lists**: `tool_inventory`, `model_assignments`, `caller_map`,
  `single_use_agents`, `shared_agents`, `undocumented_agents`,
  `existing_inline_candidates`
- **candidate_lists**: Trim, Remodel, Split, Align, Inline candidates

---

## Phase 2 — Aggregate Findings (in parallel from Phase 1 dispatch)

Collect all returned findings blocks from the parallel lens dispatch. Parse each line:
`- **[agent-name]** | [Severity] | [observation] | [fix]`

Group by lens type to produce candidate lists for Phase 4:
- **Trim candidates** — agents from Tool Hygiene findings
- **Remodel candidates** — agents from Model Fit findings
- **Split candidates** — agents from Scope Isolation findings
- **Align candidates** — agents from Caller Alignment findings
- **Inline candidates** — agents from Usage Patterns findings

Keep the raw findings lines — they form the basis of Phase 4 suggestions.

---

## Phase 3 — Draft Suggestions, Inventory Tables, Diagram and Map

Invoke `/draft-map-suggestions --type agent`. Pass as context:
- The candidate lists from Phase 2 (Trim, Remodel, Split, Align, Inline candidates with raw finding lines)
- The working lists from Phase 1 (tool inventory, model assignments, caller map,
  single-use agents, undocumented agents, existing inline candidates from docs/al-dev-agent-map.md)

`/draft-map-suggestions` handles: drafting suggestions, completing inventory tables,
dispatching the diagram generator, and writing to `docs/al-dev-agent-map.md`.

---

## Phase 4 — Present to User

After Phase 5 invocation completes and both files are written:

1. Print a one-line summary per suggestion (type + subject).
2. Mark the **highest-leverage** suggestion with `← highest leverage`.
3. Print: `Workflow diagram written to docs/al-dev-workflow-diagrams.md`
4. Ask: "Would you like to act on any of these now?"
