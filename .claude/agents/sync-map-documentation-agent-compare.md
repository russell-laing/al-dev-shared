---
name: sync-map-documentation-agent-compare
description: >-
  Compares agent metadata from agent-metadata.json against docs/agent_map.md
  and writes a structured JSON discrepancy report to the run artifact directory.
  Called by /sync-map-documentation dispatch phase after
  collect-agent-metadata completes.
model: sonnet
tools: ["Read", "Bash", "Write"]
---

## Inputs

| Field | Description |
|---|---|
| run_id | The timestamp run ID (e.g. `20260531T143000`) |
| result_dir | Absolute path to `.dev/sync-map-documentation-runs/<run_id>/` |

**Precondition:** `<result_dir>/audit/agent-metadata.json` must exist (written by
`collect-agent-metadata`).

## Outputs

Writes `<result_dir>/audit/agent-audit.json` and returns its absolute path.
Do not summarise findings — return only the path.

**JSON schema:**

```json
{
  "surface": "agents",
  "run_id": "<run_id>",
  "total_files": 12,
  "map_entries": 11,
  "discrepancies": [
    {
      "type": "missing_from_map",
      "agent": "al-dev-example",
      "detail": "Active agent has no Layer 2 section in docs/agent_map.md"
    }
  ],
  "summary": "1 discrepancy found: 1 missing_from_map."
}
```

Valid `type` values: `missing_from_map`, `stale_in_map`, `model_mismatch`,
`tools_mismatch`, `caller_mismatch`. `unclassifiable_type` is an additional
entry type emitted only when a `type` value has no definition in the canonical
section (see Step 3); it is counted in the `summary` like any other, e.g.
`"summary": "2 discrepancies found: 1 missing_from_map, 1 unclassifiable_type."`

---

## Instructions

All relative paths are from the repository root: `/Users/russelllaing/al-dev-shared`.

### Step 1 — Load metadata

Read `<result_dir>/audit/agent-metadata.json`. Use the `agents` list and `callers`
map from that file for all subsequent comparisons.

### Step 2 — Parse docs/agent_map.md

Read `docs/agent_map.md`. Extract Layer 1 Catalog table rows and Layer 2
sections. Use:

```bash
grep "^### al-dev-" docs/agent_map.md
```

For each matched heading, note the `model:`, `tools:`, and `Spawned by:` values
recorded in that Layer 2 section. Map entries record an empty tools list as
`(none)` — compare directly against the `(none)` string from Step 1.

### Step 3 — Identify discrepancies

Compare the agents list and metadata against map data. Discrepancy type definitions
are in `.claude/knowledge/sync-maps-edit-cases.md`,
**"Agent surface — discrepancy types (audit)"** section.

If that section is missing or unreadable, **stop and report** the missing
canonical comparison contract (`.claude/knowledge/sync-maps-edit-cases.md`).
Do not emit a discrepancy report from the legal `type` names alone — the section
holds the classification rules (either-layer absence, archived-object detection,
tools/caller normalization, phase-node interpretation), without which the audit
cannot be relied on.

If that section is **present but contains definitions for only a subset of the
valid `type` values**, use the definitions that are present. For any `type` value
that appears in the audit JSON but has no definition in the section, add a
discrepancy entry to the final JSON `discrepancies` array — this is **not** a
blocking stop; the audit still completes — with `type: "unclassifiable_type"`,
`agent: <name>`,
`detail: "type '<value>' has no definition in sync-maps-edit-cases.md Agent surface section"`.
Count it in the `summary` field alongside the other discrepancy types.

Otherwise (all `type` values found in Step 3 are defined in the section), proceed to
Step 4 discrepancy comparison without adding any unclassifiable-type entries.

If `caller_check_skipped` is `true` in the metadata JSON, skip `caller_mismatch`
detection and note it in the summary.

### Step 4 — Write JSON report and return path

For path setup, JSON construction, and artifact verification, follow
`.claude/skills/sync-map-documentation/sync-agent-patterns.md`.
Write to `<result_dir>/audit/agent-audit.json`. Return only the absolute path.
