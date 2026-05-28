# Audit Skill Fix Cap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a hard 5% per-file content reduction cap to the fix-application step in both audit skills (`/audit-agent-quality` and `/audit-skill-quality`).

**Architecture:** Phase 6 of each skill gains a "Fix Application Protocol" subsection. The protocol instructs the model to read each file's line count, calculate a line-removal budget, apply only atomic fixes within that budget, and skip any fix that would exceed it. The two skill files are nearly identical in structure — the same block of new text is appended to Phase 6 of each. No other files change.

**Execution note:** Track progress outside this file while executing the plan. Do not treat checklist state changes in this plan as repository changes.

**Tech Stack:** Markdown skill files; Edit tool for in-place modification; Bash for pre/post line-count verification.

---

## File Map

| Action | Path |
|--------|------|
| Modify | `.claude/skills/audit-agent-quality/SKILL.md` (Phase 6, line 155–161) |
| Modify | `.claude/skills/audit-skill-quality/SKILL.md` (Phase 6, line 155–161) |

---

### Task 1: Add Fix Application Protocol to audit-agent-quality/SKILL.md

**Files:**
- Modify: `.claude/skills/audit-agent-quality/SKILL.md`

- [ ] **Step 1: Confirm current Phase 6 content**

  Run:
  ```bash
  wc -l /Users/russelllaing/al-dev-shared/.claude/skills/audit-agent-quality/SKILL.md
  ```
  Expected: `161`

- [ ] **Step 2: Apply the edit**

  Use the Edit tool on `/Users/russelllaing/al-dev-shared/.claude/skills/audit-agent-quality/SKILL.md`.

  `old_string`:
  ```
  Ask: "Would you like to fix any of these now?"
  ```

  `new_string`:
  ```
  Ask: "Would you like to fix any of these now?"

  ### If the user says yes — Fix Application Protocol

  For each file to be modified:

  1. **Read the file** and record its original line count (`original_lines`).
  2. **Calculate budget:** `floor(original_lines × 0.05)` — max net lines
     removable from this file in this pass.
     If the result is `0`, skip all non-atomic edits for that file this pass.
  3. **Apply only atomic fixes** per finding, in priority order:
     High → Medium → Low. An atomic fix is one that fully resolves a finding
     without rewriting unrelated sections.
  4. **If the next full fix would exceed `budget`:**
     skip that finding for this pass, append to the report section for that file:
     `"Skipped — full fix exceeds remaining budget; queue for next audit pass."`
  5. **Do not partially rewrite structural blocks** such as headings, lists,
     frontmatter, or phase instructions. If a finding touches a structural block
     and cannot be resolved atomically within the remaining budget, skip it.
  6. **Verify after edit:** `wc -l <file>` — confirm net reduction ≤ budget.
     Also confirm the edited file still contains the required structural sections
     for its type before proceeding to the next file.
  7. **Leave commits to the surrounding workflow.** The protocol only governs
     safe edit application; it does not introduce a new commit step.
  ```

- [ ] **Step 3: Verify line count grew**

  Run:
  ```bash
  wc -l /Users/russelllaing/al-dev-shared/.claude/skills/audit-agent-quality/SKILL.md
  ```
  Expected: `184` (161 + 23 new lines). Accept any value in the range 182–186 — minor whitespace differences are fine.

- [ ] **Step 4: Verify Phase 6 content**

  Run:
  ```bash
  grep -n "Fix Application Protocol\|floor(original_lines\|wc -l <file>" /Users/russelllaing/al-dev-shared/.claude/skills/audit-agent-quality/SKILL.md
  ```
  Expected: three matching lines, all in the Phase 6 region (lines 163+).

- [ ] **Step 5: Forbidden-pattern scan**

  Run:
  ```bash
  grep -n "TODO\|TBD\|YYYY-MM-DD\|\[date\]\|claude:\|copilot:" /Users/russelllaing/al-dev-shared/.claude/skills/audit-agent-quality/SKILL.md
  ```
  Expected: no output.

---

### Task 2: Add Fix Application Protocol to audit-skill-quality/SKILL.md

**Files:**
- Modify: `.claude/skills/audit-skill-quality/SKILL.md`

- [ ] **Step 1: Confirm current Phase 6 content**

  Run:
  ```bash
  wc -l /Users/russelllaing/al-dev-shared/.claude/skills/audit-skill-quality/SKILL.md
  ```
  Expected: `161`

- [ ] **Step 2: Apply the edit**

  Use the Edit tool on `/Users/russelllaing/al-dev-shared/.claude/skills/audit-skill-quality/SKILL.md`.

  `old_string`:
  ```
  Ask: "Would you like to fix any of these now?"
  ```

  `new_string`:
  ```
  Ask: "Would you like to fix any of these now?"

  ### If the user says yes — Fix Application Protocol

  For each file to be modified:

  1. **Read the file** and record its original line count (`original_lines`).
  2. **Calculate budget:** `floor(original_lines × 0.05)` — max net lines
     removable from this file in this pass.
  3. **Apply only atomic fixes** per finding, in priority order:
     High → Medium → Low. An atomic fix is one that fully resolves a finding
     without rewriting unrelated sections.
  4. **If the next full fix would exceed `budget`:**
     skip that finding for this pass, append to the report section for that file:
     `"Skipped — full fix exceeds remaining budget; queue for next audit pass."`
  5. **Do not partially rewrite structural blocks** such as headings, lists,
     frontmatter, or phase instructions. If a finding touches a structural block
     and cannot be resolved atomically within the remaining budget, skip it.
  6. **Verify after edit:** `wc -l <file>` — confirm net reduction ≤ budget.
     Also confirm the edited file still contains the required structural sections
     for its type before proceeding to the next file.
  7. **Leave commits to the surrounding workflow.** The protocol only governs
     safe edit application; it does not introduce a new commit step.
  ```

- [ ] **Step 3: Verify line count grew**

  Run:
  ```bash
  wc -l /Users/russelllaing/al-dev-shared/.claude/skills/audit-skill-quality/SKILL.md
  ```
  Expected: `184` (161 + 23 new lines). Accept any value in the range 182–186.

- [ ] **Step 4: Verify Phase 6 content**

  Run:
  ```bash
  grep -n "Fix Application Protocol\|floor(original_lines\|wc -l <file>" /Users/russelllaing/al-dev-shared/.claude/skills/audit-skill-quality/SKILL.md
  ```
  Expected: three matching lines, all in the Phase 6 region (lines 163+).

- [ ] **Step 5: Forbidden-pattern scan**

  Run:
  ```bash
  grep -n "TODO\|TBD\|YYYY-MM-DD\|\[date\]\|claude:\|copilot:" /Users/russelllaing/al-dev-shared/.claude/skills/audit-skill-quality/SKILL.md
  ```
  Expected: no output.

---

### Task 3: Acceptance Criteria Check and Commit

**Files:** No new changes — verification and commit only.

- [ ] **Step 1: Verify both acceptance criteria**

  Each criterion from the spec must be met:

  1. `audit-agent-quality/SKILL.md` Phase 6 includes Fix Application Protocol with 5% cap:
     ```bash
     grep -c "0.05" /Users/russelllaing/al-dev-shared/.claude/skills/audit-agent-quality/SKILL.md
     ```
     Expected: `1`

  2. `audit-skill-quality/SKILL.md` Phase 6 includes Fix Application Protocol with 5% cap:
     ```bash
     grep -c "0.05" /Users/russelllaing/al-dev-shared/.claude/skills/audit-skill-quality/SKILL.md
     ```
     Expected: `1`

  3. Protocol specifies all required elements — check both files for each required phrase:
     ```bash
     for f in \
       /Users/russelllaing/al-dev-shared/.claude/skills/audit-agent-quality/SKILL.md \
       /Users/russelllaing/al-dev-shared/.claude/skills/audit-skill-quality/SKILL.md; do
       echo "=== $f ==="
       grep -c "original_lines" "$f"
       grep -c "floor" "$f"
       grep -c "atomic" "$f"
       grep -c "Skipped" "$f"
       grep -c "structural blocks" "$f"
       grep -c "wc -l" "$f"
     done
     ```
     Expected: each `grep -c` returns `1` for both files.

  4. No changes to lens agents:
     ```bash
     git -C /Users/russelllaing/al-dev-shared diff --name-only
     ```
     Expected: after staging the two skill files, `git diff --cached --name-only`
     reports exactly two paths —
     `.claude/skills/audit-agent-quality/SKILL.md` and
     `.claude/skills/audit-skill-quality/SKILL.md`. Any other staged path is a failure.

- [ ] **Step 2: Commit**

  ```bash
  git -C /Users/russelllaing/al-dev-shared add \
    .claude/skills/audit-agent-quality/SKILL.md \
    .claude/skills/audit-skill-quality/SKILL.md
  git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
  feat(skills): add 5% per-file fix cap to audit skill Phase 6

  Adds a Fix Application Protocol to Phase 6 of both audit-agent-quality
  and audit-skill-quality. When the user chooses to apply fixes, the model
  now reads each file's line count, calculates a floor(N × 0.05) line-removal
  budget, applies only atomic fixes within that budget, and queues any fix
  that would exceed it for the next audit pass.
  EOF
  )"
  ```

- [ ] **Step 3: Confirm commit count**

  ```bash
  git -C /Users/russelllaing/al-dev-shared log --oneline -n 1
  ```
  Expected: one new commit whose message begins `feat(skills): add 5% per-file fix cap`.
