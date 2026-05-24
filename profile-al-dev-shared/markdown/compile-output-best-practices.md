---
title: Compile Output & Context Management Best Practices
---

# Compile Output & Context Management Best Practices

## Summary

Piping `al-compile` output to terminal viewers (`head`, `tail`, `grep`) causes entire compile logs (4.7MB+) to be captured in session context, triggering forced context compacts and session restarts. This guide documents the correct approach.

## The Problem

### What Happens

```bash
# Command runs silently to file:
al-compile --output .dev/compile-errors.log

# Piping to a terminal viewer:
al-compile --output .dev/compile-errors.log 2>&1 | head -20
#                                                    ↑
#                                          Captures entire stdout
```

**Result:**
1. User sees first 20 lines on terminal ✓
2. Bash tool captures entire stdout in session context ✗ (4.7MB)
3. Session context grows 4.7MB per compile check
4. After 2–3 compiles, harness triggers context compact
5. Forced session restart, lost state

### Why This Happens

- The `al-compile` command writes a **single large JSON file** (4.7MB) to disk
- Without piping, this file stays on disk, no stdout in context
- Piping to `head/tail/grep` sends the entire JSON through the pipe
- The Bash tool captures all of stdout (not just what `head` displays)
- Harness treats the 4.7MB stdout as part of session context
- No way to exclude it post-capture

## The Solution

### Rule 1: Never Pipe al-compile Output

```bash
# ❌ WRONG
al-compile --output .dev/compile-errors.log 2>&1 | head -20
al-compile --output .dev/compile-errors.log 2>&1 | tail -15
al-compile 2>&1 | grep -E "(error|warning)"

# ✅ CORRECT
al-compile --output .dev/compile-errors.log
```

**Rationale:**
- The `--output` flag already writes diagnostics silently to a file
- No terminal display needed — the file is the output
- User/agent can inspect the file afterward via Read tool or file-based grep
- Zero stdout captured in session context

### Rule 2: Always Provide Description on Bash Compile Calls

```json
{
  "tool": "Bash",
  "input": {
    "command": "al-compile --output .dev/compile-errors.log",
    "description": "Compile AL project and write results to log file"
  }
}
```

**Rationale:**
- The `description` parameter tells the harness this is a logging operation (file capture)
- Without description, harness may re-read the log file for validation, loading it into context
- Short description prevents context bloat from validation re-reads

### Rule 3: Inspect Compile Results via File Operations

If you need to see compile results:

```bash
# ✅ CORRECT — Read the file
# (Use Read tool in Claude Code, or bash cat for inspection)

# ✅ CORRECT — Filter with file-based grep
grep -E "^Error" .dev/compile-errors.log
grep -E "error|warning" .dev/compile-errors.log | grep -E "\.(Page|PageExt)\.al"

# ❌ WRONG — Pipe through grep (same as piping al-compile)
al-compile 2>&1 | grep -E "error|warning"
```

### Rule 4: Count and Summarize Without Piping

```bash
# ✅ CORRECT — Count via file grep
grep -c '^Error' .dev/compile-errors.log
grep -c '^Warning' .dev/compile-errors.log

# ❌ WRONG
al-compile 2>&1 | grep -c '^Error'
```

## Decision Tree: When to Use What

```
Does your command write to a file (--output flag)?
  ├─ YES → Do NOT pipe. Use --output only.
  │         Example: al-compile --output .dev/compile-errors.log
  │
  └─ NO → If output is large, consider capturing to file first.
          Example: command > .dev/output.log 2>&1
              Then inspect via Read tool or file grep.
```

## Checking for Violations

### Code Review Checklist

When reviewing code or agent prompts, flag any of these patterns:

- [ ] `al-compile ... 2>&1 | head/tail` — **Remove pipe**
- [ ] `al-compile ... 2>&1 | grep` — **Compile to file, then grep file**
- [ ] `al-compile` without `--output` — **Add `--output .dev/compile-errors.log`**
- [ ] Bash tool call with compile command but no `description` parameter — **Add description**

### Automated Detection

Search codebase for violations:

```bash
# Find al-compile commands with pipes
grep -r "al-compile.*|" profile-al-dev-shared/ --include="*.md"

# Find Bash calls without description (requires JSONL/transcript review)
grep "al-compile" .dev/*.jsonl | grep -v "description"
```

## Related Patterns

### Pattern A: Large Grep Output

Other commands that produce large outputs should also avoid piping:

```bash
# ❌ WRONG — large grep output piped through head
grep -r "search-term" . --include="*.al" | head -50

# ✅ CORRECT — capture to file, then inspect
grep -r "search-term" . --include="*.al" > .dev/search-results.log
# User reviews .dev/search-results.log
```

### Pattern B: Multi-Step Filtering

If you need to filter compile results (e.g., only Page-related warnings):

```bash
# Step 1: Compile (no pipes)
al-compile --output .dev/compile-errors.log

# Step 2: Filter the file (no pipes through compile output)
grep -E "warning|error" .dev/compile-errors.log | grep -E "\.(Page|PageExt)\.al" > .dev/page-warnings.log

# Step 3: Inspect via Read tool
# (Read tool displays page-warnings.log contents)
```

## Summary

| Action | Safe? | Context Cost | Notes |
|--------|-------|--------------|-------|
| `al-compile --output FILE` | ✅ | ~0KB | File stays on disk, no stdout |
| `al-compile --output FILE \| head` | ❌ | 4.7MB | Entire output in context |
| `al-compile --output FILE \| grep` | ❌ | 4.7MB | Entire output captured |
| `grep FILE` (file-based) | ✅ | 0KB | Only grep results in stdout |
| `command > FILE` + Read | ✅ | ~0KB | File on disk, Read opens it separately |

---

**Last Updated:** 2026-05-24
**Related:** `knowledge/compile-lint-procedure.md`, `knowledge/agent-tool-projection-policy.md`
