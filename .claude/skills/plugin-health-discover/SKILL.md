---
name: plugin-health-discover
description: >-
  Discovery phase of the plugin health sweep. Builds file lists, aggregates
  context from documentation maps, dispatches all design and quality lenses,
  and writes structured findings to docs/health/YYYY-MM-DD-<surface>-findings.md.
  Called by /plugin-health-audit; can also be run standalone to refresh findings
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

## Phase 3 — Resume detection (if --resume flag)

If invoked with `--resume` flag:

1. **Scan `.dev/` directory for existing lens output files:**
   ```bash
   ls -1 .dev/plugin-health-lens-*.json 2>/dev/null
   ```

2. **Extract completed lens names:**
   - For each `.json` file, parse the `"lens"` field
   - Build `completed_lenses` set

3. **Filter remaining lenses:**
   - `remaining_lenses = [l for l in ALL_LENSES if l not in completed_lenses]`
   - Log: `"Resuming: X lenses already completed, Y remaining"`

If NOT invoked with `--resume`:
- `remaining_lenses = ALL_LENSES`

## Phase 3a — Dispatch lenses with per-lens disk streaming (batched by token budget)

Dispatch lenses in waves to stay within session token limits. After each lens
completes, write its result immediately to disk.

**Token budget calculation:**
```python
per_lens_token_budget = 5000  # Typical lens cost (varies by scope)
remaining_budget = budget.remaining()
lenses_per_wave = max(1, remaining_budget // (per_lens_token_budget * 1.2))
```

**For each wave:**

1. **Log wave progress:**
   ```
   Wave 1: Running 3 lenses (1-3 of 21 total)
   ```

2. **Dispatch this wave's lenses in parallel.**

3. **For each completed lens, immediately write result to disk:**
   ```python
   timestamp = datetime.now().isoformat()
   output_file = f".dev/2026-05-31-plugin-health-lens-{lens_name}.json"
   with open(output_file, 'w') as f:
       json.dump({
           "lens": lens_name,
           "findings": lens_result,
           "completed_at": timestamp
       }, f, indent=2)
   ```

4. **Check remaining budget:**
   - If `budget.remaining() < 10000`: Log "Approaching budget limit; call with
     `--resume` in a fresh session to complete"
   - Halt if approaching limit; remaining lenses will be picked up by --resume

Use per-lens minimal context per `knowledge/lens-invocation-patterns.md`.

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

## Phase 4 — Assemble findings file from disk

For each surface that had lenses run:

1. **Collect all lens output files from `.dev/`:**
   ```bash
   ls -1 .dev/plugin-health-lens-*.json | sort
   ```

2. **Read and assemble findings:**
   - For each `.json` file, load and extract `"findings"` field
   - Parse any "Failed lenses" entries (returned by failed lens agents)
   - Build findings markdown blocks in order

3. **Write findings file:**
   `docs/health/YYYY-MM-DD-<surface>-findings.md` (substitute today's date and
   `plugin`/`tooling`)

   Structure:
   ```markdown
   # <Surface> Findings — YYYY-MM-DD

   ## Raw lens output

   ### <Lens Name> Findings
   [findings block from .dev/ file]

   ---

   ### <Lens Name> Findings
   [next block]

   ---

   ## Failed lenses
   [one line per failed lens, or "None" if all returned results]
   
   ## Resume information
   - Total lenses in scope: N
   - Completed this session: M
   - Completed in prior sessions: P (from --resume)
   - Status: [COMPLETE / INCOMPLETE — call with --resume to finish]
   ```

4. **Clean up disk files after assembly:**
   ```bash
   rm .dev/plugin-health-lens-*.json
   ```

5. **Return to caller:**
   Print the findings file path, line count, and resume status.
