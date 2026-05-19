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
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills -name "SKILL.md" | sort
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
- Any single step > 30 lines
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

### /<other-skill> — No findings.

---
```

Ordering rules: skills with findings first (sorted by highest-severity finding
descending), then clean skills. Each skill section ends with `---`.

### Scoped run (argument passed)

1. Read `docs/al-dev-skill-quality.md` if it exists.
2. Locate the section for the named skill — from `### /<arg>` to just before
   the next `### /` heading or the end of `## Findings`.
3. Build a replacement section with the new findings (or `### /<arg> — No findings.`).
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
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-skill-quality.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update skill quality audit"
```

For scoped runs, name the target in the message:

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update skill quality audit — /<skill-name>"
```

Replace `<skill-name>` with the actual argument value.

---

## Step 5 — Present to User

Print one line per audited skill:
- With findings: `/<skill-name>: N High, N Medium, N Low`
- Without findings: `/<skill-name>: clean`

Ask: "Would you like to fix any of these now?"
