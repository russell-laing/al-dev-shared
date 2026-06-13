---
name: quality-skill-lens-clarity
description: Apply Prompt Clarity lens to SKILL.md files — identifies ambiguous instructions, vague qualifiers, incomplete conditionals, and pseudo-code blocks. Returns a findings block.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

Returns a findings block. See Output Format.

**Definition check — run before flagging any occurrence.** A term, qualifier, or
conditional is only a finding when it is unresolved in the material available to
you. Before flagging:

- Scan the **entire file**, not just the sentence in question — later sections, a
  Severity Rules block, a table, a subsequent phase, or an enumerated list often
  define the term or supply the missing `else` branch. If the term is defined,
  enumerated, or disambiguated anywhere in the same file, do **not** flag it.
- If the text defers definition to a named repo doc (e.g. "see
  `knowledge/foo.md`") and that relative path resolves, Read it; if the term is
  defined there, do **not** flag it.

Flag only what stays unresolved after both checks. Resolving a term elsewhere is
not a miss — genuine ambiguity (undefined everywhere) still fires.

---

## Lens: Prompt Clarity

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name (e.g., `.../skills/al-dev-develop/SKILL.md`
→ skill name `al-dev-develop`).

**Check for — flag every occurrence:**

- Instructions interpretable in more than one way — record the ambiguous sentence verbatim
- Vague qualifiers with no operative definition: "as needed", "appropriate", "reasonable", "if necessary"
- Incomplete prose conditionals: a prose sentence stating a condition and its
  outcome (`if X, do Y` / `when X, Y`) with no `else` / `otherwise` outcome
  for the unmet case. Applies to prose sentences only — do not analyze
  conditionals inside fenced code blocks.
- Bash code blocks that are pseudo-code rather than runnable commands. A binary
  name is **recognised** (do not flag) if it is a standard POSIX/coreutils
  command (e.g. `ls`, `grep`, `find`, `sed`, `awk`, `cat`, `python3`, `git`,
  `jq`, `mkdir`, `rm`), a command defined earlier in the same block (e.g. a shell
  function or variable), or a script under the repo's `scripts/` directory.
  Flag a block only when it uses an **unrecognised** binary outside those
  categories, unexplained `<placeholder>` syntax, or variables defined nowhere.
  (Note: In these instructions, `<placeholder>` is meta-notation indicating a
  substitution point; actual bash blocks with undefined placeholder syntax should
  be flagged as such.)
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
