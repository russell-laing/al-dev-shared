---
name: quality-agent-lens-structure
description: Apply Structural Conventions lens to agent files — checks frontmatter completeness, tool canonicality, Inputs/Outputs tables, header numbering, and code block language tags. Returns a findings block.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to agent `.md` files |

## Outputs

Returns a findings block. See Output Format.

---

## Lens: Structural Conventions

Read every file path provided in the dispatch prompt. For each file, derive the
agent name from the filename (strip directory path and `.md` extension).

**Check each file for:**
- Agent filename (without `.md`) matches the `al-dev-<name>` prefix convention
- `description` field is present in YAML frontmatter and is a single sentence
- `model` field is present in YAML frontmatter
- `tools` field is present in YAML frontmatter and contains only canonical
  **source-vocabulary** capability names — the harness-neutral terms, not any
  harness's projected tool names. The canonical set is:
  <!-- canonical-tools:start -->
  `USER_GATE`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `MCP: al-mcp-server`, `MCP: bc-code-intelligence`, `MCP: microsoft-docs`
  <!-- canonical-tools:end -->
- Frontmatter contains no skill-only fields (`argument-hint`, `triggers`) that
  are invalid in agents
- `## Inputs` and `## Outputs` sections are present, or a stated reason explains
  their absence
- Phase/step headers are numbered consistently — not mixing "Phase N" and "Step N"
  in the same file
- Every code block has a language tag (`bash`, `markdown`, `python`, etc.)

**Severity rules:**
- High: missing `model` or `tools` frontmatter fields
- Medium: missing Inputs/Outputs sections, non-canonical tool names, filename not
  matching `al-dev-<name>` convention, or skill-only fields in frontmatter
- Low: numbering inconsistency or missing code block language tags

---

## Output Format

Return exactly this structure (no additional prose before or after the block):

### Structural Conventions Findings
- **[agent-name]** | [High|Medium|Low] | [observation] | [fix]

If no issues found:

### Structural Conventions Findings
_No issues found._
