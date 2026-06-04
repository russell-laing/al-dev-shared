---
name: plugin-health-discover
description: >-
  Discovery phase of the plugin health sweep. Builds file lists, aggregates
  context from documentation maps, dispatches all design, quality, and naming
  lenses,
  and writes structured findings to docs/health/YYYY-MM-DD-<surface>-findings.md.
  Called by /plugin-health-audit; can also be run standalone to refresh findings
  without re-running the report phase.
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|all] [--resume]"
---

# Skill: /plugin-health-discover

Discovery phase of the health sweep. Dispatches lenses and writes findings files
that `/plugin-health-report` consumes.

## Phase 0 — Parse arguments

- `--surface` ∈ `plugin` | `tooling` | `both` (default `both`)
- `--dimension` ∈ `design` | `quality` | `all` (default `all`)
- `--resume` ∈ present | absent (default absent)

Surface → directory mapping:

- `plugin` → `profile-al-dev-shared/`
- `tooling` → `.claude/`

### Cadence guard (per requested surface)

Re-sweeping before the prior dossier is dispositioned mostly re-measures
known findings at full lens cost. Before dispatching:

```bash
# Most recent dossier for the surface
ls -t /Users/russelllaing/al-dev-shared/docs/health/*-<surface>-health.md 2>/dev/null | head -1
```

If a dossier exists, check whether `docs/health/dispositions.md` contains
any rows dated on or after that dossier's date. If it does not (or the
ledger is absent), warn:

```text
The latest <surface> dossier (<date>) has no recorded dispositions.
A new sweep will largely re-discover its open findings. Record
accept/decline/fixed rows in docs/health/dispositions.md first, or
confirm to sweep anyway.
```

Then branch explicitly:

- User confirms → proceed to Phase 1.
- User declines, or gives no clear confirmation → stop. Report "Sweep not
  dispatched — record dispositions in `docs/health/dispositions.md` and
  re-run." Do not dispatch any lens.

Skip the guard when `--resume` is present (resuming an interrupted sweep is
not a new sweep).

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

**Read and parse `docs/al-dev-skills-map.md`:**

- Extract the Layer 1 diagram block → `layer1_diagram_content`
- For each skill section: extract phase count, agent references, output files
- Build: `phase_counts`, `handoff_chains`, `preplanning_skills` (skills with `-.->` arrows)

**Compute derived mappings:**

- `agent_usage_counts`: agent → count of spawning skills
- `single_use_agents`: agents where `agent_usage_counts == 1`
- `already_inline_candidates`: filter of `single_use_agents`
- `no_agent_skills`: skills with zero spawned agents

## Phase 3 — Resume & dispatch

### 3.1 Resume detection (if --resume flag)

If invoked with `--resume` flag:

1. **Scan `.dev/` directory for existing lens output files:**

   ```bash
   ls -1 .dev/*-plugin-health-lens-*.json 2>/dev/null
   ```

2. **Extract completed lens names:**
   - For each `.json` file, parse the `"lens"` field
   - Build `completed_lenses` set

3. **Filter remaining lenses:**
   - `remaining_lenses = [l for l in ALL_LENSES if l not in completed_lenses]`
   - Log: `"Resuming: X lenses already completed, Y remaining"`
   - If `remaining_lenses` is empty, log: `"Resuming: all lenses already complete; skipping dispatch and assembling findings from disk."`

If NOT invoked with `--resume`:

- `remaining_lenses = ALL_LENSES`

### 3.1b Surface-scoped lenses (mandatory filter)

`ALL_LENSES` is surface-dependent. `design-skill-lens-surface-placement`
exists solely to find **distributed** skills that belong in the repo-local
maintainer surface; aimed at files already in the maintainer surface it can
only emit false "Move" findings (9 per sweep on 2026-06-03 and 2026-06-04).

- Surface `plugin` → all lenses.
- Surface `tooling` → exclude `design-skill-lens-surface-placement` from
  `ALL_LENSES` before computing `remaining_lenses`.

### 3.2 Dispatch lenses via Workflow (isolated contexts)

If `remaining_lenses` is empty, skip dispatch entirely and proceed to Phase 4.

Lenses run in parallel in a Workflow to isolate agent conversations. Construct lens prompts per the examples in `.claude/skills/plugin-health-discover/workflow-lens-dispatch-reference.md`, then invoke the Workflow script with the lens prompt list.

For each lens, pass only the context fields it requires (per `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`).

**Invoke Workflow:**

```python
import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, str(Path.cwd() / ".claude" / "skills" / "plugin-health-discover"))
from workflow_utils import invoke_workflow, wait_for_workflow

today = datetime.now().strftime("%Y-%m-%d")  # used for every .dev/ output filename
workflow_path = Path(".claude/skills/plugin-health-discover/workflow-lens-dispatch.js")

task_id = invoke_workflow(
    script=str(workflow_path),
    args=json.dumps(lens_prompt_list),
    label="plugin-health-lens-sweep"
)
```

**Wait for completion and process results:**

```python
findings = wait_for_workflow(task_id, timeout_seconds=600)

if findings is None:
    findings = []

for lens in findings:
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

### 3.3 Confirm returns (check for missing lenses)

The current Workflow script returns only truthy lens result objects and does not emit a `failed_lenses` list. Compare the returned lens identifiers against `remaining_lenses` to detect any that did not come back:

```python
returned = {lens['lens'] for lens in findings}
missing_lenses = [l for l in remaining_lenses if l not in returned]
# missing_lenses now holds every expected lens that did NOT return a result
```

Record missing lenses in a `## Failed lenses` section at the top of the findings
file, one per line:
`- <lens-name>: not returned (missing from Workflow results)`

See `.claude/skills/plugin-health-discover/workflow-lens-dispatch-reference.md` for implementation details and code examples. Verify that `agentType` is used consistently in the built prompt list, the reference document, and `.claude/skills/plugin-health-discover/workflow-lens-dispatch.js`.

## Phase 4 — Assemble findings file from disk

For each surface that had lenses run:

1. **Collect all lens output files from `.dev/`:**

   ```bash
   ls -1 .dev/*-plugin-health-lens-*.json | sort
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
   rm -f .dev/*-plugin-health-lens-*.json
   ```

5. **Return to caller:**
   Print the findings file path, line count, and resume status.
