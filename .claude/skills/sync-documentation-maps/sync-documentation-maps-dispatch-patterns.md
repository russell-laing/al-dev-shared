# Sync-Documentation-Maps Audit-Agent Dispatch Patterns

Canonical dispatch template for the four audit agents used in
`/sync-documentation-maps` Phase 3. Reference this doc when adding new callers
so the template does not drift. Mirrors `collect-dispatch-patterns.md` for
the update-agent side.

The audit phase runs in two sequential steps: metadata agents must complete
before discrepancy agents are dispatched (discrepancy agents read the
`*-metadata.json` files written by metadata agents).

---

## Step 3.1 — Metadata Agent Dispatch Template

Dispatch **both** metadata agents simultaneously with `run_in_background: false`
(synchronous — discrepancy agents cannot start until metadata is ready).
Use the `Agent` tool per the canonical Background-Agent Dispatch Pattern in
`checkpoint-patterns.md`.

```text
Agent: <SUBAGENT_TYPE>
Prompt:
  Extract metadata for <TARGET_DESCRIPTION>.

  Inputs:
  - run_id: <RUN_ID>
  - result_dir: <RUN_DIR>

  Write metadata snapshot to <result_dir>/audit/<OUTPUT_FILE> per the schema in
  your agent definition.
```

| Surface | `<SUBAGENT_TYPE>` | `<TARGET_DESCRIPTION>` | `<OUTPUT_FILE>` |
|---------|-------------------|------------------------|-----------------|
| Skills  | `sync-documentation-maps-skill-metadata` | `skills in profile-al-dev-shared/skills/` | `skill-metadata.json` |
| Agents  | `sync-documentation-maps-agent-metadata` | `agents in profile-al-dev-shared/agents/` | `agent-metadata.json` |

**Wait for both metadata agents to complete before proceeding to Step 3.2.**

Capture the returned agent IDs as `SKILL_METADATA_TEAM_ID` and `AGENT_METADATA_TEAM_ID`.

---

## Step 3.2 — Discrepancy Agent Dispatch Template

Dispatch **both** discrepancy agents simultaneously with `run_in_background: true`
after Step 3.1 metadata agents have completed.
Use the `Agent` tool per the canonical Background-Agent Dispatch Pattern in
`checkpoint-patterns.md`.

```text
Agent: <SUBAGENT_TYPE>
Prompt:
  Detect discrepancies for <TARGET_DESCRIPTION> against <MAP_FILE>.

  Inputs:
  - run_id: <RUN_ID>
  - result_dir: <RUN_DIR>

  Read <result_dir>/audit/<INPUT_FILE> (written by the metadata agent) and
  write discrepancy report to <result_dir>/audit/<OUTPUT_FILE> per the schema
  in your agent definition.
```

| Surface | `<SUBAGENT_TYPE>` | `<TARGET_DESCRIPTION>` / `<MAP_FILE>` | `<INPUT_FILE>` | `<OUTPUT_FILE>` |
|---------|-------------------|-----------------------------------------|----------------|-----------------|
| Skills  | `sync-documentation-maps-skill-compare` | `skills in profile-al-dev-shared/skills/` against `docs/al-dev-skills-map.md` | `skill-metadata.json` | `skill-audit.json` |
| Agents  | `sync-documentation-maps-agent-compare` | `agents in profile-al-dev-shared/agents/` against `docs/al-dev-agent-map.md` | `agent-metadata.json` | `agent-audit.json` |

---

## Return Values

Capture the returned background agent IDs as `SKILL_DISCREPANCY_TEAM_ID` and
`AGENT_DISCREPANCY_TEAM_ID` (plus the metadata IDs from Step 3.1).
These IDs are informational checkpoint fields — the authoritative handoff is the
audit JSON each agent writes to `${RUN_DIR}/audit/`, which
`/sync-documentation-maps-collect` reads directly. Do **not** poll these IDs
with `TaskGet`.
