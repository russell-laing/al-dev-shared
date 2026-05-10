# Compile + Lint Procedure

Standard AL compile and lint-fix pass used by `al-dev-lint`,
`al-dev-develop`, and `al-dev-fix`.

## Step 1 — Compile

Ensure output directory exists:

```bash
mkdir -p .dev
```

Run:

```bash
if command -v al-compile &>/dev/null; then
  al-compile --output .dev/compile-errors.log
else
  al compile /project:. /packagecachepath:.alpackages \
    /errorlog:.dev/compile-errors.log
fi
```

If the log is absent, empty, or contains no `Warning` or `Error`
lines, report clean and stop.

## Step 2 — Spawn diagnostics-fixer

If compile errors were found, spawn `al-dev-developer` to fix
them first, re-compile, then continue.

If only warnings remain after a clean compile, spawn
`al-dev-diagnostics-fixer`:

```text
Read .dev/compile-errors.log and knowledge/al-linting-rules.md.
Fix all auto-fixable lint warnings and errors in the AL source
files. Write .dev/lint-report.md with a fixed/unresolved summary
structured as:
- Fixed (scripted): rules fixed via Python script with count
- Fixed (direct): rules fixed via Edit tool with file:line refs
- Unresolved: rules requiring human judgment with reason
- Compile Status: post-fix compile result
```

## Step 3 — Report

Surface the lint-report location and unresolved items to the
caller. The caller decides whether to gate on unresolved items.
