# Fix Compile Output Handling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate piping of `al-compile` output to terminal viewers, preventing 4.7MB+ context bloat and forced session compacts.

**Architecture:** Three-part fix: (1) update compile-lint-procedure.md with explicit anti-patterns and Bash description requirements, (2) add compile-output safeguards to developer agent system prompt, (3) add output-suppression guidance to knowledge base for future reference.

**Tech Stack:** Markdown documentation, AL compiler (`al-compile`), Bash tool descriptions.

---

## File Structure

```
profile-al-dev-shared/
  knowledge/
    compile-lint-procedure.md          [UPDATE: add "Anti-Patterns" section]
  agents/
    al-dev-developer.md                [UPDATE: add safeguard to system prompt]
  markdown/
    compile-output-best-practices.md   [CREATE: reference guide for agents]
```

---

## Task 1: Document Anti-Patterns in compile-lint-procedure.md

**Files:**
- Modify: `profile-al-dev-shared/knowledge/compile-lint-procedure.md:70-95`

**Context:** The current procedure file shows the *correct* way to run compile commands, but doesn't explicitly warn against piping output to terminal viewers. Developers following the procedures don't know that `al-compile --output FILE 2>&1 | head -20` violates the anti-pattern.

- [ ] **Step 1: Read the current compile-lint-procedure.md**

Already read above. Current Step 1 (Compile, lines 52–99) shows correct usage but no anti-patterns section.

- [ ] **Step 2: Insert anti-patterns section after Step 1 compile block**

Add this section between line 99 (end of "al-compile Command Options") and line 101 (start of Step 2):

```markdown
### ⚠️ Anti-Patterns: What NOT to Do

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
- Result: forced context compacts and session restarts after 2–3 compile checks

**✅ DO: Write to file, then inspect via Read or grep the file if needed:**

```bash
# CORRECT — write diagnostics to file, suppress stdout
al-compile --output .dev/compile-errors.log

# If you need to inspect a subset of errors:
grep -E "error|warning" .dev/compile-errors.log | grep -E "\.(Page|PageExt)\.al"

# If you need a summary count:
grep -c '^Error' .dev/compile-errors.log
```

**Always include a `description` parameter on Bash tool calls invoking `al-compile`:**

The description helps the harness track intent (logging vs. inspection) and prevents re-reading large log files:

```json
{
  "tool": "Bash",
  "input": {
    "command": "al-compile --output .dev/compile-errors.log",
    "description": "Compile AL project and write results to log file"
  }
}
```
```

- [ ] **Step 3: Verify the section is placed correctly**

The new section should appear after line 99 (end of "al-compile Command Options and Output Format") and before line 101 (start of Step 2 — Spawn diagnostics-fixer).

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/compile-lint-procedure.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add anti-patterns section to compile-lint-procedure

Document piping compile output to terminal viewers as harmful anti-pattern.
Show correct approach: write to file without pipes, inspect via Read or file grep.
Include guidance on Bash tool description parameter for intent tracking.

Fixes context bloat issue from 4.7MB compile logs being captured in session context."
```

---

## Task 2: Add Compile Output Safeguard to al-dev-developer Agent

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-developer.md`

**Context:** The al-dev-developer agent is spawned by skills to implement code changes. Its system prompt must explicitly prevent piping compile output, since that's where the anti-pattern violations occur in practice.

- [ ] **Step 1: Read the al-dev-developer agent file**

```bash
head -100 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
```

Identify the section covering "Compile" or "Build" behavior.

- [ ] **Step 2: Locate the compile/build section in the system prompt**

Search for keywords like "compile", "al-compile", "build", "error log" to find where the agent is instructed to run compilation.

- [ ] **Step 3: Add safeguard clause after the compile instructions**

Insert this text immediately after any instructions to run `al-compile`:

```markdown
### Compile Output — Critical Safeguard

When running `al-compile --output .dev/compile-errors.log`:

**DO:**
- Run the command without pipes: `al-compile --output .dev/compile-errors.log`
- Always include a `description` parameter on the Bash tool call (e.g., "Compile AL project and write results to log file")
- Use the Read tool to inspect the log file afterward if needed
- Use file-based grep if you need to filter results: `grep -E "pattern" .dev/compile-errors.log`

**DO NOT:**
- Pipe output to terminal viewers: `al-compile ... 2>&1 | head/tail/grep` ❌
- Omit the `description` parameter on Bash calls
- Run `al-compile` without the `--output` flag (unless explicitly verifying stderr capture)

**Why:** Piping compile output causes the entire log (4.7MB+) to be captured in session context, triggering context compacts and session restarts. The `--output` flag already writes silently — pipes serve no functional purpose and only cause harm.
```

- [ ] **Step 4: Verify placement**

The safeguard should be in a prominent location that developers will see before running compile commands — ideally in a "Critical Safeguards" or "Build Procedures" section of the agent prompt.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-developer.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add compile output safeguard to al-dev-developer agent

Explicitly prevent piping al-compile output to terminal viewers.
Require description parameter on Bash tool calls for intent tracking.
Provide DO/DO NOT checklist and explanation of why piping is harmful.

Prevents 4.7MB+ context bloat from compile logs captured in session context."
```

---

## Task 3: Create Compile Output Best Practices Reference Guide

**Files:**
- Create: `profile-al-dev-shared/markdown/compile-output-best-practices.md`

**Context:** This creates a standalone reference guide that agents and developers can cite when reviewing or auditing code. It serves as both documentation and a checkable standard for code review.

- [ ] **Step 1: Create the file with comprehensive best practices**

```markdown
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
```

- [ ] **Step 2: Verify the file exists and has content**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/markdown/compile-output-best-practices.md
```

Expected: 250+ lines. If file is empty or missing, escalate.

- [ ] **Step 3: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/markdown/compile-output-best-practices.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add compile output best practices reference guide

Comprehensive guide for agents on preventing context bloat from piping
al-compile output. Includes decision tree, code review checklist, and
automated detection patterns.

Serves as standalone reference for auditing and future code review."
```

---

## Task 4: Update al-dev-develop Skill with Compile Safeguard Reference

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`

**Context:** The al-dev-develop skill instructs developers to run `al-compile --output .dev/compile-errors.log` ONCE (per the grep results from earlier). Add a reference to the best practices guide to ensure developers understand the constraints.

- [ ] **Step 1: Read the al-dev-develop skill to find the compile section**

```bash
grep -n "al-compile\|compile-lint-procedure" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected output shows lines 432-434 mention compile. Read those lines in context.

- [ ] **Step 2: Locate the exact compile instruction in the skill**

Read lines 430-440 of the skill to see the full context around the compile instruction.

- [ ] **Step 3: Add reference after the compile instruction**

After the line "When code is complete, run `al-compile --output .dev/compile-errors.log` ONCE", add:

```markdown
(See `markdown/compile-output-best-practices.md` for critical safeguards on compile output handling — never pipe to terminal viewers.)
```

- [ ] **Step 4: Verify the reference is clear and helpful**

The reference should be short but point developers to the full guidance without cluttering the skill.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-develop/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add compile best practices reference to al-dev-develop skill

Point developers to compile-output-best-practices.md when running compile.
Ensures developers know the safeguards against piping compile output."
```

---

## Task 5: Update al-dev-fix Skill with Compile Safeguard Reference

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`

**Context:** The al-dev-fix skill also references compile procedures. Add the same safeguard reference.

- [ ] **Step 1: Find the compile reference in al-dev-fix skill**

```bash
grep -n "al-compile\|compile-lint-procedure" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

- [ ] **Step 2: Locate the context around the reference**

Read the lines surrounding the grep result to understand where the compile instruction appears.

- [ ] **Step 3: Add reference after the compile instruction**

Add the same reference as in Task 4:

```markdown
(See `markdown/compile-output-best-practices.md` for critical safeguards on compile output handling — never pipe to terminal viewers.)
```

- [ ] **Step 4: Verify the reference is clear**

The reference should match the wording from Task 4 for consistency.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-fix/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add compile best practices reference to al-dev-fix skill

Point developers to compile-output-best-practices.md when running compile.
Consistent with al-dev-develop skill update."
```

---

## Task 6: Update al-dev-lint Skill with Compile Safeguard Reference

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-lint/SKILL.md`

**Context:** The al-dev-lint skill also references compile procedures. Add the same safeguard reference for consistency across all compile-invoking skills.

- [ ] **Step 1: Find the compile reference in al-dev-lint skill**

```bash
grep -n "al-compile\|compile-lint-procedure" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-lint/SKILL.md
```

- [ ] **Step 2: Locate the context around the reference**

Read the lines surrounding the grep result.

- [ ] **Step 3: Add reference after the compile instruction**

Add the same reference as in Task 4:

```markdown
(See `markdown/compile-output-best-practices.md` for critical safeguards on compile output handling — never pipe to terminal viewers.)
```

- [ ] **Step 4: Verify the reference is consistent**

Should match the wording from Tasks 4 and 5.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-lint/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add compile best practices reference to al-dev-lint skill

Point developers to compile-output-best-practices.md when running compile.
Consistent with al-dev-develop and al-dev-fix skill updates."
```

---

## Task 7: Verification and Final Commit Count

**Files:**
- Verify: All files from Tasks 1–6

- [ ] **Step 1: Check git status**

```bash
git -C /Users/russelllaing/al-dev-shared status
```

Expected: 6 modified files (compile-lint-procedure.md, al-dev-developer.md, al-dev-develop.md, al-dev-fix.md, al-dev-lint.md) and 1 new file (compile-output-best-practices.md).

- [ ] **Step 2: Verify line counts are reasonable**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/compile-lint-procedure.md \
       /Users/russelllaing/al-dev-shared/profile-al-dev-shared/markdown/compile-output-best-practices.md
```

Expected: compile-lint-procedure.md should increase by ~40 lines (anti-patterns section), compile-output-best-practices.md should be ~280+ lines.

- [ ] **Step 3: Verify no forbidden patterns in changed files**

```bash
# Check for unrendered date placeholders
grep -E "\[2026-05-" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/compile-lint-procedure.md /Users/russelllaing/al-dev-shared/profile-al-dev-shared/markdown/compile-output-best-practices.md

# Check for TODO/TBD
grep -i "TODO\|TBD" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/compile-lint-procedure.md /Users/russelllaing/al-dev-shared/profile-al-dev-shared/markdown/compile-output-best-practices.md

# Check for harness-specific tokens
grep -E "claude:|copilot:|codex:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/compile-lint-procedure.md /Users/russelllaing/al-dev-shared/profile-al-dev-shared/markdown/compile-output-best-practices.md
```

Expected: No output (no forbidden patterns found).

- [ ] **Step 4: Verify commit count**

```bash
git -C /Users/russelllaing/al-dev-shared log --oneline -6
```

Expected: 6 commits (one per task) in order: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6.

- [ ] **Step 5: Final verification summary**

```
All changes verified:
✅ compile-lint-procedure.md: Anti-patterns section added
✅ al-dev-developer.md: Compile output safeguard added
✅ compile-output-best-practices.md: New reference guide created
✅ al-dev-develop.md: Best practices reference added
✅ al-dev-fix.md: Best practices reference added
✅ al-dev-lint.md: Best practices reference added
✅ 6 atomic commits created
✅ No forbidden patterns detected
```

---

## Implementation Notes

- **Bash descriptions:** The plan assumes Bash tool calls are made by subagents. The safeguards in Task 2 (al-dev-developer agent) explicitly instruct the agent to include `description` parameters. When reviewing actual Bash calls during execution, verify this is being followed.

- **Knowledge file updates:** All changes to `knowledge/` directory are harness-neutral (no claude:/copilot:/codex: prefixes). The `compile-output-best-practices.md` file can be referenced in code reviews and audits across all three harnesses.

- **Skill consistency:** Tasks 4–6 add identical references to three skills for consistency. If additional skills invoke compile in the future, this reference should be added to those as well.

- **Future safeguards:** Consider extending this pattern to other large-output commands (grep, find) that could benefit from piping suppression guidance.

---

**Commit Summary:**

- Task 1: docs: add anti-patterns section to compile-lint-procedure
- Task 2: docs: add compile output safeguard to al-dev-developer agent
- Task 3: docs: add compile output best practices reference guide
- Task 4: docs: add compile best practices reference to al-dev-develop skill
- Task 5: docs: add compile best practices reference to al-dev-fix skill
- Task 6: docs: add compile best practices reference to al-dev-lint skill
- Task 7: Verification (no commit, just checks)

**Total commits expected:** 6
