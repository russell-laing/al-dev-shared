# Compile + Lint Procedure

Standard AL compile and lint-fix pass used by `al-dev-lint`,
`al-dev-develop`, and `al-dev-fix`.

## Step 0 — Log Freshness Check

**Never trust an existing compile log.** Before reading or acting on
`.dev/compile-errors.log`, verify it is not stale:

```bash
LOG=".dev/compile-errors.log"
if [[ -f "$LOG" ]]; then
  NEWEST_AL=$(find . -name "*.al" -newer "$LOG" 2>/dev/null | head -1)
  if [[ -n "$NEWEST_AL" ]]; then
    echo "⚠️  Log is stale — .al files modified since last compile. Deleting stale log."
    rm -f "$LOG"
  else
    echo "Log appears current (no .al files newer than log)."
  fi
fi
```

If any `.al` file is newer than the log, delete the old log and proceed
to Step 1 to compile fresh.

**Claiming "only pre-existing warnings" is only valid if the log was
produced AFTER the most recent edit.** If the log predates recent changes,
it is evidence of the previous state, not the current one.

### Optional: Baseline + Diff for Edit Sessions

When modifying existing AL files (not creating new ones), capturing a
baseline before editing lets you show exactly which diagnostics are new:

```bash
# 1. Before any edits — capture baseline
al-compile --output .dev/compile-baseline.log 2>/dev/null || true

# 2. After edits — compile and diff
al-compile --output .dev/compile-errors.log
diff .dev/compile-baseline.log .dev/compile-errors.log | rg '^[<>]'
```

Lines prefixed `>` are new diagnostics introduced by your edits.
Lines prefixed `<` are diagnostics your edits resolved.

**Only claim success if the diff shows zero new `Error` lines.**
New `Warning` lines introduced by your edits must be acknowledged
(even if the compile is technically clean).

> **⛔ Never mutate the working tree to manufacture a baseline.**
> Do not use `git stash` / `git stash pop` / `git reset` (or `git checkout`)
> to isolate a baseline compile. These commands can fail on untracked or
> binary files and tempt a destructive recovery (`git reset --hard`) that
> permanently erases staged and unstaged work. The baseline must be captured
> by writing `.dev/compile-baseline.log` **before the session's first edit**
> and diffing it against the current `.dev/compile-errors.log` (the mechanism
> shown above). If no pre-edit baseline was captured, do **not** create one by
> changing the working tree — compile the current state and report all
> diagnostics as-is.

## Step 1 — Compile

Ensure output directory exists:

```bash
mkdir -p .dev
```

Run:

```bash
if command -v al-compile &>/dev/null; then
  al-compile --output .dev/compile-errors.log
elif command -v al &>/dev/null; then
  al compile /project:. /packagecachepath:.alpackages \
    /errorlog:.dev/compile-errors.log
else
  echo "AL compiler not found; install al-compile or AL CLI tools before retrying." \
    | tee .dev/compile-errors.log
fi
```

If the log is absent, empty, or contains no `Warning` or `Error`
lines, treat that as incomplete evidence. A missing log is not a clean
compile; re-run Step 1 and only report clean after a current log exists
and contains no warnings or errors.

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

### ⚠️ Anti-Patterns: What NOT to Do

These mistakes are dangerous because they look harmless in the terminal while
quietly expanding the captured session payload.
Avoid them even when you only want a quick glance at compile output.

**❌ DO NOT pipe `al-compile` output to terminal viewers:**

```bash
# WRONG — pipes full compile output through head/tail
al-compile --output .dev/compile-errors.log 2>&1 | head -20
al-compile --output .dev/compile-errors.log 2>&1 | tail -15

# WRONG — pipes through grep without file capture
al-compile 2>&1 | grep -E "(error|warning)"
```

**Why this is harmful:**

- The `--output` flag already writes diagnostics silently to file
- Piping to `head/tail/grep` causes the **entire stdout to be captured in session context** (4.7MB+ for this codebase)
- Terminal viewers only display first/last N lines to user ✓, but the Bash tool captures the entire output ✗
- The safer pattern is: write to file first, then inspect the file with a
  targeted reader or filtered follow-up command.
- This keeps compile evidence durable without flooding the active session.
- Result: forced context compacts and session restarts after 2–3 compile checks

**✅ DO: Write to file, then inspect the file directly or filter it with `rg` if needed:**

```bash
# CORRECT — write diagnostics to file, suppress stdout
al-compile --output .dev/compile-errors.log

# If you need to inspect a subset of errors:
rg -n -e "error|warning" .dev/compile-errors.log | rg '\.(Page|PageExt)\.al'

# If you need a summary count:
rg -c '^Error' .dev/compile-errors.log
```

**Always include a short purpose note on tool calls invoking `al-compile`:**

Use a description that clearly states whether the call is compiling,
inspecting, or diffing the log, for example:

```text
Compile AL project and write results to log file
```

### Session Reporting Rule

After parsing `.dev/compile-errors.log`, summarize the result
instead of replaying raw log lines into the session.

Required summary fields:

- `Errors:` count
- `Warnings:` count
- `Representative diagnostics:` up to 3
- `Files affected:` unique file list
- `Detailed log:` `.dev/compile-errors.log`

Do not use `tail`, `head`, or bulk `cat` output as a status
update.

### Error Log Parsing Procedures

Parse `.dev/compile-errors.log` to separate actionable items from noise:

1. **Count errors and warnings separately:**

   ```bash
   rg -c '^Error' .dev/compile-errors.log   # must be 0 before merging
   rg -c '^Warning' .dev/compile-errors.log  # drive lint-fix pass
   ```

2. **Extract file and line references** for each diagnostic using the bracketed suffix
   `[<file>(<line>,<col>)]`. Feed these coordinates directly to the active file-editing capability —
   do not search the file free-text for the error message.
3. **Group by AL code** (e.g. `AL0118`, `AA0231`) before fixing. All instances of the
   same rule can usually be fixed with a single strategy, reducing re-reads.
4. **Re-compile after every fix batch** to confirm the count is decreasing and no new
   diagnostics were introduced.

Example parse pipeline:

```bash
rg '^Error' .dev/compile-errors.log | sed 's/.*\[\(.*\)\]/\1/' | sort -u
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

**Note:** `al-dev-commit` must consume this procedure before any commit orchestration begins.

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

## Step 2 — Spawn diagnostics-resolver

If compile errors were found, spawn `al-dev-fix` to fix them first,
re-compile, then continue.

If only warnings remain after a clean compile, spawn
`al-dev-diagnostics-resolver`:

```text
Dispatch agent: al-dev-shared:al-dev-diagnostics-resolver
  description: "Resolve auto-fixable diagnostics from the current compile log"
  prompt: |
    Read `.dev/compile-errors.log` and `knowledge/al-linting-rules.md`.
    Fix all auto-fixable lint warnings and errors in the AL source files.
    Write `.dev/lint-report.md` with a fixed/unresolved summary structured as:
    - Fixed (scripted): rules fixed via Python script with count
    - Fixed (direct): rules fixed via direct file edits with file:line refs
    - Unresolved: rules requiring human judgment with reason
    - Compile Status: post-fix compile result
```

## Step 3 — Report

Surface the lint-report location and unresolved items to the
caller. The caller decides whether to gate on unresolved items.
