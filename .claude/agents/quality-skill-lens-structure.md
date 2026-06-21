---
name: quality-skill-lens-structure
description: Apply Structural Conventions lens to SKILL.md files — checks frontmatter fields, argument-hint presence, output file naming, and header numbering. Returns a findings block.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

A markdown findings block:

```text
## Structural Conventions Findings

| Severity | File:Line | Finding | Suggested fix |
|----------|-----------|---------|---------------|
| High/Medium/Low | skills/name/SKILL.md:NN | description | fix description |
```

Returns `_No issues found._` when no violations are detected. The caller includes
this block verbatim in the aggregated dossier.

---

## Lens: Structural Conventions

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name.

**Check each file for:**

- `name` field in YAML frontmatter matches the parent directory name exactly
- `description` field is present in frontmatter
- `argument-hint` is present in frontmatter when the body references an optional
  argument **in instruction prose** (look for `If an argument was passed` or
  `[arg]` patterns; count only prose mentions — exclude frontmatter and fenced
  code/example blocks)
- Phase/step headers are numbered consistently — not mixing "Phase N" and
  "Step N" in the same file
- Output files named in prose step instructions — exclude frontmatter `outputs:`
  fields and code-block examples — follow the `.dev/YYYY-MM-DD-<skill>-*.md`
  naming convention (or `docs/` for persistent report-style outputs)

**Not a structural requirement — do not flag:** missing code-block language tags
(markdownlint rule MD040). This is a deterministic, line-exact lint check that an
LLM scanning fences performs unreliably, and it is already enforced by the
`.claude/hooks/post_edit_markdownlint.py` post-edit hook and the commit preflight.
Do not raise MD040 findings here — they are redundant and historically dominated
by false positives.

**Severity rules:**

- Medium: missing or inconsistent frontmatter fields, `argument-hint` absent
  when body uses optional argument, output file naming doesn't follow convention
- Low: numbering inconsistency

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Structural Conventions Findings

- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Structural Conventions Findings

_No issues found._
