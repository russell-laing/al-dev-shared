---
name: design-skill-lens-complexity
description: Apply Complexity Outliers lens to plugin skills — ranks skills by phase count to find high-phase skills with separable concerns (Atomise) and zero-agent 2-phase skills (Absorb candidates). Returns findings.
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

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Complexity Outliers Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Complexity Outliers Findings
_No issues found._
