---
name: audit-agents-against-map
description: >-
  Use when verifying that profile-al-dev-shared agents are accurately documented
  in the map without modifying files. Scans agent files, extracts profiles,
  cross-references callers, compares against current map, reports discrepancies.
  For audit-only workflows (CI verification, dry-run before update).
---

> **ARCHIVED 2026-05-31** — Use `/review-agent-map --no-update` instead.

---

# Audit Agents Against Map

Audit `profile-al-dev-shared/agents/` and verify `docs/al-dev-agent-map.md`
accurately reflects the current active agents, their models, tools, and caller
relationships. **No file modifications** — findings only.

Usage: `/audit-agents-against-map [agent-name]`.

---

## Phase 1: Scan Agent Files

Run these commands and record the results:

```bash
# Active agents
ls profile-al-dev-shared/agents/

# Archived agents (excluded from the map)
ls profile-al-dev-shared/archived/agents/ 2>/dev/null
```

Build two lists:
- **Active agents** — `.md` files in `agents/` minus anything in `archived/agents/`
- **Archived agents** — excluded from all subsequent phases

---

## Phase 2: Extract Agent Profiles

For each active agent (read `profile-al-dev-shared/agents/<name>.md`):

Extract from frontmatter:
1. **model** — `sonnet`, `opus`, or `haiku`
2. **tools** — full tools list
3. **description** — first sentence only

Extract from body:
4. **Inputs table** — the `## Inputs` section (or "Not documented" if absent)
5. **Outputs table** — the `## Outputs` section (or "Not documented" if absent)

Record in a working table:

| Agent | Model | Tools | Has Inputs? | Has Outputs? |
|-------|-------|-------|-------------|--------------|

If `$ARGUMENTS` is an agent name, focus only on that agent and skip the rest.

---

## Phase 3: Cross-Reference Callers

For each active agent, use a two-pass grep to find all skills that spawn it.
Skills may reference agents by qualified type name (`al-dev-shared:<name>`)
or by short filename stem in prose — search both forms and union the results:

```bash
# Pass 1: qualified type name (used in subagent_type YAML blocks)
grep -rl "al-dev-shared:<filename-without-.md>" \
  profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null

# Pass 2: short name prose references
grep -rl "<filename-without-.md>" \
  profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null
```

Union the file lists from both passes to get the full caller set.

If `$ARGUMENTS` names a specific agent, restrict both passes to that agent only.

Record:
- **Spawned by:** list of skill names (extract directory name from matching paths)
- **Spawn count:** single-use (1 skill) or shared (2+ skills)

---

## Phase 4: Compare Against `docs/al-dev-agent-map.md`

If `docs/al-dev-agent-map.md` does not exist, note: "Agent map does not exist yet." and stop.

Read the file. Check:

### Layer 1 (Agent Catalog table)

Verify:
- All active agents appear as table rows
- No archived agent appears as a row
- Model and tools match the actual frontmatter values
- "Spawned by" matches the grep results from Phase 3

### Layer 2 (Per-agent profiles)

For each active agent, verify the `### <filename-without-.md>` section
(e.g., `### al-dev-developer`, `### commit-learn-verifier`):
- Model and tools list match the frontmatter
- Spawned-by list matches Phase 3 results
- Inputs/Outputs match Phase 2 findings (or "Not documented" if absent)

---

## Phase 5: Report Discrepancies

Before suggesting edits, summarise findings:

```
Agent map audit findings:
Layer 1:
  - [issue or "✅ accurate"]
Layer 2 per-agent:
  - al-dev-developer: [issue or "✅ accurate"]
  - al-dev-solution-architect: [issue or "✅ accurate"]
  ...
Missing from map: [agents not in map]
Stale in map:    [agents in map but now archived]
```

If everything is accurate, report: **"Agent map is accurate. No discrepancies found."** and stop.

---

## Phase 6: Suggest Fixes

For each discrepancy found, suggest specific fixes:

**For Layer 1 (Catalog table):**
- To add an agent row: insert name, model, tools, spawned-by columns
- To remove an agent row: delete the table row
- To fix values: correct model, tools list, or spawned-by list

**For Layer 2 (Per-agent profiles):**
- To update a profile: rewrite the `### agent-name` section with corrected content
- To add a missing profile: insert a new section following the existing template
- To remove a stale profile: delete its `### agent-name` section entirely

**Present all suggested fixes to the user without modifying files.** The user may:
- Run `/update-agent-map` to apply all fixes
- Run `/update-agent-map <agent-name>` to update a specific agent
- Run `/audit-agents-against-map` again after manual updates

---

## Next Steps

To apply changes, user should run `/update-agent-map`.
