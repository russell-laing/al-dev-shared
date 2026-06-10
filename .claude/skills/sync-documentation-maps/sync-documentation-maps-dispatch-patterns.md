# Sync-Documentation-Maps Audit-Agent Dispatch Patterns

Canonical dispatch template for the two background audit agents used in
`/sync-documentation-maps` Phase 3. Reference this doc when adding new callers
so the template does not drift. Mirrors `collect-dispatch-patterns.md` for
the update-agent side.

---

## Audit-Agent Dispatch Template

Dispatch **both** audit agents simultaneously with `run_in_background: true`.
Vary only the three surface parameters in the table below. Use the `Agent` tool
per the canonical Background-Agent Dispatch Pattern in `checkpoint-patterns.md`.

```text
Agent: <SUBAGENT_TYPE>
Prompt:
  Audit <TARGET_DESCRIPTION> against <MAP_FILE>.

  Inputs:
  - run_id: <RUN_ID>
  - result_dir: <RUN_DIR>

  Write audit findings to <result_dir>/audit/<OUTPUT_FILE> per the schema in
  your agent definition.
```

| Surface | `<SUBAGENT_TYPE>` | `<TARGET_DESCRIPTION>` / `<MAP_FILE>` | `<OUTPUT_FILE>` |
|---------|-------------------|----------------------------------------|-----------------|
| Skills  | `sync-documentation-maps-skill-audit` | `skills in profile-al-dev-shared/skills/` against `docs/al-dev-skills-map.md` | `skill-audit.json` |
| Agents  | `sync-documentation-maps-agent-audit` | `agents in profile-al-dev-shared/agents/` against `docs/al-dev-agent-map.md` | `agent-audit.json` |

---

## Return Values

Capture the returned background agent IDs as `SKILL_TEAM_ID` and `AGENT_TEAM_ID`.
These IDs are informational checkpoint fields — the authoritative handoff is the
audit JSON each agent writes to `${RUN_DIR}/audit/`, which
`/sync-documentation-maps-collect` reads directly. Do **not** poll these IDs
with `TaskGet`.
