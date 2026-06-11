---
name: quality-agent-lens-clarity
description: Apply Prompt Clarity lens to agent files — identifies ambiguous instructions, vague qualifiers, incomplete conditionals, and pseudo-code blocks. Returns a findings block.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |

**Note:** All checks analyze the prose instructions in each agent file directly — no external context is required beyond the file list. The incomplete-conditional check looks for `if` clauses in prose that have no corresponding `else`/`otherwise` branch; it does not analyze code blocks.

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Prompt Clarity

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

**Check for — flag every occurrence:**

- Instructions interpretable in more than one way — flag a sentence when a
  reader could plausibly act two different ways from it and those two readings
  lead to different observable actions; record the ambiguous sentence verbatim
- Vague qualifiers with no operative definition: "as needed", "appropriate", "reasonable", "if necessary"
- `if X` branches with no `else` / `otherwise` clause (incomplete conditional)
- Bash code blocks that are pseudo-code rather than runnable commands: unrecognised
  binary names, unexplained `<placeholder>` syntax, variables defined nowhere.
  (Note: In these instructions, `<placeholder>` is meta-notation indicating a substitution point;
  actual bash blocks with undefined placeholder syntax should be flagged as such.)
  A bash block is acceptable when every binary it invokes is a recognised tool
  in this repository's workflows (e.g. `git`, `grep`, `sed`, `find`, `python3`,
  `rg`) or a script that exists in the repository, every variable is defined in
  the block or earlier in the same file, and every `<placeholder>` is
  accompanied by an instruction stating what to substitute.
- Steps that reference undefined placeholders or variables

**Severity rules:**

- High: ambiguity that changes observable behavior
- Medium: vague qualifiers with no definition
- Low: minor style issues

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Prompt Clarity Findings

- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Prompt Clarity Findings

_No issues found._
