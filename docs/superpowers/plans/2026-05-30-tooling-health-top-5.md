# Tooling Health Top-5 Actions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the five highest-priority findings from the 2026-05-30 tooling health dossier — two targeted text fixes, one dispatch-template restructure across three skills, one suggestion-drafter extraction, and one plugin-health split.

**Architecture:** Tasks 1–2 are atomic text edits to existing SKILL.md files (no new files). Task 3 restructures Phase 2 dispatch templates in `analyze-agent-design`, `analyze-skill-design`, and `plugin-health` to send per-lens minimal context instead of the full context blob. Task 4 creates `.claude/skills/draft-map-suggestions/SKILL.md` parameterized by `--type agent|skill` and collapses phases 5–8 of both `analyze-*-design` skills into a single drafter dispatch. Task 5 creates two new skills (`plugin-health-discover`, `plugin-health-report`) with an intermediate findings file handoff, and reduces `plugin-health` to a thin router.

**Tech Stack:** SKILL.md markdown files in `.claude/skills/`; verification via `grep`, `wc -l`, `ls`; neutrality gate via `python3 scripts/validate_harness_neutrality.py`.

---

### Task 1: Remove `subagent_type` from audit-quality

**Files:**
- Modify: `.claude/skills/audit-quality/SKILL.md` (lines 96 and 113)

- [ ] **Step 1: Confirm both occurrences**

```bash
grep -n "subagent_type" /Users/russelllaing/al-dev-shared/.claude/skills/audit-quality/SKILL.md
```

Expected:
```
96:Agents to dispatch simultaneously (use `subagent_type` for each):
113:Agents to dispatch simultaneously (use `subagent_type` for each):
```

- [ ] **Step 2: Replace both occurrences**

In `.claude/skills/audit-quality/SKILL.md`, use Edit with `replace_all: true`:

old_string: ``Agents to dispatch simultaneously (use `subagent_type` for each):``

new_string: `Agents to dispatch simultaneously (spawn each in parallel):`

- [ ] **Step 3: Verify token is gone**

```bash
grep "subagent_type" /Users/russelllaing/al-dev-shared/.claude/skills/audit-quality/SKILL.md
```

Expected: empty output (zero lines).

- [ ] **Step 4: Run the neutrality validator**

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/validate_harness_neutrality.py /Users/russelllaing/al-dev-shared/.claude
```

Expected: exit 0, or pre-existing issues only (none mentioning `audit-quality`).

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/skills/audit-quality/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "fix(tooling): replace subagent_type with neutral dispatch language in audit-quality"
```

---

### Task 2: Define "independent suggestions" in plan-map-changes

**Files:**
- Modify: `.claude/skills/plan-map-changes/SKILL.md` (~line 100)

- [ ] **Step 1: Confirm the undefined gate**

```bash
grep -n "independent" /Users/russelllaing/al-dev-shared/.claude/skills/plan-map-changes/SKILL.md
```

Expected: exactly one line — `100:When there are 3+ independent suggestions, invoke ...` — with no definition anywhere.

- [ ] **Step 2: Insert the definition**

In `.claude/skills/plan-map-changes/SKILL.md`, use Edit:

old_string:
```
### Parallel exploration

When there are 3+ independent suggestions, invoke `superpowers:dispatching-parallel-agents`
before starting rubber-ducking.
```

new_string:
```
### Parallel exploration

Two suggestions are **independent** if they modify no overlapping files and neither
suggestion's output is an input to the other's rubber-duck phase. If suggestion A
writes a file that suggestion B must read before it can be rubber-ducked, B is
ordered after A.

When there are 3+ independent suggestions, invoke `superpowers:dispatching-parallel-agents`
before starting rubber-ducking.
```

- [ ] **Step 3: Verify definition is present**

```bash
grep -A 4 "Two suggestions are" /Users/russelllaing/al-dev-shared/.claude/skills/plan-map-changes/SKILL.md
```

Expected: the three definition lines followed by a blank line.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/skills/plan-map-changes/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "fix(tooling): define independent suggestions in plan-map-changes parallel gate"
```

---

### Task 3: Per-lens minimal-context dispatch

**Files:**
- Modify: `.claude/skills/analyze-agent-design/SKILL.md` (Phase 2 template)
- Modify: `.claude/skills/analyze-skill-design/SKILL.md` (Phase 2 template)
- Modify: `.claude/skills/plugin-health/SKILL.md` (Phase 2.1 templates)

`knowledge/lens-invocation-patterns.md` is the authoritative per-lens field table. Currently all three skills pass a monolithic full-context block to every lens. This task replaces each monolithic block with per-lens minimal dispatch prompts.

#### 3a — analyze-agent-design Phase 2

- [ ] **Step 1: Confirm the monolithic block exists**

```bash
grep -n "Tool inventory (agent" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-agent-design/SKILL.md
```

Expected: one matching line inside Phase 2.

- [ ] **Step 2: Replace the monolithic template with per-lens blocks**

In `.claude/skills/analyze-agent-design/SKILL.md`, use Edit:

old_string:
```
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
```

new_string:
```
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
```

- [ ] **Step 3: Verify old block gone**

```bash
grep "Tool inventory (agent" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-agent-design/SKILL.md
```

Expected: empty output.

#### 3b — analyze-skill-design Phase 2

- [ ] **Step 4: Replace the monolithic template with per-lens blocks**

In `.claude/skills/analyze-skill-design/SKILL.md`, use Edit:

old_string:
```
For each agent, pass this prompt (substituting actual data from Phase 1):

```
Analyze the following skill files. Apply your lens and return a findings block.

## File list
/absolute/path/to/skills/skill-name/SKILL.md
[one path per line]

## Context from plugin map analysis
Agent usage counts (agent-type → skills that use it):
[paste agent_usage_counts here]

Phase counts (skill-name → count):
[paste phase_counts here]

No-agent skills:
[comma-separated list]

Handoff chains:
[paste handoff_chains here — skill → output-file → consuming-skill]

Pre-planning skills:
[comma-separated list]

Layer 1 diagram content:
[paste the Layer 1 diagram block from docs/al-dev-plugin-map.md]
```
```

new_string:
```
For each lens, pass only the context fields it requires (per `knowledge/lens-invocation-patterns.md`).
Construct one dispatch prompt per lens:

**design-skill-lens-shared-backbone:**
```
Analyze the following SKILL.md files. Apply your lens and return a findings block.
File list: [one path per line]
agent_usage_counts: {agent-type → [skills that spawn it]}
```

**design-skill-lens-complexity:**
```
Analyze the following SKILL.md files. Apply your lens and return a findings block.
File list: [one path per line]
phase_counts: {skill → phase count}
no_agent_skills: [list]
```

**design-skill-lens-near-duplicates:**
```
Analyze the following SKILL.md files. Apply your lens and return a findings block.
File list: [one path per line]
agent_usage_counts: {agent-type → [skills that spawn it]}
phase_counts: {skill → phase count}
```

**design-skill-lens-handoff-gaps:**
```
Analyze the following SKILL.md files. Apply your lens and return a findings block.
File list: [one path per line]
handoff_chains: {skill → [output files]}
```

**design-skill-lens-preplanning:**
```
Analyze the following SKILL.md files. Apply your lens and return a findings block.
File list: [one path per line]
preplanning_skills: [list]
layer1_diagram_content: [raw text of Layer 1 Mermaid diagram]
```
```

- [ ] **Step 5: Verify old block gone**

```bash
grep "Agent usage counts (agent-type" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-skill-design/SKILL.md
```

Expected: empty output.

#### 3c — plugin-health Phase 2.1 (resolve contradictory templates)

The current templates say "include only the fields this lens requires" but then list the full context block — contradicting the instruction. Replace with a lookup table and a minimal template.

- [ ] **Step 6: Fix the agent-lens template**

In `.claude/skills/plugin-health/SKILL.md`, use Edit:

old_string:
```
**For design-agent-lens-* agents:**
```
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Context (include only the fields this lens requires — see knowledge/lens-invocation-patterns.md):

tool_inventory: {mapping of agent → [tools]}
model_assignments: {mapping of agent → model}
caller_map: {mapping of agent → [spawning skills]}
single_use_agents: [list of agents with exactly one spawning skill]
already_inline_candidates: [single-use agents that could be inlined]
```
```

new_string:
```
**For design-agent-lens-* agents** — include only the per-lens fields from `knowledge/lens-invocation-patterns.md`:

| Lens | Context field(s) to include |
|------|-----------------------------|
| `design-agent-lens-tool-hygiene` | `tool_inventory` |
| `design-agent-lens-model-fit` | `model_assignments` |
| `design-agent-lens-scope-isolation` | *(file list only — no context fields)* |
| `design-agent-lens-caller-alignment` | `caller_map` |
| `design-agent-lens-usage-patterns` | `single_use_agents`, `already_inline_candidates` |

Template:
```
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Context:
[include only the field(s) for this lens per the table above]
```
```

- [ ] **Step 7: Fix the skill-lens template**

In `.claude/skills/plugin-health/SKILL.md`, use Edit:

old_string:
```
**For design-skill-lens-* agents:**
```
Analyze the following SKILL.md files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Context (include only the fields this lens requires — see knowledge/lens-invocation-patterns.md):

agent_usage_counts: {mapping of agent-type → [skill names that spawn it]}
phase_counts: {mapping of skill → phase count}
no_agent_skills: [list of skills with zero spawned agents]
handoff_chains: {mapping of skill → [output files]}
preplanning_skills: [pre-planning skill names (dashed arrows in Layer 1)]
layer1_diagram_content: [raw text of Layer 1 Mermaid diagram from docs/al-dev-plugin-map.md]
```
```

new_string:
```
**For design-skill-lens-* agents** — include only the per-lens fields from `knowledge/lens-invocation-patterns.md`:

| Lens | Context field(s) to include |
|------|-----------------------------|
| `design-skill-lens-shared-backbone` | `agent_usage_counts` |
| `design-skill-lens-complexity` | `phase_counts`, `no_agent_skills` |
| `design-skill-lens-near-duplicates` | `agent_usage_counts`, `phase_counts` |
| `design-skill-lens-handoff-gaps` | `handoff_chains` |
| `design-skill-lens-preplanning` | `preplanning_skills`, `layer1_diagram_content` |

Template:
```
Analyze the following SKILL.md files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Context:
[include only the field(s) for this lens per the table above]
```
```

- [ ] **Step 8: Verify contradiction resolved in plugin-health**

```bash
grep "tool_inventory:.*model_assignments:" /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health/SKILL.md
```

Expected: empty (the old consecutive-field list is gone).

- [ ] **Step 9: Commit all three files**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  .claude/skills/analyze-agent-design/SKILL.md \
  .claude/skills/analyze-skill-design/SKILL.md \
  .claude/skills/plugin-health/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "refactor(tooling): per-lens minimal-context dispatch in analyze-*-design and plugin-health"
```

---

### Task 4: Extract draft-map-suggestions skill

**Files:**
- Create: `.claude/skills/draft-map-suggestions/SKILL.md`
- Modify: `.claude/skills/analyze-agent-design/SKILL.md` (phases 5–8 → single drafter call)
- Modify: `.claude/skills/analyze-skill-design/SKILL.md` (phases 5–8 → single drafter call)

The new skill owns: drafting suggestions, completing inventory tables, dispatching the diagram generator, and writing to the map file. It is parameterized by `--type agent|skill`.

- [ ] **Step 1: Create the skill directory and file**

```bash
mkdir -p /Users/russelllaing/al-dev-shared/.claude/skills/draft-map-suggestions
```

Write `.claude/skills/draft-map-suggestions/SKILL.md` with this exact content:

```markdown
---
name: draft-map-suggestions
description: >-
  Drafts improvement suggestions from aggregated lens findings and writes them
  to the Observations section of the appropriate map document. Called by
  /analyze-agent-design (--type agent) and /analyze-skill-design (--type skill)
  after lens aggregation. Requires --type argument; not intended as a standalone
  user-facing entry point.
argument-hint: "--type agent|skill"
---

# Skill: /draft-map-suggestions

Converts aggregated lens findings into structured map observations. Requires
`--type agent` or `--type skill` to select the correct templates and output file.

---

## Phase 1 — Parse argument

Read the required `--type` argument:
- `--type agent` → writes to `docs/al-dev-agent-map.md`; uses Trim/Remodel/Split/Inline/Align vocabulary
- `--type skill` → writes to `docs/al-dev-plugin-map.md`; uses Atomise/Connect/Merge/Promote/Extend vocabulary

If `--type` is missing or not `agent`/`skill`, report the error and stop.

---

## Phase 2 — Receive aggregated findings

The caller passes findings as input context in the dispatch prompt.

For `--type agent`, expect: Trim candidates, Remodel candidates, Split candidates,
Align candidates, Inline candidates — from Phase 3 of `analyze-agent-design`.
Also receive the working lists from Phase 1 of `analyze-agent-design`: tool inventory,
model assignments, caller map, single-use agents, undocumented agents, existing inline candidates.

For `--type skill`, expect: Connect/Promote candidates, Atomise/Absorb candidates,
Merge candidates, Extend candidates, Diagram/labelling gaps — from Phase 3 of `analyze-skill-design`.
Also receive the working lists from Phase 1 of `analyze-skill-design`: agent usage counts,
phase counts, file handoff chains, no-agent skills, pre-planning tributaries.

---

## Phase 3 — Draft suggestions

Write 3–6 high-quality suggestions. Skip patterns that don't yield a real improvement.
Before writing each suggestion, check the current `## Observations` section of the
target map file — skip anything already marked `← implemented`.

**For `--type agent`**, use these templates:

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

**For `--type skill`**, use these templates:

```
**Atomise: /skill-name**
Observation: Phases N–M handle X; phases N–M handle Y — separable concerns.
Suggestion: Extract [phase group] into /new-skill-name.
Trade-off: New skill to learn; each skill's scope becomes narrower and clearer.
```

```
**Connect: /skill-a and /skill-b**
Observation: Both spawn [agent-type] with the same pattern but define it independently.
Suggestion: Document the canonical spawn pattern in knowledge/[pattern-name].md;
  have both skills reference it.
Trade-off: Small authoring cost; drift is prevented when the pattern needs updating.
```

```
**Merge: /skill-a + /skill-b**
Observation: /skill-b is /skill-a plus [small delta]; users must choose between two
  near-identical skills.
Suggestion: Add [delta] as an option to /skill-a; archive /skill-b.
Trade-off: Simpler skill list; /skill-a's interface becomes slightly broader.
```

```
**Promote: [agent usage pattern]**
Observation: [agent-type] is invoked by N skills. The invocation is copy-pasted
  rather than shared.
Suggestion: Write a canonical invocation template in knowledge/ and link from each
  skill that uses it.
Trade-off: One canonical source; callers adapt slightly to reference it.
```

```
**Extend: [gap description]**
Observation: The [X → Y → Z] chain is well-established but stops at Z.
Suggestion: A /new-skill-name that consumes Z's output would complete the natural
  workflow and enable [use case].
Trade-off: Adds scope; only worth building if the use case is frequent.
```

---

## Phase 4 — Complete inventory tables

**For `--type agent`**, build three inventory tables from the working lists supplied by the caller:

1. **Agents used by only one skill** — list each single-use agent and its sole caller.
2. **Agents with no inputs/outputs documentation** — list each (black-box agents).
3. **Potential shared agents** — list agents spawned by 2+ skills.

**For `--type skill`**, build three inventory tables:

1. **Agents used by only one skill** — list each single-use agent and its skill.
2. **Skills with no dedicated agent** — list each; note absorption candidates.
3. **Potential shared agents** — list agent types used by 2+ skills.

---

## Phase 5 — Dispatch diagram generation

Dispatch the `al-dev-diagram-generator` agent to generate the workflow diagram.
Pass the caller name so the diagram references the correct re-run command:
- For `--type agent`: pass `--caller-name analyze-agent-design`
- For `--type skill`: pass `--caller-name analyze-skill-design`

The generator writes `docs/al-dev-workflow-diagrams.md`.

---

## Phase 6 — Write observations to the map file

**For `--type agent`** — replace the entire `## Observations` section of `docs/al-dev-agent-map.md`:

```markdown
## Observations

> Generated by /analyze-agent-design on [today's date].
> Run /review-agent-map first if the agent list has changed since this was written.

### Agents used by only one skill

- **al-dev-<name>** — used only by /skill-name
[one bullet per single-use agent]

### Agents with no inputs/outputs documentation

- **al-dev-<name>** — [one-line description]
[one bullet per undocumented agent]

### Potential shared agents

- **al-dev-<name>** — used by /skill-a, /skill-b
[one bullet per shared agent]

### Quality suggestions

[one suggestion block per finding in Trim/Remodel/Split/Inline/Align format]
```

Update `**Last updated:**` in the document header to today's date.

**For `--type skill`** — replace the entire `## Observations` section of `docs/al-dev-plugin-map.md`:

```markdown
## Observations

> Generated by /analyze-skill-design on [today's date].
> Run /review-skill-map first if the skill list has changed since this was written.

### Agents used by only one skill

[bullet per agent: "- **agent-type** — used only by /skill-name"]

### Skills with no dedicated agent (skill does the work itself)

[bullet per skill: "- **/skill-name** — [one-line description]"]

### Potential shared agents not yet extracted

[bullet per shared agent: "- **agent-type** — used by /skill-a, /skill-b, /skill-c"]

### Architectural suggestions

[one suggestion block per finding in Atomise / Connect / Merge / Promote / Extend format]

### Extension opportunities

[1–2 forward-looking Extend blocks, or "None identified at this time."]
```

Update `**Last updated:**` in the document header to today's date.

---

## Phase 7 — Present to user

After Phase 5 dispatch returns and the map file is written:

1. Print a one-line summary per suggestion (type + subject).
2. Mark the **highest-leverage** suggestion with `← highest leverage`.
3. Print: `Workflow diagram written to docs/al-dev-workflow-diagrams.md`
4. Ask: "Would you like to act on any of these now?"
```

- [ ] **Step 2: Verify the file was written**

```bash
ls -la /Users/russelllaing/al-dev-shared/.claude/skills/draft-map-suggestions/SKILL.md
wc -l /Users/russelllaing/al-dev-shared/.claude/skills/draft-map-suggestions/SKILL.md
```

Expected: file exists, ≥ 100 lines.

- [ ] **Step 3: Slim analyze-agent-design — collapse phases 5–8 into one drafter call**

In `.claude/skills/analyze-agent-design/SKILL.md`, use Edit:

old_string:
```
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
```

new_string:
```
## Phase 5 — Draft Suggestions, Inventory Tables, Diagram and Map

Invoke `/draft-map-suggestions --type agent`. Pass as context:
- The candidate lists from Phase 3 (Trim, Remodel, Split, Align, Inline candidates with raw finding lines)
- The working lists from Phase 1 (tool inventory, model assignments, caller map,
  single-use agents, undocumented agents, existing inline candidates from docs/al-dev-agent-map.md)

`/draft-map-suggestions` handles: drafting suggestions, completing inventory tables,
dispatching the diagram generator, and writing to `docs/al-dev-agent-map.md`.
```

- [ ] **Step 4: Rename Phase 9 to Phase 6 in analyze-agent-design**

In `.claude/skills/analyze-agent-design/SKILL.md`, use Edit:

old_string:
```
## Phase 9 — Present to User
```

new_string:
```
## Phase 6 — Present to User
```

- [ ] **Step 5: Slim analyze-skill-design — collapse phases 5–8 into one drafter call**

In `.claude/skills/analyze-skill-design/SKILL.md`, use Edit:

old_string:
```
## Phase 5 — Draft Suggestions

Write 3–6 high-quality suggestions. Skip patterns that don't yield a real
improvement. Before writing a suggestion, check the current `## Observations`
section — if a suggestion identical or equivalent to yours is already marked
`← implemented`, skip it. Use these templates:

```
**Atomise: /skill-name**
Observation: Phases N–M handle X; phases N–M handle Y — separable concerns.
Suggestion: Extract [phase group] into /new-skill-name.
Trade-off: New skill to learn; each skill's scope becomes narrower and clearer.
```

```
**Connect: /skill-a and /skill-b**
Observation: Both spawn [agent-type] with the same pattern but define it independently.
Suggestion: Document the canonical spawn pattern in knowledge/[pattern-name].md;
  have both skills reference it.
Trade-off: Small authoring cost; drift is prevented when the pattern needs updating.
```

```
**Merge: /skill-a + /skill-b**
Observation: /skill-b is /skill-a plus [small delta]; users must choose between two
  near-identical skills.
Suggestion: Add [delta] as an option to /skill-a; archive /skill-b.
Trade-off: Simpler skill list; /skill-a's interface becomes slightly broader.
```

```
**Promote: [agent usage pattern]**
Observation: [agent-type] is invoked by N skills. The invocation is copy-pasted
  rather than shared.
Suggestion: Write a canonical invocation template in knowledge/ and link from each
  skill that uses it.
Trade-off: One canonical source; callers adapt slightly to reference it.
```

```
**Extend: [gap description]**
Observation: The [X → Y → Z] chain is well-established but stops at Z.
Suggestion: A /new-skill-name that consumes Z's output would complete the natural
  workflow and enable [use case].
Trade-off: Adds scope; only worth building if the use case is frequent.
```

---

## Phase 6 — Complete the Agent Inventory Tables

Fill in the four inventory tables for the Observations section:

**Agents used by only one skill** — list each single-use agent and its skill.
These are candidates for inlining into the skill body if they're simple, or
for abstraction if they're likely to be reused.

**Skills with no dedicated agent** — list each. Note whether they're candidates
for absorption into an adjacent skill.

**Potential shared agents** — list agent types used by 2+ skills.

---

## Phase 7 — Dispatch Diagram Generation

Dispatch `/al-dev-diagram-generator` to generate the workflow diagram. This skill
handles all diagram logic and writes `docs/al-dev-workflow-diagrams.md`.

Pass `--caller-name analyze-skill-design` so the generated diagram references the correct command for re-runs.

---

## Phase 8 — Write to `docs/al-dev-plugin-map.md`

Replace the entire `## Observations` section (from the `## Observations` heading
to the end of the file) with:

```markdown
## Observations

> Generated by /analyze-skill-design on [today's date].
> Run /review-skill-map first if the skill list has changed since this was written.

### Agents used by only one skill

[bullet per agent: "- **agent-type** — used only by /skill-name"]

### Skills with no dedicated agent (skill does the work itself)

[bullet per skill: "- **/skill-name** — [one-line description of what it does alone]"]

### Potential shared agents not yet extracted

[bullet per shared agent: "- **agent-type** — used by /skill-a, /skill-b, /skill-c"]

### Architectural suggestions

[one suggestion block per finding in Atomise / Connect / Merge / Promote / Extend format]

### Extension opportunities

[1–2 forward-looking Extend blocks, or "None identified at this time."]
```

Update `**Last updated:**` in the document header to today's date.
```

new_string:
```
## Phase 5 — Draft Suggestions, Inventory Tables, Diagram and Map

Invoke `/draft-map-suggestions --type skill`. Pass as context:
- The candidate lists from Phase 3 (Connect/Promote, Atomise/Absorb, Merge, Extend candidates with raw finding lines)
- The working lists from Phase 1 (agent usage counts, phase counts, file handoff chains,
  no-agent skills, pre-planning tributaries, Layer 1 diagram content)

`/draft-map-suggestions` handles: drafting suggestions, completing inventory tables,
dispatching the diagram generator, and writing to `docs/al-dev-plugin-map.md`.
```

- [ ] **Step 6: Rename Phase 9 to Phase 6 in analyze-skill-design**

In `.claude/skills/analyze-skill-design/SKILL.md`, use Edit:

old_string:
```
## Phase 9 — Present to User
```

new_string:
```
## Phase 6 — Present to User
```

- [ ] **Step 7: Verify phase structure of both slimmed skills**

```bash
grep "^## Phase" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-agent-design/SKILL.md
grep "^## Phase" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-skill-design/SKILL.md
```

Expected for both:
```
## Phase 1 — Read the ... Map and Build Working Lists
## Phase 2 — Parallel Lens Dispatch
## Phase 3 — Aggregate Findings
## Phase 5 — Draft Suggestions, Inventory Tables, Diagram and Map
## Phase 6 — Present to User
```

(The Phase 4 gap is pre-existing in both skills and not introduced by this task.)

- [ ] **Step 8: Verify draft-map-suggestions is referenced in both slimmed skills**

```bash
grep "draft-map-suggestions" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-agent-design/SKILL.md
grep "draft-map-suggestions" /Users/russelllaing/al-dev-shared/.claude/skills/analyze-skill-design/SKILL.md
```

Expected: one line each referencing `/draft-map-suggestions --type agent` and `--type skill`.

- [ ] **Step 9: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  .claude/skills/draft-map-suggestions/SKILL.md \
  .claude/skills/analyze-agent-design/SKILL.md \
  .claude/skills/analyze-skill-design/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(tooling): extract draft-map-suggestions skill; slim analyze-*-design phases 5-8"
```

---

### Task 5: Split plugin-health into discover and report

**Files:**
- Create: `.claude/skills/plugin-health-discover/SKILL.md`
- Create: `.claude/skills/plugin-health-report/SKILL.md`
- Modify: `.claude/skills/plugin-health/SKILL.md` (replaced with thin router)

**Handoff artifact:** `plugin-health-discover` writes
`docs/health/YYYY-MM-DD-<surface>-findings.md` (one per surface). `plugin-health-report`
reads it. This allows re-running report on existing findings without re-dispatching lenses.

#### 5a — Create plugin-health-discover

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-discover
```

- [ ] **Step 2: Write plugin-health-discover/SKILL.md**

Write `.claude/skills/plugin-health-discover/SKILL.md` with this exact content:

```markdown
---
name: plugin-health-discover
description: >-
  Discovery phase of the plugin health sweep. Builds file lists, aggregates
  context from documentation maps, dispatches all design and quality lenses,
  and writes structured findings to docs/health/YYYY-MM-DD-<surface>-findings.md.
  Called by /plugin-health; can also be run standalone to refresh findings
  without re-running the report phase.
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|all]"
---

# Skill: /plugin-health-discover

Discovery phase of the health sweep. Dispatches lenses and writes findings files
that `/plugin-health-report` consumes.

## Phase 0 — Parse arguments

- `--surface` ∈ `plugin` | `tooling` | `both` (default `both`)
- `--dimension` ∈ `design` | `quality` | `all` (default `all`)

Surface → directory mapping:
- `plugin` → `profile-al-dev-shared/`
- `tooling` → `.claude/`

## Phase 1 — Build file lists (per requested surface)

For each requested surface, glob both object types:

```bash
# plugin surface
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" | sort
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills -name "SKILL.md" | sort
# tooling surface
find /Users/russelllaing/al-dev-shared/.claude/agents -name "*.md" | sort
find /Users/russelllaing/al-dev-shared/.claude/skills -name "SKILL.md" | sort
```

Keep the agent list and skill list separate — different lenses target each.

## Phase 2 — Pre-dispatch aggregation

Extract context from documentation maps before dispatching lenses.

**Read and parse `docs/al-dev-agent-map.md`:**
- Extract the Agent Catalog table
- For each agent row: extract agent name, model, tools list, and "Spawned by" field
- Build: `tool_inventory`, `model_assignments`, `caller_map`
- "Spawned by" may contain comma-separated names or "(none found)" — treat the latter as empty list

**Read and parse `docs/al-dev-plugin-map.md`:**
- Extract the Layer 1 diagram block → `layer1_diagram_content`
- For each skill section: extract phase count, agent references, output files
- Build: `phase_counts`, `handoff_chains`, `preplanning_skills` (skills with `-.->` arrows)

**Compute derived mappings:**
- `agent_usage_counts`: agent → count of spawning skills
- `single_use_agents`: agents where `agent_usage_counts == 1`
- `already_inline_candidates`: filter of `single_use_agents`
- `no_agent_skills`: skills with zero spawned agents

## Phase 3 — Dispatch lenses (per surface, per dimension)

Dispatch in a single response (parallel agent calls). Use per-lens minimal context
per `knowledge/lens-invocation-patterns.md`.

**For design-agent-lens-* agents** (when `--dimension design` or `all`):

| Lens | Context field(s) |
|------|-----------------------------|
| `design-agent-lens-tool-hygiene` | `tool_inventory` |
| `design-agent-lens-model-fit` | `model_assignments` |
| `design-agent-lens-scope-isolation` | *(file list only)* |
| `design-agent-lens-caller-alignment` | `caller_map` |
| `design-agent-lens-usage-patterns` | `single_use_agents`, `already_inline_candidates` |

**For design-skill-lens-* agents** (when `--dimension design` or `all`):

| Lens | Context field(s) |
|------|-----------------------------|
| `design-skill-lens-shared-backbone` | `agent_usage_counts` |
| `design-skill-lens-complexity` | `phase_counts`, `no_agent_skills` |
| `design-skill-lens-near-duplicates` | `agent_usage_counts`, `phase_counts` |
| `design-skill-lens-handoff-gaps` | `handoff_chains` |
| `design-skill-lens-preplanning` | `preplanning_skills`, `layer1_diagram_content` |

**For quality-agent-lens-*, quality-skill-lens-*, naming-convention-lens** (when `--dimension quality` or `all`):
Pass file list only. For naming-convention-lens, also pass:
`Convention doc: /Users/russelllaing/al-dev-shared/docs/al-dev-naming-convention.md`

A lens that returns a malformed or empty block is recorded as `lens <name>: no result`
and the sweep continues — a failed lens never aborts discovery.

## Phase 4 — Write findings file (per surface)

For each swept surface, write:
`docs/health/YYYY-MM-DD-<surface>-findings.md` (substitute today's date and `plugin`/`tooling`)

Structure:
```markdown
# <Surface> Findings — YYYY-MM-DD

## Raw lens output

### <Lens Name> Findings
[findings block returned by the lens agent, verbatim]

---

### <Lens Name> Findings
[next block]

---

## Failed lenses
[one line per "lens <name>: no result", or "None" if all returned results]
```

After writing, print the file path and line count, then return to the caller.
```

- [ ] **Step 3: Verify the discover file was written**

```bash
ls -la /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-discover/SKILL.md
wc -l /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-discover/SKILL.md
```

Expected: file exists, ≥ 60 lines.

#### 5b — Create plugin-health-report

- [ ] **Step 4: Create the skill directory**

```bash
mkdir -p /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-report
```

- [ ] **Step 5: Write plugin-health-report/SKILL.md**

Write `.claude/skills/plugin-health-report/SKILL.md` with this exact content:

```markdown
---
name: plugin-health-report
description: >-
  Report phase of the plugin health sweep. Reads a findings file written by
  /plugin-health-discover, ranks findings, writes the dossier, optionally
  refreshes the dependency graph, and presents results to the user.
  Called by /plugin-health; can also be run standalone against an existing
  findings file to re-rank or reformat without re-dispatching lenses.
argument-hint: "[--findings <path>] [--surface plugin|tooling]"
---

# Skill: /plugin-health-report

Report phase of the health sweep. Reads a findings file and writes the dossier.

## Phase 0 — Locate findings file

If `--findings <path>` is passed, read that file.

Otherwise, find the most recent findings file for each surface requested:
```bash
ls -t /Users/russelllaing/al-dev-shared/docs/health/*-findings.md 2>/dev/null | head -2
```

If no findings file exists, report: "No findings file found. Run /plugin-health-discover first." and stop.

## Phase 1 — Parse findings

Read the findings file. Extract each `### <Lens Name> Findings` block.
Parse each finding line: `- **[name]** | [Severity] | [observation] | [fix]`

Note any "Failed lenses" listed at the foot of the file.

## Phase 2 — Rank

Order findings High → Medium → Low, grouped by dimension (design before quality
before naming), then by object (agent before skill). Pick the top 5 ranked actions
for the summary.

## Phase 3 — Write dossier

Write `docs/health/YYYY-MM-DD-<surface>-health.md` (substitute today's date and
`plugin`/`tooling` from the findings filename). The dossier must use generic
vocabulary (no harness-specific tokens). Structure:

```markdown
# <Surface> Health — YYYY-MM-DD

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | <n>    | <n>     | <n>    | <n>   |
| Medium   | <n>    | <n>     | <n>    | <n>   |
| Low      | <n>    | <n>     | <n>    | <n>   |

Top 5 ranked actions:
1. ...

## Design suggestions

[Atomise / Merge / Trim / Split / Align findings — each: finding | rationale | fix]
_No issues found._  ← if empty

## Quality findings

[Bloat / Clarity / Structure / Name-fit / Description — with file:line]
_No issues found._  ← if empty

## Naming violations

[actual name/path vs convention-expected — from naming-convention-lens]
_No issues found._  ← if empty

## Graph deltas

[orphans, dead links, off-path skills, missing refs — plugin surface only;
 omit this section for the tooling surface]
_No issues found._  ← if empty
```

Record any failed lenses at the foot of the Summary section.

## Phase 4 — Refresh dependency graph (plugin surface only)

If the findings file is for the plugin surface, run:

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate-plugin-graph.py
```

The generator writes `docs/al-dev-plugin-graph.md` and exits 0 even on parse errors.

## Phase 5 — Present to user

Print, per surface: dossier path + severity counts + the top action.
List any failed lenses.
Ask: "Review the dossier and run `/plan-map-changes` on the items you accept?"
Do not edit any source file.
```

- [ ] **Step 6: Verify the report file was written**

```bash
ls -la /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-report/SKILL.md
wc -l /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-report/SKILL.md
```

Expected: file exists, ≥ 50 lines.

#### 5c — Replace plugin-health with thin router

- [ ] **Step 7: Read the current plugin-health/SKILL.md line count**

```bash
wc -l /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health/SKILL.md
```

Record this as `ORIGINAL_LINES` for reference.

- [ ] **Step 8: Overwrite plugin-health with the thin router**

Write `.claude/skills/plugin-health/SKILL.md` with this exact content:

```markdown
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
```

- [ ] **Step 9: Verify the router was written**

```bash
wc -l /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health/SKILL.md
ls -la /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health/SKILL.md
```

Expected: file exists, ≤ 45 lines (significantly shorter than `ORIGINAL_LINES`).

- [ ] **Step 10: Verify all three skill files exist**

```bash
ls /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health/SKILL.md \
   /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-discover/SKILL.md \
   /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-report/SKILL.md
```

Expected: all three paths print without error.

- [ ] **Step 11: Check for forbidden patterns in all three files**

```bash
grep -rn "subagent_type\|claude:\|copilot:\|YYYY-MM-DD\b\|\bTODO\b\|\bTBD\b" \
  /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health/SKILL.md \
  /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-discover/SKILL.md \
  /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-report/SKILL.md
```

Expected: only `YYYY-MM-DD` in template placeholder context (e.g., `YYYY-MM-DD-<surface>-findings.md`) — this is intentional. Any harness tokens or bare `TODO`/`TBD` are failures.

- [ ] **Step 12: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  .claude/skills/plugin-health/SKILL.md \
  .claude/skills/plugin-health-discover/SKILL.md \
  .claude/skills/plugin-health-report/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat(tooling): split plugin-health into discover + report sub-skills"
```

---

## Self-Review

**Spec coverage check:**

| Health finding | Task | Covered? |
|---------------|------|----------|
| Remove `subagent_type` from audit-quality | Task 1 | ✓ |
| Define "independent suggestions" in plan-map-changes | Task 2 | ✓ |
| Per-lens minimal-context dispatch (3 skills) | Task 3 | ✓ |
| Atomise analyze-agent-design + analyze-skill-design | Task 4 | ✓ |
| Atomise plugin-health | Task 5 | ✓ |

**Placeholder scan:** No TBD, TODO, or "similar to Task N" patterns. All file content is explicit.

**Scope gaps resolved:**
- Task 4: draft-map-suggestions is parameterized `--type agent|skill` to handle the non-identical templates (confirmed in rubber duck).
- Task 5: Intermediate findings file format defined; thin router preserves all existing references to `/plugin-health` in plan-map-changes and CLAUDE.md.
- Task 1: Used plain English rather than `agent_type` (still a field-name token) per rubber duck finding.
