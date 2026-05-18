# Agent Map Skills Design

**Date:** 2026-05-18  
**Status:** Approved  
**Scope:** Two new project-local skills (`/review-agent-map`, `/analyze-agent-design`) plus a targeted extension to `/plan-plugin-map-changes`, producing a new `docs/al-dev-agent-map.md` document.

---

## Motivation

The existing plugin analyzer skills (`/review-plugin-map`, `/analyze-plugin-design`, `/plan-plugin-map-changes`) give thorough coverage of skill design and workflow but treat agents as catalog items — objects consumed by skills — rather than subjects of analysis in their own right. No existing skill reads an agent's `model`, `tools`, system prompt body, or caller contract and asks "is this agent well-designed?" This gap grows as the agent roster expands.

---

## Architecture

Three deliverables:

| Deliverable | Type | Location |
|---|---|---|
| `/review-agent-map` | New skill | `.claude/skills/review-agent-map/SKILL.md` |
| `/analyze-agent-design` | New skill | `.claude/skills/analyze-agent-design/SKILL.md` |
| `/plan-plugin-map-changes` | Extend existing | Add `--agents` argument |
| `docs/al-dev-agent-map.md` | New document | Written/maintained by the two new skills |

Both new skills live in `.claude/skills/` (project-local), consistent with the existing analyzer skills — they are maintenance tools for this repo, not distributed plugin skills.

---

## Skill 1: `/review-agent-map`

**Purpose:** Keep `docs/al-dev-agent-map.md` accurate as agents are added, removed, or restructured.

**Phases:**

1. **Scan** — list `profile-al-dev-shared/agents/*.md` (active) and `archived/agents/` (excluded). Build the agent inventory.

2. **Extract agent profiles** — for each active agent file, read frontmatter and body to capture:
   - `model` (sonnet/opus/haiku)
   - `tools` list
   - `description` (first sentence — what it does and who spawns it)
   - Inputs/outputs tables (if present in the body)

3. **Cross-reference callers** — grep each skill's `SKILL.md` for the agent's type name to determine which skills spawn it. Record spawn count (single-use vs. shared).

4. **Compare against `docs/al-dev-agent-map.md`** — check Layer 1 catalog table and Layer 2 per-agent sections for accuracy. Flag: stale entries, missing agents, changed model or tools.

5. **Report discrepancies** — summarise findings before editing. If everything is accurate, say so and stop.

6. **Update the map** — targeted edits only. Update the `Last updated` header.

7. **Detect inline candidates** — score each agent against three signals:
   - Spawned by only one skill
   - Fewer than 10 lines of system prompt body
   - No dedicated inputs/outputs tables

   An agent scoring 2+ signals is an inline candidate. Append findings to the `## Observations` section of `docs/al-dev-agent-map.md`. Commit if any candidates found.

**Triggers:** "review agent map", "update agent map", "sync agent map", "is the agent map accurate"

---

## Skill 2: `/analyze-agent-design`

**Purpose:** Apply analytical lenses to agent files and write quality improvement suggestions to `docs/al-dev-agent-map.md`'s `## Observations` section.

**Prerequisite:** Run `/review-agent-map` first if the map may be out of date.

**Analytical lenses:**

| Lens | What it checks |
|---|---|
| **Tool hygiene** | Does the `tools` list match what the system prompt actually needs? Read-only agents should not have Write/Edit. |
| **Model fit** | Is sonnet/opus/haiku appropriate? Multi-file synthesis agents warrant opus; simple single-task agents may be over-allocated. |
| **Scope isolation** | Is the agent doing one well-bounded thing? Flag system prompts with two clearly separable concerns. |
| **Caller alignment** | Do the agent's documented inputs/outputs match how spawning skills actually call it? |
| **Description quality** | Is the description accurate and specific enough to be useful in the agent list without being over-broad? |
| **Usage patterns** | Is a dedicated agent file justified by complexity and reuse, or could it be inlined into the calling skill? |

**Suggestion vocabulary** (parallel to the skill map's Atomise/Connect/Merge/Promote/Extend):

- **Trim** — remove unused tools from the tools list
- **Remodel** — upgrade or downgrade the model assignment
- **Split** — agent doing two separable jobs; extract one
- **Inline** — single-use, trivial agent; absorb into the calling skill
- **Align** — caller/agent contract mismatch; fix inputs/outputs documentation

**Steps:**

1. Read `docs/al-dev-agent-map.md` in full. Build working lists: tool usage per agent, model assignments, single vs. shared use, caller references.
2. Apply each lens to every agent. Note findings.
3. Draft 3–6 high-quality suggestions. Skip patterns that don't yield a real improvement. Check existing Observations — skip anything already marked `← implemented`.
4. Complete inventory tables: agents used by only one skill, agents with no inputs/outputs docs, potential shared agents used by 2+ skills.
5. Write to `## Observations` in `docs/al-dev-agent-map.md` (replace entire section).
6. Present a one-line summary per suggestion. Mark the highest-leverage suggestion. Ask: "Would you like to act on any of these now?"

**Triggers:** "analyze agent design", "agent quality review", "review agent quality", "agent improvement suggestions"

---

## Extension: `/plan-plugin-map-changes` — `--agents` argument

**Change:** Add `--agents` as a recognised argument value. When present:

- Source document switches from `docs/al-dev-plugin-map.md` → `docs/al-dev-agent-map.md`
- Rubber-ducking reads agent `.md` files (`profile-al-dev-shared/agents/<name>.md`) instead of skill `SKILL.md` files
- Plan tasks reference agent file paths
- Suggestion vocabulary expands to include Trim/Remodel/Split/Inline/Align in addition to the existing types

Everything else — the rubber-duck protocol, plan output format, verification checklist — stays identical.

**Argument-hint update:** `[optional: connect | merge | trim | remodel | inline | align | all | --agents]`

---

## Output Document: `docs/al-dev-agent-map.md`

Agents don't form a workflow graph (unlike skills), so the document uses a table for Layer 1 rather than a Mermaid flowchart.

**Structure:**

```
# AL Dev Agent Map

Last updated: YYYY-MM-DD

## Layer 1: Agent Catalog

| Agent | Model | Tools | Spawned by |
|-------|-------|-------|------------|
| al-dev-developer | sonnet | Read, Write, Edit, Glob, Grep, Bash | /al-dev-develop, /al-dev-fix |
...

## Layer 2: Per-Agent Profiles

### al-dev-<name>

**Description:** ...
**Model:** sonnet/opus/haiku
**Tools:** [list]
**Spawned by:** /skill-a, /skill-b
**Inputs:** [table or "Not documented"]
**Outputs:** [table or "Not documented"]

...

## Observations

> Generated by /analyze-agent-design on YYYY-MM-DD.
> Run /review-agent-map first if the agent list has changed since this was written.

### Agents used by only one skill
...

### Agents with no inputs/outputs documentation
...

### Potential shared agents
...

### Quality suggestions
[one block per finding in Trim/Remodel/Split/Inline/Align format]
```

The initial document is created by the first run of `/review-agent-map`. Subsequent runs keep it accurate; `/analyze-agent-design` populates `## Observations`.

---

## What Is Not in Scope

- Analysing archived agents
- Analysing agent `.md` files in other plugins or repos
- Automated fixing of agent files (the plan skill handles that)
- Changes to how the distributed plugin skills invoke agents
