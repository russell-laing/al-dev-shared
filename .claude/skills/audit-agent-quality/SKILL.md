---
name: audit-agent-quality
description: >-
  Audit profile-al-dev-shared agents for internal quality: prompt clarity,
  structural conventions, description drift, bloat, and name fit. Reads each
  agent .md directly and writes findings to docs/al-dev-agent-quality.md.
  Run after /analyze-agent-design for a complete picture. Triggers on:
  "audit agent quality", "check agent quality", "are agents well written",
  "agent quality report", "check for agent drift", "agent bloat".
argument-hint: "[agent-name]"
---

# Skill: /audit-agent-quality

Per-file quality audit of al-dev plugin agents. Dispatches five parallel lens
agents, aggregates their findings, and writes a structured report to
`docs/al-dev-agent-quality.md`.

If an argument is passed (e.g., `/audit-agent-quality al-dev-developer`), only
that agent is audited and only its section is updated in the report.

---

## Phase 1 — Discover Agent Files

```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" | sort
```

Build a list of absolute paths (`file_list`). Derive agent names from filenames
(strip directory path and `.md` extension).

If an argument was passed, filter `file_list` to the single matching path.
Normalize: strip `al-dev-` prefix if present when matching input; always use
`al-dev-<name>` for section headings in the report.

---

## Phase 2 — Parallel Lens Dispatch

Dispatch all five lens agents in a **single response** (five parallel Agent tool calls).

Pass this prompt to each agent, substituting the actual absolute paths:

```
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
/absolute/path/to/agent1.md
/absolute/path/to/agent2.md
[one path per line — paste all paths from Phase 1 here]
```

Agents to dispatch simultaneously (use `subagent_type` for each):
- `quality-lens-clarity`
- `quality-lens-structure`
- `quality-lens-description`
- `quality-lens-bloat`
- `quality-lens-name-fit`

Each agent returns one block headed `### [Lens Name] Findings`.

---

## Phase 3 — Aggregate Findings

Collect all five findings blocks. Each block contains lines in this format:
`- **[agent-name]** | [Severity] | [observation] | [fix]`

Reorganize by agent name for the report:

1. Parse every findings line across all five blocks.
2. Group lines by agent name.
3. For each agent with at least one finding:
   - Sort findings by severity: High first, then Medium, then Low.
   - Format each finding with its lens name as the heading.
4. Sort agents: those with High findings first, then Medium, then Low, then clean.
5. Agents with no findings across all five lenses → `### al-dev-<name> — No findings.`

---

## Phase 4 — Write the Report

### Full run (no argument passed)

Fully replace `docs/al-dev-agent-quality.md`. Substitute actual values for all
angle-bracket placeholders before writing:

```markdown
# AL Dev Agent Quality Audit

**Last run:** <today's date>
**Agents audited:** <N>

## Summary

| Severity | Count |
|----------|-------|
| High     | <N>   |
| Medium   | <N>   |
| Low      | <N>   |

## Findings

### al-dev-<agent-name>

**[High] Prompt Clarity**
Observation: <offending text or pattern>
Fix: <one-line suggestion>

**[Medium] Bloat**
Observation: <what is bloated>
Fix: <one-line suggestion>

---

### al-dev-<other-agent> — No findings.

---
```

Ordering: agents with findings first (highest-severity finding descending), then
clean agents. Each agent section ends with `---`.

### Scoped run (argument passed)

1. Read `docs/al-dev-agent-quality.md` if it exists.
2. Locate the section for the named agent — from `### al-dev-<arg>` to just
   before the next `### al-dev-` heading or end of `## Findings`.
3. Build a replacement section with new findings (or `### al-dev-<arg> — No findings.`).
4. Replace in-place using the Edit tool, with the old section as `old_string`.
5. If the section doesn't exist yet: append at the end of `## Findings`.
6. Recalculate Summary counts by scanning all `**[High]`, `**[Medium]`, `**[Low]`
   occurrences in the updated file, then rewrite the Summary table.
7. If `docs/al-dev-agent-quality.md` doesn't exist: write a new full report
   containing only the named agent's section.

---

## Phase 5 — Commit

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-agent-quality.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update agent quality audit"
```

For scoped runs, name the target in the commit message:

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update agent quality audit — al-dev-<agent-name>"
```

---

## Phase 6 — Present to User

Print one line per audited agent:
- With findings: `al-dev-<agent-name>: N High, N Medium, N Low`
- Without findings: `al-dev-<agent-name>: clean`

Ask: "Would you like to fix any of these now?"
