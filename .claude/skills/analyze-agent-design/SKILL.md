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

For each agent, pass this prompt (substituting actual data from Phase 1):

```
Analyze the following agent files. Apply your lens and return a findings block.

## File list
/absolute/path/to/agent1.md
/absolute/path/to/agent2.md
[one path per line]

## Context from map analysis
Tool inventory (agent → tools):
[paste tool_inventory here]

Model assignments (agent → model):
[paste model_assignments here]

Caller map (agent → spawning skills):
[paste caller_map here]

Single-use agents (spawned by exactly one skill):
[comma-separated list]

Already-listed inline candidates:
[comma-separated list from docs/al-dev-agent-map.md]
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

## Phase 5 — Draft Suggestions

Write 3–6 high-quality suggestions. Skip patterns that don't yield a real
improvement.

Before writing each suggestion, check the current `## Observations` section —
skip anything already marked `← implemented`.

Use these templates:

```
**Trim: al-dev-<name>**
Observation: Tools list includes [tool]; system prompt body contains no [tool] usage.
Suggestion: Remove [tool] from the tools list in the agent frontmatter.
Trade-off: Minimal — tool wasn't used; tighter least-privilege posture.
```

```
**Remodel: al-dev-<name>**
Observation: Agent performs [task description]; currently assigned [current-model].
Suggestion: Change model to [new-model] — task [does/does not] require multi-file synthesis.
Trade-off: [Faster + cheaper / More capable]; justified because [reason].
```

```
**Split: al-dev-<name>**
Observation: System prompt describes [concern A] and [concern B] — separable concerns.
Suggestion: Extract [concern B] into a new agent al-dev-<new-name>.
Trade-off: New agent file to maintain; each agent's scope becomes narrower and easier to evolve.
```

```
**Inline: al-dev-<name>**
Observation: Spawned only by /skill-name; [N]-line system prompt; no Inputs/Outputs documented.
Suggestion: Absorb system prompt into /skill-name's dispatch block; delete the agent file.
Trade-off: Less indirection; agent no longer reusable if a second caller is added later.
```

```
**Align: al-dev-<name>**
Observation: /skill-name passes [file/param X]; agent Inputs table does not document [X].
Suggestion: Update the agent's Inputs table to reflect the actual caller contract.
Trade-off: Documentation-only change; prevents future caller confusion.
```

---

## Phase 6 — Complete Inventory Tables

Build the three inventory tables from your working lists in Step 1:

**Agents used by only one skill** — list each single-use agent and its
sole caller. These are Inline candidates if they are also simple.

**Agents with no inputs/outputs documentation** — list each. These are
"black box" agents — callers must read the spawning skill to understand
the contract.

**Potential shared agents** — list agent types spawned by 2+ skills. These
are candidates for caller-contract documentation in `knowledge/`.

---

## Phase 7 — Dispatch Diagram Generation

Dispatch `/al-dev-diagram-generator` to generate the workflow diagram. This skill
handles all diagram logic (Sub-steps A–D) and writes `docs/al-dev-workflow-diagrams.md`.

Pass `--caller-name analyze-agent-design` so the generated diagram references the correct command for re-runs.

---

## Phase 8 — Write Observations to `docs/al-dev-agent-map.md`

Replace the entire `## Observations` section (from the `## Observations`
heading to the end of the file) with:

```markdown
## Observations

> Generated by /analyze-agent-design on [today's date — substitute before writing].
> Run /review-agent-map first if the agent list has changed since this was written.

### Agents used by only one skill

- **al-dev-<name>** — used only by /skill-name
[one bullet per single-use agent]

### Agents with no inputs/outputs documentation

- **al-dev-<name>** — [one-line description of what it does]
[one bullet per undocumented agent]

### Potential shared agents

- **al-dev-<name>** — used by /skill-a, /skill-b
[one bullet per shared agent]

### Quality suggestions

[one suggestion block per finding in Trim/Remodel/Split/Inline/Align format]
```

Update `**Last updated:**` in the document header to today's date.

---

## Phase 9 — Present to User

After Phase 7 dispatch returns and both files are written:

1. Print a one-line summary per suggestion (type + subject).
2. Mark the **highest-leverage** suggestion with `← highest leverage`.
3. Print: `Workflow diagram written to docs/al-dev-workflow-diagrams.md`
4. Ask: "Would you like to act on any of these now?"
