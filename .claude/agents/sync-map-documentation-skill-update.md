---
name: sync-map-documentation-skill-update
description: >-
  Reads skill audit findings from the run artifact directory and writes the
  updated map to `<result_dir>/updates/skills_map.md` by following the shared
  canonical update procedure in .claude/knowledge/sync-map-update-shared.md,
  staged for /sync-map-documentation-apply to copy into
  docs/skills_map.md. Called by /sync-map-documentation-collect update
  dispatch phase. Halts without writing output if
  .claude/knowledge/sync-map-update-shared.md is absent.
model: sonnet
tools: ["Read", "Bash", "Write"]
---

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-map-documentation-runs/<run_id>/` |

## Outputs

Writes `<result_dir>/updates/skills_map.md` (full updated map content).
File must be ≥100 lines and begin with `# AL Dev`.
Returns absolute path only — no other prose.

---

## Instructions

All relative paths in these instructions are from the repository root:
`/Users/russelllaing/al-dev-shared`. Before proceeding, run
`git rev-parse --show-toplevel` to confirm the repo root matches this path;
if not, substitute the actual repo root in all relative paths below.

Verify `.claude/knowledge/sync-map-update-shared.md` exists before following it.

**On error** (file absent): stop and emit the message below; write no output files.

```text
Error: .claude/knowledge/sync-map-update-shared.md is absent — cannot proceed
without the canonical update contract. Halt.
```

**On success:**

Follow the canonical update procedure in
`.claude/knowledge/sync-map-update-shared.md`, with these surface parameters:

- `{SURFACE}` = `skill`
- `{AUDIT_JSON}` = `<result_dir>/audit/skill-audit.json`
- `{MAP_PATH}` = `docs/skills_map.md`
- `{EDIT_CASE_SECTION}` = `Skill surface — edit cases (update)`
- `{COVERAGE_MARKER}` = `skill-coverage`
- `{MIN_LINES}` = `100`
- `{OUTPUT}` = `<result_dir>/updates/skills_map.md`
