---
name: sync-documentation-maps-skill-update
description: >-
  Reads skill audit findings from the run artifact directory and writes the
  updated map to `<result_dir>/updates/skills-map.md` by following the shared
  canonical update procedure in .claude/knowledge/sync-map-update-shared.md,
  staged for /sync-documentation-maps-apply to copy into
  docs/al-dev-skills-map.md. Called by /sync-documentation-maps-collect update
  dispatch phase.
model: haiku
tools: ["Read", "Bash", "Write"]
---

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-documentation-maps-runs/<run_id>/` |

## Outputs

Writes `<result_dir>/updates/skills-map.md` (full updated map content).
File must be ≥100 lines and begin with `# AL Dev`.
Returns absolute path only — no other prose.

---

## Instructions

All relative paths in these instructions are from the repository root:
`/Users/russelllaing/al-dev-shared`. Adjust paths if the working directory differs.

Verify `.claude/knowledge/sync-map-update-shared.md` exists before following it;
if it is absent, stop and emit:

```text
Error: .claude/knowledge/sync-map-update-shared.md is absent — cannot proceed
without the canonical update contract. Halt.
```

Write no output files.

Follow the canonical update procedure in
`.claude/knowledge/sync-map-update-shared.md`, with these surface parameters:

- `{SURFACE}` = `skill`
- `{AUDIT_JSON}` = `<result_dir>/audit/skill-audit.json`
- `{MAP_PATH}` = `docs/al-dev-skills-map.md`
- `{EDIT_CASE_SECTION}` = `Skill surface — edit cases (update)`
- `{COVERAGE_MARKER}` = `skill-coverage`
- `{MIN_LINES}` = `100`
- `{OUTPUT}` = `<result_dir>/updates/skills-map.md`
