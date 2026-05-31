---
name: sync-documentation-maps-skill-audit
description: >-
  Audits active skills in profile-al-dev-shared/skills/ against
  docs/al-dev-skills-map.md and writes a structured JSON discrepancy report
  to the run artifact directory. Called by /sync-documentation-maps dispatch phase.
model: claude-sonnet-4-6
tools: ["Read", "Bash", "Write"]
---

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

Compare the active skill list and extracted metadata against the map data:

- **`missing_from_map`** — an active skill has no corresponding `### /skill-name`
  section in the Layer 2 portion of `docs/al-dev-skills-map.md`.
- **`stale_in_map`** — a `### /skill-name` Layer 2 section exists for a skill
  that is archived (not in the active list).
- **`phase_count_mismatch`** — the phase count extracted from `SKILL.md` does not
  match the phase count implied by the map. Because the skills map has no
  explicit "phase count" field, derive the map's phase count from the `flowchart
  LR` Mermaid diagram in the skill's Layer 2 section: scan node IDs for the
  pattern `Phase<N>` (e.g. `Phase0`, `Phase4`) and take the highest N as the
  map's phase count; compare against the highest `## Phase N` heading number in
  `SKILL.md`. If the diagram is absent or the node IDs are ambiguous, record the
  discrepancy with `type: phase_count_mismatch` and a `detail` that describes
  the ambiguity (e.g. `"map shows phases 0–3, skill file has phases 0–5"`).
- **`agent_name_mismatch`** — an agent name extracted from `SKILL.md`
  (`al-dev-shared:<name>`) does not appear in the map's Layer 2 section for
  that skill.

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
