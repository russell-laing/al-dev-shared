---
name: sync-documentation-maps-skill-discrepancy
description: >-
  Compares skill metadata from skill-metadata.json against docs/al-dev-skills-map.md
  and writes a structured JSON discrepancy report to the run artifact directory.
  Called by /sync-documentation-maps dispatch phase after
  sync-documentation-maps-skill-metadata completes.
model: sonnet
tools: ["Read", "Bash", "Write"]
---

# sync-documentation-maps-skill-discrepancy

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-documentation-maps-runs/<run_id>/` |

**Precondition:** `<result_dir>/audit/skill-metadata.json` must exist (written by
`sync-documentation-maps-skill-metadata`).

## Outputs

Writes `<result_dir>/audit/skill-audit.json` and returns its absolute path.
Do not summarise findings — return only the path.

**JSON schema:**

```json
{
  "surface": "skills",
  "run_id": "<run_id>",
  "total_files": 19,
  "map_entries": 19,
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

All relative paths are from the repository root: `/Users/russelllaing/al-dev-shared`.

### Step 1 — Load metadata

Read `<result_dir>/audit/skill-metadata.json`. Use the `skills` list from that file
for all subsequent comparisons. Each skill entry includes `phase_count` and
`spawned_agents` — these are required for `phase_count_mismatch` and
`agent_name_mismatch` detection.

### Step 2 — Parse docs/al-dev-skills-map.md

Read `docs/al-dev-skills-map.md`. Extract:

```bash
grep "^### " docs/al-dev-skills-map.md
```

- **Layer 1 node IDs:** flowchart node identifiers from the Layer 1 Mermaid diagram.
- **Layer 2 sections:** collect all `### /skill-name` headings (the skill name
  immediately follows the `/` prefix).

For each Layer 2 section, note the phase nodes in the `flowchart LR` Mermaid
diagram and the `Agents spawned:` list.

### Step 3 — Identify discrepancies

Compare the active skill list and extracted metadata against the map data.
Discrepancy type definitions are in `.claude/knowledge/sync-maps-edit-cases.md`,
**"Skill surface — discrepancy types (audit)"** section.

If that section is missing or unreadable, **stop and report** the missing
canonical comparison contract (`.claude/knowledge/sync-maps-edit-cases.md`).
Do not emit a discrepancy report from the legal `type` names alone — the section
holds the classification rules (either-layer absence, archived-object detection,
tools/caller normalization, phase-node interpretation), without which the audit
cannot be relied on.

For each type found, construct a discrepancy entry with `type`, `skill`, and
`detail` fields. Populate `detail` with context (e.g., for `phase_count_mismatch`,
record both the map-derived count and the SKILL.md count from `skill-metadata.json`).

### Step 4 — Write JSON report and return path

For path setup, JSON construction, and artifact verification, follow
`.claude/skills/sync-documentation-maps/sync-agent-patterns.md`.
Write to `<result_dir>/audit/skill-audit.json`. Return only the absolute path.
