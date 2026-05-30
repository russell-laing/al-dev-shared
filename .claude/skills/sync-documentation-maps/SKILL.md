---
name: sync-documentation-maps
description: >-
  Use when plugin documentation maps are out of sync with the current codebase,
  or to verify accuracy after adding/removing skills or agents. Coordinates
  skill and agent map audits and updates in one unified workflow.
argument-hint: "[optional: --all | --skip-commit]"
---

# Sync Documentation Maps

Unified entry point that coordinates audits and updates of both `docs/al-dev-skills-map.md`
and `docs/al-dev-agent-map.md`. Runs audits in parallel, presents findings, asks user
which to update, applies changes.

---

## Phase 1: Parallel Audits

Dispatch both audits to run in parallel:

```
Spawn: /audit-skills-against-map
Spawn: /audit-agents-against-map
```

Wait for both to complete. Collect audit findings for each map.

---

## Phase 2: Present Findings

Display findings from both audits in a summary table:

```
Skills Map Audit:
  [findings summary from /audit-skills-against-map]

Agent Map Audit:
  [findings summary from /audit-agents-against-map]
```

If both maps are accurate with no discrepancies, report:
**"Both documentation maps are accurate. No updates needed."** and stop.

---

## Phase 3: Ask User What to Update

**If `--all` argument was passed:** Skip to Phase 4 and update both maps.

**Otherwise, ask the user:**

```
Which map would you like to update?
  [1] Skills map only (docs/al-dev-skills-map.md)
  [2] Agent map only (docs/al-dev-agent-map.md)
  [3] Both maps
  [4] Neither (skip updates)
```

Record user's choice.

---

## Phase 4: Conditional Updates

Based on user's choice from Phase 3, dispatch the appropriate update skills:

**If skills map selected:**
```
Spawn: /update-skill-map
Wait for completion
```

**If agent map selected:**
```
Spawn: /update-agent-map
Wait for completion
```

**If both selected:**
```
Spawn: /update-skill-map
Spawn: /update-agent-map
Wait for both to complete
```

**If neither selected:**
Skip to Phase 5.

---

## Phase 5: Finalize

**If `--skip-commit` was passed:** Display changes that would be committed, then stop.

**Otherwise:**
- Refresh the dependency graph (plugin surface):
  ```bash
  python3 scripts/generate-agent-projections.py
  ```
- Present summary of all changes made
- Report: "Documentation maps synchronized successfully."

---

## Arguments

**`--all`** (optional)
- Update both maps without asking user which to update
- Useful for CI workflows or automated syncs

**`--skip-commit`** (optional)
- Show what changes would be made, but don't commit
- Useful for review before applying updates
- Implies dry-run mode

---

## Workflow Examples

### Example 1: Full sync (interactive)
```
User: /sync-documentation-maps
→ Audits both maps in parallel
→ Shows findings
→ Asks user which to update
→ Updates selected maps
→ Refreshes dependency graph
→ Commits
```

### Example 2: Update both without asking
```
User: /sync-documentation-maps --all
→ Audits both maps in parallel
→ Updates both maps automatically
→ Refreshes dependency graph
→ Commits
```

### Example 3: Dry-run (no commit)
```
User: /sync-documentation-maps --skip-commit
→ Audits both maps
→ Shows findings
→ Asks which to update
→ Shows what changes would be made
→ Stops without committing
```

---

## When to Use

**Primary entry point for:**
- Verifying maps after adding/removing skills or agents
- Regular map synchronization
- Pre-review checks before `/analyze-skill-design` or `/analyze-agent-design`

**For audit-only (no updates):**
- Use `/audit-skills-against-map` and `/audit-agents-against-map` directly

**For individual map updates:**
- Use `/update-skill-map` or `/update-agent-map` directly if you've already run audits

---

## Next Steps

After maps are synchronized, typically:
1. Run `/analyze-skill-design` to suggest architectural improvements
2. Run `/analyze-agent-design` to suggest agent quality improvements
3. Run `/plan-map-changes` to implement accepted suggestions
