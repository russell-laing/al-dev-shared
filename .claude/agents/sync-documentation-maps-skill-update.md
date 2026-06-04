---
name: sync-documentation-maps-skill-update
description: >-
  Reads skill audit findings from the run artifact directory and writes an
  updated docs/al-dev-skills-map.md to the run updates directory.
  Called by /sync-documentation-maps-collect update dispatch phase.
model: claude-haiku-4-5-20251001
tools: ["Read", "Bash", "Write"]
---

# Sync Documentation Maps: Skill Map Update

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

### Step 1 — Read audit findings

For artifact verification, follow `.claude/skills/sync-documentation-maps/sync-agent-patterns.md`.

Read `<result_dir>/audit/skill-audit.json`. Stop if absent (see patterns doc).

Parse the `discrepancies` array. Note the `type` and associated `skill` field
for each entry. If `discrepancies` is empty, skip Step 3 (no edits
needed) and proceed directly to Step 4 to update the last-updated date.

### Step 2 — Read the current skills map

Read `docs/al-dev-skills-map.md` in full. This is the base document to update.
Keep the full content in memory; you will produce a complete updated version.

### Step 3 — Apply each discrepancy fix

Process every entry in the `discrepancies` array. For each entry, apply the
fix that matches its `type` using the procedures in
`.claude/knowledge/sync-maps-edit-cases.md`,
**"Skill surface — edit cases (update)"** section.

### Step 4 — Update the last-updated date

Replace the `**Last updated:**` value with today's date in `YYYY-MM-DD` format.
Do not change any other part of the preamble line. Never add a skill count to
this line — the count lives in the `Coverage` block inside the
`BEGIN/END GENERATED: skill-coverage` markers, is generator-owned, and must be
carried through verbatim (the write step regenerates it).

### Step 5 — Write updated map and return path

For path setup and write verification, follow
`.claude/skills/sync-documentation-maps/sync-agent-patterns.md`.
This surface requires ≥100 lines; apply the skills minimum from the patterns doc.

Write the complete updated map content to `<result_dir>/updates/skills-map.md`.

Return only the absolute file path — no other prose.
