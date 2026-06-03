---
name: sync-documentation-maps-agent-audit
description: >-
  Audits active agents in profile-al-dev-shared/agents/ against
  docs/al-dev-agent-map.md and writes a structured JSON discrepancy report
  to the run artifact directory. Called by /sync-documentation-maps dispatch phase.
model: claude-haiku-4-5-20251001
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

### Step 3 — Cross-reference callers

For each active agent, derive `<agent-name>` by stripping the `.md` extension.
Run both grep commands against active (non-archived) skill directories and union
the results to build the caller list. Exclude archived skill directories to avoid
false positives from stale references:

```bash
grep -rl "al-dev-shared:<agent-name>" \
  profile-al-dev-shared/skills/ 2>/dev/null
find .claude/skills/ -not -path "*/archived/*" -type f | \
  xargs grep -l "al-dev-shared:<agent-name>" 2>/dev/null

grep -rl "<agent-name>" \
  profile-al-dev-shared/skills/ 2>/dev/null
find .claude/skills/ -not -path "*/archived/*" -type f | \
  xargs grep -l "<agent-name>" 2>/dev/null
```

After running all four commands, deduplicate the combined results: `sort -u`
the final caller list to remove duplicates from overlapping grep patterns.
The caller list is the deduplicated union of all files returned.

### Step 4 — Parse docs/al-dev-agent-map.md

Read `docs/al-dev-agent-map.md`. Extract:

- **Layer 1 Catalog table rows:** agent names listed in the Layer 1 table.
- **Layer 2 sections:** collect only `###` headings whose text matches the agent
  name pattern (starts with `al-dev-` or another defined agent prefix). Use:

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
grep-derived value for `caller_mismatch`; which map layer is absent for
`missing_from_map`).

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
