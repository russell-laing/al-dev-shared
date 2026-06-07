---
name: sync-documentation-maps-agent-audit
description: >-
  Audits active agents in profile-al-dev-shared/agents/ against
  docs/al-dev-agent-map.md and writes a structured JSON discrepancy report
  to the run artifact directory. Called by /sync-documentation-maps dispatch phase.
model: sonnet
tools: ["Read", "Bash", "Write"]
---

# sync-documentation-maps-agent-audit

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-documentation-maps-runs/<run_id>/` |

## Outputs

Writes `<result_dir>/audit/agent-audit.json` and returns its absolute path as
the sole output. Do not summarise findings to the user — return only the path.

**JSON schema:**

```json
{
  "surface": "agents",
  "run_id": "<run_id>",
  "total_files": 12,
  "map_entries": 11,
  "discrepancies": [
    {
      "type": "missing_from_map",
      "agent": "al-dev-example",
      "detail": "Active agent has no Layer 2 section in docs/al-dev-agent-map.md"
    }
  ],
  "summary": "1 discrepancy found: 1 missing_from_map."
}
```

Valid `type` values: `missing_from_map`, `stale_in_map`, `model_mismatch`,
`tools_mismatch`, `caller_mismatch`.

---

## Instructions

All relative paths in these instructions are from the repository root:
`/Users/russelllaing/al-dev-shared`. Adjust paths if the working directory differs.

### Step 1 — Build active agent list

Run `ls profile-al-dev-shared/agents/` to get all agent file names.
Run `ls profile-al-dev-shared/archived/agents/ 2>/dev/null` to get archived agent
names.
Active agents = `.md` files in `agents/` minus any names also present in
`archived/agents/`.

### Step 2 — Extract metadata from each active agent

For each active agent, Read `profile-al-dev-shared/agents/<name>.md`.
Extract from frontmatter:

- **model:** the `model:` field value.
- **tools:** the `tools:` list (all entries). If `tools` is an empty list `[]`,
  normalize it to the string `(none)` for comparison against the map.
- **description:** the first sentence of the `description:` field.

### Step 3 — Cross-reference callers (canonical derivation)

Derive the caller list for every active agent in a single step:

```bash
python3 scripts/derive-agent-callers.py
```

The script prints one JSON object mapping each agent name to its sorted
list of caller skills, using the exact edge parser that generates the
Layer 1 agent-catalog table. An empty list corresponds to `(none found)`
in the map.

**Failure path:** if the script exits non-zero, or its output is not a
JSON object with one key per active agent, stop caller cross-referencing.
Skip `caller_mismatch` detection entirely for this run and state in the
report's `summary` field that caller checks were skipped and why (e.g.
"caller checks skipped: derive-agent-callers.py exited 1"). A per-agent
empty list (`[]`) is a valid result meaning
`(none found)`.

Do **not** grep skill files for agent names as a fallback or supplement —
grep-based caller lists use looser matching semantics (bare-name hits in
frontmatter, reference tables, and the maintainer surface) than the
generator, and any mismatch they "find" is reverted when the write phase
regenerates the catalog from this same parser.

### Step 4 — Parse docs/al-dev-agent-map.md

Read `docs/al-dev-agent-map.md`. Extract:

- **Layer 1 Catalog table rows:** agent names listed in the Layer 1 table.
- **Layer 2 sections:** collect only `###` headings whose text starts with the
  distributed agent prefix `al-dev-`. (The agent map documents distributed agents
  only; maintainer-tooling agents are not mapped here.) Use:

  ```bash
  grep "^### al-dev-" docs/al-dev-agent-map.md
  ```

  Skip generic headings like "Quality suggestions", "Agents used by only one
  skill", or any other non-agent headings that appear in the Observations section.
  For each matched heading, also note the `model:` and `tools:` values recorded
  in that Layer 2 section, and the `Spawned by:` field.

### Step 5 — Identify discrepancies

Compare the active agent list and extracted metadata against the map data.
Discrepancy type definitions are in `.claude/knowledge/sync-maps-edit-cases.md`,
**"Agent surface — discrepancy types (audit)"** section.

For each type found, construct a discrepancy entry with `type`, `agent`, and
`detail` fields. Populate `detail` with context (e.g., map value vs
script-derived value for `caller_mismatch`; which map layer is absent for
`missing_from_map`).

### Step 6 — Write JSON report and return path

For path setup, JSON result construction, and artifact verification, follow
`.claude/skills/sync-documentation-maps/sync-agent-patterns.md`.

Write the report to `<result_dir>/audit/agent-audit.json`.

Return only the absolute file path — no other prose.
