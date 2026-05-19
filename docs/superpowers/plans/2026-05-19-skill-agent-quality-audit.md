# Skill and Agent Quality Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create two project-local skills — `/audit-skill-quality` and `/audit-agent-quality` — that read plugin source files directly and produce structured per-file quality reports across five lenses.

**Architecture:** Both skills live in `.claude/skills/` (project-local, consistent with the existing `analyze-skill-design` / `analyze-agent-design` pair). Each skill discovers its target files via `find`, applies five quality lenses per file, writes a structured report to `docs/`, and commits. No inter-skill dependencies; Tasks 1 and 2 are fully independent.

**Tech Stack:** Markdown (SKILL.md files), `find`/`grep`/`git` bash commands, Write/Edit tools for report output.

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `.claude/skills/audit-skill-quality/SKILL.md` | Create | 5-lens per-file quality audit for skills |
| `.claude/skills/audit-agent-quality/SKILL.md` | Create | 5-lens per-file quality audit for agents |
| `docs/al-dev-skill-quality.md` | Written at skill runtime | Output produced by `/audit-skill-quality` on first run |
| `docs/al-dev-agent-quality.md` | Written at skill runtime | Output produced by `/audit-agent-quality` on first run |

---

### Task 1: Create audit-skill-quality skill

**Files:**
- Create: `.claude/skills/audit-skill-quality/SKILL.md`

- [ ] **Step 1: Define acceptance checks — run now, expect FAIL**

```bash
ls .claude/skills/audit-skill-quality/SKILL.md 2>&1 || echo "Expected: not found"
```

- [ ] **Step 2: Create the directory**

```bash
mkdir -p .claude/skills/audit-skill-quality
```

- [ ] **Step 3: Write the skill file**

Write `.claude/skills/audit-skill-quality/SKILL.md` with this exact content:

````markdown
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

Per-file quality audit of al-dev plugin skills. Reads each SKILL.md directly
and writes a structured findings report to `docs/al-dev-skill-quality.md`.

If an argument is passed (e.g., `/audit-skill-quality al-dev-develop`), only
that skill is audited and only its section is updated in the report.

---

## Step 1 — Discover Skill Files

```bash
find profile-al-dev-shared/skills -name "SKILL.md" | sort
```

Build a list of skill names from directory names
(e.g., `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` → skill name `al-dev-develop`).

If an argument was passed, restrict to the single matching skill file only.

---

## Step 2 — Apply Five Quality Lenses

Read each SKILL.md in full. For each, run all five lenses and record every
finding with four fields: **Lens**, **Severity**, **Observation**, **Fix**.

Severity scale:
- **High** — ambiguous enough to change behavior, or an outright contradiction
- **Medium** — convention violation or moderate bloat that degrades maintainability
- **Low** — minor drift, style, or clarity issue with limited behavioral impact

### Lens 1 — Prompt Clarity

Check for:

- Instructions interpretable in more than one way — record the ambiguous sentence
- Vague qualifiers with no operative definition: "as needed", "appropriate",
  "reasonable", "if necessary"
- `if X` branches with no `else` / `otherwise` clause (incomplete conditional)
- Bash code blocks that are pseudo-code rather than runnable commands (unrecognised
  binary names, unexplained `<placeholder>` syntax, variables defined nowhere)
- Steps that reference undefined placeholders or variables

Severity: High for ambiguity that changes observable behavior; Medium for
vague qualifiers; Low for minor style issues.

### Lens 2 — Structural Conventions

Check:

- `name` field in frontmatter matches the directory name exactly
- `description` field is present in frontmatter
- `argument-hint` is present when the body references an optional argument
- Phase/step headers are numbered consistently — not mixing "Phase N" and
  "Step N" in the same file
- Output files referenced in the body follow the `.dev/YYYY-MM-DD-<skill>-*.md`
  naming convention (or `docs/` for persistent report-style outputs)
- Every code block has a language tag (`bash`, `markdown`, `python`, etc.)

Severity: Medium for missing or inconsistent frontmatter fields; Low for
numbering inconsistency or missing language tags.

### Lens 3 — Description Drift

Compare `description` and trigger phrases against the body:

- Key action verbs in the description ("Spawns", "Writes", "Reads", "Audits")
  that do not appear as actual instructions in the body
- Trigger phrases describing use cases absent from the body
- Related skills or agents mentioned in the description that do not appear in
  the body
- Description that promises an output file the body does not produce

Severity: Medium for a missing use case or absent output; Low for minor verb mismatch.

### Lens 4 — Bloat

Check:

- Step/phase count > 6
- Any single step > ~20 lines
- `skip if...` or `only if...` conditions that are effectively always true
  given normal usage (dead branches with no realistic false path)
- Repetitive instruction blocks across steps that could be stated once
- Accumulated historical commentary ("as of v2", "previously this was", "now
  uses") that belongs in git history, not the skill body

Severity: High for > 30 lines in a single step or > 8 total steps; Medium
for dead branches or repetition; Low for minor historical commentary.

### Lens 5 — Name Fit

Compare the skill name against the primary verb and scope in the description
and body:

- Name implies X but body primarily does Y (scope has shifted since naming)
- Name is too generic relative to a narrower actual scope
- Another skill in the directory has a name so similar a user would struggle
  to choose between them
- Name uses an action verb inconsistent with how the skill is triggered

Severity: High if the name actively misleads; Medium for moderate drift; Low
for minor verb mismatch.

---

## Step 3 — Write the Report

### Full run (no argument passed)

Fully replace `docs/al-dev-skill-quality.md`. Substitute actual values for all
angle-bracket placeholders before writing.

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

**[High] Lens 1 — Prompt Clarity**
Observation: <offending text or pattern>
Fix: <one-line suggestion>

**[Medium] Lens 4 — Bloat**
Observation: <what is bloated>
Fix: <one-line suggestion>

---

### /<other-skill> ✅ No findings.

---
```

Ordering rules: skills with findings first (sorted by highest-severity finding
descending), then clean skills. Each skill section ends with `---`.

### Scoped run (argument passed)

1. Read `docs/al-dev-skill-quality.md` if it exists.
2. Locate the section for the named skill — from `### /<arg>` to just before
   the next `### /` heading or the end of `## Findings`.
3. Build a replacement section with the new findings (or `### /<arg> ✅ No findings.`).
4. If the section exists: replace it in-place using the Edit tool, with the
   old section text as `old_string` and the new section as `new_string`.
5. If the section does not exist yet: append it at the end of `## Findings`.
6. Recalculate Summary counts by scanning all `**[High]`, `**[Medium]`, and
   `**[Low]` occurrences in the updated file, then rewrite the Summary table.
7. If `docs/al-dev-skill-quality.md` does not yet exist, write a new full
   report containing only the named skill's section.

---

## Step 4 — Commit

```bash
git -C . add docs/al-dev-skill-quality.md
git -C . commit -m "docs: update skill quality audit"
```

For scoped runs, name the target in the message:

```bash
git -C . commit -m "docs: update skill quality audit — /<skill-name>"
```

Replace `<skill-name>` with the actual argument value.

---

## Step 5 — Present to User

Print one line per audited skill:
- With findings: `/<skill-name>: N High, N Medium, N Low`
- Without findings: `/<skill-name>: ✅ clean`

Ask: "Would you like to fix any of these now?"
````

- [ ] **Step 4: Run acceptance checks — expect all PASS**

```bash
ls .claude/skills/audit-skill-quality/SKILL.md && echo "Exists: OK"
grep -q "^name: audit-skill-quality" .claude/skills/audit-skill-quality/SKILL.md && echo "name: OK"
grep -q "^description:" .claude/skills/audit-skill-quality/SKILL.md && echo "description: OK"
grep -q "^argument-hint:" .claude/skills/audit-skill-quality/SKILL.md && echo "argument-hint: OK"
grep -c "### Lens [1-5]" .claude/skills/audit-skill-quality/SKILL.md   # expect: 5
grep -q "git -C \." .claude/skills/audit-skill-quality/SKILL.md && echo "commit_step: OK"
grep -q "docs/al-dev-skill-quality.md" .claude/skills/audit-skill-quality/SKILL.md && echo "output_ref: OK"
wc -l .claude/skills/audit-skill-quality/SKILL.md   # expect: > 80 lines
```

- [ ] **Step 5: Commit**

```bash
git -C . add .claude/skills/audit-skill-quality/SKILL.md
git -C . commit -m "feat(skills): add audit-skill-quality skill"
```

---

### Task 2: Create audit-agent-quality skill

**Files:**
- Create: `.claude/skills/audit-agent-quality/SKILL.md`

- [ ] **Step 1: Define acceptance checks — run now, expect FAIL**

```bash
ls .claude/skills/audit-agent-quality/SKILL.md 2>&1 || echo "Expected: not found"
```

- [ ] **Step 2: Create the directory**

```bash
mkdir -p .claude/skills/audit-agent-quality
```

- [ ] **Step 3: Write the skill file**

Write `.claude/skills/audit-agent-quality/SKILL.md` with this exact content:

````markdown
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

Per-file quality audit of al-dev plugin agents. Reads each agent `.md` directly
and writes a structured findings report to `docs/al-dev-agent-quality.md`.

If an argument is passed (e.g., `/audit-agent-quality al-dev-developer`), only
that agent is audited and only its section is updated in the report.

---

## Step 1 — Discover Agent Files

```bash
find profile-al-dev-shared/agents -name "*.md" | sort
```

Build a list of agent names from filenames
(e.g., `profile-al-dev-shared/agents/al-dev-developer.md` → agent name `al-dev-developer`).

If an argument was passed, restrict to the single matching agent file only.

---

## Step 2 — Apply Five Quality Lenses

Read each agent `.md` in full. For each, run all five lenses and record every
finding with four fields: **Lens**, **Severity**, **Observation**, **Fix**.

Severity scale:
- **High** — ambiguous enough to change behavior, or an outright contradiction
- **Medium** — convention violation or moderate bloat that degrades maintainability
- **Low** — minor drift, style, or clarity issue with limited behavioral impact

### Lens 1 — Prompt Clarity

Check for:

- Instructions interpretable in more than one way — record the ambiguous sentence
- Vague qualifiers with no operative definition: "as needed", "appropriate",
  "reasonable", "if necessary"
- `if X` branches with no `else` / `otherwise` clause (incomplete conditional)
- Bash code blocks that are pseudo-code rather than runnable commands (unrecognised
  binary names, unexplained `<placeholder>` syntax, variables defined nowhere)
- Steps or missions that reference undefined placeholders or variables

Severity: High for ambiguity that changes observable behavior; Medium for
vague qualifiers; Low for minor style issues.

### Lens 2 — Structural Conventions

Check:

- Frontmatter has `description`, `model`, and `tools` fields
- `description` is a single sentence (not a multi-sentence paragraph)
- Agent has both `## Inputs` and `## Outputs` tables in the body, or a clearly
  stated reason for their absence (e.g., "Inputs: none — invoked directly")
- Tools list uses only canonical tool names: Read, Write, Edit, Glob, Grep,
  Bash, Agent, AskUserQuestion, WebSearch, WebFetch, and MCP tool names in the
  `mcp__<server>__<tool>` format

Severity: Medium for missing frontmatter fields, multi-sentence description,
or absent Inputs/Outputs tables; Low for non-canonical tool name casing.

### Lens 3 — Description Drift

Compare `description` against the body:

- Key action verbs in the description ("Spawns", "Writes", "Reads", "Dispatches")
  that do not appear as actual instructions in the body
- The description names a spawning skill or workflow context that contradicts the
  body (e.g., description says "Dispatched by /skill-a" but body only references
  a different workflow)
- Description promises an output file the body does not produce
- Description names a caller that the body does not match

Severity: Medium for a mismatched caller or absent output; Low for minor verb mismatch.

### Lens 4 — Bloat

Check:

- Section count in the system prompt body > 4 (excluding frontmatter)
- Any single section > ~20 lines
- `if X` conditions that are effectively always true (dead branches)
- Repetitive instruction blocks across sections that could be stated once
- Accumulated historical commentary ("as of v2", "previously this was", "now
  uses") that belongs in git history, not the agent body

Severity: High for > 30 lines in a single section or > 6 total sections;
Medium for dead branches or repetition; Low for minor historical commentary.

### Lens 5 — Name Fit

Compare the agent name against the primary verb and scope in the description
and body:

- Name implies X but body primarily does Y (scope has shifted since naming)
- Name is too generic relative to a narrower actual scope
- Another agent in the directory has a name so similar a user would struggle
  to distinguish them
- Name uses a noun or adjective inconsistent with what the agent actually does

Severity: High if the name actively misleads; Medium for moderate drift; Low
for minor mismatch.

---

## Step 3 — Write the Report

### Full run (no argument passed)

Fully replace `docs/al-dev-agent-quality.md`. Substitute actual values for all
angle-bracket placeholders before writing.

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

### al-dev-<name>

**[High] Lens 1 — Prompt Clarity**
Observation: <offending text or pattern>
Fix: <one-line suggestion>

**[Medium] Lens 2 — Structural Conventions**
Observation: <what is missing or inconsistent>
Fix: <one-line suggestion>

---

### al-dev-<other-name> ✅ No findings.

---
```

Ordering rules: agents with findings first (sorted by highest-severity finding
descending), then clean agents. Each agent section ends with `---`.

### Scoped run (argument passed)

1. Read `docs/al-dev-agent-quality.md` if it exists.
2. Locate the section for the named agent — from `### al-dev-<arg>` (or
   `### <arg>` if the argument was passed without prefix) to just before the
   next `### ` heading or the end of `## Findings`.
3. Build a replacement section with the new findings (or `### <agent-name> ✅ No findings.`).
4. If the section exists: replace it in-place using the Edit tool, with the
   old section text as `old_string` and the new section as `new_string`.
5. If the section does not exist yet: append it at the end of `## Findings`.
6. Recalculate Summary counts by scanning all `**[High]`, `**[Medium]`, and
   `**[Low]` occurrences in the updated file, then rewrite the Summary table.
7. If `docs/al-dev-agent-quality.md` does not yet exist, write a new full
   report containing only the named agent's section.

---

## Step 4 — Commit

```bash
git -C . add docs/al-dev-agent-quality.md
git -C . commit -m "docs: update agent quality audit"
```

For scoped runs, name the target in the message:

```bash
git -C . commit -m "docs: update agent quality audit — al-dev-<agent-name>"
```

Replace `<agent-name>` with the actual argument value.

---

## Step 5 — Present to User

Print one line per audited agent:
- With findings: `al-dev-<name>: N High, N Medium, N Low`
- Without findings: `al-dev-<name>: ✅ clean`

Ask: "Would you like to fix any of these now?"
````

- [ ] **Step 4: Run acceptance checks — expect all PASS**

```bash
ls .claude/skills/audit-agent-quality/SKILL.md && echo "Exists: OK"
grep -q "^name: audit-agent-quality" .claude/skills/audit-agent-quality/SKILL.md && echo "name: OK"
grep -q "^description:" .claude/skills/audit-agent-quality/SKILL.md && echo "description: OK"
grep -q "^argument-hint:" .claude/skills/audit-agent-quality/SKILL.md && echo "argument-hint: OK"
grep -c "### Lens [1-5]" .claude/skills/audit-agent-quality/SKILL.md   # expect: 5
grep -q "git -C \." .claude/skills/audit-agent-quality/SKILL.md && echo "commit_step: OK"
grep -q "docs/al-dev-agent-quality.md" .claude/skills/audit-agent-quality/SKILL.md && echo "output_ref: OK"
wc -l .claude/skills/audit-agent-quality/SKILL.md   # expect: > 80 lines
```

- [ ] **Step 5: Commit**

```bash
git -C . add .claude/skills/audit-agent-quality/SKILL.md
git -C . commit -m "feat(skills): add audit-agent-quality skill"
```

---

## Self-Review Notes

**Spec coverage:**
- `/audit-skill-quality` skill file → Task 1 ✓
- `/audit-agent-quality` skill file → Task 2 ✓
- All five lenses in each skill → Step 2 sub-sections in both tasks ✓
- Full replace on full runs; scoped update on named arg → Step 3 in both tasks ✓
- Each finding: lens name + severity tag + observation + fix → Step 2 format note ✓
- Both skills commit after writing → Step 4 in both tasks ✓
- Both skills are project-local (`.claude/skills/`) → directories in Tasks 1 and 2 ✓
- Trigger phrases cover all listed phrases → `description` frontmatter in both ✓
- `docs/al-dev-skill-quality.md` and `docs/al-dev-agent-quality.md` created on first run → Step 3 full-run branch in both ✓

**Placeholder scan:** No `TODO`, `TBD`, or incomplete steps found. `YYYY-MM-DD` appears only as a file-naming convention template within lens definitions (not as an unrendered date value).

**Type consistency:** Report structure, section headings, and git commit command format are consistent across Tasks 1 and 2.
