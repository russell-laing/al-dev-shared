# Skill Quality Audit Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all 12 findings from the 2026-05-19 skill quality audit (4 High, 4 Medium, 4 Low severity).

**Architecture:** Fix findings in priority order (High → Medium → Low). Each fix is scoped to a single skill. High-priority fixes improve documentation completeness and clarity. Medium-priority fixes standardize structure and naming. Low-priority fixes improve readability.

**Tech Stack:** Markdown editing, YAML frontmatter updates, directory operations for skill rename.

---

## High Priority Fixes

### Task 1: Add missing `argument-hint` fields to `/al-dev-commit` and `/al-dev-help`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` (frontmatter)
- Modify: `profile-al-dev-shared/skills/al-dev-help/SKILL.md` (frontmatter)

- [ ] **Step 1: Read `/al-dev-commit/SKILL.md` to see current frontmatter**

```bash
head -15 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected output shows frontmatter with `name:`, `description:` but missing `argument-hint`.

- [ ] **Step 2: Add `argument-hint` to `/al-dev-commit` SKILL.md**

Edit the frontmatter to add the line (insert after `description:`):

```yaml
---
name: al-dev-commit
description: >-
  [existing description text]
argument-hint: "[optional args]"
---
```

The hint documents that this skill accepts optional arguments.

- [ ] **Step 3: Read `/al-dev-help/SKILL.md` to see current frontmatter**

```bash
head -15 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-help/SKILL.md
```

- [ ] **Step 4: Add `argument-hint` to `/al-dev-help` SKILL.md**

Edit the frontmatter to add:

```yaml
argument-hint: "[commands|skills|agents|all|description]"
```

This documents the accepted argument types.

- [ ] **Step 5: Verify both files have the new field**

```bash
grep -A5 "argument-hint" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
grep -A5 "argument-hint" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-help/SKILL.md
```

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs(skills): add missing argument-hint fields to /al-dev-commit and /al-dev-help"
```

---

### Task 2: Clarify Step 0 branching logic in `/al-dev-investigate`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md` (Step 0 section)

- [ ] **Step 1: Locate Step 0 in `/al-dev-investigate/SKILL.md`**

```bash
grep -n "Step 0" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Find the section that ends with "Do these match? If findings and request disagree, stop and confirm before proceeding."

- [ ] **Step 2: Read the current Step 0 section (surrounding context)**

```bash
sed -n '<start-line>,<end-line>p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

- [ ] **Step 3: Replace the ambiguous ending with explicit decision tree**

Find this text:
```
Do these match? If findings and request disagree, stop and confirm before proceeding.
```

Replace with:
```
Do these match?

**If all align:** Continue to Step 1.

**If findings and request disagree:** STOP. Ask the user to confirm whether to:
1. Restart the investigation with clarified requirements, or
2. Proceed with the current scope despite the mismatch
```

- [ ] **Step 4: Verify the edit**

```bash
grep -A5 "If all align" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs(skills): clarify Step 0 branching logic in /al-dev-investigate"
```

---

### Task 3: Clarify AL compile command options in `/al-dev-lint`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-lint/SKILL.md` (Step 1 section)

- [ ] **Step 1: Locate Step 1 in `/al-dev-lint/SKILL.md`**

Find the section showing the two compile commands.

```bash
grep -n "al-compile\|al compile" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-lint/SKILL.md | head -10
```

- [ ] **Step 2: Read the context around both commands**

```bash
sed -n '<start-line>,<end-line>p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-lint/SKILL.md
```

- [ ] **Step 3: Add a clarification note before or after the command options**

Insert this text near where both commands appear:

```
**Note:** Use `al-compile` if available (preferred—faster and simpler). If `al-compile` is not in PATH, fall back to `al compile`. Both produce the same output log format.
```

- [ ] **Step 4: Verify the note was added**

```bash
grep -A2 "Use.*al-compile.*if available" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-lint/SKILL.md
```

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs(skills): clarify AL compile command options in /al-dev-lint"
```

---

## Medium Priority Fixes

### Task 4: Rename Step 0.5 → Step 1 in `/al-dev-handoff` and renumber cascade

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-handoff/SKILL.md` (all step numbers)

- [ ] **Step 1: View the current step numbering in `/al-dev-handoff/SKILL.md`**

```bash
grep -n "Step [0-9]" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-handoff/SKILL.md
```

This will show the current numbering (Step 0.5, Step 1, Step 2, etc.)

- [ ] **Step 2: Rename Step 0.5 to Step 1 and shift all subsequent steps up**

Use sed to replace all step numbers in order (or use Edit tool for safety):

```bash
sed -i '' 's/### Step 0\.5:/### Step 1:/' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-handoff/SKILL.md
sed -i '' 's/### Step 1:/### Step 2:/' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-handoff/SKILL.md
sed -i '' 's/### Step 2:/### Step 3:/' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-handoff/SKILL.md
# ... continue for all subsequent steps
```

- [ ] **Step 3: Verify renumbering is correct**

```bash
grep "^### Step" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-handoff/SKILL.md
```

Expected: Step 1, Step 2, Step 3, Step 4, Step 5, Step 6 (sequential, no fractional).

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs(skills): standardize step numbering in /al-dev-handoff (0.5→1, cascade)"
```

---

### Task 5: Extract long examples from `/al-dev-fix` into a companion knowledge document

**Files:**
- Create: `profile-al-dev-shared/knowledge/al-dev-fix-examples.md`
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` (remove Examples 1 & 2, add reference)

- [ ] **Step 1: Read the examples section in `/al-dev-fix/SKILL.md` (lines 333–399)**

```bash
sed -n '333,399p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Capture both examples completely.

- [ ] **Step 2: Create a new knowledge document `al-dev-fix-examples.md`**

```markdown
# /al-dev-fix Detailed Examples

This document provides detailed walkthroughs of two common fix scenarios.

## Example 1: [Title from current Example 1]

[Full example content from current SKILL.md]

## Example 2: [Title from current Example 2]

[Full example content from current SKILL.md]
```

- [ ] **Step 3: Write the knowledge file with extracted examples**

Copy the captured examples into the new knowledge document.

- [ ] **Step 4: Remove examples from `/al-dev-fix/SKILL.md` and add reference**

Delete lines 333–399, then add a new "Examples" section at the end:

```markdown
## Examples

For detailed walkthroughs of two common scenarios, see [`knowledge/al-dev-fix-examples.md`](../knowledge/al-dev-fix-examples.md).
```

- [ ] **Step 5: Verify the skill file is now shorter and the knowledge file exists**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-fix/SKILL.md
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/al-dev-fix-examples.md
```

Expected: SKILL.md reduced by ~67 lines; knowledge file created.

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/al-dev-fix-examples.md
git -C /Users/russelllaing/al-dev-shared commit -m "refactor(skills): extract /al-dev-fix examples into knowledge document"
```

---

### Task 6: Streamline credential check in `/al-dev-ticket`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md` (Step 1 and Step 2)

- [ ] **Step 1: Locate credential checks in `/al-dev-ticket/SKILL.md`**

```bash
grep -n "credential\|Step 1\|Step 2" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-ticket/SKILL.md | head -20
```

- [ ] **Step 2: Read Step 1 and Step 2 sections**

```bash
sed -n '<step1-start>,<step2-end>p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-ticket/SKILL.md
```

Identify where credential check appears twice.

- [ ] **Step 3: Consolidate credential check**

Move the credential verification logic to a single location (Step 1, after the branch decision) instead of repeating it in Step 2 or in the dispatch prompt. 

- [ ] **Step 4: Remove any duplicate credential checks from Step 2 dispatch**

If Step 2's dispatch prompt also mentions credential verification, remove that repetition.

- [ ] **Step 5: Verify the structure**

```bash
grep -c "credential\|Freshdesk.*config" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-ticket/SKILL.md
```

Expected: Fewer occurrences (ideally 1–2, not 3+).

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs(skills): consolidate credential check in /al-dev-ticket"
```

---

### Task 7: Rename `/commit-learn` skill to `/commit-recover`

**Files:**
- Rename: `profile-al-dev-shared/skills/commit-learn/` → `profile-al-dev-shared/skills/commit-recover/`
- Modify: `profile-al-dev-shared/skills/commit-recover/SKILL.md` (frontmatter `name:`)

- [ ] **Step 1: View the current skill directory and frontmatter**

```bash
ls -la /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/commit-learn/
head -10 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/commit-learn/SKILL.md
```

- [ ] **Step 2: Rename the directory**

```bash
mv /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/commit-learn /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/commit-recover
```

- [ ] **Step 3: Update the skill name in frontmatter**

Edit `/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/commit-recover/SKILL.md`:

Change `name: commit-learn` to `name: commit-recover`.

- [ ] **Step 4: Update the description for clarity**

If the description mentions "learn from commits", update it to clarify: "Recover corrupted AL files from commit integrity failures."

- [ ] **Step 5: Check for any internal references to the old name**

```bash
grep -r "commit-learn" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/
```

Update any found references to `commit-recover`.

- [ ] **Step 6: Verify the rename is complete**

```bash
ls -la /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/commit-recover/
head -5 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/commit-recover/SKILL.md
```

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add -A
git -C /Users/russelllaing/al-dev-shared commit -m "refactor(skills): rename /commit-learn to /commit-recover for clarity"
```

---

## Low Priority Fixes

### Task 8: Add jargon glossary to `/al-dev-develop`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` (add glossary section near top)

- [ ] **Step 1: Identify jargon in `/al-dev-develop/SKILL.md`**

```bash
grep -n "Scope Expansion Gate\|developer spawn prompt\|Phase" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md | head -15
```

- [ ] **Step 2: Add a glossary section after the introductory text**

Insert a new section defining key terms like "Scope Expansion Gate", "Developer Spawn Prompt", "Phase N", etc.

- [ ] **Step 3: Verify the glossary was added**

```bash
grep -A3 "## Glossary" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs(skills): add glossary to /al-dev-develop for clarity"
```

---

### Task 9: Standardize step numbering in `/al-dev-perf` (Step 1.5 → Step 1a)

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-perf/SKILL.md` (step headers)

- [ ] **Step 1: Locate fractional step in `/al-dev-perf/SKILL.md`**

```bash
grep -n "Step 1\.5" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-perf/SKILL.md
```

- [ ] **Step 2: Replace Step 1.5 with Step 1a**

Find the header and replace it with a sequential format.

- [ ] **Step 3: Update any references to Step 1.5**

```bash
grep "Step 1\.5\|Step 1a" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-perf/SKILL.md
```

- [ ] **Step 4: Verify the change**

```bash
grep -n "^### Step" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-perf/SKILL.md
```

Expected: Steps now numbered 1, 1a, 2, 3, etc. (not fractional).

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs(skills): standardize step numbering in /al-dev-perf (1.5→1a)"
```

---

### Task 10: Document phase numbering rationale in `/al-dev-plan`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` (add explanatory note)

- [ ] **Step 1: Locate the phase numbering section in `/al-dev-plan/SKILL.md`**

```bash
grep -n "Phase 0\|Phase 1" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md | head -10
```

- [ ] **Step 2: Add a note explaining the numbering scheme**

Insert a section explaining that fractional numbering (Phase 0, Phase 0.5, Phase 1–7) reflects semantic layers rather than sequential numbering.

- [ ] **Step 3: Verify the note was added clearly**

```bash
grep -A4 "Phase Numbering" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs(skills): document phase numbering rationale in /al-dev-plan"
```

---

### Task 11: Final verification and summary

**Files:**
- No new files; verification step only

- [ ] **Step 1: Spot-check key changes**

```bash
# Verify argument-hint fields
grep "argument-hint" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
grep "argument-hint" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-help/SKILL.md

# Verify skill rename
ls /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/commit-recover/SKILL.md

# Verify no fractional step numbers
! grep "Step [0-9]\.[5]" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-handoff/SKILL.md
! grep "Step [0-9]\.[5]" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-perf/SKILL.md
```

- [ ] **Step 2: View the commit log to confirm all changes**

```bash
git -C /Users/russelllaing/al-dev-shared log --oneline | head -12
```

- [ ] **Step 3: Update the audit document status (optional)**

Add a final note to `docs/al-dev-skill-quality.md` updating the status.

---

## Verification Checklist

- [ ] All 4 High-priority findings fixed
- [ ] All 4 Medium-priority findings fixed
- [ ] All 4 Low-priority findings fixed
- [ ] No placeholder patterns remain (`TODO`, `TBD`, `[date]`, `YYYY-MM-DD`)
- [ ] All step numbers are sequential (no fractional steps except where documented)
- [ ] All references to `commit-learn` updated to `commit-recover`
- [ ] All commits present in git log

