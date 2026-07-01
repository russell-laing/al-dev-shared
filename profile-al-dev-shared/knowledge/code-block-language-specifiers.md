# Code Block Language Specifiers

## Requirement

All markdown code blocks must include a language specifier immediately after the opening triple backticks (```). Language specifiers improve readability, enable syntax highlighting, and prevent ambiguity about block content.

## Pattern

**Bare code block (❌ Not allowed):**

```
```

echo "Hello"

```
```

**With language specifier (✅ Correct):**

```bash
echo "Hello"
```

```

## Supported Language Specifiers

Use the appropriate specifier based on content:

| Language | Specifier | When to Use |
|----------|-----------|------------|
| Bash/Shell | `bash` | Shell scripts, command sequences |
| YAML | `yaml` | Configuration files, fixtures, structured data |
| Python | `python` | Python scripts, helper code |
| JavaScript | `javascript` | JavaScript/TypeScript code |
| Markdown | `markdown` | Markdown examples or templates |
| AL/Business Central | `al` | AL/Business Central code |
| JSON | `json` | JSON data, config, output |
| Text/Plain | `text` | Plain text output, terminal commands (no syntax highlight needed) |

## Scanning for Bare Blocks

Find all bare code blocks in a markdown file:

```bash
grep -n '^\s*```\s*$' <file.md>
```

All output lines should be zero (no bare blocks found).

## Integration in Plan Task Examples

When a plan task includes code examples in "Validate" steps or "Gotcha" warnings, add the language specifier:

**Incorrect:**

```markdown
Validate: ```
  grep "pattern" src/file.al
```

```

**Correct:**

```markdown
Validate: ```bash
  grep "pattern" src/file.al
```

```

## Friction Context

Observed in sessions: ~9 bare code blocks in plan task templates reduced readability. Added specifiers improve clarity and enable proper syntax highlighting for users.

See `solution-plan-template.md` for implementation task structure with proper code-block formatting.
