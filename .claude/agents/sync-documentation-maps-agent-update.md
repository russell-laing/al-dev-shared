---
name: sync-documentation-maps-agent-update
description: >-
  Reads agent audit findings from the run artifact directory and writes an
  updated docs/al-dev-agent-map.md to the run updates directory.
  Called by /sync-documentation-maps-collect update dispatch phase.
model: haiku
tools: ["Read", "Bash", "Write"]
---

# Sync Documentation Maps: Agent Map Update

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-documentation-maps-runs/<run_id>/` |

## Outputs

Writes `<result_dir>/updates/agent-map.md` (full updated map content).
File must be ≥50 lines and begin with `# AL Dev`.
Returns absolute path only — no other prose.

---

## Instructions

All relative paths in these instructions are from the repository root:
`/Users/russelllaing/al-dev-shared`. Adjust paths if the working directory differs.

Follow the canonical update procedure in
`.claude/knowledge/sync-map-update-shared.md`, with these surface parameters:

- `{SURFACE}` = `agent`
- `{AUDIT_JSON}` = `<result_dir>/audit/agent-audit.json`
- `{MAP_PATH}` = `docs/al-dev-agent-map.md`
- `{EDIT_CASE_SECTION}` = `Agent surface — edit cases (update)`
- `{COVERAGE_MARKER}` = `agent-coverage`
- `{MIN_LINES}` = `50`
- `{OUTPUT}` = `<result_dir>/updates/agent-map.md`
