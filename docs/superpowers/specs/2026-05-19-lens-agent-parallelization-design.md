# Design: Lens-Agent Parallelization for Project Analysis Skills

**Date:** 2026-05-19
**Status:** Draft
**Scope:** `.claude/skills/` project-level analysis skills

---

## Problem

The project analysis skills (`/audit-agent-quality`, `/analyze-agent-design`, `/audit-skill-quality`, `/analyze-skill-design`) currently run all analytical lenses sequentially in one prompt. At 15+ units (agent/skill files), this means:

- Long wall-clock time (each file analyzed one after another)
- The main conversation context accumulates all intermediate analysis, making subsequent turns more expensive

---

## Solution

Restructure each analysis skill into three phases, with one lightweight agent spawned per analytical lens in parallel.

---

## Architecture

### Skill Structure (all four skills)

```
Phase 1 — Discovery (inline)
  └── scan filesystem, build file list

Phase 2 — Parallel Dispatch
  └── spawn one agent per lens simultaneously (single Agent tool call)
       ├── lens-agent-A  reads all files, applies Lens A
       ├── lens-agent-B  reads all files, applies Lens B
       ├── lens-agent-C  reads all files, applies Lens C
       ├── lens-agent-D  reads all files, applies Lens D
       └── lens-agent-E  reads all files, applies Lens E

Phase 3 — Aggregation (inline)
  └── collect 5 findings blocks → merge by file → write output
```

### Agent Files

Project-level agents in `.claude/agents/` (scoped to `al-dev-shared`, not the shared plugin):

**For `/audit-agent-quality`:**
| File | Lens |
|---|---|
| `quality-lens-clarity.md` | Prompt clarity issues |
| `quality-lens-structure.md` | Structural conventions |
| `quality-lens-description.md` | Description drift |
| `quality-lens-bloat.md` | Scope/bloat detection |
| `quality-lens-name-fit.md` | Name fit |

**For `/analyze-agent-design`:**
| File | Lens |
|---|---|
| `design-lens-tool-hygiene.md` | Unused tools in frontmatter |
| `design-lens-model-fit.md` | Over/under-allocated model |
| `design-lens-scope-isolation.md` | Separable concerns (Split candidates) |
| `design-lens-caller-alignment.md` | Inputs/Outputs vs. actual caller contract |
| `design-lens-usage-patterns.md` | Single-use agents (Inline candidates) |

`/audit-skill-quality` and `/analyze-skill-design` follow the same pattern with their own lens sets (separate agent files, same structural template).

---

## Data Flow

### Skill → Agent (dispatch prompt)

Each lens agent receives three things in its dispatch prompt:
1. **File list** — absolute paths to all target files
2. **Lens spec** — the rules, red flags, and severity definitions for that lens
3. **Output format** — a fixed findings block template

### Agent → Skill (return block)

Each agent returns a findings block in this format:

```
### [Lens Name] Findings
- **unit-name** | High | [observation] | [fix]
- **unit-name** | Medium | [observation] | [fix]
- **unit-name** | Low | [observation] | [fix]
```

No findings → agent returns `### [Lens Name] Findings\n_No issues found._`

### Aggregation

The skill merges all 5 blocks:
1. Collect return blocks from all agents
2. Concatenate blocks in lens order (each block is already internally sorted by severity)
3. Write to the output file

---

## Token Reality

Total raw tokens may not drop — each lens agent independently reads all target files. The efficiency gains are:

- **Speed:** 5 agents run in parallel vs. sequential lens passes — significant at 15+ units
- **Main context:** stays small (only orchestration + aggregated results, not 17 files of accumulated analysis)
- **Subsequent turns cheaper:** smaller main context means every follow-up message in the session costs less

---

## Implementation Scope and Order

1. `/audit-agent-quality` — first (cleanest lens separation, most mechanical per-file work)
2. `/analyze-agent-design` — second (same pattern, richer lens logic)
3. `/audit-skill-quality` — third
4. `/analyze-skill-design` — fourth

Each skill implementation follows the same pattern:
- Extract lens specs from the current skill body into agent files
- Replace the skill's per-file analysis loop with a parallel dispatch block
- Add an aggregation step

---

## Agent File Template

```markdown
---
name: [quality|design]-lens-[name]
description: [One-line lens description — what it checks and what it returns]
model: haiku
tools: [Read, Glob]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to target files |
| lens_spec | (embedded in this system prompt) |

## Outputs

Returns a findings block in the standard format (see system prompt).

---

## Lens: [Lens Name]

[Lens rules and red flags extracted from the current skill body]

---

## Output Format

Return exactly this structure:

### [Lens Name] Findings
- **[unit-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### [Lens Name] Findings
_No issues found._
```

**Model note:** Lens agents use `haiku` — each applies mechanical rules to one file at a time; no multi-file synthesis or complex reasoning required.

---

## Acceptance Criteria

- [ ] `/audit-agent-quality` spawns 5 parallel lens agents and produces equivalent output to the current sequential version
- [ ] Each lens agent file follows the template above with `haiku` model
- [ ] Aggregation correctly merges and deduplicates findings across lenses
- [ ] Remaining 3 skills updated with the same pattern
- [ ] No lens agent file has `Bash`, `Write`, or `Edit` in its tools list (read-only)
