# Plugin Health Top 5 — 2026-05-30 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address the five highest-ranked findings from the 2026-05-30 plugin health sweep: model fit corrections for five agents, three High-severity clarity gaps in al-dev-solution-architect, targeted clarity fixes in al-dev-develop and al-dev-developer, phase-label clarity in al-dev-review-develop, and splitting al-dev-commit-preflight into two single-concern agents.

**Architecture:** Five independent fix batches committed atomically. Tasks 1–4 are targeted edits to existing files; Task 5 creates two new agent files and updates the commit skill's dispatch block. No skill topology changes — the full atomization of al-dev-develop (Phase 1.5/4.5 extraction) and al-dev-fix (trivial/complex split) are deferred to a dedicated future plan.

**Tech Stack:** Markdown agent/skill definitions in `profile-al-dev-shared/`. All harness-agnostic vocabulary. No AL source files.

---

## File Map

| File | Action | Task |
|------|--------|------|
| `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md` | Edit model + scripted fixes clarity | 1 |
| `profile-al-dev-shared/agents/al-dev-expert-reviewer.md` | Edit model | 1 |
| `profile-al-dev-shared/agents/al-dev-performance-reviewer.md` | Edit model | 1 |
| `profile-al-dev-shared/agents/al-dev-security-reviewer.md` | Edit model | 1 |
| `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` | Edit Review Panel model label | 1 |
| `profile-al-dev-shared/agents/al-dev-solution-architect.md` | Edit 3 clarity gaps | 2 |
| `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` | Edit SYMBOL_PREFLIGHT_GATE precedence | 3 |
| `profile-al-dev-shared/agents/al-dev-developer.md` | Edit logical group + TDD hard-stop | 3 |
| `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` | Edit phase execution labels | 4 |
| `profile-al-dev-shared/agents/al-dev-commit-lint-fixer.md` | Create | 5 |
| `profile-al-dev-shared/agents/al-dev-commit-ooxml-validator.md` | Create | 5 |
| `profile-al-dev-shared/agents/al-dev-commit-preflight.md` | Delete | 5 |
| `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` | Edit Step 9.5 dispatch block | 5 |

---

## Task 1: Model Reassignments

**Files:**
- Edit: `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md` (line 7, line 44)
- Edit: `profile-al-dev-shared/agents/al-dev-expert-reviewer.md` (line 6)
- Edit: `profile-al-dev-shared/agents/al-dev-performance-reviewer.md` (line 6)
- Edit: `profile-al-dev-shared/agents/al-dev-security-reviewer.md` (line 6)
- Edit: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` (line 34)

**Rationale:** Commit-agent-execute is sequential bash with simple retry logic — no multi-step reasoning needed, downgrade saves cost. Three specialist reviewers do cross-file pattern analysis and design-level judgment — haiku is insufficient, upgrade to sonnet. The review-develop "Review Panel" label must match the actual model after upgrade.

- [ ] **Step 1: Read all five files to confirm current state**

```bash
grep -n "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
grep -n "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-expert-reviewer.md
grep -n "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-performance-reviewer.md
grep -n "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-security-reviewer.md
sed -n '33,36p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected:
- commit-agent-execute: `model: sonnet  # Upgraded from haiku: ...`
- expert-reviewer, performance-reviewer, security-reviewer: `model: haiku`
- review-develop line 34: `Three specialist agents (haiku):`

- [ ] **Step 2: Downgrade al-dev-commit-agent-execute model**

Edit `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md` line 7.

Old:
```yaml
model: sonnet  # Upgraded from haiku: multi-step commit orchestration with hook retry and error recovery requires multi-step reasoning
```

New:
```yaml
model: claude-haiku-4-5-20251001
```

- [ ] **Step 3: Add scripted fixes definition to al-dev-commit-agent-execute**

Edit `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md` around line 44.

Old:
```markdown
   - Attempt to fix issues if scripted fix available (e.g., lint fixes)
```

New:
```markdown
   - Attempt scripted fixes only: trailing whitespace (`sed -i '' 's/[ \t]*$//' <file>`), Python lint (`ruff check --fix <file>`). All other hook failures are recorded as HOOK_FAILURE without retry.
```

- [ ] **Step 4: Upgrade al-dev-expert-reviewer model**

Edit `profile-al-dev-shared/agents/al-dev-expert-reviewer.md` line 6.

Old:
```yaml
model: haiku
```

New:
```yaml
model: claude-sonnet-4-6
```

- [ ] **Step 5: Upgrade al-dev-performance-reviewer model**

Edit `profile-al-dev-shared/agents/al-dev-performance-reviewer.md` line 6.

Old:
```yaml
model: haiku
```

New:
```yaml
model: claude-sonnet-4-6
```

- [ ] **Step 6: Upgrade al-dev-security-reviewer model**

Edit `profile-al-dev-shared/agents/al-dev-security-reviewer.md` line 6.

Old:
```yaml
model: haiku
```

New:
```yaml
model: claude-sonnet-4-6
```

- [ ] **Step 7: Update Review Panel label in al-dev-review-develop**

Edit `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` line 34.

Old:
```markdown
Three specialist agents (haiku):
```

New:
```markdown
Three specialist agents (sonnet):
```

- [ ] **Step 8: Verify all model changes**

```bash
grep -n "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
grep -n "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-expert-reviewer.md
grep -n "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-performance-reviewer.md
grep -n "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-security-reviewer.md
sed -n '34p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected:
- commit-agent-execute: `model: claude-haiku-4-5-20251001`
- expert/performance/security: `model: claude-sonnet-4-6`
- review-develop line 34: `Three specialist agents (sonnet):`

- [ ] **Step 9: Verify scripted fixes definition**

```bash
grep -n "trailing whitespace\|scripted" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
```

Expected: Line showing the new `sed` and `ruff` definitions for scripted fixes.

- [ ] **Step 10: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/agents/al-dev-commit-agent-execute.md \
  profile-al-dev-shared/agents/al-dev-expert-reviewer.md \
  profile-al-dev-shared/agents/al-dev-performance-reviewer.md \
  profile-al-dev-shared/agents/al-dev-security-reviewer.md \
  profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(agents): reassign models — downgrade execute agent, upgrade reviewers

Downgrade al-dev-commit-agent-execute sonnet → haiku: task is sequential
bash calls with simple retry logic; no multi-step reasoning needed.

Upgrade al-dev-expert-reviewer, al-dev-performance-reviewer,
al-dev-security-reviewer haiku → sonnet: all three perform cross-file
pattern analysis and design-level judgment that exceeds haiku capability.

Add explicit "scripted fixes" definition to commit-agent-execute (clarity).
Update review panel model label in al-dev-review-develop to match upgrade.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 5 files changed.

---

## Task 2: Fix al-dev-solution-architect Clarity (3 High Gaps)

**Files:**
- Edit: `profile-al-dev-shared/agents/al-dev-solution-architect.md` (lines 44–66 for hierarchy, line 60 for testability gate, lines 130–132 for unverified field rule)

**Rationale:** The health sweep found 3 High clarity gaps that affect every `/al-dev-plan` invocation:
1. Research phase uses "strongest available" without a strict decision rule when multiple sources are available simultaneously.
2. "Design testability architecture (MANDATORY)" has no return-block gate verifying it was included.
3. `unverified` evidence source in Schema Mapping table has no decision rule (block vs. proceed).

- [ ] **Step 1: Read al-dev-solution-architect.md current state**

```bash
sed -n '39,70p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md
sed -n '126,138p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md
```

Expected: Workflow steps 1–10 visible (lines 39–65); Schema Mapping closing rule visible (lines 130–132).

- [ ] **Step 2: Add research source hierarchy decision rule**

Edit `profile-al-dev-shared/agents/al-dev-solution-architect.md`.

Find the research phase step 4 line that reads:
```markdown
4. **Research phase (MEDIUM/COMPLEX only):**
```

After the bullet point ending `...record `none` with a one-line rationale. This is not exact structural matching—only the best analogue the developer should inspect first.`, add a new bullet:

Old (lines 43–50, the entire step-4 sub-bullet starting with "Pattern references:"):
```markdown
   - Pattern references: For each object in the Object Design, locate the best existing
     analogue in the project using the strongest available evidence source: `AL LSP`
     when exposed by the active harness or adapter, otherwise `AL MCP`, otherwise
     scoped `text search`. Record the file path and line number as the `Pattern reference`.
     If no useful analogue exists, record `none` with a one-line rationale. This is not
     exact structural matching—only the best analogue the developer should inspect first.
```

New:
```markdown
   - Pattern references: For each object in the Object Design, locate the best existing
     analogue in the project. Use this strict evidence hierarchy — do not skip a higher tier
     if it is available: **AL LSP** (semantic correctness, preferred when harness exposes it)
     → **AL MCP** (base app / package symbols) → **text search** (pattern matching, weakest).
     Record the file path and line number as the `Pattern reference`.
     If no useful analogue exists, record `none` with a one-line rationale. This is not
     exact structural matching—only the best analogue the developer should inspect first.
```

- [ ] **Step 3: Add TESTABILITY_COMPLETE return-block gate**

Edit `profile-al-dev-shared/agents/al-dev-solution-architect.md`.

Old (line 60):
```markdown
6. **Design testability architecture (MANDATORY)** — identify dependencies, define interfaces, plan mocks (see project instructions)
```

New:
```markdown
6. **Design testability architecture (MANDATORY)** — identify dependencies, define interfaces, plan mocks (see project instructions). Add `TESTABILITY_COMPLETE: yes` to your return block after completing this step. If testability design cannot be completed, add `TESTABILITY_COMPLETE: no` and return without writing the plan — the architect must resolve before proceeding to implementation.
```

- [ ] **Step 4: Add unverified field decision rule**

Edit `profile-al-dev-shared/agents/al-dev-solution-architect.md`.

Old (lines 130–132):
```markdown
If a required external symbol is `unverified`, do not design code that depends
on guessing its signature or existence; call out the blocker in the plan.
```

New:
```markdown
If a required external symbol is `unverified`:
- **CRITICAL path field** (implementation cannot proceed without it): mark as `BLOCKED` in the Schema Mapping table and stop. Do not write implementation tasks — return the plan with a `BLOCKED` section listing the unverified fields and required resolution steps.
- **Optional field** (implementation can continue with an alternative): document the risk as a `HIGH` item in the Schema Mapping table and continue with a concrete alternative design.
```

- [ ] **Step 5: Verify all three changes**

```bash
grep -n "strict evidence hierarchy\|AL LSP.*AL MCP" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md | head -3
grep -n "TESTABILITY_COMPLETE" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md
grep -n "CRITICAL path field\|BLOCKED" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md | head -3
```

Expected: All three patterns found; each at the expected location.

- [ ] **Step 6: Verify line count preserved**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md
```

Expected: Line count increased by 6–10 lines relative to current (additions only, no deletions except the replaced lines).

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-solution-architect.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(agents): resolve 3 High clarity gaps in al-dev-solution-architect

1. Research source hierarchy: replace vague 'strongest available' with
   explicit AL LSP > AL MCP > text search decision rule (strict order).

2. Testability gate: add TESTABILITY_COMPLETE: yes|no to return block —
   agent must confirm testability design before writing implementation tasks.

3. Unverified field rule: distinguish CRITICAL-path fields (BLOCKED, stop)
   from optional fields (HIGH risk, continue with alternative design).

These gaps affect every /al-dev-plan invocation.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 1 file changed, ~10 lines added.

---

## Task 3: Fix al-dev-develop + al-dev-developer Clarity

**Files:**
- Edit: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` (lines 318–320, SYMBOL_PREFLIGHT_GATE spawn prompt)
- Edit: `profile-al-dev-shared/agents/al-dev-developer.md` (lines 45–47 TDD hard-stop, line 85 logical group)

**Rationale:** The SYMBOL_PREFLIGHT_GATE section in al-dev-develop's developer spawn prompt references both the knowledge file and an inline list without stating which wins if they diverge. The al-dev-developer agent says "hard stop for user review" three times in the TDD workflow without naming the mechanism. "Compile after each file or logical group" uses "logical group" without defining it.

- [ ] **Step 1: Read current state of both files**

```bash
sed -n '316,326p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
sed -n '43,50p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
sed -n '83,88p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
```

Expected:
- al-dev-develop lines 316–326: SYMBOL_PREFLIGHT_GATE section opening with "Follow `knowledge/al-symbol-pre-flight.md`..."
- al-dev-developer lines 43–50: TDD RED/GREEN/REFACTOR phases with "hard stop for user review"
- al-dev-developer lines 83–88: "Compile after each file or logical group"

- [ ] **Step 2: Add SYMBOL_PREFLIGHT_GATE precedence statement**

Edit `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`.

Old (lines 318–320):
```markdown
SYMBOL_PREFLIGHT_GATE — Complete BEFORE writing any AL code.
Follow `knowledge/al-symbol-pre-flight.md` for the full checklist.
Use the strongest available evidence source and label every item as
```

New:
```markdown
SYMBOL_PREFLIGHT_GATE — Complete BEFORE writing any AL code.
Follow `knowledge/al-symbol-pre-flight.md` for the full checklist; that file is
the authoritative source. If the inline list below and the knowledge file diverge,
the knowledge file takes precedence.
Use the strongest available evidence source and label every item as
```

- [ ] **Step 3: Replace TDD "hard stop" with TDD_CYCLE_GATE in al-dev-developer**

Edit `profile-al-dev-shared/agents/al-dev-developer.md`.

Old (lines 44–48):
```markdown
3. **For each test in spec:**
   - **RED Phase:** Write failing test, hard stop for user review
   - **GREEN Phase:** Implement code to pass test, hard stop for user review
   - **REFACTOR Phase:** Improve code quality, hard stop for user review
```

New:
```markdown
3. **For each test in spec:**
   - **RED Phase:** Write failing test, invoke `TDD_CYCLE_GATE` (present RED output, wait for user approval before GREEN)
   - **GREEN Phase:** Implement code to pass test, invoke `TDD_CYCLE_GATE` (present GREEN output, wait for user approval before REFACTOR)
   - **REFACTOR Phase:** Improve code quality, invoke `TDD_CYCLE_GATE` (present REFACTOR output, wait for user approval before next test)
```

- [ ] **Step 4: Define "logical group" in al-dev-developer**

Edit `profile-al-dev-shared/agents/al-dev-developer.md`.

Old (line 85):
```markdown
- Compile after each file or logical group
```

New:
```markdown
- Compile after each file or logical group (logical group = tables + their extensions, or a codeunit + its subscribers)
```

- [ ] **Step 5: Verify all three changes**

```bash
grep -n "authoritative source\|knowledge file takes precedence" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
grep -n "TDD_CYCLE_GATE" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
grep -n "logical group" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
```

Expected: All three patterns found; no "hard stop for user review" remaining in TDD workflow steps.

- [ ] **Step 6: Verify no "hard stop for user review" remains in TDD steps**

```bash
grep -n "hard stop for user review" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
```

Expected: No output (all three replaced with TDD_CYCLE_GATE invocations).

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/agents/al-dev-developer.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(skills,agents): resolve clarity gaps in develop skill and developer agent

al-dev-develop SKILL.md: add SYMBOL_PREFLIGHT_GATE precedence statement —
knowledge/al-symbol-pre-flight.md is authoritative when it diverges from
the inline list in the spawn prompt.

al-dev-developer agent: replace 'hard stop for user review' (×3 in TDD
workflow) with named TDD_CYCLE_GATE invocations matching the governance
token table. Define 'logical group' for compile frequency guidance.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 2 files changed.

---

## Task 4: Fix al-dev-review-develop Phase Execution Labels

**Files:**
- Edit: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` (6 phase headers + execution-order note)

**Rationale:** Phase headers are numbered 5, 8, 8.5, 6-7, 9, 10 to match a parent phase map, but run in non-sequential order. The existing note at line 45–46 partially addresses this but header numbers still mislead. Adding "(Run Nth)" labels to each header makes execution order immediately visible. This is the targeted bloat/clarity fix for action #1 without a full skill atomization.

- [ ] **Step 1: Confirm current phase header lines**

```bash
grep -n "^## Phase" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected output:
```
50:## Phase 5: Prepare Review Context
82:## Phase 8: Compile Verification
131:## Phase 8.5: Pre-Review Staging
141:## Phase 6-7: Dispatch Review Panel
172:## Phase 9: Write Code-Review Artifact
237:## Phase 10: Present Review Findings
```

- [ ] **Step 2: Update execution-order note (lines 45–46)**

Edit `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`.

Old (lines 45–46):
```markdown
Phases run in this order: **5 → 8 → 8.5 → 6-7 → 9 → 10**.
Phase headers are numbered to match the parent workflow's phase map; run them in the order above, not in header-number order.
```

New:
```markdown
Phases run in this order: **5 → 8 → 8.5 → 6-7 → 9 → 10** (see Run labels on each header).
Phase headers retain parent-workflow numbering; execute in the order shown, not by header number.
```

- [ ] **Step 3: Add (Run 1st) to Phase 5 header**

Edit `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`.

Old:
```markdown
## Phase 5: Prepare Review Context
```

New:
```markdown
## Phase 5 (Run 1st): Prepare Review Context
```

- [ ] **Step 4: Add (Run 2nd) to Phase 8 header**

Edit `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`.

Old:
```markdown
## Phase 8: Compile Verification
```

New:
```markdown
## Phase 8 (Run 2nd): Compile Verification
```

- [ ] **Step 5: Add (Run 3rd) to Phase 8.5 header**

Edit `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`.

Old:
```markdown
## Phase 8.5: Pre-Review Staging
```

New:
```markdown
## Phase 8.5 (Run 3rd): Pre-Review Staging
```

- [ ] **Step 6: Add (Run 4th) to Phase 6-7 header**

Edit `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`.

Old:
```markdown
## Phase 6-7: Dispatch Review Panel
```

New:
```markdown
## Phase 6-7 (Run 4th): Dispatch Review Panel
```

- [ ] **Step 7: Add (Run 5th) to Phase 9 header**

Edit `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`.

Old:
```markdown
## Phase 9: Write Code-Review Artifact
```

New:
```markdown
## Phase 9 (Run 5th): Write Code-Review Artifact
```

- [ ] **Step 8: Add (Run 6th) to Phase 10 header**

Edit `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`.

Old:
```markdown
## Phase 10: Present Review Findings
```

New:
```markdown
## Phase 10 (Run 6th): Present Review Findings
```

- [ ] **Step 9: Verify all six labels**

```bash
grep -n "^## Phase" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: All six headers now include "(Run Nth)" labels in the correct order (1st–6th).

- [ ] **Step 10: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(skills): add execution-order labels to al-dev-review-develop phase headers

Phase headers retain parent-workflow numbers (5, 8, 8.5, 6-7, 9, 10) for
cross-reference compatibility with al-dev-develop's Glossary, but now carry
(Run 1st) through (Run 6th) labels showing the actual execution sequence.

Resolves High clarity finding: non-sequential header order was misleading.
Targeted bloat/clarity fix; full atomization deferred to future plan.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 1 file changed, 8 lines modified.

---

## Task 5: Split al-dev-commit-preflight into Two Agents

**Files:**
- Create: `profile-al-dev-shared/agents/al-dev-commit-lint-fixer.md`
- Create: `profile-al-dev-shared/agents/al-dev-commit-ooxml-validator.md`
- Delete: `profile-al-dev-shared/agents/al-dev-commit-preflight.md`
- Edit: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` (Step 9.5 dispatch block, lines 407–444)

**Rationale:** al-dev-commit-preflight has two separable concerns: (1) text-file lint + whitespace fixing and (2) binary OOXML ZIP validation. Different domains, different outputs (LINT_FIXES vs OOXML_FAILURES), different expertise requirements. Splitting also resolves 2 High clarity issues stemming from the dual-concern design (baseline path and bash context ambiguity). Each new agent is haiku — mechanical single-domain tasks.

- [ ] **Step 1: Read current al-dev-commit-preflight.md and al-dev-commit SKILL.md Step 9.5**

```bash
cat /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-preflight.md
sed -n '405,445p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: Full preflight agent body; current Step 9.5 dispatching `al-dev-shared:al-dev-commit-preflight`.

- [ ] **Step 2: Create al-dev-commit-lint-fixer.md**

Write `profile-al-dev-shared/agents/al-dev-commit-lint-fixer.md`:

```markdown
---
description: >-
  Pre-flight lint and trailing-whitespace fixer for staged commit files. Runs
  Python lint (ruff), trailing whitespace fixes on text files, and line-count
  corruption detection. Returns LINT_FIXES. Dispatched sequentially by
  al-dev-commit (Step 9.5a) before OOXML validation. Applies fixes via Bash
  only; never uses Write or Edit on source files.
model: claude-haiku-4-5-20251001
tools: ["Bash", "Read"]
---

# Agent: al-dev-commit-lint-fixer

Run pre-flight lint and trailing whitespace fixes on staged source files before commit execution.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups from analysis phase (GROUP_N structured blocks with `files:` and `message:` fields) |

## Outputs

| Output | Description |
|--------|-------------|
| `LINT_FIXES` | Files re-staged after lint fixes (or `NONE`) |

⚠️ **CRITICAL:** Never use Write or Edit on staged source files. All fixes via Bash only. If a fix cannot be made via Bash, record as `LINT_FIX_FAILED` and stop.

## Phase: lint-preflight

### Step 1: Capture Baseline Line Counts

For each file in the approved groups, capture the pre-fix line count:

```bash
git diff --cached --name-only | while IFS= read -r f; do
  [ -f "$f" ] || continue
  printf '%s\t%d\n' "$f" "$(wc -l < "$f")" >> .git/.commit-baselines
done
```

If `.git/` does not exist in the current directory, use `.dev/commit-baselines` as the fallback path.

### Step 2: Python Lint Fix

For every `.py` file in the approved groups:

```bash
ruff check --fix <file> && ruff format <file> && git add <file>
```

### Step 3: Trailing Whitespace Fix (Text Files Only)

⚠️ **Regex MUST be `[ \t]+$` (horizontal whitespace only).** Never use `[[:space:]]+$` or `\s+$` — those include `\n`, collapsing entire file into one line.

Skip binary and OOXML files (`.docx`, `.xlsx`, `.pptx`, `.odt`). For all remaining staged text files:

```bash
git diff --cached --name-only | grep -v -E '\.(docx|xlsx|pptx|odt)$' | while IFS= read -r f; do
  sed -i '' 's/[ \t]*$//' "$f"
  git add "$f"
done
```

### Step 4: Corruption Detection

Compare post-fix line counts against the baseline captured in Step 1. If any file shrinks to ≤10% of its pre-fix baseline line count:
1. Restore the file: `git checkout HEAD -- <file>`
2. Record as `LINT_FIX_FAILED: <filename> (line count collapsed from N to M)`
3. Stop immediately

### Return Block (Step 5)

```text
LINT_FIXES: [file1, file2] (or NONE)
```
```

- [ ] **Step 3: Verify al-dev-commit-lint-fixer.md was created**

```bash
ls -la /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-lint-fixer.md
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-lint-fixer.md
```

Expected: File exists, ≥60 lines.

- [ ] **Step 4: Create al-dev-commit-ooxml-validator.md**

Write `profile-al-dev-shared/agents/al-dev-commit-ooxml-validator.md`:

```markdown
---
description: >-
  OOXML ZIP integrity validator for staged commit files. Validates .docx, .xlsx,
  .pptx, and .odt files using unzip integrity check. Returns OOXML_FAILURES.
  Dispatched sequentially by al-dev-commit (Step 9.5b) after lint preflight.
  Read-only: never modifies files.
model: claude-haiku-4-5-20251001
tools: ["Bash", "Read"]
---

# Agent: al-dev-commit-ooxml-validator

Validate OOXML file integrity on staged files before commit execution.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups from analysis phase (GROUP_N structured blocks with `files:` and `message:` fields) |

## Outputs

| Output | Description |
|--------|-------------|
| `OOXML_FAILURES` | OOXML files that failed ZIP validation with reason (or `NONE`) |

## Phase: ooxml-validate

### Step 1: Identify OOXML Files

For each file in the approved groups, collect files matching: `.docx`, `.xlsx`, `.pptx`, `.odt`.

If no OOXML files are present in the approved groups, return immediately:

```text
OOXML_FAILURES: NONE
```

### Step 2: ZIP Integrity Check

For each OOXML file:

```bash
unzip -t <file> > /dev/null 2>&1
echo $?
```

Exit code `0` = valid ZIP (OOXML file is intact).
Non-zero exit = corrupted ZIP. Record as: `<filename>: unzip exit code <N>`.

### Step 3: Return Block

If OOXML failures occurred:
```text
OOXML_FAILURES: [filename: unzip exit code N] (one entry per failed file)
```

If all files passed (or no OOXML files present):
```text
OOXML_FAILURES: NONE
```

If OOXML_FAILURES is not NONE, the calling skill must stop and require human resolution before re-staging.
```

- [ ] **Step 5: Verify al-dev-commit-ooxml-validator.md was created**

```bash
ls -la /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-ooxml-validator.md
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-ooxml-validator.md
```

Expected: File exists, ≥50 lines.

- [ ] **Step 6: Update al-dev-commit SKILL.md Step 9.5**

Read lines 405–445 of `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` to confirm the current Step 9.5 block, then replace it.

Old (lines 407–444):
```markdown
## Step 9.5 — Dispatch Preflight Agent

Dispatch `al-dev-shared:al-dev-commit-preflight` with the approved plan:

```text
Agent tool:
  agent: al-dev-shared:al-dev-commit-preflight
  description: "Pre-flight lint and OOXML validation"

Prompt:
  "Perform PREFLIGHT phase for git commit workflow.

   Phase: preflight

   APPROVED_PLAN:
   [paste the approved plan from Step 9]

   CRITICAL RULES:
   - NEVER use Write or Edit on staged source files — all fixes via Bash only
   - Record OOXML failures; do not proceed to commit for failed files

   Return output in exactly the format specified (LINT_FIXES, OOXML_FAILURES)."
```

If `OOXML_FAILURES` is not `NONE`, show:

```text
⚠️  OOXML VALIDATION FAILURE

The following files failed ZIP validation and cannot be committed:
[OOXML_FAILURES output]

Resolve these files (save in Microsoft Word, not via script), re-stage, and re-run.
```

Stop if any OOXML failures — do not proceed to Step 10.

Store the `LINT_FIXES` value from the preflight output for display in Step 11.
```

New:
```markdown
## Step 9.5 — Dispatch Preflight Agents

Run preflight sequentially: lint fixes first, then OOXML validation.

### Step 9.5a — Dispatch Lint Preflight Agent

Dispatch `al-dev-shared:al-dev-commit-lint-fixer` with the approved plan:

```text
Agent tool:
  agent: al-dev-shared:al-dev-commit-lint-fixer
  description: "Pre-flight lint and trailing whitespace fixes"

Prompt:
  "Perform LINT-PREFLIGHT phase for git commit workflow.

   APPROVED_PLAN:
   [paste the approved plan from Step 9]

   CRITICAL RULES:
   - NEVER use Write or Edit on staged source files — all fixes via Bash only
   - Skip binary and OOXML files in trailing-whitespace step
   - Stop immediately if corruption detected (line count collapses)

   Return output in exactly the format specified (LINT_FIXES)."
```

Store the `LINT_FIXES` value for display in Step 11.

### Step 9.5b — Dispatch OOXML Validation Agent

Dispatch `al-dev-shared:al-dev-commit-ooxml-validator` with the approved plan:

```text
Agent tool:
  agent: al-dev-shared:al-dev-commit-ooxml-validator
  description: "OOXML ZIP integrity validation"

Prompt:
  "Perform OOXML-VALIDATE phase for git commit workflow.

   APPROVED_PLAN:
   [paste the approved plan from Step 9]

   Return output in exactly the format specified (OOXML_FAILURES)."
```

If `OOXML_FAILURES` is not `NONE`, show:

```text
⚠️  OOXML VALIDATION FAILURE

The following files failed ZIP validation and cannot be committed:
[OOXML_FAILURES output]

Resolve these files (save in Microsoft Word, not via script), re-stage, and re-run.
```

Stop if any OOXML failures — do not proceed to Step 10.
```

- [ ] **Step 7: Verify Step 9.5 update in al-dev-commit SKILL.md**

```bash
grep -n "al-dev-commit-lint-fixer\|al-dev-commit-ooxml-validator\|al-dev-commit-preflight" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: Two hits for the new agent names; zero hits for `al-dev-commit-preflight`.

- [ ] **Step 8: Delete al-dev-commit-preflight.md**

```bash
git -C /Users/russelllaing/al-dev-shared rm profile-al-dev-shared/agents/al-dev-commit-preflight.md
```

Expected: File removed from working tree and staged for deletion.

- [ ] **Step 9: Commit all Task 5 changes**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/agents/al-dev-commit-lint-fixer.md \
  profile-al-dev-shared/agents/al-dev-commit-ooxml-validator.md \
  profile-al-dev-shared/skills/al-dev-commit/SKILL.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
feat(agents): split al-dev-commit-preflight into lint-fixer and ooxml-validator

Replace single dual-concern al-dev-commit-preflight agent with two
single-concern agents:

- al-dev-commit-lint-fixer: Python ruff lint, trailing whitespace (text files
  only, skips OOXML), line-count corruption detection; returns LINT_FIXES.

- al-dev-commit-ooxml-validator: ZIP integrity check for .docx/.xlsx/.pptx/.odt;
  read-only, returns OOXML_FAILURES.

Both assigned claude-haiku-4-5-20251001 (mechanical single-domain tasks).
al-dev-commit Step 9.5 updated to sequential dispatch (9.5a lint, 9.5b OOXML).

Resolves High scope-isolation finding. Split also fixes trailing-whitespace
binary-file corruption risk present in the original agent.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 3 files changed (2 added, 1 changed), al-dev-commit-preflight.md removed.

---

## Final Verification

Run after all 5 tasks complete:

```bash
# 1. All 4 commits landed
git -C /Users/russelllaing/al-dev-shared log --oneline -n 5

# 2. Model reassignments correct
grep "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
grep "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-expert-reviewer.md
grep "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-performance-reviewer.md
grep "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-security-reviewer.md

# 3. Solution-architect clarity gates present
grep -c "strict evidence hierarchy\|TESTABILITY_COMPLETE\|CRITICAL path field" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md

# 4. SYMBOL_PREFLIGHT_GATE precedence present
grep "knowledge file takes precedence" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md

# 5. TDD_CYCLE_GATE and logical group definition present
grep -c "TDD_CYCLE_GATE\|logical group = tables" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md

# 6. Phase run labels present in review-develop
grep "Run [0-9]" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md | wc -l

# 7. Preflight split: old gone, new agents exist
ls /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-lint-fixer.md
ls /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-ooxml-validator.md
ls /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-preflight.md 2>/dev/null && echo "FAIL: old file still exists" || echo "PASS: old file removed"

# 8. al-dev-commit no longer references al-dev-commit-preflight
grep "al-dev-commit-preflight" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md && echo "FAIL: old agent still referenced" || echo "PASS: old agent reference removed"
```

Expected results:
- 4 commits in log
- commit-agent-execute: `claude-haiku-4-5-20251001`; reviewers: `claude-sonnet-4-6`
- 3 patterns found in solution-architect
- Precedence statement found in al-dev-develop
- 2 patterns found in al-dev-developer
- 6 "Run N" labels in review-develop
- Two new agent files exist; old file removed; no stale reference in commit skill

---

## Scope Boundary

**In this plan:** Model reassignments, targeted clarity edits, phase execution labels, commit-preflight split.

**Deferred to future plan (too large for this batch):**
- Full atomization of al-dev-develop (extract Phase 1.5/4.5 as optional sub-skills)
- Full atomization of al-dev-review-develop (extract Phase 8 compile-verify as sub-skill)
- al-dev-fix split (trivial vs. complex paths)
- al-dev-plan preflight extraction (Phase 1.5/1.6)
- al-dev-commit partition (pre-flight vs. execute skills)
