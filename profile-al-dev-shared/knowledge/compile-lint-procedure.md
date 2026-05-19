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

### al-compile Command Options and Output Format

`al-compile` is a wrapper around the AL Language compiler. Key options:

- `--output <path>` — write diagnostics to the specified log file instead of stdout.
  Default path when omitted is stdout only; always supply `--output .dev/compile-errors.log`
  so downstream steps can parse a stable file.
- `--packagecachepath <path>` — override the `.alpackages` symbol cache directory.
  Needed when symbols live outside the project root.
- `--project <path>` — compile a project at a path other than the current directory.

Output format (one diagnostic per line):

```text
<severity> AL<code>: <message> [<file>(<line>,<col>)]
```

Example:

```text
Error AL0118: The name 'MyField' does not exist in the current context [src/MyCodeunit.al(42,5)]
Warning AA0231: Replace Error(StrSubstNo(...)) with Error(label, args) [src/MyCodeunit.al(58,3)]
```

The severity token is always one of `Error`, `Warning`, or `Info`.
An empty log (zero bytes or no `Error`/`Warning` lines) means a clean compile.

### Error Log Parsing Procedures

Parse `.dev/compile-errors.log` to separate actionable items from noise:

1. **Count errors and warnings separately:**

   ```bash
   grep -c '^Error' .dev/compile-errors.log   # must be 0 before merging
   grep -c '^Warning' .dev/compile-errors.log  # drive lint-fix pass
   ```

2. **Extract file and line references** for each diagnostic using the bracketed suffix
   `[<file>(<line>,<col>)]`. Feed these coordinates directly to the Edit tool —
   do not search the file free-text for the error message.
3. **Group by AL code** (e.g. `AL0118`, `AA0231`) before fixing. All instances of the
   same rule can usually be fixed with a single strategy, reducing re-reads.
4. **Re-compile after every fix batch** to confirm the count is decreasing and no new
   diagnostics were introduced.

Example parse pipeline:

```bash
grep '^Error' .dev/compile-errors.log | sed 's/.*\[\(.*\)\]/\1/' | sort -u
```

This extracts unique `file(line,col)` locations for all errors.

### Diagnostic Categorization Rules

Diagnostics fall into three categories that drive different responses:

| Category | Prefix pattern | Action |
|----------|---------------|--------|
| **Compile errors** | `Error AL0xxx` | Must fix before anything else; block all subsequent steps |
| **Lint warnings** | `Warning AA0xxx` | Fix in the lint pass; do not block compile-clean report |
| **Info / hints** | `Info AL0xxx` | Log only; never block or auto-fix |

**AA-code families worth knowing:**

- `AA0005–AA0099` — naming and casing conventions (auto-fixable)
- `AA0100–AA0199` — deprecated or obsolete usage (fix or suppress with justification)
- `AA0200–AA0231` — code quality rules, e.g. AA0231 (Error label) is always auto-fixable
- `AA0400+` — complexity and maintainability; requires human judgment

Treat any `Error AL0` diagnostic as a hard blocker. Treat `Warning AA0` diagnostics
as required work but not a compilation blocker. Never escalate `Info` items to the
caller — filter them out of the lint report.

### Auto-Fix Applicability Criteria

Not every diagnostic can be safely fixed by a script or the Edit tool. Use these
criteria to decide whether to auto-fix or escalate to human review:

**Auto-fix (safe to apply without review):**

- The fix is a pure textual substitution with no semantic change — e.g., renaming
  a variable to match casing convention, adding `DataClassification` to a field
  that currently has none, or replacing `Error(StrSubstNo(...))` with a label.
- The AL rule defines exactly one correct form and no alternatives.
- The fix does not alter control flow, data types, or public procedure signatures.

**Direct edit (fix but flag in report):**

- The fix requires understanding context beyond the flagged line — e.g., selecting
  the right `ApplicationArea` from a set of valid values.
- The fix changes a public interface (procedure name, parameter list) that callers
  may reference.

**Human judgment required (log as Unresolved):**

- The diagnostic is in the `AA0400+` complexity family.
- The rule has multiple valid resolutions and the correct one depends on business logic.
- The auto-fix would change behavior (e.g., removing a fallback that looks redundant
  but handles a real edge case).

Example of an auto-fixable diagnostic:

```text
Warning AA0231: Replace Error(StrSubstNo('Item %1 not found', ItemNo))
                with Error(ItemNotFoundErr, ItemNo) [src/ItemMgt.al(33,5)]
```

This is a pure label substitution; apply it without asking.

Example of a human-judgment diagnostic:

```text
Warning AA0462: The procedure 'ProcessOrder' is too long (62 statements)
                [src/OrderMgt.al(10,1)]
```

Splitting a long procedure requires understanding intent; log as Unresolved.

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
