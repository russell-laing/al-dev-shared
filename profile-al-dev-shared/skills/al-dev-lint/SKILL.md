---
name: al-dev-lint
description: Run AL compile and auto-fix AL code diagnostics.
argument-hint: "[optional: path to existing compile-errors.log]"
---

# Skill: /al-dev-lint

Run a lint-fix pass against the current AL project. No approval gate.

## Intent Preflight

Before compiling, fixing diagnostics, or writing a lint report, apply `knowledge/intent-preflight.md`.

Default intent for this skill is `EDIT`. If the request is review-only, explanation-only, or asks to assess diagnostics without changing files, stop and ask the intent-mismatch prompt from `knowledge/intent-preflight.md` before any mutating action.

## Step 1: Compile (if needed)

Ensure output directory exists:

```bash
mkdir -p .dev
```

If `$ARGUMENTS` is provided and points to an existing log file, copy it:

```bash
cp "$ARGUMENTS" .dev/compile-errors.log
```

Otherwise run:

```bash
if command -v al-compile &>/dev/null; then
  al-compile --output .dev/compile-errors.log
else
  al compile /project:. /packagecachepath:.alpackages \
    /errorlog:.dev/compile-errors.log
fi
```

**Note:** Use `al-compile` if available (preferred—faster and simpler). If `al-compile` is not in PATH, fall back to `al compile`. Both produce the same output log format.

(See `markdown/compile-output-best-practices.md` for critical safeguards on compile output handling — never pipe to terminal viewers.)

If the log is absent, empty, or contains no lines matching
`Warning` or `Error`:

```text
✅ No lint issues found. Compile clean.
```

Stop here.

## Step 2: Spawn diagnostics-fixer

Spawn `al-dev-diagnostics-fixer`:

```text
Read .dev/compile-errors.log and knowledge/al-linting-rules.md.
Fix all auto-fixable lint warnings and errors in the AL source files.
Write `.dev/$(date +%Y-%m-%d)-al-dev-lint-lint-report.md` with a
fixed/unresolved summary structured as:
- Fixed (scripted): rules fixed via Python script with occurrence count
- Fixed (direct): rules fixed via Edit tool with file:line references
- Unresolved: rules requiring human judgment with reason
- Compile Status: post-fix compile result
```

## Step 3: Present summary

```text
Lint pass complete

Fixed (scripted):   N rules, M occurrences
Fixed (direct):     N rules, M occurrences
Unresolved:         N issues requiring judgment

Compile status: [✅ Clean / ⚠️ N warnings / ❌ N errors]
Full report → `.dev/$(date +%Y-%m-%d)-al-dev-lint-lint-report.md`
```

If unresolved items exist, list them inline:

```text
Unresolved items needing input:
- AS0016 (DataClassification): src/Tables/Price.al:10,22,38
  → Choose a DataClassification value and apply manually
- PTE0001 (Object ID range): src/Codeunits/Mgt.al:1
  → Assign an ID in range 50901–50950
```
