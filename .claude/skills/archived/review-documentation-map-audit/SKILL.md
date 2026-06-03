---
name: review-documentation-map-audit
description: >-
  Audit-only phase of /review-documentation-map. Scans the plugin surface,
  compares against the map, and suggests fixes — makes no file edits. Use
  when you want to check map accuracy without committing changes. Equivalent
  to /review-documentation-map --no-update.
  Triggers on: "audit skill map", "audit agent map", "check map accuracy",
  "are the maps accurate".
argument-hint: "--surface [skills|agents]"
---

# Review Documentation Map — Audit

Audit the plugin surface against the documentation map and suggest fixes.
Makes no file edits. Run `/review-documentation-map-update` to apply fixes.

---

## Phase 0: Parse Arguments

Read `$ARGUMENTS`:

- If `--surface skills` is present, set `SURFACE=skills`.
- If `--surface agents` is present, set `SURFACE=agents`.
- If neither is present, ask:

  > Which surface do you want to audit?
  >
  > 1. skills — audit `profile-al-dev-shared/skills/` against `docs/al-dev-skills-map.md`
  > 2. agents — audit `profile-al-dev-shared/agents/` against `docs/al-dev-agent-map.md`

Set variables based on SURFACE:

- `SURFACE=skills` → `SCAN_DIR=profile-al-dev-shared/skills/`,
  `ARCHIVED_DIR=profile-al-dev-shared/archived/skills/`,
  `MAP_FILE=docs/al-dev-skills-map.md`
- `SURFACE=agents` → `SCAN_DIR=profile-al-dev-shared/agents/`,
  `ARCHIVED_DIR=profile-al-dev-shared/archived/agents/`,
  `MAP_FILE=docs/al-dev-agent-map.md`

---

## Phase 1: Scan Plugin Surface

```bash
ls {SCAN_DIR}
ls {ARCHIVED_DIR} 2>/dev/null
```

Build two lists:

- **Active items** — `.md` files (agents) or directories (skills) in `{SCAN_DIR}` minus anything in `{ARCHIVED_DIR}`
- **Archived items** — excluded from all subsequent phases

---

## Phase 2: Extract Profiles

### If SURFACE=skills

For each active skill (read `profile-al-dev-shared/skills/<name>/SKILL.md`):

Extract:

1. **Phases** — numbered phases described in the skill body
2. **Agents spawned** — any `al-dev-shared:al-dev-*` agent type mentioned with a spawn directive
3. **Parallel pattern** — is the agent spawned ×1, ×2-3, or more?
4. **Outputs** — `.dev/` files the skill writes

Record in a working table:

| Skill | Phases | Agents spawned | Pattern | Outputs |
|-------|--------|----------------|---------|---------|

### If SURFACE=agents

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

---

## Phase 3: Cross-Reference Callers

### If SURFACE=agents

For each active agent, use a two-pass grep to find all skills that spawn it:

```bash
grep -rl "al-dev-shared:<filename-without-.md>" \
  profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null

grep -rl "<filename-without-.md>" \
  profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null
```

Union the file lists from both passes. Record:

- **Spawned by:** list of skill names
- **Spawn count:** single-use (1 skill) or shared (2+ skills)

### If SURFACE=skills

No cross-reference phase needed — agents spawned are extracted in Phase 2.

---

## Phase 4: Compare Against Map File

If `{MAP_FILE}` does not exist: report it as missing and stop.

Read the file. Check both layers:

### If SURFACE=skills

**Layer 1 (Lifecycle Overview diagram):**

- All active skills represented as nodes; no archived skills
- Node IDs in `style` directives match node IDs in edges
- File handoff labels match what skills actually produce
- Three entry paths are correct

**Layer 2 (Per-skill drill-downs):**

- Phases, agents, outputs match for each skill
- No skill missing from Layer 2

### If SURFACE=agents

**Layer 1 (Agent Catalog table):**

- All active agents as table rows; no archived agents
- Model and tools match frontmatter
- "Spawned by" matches Phase 3 results

**Layer 2 (Per-agent profiles):**

- Model, tools, spawned-by, Inputs/Outputs match for each agent

---

## Phase 4b: Report and Suggest Fixes

Summarise findings:

### If SURFACE=skills

```text
Plugin map review findings:
Layer 1:
  - [issue or "✅ accurate"]
Layer 2 per-skill:
  - /al-dev-ticket: [issue or "✅ accurate"]
  ...
Missing from map: [skills not in map]
Stale in map:    [skills in map but now archived]
```

### If SURFACE=agents

```text
Agent map review findings:
Layer 1:
  - [issue or "✅ accurate"]
Layer 2 per-agent:
  - al-dev-developer: [issue or "✅ accurate"]
  ...
Missing from map: [agents not in map]
Stale in map:    [agents in map but now archived]
```

If everything is accurate, say so and stop.

Otherwise suggest specific fixes without modifying files:

**For skills surface:**

- Layer 1: add/remove nodes, edges, and `style` directives; fix handoff labels
- Layer 2: rewrite/add/remove `### /skill-name` sections

**For agents surface:**

- Layer 1 (table): insert/delete rows; correct model, tools, spawned-by columns
- Layer 2: rewrite/add/remove `### agent-name` sections

Present all suggested fixes. To apply them, run `/review-documentation-map-update --surface {SURFACE}`.
