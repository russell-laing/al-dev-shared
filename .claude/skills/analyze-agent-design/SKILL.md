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

## Step 1 — Read the Agent Map and Build Working Lists

Read `docs/al-dev-agent-map.md` in full. As you read, build these lists:

1. **Tool inventory** — for every agent, record its tools list from Layer 2.
2. **Model assignments** — for every agent, record its model.
3. **Caller map** — for every agent, record which skills spawn it (from "Spawned by").
4. **Single-use agents** — agents spawned by exactly one skill.
5. **Shared agents** — agents spawned by 2+ skills.
6. **Undocumented agents** — agents with "Not documented" for both Inputs and Outputs.

If an argument was passed, restrict analysis to that lens:
`trim`, `remodel`, `split`, `inline`, `align`, or `all` / no argument = `all`.

---

## Step 2 — Apply Five Analytical Lenses

### Lens 1 — Tool Hygiene (→ Trim)

For each agent, compare the tools list in Layer 2 against what the system
prompt body actually uses. Read the agent file:

```bash
cat profile-al-dev-shared/agents/<name>.md
```

Red flags:
- Agent described as "read-only" or analysis-only but has `Write` or `Edit`
- Agent has `Bash` but no commands are mentioned in the system prompt
- Agent has MCP tools but no MCP usage is described in the body

A tool present in the frontmatter but unused in the system prompt is a Trim
candidate.

### Lens 2 — Model Fit (→ Remodel)

For each agent, evaluate whether `sonnet` / `opus` / `haiku` is appropriate:

- **Haiku-appropriate:** Single-step retrieval, simple API calls, basic
  formatting — no multi-file reasoning needed
- **Sonnet (default):** Most implementation, code review, and analysis tasks
- **Opus justified:** Competitive design tasks, multi-file synthesis, complex
  reasoning requiring broad codebase understanding

An agent assigned `opus` for a single-step or single-file task, or `sonnet`
for a clearly haiku-appropriate task, is a Remodel candidate.

### Lens 3 — Scope Isolation (→ Split)

For each agent, read its system prompt body. Ask: does it describe two clearly
separable concerns?

Signals:
- System prompt contains two distinct "## Phase" or "## Mission" sections
  addressing unrelated outputs
- The Inputs and Outputs tables serve two different downstream consumers
- The description uses "and" to connect two distinct task categories

A system prompt with two separable concerns is a Split candidate.

### Lens 4 — Caller Alignment (→ Align)

For each agent, compare its documented Inputs/Outputs against how the spawning
skill(s) actually invoke it:

```bash
# Read how a skill spawns the agent
grep -A 20 "al-dev-<name>" profile-al-dev-shared/skills/<skill-name>/SKILL.md
```

Red flags:
- Spawning skill passes a file the agent's Inputs table doesn't list
- Agent's Outputs table names a file the spawning skill never reads
- Agent Inputs is "Not documented" but spawning skill passes structured prompt

A mismatch between caller behaviour and agent documentation is an Align
candidate.

### Lens 5 — Usage Patterns (→ Inline)

For single-use agents, ask: does the complexity justify a dedicated agent file?

Inline criteria (all three must apply):
- Spawned by exactly one skill
- System prompt body (after frontmatter) is fewer than 15 lines
- No Inputs or Outputs tables documented

An agent meeting all three is an Inline candidate. Before flagging, check the
existing `### Inline candidates` section in `docs/al-dev-agent-map.md` —
skip any agent already listed there.

---

## Step 3 — Draft Suggestions

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

## Step 4 — Complete Inventory Tables

Build the three inventory tables from your working lists in Step 1:

**Agents used by only one skill** — list each single-use agent and its
sole caller. These are Inline candidates if they are also simple.

**Agents with no inputs/outputs documentation** — list each. These are
"black box" agents — callers must read the spawning skill to understand
the contract.

**Potential shared agents** — list agent types spawned by 2+ skills. These
are candidates for caller-contract documentation in `knowledge/`.

---

## Step 5 — Write to `docs/al-dev-agent-map.md`

Replace the entire `## Observations` section (from the `## Observations`
heading to the end of the file) with:

```markdown
## Observations

> Generated by /analyze-agent-design on YYYY-MM-DD.
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

## Step 6 — Present to User

After writing the file:

1. Print a one-line summary per suggestion (type + subject).
2. Mark the **highest-leverage** suggestion with `← highest leverage`.
3. Ask: "Would you like to act on any of these now?"
