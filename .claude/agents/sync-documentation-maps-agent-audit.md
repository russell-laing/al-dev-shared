---
name: sync-documentation-maps-agent-audit
description: >-
  Audits active agents in profile-al-dev-shared/agents/ against
  docs/al-dev-agent-map.md and writes a structured JSON discrepancy report
  to the run artifact directory. Called by /sync-documentation-maps dispatch phase.
model: claude-sonnet-4-6
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
- **tools:** the `tools:` list (all entries).
- **description:** the first sentence of the `description:` field.

### Step 3 — Cross-reference callers

For each active agent, derive `<agent-name>` by stripping the `.md` extension.
Run both grep commands and union the results to build the caller list:

```bash
grep -rl "al-dev-shared:<agent-name>" \
  profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null
grep -rl "<agent-name>" \
  profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null
```

The caller list is the union of files returned by both commands.

### Step 4 — Parse docs/al-dev-agent-map.md

Read `docs/al-dev-agent-map.md`. Extract:

- **Layer 1 Catalog table rows:** agent names listed in the Layer 1 table.
- **Layer 2 sections:** collect all `### <agent-name>` headings (the agent name
  immediately follows the `###` prefix). Also note the `model:` and `tools:`
  values recorded in each Layer 2 section, and the `Spawned by:` field.

### Step 5 — Identify discrepancies

Compare the active agent list and extracted metadata against the map data:

- **`missing_from_map`** — an active agent has no corresponding `### <agent-name>`
  section in the Layer 2 portion of `docs/al-dev-agent-map.md`.
- **`stale_in_map`** — a `### <agent-name>` Layer 2 section exists for an agent
  that is archived (not in the active list).
- **`model_mismatch`** — the `model:` value in the agent frontmatter does not
  match the model recorded in the Layer 2 section for that agent.
- **`tools_mismatch`** — the `tools:` list in the agent frontmatter does not
  match the tools recorded in the Layer 2 section for that agent.
- **`caller_mismatch`** — the `Spawned by:` field in the Layer 2 section does
  not match the caller list derived from grep in Step 3. Record both the map
  value and the grep-derived value in `detail`.

### Step 6 — Write JSON report and return path

Construct the JSON object with all fields from the schema above. Populate
`total_files` from the active agent count, `map_entries` from the Layer 2
section count, and `discrepancies` from the issues found in Step 5. Write a
plain-English `summary` field (e.g. "3 discrepancies found: 2 missing_from_map,
1 stale_in_map.").

Write the report to `<result_dir>/audit/agent-audit.json`.

Verify the file exists: `ls -la <result_dir>/audit/agent-audit.json`.
If the file is not found, stop and report the failure — do not return a path
for a file that does not exist on disk.

Return only the absolute file path — no other prose.
