---
name: review-documentation-map-update
description: >-
  Update phase of /review-documentation-map. Scans the plugin surface,
  compares against the map, applies edits, and commits. Equivalent to
  /review-documentation-map without --no-update. Run /review-documentation-map-audit
  first if you want to preview changes before committing.
  Triggers on: "update skill map", "update agent map", "apply map fixes",
  "commit map changes".
argument-hint: "--surface [skills|agents]"
---

# Review Documentation Map — Update

Audit the plugin surface against the documentation map, apply targeted edits,
and commit. To preview changes first without committing, run
`/review-documentation-map-audit --surface {SURFACE}`.

---

## Phase 0: Parse Arguments

Read `$ARGUMENTS`:

- If `--surface skills` is present, set `SURFACE=skills`.
- If `--surface agents` is present, set `SURFACE=agents`.
- If neither is present, ask:

  > Which surface do you want to update?
  >
  > 1. skills — update `docs/skills-map.md` from `profile-al-dev-shared/skills/`
  > 2. agents — update `docs/agent-map.md` from `profile-al-dev-shared/agents/`

Set variables based on SURFACE:

- `SURFACE=skills` → `SCAN_DIR=profile-al-dev-shared/skills/`,
  `ARCHIVED_DIR=profile-al-dev-shared/archived/skills/`,
  `MAP_FILE=docs/skills-map.md`
- `SURFACE=agents` → `SCAN_DIR=profile-al-dev-shared/agents/`,
  `ARCHIVED_DIR=profile-al-dev-shared/archived/agents/`,
  `MAP_FILE=docs/agent-map.md`

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

If `{MAP_FILE}` does not exist, skip to Phase 5 (write from scratch).

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

Summarise findings before editing:

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

---

## Phase 5: Update the Map

If `{MAP_FILE}` does not exist, create it. Otherwise make targeted edits to fix
each discrepancy. Use the Edit tool for targeted changes (not full rewrites)
whenever the file already exists.

### If SURFACE=skills

**For Layer 1 fixes:**

- To add a skill: add a node and edge in the flowchart, add a `style` directive
- To remove a skill: remove its node declaration, all edges, and its `style` directive — leave no orphaned `style` lines
- To fix a handoff label: update the `-->|label|` on the relevant edge

**For Layer 2 fixes:**

- To update a drill-down: rewrite the affected `flowchart LR` block
- To add a missing skill: insert a new `### /skill-name` section following existing conventions
- To remove a stale skill: delete its `### /skill-name` section entirely

**Mermaid style guard:** After any edit, scan every `style X fill:...` line. Confirm
`X` matches an ID in at least one node declaration or edge. Delete orphaned `style` lines.

### If SURFACE=agents

**Document structure (for first-run creation):**

```markdown
# AL Dev Agent Map

**Last updated:** {TODAY}

## Layer 1: Agent Catalog

| Agent | Model | Tools | Spawned by |
|-------|-------|-------|------------|
| al-dev-developer | sonnet | Read, Write, Edit, Glob, Grep, Bash | /al-dev-develop, /al-dev-fix |
...

## Layer 2: Per-Agent Profiles

### <filename-without-.md>

**Description:** [first sentence from agent description frontmatter]
**Model:** sonnet/opus/haiku
**Tools:** [comma-separated list from frontmatter]
**Spawned by:** /skill-a, /skill-b
**Inputs:** [table reproduced from agent file, or "Not documented"]
**Outputs:** [table reproduced from agent file, or "Not documented"]

---
```

**For targeted updates:**

- Layer 1: insert/delete table rows; correct model, tools, spawned-by values
- Layer 2: rewrite/add/remove `### agent-name` sections

Update `**Last updated:**` to today's date.

---

## Phase 6: Verify and Commit

### If SURFACE=skills

```bash
grep -c "^### /" docs/skills-map.md
grep -E "(al-dev-test|al-dev-unit-test|al-dev-integration-test)" docs/skills-map.md
```

Commit if any edits were made:

```bash
git -C . add docs/skills-map.md
git -C . commit -m "docs: sync skill map with current plugin state"
```

### If SURFACE=agents

```bash
wc -l docs/agent-map.md
```

Commit if any edits were made:

```bash
git -C . add docs/agent-map.md
git -C . commit -m "docs: sync agent map with current agent roster"
```

Report what changed and what was verified as already correct.

> **Map accuracy only.** Design suggestions (Inline, Move, Connect, etc.) come from
> the design lenses dispatched by `/plugin-health-audit` and land in the health
> dossier. After syncing the map, run `/plugin-health-audit` to find improvements.
