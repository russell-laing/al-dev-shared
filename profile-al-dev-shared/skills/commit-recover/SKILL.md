---
name: commit-recover
description: Recover corrupted AL files flagged in `.dev/commit-integrity.log` using fallback strategies and learned patterns.
argument-hint: "[--auto-fix] [--file=path]"
---

# Skill: /commit-recover

Recovers corrupted AL files from commit integrity failures. Analyzes incidents in `.dev/commit-integrity.log` and attempts recovery using learned fallback strategies. Spawns a focused fixer subagent to analyze root causes and propose recovery methods.

## Usage

```bash
/commit-recover
```

Read-only mode: shows incidents and proposed recoveries without making changes.

```bash
/commit-recover --auto-fix
```

Execute recovery: restores files with fallback strategies and creates repair commits.

```bash
/commit-recover --file=path/to/file.al
```

Analyze specific file only.

## Steps

### Step 1: Parse the integrity log

Read `.dev/commit-integrity.log` and collect all entries marked as "CORRUPTION" or "SYNTAX_ERROR". Skip entries whose status is already RESTORED and verified (the restored file passes an AL syntax check — no errors in `.dev/compile-errors.log`).

**Integrity log format.** `.dev/commit-integrity.log` is written by the
commit-integrity pre-commit hook — one line per incident. Each entry carries a
timestamp, the affected file path, a status label, and baseline/current line
counts (see the example in Step 3). Status labels are uppercase and matched
exactly: `CORRUPTION`, `SYNTAX_ERROR`, or `RESTORED`. The file may be absent when
no integrity incident has occurred — in that case report "no incidents" and stop.
`.dev/compile-errors.log` (referenced above for the verified-restore check) is
the AL compiler error log written by `/al-dev-lint`; an empty or absent file
means no compile errors.

### Step 2: Analyze each incident with a fixer subagent

For each unresolved incident, dispatch the fixer subagent:

```text
Agent tool:
  agent: al-dev-shared:al-dev-commit-recover
  description: "Analyze incident: [file path]"

Prompt:
  "Analyze this corruption incident and propose a recovery strategy.

   Incident file path: [file path from log]
   Baseline lines: [original line count from log]
   Current lines: [wc -l output]
   Git history (last 3-5 commits for this file):
$(git log --oneline -n 5 -- <file path from log>)
   Known patterns from .dev/learnings.md: [learnings content]

   Return:
   - Root cause hypothesis
   - Matched pattern (if any) from `.dev/learnings.md`
   - Proposed fallback strategy
   - Recovery plan steps
   - Expected result after recovery"
```

### Step 3: Present analysis (read-only mode)

Display the fixer output for each incident:

```text
Commit Integrity Analysis
══════════════════════════════════════

Incident 1: codeunit.al
  Time: 2026-05-05T14:24:12Z
  Status: CORRUPTION | baseline: 89 lines → now: 1 line (98.9% collapse)
  Previously: RESTORED by hook

  Fixer Analysis:
    Root Cause Hypothesis: Perl regex [[:space:]]+$ strips newlines
    Pattern Found: Known pattern in .dev/learnings.md (2026-04-16)
    Proposed Fallback: Use sed with [ \t]+$ instead
    Recovery Plan: Restore from HEAD~1, re-apply with sed
    Expected Result: Syntax valid

  Next Step: Run with --auto-fix to execute recovery

Summary: 1 incident ready for recovery
```

If `--auto-fix` was not passed, stop here and prompt the user to re-run with `--auto-fix`.

### Step 4: Execute recovery (--auto-fix only)

For each incident approved for recovery:

1. Restore the file from `HEAD~1` using `git checkout HEAD~1 -- <file>`.
   If the restore fails (file not present in `HEAD~1` — e.g. it was first
   added in the most recent commit), do not proceed with the remaining
   sub-steps: escalate to the user with the raw git error, the file path,
   and a hint to run `git log --all -- <file>` to locate a usable ancestor
   commit.
2. Re-apply the original change using the fallback strategy (e.g., `sed` instead of `perl`)
3. Validate AL syntax
4. Create a repair commit: `fix(commit-integrity): recover <file> from <pattern>`

Display the recovery result:

```text
Commit Integrity Recovery
══════════════════════════════════════

Incident 1: codeunit.al
  Time: 2026-05-05T14:24:12Z
  Recovery Execution:
    Restored file to HEAD~1 (89 lines)
    Re-applied change with fallback strategy (sed)
    Validated AL syntax: OK
    Created repair commit: fix(commit-integrity): recover codeunit.al from perl regex corruption
    Updated .dev/learnings.md with recovery record

Summary: 1 incident recovered, learnings updated
```

### Step 5: Update learnings

Append successful recovery patterns to `.dev/learnings.md`:

- Date, file, pattern matched, recovery method, success flag
- Update running statistics (incidents, recovered, escalations)
