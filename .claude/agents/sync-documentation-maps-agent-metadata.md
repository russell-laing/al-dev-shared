---
name: sync-documentation-maps-agent-metadata
description: >-
  Builds the active agent list from profile-al-dev-shared/agents/ and extracts
  frontmatter metadata (model, tools, description, callers). Writes a structured
  JSON snapshot to the run artifact directory. Called by /sync-documentation-maps
  dispatch phase; its output is consumed by sync-documentation-maps-agent-discrepancy.
model: sonnet
tools: ["Read", "Bash", "Write"]
---

# sync-documentation-maps-agent-metadata

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-documentation-maps-runs/<run_id>/` |

## Outputs

Writes `<result_dir>/audit/agent-metadata.json` and returns its absolute path.
Do not summarise findings — return only the path.

**JSON schema:**

```json
{
  "surface": "agents",
  "run_id": "<run_id>",
  "total_files": 12,
  "agents": [
    {
      "name": "al-dev-example",
      "model": "sonnet",
      "tools": ["Read", "Bash"],
      "description": "First sentence of description field"
    }
  ],
  "callers": {
    "al-dev-example": ["al-dev-develop"]
  },
  "caller_check_skipped": false
}
```

---

## Instructions

All relative paths are from the repository root: `/Users/russelllaing/al-dev-shared`.

### Step 1 — Build active agent list

Run `ls profile-al-dev-shared/agents/` to get all agent file names.
Run `ls profile-al-dev-shared/archived/agents/ 2>/dev/null` to get archived names.
Active agents = `.md` files in `agents/` minus any names also present in `archived/agents/`.

### Step 2 — Extract metadata from each active agent

For each active agent, Read `profile-al-dev-shared/agents/<name>.md`. Extract:

- **model:** the `model:` frontmatter field value.
- **tools:** the `tools:` list. If empty `[]`, normalize to the string `(none)`.
- **description:** the first sentence of the `description:` field.

### Step 3 — Derive callers

```bash
python3 scripts/derive-agent-callers.py
```

On failure (non-zero exit or invalid JSON output): set `callers: {}` and
`caller_check_skipped: true` in the output JSON. Do not grep skill files as
a fallback.

### Step 4 — Write JSON and return path

Ensure `<result_dir>/audit/` exists (`mkdir -p`). Write `agent-metadata.json`.
Return only the absolute path.
