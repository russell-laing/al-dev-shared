---
name: audit-quality
description: >-
  Unified audit of profile-al-dev-shared agents or skills for internal quality:
  prompt clarity, structural conventions, description drift, bloat, and name fit.
  Reads each agent .md or SKILL.md directly and writes findings to
  docs/al-dev-agent-quality.md or docs/al-dev-skill-quality.md based on --type.
  Run after /analyze-agent-design or /analyze-skill-design for a complete picture.
  Triggers on: "audit quality", "check quality", "are agents/skills well written",
  "quality report", "check for quality drift", "bloat".
argument-hint: "--type agent|skill [object-name]"
---

# Skill: /audit-quality

Unified per-file quality audit of al-dev plugin agents or skills. Dispatches five
parallel lens agents, aggregates their findings, and writes a structured report to
`docs/al-dev-agent-quality.md` (for agents) or `docs/al-dev-skill-quality.md`
(for skills).

Use `--type agent` to audit agents or `--type skill` to audit skills.

If an object name is passed (e.g., `/audit-quality --type agent al-dev-developer`),
only that agent or skill is audited and only its section is updated in the report.

---

## Parsing Arguments

Parse the input to extract `--type` and optional object name:

```python
# Reference only — this parsing logic is embedded in the skill's runtime.
# Do not execute this block directly.
import sys
args = sys.argv[1:]  # Get arguments after command name
audit_type = None
object_name = None

if '--type' in args:
    idx = args.index('--type')
    if idx + 1 < len(args):
        audit_type = args[idx + 1]
        # Object name may follow --type <type>
        if idx + 2 < len(args) and not args[idx + 2].startswith('-'):
            object_name = args[idx + 2]

if not audit_type or audit_type not in ('agent', 'skill'):
    print("Error: --type must be 'agent' or 'skill'")
    sys.exit(1)
```

After parsing:
- `audit_type` = `'agent'` or `'skill'`
- `object_name` = parsed argument, or `None` for full run

---

## Phase 1 — Discover Files

**For agents:**
```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" | sort
```
Derive agent names from filenames (strip directory path and `.md` extension).

**For skills:**
```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills -name "SKILL.md" | sort
```
Derive skill names from parent directory name (e.g., `.../skills/al-dev-develop/SKILL.md` → `al-dev-develop`).

**Scoped runs:**
If an object name was passed, filter `file_list` to the single matching path.
- **For agents:** Normalize by stripping trailing `.md`; always use `al-dev-<name>` for section headings.
- **For skills:** Normalize by stripping leading `/` if present; always use `/<name>` for section headings.

Build a list of absolute paths (`file_list`).

---

## Phase 2 — Parallel Lens Dispatch

Dispatch all five lens agents in a **single response** (five parallel Agent tool calls).

**For agents, pass this prompt (substitute actual paths):**
```
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
/absolute/path/to/agent1.md
/absolute/path/to/agent2.md
[one path per line — paste all paths from Phase 1 here]
```

Agents to dispatch simultaneously (spawn each in parallel):
- `quality-agent-lens-clarity`
- `quality-agent-lens-structure`
- `quality-agent-lens-description`
- `quality-agent-lens-bloat`
- `quality-agent-lens-name-fit`

**For skills, pass this prompt (substitute actual paths):**
```
Analyze the following SKILL.md files. Apply your lens to every file and return a findings block.

File list:
/absolute/path/to/skills/skill-name/SKILL.md
/absolute/path/to/skills/other-skill/SKILL.md
[one path per line — paste all paths from Phase 1 here]
```

Agents to dispatch simultaneously (spawn each in parallel):
- `quality-skill-lens-clarity`
- `quality-skill-lens-structure`
- `quality-skill-lens-description`
- `quality-skill-lens-bloat`
- `quality-skill-lens-name-fit`

Each agent returns one block headed `### [Lens Name] Findings`.

---

## Phase 3 — Aggregate Findings

Collect all five findings blocks. Each block contains lines in this format:

**For agents:**
`- **[agent-name]** | [Severity] | [observation] | [fix]`

**For skills:**
`- **[skill-name]** | [Severity] | [observation] | [fix]`

Reorganize by object name for the report:

1. Parse every findings line across all five blocks.
2. Group lines by object name.
3. For each object with at least one finding:
   - Sort findings by severity: High first, then Medium, then Low.
   - Format each finding with its lens name as the heading.
4. Sort objects: those with High findings first, then Medium, then Low, then clean.
5. Objects with no findings across all five lenses:
   - **For agents:** `### al-dev-<name> — No findings.`
   - **For skills:** `### /<name> — No findings.`

---

## Phase 4 — Write the Report

**Report template** (shared structure for agent and skill full runs):

```markdown
# AL Dev {Type} Quality Audit

**Last run:** {today's date}
**{Types} audited:** {N}

## Summary

| Severity | Count |
|----------|-------|
| High     | {N}   |
| Medium   | {N}   |
| Low      | {N}   |

## Findings

### {prefix}{name}

**[High] Prompt Clarity**
Observation: {offending text or pattern}
Fix: {one-line suggestion}

**[Medium] Bloat**
Observation: {what is bloated}
Fix: {one-line suggestion}

---

### {prefix}{other} — No findings.

---
```

**Substitution variables:**

| Variable | Agents | Skills |
|----------|--------|--------|
| `{Type}` | `Agent` | `Skill` |
| `{Types}` | `Agents` | `Skills` |
| `{prefix}` | `al-dev-` | `/` |
| Output file | `docs/al-dev-agent-quality.md` | `docs/al-dev-skill-quality.md` |

### Full run (no object name passed)

Fully replace the output file using the report template with the appropriate
substitution variables. Ordering: objects with findings first (highest-severity
finding descending), then clean objects. Each object section ends with `---`.

### Scoped run (object name passed)

1. Determine report file per the substitution table above.
2. Read the report file if it exists.
3. Locate the section for the named object:
   - **For agents:** from `### al-dev-<arg>` to just before the next `### al-dev-` heading or end of `## Findings`
   - **For skills:** from `### /<arg>` to just before the next `### /` heading or end of `## Findings`
4. Build a replacement section with new findings (or the no-findings variant).
5. Replace in-place using the Edit tool, with the old section as `old_string`.
6. If the section doesn't exist yet: append at the end of `## Findings`.
7. Recalculate Summary counts by scanning all `**[High]`, `**[Medium]`, `**[Low]`
   occurrences in the updated file, then rewrite the Summary table.
8. If the report file doesn't exist: write a new full report containing only
   the named object's section.

---

## Phase 5 — Commit

**For agents:**
```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-agent-quality.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update agent quality audit"
```

For scoped runs:
```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update agent quality audit — al-dev-<agent-name>"
```

**For skills:**
```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-skill-quality.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update skill quality audit"
```

For scoped runs:
```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update skill quality audit — /<skill-name>"
```

---

## Phase 6 — Present to User

**For agents, print one line per audited agent:**
- With findings: `al-dev-<agent-name>: N High, N Medium, N Low`
- Without findings: `al-dev-<agent-name>: clean`

**For skills, print one line per audited skill:**
- With findings: `/<skill-name>: N High, N Medium, N Low`
- Without findings: `/<skill-name>: clean`

Ask: "Would you like to fix any of these now?"

### If the user says yes — Fix Application Protocol

For each file to be modified:

1. **Read the file** and record its original line count (`original_lines`).
2. **Calculate budget:** `floor(original_lines × 0.05)` — max net lines
   removable from this file in this pass.
   If the result is `0`, skip all non-atomic edits for that file this pass.
3. **Apply only atomic fixes** per finding, in priority order:
   High → Medium → Low. An atomic fix is one that fully resolves a finding
   without rewriting unrelated sections.
4. **If the next full fix would exceed `budget`:**
   skip that finding for this pass, append to the report section for that file:
   `"Skipped — full fix exceeds remaining budget; queue for next audit pass."`
5. **Do not partially rewrite structural blocks** such as headings, lists,
   frontmatter, or phase instructions. If a finding touches a structural block
   and cannot be resolved atomically within the remaining budget, skip it.
6. **Verify after edit:** `wc -l <file>` — confirm net reduction ≤ budget.
   Also confirm the edited file still contains the required structural sections
   for its type before proceeding to the next file.
7. **Leave commits to the surrounding workflow.** The protocol only governs
   safe edit application; it does not introduce a new commit step.
