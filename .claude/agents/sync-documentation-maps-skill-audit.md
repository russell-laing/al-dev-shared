---
name: sync-documentation-maps-skill-audit
description: >-
  Audits active skills in profile-al-dev-shared/skills/ against
  docs/al-dev-skills-map.md and writes a structured JSON discrepancy report
  to the run artifact directory. Called by /sync-documentation-maps dispatch phase.
model: haiku
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
- **Output files:** extract all `.dev/` write-target paths. First normalize any
  templated date to the literal `YYYY-MM-DD`, then extract candidate paths, then
  keep only those on lines that mention a write verb. The write-verb list
  (`write`, `writes`, `Write`, `save`, `output to`, `→`) is indicative, not
  exhaustive — keep a path when the line clearly directs writing it. Use:
  `sed -E 's/\$\(date \+[^)]*\)/YYYY-MM-DD/g' <SKILL.md> | grep -oE '\.dev/[A-Za-z0-9._/-]+\.(md|json|log)'`
  This captures both literal-dated and `$(date ...)`-templated artifacts in the
  normalized `YYYY-MM-DD` form used by the map.

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

For path setup, JSON result construction, and artifact verification, follow
`.claude/skills/sync-documentation-maps/sync-agent-patterns.md`.

Write the report to `<result_dir>/audit/skill-audit.json`.

Return only the absolute file path — no other prose.
