---
name: quality-skill-lens-clarity
description: Apply Prompt Clarity lens to SKILL.md files — identifies ambiguous instructions, vague qualifiers, incomplete conditionals, and pseudo-code blocks. Returns a findings block.
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

## Lens: Prompt Clarity

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name (e.g., `.../skills/al-dev-develop/SKILL.md`
→ skill name `al-dev-develop`).

**Check for — flag every occurrence:**
- Instructions interpretable in more than one way — record the ambiguous sentence verbatim
- Vague qualifiers with no operative definition: "as needed", "appropriate", "reasonable", "if necessary"
- `if X` branches with no `else` / `otherwise` clause (incomplete conditional)
- Bash code blocks that are pseudo-code rather than runnable commands: unrecognised
  binary names, unexplained `<placeholder>` syntax, variables defined nowhere
- Steps that reference undefined placeholders or variables

**Severity rules:**
- High: ambiguity that changes observable behavior
- Medium: vague qualifiers with no definition
- Low: minor style issues

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Prompt Clarity Findings
- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Prompt Clarity Findings
_No issues found._
