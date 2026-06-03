---
name: sync-documentation-maps-skill-audit
description: >-
  Audits active skills in profile-al-dev-shared/skills/ against
  docs/al-dev-skills-map.md and writes a structured JSON discrepancy report
  to the run artifact directory. Called by /sync-documentation-maps dispatch phase.
model: claude-haiku-4-5-20251001
tools: ["Read", "Bash", "Write"]
---

# Sync Documentation Maps: Skill Audit

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-documentation-maps-runs/<run_id>/` |

## Outputs

Writes `<result_dir>/audit/skill-audit.json` and returns its absolute path as
the sole output. Do not summarise findings to the user — return only the path.

**JSON schema:**

```json
{
  "surface": "skills",
  "run_id": "<run_id>",
  "total_files": 12,
  "map_entries": 11,
  "discrepancies": [
    {
      "type": "missing_from_map",
      "skill": "al-dev-example",
      "detail": "Active skill has no Layer 2 section in docs/al-dev-skills-map.md"
    }
  ],
  "summary": "1 discrepancy found: 1 missing_from_map."
}
```

Valid `type` values: `missing_from_map`, `stale_in_map`, `phase_count_mismatch`,
`agent_name_mismatch`.

---

## Instructions

All relative paths in these instructions are from the repository root:
`/Users/russelllaing/al-dev-shared`. Adjust paths if the working directory differs.

### Step 1 — Build active skill list

Run `ls profile-al-dev-shared/skills/` to get all skill directory names.
Run `ls profile-al-dev-shared/archived/skills/ 2>/dev/null` to get archived skill
names.
Active skills = skills/ list minus any names also present in archived/skills/.

### Step 2 — Extract metadata from each active skill

For each active skill, Read `profile-al-dev-shared/skills/<name>/SKILL.md`.
Extract:

- **Phase count:** count headings matching `## Phase N` (where N is a digit).
- **Agents spawned:** extract all `al-dev-shared:<agent-name>` patterns.
- **Output files:** extract all `.dev/` path strings referenced as write targets.

### Step 3 — Parse docs/al-dev-skills-map.md

Read `docs/al-dev-skills-map.md`. Extract:

- **Layer 1 node IDs:** flowchart node identifiers from the Layer 1 Mermaid diagram.
- **Layer 2 sections:** collect all `### /skill-name` headings (the skill name
  immediately follows the `/` prefix).

### Step 4 — Identify discrepancies

Compare the active skill list and extracted metadata against the map data.
Discrepancy type definitions are in `.claude/knowledge/sync-maps-edit-cases.md`,
**"Skill surface — discrepancy types (audit)"** section.

For each type found, construct a discrepancy entry with `type`, `skill`, and
`detail` fields. Populate `detail` with context (e.g., for `phase_count_mismatch`,
record both the map-derived count and the SKILL.md count).

### Step 5 — Write JSON report and return path

Construct the JSON object with all fields from the schema above. Populate
`total_files` from the active skill count, `map_entries` from the Layer 2
section count, and `discrepancies` from the issues found in Step 4. Write a
plain-English `summary` field (e.g. "3 discrepancies found: 2 missing_from_map,
1 stale_in_map.").

Write the report to `<result_dir>/audit/skill-audit.json`.

Verify the file exists: `ls -la <result_dir>/audit/skill-audit.json`.
If the file is not found, stop and report the failure — do not return a path
for a file that does not exist on disk.

Return only the absolute file path — no other prose.
