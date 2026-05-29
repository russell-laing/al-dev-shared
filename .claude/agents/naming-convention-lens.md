---
name: naming-convention-lens
description: Apply the Naming Convention lens to maintainer tool files and output paths — flags any tool name or output filename that violates docs/al-dev-naming-convention.md. Returns a findings block.
model: haiku
tools: ["Read", "Glob"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` and/or skill `SKILL.md` files |
| convention_doc | Absolute path to `docs/al-dev-naming-convention.md` (read it before judging) |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Naming Convention

Read `docs/al-dev-naming-convention.md` first — it is the source of truth. Then
read every file path in the dispatch prompt and derive each tool's name:
- Agent name = filename without directory and `.md`.
- Skill name = parent directory name of `SKILL.md`.

**Check tool names:**
- Lens agents (filename matches `*-lens-*`) MUST match
  `{design|quality}-{agent|skill}-lens-{aspect}`. The single allowed exception
  is `naming-convention-lens`. Any other lens-agent name that deviates is a
  **High** finding.
- Maintainer skills SHOULD match `{verb}-{object}-{aspect}` with the documented
  verb/object sets. A non-conforming skill name that is not a grandfathered
  pre-existing skill (`projection-sync`, `align-harness-repos`) is a **Low**
  finding (advisory).

**Check output paths** mentioned in the body (Write/output targets):
- Living docs must match `al-dev-{object}-{kind}.md`.
- Dated artifacts must match `{dir}/YYYY-MM-DD-{surface}-{kind}.md` with
  `surface` ∈ `plugin` | `tooling`.
- A documented output path that violates either pattern is a **Medium** finding.

**Severity summary:**
- High: a lens-agent filename that breaks the enforced lens pattern
- Medium: an output path that breaks a documented output pattern
- Low: an advisory skill-name deviation

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Naming Convention Findings
- **[tool-or-path-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Naming Convention Findings
_No issues found._
