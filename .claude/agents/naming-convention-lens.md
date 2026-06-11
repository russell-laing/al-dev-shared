---
name: naming-convention-lens
description: Apply the Naming Convention lens to maintainer tool files and output paths — flags any tool name or output filename that violates docs/al-dev-naming-convention.md. Returns a findings block.
model: haiku
tools: ["Read"]
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
  verb/object sets. A non-conforming skill name that is not listed in the
  `## Grandfathered exceptions` section of `docs/al-dev-naming-convention.md` is
  a **Low** finding (advisory). Treat that section as the authoritative
  grandfather set — do not hardcode names here, as the set is consolidated and
  maintained in the convention doc.

**Check output paths** named in prose instructions only — exclude YAML frontmatter
and code-block examples (Write/output targets):

- Living docs must match `al-dev-{object}-{kind}.md`.
- Dated artifacts must match `{dir}/YYYY-MM-DD-{surface}-{kind}.md` with
  `surface` in `{plugin, tooling}`.
- A documented output path that violates either pattern is a **Medium** finding.

## Severity Rules

**How a deviation maps to severity** (apply the most severe that fits):

- **High:** the name breaks an enforced (MUST) pattern — a lens-agent filename
  not matching `{design|quality}-{agent|skill}-lens-{aspect}` (and not
  `naming-convention-lens`), or a name colliding with an existing tool.
- **Medium:** a documented output path that breaks a documented output pattern.
- **Low:** the name breaks a recommended (SHOULD) pattern only — an advisory
  skill-name deviation not listed in `## Grandfathered exceptions`.

The "How a deviation maps to severity" block above is the single authoritative
severity mapping for this lens.

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Naming Convention Findings

- **[tool-or-path-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Naming Convention Findings

_No issues found._
