---
name: discover-agent-design
description: >-
  Internal discovery phase for agent design analysis. Reads the agent map, builds
  working lists, and dispatches design-agent lens agents. Returns candidate lists
  and working lists for synthesis. Called by /analyze-agent-design; can also be
  invoked standalone by health sweeps or other synthesis consumers.
  Output: structured context returned to caller (no file written).
argument-hint: "[focus: trim|remodel|split|inline|align|all]"
---

# Skill: /discover-agent-design

Discovery phase for agent design analysis. Returns **working_lists** (context built
from the agent map) and **candidate_lists** (findings from lens dispatch) to the
caller. Consumed by `/analyze-agent-design`'s synthesis phase, or by health sweeps
that need design-agent lens results without full synthesis.

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
```text
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
tool_inventory: {agent → [tools]}
```

**design-agent-lens-model-fit:**
```text
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
model_assignments: {agent → model}
```

**design-agent-lens-scope-isolation:**
```text
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
```

**design-agent-lens-caller-alignment:**
```text
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
caller_map: {agent → [spawning skills]}
```

**design-agent-lens-usage-patterns:**
```text
Analyze the following agent files. Apply your lens and return a findings block.
File list: [one path per line]
single_use_agents: [list]
already_inline_candidates: [agents already in ### Inline candidates in docs/al-dev-agent-map.md]
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

## Output

Return the following structured context to the caller:

**working_lists:**
- `tool_inventory`: {agent → [tools]}
- `model_assignments`: {agent → model}
- `caller_map`: {agent → [spawning skills]}
- `single_use_agents`: [list]
- `shared_agents`: [list]
- `undocumented_agents`: [list]
- `existing_inline_candidates`: [list]

**candidate_lists** (parsed from Phase 2 findings blocks):
- Trim candidates — from Tool Hygiene findings
- Remodel candidates — from Model Fit findings
- Split candidates — from Scope Isolation findings
- Align candidates — from Caller Alignment findings
- Inline candidates — from Usage Patterns findings
