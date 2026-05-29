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

## Phase 0 — Parse arguments

- `--surface` ∈ `plugin` | `tooling` | `both` (default `both`)
- `--dimension` ∈ `design` | `quality` | `all` (default `all`)

Surface → directory mapping:
- `plugin` → `profile-al-dev-shared/` → dossier `docs/health/YYYY-MM-DD-plugin-health.md`
- `tooling` → `.claude/` → dossier `docs/health/YYYY-MM-DD-tooling-health.md`

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

Keep the agent list and the skill list separate — different lenses target each.

## Phase 2 — Parallel lens dispatch (per surface)

### Sub-phase 2.0: Pre-dispatch aggregation

Extract context from documentation maps before dispatching lenses. This provides
the structured data lenses need to perform alignment, hygiene, and architecture
analysis.

**Read and parse `docs/al-dev-agent-map.md`:**
- Extract the Agent Catalog table (first table after "Layer 1: Agent Catalog")
- For each agent row: extract agent name, model, tools list, and "Spawned by" field
- Build these mappings:
  - `tool_inventory`: `{agent-name: [tool1, tool2, ...], ...}`
  - `model_assignments`: `{agent-name: model, ...}` (haiku/sonnet/opus)
  - `caller_map`: `{agent-name: [skill1, skill2, ...], ...}` (parse "Spawned by" field;
    extract skill names like `/al-dev-commit`; handle "(none found)" as empty list)

**Read and parse `docs/al-dev-plugin-map.md`:**
- Extract the Layer 1 diagram (the `mermaid` block after "Layer 1: Lifecycle Overview")
- Extract all skill names from the diagram as `layer1_diagram_content` (raw diagram text)
- Scan the entire document for skill sections (e.g., "### /al-dev-ticket", "### /al-dev-fix")
- For each skill section, extract:
  - Phase count: count `## Phase` headings (or Mermaid `["Phase N<br/>`-style entries)
  - Agent references: extract all agent names mentioned in the section
  - Output files: extract `.dev/*` file patterns mentioned in the section
- Build these mappings:
  - `phase_counts`: `{skill-name: phase-count, ...}`
  - `handoff_chains`: `{skill-name: [output-files], ...}`
  - `preplanning_skills`: `[al-dev-explore, al-dev-interview, al-dev-perf, ...]` 
    (skills with dashed lines in the diagram; scan "tributaries" section)

**Compute derived mappings:**
- `agent_usage_counts`: For each agent, count how many skills spawn it
  (from `caller_map`)
- `single_use_agents`: Agents with `agent_usage_counts[agent] == 1`
- `already_inline_candidates`: Filter of `single_use_agents` (agents that could
  be inlined into their sole spawner)
- `no_agent_skills`: Skills with zero agents spawned (skills that do all work internally)

**Store all 11 context structures as named variables for reuse in dispatch prompts:**
1. `tool_inventory`
2. `model_assignments`
3. `caller_map`
4. `phase_counts`
5. `handoff_chains`
6. `preplanning_skills`
7. `agent_usage_counts`
8. `single_use_agents`
9. `already_inline_candidates`
10. `no_agent_skills`
11. `layer1_diagram_content` — raw text of the Layer 1 Mermaid diagram from
    `docs/al-dev-plugin-map.md` (required by `design-skill-lens-preplanning`)

**Extraction implementation notes:**
- Use Read tool on both map files to extract tables and text
- For Mermaid diagram sections, capture the raw text (linters refer to it)
- "Spawned by" field may contain multiple skills separated by commas or multiple rows
  (e.g., "/al-dev-develop, /al-dev-fix" or "/al-dev-ticket (support mode: X)");
  extract all skill names (those starting with `/`)
- "Spawned by" field may contain "(none found)" or "(not spawned...)" — treat as
  empty caller list for that agent
- Phase count may be derived from either explicit "## Phase N" headers or from
  Mermaid diagram content (count Phase N entries)
- Preplanning skills: grep for dashed arrows (`-.->`) in the Layer 1 diagram

### Phase 2.1 — Dispatch all design/quality lenses (with context)

**Dispatch in a single response (parallel Agent tool calls). Choose lenses by the
object type and the `--dimension` argument:**

**Agent file list** receives:
- `design`/`all`: `design-agent-lens-tool-hygiene`, `design-agent-lens-model-fit`,
  `design-agent-lens-scope-isolation`, `design-agent-lens-caller-alignment`,
  `design-agent-lens-usage-patterns`
- `quality`/`all`: `quality-agent-lens-clarity`, `quality-agent-lens-structure`,
  `quality-agent-lens-description`, `quality-agent-lens-bloat`,
  `quality-agent-lens-name-fit`

**Skill file list** receives:
- `design`/`all`: `design-skill-lens-shared-backbone`, `design-skill-lens-complexity`,
  `design-skill-lens-near-duplicates`, `design-skill-lens-handoff-gaps`,
  `design-skill-lens-preplanning`
- `quality`/`all`: `quality-skill-lens-clarity`, `quality-skill-lens-structure`,
  `quality-skill-lens-description`, `quality-skill-lens-bloat`,
  `quality-skill-lens-name-fit`

**Both object lists** additionally receive `naming-convention-lens`, with
`docs/al-dev-naming-convention.md` passed as the convention doc.

Dispatch prompt templates — use the variant matching each lens class.
See `knowledge/lens-invocation-patterns.md` for the full context-field reference.

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

**For quality-agent-lens-*, quality-skill-lens-*, and naming-convention-lens:**
```
Analyze the following files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]
```

Convention doc (naming-convention-lens only):
/Users/russelllaing/al-dev-shared/docs/al-dev-naming-convention.md

## Phase 3 — Collect findings (fault-tolerant)

Collect each lens's findings block. A lens that returns a malformed or empty
block is recorded as `lens <name>: no result` and the run continues — a failed
lens NEVER aborts the sweep.

Parse each finding line: `- **[name]** | [Severity] | [observation] | [fix]`.

## Phase 4 — Rank

Order findings High → Medium → Low, grouped by dimension (design before quality
before naming), then by object (agent before skill). Pick the top 5 ranked
actions for the summary.

## Phase 5 — Write ONE dossier per surface

Write `docs/health/YYYY-MM-DD-<surface>-health.md` (substitute today's date and
`plugin`/`tooling`). The dossier MUST use generic vocabulary (no harness-specific
tokens). Structure:

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

Record any `lens <name>: no result` notes at the foot of the Summary section.

## Phase 6 — Refresh the dependency graph (plugin surface only)

If the plugin surface was swept, run the generator and source the "Graph deltas"
section from its health callouts (single source of truth for both the picture and
those findings):

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate-plugin-graph.py
```

The generator writes `docs/al-dev-plugin-graph.md` and exits 0 even on a parse
error (partial graph + "incomplete" banner).

## Phase 7 — Present to user

Print, per surface: dossier path + severity counts + the top action. List any
`no result` lenses. Ask: "Review the dossier and run `/plan-map-changes` on the
items you accept?" Do not edit any source file.
