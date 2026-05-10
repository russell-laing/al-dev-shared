---
name: commit-learn
description: Analyze commit semantics and learn from code review feedback.
argument-hint: "[--auto-fix] [--file=path]"
---

# Skill: /commit-learn

Analyzes incidents from `.dev/commit-integrity.log` and attempts to recover corrupted files using learned fallback strategies. Spawns a focused verifier subagent to analyze root causes and propose recovery methods.

## Usage

```bash
/commit-learn
```
Read-only mode: shows incidents and proposed recoveries without making changes.

```bash
/commit-learn --auto-fix
```
Execute recovery: restores files with fallback strategies and creates repair commits.

```bash
/commit-learn --file=path/to/file.al
```
Analyze specific file only.

## How It Works

1. **Read incidents:** Parse `.dev/commit-integrity.log` for entries marked as "CORRUPTION" or "SYNTAX_ERROR"
2. **For each incident:**
   - Skip if already fully recovered (status = RESTORED and verified)
   - Spawn **verifier subagent** with incident details
   - Verifier analyzes git history and learnings.md
   - Verifier proposes fallback strategy
   - If `--auto-fix`: execute recovery and create repair commit
3. **Update learnings:** Append successful recovery patterns to `.dev/learnings.md`

## Output (Read-Only Mode)

```
Commit Integrity Analysis
══════════════════════════════════════

Incident 1: codeunit.al
  Time: 2026-05-05T14:24:12Z
  Status: CORRUPTION | baseline: 89 lines → now: 1 line (98.9% collapse)
  Previously: RESTORED by hook

  Verifier Analysis:
    Root Cause Hypothesis: Perl regex [[:space:]]+$ strips newlines
    Pattern Found: Known pattern in learnings.md (2026-04-16)
    Proposed Fallback: Use sed with [ \t]+$ instead
    Recovery Plan: Restore from HEAD~1, re-apply with sed
    Expected Result: ✓ Syntax valid

  Next Step: Run with --auto-fix to execute recovery

Summary: 1 incident ready for recovery
```

## Output (With --auto-fix)

```
Commit Integrity Recovery
══════════════════════════════════════

Incident 1: codeunit.al
  Time: 2026-05-05T14:24:12Z
  Recovery Execution:
    ✓ Restored file to HEAD~1 (89 lines)
    ✓ Re-applied change with fallback strategy (sed)
    ✓ Validated AL syntax: OK
    ✓ Created repair commit: 🔧 fix(commit-integrity): recover codeunit.al from perl regex corruption
    ✓ Updated learnings.md with recovery record

Summary: 1 incident recovered, learnings updated
```

## Internal Workflow

**Triggered by:** `User: /commit-learn` or `/commit-learn --auto-fix`

**Calls verifier subagent with:**
- Incident file path
- Baseline/current line count
- Git history (last 3-5 commits for file)
- Current learnings.md content

**Verifier returns:**
- Root cause hypothesis
- Fallback strategy to use
- Success/failure result
- Learning record (pattern, strategy, success rate)

**Post-recovery:**
- Create repair commit with gitmoji 🔧
- Append to learnings.md:
  - Date, file, pattern matched, recovery method, success
  - Update statistics (incidents, recovered, escalations)
