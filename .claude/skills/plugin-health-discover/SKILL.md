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
