---
name: review-documentation-map
description: >-
  Review a plugin documentation map for accuracy and optionally update it.
  Accepts --surface [skills|agents] to select which map to review. Pass
  --no-update to audit only without modifying files. Replaces /review-skill-map
  (use --surface skills) and /review-agent-map (use --surface agents).
  Triggers on: "review documentation map", "update skill map", "update agent
  map", "review skill map", "review agent map", "sync maps", "is the map
  accurate", "check the maps".
argument-hint: "--surface skills|agents [--no-update]"
workflow:
  stage: map-sync
  invoked-by: both
  repeatable: true
  inputs:
    - docs/al-dev-skills-map.md
    - docs/al-dev-agent-map.md
    - profile-al-dev-shared/skills/
    - profile-al-dev-shared/agents/
  outputs:
    - docs/al-dev-skills-map.md
    - docs/al-dev-agent-map.md
  next: [plugin-health-audit]
---

# Review Documentation Map

Audit the plugin surface and update the corresponding documentation map so it
accurately reflects the current state of the codebase.

---

## Phase 0: Parse Arguments

Read `$ARGUMENTS`:

- If `--no-update` is present, set `NO_UPDATE=true`.
- If `--surface skills` is present, set `SURFACE=skills`.
- If `--surface agents` is present, set `SURFACE=agents`.
- If neither `--surface skills` nor `--surface agents` is present, ask:

  > Which surface do you want to review?
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

## Phase 2: Extract Profiles and Build Caller Sets

### Phase 2a: Extract profiles

#### If SURFACE=skills

For each active skill (read `profile-al-dev-shared/skills/<name>/SKILL.md`):

Extract:

1. **Phases** — numbered phases described in the skill body (Phase 1, Phase 2, etc.)
2. **Agents spawned** — any `al-dev-shared:al-dev-*` agent type mentioned with a spawn directive
3. **Parallel pattern** — is the agent spawned ×1, ×2-3, or more?
4. **Outputs** — `.dev/` files the skill writes

**What to look for when parsing SKILL.md:**

- Phase headers (`## Phase N`, `### Step N`, `## Phase N:`)
- Agent spawn directives (`Spawn`, `spawn an`, `al-dev-developer`, `al-dev-solution-architect`, etc.)
- Parallel markers (`in parallel`, `at once`, `×2`, `×2-3`, `parallel`)
- Output file writes (`write to .dev/`, `save to .dev/`, `.dev/*-<skill>-*.md`)

Record in a working table:

| Skill | Phases | Agents spawned | Pattern | Outputs |
|-------|--------|----------------|---------|---------|

#### If SURFACE=agents

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

### Phase 2b: Build caller sets

#### If SURFACE=agents

For each active agent, use a two-pass grep to find all skills that spawn it:

```bash
# Pass 1: qualified type name
grep -rl "al-dev-shared:<filename-without-.md>" \
  profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null

# Pass 2: short name prose references
grep -rl "<filename-without-.md>" \
  profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null
```

**Union/dedup ordering:** Union all grep results first (concatenate the file
lists from both passes), **then** `sort -u` the combined set once. Do not
`sort -u` each pass independently before unioning — dedup the merged set in a
single pass so a file matched by both passes is counted once.

Record:

- **Spawned by:** list of skill names (extract directory name from matching paths)
- **Spawn count:** single-use (1 skill) or shared (2+ skills)

#### If SURFACE=skills

No caller-set phase needed for skills — agents spawned are extracted in Phase 2a.

---

## Phase 3: Profiles and Caller Sets Ready

Caller-set cross-referencing now lives in Phase 2b. Confirm the working table(s)
from Phase 2 are complete before comparing against the map: every active item has
a profile row, and (for agents) a deduped caller set from Phase 2b.

---

## Phase 4: Compare Against Map File

If `{MAP_FILE}` does not exist, skip to Phase 5 (write from scratch).

Read the file.

### Phase 4a: Compare against map

Check both layers and record each mismatch as a discrepancy.

#### If SURFACE=skills

**Layer 1 (Lifecycle Overview diagram):**

- All active skills that are part of the lifecycle are represented as nodes
- No archived skill appears as a node
- Node IDs in `style` directives match node IDs in edges (orphaned `style` directives create ghost nodes)
- File handoff labels on edges match what the skills actually produce
- The three entry paths are correct (ticket→support, investigate→decision, direct fix)

**Layer 2 (Per-skill drill-downs):**

For each active skill, check the matching drill-down diagram:

- Phases match the skill's actual phase count
- Agents match what the skill spawns (by name and pattern)
- Outputs match what the skill actually writes
- No skill is missing from Layer 2

#### If SURFACE=agents

**Layer 1 (Agent Catalog table):**

- All active agents appear as table rows
- No archived agent appears as a row
- Model and tools match the actual frontmatter values
- "Spawned by" matches the deduped caller set from Phase 2b

**Layer 2 (Per-agent profiles):**

For each active agent, verify the `### <filename-without-.md>` section:

- Model and tools list match the frontmatter
- Spawned-by list matches the Phase 2b caller set
- Inputs/Outputs match Phase 2a findings (or "Not documented" if absent)

### Phase 4b: Style-guard

Only applies when `{MAP_FILE}` contains Mermaid diagrams (the skills surface).

Operationalize the Mermaid check on each diagram block:

- **Identify edge lines.** Each Mermaid edge line must match:

  ```bash
  grep -nE '^\s*[A-Za-z0-9_]+ ?-(.|-)?->' "{MAP_FILE}"
  ```

  This matches `A --> B`, `A -.-> B`, `A ---> B`, and labeled edges
  `A -->|label| B`. (HTML comments and prose containing `-->` do not start
  with a node ID, so they are not matched.)
- **Check node declarations.** Derive the declared-node set with
  `grep -oE '^\s*[A-Za-z0-9_]+\[' "{MAP_FILE}"` (node statements), plus the
  left-hand node ID of every edge line from the edge grep above. Any node ID
  appearing on the right of an edge but in neither set is a ghost node. Flag
  each ghost node as a discrepancy.
- **Check `style` directives.** Confirm every `style X fill:...` directive's `X`
  matches a node ID that appears in a node declaration or an edge. Orphaned
  `style` lines are discrepancies (see the Phase 5 style guard for the fix).

Record any ghost nodes or orphaned `style` lines as discrepancies for Phase 5.

### Phase 4c: Report and Audit-Only Exit

Before editing, summarise findings:

#### If SURFACE=skills

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

#### If SURFACE=agents

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

If `NO_UPDATE=true`, suggest specific fixes without modifying files, then stop:

**For skills surface:**

- Layer 1: add/remove nodes, edges, and `style` directives; fix handoff labels
- Layer 2: rewrite/add/remove `### /skill-name` sections

**For agents surface:**

- Layer 1 (table): insert/delete rows; correct model, tools, spawned-by columns
- Layer 2: rewrite/add/remove `### agent-name` sections

Present all suggested fixes. The user may re-run without `--no-update` to apply.
Do not proceed to Phase 5.

---

## Phase 5: Update the Map

If `{MAP_FILE}` does not exist, create it. Otherwise make targeted edits to fix
each discrepancy found in Phases 4a and 4b. Use the Edit tool for targeted
changes (not full rewrites) whenever the file already exists.

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
grep -c "^### /" docs/al-dev-skills-map.md
grep -E "(al-dev-test|al-dev-unit-test|al-dev-integration-test)" docs/al-dev-skills-map.md
```

Commit if any edits were made:

```bash
git -C . add docs/al-dev-skills-map.md
git -C . commit -m "docs: sync skill map with current plugin state"
```

### If SURFACE=agents

```bash
wc -l docs/al-dev-agent-map.md
```

Commit if any edits were made:

```bash
git -C . add docs/al-dev-agent-map.md
git -C . commit -m "docs: sync agent map with current agent roster"
```

Report what changed and what was verified as already correct.

> **Map accuracy only.** Design suggestions (Inline, Move, Connect, etc.) come from
> the design lenses dispatched by `/plugin-health-audit` and land in the health
> dossier. After syncing the map, run `/plugin-health-audit` to find improvements.
