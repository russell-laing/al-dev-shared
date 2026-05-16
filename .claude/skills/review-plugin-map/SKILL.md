---
name: review-plugin-map
description: >-
  Review profile-al-dev-shared for accuracy and update docs/al-dev-plugin-map.md.
  Use whenever skills or agents are added, removed, or restructured in the plugin,
  or when you want to verify the map reflects the current state of the codebase.
  Triggers on: "review plugin map", "update plugin map", "sync plugin map",
  "is the plugin map accurate", "update the map", "check the map".
argument-hint: "[optional: skill name to focus on]"
---

# Review Plugin Map

Audit `profile-al-dev-shared` and update `docs/al-dev-plugin-map.md` so it
accurately reflects the current active skills, agents, phases, and file handoffs.

---

## Phase 1: Scan Plugin Structure

Run these three commands and record the results:

```bash
# Active skills (directories in skills/)
ls profile-al-dev-shared/skills/

# Active agents (files in agents/)
ls profile-al-dev-shared/agents/

# Archived items (excluded from the map)
ls profile-al-dev-shared/archived/skills/ 2>/dev/null
ls profile-al-dev-shared/archived/agents/ 2>/dev/null
```

Build two lists:
- **Active skills** — directories in `skills/` minus anything in `archived/skills/`
- **Active agents** — `.md` files in `agents/` minus anything in `archived/agents/`

---

## Phase 2: Extract Skill Profiles

For each active skill (read `profile-al-dev-shared/skills/<name>/SKILL.md`):

Extract:
1. **Phases** — numbered phases described in the skill body (Phase 1, Phase 2, etc.)
2. **Agents spawned** — any `al-dev-shared:al-dev-*` agent type mentioned with a spawn directive
3. **Parallel pattern** — is the agent spawned ×1, ×2-3, or more?
4. **Outputs** — `.dev/` files the skill writes (e.g. `explore-findings.md`, `solution-plan.md`)

Record this in a working table:

| Skill | Phases | Agents spawned | Pattern | Outputs |
|-------|--------|----------------|---------|---------|

**What to look for when parsing SKILL.md:**
- Phase headers (`## Phase N`, `### Step N`, `## Phase N:`)
- Agent spawn directives (`Spawn`, `spawn an`, `al-dev-developer`, `al-dev-solution-architect`, etc.)
- Parallel markers (`in parallel`, `at once`, `×2`, `×2-3`, `parallel`)
- Output file writes (`write to .dev/`, `save to .dev/`, `.dev/*-<skill>-*.md`)

If `$ARGUMENTS` is a skill name, focus only on that skill and skip the rest.

---

## Phase 3: Compare Against Plugin Map

Read `docs/al-dev-plugin-map.md`.

Check each layer:

### Layer 1 (Lifecycle Overview diagram)

Verify:
- All active skills that are part of the lifecycle are represented as nodes
- No archived skill appears as a node
- Node IDs in `style` directives match node IDs in edges (orphaned `style` directives create ghost nodes — check every `style X` against the declared node IDs)
- File handoff labels on edges match what the skills actually produce
- The three entry paths are correct (ticket→support, investigate→decision, direct fix)

### Layer 2 (Per-skill drill-downs)

For each active skill, check the matching drill-down diagram:
- Phases match the skill's actual phase count
- Agents match what the skill spawns (by name and pattern)
- Outputs match what the skill actually writes
- No skill is missing from Layer 2

---

## Phase 4: Report Discrepancies

Before editing, summarise what you found:

```
Plugin map review findings:
Layer 1:
  - [issue or "✅ accurate"]
Layer 2 per-skill:
  - /al-dev-ticket: [issue or "✅ accurate"]
  - /al-dev-support: [issue or "✅ accurate"]
  ...
Missing from map: [skills not in map]
Stale in map:    [skills in map but now archived]
```

If everything is accurate, say so and stop.

---

## Phase 5: Update the Map

Make targeted edits to `docs/al-dev-plugin-map.md` to fix each discrepancy.

**For Layer 1 fixes:**
- To add a skill: add a node and edge in the flowchart, add a `style` directive
- To remove a skill: remove its node declaration, all edges that reference its ID, and its `style` directive — leave no orphaned `style` lines
- To fix a handoff label: update the `-->|label|` on the relevant edge

**For Layer 2 fixes:**
- To update a drill-down: rewrite the affected `flowchart LR` block — keep all `style` directives consistent with the node IDs used in edges
- To add a missing skill: insert a new `### /skill-name` section with a `flowchart LR` block following the existing style and notation conventions
- To remove a stale skill: delete its `### /skill-name` section entirely

**Mermaid style guard:** After any edit, scan every `style X fill:...` line in the modified diagram. Confirm that `X` matches an ID used in at least one node declaration or edge. Delete any `style` line where `X` has no corresponding node — Mermaid will render it as an orphaned node.

Update `**Last updated:**` in the document header to today's date.

---

## Phase 6: Verify and Commit

Run a quick sanity check:

```bash
# Expect one section per active lifecycle skill
grep -c "^### /" docs/al-dev-plugin-map.md

# Expect no archived skill names to appear
grep -E "(al-dev-test|al-dev-unit-test|al-dev-integration-test|al-dev-scenario-test|al-dev-edge-case-test|al-dev-test-coverage)" docs/al-dev-plugin-map.md
```

If checks pass, commit:

```bash
git -C . add docs/al-dev-plugin-map.md
git -C . commit -m "docs: sync plugin map with current plugin state"
```

Report what changed and what was verified as already correct.
