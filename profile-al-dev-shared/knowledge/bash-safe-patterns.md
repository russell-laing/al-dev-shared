# Bash Safe Patterns

Safety rules for destructive text edits in Bash (used by commit lint/fix agents).

## Trailing-whitespace stripping

Use `[[:blank:]]+$` (horizontal whitespace only):

```bash
sed -E -i '' 's/[[:blank:]]+$//' <file>
```

- On BSD `sed`, do NOT use `[ \t]+$` / `[ \t]*$` — `\t` is a literal `t` and can
  strip terminal `t` characters.
- Never use `[[:space:]]+$` or `\s+$` — those include `\n` and collapse the whole
  file onto one line.

## Backtick Command Substitution Hazard

Backticks inside double-quoted strings can break interpolation and cause unintended variable expansion or command execution.

### ❌ Unsafe Pattern

```bash
message="The current directory is `pwd` and user is `whoami`"
```

**Problem:** Backticks trigger command substitution even inside double quotes, making the string vulnerable to:

- Unexpected variable expansion (`$HOME` is expanded)
- Command injection if the string contains user input
- Syntax errors if the substituted output contains special characters

### ✅ Safe Pattern

Use `$()` syntax instead (modern POSIX, always quoted):

```bash
message="The current directory is $(pwd) and user is $(whoami)"
```

Or avoid dynamic substitution in the string:

```bash
cwd=$(pwd)
user=$(whoami)
message="The current directory is $cwd and user is $user"
```

### When This Matters in Plans

If a plan task says:

- "Run this command: `echo \"$(git log ...)\"`" → Safe (uses `$()`)
- "Run this command: `echo \"\`git log\`\"`" → Unsafe (uses backticks)

Always prefer `$()` over backticks in bash examples, especially in plan documentation where users might copy-paste commands directly.
