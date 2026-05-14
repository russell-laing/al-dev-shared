# Commit Validation Enforcement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent the three commit-convention violations found in the 2026-05-15 session review: missing emoji prefix, wrong AL body structure, and AI attribution footers slipping into commit messages.

**Architecture:** Four targeted edits across three files. No new files are created. Each task is independently correct and independently committable. Tasks 1 and 2 both edit `al-dev-commit-agent.md` but in separate, non-overlapping sections (analysis phase vs execute phase); do Task 1 before Task 2.

**Tech Stack:** Markdown files only. Verification via Grep and `wc -l`.

---

## File Map

| File | Change |
| --- | --- |
| `profile-al-dev-shared/agents/al-dev-commit-agent.md` | Add Step 6.5 (validation) in analysis phase; strengthen Step 2 (scrubbing) in execute phase |
| `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` | Add "do not commit" guard to developer prompt; add `/al-dev-commit` routing after Phase 10 approval |
| `profile-al-dev-shared/knowledge/commit-conventions.md` | Add Common Violations section |

---

### Task 1: Add message validation step to analysis phase (al-dev-commit-agent.md)

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent.md:147-157`

- [ ] **Step 1: Verify current file state**

  ```bash
  wc -l profile-al-dev-shared/agents/al-dev-commit-agent.md
  grep -n "Step 7 — Return analysis output" profile-al-dev-shared/agents/al-dev-commit-agent.md
  ```

  Expected: line count ~330; Step 7 heading found at approximately line 158.

- [ ] **Step 2: Insert Step 6.5 between Step 6 subject-line rules and Step 7**

  Locate the exact string to use as the insertion point. The old text ends with this block (the two lines before `### Step 7`):

  ```
  - Never append `Co-Authored-By`, `Generated with Claude Code`,
    or any AI attribution footer to the commit message

  ### Step 7 — Return analysis output
  ```

  Replace it with (preserving the two lines above and adding Step 6.5 between them and Step 7):

  ```
  - Never append `Co-Authored-By`, `Generated with Claude Code`,
    or any AI attribution footer to the commit message

  ### Step 6.5 — Validate and correct drafted messages

  Run these checks against every drafted message before returning.
  Auto-correct where possible; add a `WARNINGS` entry for anything
  that cannot be auto-corrected.

  **Emoji check (auto-correct):**

  - Is a leading emoji present on the subject line?
  - Does the emoji match the canonical type (e.g. `fix` → `🐛`,
    `feat` → `✨`, `refactor` → `♻️`)?

  If the emoji is absent or wrong, replace it with the correct
  canonical emoji from the table in Step 6. This is an auto-fix —
  do not leave the message without the correct emoji.

  **AI attribution strip (auto-correct):**

  Scan every line of every drafted message for:
  - Lines starting with `Co-Authored-By:`
  - Lines containing `Generated with Claude Code`
  - Lines containing `Generated with [any model name]`

  Remove any such lines before returning. Record stripped lines in
  the `WARNINGS` block so they are visible to the user.

  **AL body structure check (warn only):**

  If any file in the group ends in `.al`, the project uses AL
  conventions. For any message where `type` is `feat`, `fix`,
  `refactor`, or `hotfix`:

  - Is a `WHY:` block present?
  - Is a `CHANGED COMPONENTS` block present with at least one
    file entry?

  If either is missing, add to `WARNINGS`:

  ```text
  BODY_MISSING: Group <N> — AL commit type '<type>' requires
  '<missing block>'. Add it before approving this message.
  ```

  **Subject line sanity (warn only):**

  - Total subject line length ≤ 72 characters
  - Subject does not end with a period

  Add a `WARNINGS` entry for any violation; do not block the group.

  ### Step 7 — Return analysis output
  ```

- [ ] **Step 3: Verify the insertion**

  ```bash
  grep -n "Step 6.5" profile-al-dev-shared/agents/al-dev-commit-agent.md
  grep -n "Step 7" profile-al-dev-shared/agents/al-dev-commit-agent.md
  wc -l profile-al-dev-shared/agents/al-dev-commit-agent.md
  ```

  Expected: Step 6.5 heading found; Step 7 heading found at a higher line number than before; new line count is roughly 330 + ~45 = ~375.

- [ ] **Step 4: Commit**

  ```bash
  git add profile-al-dev-shared/agents/al-dev-commit-agent.md
  git commit -m "$(cat <<'EOF'
  ✨ feat(al-dev-commit): add Step 6.5 message validation to analysis phase

  Validates emoji, strips AI attribution, warns on missing AL body blocks.
  EOF
  )"
  ```

---

### Task 2: Strengthen AI attribution scrubbing in execute phase (al-dev-commit-agent.md)

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent.md` (execute phase Step 2)

- [ ] **Step 1: Locate execute phase Step 2**

  ```bash
  grep -n "Step 2 — Execute git commit" profile-al-dev-shared/agents/al-dev-commit-agent.md
  ```

  Expected: heading found; note the line number.

- [ ] **Step 2: Strengthen Step 2 with a pre-commit scrubbing instruction**

  The current Step 2 opens with:

  ```
  ### Step 2 — Execute git commit

  Use the approved message verbatim. Do NOT append
  `Co-Authored-By` trailers, `Generated with Claude Code`
  footers, or any other attribution text.
  ```

  Replace those four lines with:

  ```
  ### Step 2 — Execute git commit

  Before committing, scrub AI attribution from the approved message.
  Strip any lines matching these patterns (case-insensitive prefix):

  - `Co-Authored-By:`
  - `Generated with Claude Code`
  - `Generated with [any model name]`

  If any lines are stripped, include them in the execution output
  under `STRIPPED_ATTRIBUTIONS` so the user can audit what was
  removed. Never re-add them.

  After scrubbing, commit the cleaned message:
  ```

- [ ] **Step 3: Verify**

  ```bash
  grep -n "STRIPPED_ATTRIBUTIONS" profile-al-dev-shared/agents/al-dev-commit-agent.md
  grep -n "Step 2 — Execute git commit" profile-al-dev-shared/agents/al-dev-commit-agent.md
  ```

  Expected: both strings found. Line count should increase by ~7 lines from Task 1 result.

- [ ] **Step 4: Update execution output format in Step 3 to include STRIPPED_ATTRIBUTIONS**

  In execute phase Step 3, the return format block currently ends with `HOOK_FAILURES`. Locate:

  ```
  HOOK_FAILURES: NONE
  (or)
  HOOK_FAILURES:
    Group <N>: <raw hook output>
  ```

  Append after that block (before the closing triple-backtick):

  ```
  STRIPPED_ATTRIBUTIONS: NONE
  (or)
  STRIPPED_ATTRIBUTIONS:
    Group <N>: <stripped line>
  ```

- [ ] **Step 5: Verify**

  ```bash
  grep -n "STRIPPED_ATTRIBUTIONS" profile-al-dev-shared/agents/al-dev-commit-agent.md
  wc -l profile-al-dev-shared/agents/al-dev-commit-agent.md
  ```

  Expected: `STRIPPED_ATTRIBUTIONS` appears twice (Step 2 instruction + Step 3 output format).

- [ ] **Step 6: Commit**

  ```bash
  git add profile-al-dev-shared/agents/al-dev-commit-agent.md
  git commit -m "$(cat <<'EOF'
  🐛 fix(al-dev-commit): strip AI attribution in execute phase before git commit
  EOF
  )"
  ```

---

### Task 3: Guard against developer agents committing in al-dev-develop

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md:74-100` (Phase 3 developer prompt)
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md:292-300` (Phase 10 USER_GATE)

- [ ] **Step 1: Locate insertion points**

  ```bash
  grep -n "Naming prefix" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  grep -n "USER_GATE" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: "Naming prefix" around line 99; "USER_GATE" around line 294.

- [ ] **Step 2: Add do-not-commit rule to Phase 3 developer prompt**

  The developer prompt template ends with:

  ```
  Naming prefix: [from plan or project-context.md]
  Project patterns: [from project-context.md if available]
  ```

  Replace those two lines with:

  ```
  Naming prefix: [from plan or project-context.md]
  Project patterns: [from project-context.md if available]

  IMPORTANT: Do NOT run git commit. Your role is to implement
  and verify compilation only. Commits are handled separately
  by /al-dev-commit after user approval.
  ```

- [ ] **Step 3: Add /al-dev-commit routing after Phase 10 USER_GATE**

  The USER_GATE options currently read:

  ```
  USER_GATE — ask the user with options:
  - Approve - Proceed to testing
  - Review Issues - Show high-priority issues in detail
  - Fix Issues First - Address high-priority issues now
  - Refine - Adjust implementation
  - Stop - Cancel development
  ```

  Replace with:

  ```
  USER_GATE — ask the user with options:
  - Approve - Proceed to testing
  - Review Issues - Show high-priority issues in detail
  - Fix Issues First - Address high-priority issues now
  - Refine - Adjust implementation
  - Stop - Cancel development

  After user approves, remind them: "Run `/al-dev-commit` to stage
  and commit the implemented changes using the validated commit
  workflow."
  ```

- [ ] **Step 4: Verify**

  ```bash
  grep -n "Do NOT run git commit" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  grep -n "al-dev-commit" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: "Do NOT run git commit" found once (Phase 3 prompt); "al-dev-commit" found at least once (Phase 10 reminder); line count increased by ~7 from original 300.

- [ ] **Step 5: Commit**

  ```bash
  git add profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  git commit -m "$(cat <<'EOF'
  🐛 fix(al-dev-develop): block developer commits, route to /al-dev-commit after approval
  EOF
  )"
  ```

---

### Task 4: Add Common Violations section to commit-conventions.md

**Files:**
- Modify: `profile-al-dev-shared/knowledge/commit-conventions.md`

- [ ] **Step 1: Verify current end of file**

  ```bash
  wc -l profile-al-dev-shared/knowledge/commit-conventions.md
  tail -10 profile-al-dev-shared/knowledge/commit-conventions.md
  ```

  Expected: ~240 lines; file ends after the Tool example (`🐛 fix(al-dev-align): ...`).

- [ ] **Step 2: Append Common Violations section**

  Locate the last line of the file (the tool skill-fix example):

  ```
  **Tool — skill fix:**

  ```text
  🐛 fix(al-dev-align): handle Unicode apostrophe in prohibition check
  ```

  **Tool — new skill:**

  ```text
  ✨ feat(al-dev-commit): add advisory alignment check to commit workflow
  ```
  ```

  Append after the final closing backtick block:

  ````markdown

  ---

  ## Common Violations

  Violations observed in sessions and called out explicitly to prevent recurrence.

  ### 1. Missing emoji prefix

  ❌ **Wrong:**

  ```text
  fix(report): Remove dead GLN columns
  ```

  ✅ **Correct:**

  ```text
  🐛 fix(report): Remove dead GLN columns
  ```

  The emoji is **Required**. The emoji must match the canonical type. Never omit it.

  ---

  ### 2. Freestyle body sections in AL commits

  ❌ **Wrong (freestyle `## Changes` / `## Verification` sections):**

  ```text
  🐛 fix(report): Remove dead GLN columns

  ## Changes
  - Removed GlobalLocationNumber column from Sales Report

  ## Verification
  - Compilation: SUCCESS
  ```

  ✅ **Correct (canonical AL body for `fix`):**

  ```text
  🐛 fix(report): Remove dead GLN columns

  WHY: Removes deprecated field references blocking BC 28 upgrade.

  CHANGED COMPONENTS
  - SalesReport.Report.al [50920] [m]
  ```

  The `WHY:` and `CHANGED COMPONENTS` blocks are **Required** for `feat`, `fix`,
  `refactor`, and `hotfix` in AL projects. Free-form section headers are never valid.

  ---

  ### 3. AI attribution footer

  ❌ **Wrong:**

  ```text
  🐛 fix(report): Remove dead GLN columns

  Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
  ```

  ✅ **Correct:**

  ```text
  🐛 fix(report): Remove dead GLN columns
  ```

  The **No AI attribution** rule is explicit. Strip any `Co-Authored-By` or
  `Generated with` line before committing.
  ````

- [ ] **Step 3: Verify**

  ```bash
  grep -n "Common Violations" profile-al-dev-shared/knowledge/commit-conventions.md
  wc -l profile-al-dev-shared/knowledge/commit-conventions.md
  ```

  Expected: "Common Violations" heading found; line count increased by ~60 from ~240 to ~300.

- [ ] **Step 4: Commit**

  ```bash
  git add profile-al-dev-shared/knowledge/commit-conventions.md
  git commit -m "$(cat <<'EOF'
  📝 docs(knowledge): add Common Violations section to commit-conventions
  EOF
  )"
  ```

---

## Self-Review

**Spec coverage check:**

| Finding | Task that addresses it |
| --- | --- |
| Missing emoji prefix | Task 1 (Step 6.5 auto-correct) |
| Wrong body structure (AL) | Task 1 (Step 6.5 warn on missing WHY/CHANGED COMPONENTS) |
| Co-Authored-By footer | Task 1 (Step 6.5 auto-strip) + Task 2 (execute phase scrub) |
| Root cause: developers may commit directly | Task 3 (do-not-commit guard in Phase 3) |
| Common Violations not documented | Task 4 |

**Placeholder scan:** No TBD/TODO/implement-later text present.

**Type consistency:** No cross-task symbol references — each task edits isolated file sections.

**Notes on scope:**

- The `al-dev-fix` skill itself never runs `git commit` (it just presents to the user), so no change is needed there.
- The commit-conventions.md "Common Violations" section uses the same canonical examples as the existing "Examples" section — no new types or emoji introduced.
- Tasks 1 and 2 both edit `al-dev-commit-agent.md`. Task 1 must complete before Task 2 to avoid stale line numbers. Each task commits separately so the diff is legible.
