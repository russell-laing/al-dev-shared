---
name: design-skill-lens-complexity
description: Apply Complexity Outliers and Surface Placement lenses to plugin skills — ranks skills by phase count to find high-phase skills with separable concerns (Atomise) and zero-agent 2-phase skills (Absorb), and flags skills that belong in the repo-local maintainer surface (Move). Returns findings.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| phase_counts | Mapping of skill-name → phase/step count (provided in dispatch prompt) |
| no_agent_skills | List of skills with no dedicated agent spawned (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Complexity Outliers (→ Atomise or Absorb)

Read every file path provided in the dispatch prompt. Use `phase_counts` for ranking.

**High-phase skills (6+ phases):**
Read each. Ask: do the phases cluster into two distinct concerns (e.g., pre-flight +
execution, or discovery + analysis + output)? If two distinct concern groups are
identifiable by deleting a contiguous block of phases, flag as Atomise candidate.

**Zero-agent, 2-phase skills (from `no_agent_skills`):**
Ask: could this skill be absorbed into an adjacent skill as an option flag or
sub-step rather than a separate invocation? Flag as Absorb candidate if the
skill's entire body could fit as one extra phase in an existing adjacent skill.

**Severity rules:**
- High: skill has 8+ phases with two clearly separable concerns (significant
  cognitive load on every invocation)
- Medium: skill has 6-7 phases with separable concerns, or zero-agent 2-phase
  skill that overlaps heavily with an adjacent skill
- Low: minor complexity that warrants monitoring but not immediate action

---

## Lens: Surface Placement (→ Move)

For each skill in `file_list`, score these three signals:

| Signal | What to check |
|--------|---------------|
| Internal path references | Body references `profile-al-dev-shared/`, `.claude/`, or repo-root filenames (e.g. `marketplace.json`) that only resolve inside this repo |
| Self-audit purpose | Stated purpose is maintaining or auditing the plugin itself (alignment checks, map reviews, design analysis) — not serving AL developers |
| No spawned agents | Skill name appears in `no_agent_skills` (no `al-dev-shared:` agent in the body) |

A skill scoring **2 or more signals** belongs in the repo-local maintainer
surface rather than the distributed plugin — flag as a Move candidate.

**Severity rules:**
- Medium: scores all three signals
- Low: scores exactly two signals

---

## Output Format

Return exactly these two blocks (no additional prose before, between, or after):

### Complexity Outliers Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

### Surface Placement Findings
- **[skill-name]** | [Medium|Low] | [observation] | [Move to .claude/skills/]

If a block has no findings, emit it with a single `_No issues found._` line:

### Complexity Outliers Findings
_No issues found._

### Surface Placement Findings
_No issues found._
