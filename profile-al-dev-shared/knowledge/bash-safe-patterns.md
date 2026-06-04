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
