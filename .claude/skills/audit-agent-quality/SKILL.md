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

Per-file quality audit of al-dev plugin agents. Reads each agent markdown
directly and writes a structured findings report to `docs/al-dev-agent-quality.md`.

If an argument is passed (e.g., `/audit-agent-quality al-dev-developer`), only
that agent is audited and only its section is updated in the report.

---

## Step 1 — Discover Agent Files

```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" | sort
```

Build a list of agent names from file names without the `.md` extension
(e.g., `profile-al-dev-shared/agents/al-dev-developer.md` -> agent name `al-dev-developer`).

If an argument was passed, restrict to the single matching agent file only.

---

## Step 2 — Apply Five Quality Lenses

Read each agent file in full. For each, run all five lenses and record every
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

- Agent file name (without `.md`) matches the `al-dev-<name>` prefix convention
- `description` field is present in frontmatter and is a single sentence
- `model` field is present in frontmatter
- `tools` field is present in frontmatter and contains only canonical names:
  `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `Agent`, `AskUserQuestion`,
  `WebSearch`, `WebFetch`, or `mcp__`-prefixed tool names
- Frontmatter contains no skill-only fields (`argument-hint`, `triggers`) that
  are invalid in agents
- `## Inputs` and `## Outputs` tables are present, or a stated reason explains
  their absence
- Phase/step headers are numbered consistently — not mixing "Phase N" and
  "Step N" in the same file
- Every code block has a language tag (`bash`, `markdown`, `python`, etc.)

Severity: High for missing `model` or `tools` frontmatter fields; Medium for
missing Inputs/Outputs tables, non-canonical tool names, a file name that does
not match the `al-dev-<name>` convention, or skill-only fields in frontmatter;
Low for numbering inconsistency or missing language tags.

### Lens 3 — Description Drift

Compare `description` against the body:

- Key action verbs in the description ("Spawns", "Writes", "Reads", "Implements",
  "Audits") that do not appear as actual instructions in the body
- Description names the spawning skill or workflow but body contradicts it
- Description promises an output file that the body does not produce
- Description names the expected caller but the body does not match that caller's
  conventions

Severity: Medium for a missing use case or absent output; Low for minor verb mismatch.

### Lens 4 — Bloat

Check:

- Section count in the system prompt body > 6 top-level sections
- Any single section > 30 lines
- `skip if...` or `only if...` conditions that are effectively always true
  given normal usage (dead branches with no realistic false path)
- Repetitive instruction blocks across sections that could be stated once
- Accumulated historical commentary ("as of v2", "previously this was", "now
  uses") that belongs in git history, not the agent body

Severity: High for any single section > 30 lines or > 6 total top-level
sections; Medium for dead branches or repetition; Low for minor historical
commentary.

### Lens 5 — Name Fit

Compare the agent name against the primary verb and scope in the description
and body:

- Name implies X but body primarily does Y (scope has shifted since naming)
- Name is too generic relative to a narrower actual scope
- Another agent in the directory has a name so similar a user would struggle
  to choose between them
- Name uses a noun or adjective that conflicts with the agent's actual action

Severity: High if the name actively misleads; Medium for moderate drift; Low
for minor verb mismatch.

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

### al-dev-<agent-name>

**[High] Lens 1 — Prompt Clarity**
Observation: <offending text or pattern>
Fix: <one-line suggestion>

**[Medium] Lens 4 — Bloat**
Observation: <what is bloated>
Fix: <one-line suggestion>

---

### al-dev-<other-agent> — No findings.

---
```

Ordering rules: agents with findings first (sorted by highest-severity finding
descending), then clean agents. Each agent section ends with `---`.

Clean agents use exactly this format (no emoji): `### al-dev-<name> — No findings.`

### Scoped run (argument passed)

The argument may include or omit the `al-dev-` prefix; normalize by stripping
it if present and always prepend `al-dev-` when constructing the section heading.
For example, both `al-dev-developer` and `developer` resolve to section heading
`### al-dev-developer`.

1. Read `docs/al-dev-agent-quality.md` if it exists.
2. Locate the section for the named agent — from `### al-dev-<arg>` to just
   before the next `### al-dev-` heading or the end of `## Findings`.
3. Build a replacement section with the new findings (or
   `### al-dev-<arg> — No findings.`).
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
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-agent-quality.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update agent quality audit"
```

For scoped runs, name the target in the message:

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs: update agent quality audit — al-dev-<agent-name>"
```

Replace `<agent-name>` with the actual argument value.

---

## Step 5 — Present to User

Print one line per audited agent:
- With findings: `al-dev-<agent-name>: N High, N Medium, N Low`
- Without findings: `al-dev-<agent-name>: clean`

Ask: "Would you like to fix any of these now?"
