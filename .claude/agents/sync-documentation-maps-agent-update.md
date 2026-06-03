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

**Common to all cases:**

- (a) Locate the target section in the map file before editing.
- (b) After each edit, verify: `wc -l <map-file>` did not decrease unexpectedly.

Case-specific edit logic follows.

Process every entry in the `discrepancies` array. For each entry, apply the
fix that matches its `type`:

**`missing_from_map`** — an active agent has no entry in the Layer 1 Catalog
table OR no `### <agent-name>` Layer 2 section.

1. Read `profile-al-dev-shared/agents/<agent-name>.md` to extract the agent's
   `model:`, `tools:` list, and `description:` frontmatter fields.
2. Add a new row to the Layer 1 Catalog table (`Agent | Model | Tools | Spawned by`);
   use the caller list from the discrepancy `detail` field, or `(none found)`.
3. Insert a new `### <agent-name>` Layer 2 profile section (before Observations
   if present) with `**Description:**`, `**Model:**`, `**Tools:**`, `**Spawned by:**` lines.

**`stale_in_map`** — an archived agent still has a Layer 1 row or Layer 2 section.

1. Remove the agent's row from the Layer 1 Catalog table.
2. Remove the entire `### <agent-name>` Layer 2 section (heading through the
   next `###` or `##` heading, exclusive).

**`model_mismatch`** — the `model:` value in the agent frontmatter does not
match the model recorded in the Layer 2 section.

1. Read `profile-al-dev-shared/agents/<agent-name>.md` to confirm the
   authoritative model value from frontmatter.
2. Update the `Model` column in the Layer 1 Catalog table row and the
   `**Model:**` line in the Layer 2 profile section for this agent.

**`tools_mismatch`** — the `tools:` list in the agent frontmatter does not
match the tools recorded in the Layer 2 section.

1. Read `profile-al-dev-shared/agents/<agent-name>.md` to confirm the
   authoritative tools list from frontmatter (use `(none)` if the list is `[]`).
2. Update the `Tools` column in the Layer 1 Catalog table row and the
   `**Tools:**` line in the Layer 2 profile section for this agent.

**`caller_mismatch`** — the `Spawned by:` field in the Layer 2 section does
not match the caller list derived from grep.

1. Use the grep-derived caller list from the discrepancy `detail` field
   (or `(none found)` if empty).
2. Update the `Spawned by` column in the Layer 1 Catalog table row and the
   `**Spawned by:**` line in the Layer 2 profile section for this agent.

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
