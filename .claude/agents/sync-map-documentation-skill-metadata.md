---
name: sync-map-documentation-skill-metadata
description: >-
  Builds the active skill list from profile-al-dev-shared/skills/ and extracts
  frontmatter metadata (name, description, argument-hint, workflow stage, phase count,
  spawned agents). Writes a structured JSON snapshot to the run artifact directory.
  Called by /sync-map-documentation dispatch phase; its output is consumed by
  sync-map-documentation-skill-compare. spawned_agents is derived by
  scripts/derive_skill_spawned_agents.py — the same edge parser the map
  generator uses — so it can never disagree with the generated drilldowns.
model: sonnet
tools: ["Read", "Bash", "Write"]
---

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-map-documentation-runs/<run_id>/` |

## Outputs

Writes `<result_dir>/audit/skill-metadata.json` and returns its absolute path.
Do not summarise findings — return only the path.

**JSON schema:**

```json
{
  "surface": "skills",
  "run_id": "<run_id>",
  "total_files": 19,
  "skills": [
    {
      "name": "al-dev-example",
      "description": "First sentence of description field",
      "argument_hint": "[optional args]",
      "workflow_stage": "develop",
      "phase_count": 3,
      "spawned_agents": ["al-dev-shared:al-dev-developer"]
    }
  ]
}
```

`phase_count` is the count of `## Phase N` headings in `SKILL.md` (where N is a
digit). `spawned_agents` is the per-skill list emitted by
`scripts/derive_skill_spawned_agents.py` (canonical `al-dev-shared:<agent-name>`
form). These two fields are required by `sync-map-documentation-skill-compare`
to detect `phase_count_mismatch` and `agent_name_mismatch` discrepancy types.

---

## Instructions

All relative paths are from the repository root: `/Users/russelllaing/al-dev-shared`.

### Step 1 — Build active skill list

Run `ls profile-al-dev-shared/skills/` to get all skill directory names.
Run `ls profile-al-dev-shared/archived/skills/ 2>/dev/null` to get archived skill
names.
Active skills = skills in `skills/` minus any names also present in `archived/skills/`.

### Step 2 — Extract metadata from each active skill

For each active skill, Read `profile-al-dev-shared/skills/<name>/SKILL.md`. Extract:

- **name:** the `name:` frontmatter field value.
- **description:** the first sentence of the `description:` field.
- **argument_hint:** the `argument-hint:` frontmatter field value (empty string if absent).
- **workflow_stage:** the `workflow.stage:` frontmatter field value (empty string if absent).
- **phase_count:** count headings matching `## Phase N` (where N is a digit).
- **spawned_agents:** do **not** hand-extract these from the body. Run
  `python3 scripts/derive_skill_spawned_agents.py` once (it prints a JSON object
  mapping every skill name to its sorted `al-dev-shared:<agent-name>` list) and
  use this skill's entry verbatim. This script reuses the map generator's edge
  parser, so it catches both canonical `al-dev-shared:` references and bare
  references on spawn-hint lines (e.g. `Spawn **al-dev-solution-architect**`) —
  matching the generated drilldowns exactly and avoiding the
  `agent_name_mismatch` false positives that canonical-only matching produced.
  If the script exits non-zero, fall back to extracting well-formed
  `al-dev-shared:[a-z-]+` references from the body and note the fallback.

### Step 3 — Write JSON and return path

`derive_skill_spawned_agents.py` covers skill→agent edges (see Step 2), but there
is no equivalent deriver for skill-to-skill *caller* references.
Set `callers: {}` always — omit the callers derivation step.

Ensure `<result_dir>/audit/` exists (`mkdir -p`). Write `skill-metadata.json`.
Return only the absolute path.
