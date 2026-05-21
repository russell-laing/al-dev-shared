# Usage Report Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply 4 low-effort, high-impact improvements identified in the Claude Code usage report to reduce recurring friction in commit workflows, design sessions, and skill invocations.

**Architecture:** Three config/skill file edits — two to `~/.claude/CLAUDE.md` (global rules), one to `~/.claude/settings.json` (automation hook), and one to the `al-dev-plan` skill file (input validation). No new files are created; all changes are additive edits to existing files.

**Tech Stack:** Markdown (CLAUDE.md, SKILL.md), JSON (settings.json), shell (PostToolUse hook command)

**Not addressed (already implemented):** File Creation Verification — already covered in the Write-Persistence Verification section of `~/.claude/CLAUDE.md`.

---

## File Structure

- Modify: `~/.claude/CLAUDE.md` — add Commit Discipline rules + Design Presentations section
- Modify: `~/.claude/settings.json` — add PostToolUse hook for Pyright on Python files
- Modify: `/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md` — add input validation gate before Phase 1 context gathering

---

### Task 1: Add Commit Discipline Rules to CLAUDE.md

**Files:**
- Modify: `~/.claude/CLAUDE.md` (lines 9–13, Git Commit Conventions section)

**Evidence from report:** Multiple sessions showed Claude combining two approved commit groups into one commit despite explicit approval as separate units. The commit-conventions.md knowledge file covers atomicity but not the "never combine approved groups" rule.

- [ ] **Step 1: Read the file to confirm current state**

  Run: `wc -l ~/.claude/CLAUDE.md`
  Expected: 69 lines (confirms no drift since last read)

- [ ] **Step 2: Add commit discipline rules**

  Use the Edit tool with this exact change:

  Old string:
  ```
  - Always use `git -C <path>` instead of `cd <path> && git ...` to avoid approval prompts
  ```

  New string:
  ```
  - Always use `git -C <path>` instead of `cd <path> && git ...` to avoid approval prompts
  - When multiple commit groups are approved in a single session, create each as a **separate atomic commit** — never combine approved groups into one commit.
  - Verify commit count matches the plan: run `git log --oneline -n <N>` before reporting completion.
  ```

- [ ] **Step 3: Verify the edit**

  Run: `grep -A3 "git -C" ~/.claude/CLAUDE.md`
  Expected: all three bullet points visible

---

### Task 2: Add Concrete-First Design Presentations Rule to CLAUDE.md

**Files:**
- Modify: `~/.claude/CLAUDE.md` (after the AL Development section, end of file)

**Evidence from report:** "Concrete Over Abstract in Design Brainstorms" — a session noted the user found Claude's three-option presentation "too abstract" and asked for more concrete detail before deciding. Adding a standing rule to CLAUDE.md prevents this in all future design/brainstorm sessions.

- [ ] **Step 1: Append Design Presentations section**

  Use the Edit tool with this exact change:

  Old string:
  ```
  - Replace `Error(StrSubstNo(...))` with `Error(label, args)` to satisfy AA0231
  ```

  New string:
  ```
  - Replace `Error(StrSubstNo(...))` with `Error(label, args)` to satisfy AA0231

  ## Design Presentations

  When presenting design options or architectural choices:
  - Include a 3-5 line concrete sketch per option (code snippet, file structure, or example command).
  - State what changes vs. the status quo for each option.
  - State one specific tradeoff per option.
  Skip abstract philosophy — show the artifact, then explain it.
  ```

- [ ] **Step 2: Verify the edit**

  Run: `tail -12 ~/.claude/CLAUDE.md`
  Expected: the new section is visible with the heading and 3 bullet points

---

### Task 3: Add Pyright PostToolUse Hook to settings.json

**Files:**
- Modify: `~/.claude/settings.json`

**Evidence from report:** "Implementer subagent introduced Pyright type errors and whitespace issues requiring a second cleanup commit." The `pyright-lsp` plugin is already enabled, confirming Pyright is available at `/opt/homebrew/bin/pyright`. A PostToolUse hook auto-runs it after Python file edits so errors surface immediately.

- [ ] **Step 1: Read the file to confirm current state**

  Run: `python3 -c "import json; d=json.load(open('/Users/russelllaing/.claude/settings.json')); print('hooks' in d)"`
  Expected: `False` (no hooks key yet)

- [ ] **Step 2: Add hooks key to settings.json**

  Use the Edit tool with this exact change:

  Old string:
  ```
    "verbose": false
  }
  ```

  New string:
  ```
    "verbose": false,
    "hooks": {
      "PostToolUse": [
        {
          "matcher": "Edit|Write",
          "hooks": [
            {
              "type": "command",
              "command": "if [[ \"$CLAUDE_FILE_PATHS\" == *.py ]]; then /opt/homebrew/bin/pyright \"$CLAUDE_FILE_PATHS\" 2>&1 | head -20; fi"
            }
          ]
        }
      ]
    }
  }
  ```

- [ ] **Step 3: Verify JSON is valid**

  Run: `python3 -m json.tool ~/.claude/settings.json > /dev/null && echo "valid JSON"`
  Expected: `valid JSON`

- [ ] **Step 4: Verify hook was added**

  Run: `python3 -c "import json; d=json.load(open('/Users/russelllaing/.claude/settings.json')); print(d['hooks']['PostToolUse'][0]['hooks'][0]['command'])"`
  Expected: prints the pyright command string

---

### Task 4: Add Pre-Plan Clarification Gate to al-dev-plan SKILL.md

**Files:**
- Modify: `/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md` (Phase 1, before step 1)

**Evidence from report:** "You invoked the al-dev-plan skill twice with no feature description, resulting in no plan being created." Phase 1 currently reads `$ARGUMENTS` without validating it contains a meaningful description. The gate should STOP before any MCP calls or subagent spawning if no description is provided.

- [ ] **Step 1: Read current Phase 1 opening to confirm anchor**

  Run: `sed -n '55,62p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md`
  Expected: output shows `## Phase 1: Gather Context` and `1. Read user's request from $ARGUMENTS`

- [ ] **Step 2: Add input validation gate**

  Use the Edit tool with this exact change:

  Old string:
  ```
  ## Phase 1: Gather Context

  1. Read user's request from $ARGUMENTS
  ```

  New string:
  ```
  ## Phase 1: Gather Context

  **Input Validation Gate (run before any other step):**
  Check whether $ARGUMENTS contains a meaningful feature description.
  - If $ARGUMENTS is empty, missing, or only a vague word (e.g. "plan", "help", "this") with no feature context — **STOP immediately**. Ask the user exactly one question:
    > "What AL feature or fix should I plan? Please describe the requirement or paste a spec."
  - Do **not** proceed to steps 1–4 below, read any files, or spawn any agents until a substantive answer is provided.
  - Once a description is given, resume from step 1 with it as the effective $ARGUMENTS.

  1. Read user's request from $ARGUMENTS
  ```

- [ ] **Step 3: Verify the edit**

  Run: `grep -n "Input Validation Gate" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md`
  Expected: one line matching the gate heading with a line number in the 57–65 range

- [ ] **Step 4: Verify line count increased by expected amount (~9 lines)**

  Run: `wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md`
  Expected: 331 lines (was 322, +9)

- [ ] **Step 5: Commit the SKILL.md change**

  Run:
  ```bash
  git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-plan/SKILL.md
  git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
  fix(al-dev-plan): add input validation gate to prevent invocation without feature description

  Addresses recurring pattern (2+ sessions) where the skill was invoked
  with no arguments, causing wasted cycles and interrupted sessions.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

  Run: `git -C /Users/russelllaing/al-dev-shared log --oneline -1`
  Expected: commit with "fix(al-dev-plan)" in the message

---

## Self-Review

### Spec coverage
- Commit Discipline → Task 1 ✓
- Pyright auto-check → Task 3 ✓
- Pre-Plan clarification gate → Task 4 ✓
- Concrete-first design → Task 2 ✓
- File creation verification — excluded (already in CLAUDE.md) ✓

### Placeholder scan
No TBD, TODO, or template tokens present.

### Type consistency
No code types involved — only configuration and markdown edits. All file paths use absolute paths. The pyright command references the confirmed binary at `/opt/homebrew/bin/pyright`.

### Preconditions verified
- `~/.claude/CLAUDE.md` exists at 69 lines — confirmed by Read
- `~/.claude/settings.json` exists with no hooks key — confirmed by Bash
- `/opt/homebrew/bin/pyright` exists — confirmed by `which pyright`
- `al-dev-plan/SKILL.md` is 322 lines with Phase 1 at line ~57 — confirmed by Bash
