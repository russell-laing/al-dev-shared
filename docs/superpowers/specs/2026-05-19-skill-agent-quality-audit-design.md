# Skill and Agent Quality Audit Design

**Date:** 2026-05-19  
**Status:** Approved  
**Scope:** Two new project-local skills (`/audit-skill-quality`, `/audit-agent-quality`) that read source files directly and check for prompt clarity, structural conventions, description drift, bloat, and name fit.

---

## Motivation

The existing analyzer skills (`/analyze-skill-design`, `/analyze-agent-design`) address *architectural* quality: how skills and agents relate to each other, whether they should be merged, split, or connected. They do not check the internal quality of each skill or agent file — prompt clarity, convention adherence, description drift, bloat, and whether names still fit their contents.

As the plugin grows and skills evolve, these per-file quality concerns accumulate silently. A new `audit` tier fills this gap and completes the analysis pipeline:

```
/review-skill-map  → /analyze-skill-design  → /audit-skill-quality
/review-agent-map  → /analyze-agent-design  → /audit-agent-quality
```

---

## Architecture

Two new skills, both project-local (`.claude/skills/`), consistent with the existing analyzer pair:

| Deliverable | Type | Location |
|---|---|---|
| `/audit-skill-quality` | New skill | `.claude/skills/audit-skill-quality/SKILL.md` |
| `/audit-agent-quality` | New skill | `.claude/skills/audit-agent-quality/SKILL.md` |
| `docs/al-dev-skill-quality.md` | New document | Written by `/audit-skill-quality` |
| `docs/al-dev-agent-quality.md` | New document | Written by `/audit-agent-quality` |

Each skill reads source files directly (SKILL.md / agent .md files), not the map docs. They do not depend on the maps being fresh, but running the review skills first ensures the active file list is accurate.

---

## The Five Quality Lenses

Both skills apply the same five lenses to their respective file types:

### Lens 1 — Prompt Clarity

Reads the body for:
- Instructions interpretable in more than one way
- Vague qualifiers without a definition: "as needed", "appropriate", "reasonable", "if necessary"
- `if X` branches with no `else` / `otherwise` (incomplete conditional)
- Bash blocks that are pseudo-code rather than runnable commands
- Steps that reference undefined placeholders or variables

### Lens 2 — Structural Conventions

For **skills**, checks:
- Frontmatter has `name` (matching directory name), `description`, and `argument-hint` when the skill accepts arguments
- Phase/step headers are numbered consistently — not mixing "Phase N" and "Step N" in the same file
- Output files follow the `.dev/YYYY-MM-DD-<skill>-*.md` naming pattern
- All code blocks carry a language tag (`bash`, `markdown`, etc.)

For **agents**, checks:
- Frontmatter has `name`, `description`, `model`, and `tools`
- Agent has `## Inputs` and `## Outputs` tables (or a documented reason for their absence)
- Description is a single sentence (consistent with existing agents)
- Tools list uses the canonical tool names (Read, Write, Edit, Glob, Grep, Bash, Agent)

### Lens 3 — Description Drift

Compares the frontmatter `description` (and trigger phrases for skills) against what the body actually does:
- Key action verbs in the description ("Spawns", "Writes", "Reads", "Audits") do not match the body
- Trigger phrases describe use cases absent from the body
- Related skills/agents mentioned in the description do not appear in the body
- The description promises an output that the body does not produce

### Lens 4 — Bloat

- Phase/step count > 6 for skills; section count > 4 for agent system prompts
- Any single phase > ~20 lines
- `skip if...` or `only if...` conditions that are effectively always true (dead branches)
- Repetitive instruction patterns across phases that could be stated once
- Accumulated historical commentary or change notes that belong in git history, not the file body

### Lens 5 — Name Fit

Compares the skill/agent name against the primary verb and scope in the description and body:
- Name implies X but the body primarily does Y (scope has shifted since naming)
- Name has become too generic relative to a narrower actual scope
- Two skills or agents with names so similar that a user would struggle to choose between them
- Name uses an action verb inconsistent with how the skill is actually triggered or used

---

## Output Format

Both skills write a structured markdown report. The file is **fully replaced on each run** — it always reflects current state. Fixed findings disappear; there is no `← implemented` accumulation.

### Report structure

```markdown
# AL Dev Skill Quality Audit

**Last run:** YYYY-MM-DD
**Skills audited:** N

## Summary

| Severity | Count |
|----------|-------|
| High     | 0     |
| Medium   | N     |
| Low      | N     |

## Findings

### /skill-name

**[High] Lens 1 — Prompt Clarity**
Observation: Step 3 says "handle appropriately" with no definition of appropriate.
Fix: Replace with explicit success and failure branches.

**[Low] Lens 4 — Bloat**
Observation: Phase 5 is 28 lines; the conditional logic repeats Phase 3.
Fix: Consolidate into a shared instruction block.

---

### /other-skill ✅ No findings.

---
```

Severity definitions:
- **High** — instruction is ambiguous enough to change behavior, or a contradiction exists
- **Medium** — convention violation or moderate bloat that degrades maintainability
- **Low** — minor drift, style, or clarity issue with limited behavioral impact

### Argument support

Both skills accept an optional skill/agent name argument to scope the audit to one file:

```
/audit-skill-quality al-dev-develop
/audit-agent-quality al-dev-developer
```

In scoped mode, only the named file is audited. The output section for that skill/agent is updated in-place in the report without replacing the full file.

---

## Commit Behaviour

After writing the report, each skill commits:

```bash
git -C . add docs/al-dev-skill-quality.md   # or al-dev-agent-quality.md
git -C . commit -m "docs: update skill quality audit"
```

If run in scoped mode (single skill/agent), the commit message names the target:

```bash
git -C . commit -m "docs: update skill quality audit — /al-dev-develop"
```

---

## Trigger Descriptions

`audit-skill-quality`:
> Audit profile-al-dev-shared skills for internal quality: prompt clarity, structural conventions, description drift, bloat, and name fit. Reads each SKILL.md directly and writes findings to docs/al-dev-skill-quality.md. Run after /analyze-skill-design for a complete picture. Triggers on: "audit skill quality", "check skill quality", "are skills well written", "skill quality report", "check for skill drift", "skill bloat".

`audit-agent-quality`:
> Audit profile-al-dev-shared agents for internal quality: prompt clarity, structural conventions, description drift, bloat, and name fit. Reads each agent .md directly and writes findings to docs/al-dev-agent-quality.md. Run after /analyze-agent-design for a complete picture. Triggers on: "audit agent quality", "check agent quality", "are agents well written", "agent quality report", "check for agent drift", "agent bloat".

---

## Acceptance Criteria

- [ ] `audit-skill-quality` skill file exists at `.claude/skills/audit-skill-quality/SKILL.md`
- [ ] `audit-agent-quality` skill file exists at `.claude/skills/audit-agent-quality/SKILL.md`
- [ ] Both skills apply all five lenses (Clarity, Conventions, Drift, Bloat, Name Fit) and document each lens in the skill body
- [ ] Output files are fully replaced on full runs; scoped runs update only the named section
- [ ] Each finding includes lens name, severity tag, observation, and a one-line fix suggestion
- [ ] Both skills commit the output doc after writing
- [ ] Both skills appear in `.claude/skills/` (project-local, not distributed plugin)
- [ ] Trigger descriptions cover all listed trigger phrases
- [ ] `docs/al-dev-skill-quality.md` and `docs/al-dev-agent-quality.md` are created on first run
