---
name: audit-skills-against-map
description: >-
  Use when verifying that profile-al-dev-shared skills are accurately documented
  in the map without modifying files. Scans plugin structure, extracts profiles,
  compares against current map, reports discrepancies. For audit-only workflows
  (CI verification, dry-run before update).
---

> **ARCHIVED 2026-05-31** — Use `/review-skill-map --no-update` instead.

---

# Audit Skills Against Map

Audit `profile-al-dev-shared` and verify `docs/skills-map.md` accurately
reflects the current active skills, agents, phases, file handoffs, and generated
projection surfaces. **No file modifications** — findings only.

Usage: `/audit-skills-against-map [skill-name]`.

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

## Phase 3: Compare Against Skills Map

Read `docs/skills-map.md`.

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

Summarise findings:

```
Skills map audit findings:
Layer 1:
  - [issue or "✅ accurate"]
Layer 2 per-skill:
  - /skill-a: [issue or "✅ accurate"]
  - /skill-b: [issue or "✅ accurate"]
  ...
Missing from map: [skills not in map]
Stale in map:    [skills in map but now archived]
```

If everything is accurate, report: **"Skills map is accurate. No discrepancies found."** and stop.

---

## Phase 5: Suggest Fixes

For each discrepancy found, suggest specific fixes:

**For Layer 1 fixes:**
- To add a skill: add a node and edge in the flowchart, add a `style` directive
- To remove a skill: remove its node declaration, all edges that reference its ID, and its `style` directive — leave no orphaned `style` lines
- To fix a handoff label: update the `-->|label|` on the relevant edge

**For Layer 2 fixes:**
- To update a drill-down: rewrite the affected `flowchart LR` block — keep all `style` directives consistent with the node IDs used in edges
- To add a missing skill: insert a new `### /skill-name` section with a `flowchart LR` block following the existing style and notation conventions
- To remove a stale skill: delete its `### /skill-name` section entirely

**Present all suggested fixes to the user without modifying files.** The user may:
- Run `/update-skill-map` to apply all fixes
- Run `/update-skill-map <skill-name>` to update a specific skill
- Run `/audit-skills-against-map` again after manual updates

---

## Next Steps

To apply changes, user should run `/update-skill-map`.
