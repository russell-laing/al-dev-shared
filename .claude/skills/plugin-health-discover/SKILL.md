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

## Phase 3a — Dispatch lenses via Workflow (isolated contexts)

Lenses run in a Workflow to isolate agent conversations. The Workflow receives
a list of lens prompts (built in this phase) and fans them out via `pipeline()`,
running all lenses concurrently. Each lens result is returned as a structured
JSON object (~1KB), keeping the main session context lean.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / ".claude" / "skills" / "plugin-health-discover"))
from workflow_utils import invoke_workflow, wait_for_workflow
```

### Step 1: Build lens prompt list from assembled lens definitions

For each lens in scope (`remaining_lenses`), construct a prompt object:

```
lens_prompt_list = []

for lens_name in remaining_lenses:
    lens_prompt = {
        "name": lens_name,
        "agent_type": lens_name,  # e.g. "design-agent-lens-tool-hygiene"
        "prompt": f"""
Run the {lens_name} analysis.

Files to analyze:
{formatted_file_list}

Context fields:
{context_field_content}
"""
    }
    lens_prompt_list.append(lens_prompt)
```

**Context field tables (per lens):**

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

### Step 2: Invoke Workflow with lens prompt list

```python
workflow_path = Path(".claude/skills/plugin-health-discover/workflow-lens-dispatch.js")

task_id = invoke_workflow(
    script=str(workflow_path),
    args=json.dumps(lens_prompt_list),
    label="plugin-health-lens-sweep"
)
```

The Workflow script (below) runs all lenses in parallel via `pipeline()`:

```javascript
export const meta = {
  name: 'plugin-health-lens-sweep',
  description: 'Fan out plugin health lens agents in parallel, return structured findings',
  phases: [{ title: 'Lens sweep' }]
}

const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['lens', 'findings', 'suggestion_count'],
  properties: {
    lens:             { type: 'string' },
    findings:         { type: 'string' },
    suggestion_count: { type: 'number' }
  }
}

// args = [{ name, agent_type, prompt }]
const results = await pipeline(
  args,
  lens => agent(
    lens.prompt,
    {
      label:      lens.name,
      phase:      'Lens sweep',
      schema:     FINDINGS_SCHEMA,
      agentType:  lens.agent_type
    }
  )
)

return results.filter(Boolean)
```

### Step 3: Wait for Workflow completion and process results

```python
findings = wait_for_workflow(task_id, timeout=600)
```

For each completed lens in `findings`:

```python
timestamp = datetime.now().isoformat()
output_file = f".dev/{today}-plugin-health-lens-{lens['lens']}.json"
with open(output_file, 'w') as f:
    json.dump({
        "lens": lens['lens'],
        "findings": lens['findings'],
        "suggestion_count": lens.get('suggestion_count', 0),
        "completed_at": timestamp
    }, f, indent=2)
```

### Step 4: Write findings to disk

All lens results are now in `.dev/` as individual `.json` files. Phase 4 will
read and assemble them.

### Step 5: Check for failed lenses

If the Workflow result includes a `failed_lenses` list:

```
Log: "Failed lenses: {', '.join(failed_lenses)}"
```

A failed lens never aborts discovery; the sweep continues.

Use per-lens minimal context per `knowledge/lens-invocation-patterns.md`.

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
