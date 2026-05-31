---
name: sync-documentation-maps-skill-update
description: >-
  Reads skill audit findings from the run artifact directory and writes an
  updated docs/al-dev-skills-map.md to the run updates directory.
  Called by /sync-documentation-maps-collect update dispatch phase.
model: claude-sonnet-4-6
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

### Step 1 — Read audit findings

Read `<result_dir>/audit/skill-audit.json`.

If the file does not exist, stop immediately and report:
`ERROR: skill-audit.json not found at <result_dir>/audit/skill-audit.json — cannot proceed.`

Parse the `discrepancies` array. Note the `type` and associated `skill` field
for each entry. If `discrepancies` is empty, skip Step 3 (no edits
needed) and proceed directly to Step 4 to update the last-updated date.

### Step 2 — Read the current skills map

Read `docs/al-dev-skills-map.md` in full. This is the base document to update.
Keep the full content in memory; you will produce a complete updated version.

### Step 3 — Apply each discrepancy fix

Process every entry in the `discrepancies` array. For each entry, apply the
fix that matches its `type`:

**`missing_from_map`** — an active skill has no Layer 2 `### /skill-name` section.

1. Read `profile-al-dev-shared/skills/<skill>/SKILL.md` to extract the skill
   description (from the `description:` frontmatter field) and phase count
   (count `## Phase N` headings).
2. Insert a new Layer 2 `### /skill-name` section following the template
   pattern used by adjacent sections: include a description sentence, a
   `flowchart LR` Mermaid diagram with phase nodes matching the SKILL.md
   phase count, and an `Agents spawned:` list (extract all
   `al-dev-shared:<name>` patterns from SKILL.md).
3. If this skill belongs in the Layer 1 lifecycle diagram (i.e. it is a
   primary distributed skill referenced by other skills or tickets), add a
   node ID and edges in the Layer 1 Mermaid block and a matching `style`
   line.
4. After any Layer 1 edit, confirm every `style X` line refers to a node ID
   that exists in the diagram. Delete any orphaned `style` lines.

**`stale_in_map`** — a `### /skill-name` Layer 2 section exists for an archived skill.

1. Remove the entire `### /skill-name` Layer 2 section (heading through the
   next `###` or `##` heading, exclusive).
2. Remove any node, edge, and `style` line for this skill from the Layer 1
   Mermaid diagram.
3. After removal, scan all `style X` lines in Layer 1 and delete any whose
   node ID no longer appears in the diagram.

**`phase_count_mismatch`** — the Layer 2 Mermaid diagram phase count does not
match SKILL.md.

1. Read `profile-al-dev-shared/skills/<skill>/SKILL.md` and count `## Phase N`
   headings to determine the authoritative phase count.
2. Rewrite the `flowchart LR` Mermaid block in the Layer 2 section for this
   skill to use the correct number of phase nodes (Phase0 through PhaseN).
   Preserve existing node labels where they exist; add generic `PhaseN` labels
   for new nodes.

**`agent_name_mismatch`** — an agent reference in the Layer 2 section does not
match what SKILL.md declares.

1. Read `profile-al-dev-shared/skills/<skill>/SKILL.md` to extract the
   current `al-dev-shared:<name>` agent references.
2. In the Layer 2 section for this skill, update the `Agents spawned:` list
   to match the extracted references exactly.

After every Layer 1 edit, regardless of discrepancy type: confirm that every
`style X` line in the Layer 1 diagram has a matching node ID in that diagram.
Delete any orphaned `style` lines before proceeding.

### Step 4 — Update the last-updated date

Replace the `**Last updated:**` value with today's date in `YYYY-MM-DD` format.
Do not change any other part of the preamble line.

### Step 5 — Write updated map and return path

Create the directory if it does not exist:

```bash
mkdir -p <result_dir>/updates
```

Write the complete updated map content to `<result_dir>/updates/skills-map.md`.

Verify the file was written:

```bash
ls -la <result_dir>/updates/skills-map.md
wc -l <result_dir>/updates/skills-map.md
```

If `wc -l` reports fewer than 100 lines, stop and report:
`ERROR: written file has <N> lines (expected ≥100) — content may be truncated.`

If the file does not begin with `# AL Dev`, stop and report:
`ERROR: written file does not begin with "# AL Dev" — content format incorrect.`

Return only the absolute file path — no other prose.
