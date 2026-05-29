---
name: quality-skill-lens-name-fit
description: Apply Name Fit lens to SKILL.md files — compares skill name against primary verb and scope in description and body to detect naming drift and trigger-phrase conflicts. Returns a findings block.
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

## Lens: Name Fit

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name.

**Compare skill name against the primary verb and scope in description and body.
Check for:**
- Name implies X but body primarily does Y (scope has shifted since naming)
- Name is too generic relative to a narrower actual scope
- Another skill in the file list has a name so similar a user would struggle
  to choose between them
- Name uses an action verb inconsistent with how the skill is triggered
  (e.g., trigger phrases describe a different action than the name suggests)

**Severity rules:**
- High: name actively misleads a user about what the skill does when invoked
- Medium: moderate drift between name and actual scope or trigger phrases
- Low: minor verb mismatch with no behavioral consequence

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Name Fit Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Name Fit Findings
_No issues found._
