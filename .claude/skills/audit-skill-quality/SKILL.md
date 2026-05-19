---
name: audit-skill-quality
description: >-
  Audit profile-al-dev-shared skills for internal quality: prompt clarity,
  structural conventions, description drift, bloat, and name fit. Reads each
  SKILL.md directly and writes findings to docs/al-dev-skill-quality.md.
  Run after /analyze-skill-design for a complete picture. Triggers on:
  "audit skill quality", "check skill quality", "are skills well written",
  "skill quality report", "check for skill drift", "skill bloat".
argument-hint: "[skill-name]"
---

# Skill: /audit-skill-quality

Per-file quality audit of al-dev plugin skills. Dispatches five parallel lens
agents, aggregates their findings, and writes a structured report to
`docs/al-dev-skill-quality.md`.

If an argument is passed (e.g., `/audit-skill-quality al-dev-develop`), only
that skill is audited and only its section is updated in the report.

---

## Phase 1 — Discover Skill Files

```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills -name "SKILL.md" | sort
```

Build a list of absolute paths (`file_list`). Derive skill names from the parent
directory name (e.g., `.../skills/al-dev-develop/SKILL.md` → `al-dev-develop`).

If an argument was passed, filter `file_list` to the single matching path.
Normalize: strip `/` prefix if present when matching input; always use `/<name>`
for section headings in the report.

---

## Phase 2 — Parallel Lens Dispatch

Dispatch all five lens agents in a **single response** (five parallel Agent tool calls).

Pass this prompt to each agent, substituting the actual absolute paths:

```
Analyze the following SKILL.md files. Apply your lens to every file and return a findings block.

File list:
/absolute/path/to/skills/skill-name/SKILL.md
/absolute/path/to/skills/other-skill/SKILL.md
[one path per line — paste all paths from Phase 1 here]
```

Agents to dispatch simultaneously (use `subagent_type` for each):
- `quality-skill-lens-clarity`
- `quality-skill-lens-structure`
- `quality-skill-lens-description`
- `quality-skill-lens-bloat`
- `quality-skill-lens-name-fit`

Each agent returns one block headed `### [Lens Name] Findings`.

---

## Phase 3 — Aggregate Findings

Collect all five findings blocks. Each block contains lines in this format:
`- **[skill-name]** | [Severity] | [observation] | [fix]`

Reorganize by skill name for the report:

1. Parse every findings line across all five blocks.
2. Group lines by skill name.
3. For each skill with at least one finding:
   - Sort findings by severity: High first, then Medium, then Low.
   - Format each finding with its lens name as the heading.
4. Sort skills: those with High findings first, then Medium, then Low, then clean.
5. Skills with no findings across all five lenses → `### /<name> — No findings.`

---

## Phase 4 — Write the Report

### Full run (no argument passed)

Fully replace `docs/al-dev-skill-quality.md`. Substitute actual values for all
angle-bracket placeholders before writing:

```markdown
# AL Dev Skill Quality Audit

**Last run:** <today's date>
**Skills audited:** <N>

## Summary

| Severity | Count |
|----------|-------|
| High     | <N>   |
| Medium   | <N>   |
| Low      | <N>   |

## Findings

### /<skill-name>

**[High] Prompt Clarity**
Observation: <offending text or pattern>
Fix: <one-line suggestion>

**[Medium] Bloat**
Observation: <what is bloated>
Fix: <one-line suggestion>

---

### /<other-skill> — No findings.

---
```

Ordering: skills with findings first (highest-severity finding descending), then
clean skills. Each skill section ends with `---`.

### Scoped run (argument passed)

1. Read `docs/al-dev-skill-quality.md` if it exists.
2. Locate the section for the named skill — from `### /<arg>` to just before
   the next `### /` heading or end of `## Findings`.
3. Build a replacement section with new findings (or `### /<arg> — No findings.`).
4. Replace in-place using the Edit tool, with the old section as `old_string`.
5. If the section doesn't exist yet: append at the end of `## Findings`.
6. Recalculate Summary counts by scanning all `**[High]`, `**[Medium]`, `**[Low]`
   occurrences in the updated file, then rewrite the Summary table.
7. If `docs/al-dev-skill-quality.md` doesn't exist: write a new full report
   containing only the named skill's section.

---

## Phase 5 — Commit

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-skill-quality.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update skill quality audit"
```

For scoped runs, name the target in the commit message:

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update skill quality audit — /<skill-name>"
```

---

## Phase 6 — Present to User

Print one line per audited skill:
- With findings: `/<skill-name>: N High, N Medium, N Low`
- Without findings: `/<skill-name>: clean`

Ask: "Would you like to fix any of these now?"
