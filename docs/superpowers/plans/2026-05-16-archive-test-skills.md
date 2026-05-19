# Archive Test Skills and Agents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the `al-dev-test` skill and all 5 test-engineer agents out of the active plugin directories into `profile-al-dev-shared/archived/`, then update 4 active skills to remove all references to archived items.

**Architecture:** Use `git mv` (not `mv`) for all file moves to preserve git history. Edits to active skills use the Edit tool with exact string matches to avoid collapsing whitespace or line count changes.

**Tech Stack:** Bash (git mv, mkdir), Claude Code Edit tool, Markdown.

---

## File Map

**Created:**
- `profile-al-dev-shared/archived/README.md` — new file, explains the archive

**Moved (git mv):**
- `profile-al-dev-shared/skills/al-dev-test/` → `profile-al-dev-shared/archived/skills/al-dev-test/`
- `profile-al-dev-shared/agents/al-dev-unit-test-engineer.md` → `profile-al-dev-shared/archived/agents/`
- `profile-al-dev-shared/agents/al-dev-integration-test-engineer.md` → `profile-al-dev-shared/archived/agents/`
- `profile-al-dev-shared/agents/al-dev-scenario-test-engineer.md` → `profile-al-dev-shared/archived/agents/`
- `profile-al-dev-shared/agents/al-dev-edge-case-test-engineer.md` → `profile-al-dev-shared/archived/agents/`
- `profile-al-dev-shared/agents/al-dev-test-coverage-reviewer.md` → `profile-al-dev-shared/archived/agents/`

**Modified:**
- `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` — remove test-coverage-reviewer, update 4→3 specialist counts
- `profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md` — same pattern as al-dev-develop
- `profile-al-dev-shared/skills/al-dev-help/SKILL.md` — remove /al-dev-test rows, test-agent rows, conditional suggestions
- `profile-al-dev-shared/skills/al-dev-document/SKILL.md` — remove 05-test-plan.md references, /al-dev-test timing note

---

### Task 1: Create Archive Directory and README

**Files:**
- Create: `profile-al-dev-shared/archived/README.md`

All paths below are relative to `/Users/russelllaing/al-dev-shared/`.

- [ ] **Step 1: Create the archive subdirectories**

```bash
mkdir -p profile-al-dev-shared/archived/skills
mkdir -p profile-al-dev-shared/archived/agents
```

- [ ] **Step 2: Verify directories exist**

```bash
ls profile-al-dev-shared/archived/
```

Expected output:
```
agents
skills
```

- [ ] **Step 3: Write the README**

Create `profile-al-dev-shared/archived/README.md` with this exact content:

```markdown
# Archived Skills and Agents

Files here are inactive — not loaded by the plugin. Move them back to
`skills/` or `agents/` to reinstate.

## What is here

| Item | Type | Archived reason |
|------|------|-----------------|
| `skills/al-dev-test/` | Skill | Test codeunit workflow not yet in use |
| `agents/al-dev-unit-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-integration-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-scenario-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-edge-case-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-test-coverage-reviewer.md` | Agent | Spawned by al-dev-develop/al-dev-autonomous |

## Reinstatement steps

1. `git mv archived/skills/al-dev-test skills/al-dev-test`
2. `git mv archived/agents/al-dev-unit-test-engineer.md agents/`
3. `git mv archived/agents/al-dev-integration-test-engineer.md agents/`
4. `git mv archived/agents/al-dev-scenario-test-engineer.md agents/`
5. `git mv archived/agents/al-dev-edge-case-test-engineer.md agents/`
6. `git mv archived/agents/al-dev-test-coverage-reviewer.md agents/`
7. Revert all edits described in the spec:
   `docs/superpowers/specs/2026-05-16-archive-test-skills-design.md`
```

- [ ] **Step 4: Verify README was written**

```bash
wc -l profile-al-dev-shared/archived/README.md
```

Expected: non-zero line count (approximately 30 lines).

---

### Task 2: Move Files with git mv

**Files:**
- Move: `profile-al-dev-shared/skills/al-dev-test/` → `profile-al-dev-shared/archived/skills/al-dev-test/`
- Move: 5 agent files from `profile-al-dev-shared/agents/` → `profile-al-dev-shared/archived/agents/`

All commands run from `/Users/russelllaing/al-dev-shared/`.

- [ ] **Step 1: Move the skill directory**

```bash
git -C /Users/russelllaing/al-dev-shared mv \
  profile-al-dev-shared/skills/al-dev-test \
  profile-al-dev-shared/archived/skills/al-dev-test
```

- [ ] **Step 2: Verify skill moved**

```bash
ls profile-al-dev-shared/archived/skills/al-dev-test/
```

Expected:
```
SKILL.md
validate-test-plan.py
```

And confirm it's gone from active skills:

```bash
ls profile-al-dev-shared/skills/ | grep al-dev-test
```

Expected: no output.

- [ ] **Step 3: Move the 5 agent files**

```bash
git -C /Users/russelllaing/al-dev-shared mv \
  profile-al-dev-shared/agents/al-dev-unit-test-engineer.md \
  profile-al-dev-shared/archived/agents/al-dev-unit-test-engineer.md

git -C /Users/russelllaing/al-dev-shared mv \
  profile-al-dev-shared/agents/al-dev-integration-test-engineer.md \
  profile-al-dev-shared/archived/agents/al-dev-integration-test-engineer.md

git -C /Users/russelllaing/al-dev-shared mv \
  profile-al-dev-shared/agents/al-dev-scenario-test-engineer.md \
  profile-al-dev-shared/archived/agents/al-dev-scenario-test-engineer.md

git -C /Users/russelllaing/al-dev-shared mv \
  profile-al-dev-shared/agents/al-dev-edge-case-test-engineer.md \
  profile-al-dev-shared/archived/agents/al-dev-edge-case-test-engineer.md

git -C /Users/russelllaing/al-dev-shared mv \
  profile-al-dev-shared/agents/al-dev-test-coverage-reviewer.md \
  profile-al-dev-shared/archived/agents/al-dev-test-coverage-reviewer.md
```

- [ ] **Step 4: Verify all 5 agents are in the archive**

```bash
ls profile-al-dev-shared/archived/agents/
```

Expected (all 5 files present):
```
al-dev-edge-case-test-engineer.md
al-dev-integration-test-engineer.md
al-dev-scenario-test-engineer.md
al-dev-test-coverage-reviewer.md
al-dev-unit-test-engineer.md
```

- [ ] **Step 5: Confirm no test agents remain in active agents/**

```bash
ls profile-al-dev-shared/agents/ | grep -E "test-engineer|test-coverage"
```

Expected: no output.

---

### Task 3: Edit `al-dev-develop/SKILL.md`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`

There are 5 edit operations. Apply them in order, using the Edit tool with exact string matches.

- [ ] **Step 1: Update frontmatter description (4-specialist → 3-specialist)**

Find and replace in `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`:

Old:
```
  and 4-specialist review (security, AL expert, performance,
  test coverage). Use when implementing a planned feature,
```

New:
```
  and 3-specialist review (security, AL expert, performance).
  Use when implementing a planned feature,
```

- [ ] **Step 2: Update the skill header paragraph**

Old:
```
Implement an AL/BC solution using parallel developers
and 4-specialist review. You do NOT write code yourself.
```

New:
```
Implement an AL/BC solution using parallel developers
and 3-specialist review. You do NOT write code yourself.
```

- [ ] **Step 3: Update Phase 5 spawn count**

Old:
```
When all developers complete, spawn 4 reviewers in parallel
as a single batch:
```

New:
```
When all developers complete, spawn 3 reviewers in parallel
as a single batch:
```

- [ ] **Step 4: Remove the al-dev-test-coverage-reviewer block from Phase 5**

Old (remove this entire block including the blank line before it):
```

**al-dev-test-coverage-reviewer:**
Review for testability (dependency injection present?),
interfaces for mocking, event extensibility, test scenario
coverage. Compare to the latest solution plan
(.dev/*-al-dev-plan-solution-plan.md) testability
requirements.
```

New: `` (empty string — delete the block entirely)

- [ ] **Step 5: Update Phase 6 "four" → "three"**

Old:
```
1. Read all four review outputs
```

New:
```
1. Read all three review outputs
```

- [ ] **Step 6: Update Phase 10 reviewer count in the user-facing summary**

Old:
```
Review findings (4 specialist reviewers):
```

New:
```
Review findings (3 specialist reviewers):
```

- [ ] **Step 7: Verify line count is preserved (approximately)**

```bash
wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: approximately 298 lines (original was 308; the removed block was ~9 lines and the 2-line reflow saves 1 line → net ~10 lines fewer).

- [ ] **Step 8: Verify no test-coverage-reviewer references remain**

```bash
grep -n "test-coverage-reviewer\|4-specialist\|4 reviewer\|4 specialist\|all four" \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: no output.

---

### Task 4: Edit `al-dev-autonomous/SKILL.md`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md`

Apply 4 edit operations in order.

- [ ] **Step 1: Update Phase 5 spawn count**

Old:
```
Spawn 4 reviewers in parallel as a single batch.
```

New:
```
Spawn 3 reviewers in parallel as a single batch.
```

- [ ] **Step 2: Remove the al-dev-test-coverage-reviewer block**

Old (remove this entire block including the blank line before it):
```

**al-dev-test-coverage-reviewer:** Review for testability,
interfaces for mocking, event extensibility, test scenario
coverage vs solution plan.
```

New: `` (empty string — delete the block entirely)

- [ ] **Step 3: Update Phase 6 "four" → "three"**

Old:
```
1. Read all four review outputs
```

New:
```
1. Read all three review outputs
```

- [ ] **Step 4: Update the user-facing summary reviewer count**

Old:
```
Review findings (4 specialist reviewers):
[N] critical issues found and fixed
[N] high-priority issues for your decision
[N] minor suggestions documented
```

New:
```
Review findings (3 specialist reviewers):
[N] critical issues found and fixed
[N] high-priority issues for your decision
[N] minor suggestions documented
```

- [ ] **Step 5: Verify no test-coverage-reviewer or "4 reviewer" references remain**

```bash
grep -n "test-coverage-reviewer\|4 reviewer\|4-specialist\|all four" \
  profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
```

Expected: no output.

---

### Task 5: Edit `al-dev-help/SKILL.md`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-help/SKILL.md`

There are 9 edit operations. This file is 235 lines — use exact string matches to avoid false matches.

- [ ] **Step 1: Remove /al-dev-test row from the first skills reference table (line ~63)**

Old:
```
| /al-dev-develop       | Parallel implementation + 4-specialist code review   |
| /al-dev-test          | Comprehensive test suite with 4 parallel engineers   |
| /al-dev-release-notes | End-user release notes from git diff                 |
```

New:
```
| /al-dev-develop       | Parallel implementation + 3-specialist code review   |
| /al-dev-release-notes | End-user release notes from git diff                 |
```

- [ ] **Step 2: Remove /al-dev-test row from the second skills reference table (line ~80)**

Old:
```
| /al-dev-develop       | Parallel implementation + 4-specialist code review    |
| /al-dev-test          | Comprehensive test suite with 4 parallel engineers    |
| /al-dev-release-notes | End-user release notes from git diff                  |
```

New:
```
| /al-dev-develop       | Parallel implementation + 3-specialist code review    |
| /al-dev-release-notes | End-user release notes from git diff                  |
```

- [ ] **Step 3: Remove the 5 test-agent rows from the agent catalogue (lines ~106–110)**

Old:
```
| performance-reviewer      | Query efficiency, N+1, resource usage           |
| test-coverage-reviewer    | Test adequacy and missing scenarios             |
| unit-test-engineer        | Unit test development                           |
| integration-test-engineer | Cross-object integration tests                  |
| scenario-test-engineer    | End-to-end scenario test development            |
| edge-case-test-engineer   | Boundary and error case test development        |
| interview                 | Deep requirements gathering                     |
```

New:
```
| performance-reviewer      | Query efficiency, N+1, resource usage           |
| interview                 | Deep requirements gathering                     |
```

- [ ] **Step 4: Remove the "/al-dev-test" row from the situation → workflow table (line ~138)**

Old:
```
| Have a plan, ready to implement | `/al-dev-develop` |
| Implementation done, need tests | `/al-dev-test` |
| Feature complete, need docs | `/al-dev-document` |
```

New:
```
| Have a plan, ready to implement | `/al-dev-develop` |
| Feature complete, need docs | `/al-dev-document` |
```

- [ ] **Step 5: Remove `.dev/05-test-plan.md` from the artifact scan list (line ~152)**

Old:
```
- `.dev/03-code-review.md` — implementation reviewed
- `.dev/05-test-plan.md` — tests written

Apply these refinements:
```

New:
```
- `.dev/03-code-review.md` — implementation reviewed

Apply these refinements:
```

- [ ] **Step 6: Remove the conditional suggestion for /al-dev-test (lines ~162–163)**

Old:
```
- `02-solution-plan.md` exists → skip `/al-dev-plan`,
  suggest `/al-dev-develop`
- `03-code-review.md` exists but no `05-test-plan.md` → suggest
  `/al-dev-test`

**Step 3: Output recommendation:**
```

New:
```
- `02-solution-plan.md` exists → skip `/al-dev-plan`,
  suggest `/al-dev-develop`

**Step 3: Output recommendation:**
```

- [ ] **Step 7: Remove /al-dev-test from the suggested sequence example (line ~181)**

Old:
```
  1. /al-dev-interview "credit limit validation"  -- gather requirements
  2. /al-dev-plan                                 -- design solution
  3. /al-dev-develop                              -- implement + review
  4. /al-dev-test                                 -- if business-critical

Or skip to /al-dev-plan directly if requirements are already clear.
```

New:
```
  1. /al-dev-interview "credit limit validation"  -- gather requirements
  2. /al-dev-plan                                 -- design solution
  3. /al-dev-develop                              -- implement + review

Or skip to /al-dev-plan directly if requirements are already clear.
```

- [ ] **Step 8: Update the Step 2C pipeline state table and sample output (lines ~200–218)**

Old:
```
| `02-solution-plan.md` present | Run `/al-dev-develop` to implement |
| `03-code-review.md` present | Run `/al-dev-test` if coverage matters |
| `05-test-plan.md` present | Run `/al-dev-document` for reference documentation |

**Step 3: Output:**

```text
Current project state:

  .dev/project-context.md   ✅ found
  .dev/01-requirements.md   ✅ found (12 REQ: tokens)
  .dev/02-solution-plan.md  ✅ found
  .dev/03-code-review.md    ❌ not found
  .dev/05-test-plan.md      ❌ not found

Recommendation: Run /al-dev-develop to implement the solution plan.

The plan exists — the next step is parallel implementation
followed by 4-specialist code review.
```
```

New:
```
| `02-solution-plan.md` present | Run `/al-dev-develop` to implement |
| `03-code-review.md` present | Run `/al-dev-document` for reference documentation |

**Step 3: Output:**

```text
Current project state:

  .dev/project-context.md   ✅ found
  .dev/01-requirements.md   ✅ found (12 REQ: tokens)
  .dev/02-solution-plan.md  ✅ found
  .dev/03-code-review.md    ❌ not found

Recommendation: Run /al-dev-develop to implement the solution plan.

The plan exists — the next step is parallel implementation
followed by 3-specialist code review.
```
```

- [ ] **Step 9: Remove /al-dev-test from the quick-reference table (line ~228)**

Old:
```
  /al-dev-develop       -- parallel implementation + code review
  /al-dev-test          -- 4-engineer parallel test suite
  /al-dev-document      -- generate technical documentation
```

New:
```
  /al-dev-develop       -- parallel implementation + code review
  /al-dev-document      -- generate technical documentation
```

- [ ] **Step 10: Verify no /al-dev-test references remain**

```bash
grep -n "al-dev-test\|test-engineer\|test-coverage\|05-test-plan\|4-engineer" \
  profile-al-dev-shared/skills/al-dev-help/SKILL.md
```

Expected: no output.

---

### Task 6: Edit `al-dev-document/SKILL.md`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-document/SKILL.md`

4 edit operations targeting 4 distinct locations.

- [ ] **Step 1: Remove the "05-test-plan.md" step from the Step 1 checklist and fix numbering**

Old:
```
1. Find implemented AL files
2. Read .dev/01-requirements.md — note how many REQ: tokens are present
3. Read .dev/02-solution-plan.md if available (for context)
4. Check for test results (.dev/05-test-plan.md)
5. Determine inferred RTM status from .dev/ files present:
   - only 01-requirements.md → DEFINED
   - 02-solution-plan.md present → IN-PROGRESS
   - 03-code-review.md present → IMPLEMENTED
   - 05-test-plan.md present → VERIFIED
6. Identify target audience (developers, users, admins)
```

New:
```
1. Find implemented AL files
2. Read .dev/01-requirements.md — note how many REQ: tokens are present
3. Read .dev/02-solution-plan.md if available (for context)
4. Determine inferred RTM status from .dev/ files present:
   - only 01-requirements.md → DEFINED
   - 02-solution-plan.md present → IN-PROGRESS
   - 03-code-review.md present → IMPLEMENTED
5. Identify target audience (developers, users, admins)
```

- [ ] **Step 2: Remove the test-plan context line from the docs-writer spawn block**

Old:
```
- Requirements: .dev/01-requirements.md (parse REQ: tokens for RTM)
- Solution plan: .dev/02-solution-plan.md
- Test plan: .dev/05-test-plan.md (if exists)
- Code review: .dev/03-code-review.md (if exists)
```

New:
```
- Requirements: .dev/01-requirements.md (parse REQ: tokens for RTM)
- Solution plan: .dev/02-solution-plan.md
- Code review: .dev/03-code-review.md (if exists)
```

- [ ] **Step 3: Remove the /al-dev-test timing note**

Old:
```
**Timing:** Usually run after `/al-dev-develop` and optionally after
`/al-dev-test`.
```

New:
```
**Timing:** Usually run after `/al-dev-develop`.
```

- [ ] **Step 4: Verify no test-plan or /al-dev-test references remain**

```bash
grep -n "05-test-plan\|al-dev-test" \
  profile-al-dev-shared/skills/al-dev-document/SKILL.md
```

Expected: no output.

---

### Task 7: Full Verification and Commit

- [ ] **Step 1: Verify al-dev-test is not in active skills**

```bash
ls profile-al-dev-shared/skills/ | grep al-dev-test
```

Expected: no output.

- [ ] **Step 2: Verify no test agents remain in active agents/**

```bash
ls profile-al-dev-shared/agents/ | grep -E "test-engineer|test-coverage"
```

Expected: no output.

- [ ] **Step 3: Scan active skills for any surviving references to archived items**

```bash
grep -r "al-dev-test\b\|test-coverage-reviewer\|test-engineer" \
  profile-al-dev-shared/skills/ --include="*.md"
```

Expected: no output. (The word "test" alone is fine in prose; this grep targets the specific skill/agent names.)

- [ ] **Step 4: Confirm archive contains all expected files**

```bash
ls profile-al-dev-shared/archived/skills/al-dev-test/
```

Expected:
```
SKILL.md
validate-test-plan.py
```

```bash
ls profile-al-dev-shared/archived/agents/
```

Expected:
```
al-dev-edge-case-test-engineer.md
al-dev-integration-test-engineer.md
al-dev-scenario-test-engineer.md
al-dev-test-coverage-reviewer.md
al-dev-unit-test-engineer.md
```

- [ ] **Step 5: Verify git status shows only expected changes**

```bash
git -C /Users/russelllaing/al-dev-shared status
```

Expected: staged renames for the 6 moved items (skill dir + 5 agents), plus modifications to the 4 active skill files and the new README. No unexpected deletions.

- [ ] **Step 6: Commit**

Stage all changes:

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/archived/ \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md \
  profile-al-dev-shared/skills/al-dev-help/SKILL.md \
  profile-al-dev-shared/skills/al-dev-document/SKILL.md
```

Commit:

```bash
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
chore(al-dev-shared): archive test skill and test-engineer agents

Move al-dev-test skill and 5 test-related agents to
profile-al-dev-shared/archived/ to reduce active plugin surface
while AL test codeunit workflow is not in use. Files are preserved
intact for future reinstatement.

Update al-dev-develop, al-dev-autonomous, al-dev-help, and
al-dev-document to remove references to archived items.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 7: Confirm commit succeeded**

```bash
git -C /Users/russelllaing/al-dev-shared log --oneline -1
```

Expected: your commit message appears as the most recent commit.
