---
name: design-skill-lens-complexity
description: Apply the Complexity Outliers lens to plugin skills — evaluates skills ranked by phase count to find high-phase skills with separable concerns (Atomise) and zero-agent 2-phase skills (Absorb). Returns findings.
model: sonnet
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| phase_counts | Mapping of skill-name → phase/step count (provided in dispatch prompt). Format: JSON object `{ "skill-name": N, … }` |
| no_agent_skills | List of skills with no dedicated agent spawned (provided in dispatch prompt). Format: JSON array `["skill-name", …]` |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Complexity Outliers (→ Atomise or Absorb)

Read every file path provided in the dispatch prompt. Use `phase_counts` for ranking.

**High-phase skills (6+ phases):**
Read each. Ask: do the phases cluster into two distinct concerns (e.g., pre-flight +
execution, or discovery + analysis + output)? Flag as Atomise candidate only if
**each concern spans ≥2 phases and is independently runnable** (the concern's phases
form a contiguous block that produces a deliverable usable by a downstream step
without executing the other concern's phases). A concern that is a single phase,
or that cannot run without the rest of the skill, is not an Atomise candidate.

**Zero-agent, 2-phase skills (from `no_agent_skills`):**
Ask: could this skill be absorbed into an adjacent skill as an option flag or
sub-step rather than a separate invocation? Flag as Absorb candidate if the
skill's entire body could fit as one extra phase in an existing adjacent skill.

---

## Verdict and Severity Rules

**Severity rules:**

- High: skill has 8+ phases with two clearly separable concerns ("clearly separable" = each concern spans ≥2 phases and is independently runnable — see Atomise criteria in the Lens body below) (significant
  cognitive load on every invocation)
- Medium: skill has 6-7 phases with separable concerns, or zero-agent 2-phase
  skill that overlaps heavily with an adjacent skill
- Low: minor complexity that warrants monitoring but not immediate action

**Verdict gates severity.** Every finding carries an explicit verdict:
`Atomise`, `Absorb`, or `None`. High and Medium both require separable
concerns — they are only valid with verdict `Atomise` or `Absorb`. Verdict
`None` means no actionable finding: the skill does not meet the Atomise or
Absorb criteria, regardless of its phase count. A `None`-verdict finding
carries severity Low as an informational note only — it is not a Low-severity
defect flag. Never emit a High or Medium finding with verdict `None`.

**Fail-both case** (phase-count threshold met, but both Atomise and Absorb
fail): when a skill's phase count alone would qualify it as High or Medium yet
it fails BOTH the Atomise and Absorb criteria, downgrade it to **Low with
verdict `None`**. Record the raw phase count and the severity-mismatch reason
(phase count implied High/Medium, but no separable concern qualified) in the
observation field, so the diagnostic value is preserved without inflating
severity.

---

## Output Format

Return exactly this block (no additional prose before or after):

### Complexity Outliers Findings

- **[skill-name]** | [High|Medium|Low] | verdict=[Atomise|Absorb|None] | [observation] | [fix]

If the block has no findings, emit it with a single `_No issues found._` line:

### Complexity Outliers Findings

_No issues found._
