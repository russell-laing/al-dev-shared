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

## Phase 1 — Read the Agent Map and Build Working Lists

Read `docs/al-dev-agent-map.md` in full. Build these working lists:

1. **Tool inventory** — for every agent, record its tools list from the map.
2. **Model assignments** — for every agent, record its model.
3. **Caller map** — for every agent, record which skills spawn it.
4. **Single-use agents** — agents spawned by exactly one skill.
5. **Shared agents** — agents spawned by 2+ skills.
6. **Undocumented agents** — agents with "Not documented" for both Inputs and Outputs.
7. **Existing inline candidates** — agents already listed in `### Inline candidates`
   in `docs/al-dev-agent-map.md`.

If an argument was passed, restrict analysis to that lens:
`trim`, `remodel`, `split`, `inline`, `align`, or `all` / no argument = `all`.

Also run this command to get agent file paths:

```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" | sort
```

---

## Phase 2 — Parallel Lens Dispatch

Dispatch the relevant lens agents in a **single response** (parallel Agent tool calls).

For each lens, pass only the context fields it requires (per `knowledge/lens-invocation-patterns.md`).
Construct one dispatch prompt per lens:

**design-agent-lens-tool-hygiene:**
```
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
tool_inventory: {agent → [tools]}
```

**design-agent-lens-model-fit:**
```
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
model_assignments: {agent → model}
```

**design-agent-lens-scope-isolation:**
```
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
```

**design-agent-lens-caller-alignment:**
```
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
caller_map: {agent → [spawning skills]}
```

**design-agent-lens-usage-patterns:**
```
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
single_use_agents: [list]
already_inline_candidates: [list from docs/al-dev-agent-map.md]
```

Agents to dispatch based on the focus argument:
- `all` or no argument: dispatch all five simultaneously
  - `design-agent-lens-tool-hygiene`
  - `design-agent-lens-model-fit`
  - `design-agent-lens-scope-isolation`
  - `design-agent-lens-caller-alignment`
  - `design-agent-lens-usage-patterns`
- `trim`: dispatch only `design-agent-lens-tool-hygiene`
- `remodel`: dispatch only `design-agent-lens-model-fit`
- `split`: dispatch only `design-agent-lens-scope-isolation`
- `align`: dispatch only `design-agent-lens-caller-alignment`
- `inline`: dispatch only `design-agent-lens-usage-patterns`

Each agent returns one block headed `### [Lens Name] Findings`.

---

## Phase 3 — Aggregate Findings

Collect all returned findings blocks. Parse each line:
`- **[agent-name]** | [Severity] | [observation] | [fix]`

Group by lens type to produce candidate lists for Phase 4:
- **Trim candidates** — agents from Tool Hygiene findings
- **Remodel candidates** — agents from Model Fit findings
- **Split candidates** — agents from Scope Isolation findings
- **Align candidates** — agents from Caller Alignment findings
- **Inline candidates** — agents from Usage Patterns findings

Keep the raw findings lines — they form the basis of Phase 4 suggestions.

---

## Phase 5 — Draft Suggestions, Inventory Tables, Diagram and Map

Invoke `/draft-map-suggestions --type agent`. Pass as context:
- The candidate lists from Phase 3 (Trim, Remodel, Split, Align, Inline candidates with raw finding lines)
- The working lists from Phase 1 (tool inventory, model assignments, caller map,
  single-use agents, undocumented agents, existing inline candidates from docs/al-dev-agent-map.md)

`/draft-map-suggestions` handles: drafting suggestions, completing inventory tables,
dispatching the diagram generator, and writing to `docs/al-dev-agent-map.md`.

---

## Phase 6 — Present to User

After Phase 5 invocation completes and both files are written:

1. Print a one-line summary per suggestion (type + subject).
2. Mark the **highest-leverage** suggestion with `← highest leverage`.
3. Print: `Workflow diagram written to docs/al-dev-workflow-diagrams.md`
4. Ask: "Would you like to act on any of these now?"
