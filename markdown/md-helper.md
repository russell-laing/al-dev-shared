---
applyTo: "**/*.md"
---

# Markdown Style Guide

## General Rules

- Line length: under 80 characters
- Semantic line breaks: one idea per line
- No trailing spaces at line ends
- End files with exactly one newline character

## Critical Lint Rules

| Rule | Requirement |
| --- | --- |
| MD009 | No trailing spaces |
| MD022 | Blank lines before and after headings |
| MD031 | Blank lines before and after code blocks |
| MD032 | Blank lines before and after lists |
| MD040 | Always specify language for code blocks |
| MD029 | Use `1.` for all ordered list items |
| MD047 | End files with exactly one newline |

## Suppressed Rules

- **MD024**: Duplicate headings allowed (avoid when possible)
- **MD041**: Content before first heading allowed
- **MD033**: HTML allowed when necessary

## Code Block Language Tags

- `al` — AL language
- `json` — JSON/config
- `text` — plain text
- `markdown` — markdown examples
- `bash` — shell commands
- `powershell` — PowerShell
- `yaml` — YAML
- `xml` — XML
- `sql` — SQL
- `css` — CSS

## Tables

- Use only for truly tabular data
- Include header rows
- Use consistent column widths

## Blockquotes

- Include blank lines before and after
- Use `>` at start of each line

## Callouts

Use emoji + blockquote format:

```markdown
> ⚠️ **Warning**
>
> Warning message.
```

## Horizontal Rules

- Use `---` with blank lines before and after
- Use sparingly

## Mermaid Diagrams

For mermaid diagrams, follow `markdown/md-mermaid-helper.md`.

## Headings

- One H1 per document
- Make headings unique — prefix with parent context if similar
  structure repeats
- Use action-oriented headings for procedures
- Avoid vague headings (Setup, Issues, Miscellaneous)

## AL Documentation Guidelines

- Use `al` language tag for all AL code blocks
- Include XML doc comments (`/// <summary>`) in examples
- Show complete object declarations with object IDs
- Use proper access modifiers (`internal`, `local`)
- Use realistic field names and business scenarios
