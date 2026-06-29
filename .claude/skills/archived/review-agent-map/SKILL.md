---
name: review-agent-map
description: >-
  Review profile-al-dev-shared agents for accuracy and update
  docs/agent-map.md. Use whenever agents are added, removed, or
  restructured in the plugin, or when you want to verify the map reflects
  the current state of agent files. Pass --no-update to run audit-only mode:
  reports discrepancies and suggests fixes without modifying any files.
  Replaces /audit-agents-against-map (use --no-update) and /update-agent-map.
  Triggers on: "review agent map", "update agent map", "sync agent map",
  "is the agent map accurate".
argument-hint: "[--no-update] [optional: agent name to focus on]"
---

# Review Agent Map

Audit `profile-al-dev-shared/agents/` and update `docs/agent-map.md`
so it accurately reflects the current active agents, their models, tools,
and caller relationships.

---

## Phase 0: Parse Arguments

Read `$ARGUMENTS`:
- If `--no-update` is present, set `NO_UPDATE=true`.
- If an agent name is present (not a flag), set it as `TARGET_AGENT` and
  focus all subsequent phases on that agent only.
- Flags are not exclusive: `--no-update al-dev-developer` is valid.

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

## Phase 4: Compare Against `docs/agent-map.md`

If `docs/agent-map.md` does not exist, skip to Phase 6 (write from
scratch).

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

Before editing, summarise findings:

```text
Agent map review findings:
Layer 1:
  - [issue or "✅ accurate"]
Layer 2 per-agent:
  - al-dev-developer: [issue or "✅ accurate"]
  - al-dev-solution-architect: [issue or "✅ accurate"]
  ...
Missing from map: [agents not in map]
Stale in map:    [agents in map but now archived]
```

If everything is accurate, say so and stop.

---

## Phase 5b: Audit-Only Exit (--no-update)

If `NO_UPDATE=true`:

For each discrepancy found in Phase 5, suggest specific fixes without modifying files:

**For Layer 1 (Catalog table):**
- To add an agent row: insert name, model, tools, spawned-by columns
- To remove an agent row: delete the table row
- To fix values: correct model, tools list, or spawned-by list

**For Layer 2 (Per-agent profiles):**
- To update a profile: rewrite the `### agent-name` section with corrected content
- To add a missing profile: insert a new section following the existing template
- To remove a stale profile: delete its `### agent-name` section entirely

**Present all suggested fixes without modifying files.** The user may:
- Run `/review-agent-map` (without `--no-update`) to apply all fixes.

Then stop. Do not proceed to Phase 6.

---

## Phase 6: Update the Map

If `docs/agent-map.md` does not exist, create it. Otherwise make
targeted edits to fix each discrepancy found in Phase 5.

**Document structure (full template for first-run creation):**

```markdown
# AL Dev Agent Map

**Last updated:** YYYY-MM-DD

## Layer 1: Agent Catalog

| Agent | Model | Tools | Spawned by |
|-------|-------|-------|------------|
| al-dev-developer | sonnet | Read, Write, Edit, Glob, Grep, Bash | /al-dev-develop, /al-dev-fix |
...

## Layer 2: Per-Agent Profiles

### <filename-without-.md>

**Description:** [first sentence from the agent description frontmatter]
**Model:** sonnet/opus/haiku
**Tools:** [comma-separated list from frontmatter]
**Spawned by:** /skill-a, /skill-b
**Inputs:** [table reproduced from agent file, or "Not documented"]
**Outputs:** [table reproduced from agent file, or "Not documented"]

---

[repeat for each active agent]
```

After writing or updating, confirm:
```bash
wc -l docs/agent-map.md
# Expected: roughly (active agent count × 5) lines minimum
```

Set `**Last updated:**` to today's date.

Commit if any edits were made:

```bash
git -C . add docs/agent-map.md
git -C . commit -m "docs: sync agent map with current agent roster"
```

> **Map accuracy only.** This skill no longer detects Inline candidates or any
> other design suggestion. Inline and all other structural findings now come
> from the design lenses dispatched by `/plugin-health-audit` and land in the
> health dossier. After syncing the map, run `/plugin-health-audit` to find
> improvements.
