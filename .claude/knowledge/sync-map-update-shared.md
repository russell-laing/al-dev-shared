# Shared procedure: documentation-map update agents

Canonical 5-step update procedure shared by `sync-map-documentation-agent-update`
and `sync-map-documentation-skill-update`. Each agent references this doc and
supplies the surface-specific parameters listed below; do not duplicate the steps
in the agent bodies.

Parameters supplied by the caller agent:

| Placeholder | agent-update | skill-update |
| ------------- | -------------- | -------------- |
| `{SURFACE}` | `agent` | `skill` |
| `{AUDIT_JSON}` | `<result_dir>/audit/agent-audit.json` | `<result_dir>/audit/skill-audit.json` |
| `{MAP_PATH}` | `docs/agent_map.md` | `docs/skills_map.md` |
| `{EDIT_CASE_SECTION}` | Agent surface — edit cases (update) | Skill surface — edit cases (update) |
| `{COVERAGE_MARKER}` | `agent-coverage` | `skill-coverage` |
| `{MIN_LINES}` | 50 | 100 |
| `{OUTPUT}` | `<result_dir>/updates/agent_map.md` | `<result_dir>/updates/skills_map.md` |

## Error handling

**Halt conditions:** If any of the following occur during plan generation, halt
immediately without writing output and report the error to the user:

1. **Missing source document** — The audit findings file referenced in Phase 1 does
   not exist or is empty. Report: "No audit findings found at <path>; run
   /discover-plugin-health first."

2. **Malformed JSON in audit report** — The JSON structure from the audit agent
   does not match the expected schema (missing `findings` array, invalid verdict
   values, etc.). Report: "Audit report malformed at <path>; regenerate with
   /discover-plugin-health."

3. **Empty findings after filter** — The dimensional or surface filter produces
   zero results. This may indicate over-filtering or stale audit data. Report:
   "No findings match filter <filter>; check surface/dimension values and audit
   recency."

**Logging:** Include the absolute path to the blocking file and the exact
conditional that triggered the halt in your error message so users can diagnose
and fix without re-running the entire audit.

## Step 1 — Read audit findings

For artifact verification, follow `.claude/skills/sync-map-documentation/sync-agent-patterns.md`.

Read the surface audit JSON from the run artifact directory. Stop if absent
(see patterns doc).

Parse the `discrepancies` array. Note the `type` and associated surface field
for each entry. If `discrepancies` is empty, skip Step 3 (no edits needed) and
proceed directly to Step 4 to update the last-updated date.

## Step 2 — Read the current map

Read the current surface map in full. This is the base document to update.
Keep the full content in memory; you will produce a complete updated version.

## Step 3 — Apply each discrepancy fix

Process every entry in the `discrepancies` array. For each entry, apply the
fix that matches its `type` using the procedures in
`.claude/knowledge/sync-maps-edit-cases.md`, in the surface-specific edit
cases section named in the parameter table above.

## Step 4 — Update the last-updated date

Replace the `**Last updated:**` value with today's date in `YYYY-MM-DD` format.
Do not change any other part of the preamble line. Never add a surface count to
this line — the count lives in the `Coverage` block inside the generated
coverage markers, is generator-owned, and must be carried through verbatim (the
write step regenerates it).

## Step 5 — Write updated map and return path

For path setup and write verification, follow
`.claude/skills/sync-map-documentation/sync-agent-patterns.md`.
This surface requires the minimum line count specified in the parameter table
above.

Write the complete updated map content to the surface output path.

Return only the absolute file path — no other prose.
