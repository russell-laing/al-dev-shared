---
name: quality-skill-lens-description
description: Apply Description Drift lens to SKILL.md files — compares description and trigger phrases against body content to detect disconnected verbs, missing outputs, and absent use cases. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Description Drift

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name.

**Compare the `description` frontmatter and trigger phrases against the body.
Check for:**
- Key action verbs in the description ("Spawns", "Writes", "Reads", "Audits")
  that do not appear as actual instructions in the body
- Trigger phrases describing use cases that are absent from the body steps
- Related skills or agents mentioned in the description that do not appear in
  the body
- Description that promises an output file the body does not produce

**Severity rules:**
- Medium: missing use case, absent promised output, or related skill/agent
  mentioned in description but not used in body
- Low: minor verb mismatch that does not affect behavior

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Description Drift Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Description Drift Findings
_No issues found._
