---
name: quality-skill-lens-bloat
description: Apply Bloat lens to SKILL.md files — detects oversized steps, dead conditional branches, repetitive instruction blocks, and historical commentary. Returns a findings block.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Bloat

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name.

> Note: this lens counts top-level **steps/phases** (>8); the agent bloat lens
> (`quality-agent-lens-bloat`) counts **sections** (>6). The thresholds differ
> by design because they measure different surfaces — do not flag the mismatch
> as an inconsistency.

**Check for:**

- Step/phase count (top-level `## Step` or `## Phase` headers) > 8
- Any single step > 30 lines
- `skip if...` or `only if...` conditions that always evaluate the same way in all
  realistic invocations based on the agent's documented contract (dead branches)
- Repetitive instruction blocks across steps that could be stated once
- Accumulated historical commentary ("as of v2", "previously this was", "now uses")
  that belongs in git history, not the skill body

**Severity rules:**

- High: any single step > 30 lines or > 8 total top-level steps
- Medium: dead branches or repetitive instruction blocks
- Low: minor historical commentary

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Bloat Findings

- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Bloat Findings

_No issues found._
