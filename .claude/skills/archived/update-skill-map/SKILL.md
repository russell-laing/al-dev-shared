---
name: update-skill-map
description: >-
  Use after /audit-skills-against-map to apply discrepancies to docs/skills-map.md.
  Writes/updates the skills map file, detects move candidates (project-local vs distributed),
  appends findings to Observations section, and commits changes.
---

> **ARCHIVED 2026-05-31** — Use `/review-skill-map` instead.

---

# Update Skill Map

Apply audit findings from `/audit-skills-against-map` to update `docs/skills-map.md`.
Writes changes, detects architectural candidates, commits to git.

Usage: `/update-skill-map [skill-name]`.

---

## Phase 1: Audit (Optional Re-scan)

If audit findings are not provided, run the full audit from Phase 1-4 of `/audit-skills-against-map`:
- Scan plugin structure
- Extract skill profiles
- Compare against current map
- Report discrepancies

Otherwise, use findings provided by previous audit run.

---

## Phase 2: Update Layer 1

Make targeted edits to Layer 1 (Lifecycle Overview diagram) in `docs/skills-map.md` to fix each discrepancy:

**For each issue found in audit:**
- To add a skill: add a node and edge in the flowchart, add a `style` directive
- To remove a skill: remove its node declaration, all edges that reference its ID, and its `style` directive — leave no orphaned `style` lines
- To fix a handoff label: update the `-->|label|` on the relevant edge

**Mermaid style guard:** After any edit, scan every `style X fill:...` line in the diagram. Confirm that `X` matches an ID used in at least one node declaration or edge. Delete any `style` line where `X` has no corresponding node — Mermaid will render it as an orphaned node.

---

## Phase 3: Update Layer 2

For each discrepancy in Layer 2 (per-skill drill-downs):
- To update a drill-down: rewrite the affected `flowchart LR` block — keep all `style` directives consistent with the node IDs used in edges
- To add a missing skill: insert a new `### /skill-name` section with a `flowchart LR` block following the existing style and notation conventions
- To remove a stale skill: delete its `### /skill-name` section entirely

---

## Phase 4: Update Metadata

Set `**Last updated:**` in the document header to today's date (YYYY-MM-DD format).

---

## Phase 5: Detect Move Candidates

Scan every active skill for signals that it belongs in the project-local `.claude/skills/`
directory rather than the distributed plugin:

### Detection signals

Score each active skill against these three signals:

| Signal | What to check |
|--------|---------------|
| **Internal path references** | Skill body contains paths like `profile-al-dev-shared/`, `.claude/`, or repo-root filenames (e.g. `marketplace.json`) that only resolve inside this repo |
| **Self-audit purpose** | Skill's stated purpose is maintaining or auditing the plugin itself — alignment checks, map reviews, design analysis — not serving AL developers |
| **No spawned agents** | No `al-dev-shared:` agent type appears in the skill body |

A skill scoring **2 or more signals** is a Move candidate.

### Output

Ensure `docs/skills-map.md` has a `## Observations` section. If not, create it.

Within `## Observations`, ensure an `### Architectural suggestions` subsection exists. Create if missing.

For each Move candidate, append inside `### Architectural suggestions`:

```markdown
**Move: /skill-name → .claude/skills/**
Observation: [Why this skill has no value to plugin consumers.]
Signals: internal path refs (✓/✗), self-audit purpose (✓/✗), no spawned agents (✓/✗).
Suggestion: Move `profile-al-dev-shared/skills/<skill-name>/` to `.claude/skills/<skill-name>/` and update the plugin map scope line to exclude it.
Trade-off: Skill remains available in this project; removed from the distributed plugin.
```

If no candidates are found, ensure this subsection exists:

```markdown
### Architectural suggestions

None detected.
```

---

## Phase 6: Verify and Commit

Run a quick sanity check:

```bash
# Expect one section per active lifecycle skill
grep -c "^### /" docs/skills-map.md

# Expect no archived skill names to appear
grep -E "(al-dev-test|al-dev-unit-test|al-dev-integration-test|al-dev-scenario-test|al-dev-edge-case-test|al-dev-test-coverage)" docs/skills-map.md
```

If checks pass, commit:

```bash
git -C . add docs/skills-map.md
git -C . commit -m "docs: sync skills map with current plugin state"
```

Report what changed and what was verified as already correct.

---

## Notes

- This skill only updates the **skills map** (docs/skills-map.md)
- For agent map updates, use `/update-agent-map`
- For coordinated audit+update of both maps, use `/sync-documentation-maps`
