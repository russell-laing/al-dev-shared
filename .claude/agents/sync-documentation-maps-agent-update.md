---
name: sync-documentation-maps-agent-update
description: >-
  Reads agent audit findings from the run artifact directory and writes an
  updated docs/al-dev-agent-map.md to the run updates directory.
  Called by /sync-documentation-maps-collect update dispatch phase.
model: claude-haiku-4-5-20251001
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

### Step 1 — Read audit findings

Read `<result_dir>/audit/agent-audit.json`.

If the file does not exist, stop immediately and report:
`ERROR: agent-audit.json not found at <result_dir>/audit/agent-audit.json`
`— cannot proceed.`

Parse the `discrepancies` array. Note the `type` and associated `agent` field
for each entry. If `discrepancies` is empty, skip Step 3 (no edits
needed) and proceed directly to Step 4 to update the last-updated date.

### Step 2 — Read the current agent map

Read `docs/al-dev-agent-map.md` in full. This is the base document to update.
Keep the full content in memory; you will produce a complete updated version.

### Step 3 — Apply each discrepancy fix

Process every entry in the `discrepancies` array. For each entry, apply the
fix that matches its `type` using the procedures in
`.claude/knowledge/sync-maps-edit-cases.md`,
**"Agent surface — edit cases (update)"** section.

### Step 4 — Update the last-updated date

Replace the `**Last updated:**` value with today's date in `YYYY-MM-DD` format.
Do not change any other part of the preamble line.

### Step 5 — Write updated map and return path

Create the directory if it does not exist:

```bash
mkdir -p <result_dir>/updates
```

Write the complete updated map content to `<result_dir>/updates/agent-map.md`.

Verify the file was written:

```bash
ls -la <result_dir>/updates/agent-map.md
wc -l <result_dir>/updates/agent-map.md
```

If `wc -l` reports fewer than 50 lines, stop and report:
`ERROR: written file has <N> lines (expected ≥50) — content may be truncated.`

If the file does not begin with `# AL Dev`, stop and report:
`ERROR: written file does not begin with "# AL Dev" — content format incorrect.`

Return only the absolute file path — no other prose.
