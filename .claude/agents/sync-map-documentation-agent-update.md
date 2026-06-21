---
name: sync-map-documentation-agent-update
description: >-
  Reads agent audit findings from the run artifact directory and writes the
  updated map to `<result_dir>/updates/agent-map.md` by following the shared
  canonical update procedure in .claude/knowledge/sync-map-update-shared.md,
  staged for /sync-map-documentation-apply to copy into
  docs/al-dev-agent-map.md. Called by /sync-map-documentation-collect update
  dispatch phase.
model: sonnet
tools: ["Read", "Bash", "Write"]
---

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-map-documentation-runs/<run_id>/` |

## Outputs

Writes `<result_dir>/updates/agent-map.md` (full updated map content).
File must be ≥50 lines and begin with `# AL Dev`.
Returns absolute path only — no other prose.

---

## Instructions

All relative paths in these instructions are from the repository root:
`/Users/russelllaing/al-dev-shared`. Before proceeding, run
`git rev-parse --show-toplevel` to confirm the repo root matches this path;
if not, substitute the actual repo root in all relative paths below.

If `git rev-parse --show-toplevel` fails or returns a path that is not the
al-dev-shared repository root, stop and emit the error
"agent-update: could not resolve repo root — aborting map update". Write the
error message to stdout. Write no output files.
Return no artifact paths to the caller — an absent output signals a halted agent.

Verify `.claude/knowledge/sync-map-update-shared.md` exists before following it;
if it is absent, stop and emit:

```text
Error: .claude/knowledge/sync-map-update-shared.md is absent — cannot proceed
without the canonical update contract. Halt.
```

Write no output files. Write the error message to stdout.
Return no artifact paths to the caller — an absent output signals a halted agent.

Follow the canonical update procedure in
`.claude/knowledge/sync-map-update-shared.md`, with these surface parameters:

- `{SURFACE}` = `agent`
- `{AUDIT_JSON}` = `<result_dir>/audit/agent-audit.json`
- `{MAP_PATH}` = `docs/al-dev-agent-map.md`
- `{EDIT_CASE_SECTION}` = `Agent surface — edit cases (update)`
- `{COVERAGE_MARKER}` = `agent-coverage`
- `{MIN_LINES}` = `50`
- `{OUTPUT}` = `<result_dir>/updates/agent-map.md`
