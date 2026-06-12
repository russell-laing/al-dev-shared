---
name: sync-documentation-maps-agent-update
description: >-
  Reads agent audit findings from the run artifact directory and writes the
  updated map to `<result_dir>/updates/agent-map.md` by following the shared
  canonical update procedure in .claude/knowledge/sync-map-update-shared.md,
  staged for /sync-documentation-maps-apply to copy into
  docs/al-dev-agent-map.md. Called by /sync-documentation-maps-collect update
  dispatch phase.
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

Verify `.claude/knowledge/sync-map-update-shared.md` exists before following it;
if it is absent, stop and report the missing canonical update procedure rather
than improvising the map edit.

Follow the canonical update procedure in
`.claude/knowledge/sync-map-update-shared.md`, with these surface parameters:

- `{SURFACE}` = `agent`
- `{AUDIT_JSON}` = `<result_dir>/audit/agent-audit.json`
- `{MAP_PATH}` = `docs/al-dev-agent-map.md`
- `{EDIT_CASE_SECTION}` = `Agent surface — edit cases (update)`
- `{COVERAGE_MARKER}` = `agent-coverage`
- `{MIN_LINES}` = `50`
- `{OUTPUT}` = `<result_dir>/updates/agent-map.md`
