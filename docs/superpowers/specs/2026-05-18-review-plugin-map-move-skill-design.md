# Design: Add Move Candidate Detection to review-plugin-map

**Date:** 2026-05-18  
**Scope:** `review-plugin-map` skill (`al-dev-shared/.claude/skills/review-plugin-map/SKILL.md`)  
**Status:** Approved

---

## Problem

The `review-plugin-map` skill keeps `docs/al-dev-plugin-map.md` accurate but has no mechanism for identifying skills or agents that don't belong in the shared plugin at all. Skills like `al-dev-align` are project-internal tools (they audit `al-dev-shared` itself) but currently live in `profile-al-dev-shared/skills/` alongside skills intended for plugin consumers.

The existing Architectural suggestions section in the map already tracks Connect / Merge / Promote / Extend patterns. There is no `Move` type for "this skill should live in `.claude/skills/` instead."

---

## Goal

Extend `review-plugin-map` with a new **Phase 7: Detect Move Candidates** that scans active skills for signals that they belong in the project-local `.claude/skills/` directory rather than the distributed plugin. Candidates are reported as `Move:` suggestions in the map's Architectural suggestions section. No files are moved — report only.

---

## Detection Signals

A skill scoring **2 or more** of these signals is flagged as a Move candidate:

| Signal | What to check |
|--------|---------------|
| **Internal path references** | Skill body contains paths like `profile-al-dev-shared/`, `.claude/`, or repo-root filenames (e.g. `marketplace.json`) that only resolve inside this repo |
| **Self-audit purpose** | Skill's stated purpose is maintaining or auditing the plugin itself — alignment checks, map reviews, design analysis — not serving AL developers |
| **No spawned agents** | No `al-dev-shared:` agent type appears in the skill body |

Agents are not scanned separately. If a skill flagged for moving is the sole caller of an agent, the suggestion notes the agent as a side-effect consideration.

---

## Output Format

Phase 7 appends to the `### Architectural suggestions` section of `docs/al-dev-plugin-map.md`, following the existing style:

```markdown
**Move: /al-dev-align → .claude/skills/**
Observation: Skill references internal paths (`profile-al-dev-shared/`, repo root) and its purpose is auditing the plugin itself — it provides no value to plugin consumers.
Signals: internal path refs (✓), self-audit purpose (✓), no spawned agents (✓).
Suggestion: Move `profile-al-dev-shared/skills/al-dev-align/` to `.claude/skills/al-dev-align/` and update the plugin map scope line to exclude it.
Trade-off: Skill remains available in this project; removed from the distributed plugin.
```

If no candidates are found, Phase 7 writes a `### Move candidates` subheading with a single line: `None detected.`

---

## Integration with Existing Phases

**Placement:** Phase 7 runs after Phase 6 (Verify and Commit). Phase 6's existing commit covers accuracy fixes. Phase 7 then appends Move suggestions and commits them separately:

```
docs: add Move candidates to plugin map architectural suggestions
```

If Phase 7 finds no candidates, the commit is skipped entirely.

**Scoped invocation guard:** When `$ARGUMENTS` contains a specific skill name (focused accuracy-check mode), Phase 7 is skipped. The skill notes: *"Move candidate scan skipped — run without arguments for full analysis."*

---

## Skill Structure After Change

```
Phase 1  Scan plugin structure         (unchanged)
Phase 2  Extract skill profiles        (unchanged)
Phase 3  Compare against plugin map    (unchanged)
Phase 4  Report discrepancies          (unchanged)
Phase 5  Update the map               (unchanged)
Phase 6  Verify and commit             (unchanged)
Phase 7  Detect Move candidates        ← new
```

---

## Acceptance Criteria

1. Phase 7 section appears at the end of `SKILL.md` with the detection table and output format template
2. Detection checks all three signals; a skill scoring 2+ is flagged
3. Output follows the `**Move: /skill-name → .claude/skills/**` format with Observation / Signals / Suggestion / Trade-off fields
4. Phase 7 commits separately from Phase 6 (or skips if no candidates found)
5. When `$ARGUMENTS` names a skill, Phase 7 is skipped with the stated note
6. `al-dev-align` would be flagged if the skill were run against the current plugin state (manual verification criterion)
