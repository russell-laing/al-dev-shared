---
name: design-skill-lens-near-duplicates
description: Apply Near-Duplicate Shapes lens to plugin skills — identifies pairs with similar structure (same agents, similar phase count, similar output patterns) that could be merged. Returns findings for Merge suggestions.
model: haiku
tools: ["Read"]
---

# Near-Duplicate Shapes Lens

## Inputs

| Field | Description |
| --- | --- |
| file_list | Newline-separated absolute paths to `SKILL.md` files |
| agent_usage_counts | Mapping of agent-type → list of skills that use it (provided in dispatch prompt) |
| phase_counts | Mapping of skill-name → phase/step count (provided in dispatch prompt) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Near-Duplicate Shapes (→ Merge)

Read the relevant file paths. Use `agent_usage_counts` to find pairs of skills
that use the same agent types.

For each pair sharing the same agent types:

1. Compare phase counts. If phase counts differ by at most 2, read both files.
2. Ask: is the difference a small delta — the two skills differ by ≤2 phases
   AND the complex skill adds **exactly one** element of: one output file, one reviewer, or one option flag (not multiple elements from this set)?
3. If yes: could the simpler skill become an option or mode of the more complex one?

**Merge criteria (all should be true):**

- Both skills use the same agent types
- Phase counts differ by at most 2
- The unique elements of the simpler skill could be expressed as an option flag
  on the more complex skill (e.g., `--quick`, `--dry-run`, `--light`)

**Severity rules:**

- Medium: pair meets all merge criteria and users would plausibly confuse the two (operative test: names differ by ≤1 content token, OR both appear in the same workflow layer with near-identical descriptions)
- Low: pair is similar but serves clearly distinct purposes that justify two skills

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Near-Duplicate Shapes Findings

- **[skill-a + skill-b]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

_No issues found._
