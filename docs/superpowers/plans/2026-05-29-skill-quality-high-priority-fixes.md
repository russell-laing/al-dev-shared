# Skill Quality High-Priority Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all 16 High-severity findings from `docs/al-dev-skill-quality.md` across 9 skill files.

**Architecture:** Pure text edits to SKILL.md files plus two new knowledge extraction files. No code compilation required — verification is grep-based. Tasks 1–9 are mostly independent text fixes (one-line to paragraph-level), but Tasks 2 and 3 must run in sequence because they touch the same `al-dev-commit` section. Tasks 10–12 are structural refactors that create new knowledge files and update skill references.

**Tech Stack:** Markdown text editing only. Verification: `grep`, `wc -l`, forbidden-pattern scan, `git status`.

---

## File Structure

Files modified:
- `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` — 2 clarity fixes
- `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` — 1 clarity fix + 1 structural consolidation
- `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` — 1 decision-tree label fix
- `profile-al-dev-shared/skills/al-dev-interview/SKILL.md` — 1 GATE definition fix
- `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md` — 1 spawn-count contradiction fix
- `profile-al-dev-shared/skills/al-dev-perf/SKILL.md` — 1 skill-author instruction removal
- `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md` — 1 Step 1.5 navigation fix
- `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` — 4 clarity fixes + Scope Gate extraction + dead-branch refactor
- `profile-al-dev-shared/skills/al-dev-consolidate/SKILL.md` — extraction reference update

Files created:
- `profile-al-dev-shared/knowledge/scope-expansion-gate.md` — extracted gate rules (Task 10)
- `profile-al-dev-shared/knowledge/consolidate-extraction-patterns.md` — extracted bash patterns (Task 12)

---

## Task 1: Fix al-dev-plan Phase 1 and Phase 2 clarity

**Source findings:** [High] Phase 1 Input Validation Gate "vague word" undefined; [High] Phase 2 fallback list has no ordering guidance.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md:81-85` (Phase 1 gate)
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md:219-221` (Phase 2 fallback)

- [ ] **Step 1: Read the file**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-plan/SKILL.md
  ```
  Confirm the file exists and note the line count for post-edit verification.

- [ ] **Step 2: Fix Phase 1 Input Validation Gate (add "sufficient context" definition)**

  In `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, find this text in the Phase 1 Input Validation Gate:

  ```text
  - If $ARGUMENTS is empty, missing, or only a vague word (e.g. "plan", "help", "this") with no feature context — **STOP immediately**. Ask the user exactly one question:
  ```

  Replace with:

  ```text
  - If $ARGUMENTS is empty, missing, or only a vague word (e.g. "plan", "help", "this") with no feature context — **STOP immediately**. Sufficient context requires: (1) a feature name or description, AND (2) at least one functional requirement. Example: "Add a credit limit check during posting." Ask the user exactly one question:
  ```

- [ ] **Step 3: Fix Phase 2 default fallback list (add ordering guidance)**

  In `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, find this text:

  ```text
  Default fallback if nothing more specific fits: table
  extension approach / separate table approach /
  event-driven approach.
  ```

  Replace with:

  ```text
  Default fallback if nothing more specific fits — use these debate angles in order:
  (1) table extension (conservative, builds on base app);
  (2) separate table (isolated scope, decoupled from base);
  (3) event-driven (flexible, extensible, minimal coupling).
  ```

- [ ] **Step 4: Verify changes are present**

  ```bash
  grep -n "Sufficient context requires" profile-al-dev-shared/skills/al-dev-plan/SKILL.md
  grep -n "table extension (conservative" profile-al-dev-shared/skills/al-dev-plan/SKILL.md
  ```

  Expected: both lines found.

- [ ] **Step 5: Forbidden pattern scan**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/skills/al-dev-plan/SKILL.md
  ```

  Expected: no matches.

- [ ] **Step 6: Commit**

  ```bash
  git add profile-al-dev-shared/skills/al-dev-plan/SKILL.md
  git commit -m "fix(skill): clarify al-dev-plan Phase 1 gate and Phase 2 fallback ordering"
  ```

---

## Task 2: Fix al-dev-commit Step 4a AL-affecting file definition

**Source finding:** [High] "AL-affecting staged set" undefined — the gate condition uses vague language.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md:141-142` (Step 4a gate condition)

- [ ] **Step 1: Read the file**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-commit/SKILL.md
  ```

- [ ] **Step 2: Replace vague gate condition with explicit file type list**

  In `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`, find:

  ```text
  Run this gate only when the staged set includes `.al` files or other files that can affect AL compilation.
  Skip it for docs-only or other non-AL staged changes.
  ```

  Replace with:

  ```text
  Run this gate when staged changes include any `.al`, `app.json`, or `.al.json` files.
  Skip for pure documentation (`.md`, `.txt`), changelog, or manifest-only edits.
  ```

- [ ] **Step 3: Verify**

  ```bash
  grep -n "app\.json" profile-al-dev-shared/skills/al-dev-commit/SKILL.md
  grep -n "\.al\.json" profile-al-dev-shared/skills/al-dev-commit/SKILL.md
  ```

  Expected: both lines found in Step 4a.

- [ ] **Step 4: Forbidden pattern scan**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/skills/al-dev-commit/SKILL.md
  ```

  Expected: no matches.

- [ ] **Step 5: Commit**

  ```bash
  git add profile-al-dev-shared/skills/al-dev-commit/SKILL.md
  git commit -m "fix(skill): define AL-affecting file types explicitly in al-dev-commit Step 4a"
  ```

---

## Task 3: Consolidate al-dev-commit Steps 4 and 4a

**Source finding:** [High] Steps 4 and 4a cover overlapping staged-file concerns and should be consolidated into a single staged-file verification phase.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` (Steps 4 and 4a)

- [ ] **Step 1: Read the file to load it before editing**

  Read `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` and note:
  - The exact text of the current `## Step 4 — Check Staged Files` section
  - The exact text of the current `## Step 4a — Pre-Commit Compile Verification` section

- [ ] **Step 2: Replace Steps 4 and 4a with a single unified Step 4**

  In `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`, find the entire block from `## Step 4 — Check Staged Files` through the end of `## Step 4a — Pre-Commit Compile Verification` (the line `5. Only continue to the existing commit workflow when the compile result shows zero errors`), and replace the two separate sections with this single section:

  ```markdown
  ## Step 4 — Verify Staged Files

  Check what is staged:

  ```bash
  git diff --cached --name-only --diff-filter=ACMRDT
  ```

  If empty:

  Tell the user: "No staged files found. Use `git add` to stage
  your changes, then run `/al-dev-commit` again."

  **Stop.**

  **AL-affecting staged set check:** Run this compile gate when staged changes include any
  `.al`, `app.json`, or `.al.json` files. Skip for pure documentation (`.md`, `.txt`),
  changelog, or manifest-only edits.

  ```bash
  AL_STAGED=$(git diff --cached --name-only --diff-filter=ACMRDT \
    | grep -E '(^|/)(app\.json|[^/]+\.al|[^/]+\.al\.json)$')
  ```

  If `$AL_STAGED` is non-empty, run the compile gate before dispatching commit agents:

  1. Apply `knowledge/compile-lint-procedure.md`
  2. Produce a fresh `.dev/compile-errors.log` if the current log is absent or stale
  3. Read the log and report:
     - `Errors:` count
     - `Warnings:` count
     - up to 3 representative diagnostics
     - `Detailed log:` `.dev/compile-errors.log`
  4. If `Errors > 0`, stop the commit workflow and tell the user the staged changes are not ready to commit
  5. Only continue when the compile result shows zero errors

  Critical rule: never claim the staged set is ready, "clean compile", or "zero errors"
  without reading the actual success evidence required by
  `knowledge/artifact-contracts.md` for the current staged state.
  ```

- [ ] **Step 3: Verify the old Step 4a header is gone and Step 4 contains the compile gate**

  ```bash
  grep -n "Step 4" profile-al-dev-shared/skills/al-dev-commit/SKILL.md
  ```

  Expected: `## Step 4 — Verify Staged Files` present; `## Step 4a` absent.

  ```bash
  grep -n "AL_STAGED" profile-al-dev-shared/skills/al-dev-commit/SKILL.md
  ```

  Expected: the new `AL_STAGED` check found inside Step 4.

- [ ] **Step 4: Forbidden pattern scan**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/skills/al-dev-commit/SKILL.md
  ```

  Expected: no matches (the `$(date +%Y-%m-%d)` shell expressions in agent prompts are fine — only literal string `YYYY-MM-DD` is forbidden).

- [ ] **Step 5: Commit**

  ```bash
  git add profile-al-dev-shared/skills/al-dev-commit/SKILL.md
  git commit -m "fix(skill): consolidate al-dev-commit Steps 4 and 4a into unified staged-file verification"
  ```

---

## Task 4: Fix al-dev-fix decision tree node labels

**Source finding:** [High] Decision Tree diagram nodes lack decision labels (e.g., "TRIVIAL?", "NON-TRIVIAL?").

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md:280-282` (Decision Tree)

- [ ] **Step 1: Read the file**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-fix/SKILL.md
  ```

- [ ] **Step 2: Add decision label to the "Analyze complexity" node**

  In `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`, find:

  ```text
  User: "/fix [issue]"
      ↓
  You: Analyze complexity
      ↓
      ├─→ TRIVIAL (simple, obvious)
  ```

  Replace with:

  ```text
  User: "/fix [issue]"
      ↓
  You: Analyze complexity [Is it TRIVIAL or NON-TRIVIAL?]
      ↓
      ├─→ TRIVIAL (simple, obvious, single-file)
  ```

- [ ] **Step 3: Verify**

  ```bash
  grep -n "TRIVIAL or NON-TRIVIAL" profile-al-dev-shared/skills/al-dev-fix/SKILL.md
  ```

  Expected: line found in the Decision Tree section.

- [ ] **Step 4: Forbidden pattern scan**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/skills/al-dev-fix/SKILL.md
  ```

  Expected: no matches.

- [ ] **Step 5: Commit**

  ```bash
  git add profile-al-dev-shared/skills/al-dev-fix/SKILL.md
  git commit -m "fix(skill): add decision labels to al-dev-fix decision tree diagram"
  ```

---

## Task 5: Fix al-dev-interview GATE definition

**Source finding:** [High] Phase 2 GATE "signalling completion" is undefined — the agent has no explicit completion signal to emit.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-interview/SKILL.md:73-75` (Phase 2 GATE)

- [ ] **Step 1: Read the file**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-interview/SKILL.md
  ```

- [ ] **Step 2: Define the completion signal**

  In `profile-al-dev-shared/skills/al-dev-interview/SKILL.md`, find:

  ```text
  5. **GATE: The interview agent must complete all categories
     before signalling completion. Upon agent return, proceed
     to Phase 3.**
  ```

  Replace with:

  ```text
  5. **GATE: The interview agent must explicitly state "INTERVIEW COMPLETE" and
     confirm questions were asked in all 11 categories listed above. Upon this
     explicit signal, proceed to Phase 3.**
  ```

- [ ] **Step 3: Verify**

  ```bash
  grep -n "INTERVIEW COMPLETE" profile-al-dev-shared/skills/al-dev-interview/SKILL.md
  ```

  Expected: line found in Phase 2.

- [ ] **Step 4: Forbidden pattern scan**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/skills/al-dev-interview/SKILL.md
  ```

  Expected: no matches.

- [ ] **Step 5: Commit**

  ```bash
  git add profile-al-dev-shared/skills/al-dev-interview/SKILL.md
  git commit -m "fix(skill): define explicit INTERVIEW COMPLETE signal in al-dev-interview GATE"
  ```

---

## Task 6: Fix al-dev-investigate spawn count contradiction

**Source finding:** [High] Step 4 says "if ≤2 hypotheses, spawn 1 agent" then immediately says "Spawn 2 Explore agents in parallel" — contradictory without a complete decision tree.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md:164-168` (Step 4 routing)

- [ ] **Step 1: Read the file**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
  ```

- [ ] **Step 2: Replace contradictory spawn instructions with a clear decision table**

  In `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`, find:

  ```text
  Route by hypothesis count: if ≤2 hypotheses, spawn 1 agent with all hypotheses. If 3–4 hypotheses, spawn 2 agents in parallel, assigning 2 hypotheses each:

  Spawn 2 Explore agents in parallel, assigning 2 hypotheses each:
  ```

  Replace with:

  ```text
  Route by hypothesis count:
  - **1–2 hypotheses:** spawn 1 agent with all hypotheses.
  - **3–4 hypotheses:** spawn 2 agents in parallel (H1+H2 → agent 1; H3+H4 → agent 2).
  - **5+ hypotheses:** spawn 3 agents, distributing hypotheses evenly.
  ```

  Note: the immediately following agent spawn block (starting with ` ```text ` and `Spawn an explore agent:`) remains unchanged — it is the template for the agent prompt, not a literal "always spawn 2" instruction.

- [ ] **Step 3: Verify old contradictory line is gone**

  ```bash
  grep -n "Spawn 2 Explore agents in parallel" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
  ```

  Expected: no matches.

  ```bash
  grep -n "3–4 hypotheses.*agent 1" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
  ```

  Expected: line found.

- [ ] **Step 4: Forbidden pattern scan**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
  ```

  Expected: no matches.

- [ ] **Step 5: Commit**

  ```bash
  git add profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
  git commit -m "fix(skill): resolve contradictory spawn count in al-dev-investigate Step 4"
  ```

---

## Task 7: Fix al-dev-perf skill-author instruction in agent prompt

**Source finding:** [High] "Paste the full content of that file here before dispatching" is a skill-author instruction embedded inside an agent dispatch prompt — models will read it as an instruction to themselves.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-perf/SKILL.md` (Step 2 prompt)

- [ ] **Step 1: Read the file**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-perf/SKILL.md
  ```

- [ ] **Step 2: Add a pre-dispatch read step before the spawn block in Step 2**

  In `profile-al-dev-shared/skills/al-dev-perf/SKILL.md`, find the line that begins `### Step 2 — Spawn Performance Analysis Agent` and insert this pre-dispatch step immediately before the `> Pattern:` line:

  **Before:**
  ```text
  ### Step 2 — Spawn Performance Analysis Agent

  > Pattern: `knowledge/explore-subagent-pattern.md` — Steps A–D.
  > Performance-specific prompt content is below.

  ```text
  Spawn an explore agent:
  ```

  **After:**
  ```text
  ### Step 2 — Spawn Performance Analysis Agent

  Before assembling the dispatch prompt, read
  `knowledge/perf-anti-patterns-prompt.md` and hold its full content as
  `PERF_PATTERNS` in working memory. Do not read any other file at this step.

  > Pattern: `knowledge/explore-subagent-pattern.md` — Steps A–D.
  > Performance-specific prompt content is below.

  ```text
  Spawn an explore agent:
  ```

- [ ] **Step 3: Remove the skill-author instruction from the agent prompt**

  In `profile-al-dev-shared/skills/al-dev-perf/SKILL.md`, find inside the Step 2 agent prompt block:

  ```text
     Anti-patterns to find and 'Do NOT flag' exclusions: See `knowledge/perf-anti-patterns-prompt.md`. Paste the full content of that file here before dispatching.
  ```

  Replace with:

  ```text
     Anti-patterns to find and 'Do NOT flag' exclusions:
     [PERF_PATTERNS — content of knowledge/perf-anti-patterns-prompt.md loaded above]
  ```

- [ ] **Step 4: Verify the instruction is removed**

  ```bash
  grep -n "Paste the full content" profile-al-dev-shared/skills/al-dev-perf/SKILL.md
  ```

  Expected: no matches.

  ```bash
  grep -n "PERF_PATTERNS" profile-al-dev-shared/skills/al-dev-perf/SKILL.md
  ```

  Expected: two matches (one in pre-dispatch step, one in the prompt).

- [ ] **Step 5: Forbidden pattern scan**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/skills/al-dev-perf/SKILL.md
  ```

  Expected: no matches.

- [ ] **Step 6: Commit**

  ```bash
  git add profile-al-dev-shared/skills/al-dev-perf/SKILL.md
  git commit -m "fix(skill): move perf-anti-patterns read to pre-dispatch step in al-dev-perf"
  ```

---

## Task 8: Fix al-dev-ticket Step 1.5 navigation clarity

**Source finding:** [High] Step 1 includes "skip to Step 1.5" but the Step 1.5 header position is unclear in the document flow due to mixed "Phase"/"Step" nomenclature and a section separator before it.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md` (Step 1 navigation bullet)

- [ ] **Step 1: Read the file**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-ticket/SKILL.md
  ```

- [ ] **Step 2: Make the skip instruction explicitly reference the section heading**

  In `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md`, find:

  ```text
  - **`search <terms>` or non-numeric text**: this is a keyword
    search — skip to Step 1.5.
  ```

  Replace with:

  ```text
  - **`search <terms>` or non-numeric text**: this is a keyword
    search — skip to **Step 1.5 — Search Tickets** (the section immediately following this one).
  ```

- [ ] **Step 3: Verify**

  ```bash
  grep -n "Step 1.5 — Search Tickets" profile-al-dev-shared/skills/al-dev-ticket/SKILL.md
  ```

  Expected: two matches — one in the skip instruction (Step 1) and one as the section header.

- [ ] **Step 4: Forbidden pattern scan**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/skills/al-dev-ticket/SKILL.md
  ```

  Expected: no matches.

- [ ] **Step 5: Commit**

  ```bash
  git add profile-al-dev-shared/skills/al-dev-ticket/SKILL.md
  git commit -m "fix(skill): clarify Step 1.5 navigation reference in al-dev-ticket Step 1"
  ```

---

## Task 9: Fix al-dev-develop clarity issues (4 High findings)

**Source findings:**
1. [High] "required" external procedure undefined in Phase 1.5
2. [High] Phase 8 Compile-Verify Loop glossary entry missing success stop condition
3. [High] Scope Expansion Gate missing else clause (what to do when all edits are in-scope)
4. [High] Phase 3 spawn prompt Scope Expansion Gate missing explicit blocking language

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` (4 locations)

- [ ] **Step 1: Read the file and note line count**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

- [ ] **Step 2: Define "required" procedure in Phase 1.5**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find:

  ```text
  If any required external procedure is NOT VERIFIED, do not spawn
  developers for code that depends on that signature. Stop and report the
  unverified required signature to the orchestrator or user.
  ```

  Replace with:

  ```text
  A procedure is "required" if it is explicitly referenced in the approved solution plan
  and the assigned developer task must call it. If any required external procedure is
  NOT VERIFIED, do not spawn developers for code that depends on that signature.
  Stop and report the unverified required signature to the orchestrator or user.
  ```

- [ ] **Step 3: Add success stop condition to Phase 8 Compile-Verify Loop glossary entry**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find:

  ```text
  **Phase 8 Compile-Verify Loop:** Extended compilation strategy used
  in autonomous mode. Runs up to 5 sequential compile-fix-compile
  cycles with detailed error tracking per attempt. After each compile,
  parses errors, spawns a developer to fix them, and re-compiles.
  Stops after 5 failed attempts and escalates to the user.
  ```

  Replace with:

  ```text
  **Phase 8 Compile-Verify Loop:** Extended compilation strategy used
  in autonomous mode. Runs up to 5 sequential compile-fix-compile
  cycles with detailed error tracking per attempt. After each compile,
  parses errors, spawns a developer to fix them, and re-compiles.
  Stop when: (1) compilation succeeds with zero errors, OR (2) 5 attempts
  exhausted. If exhausted, escalate to the user with the final compile error log.
  ```

- [ ] **Step 4: Add else clause to the main Scope Expansion Gate section**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find:

  ```text
  **What does NOT count as "out of scope":**

  - Cosmetic adjustments inside an in-scope edit (whitespace,
    formatter output)
  - Importing a dependency required to implement an in-scope change

  This gate is passed verbatim into every developer agent dispatch
  in Phase 3 so the rule propagates to subagents.
  ```

  Replace with:

  ```text
  **What does NOT count as "out of scope":**

  - Cosmetic adjustments inside an in-scope edit (whitespace,
    formatter output)
  - Importing a dependency required to implement an in-scope change

  If no out-of-scope changes are proposed, proceed with the edits.

  This gate is passed verbatim into every developer agent dispatch
  in Phase 3 so the rule propagates to subagents.
  ```

- [ ] **Step 5: Add blocking language to the Phase 3 spawn prompt gate**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find (inside the Phase 3 developer spawn prompt block):

  ```text
  Wait for per-item decision before resuming. Do NOT silently
  expand scope by fixing encountered lint warnings, deprecated
  APIs, or unrelated issues not named in the plan.
  ```

  Replace with:

  ```text
  Wait for per-item decision before resuming. Do NOT continue writing
  code until the user confirms each item. Do NOT silently expand scope
  by fixing encountered lint warnings, deprecated APIs, or unrelated
  issues not named in the plan.
  ```

- [ ] **Step 6: Verify all four changes**

  ```bash
  grep -n "A procedure is .required. if it is explicitly" \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  grep -n "compilation succeeds with zero errors" \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  grep -n "no out-of-scope changes are proposed" \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  grep -n "Do NOT continue writing" \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: each grep returns exactly one match.

- [ ] **Step 7: Forbidden pattern scan**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: no matches.

- [ ] **Step 8: Commit**

  ```bash
  git add profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  git commit -m "fix(skill): clarify required-procedure definition, Phase 8 stop conditions, and Scope Gate else clause in al-dev-develop"
  ```

---

## Task 10: Extract Scope Expansion Gate to knowledge/

**Source finding:** [High] Scope Expansion Gate is stated twice verbatim in al-dev-develop — 60+ lines duplicated in the skill body and in the developer spawn prompt.

**Files:**
- Create: `profile-al-dev-shared/knowledge/scope-expansion-gate.md`
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` (main gate section + Phase 3 spawn prompt)

- [ ] **Step 1: Read al-dev-develop to confirm current gate content**

  Read `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` and locate:
  - The main `## Scope Expansion Gate` section (lines ~104–141)
  - The inline gate inside the Phase 3 developer spawn prompt (the `SCOPE EXPANSION GATE:` block starting at the `SCOPE EXPANSION GATE:` label inside the backtick-fenced block)

- [ ] **Step 2: Create knowledge/scope-expansion-gate.md**

  Write `profile-al-dev-shared/knowledge/scope-expansion-gate.md` with this content:

  ```markdown
  # Scope Expansion Gate

  A governance checkpoint enforced during development that prevents out-of-scope
  changes. Before editing any file or line not explicitly named in the approved
  solution plan, the developer must stop and present proposed changes to the user
  for per-item approval. Prevents scope creep and ensures the solution stays true
  to the plan.

  ## Gate Procedure

  BEFORE editing a file or line not explicitly named in the approved plan:

  1. **Stop** — do not invoke the edit tool yet.
  2. List the proposed out-of-scope change(s) as numbered items:

     ```text
     **Proposed out-of-scope changes:**
     1. [file:line] — [what would change and why]
     2. [file:line] — [what would change and why]
     ```

  3. Present to the user with this exact prompt:
     "These changes are outside the approved plan. Approve, reject,
     or defer each. Reply with item numbers (e.g., '1 approve, 2 defer')."
  4. Wait for per-item decision before resuming. Do NOT continue writing code
     until the user confirms each item.

  If no out-of-scope changes are proposed, proceed with the edits.

  ## What Counts as "Out of Scope"

  - New file not listed in the plan
  - Edit to a procedure, field, or object not referenced in the plan, even if
    it is in a file the plan does name
  - Fixing an "encountered" issue (lint warning, deprecated API, unrelated bug)
    that the plan did not call out

  ## What Does NOT Count as "Out of Scope"

  - Cosmetic adjustments inside an in-scope edit (whitespace, formatter output)
  - Importing a dependency required to implement an in-scope change

  ## Propagation

  This gate applies to the orchestrating skill and to every spawned developer
  agent. Include this gate (or a reference to this file) in every developer
  spawn prompt so the rule propagates to subagents.
  ```

- [ ] **Step 3: Verify the knowledge file was written**

  ```bash
  ls -la profile-al-dev-shared/knowledge/scope-expansion-gate.md
  wc -l profile-al-dev-shared/knowledge/scope-expansion-gate.md
  ```

  Expected: file exists, non-empty (25+ lines).

- [ ] **Step 4: Replace the main Scope Expansion Gate section in al-dev-develop with a reference**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find and replace the entire `## Scope Expansion Gate` section (from `## Scope Expansion Gate` through `This gate is passed verbatim into every developer agent dispatch`... including the sentence about Phase 3):

  Replace the entire section body with:

  ```markdown
  ## Scope Expansion Gate

  The full gate rules (procedure, in-scope/out-of-scope definitions, and propagation
  requirement) are in `knowledge/scope-expansion-gate.md`. Read it before dispatching
  any developer.

  Summary: BEFORE editing any file or line not in the approved plan, stop, list
  proposed out-of-scope changes as numbered items, present to the user for per-item
  approval, and wait before resuming. If no out-of-scope changes are proposed,
  proceed.
  ```

- [ ] **Step 5: Replace the inline gate block in the Phase 3 developer spawn prompt**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, inside the Phase 3 developer spawn prompt (the backtick-fenced `text` block), find the entire `SCOPE EXPANSION GATE:` paragraph (from `SCOPE EXPANSION GATE: Before editing any file...` through `...or unrelated issues not named in the plan.`).

  Replace that block with:

  ```text
  SCOPE EXPANSION GATE: Apply the full gate procedure from
  `knowledge/scope-expansion-gate.md`. Before editing any file or line
  not in the plan: stop, list proposed changes, present to the user,
  and wait for per-item approval. Do NOT continue writing code until
  confirmed. Do NOT silently fix lint warnings, deprecated APIs, or
  unrelated issues not named in the plan.
  ```

- [ ] **Step 6: Verify old verbose gate text is removed from both locations**

  ```bash
  grep -c "What counts as .out of scope" \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: 0 (the detailed rules now live in knowledge/).

  ```bash
  grep -n "scope-expansion-gate.md" \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: 2 matches (one in the main Gate section, one in the Phase 3 spawn prompt).

- [ ] **Step 7: Forbidden pattern scan on both files**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/knowledge/scope-expansion-gate.md \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: no matches.

- [ ] **Step 8: Commit**

  ```bash
  git add profile-al-dev-shared/knowledge/scope-expansion-gate.md \
          profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  git commit -m "fix(skill): extract Scope Expansion Gate to knowledge/ and replace duplicated body in al-dev-develop"
  ```

---

## Task 11: Refactor al-dev-develop autonomous dead-branch conditions

**Source finding:** [High] Dead-branch conditions "Skip this phase if `--autonomous` is not in `$ARGUMENTS`" appear in Phases 1.5 and 4.5, creating always-skipped code paths in normal mode since Phase 1 already handles the routing.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` (Phase 1.5 and Phase 4.5 headers)

**Note:** Phase 1 already contains a clean autonomous mode detection block that routes to Phases 1.5 and 4.5 conditionally. The "Skip this phase if" guards in 1.5 and 4.5 are redundant and create dead-branch confusion. The fix is to remove the skip guards and replace the phase headers with clear "Autonomous Mode Only" labels so normal-mode readers can skip without confusion.

- [ ] **Step 1: Read the file**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

- [ ] **Step 2: Replace Phase 1.5 dead-branch guard with an Autonomous-Mode heading note**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find:

  ```text
  ## Phase 1.5: Signature Verification (--autonomous only)

  Skip this phase if `--autonomous` is not in `$ARGUMENTS`.

  Before dispatching any developer, verify every external procedure
  ```

  Replace with:

  ```text
  ## Phase 1.5: Signature Verification (Autonomous Mode — activated by Phase 1)

  Phase 1 routes here when `--autonomous` is present in `$ARGUMENTS`. In standard
  mode, Phase 1 skips this phase entirely and proceeds to Phase 2.

  Before dispatching any developer, verify every external procedure
  ```

- [ ] **Step 3: Replace Phase 4.5 dead-branch guard with an Autonomous-Mode heading note**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find:

  ```text
  ## Phase 4.5: Static Validation (--autonomous only)

  Skip this phase if `--autonomous` is not in `$ARGUMENTS`.

  Run these checks on all newly created AL files before the
  review team is spawned.
  ```

  Replace with:

  ```text
  ## Phase 4.5: Static Validation (Autonomous Mode — activated by Phase 1)

  Phase 1 routes here when `--autonomous` is present in `$ARGUMENTS`. In standard
  mode, Phase 1 skips this phase entirely and proceeds to review dispatch.

  Run these checks on all newly created AL files before the
  review team is spawned.
  ```

- [ ] **Step 4: Verify old "Skip this phase if" guards are removed**

  ```bash
  grep -n "Skip this phase if" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: no matches.

  ```bash
  grep -n "Autonomous Mode — activated by Phase 1" \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: 2 matches (one in Phase 1.5, one in Phase 4.5).

- [ ] **Step 5: Forbidden pattern scan**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: no matches.

- [ ] **Step 6: Commit**

  ```bash
  git add profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  git commit -m "fix(skill): replace dead-branch skip guards in al-dev-develop Phases 1.5 and 4.5 with routing notes"
  ```

---

## Task 12: Extract al-dev-consolidate bash patterns to knowledge/

**Source finding:** [High] Phase 2 spans 120+ lines with 5 extraction command groups (A–E) each repeating the same bash pattern (headings + verdict lines + first-N-lines-per-section).

**Files:**
- Create: `profile-al-dev-shared/knowledge/consolidate-extraction-patterns.md`
- Modify: `profile-al-dev-shared/skills/al-dev-consolidate/SKILL.md` (Phase 2 group sections)

- [ ] **Step 1: Read al-dev-consolidate to understand Phase 2 structure**

  Read `profile-al-dev-shared/skills/al-dev-consolidate/SKILL.md` Phase 2 (the Group A through Persistent sections) and identify the repeated patterns:
  - All groups run `grep '^#' "$file"` (heading extraction)
  - Groups A and C use a per-section awk pattern (differing only in `remaining=N`)
  - Groups D and Persistent use `grep -E '^✅|^❌|...'` for verdict lines

- [ ] **Step 2: Create knowledge/consolidate-extraction-patterns.md**

  Write `profile-al-dev-shared/knowledge/consolidate-extraction-patterns.md` with this content:

  ```markdown
  # Consolidate Extraction Patterns

  Reusable bash patterns for `al-dev-consolidate` Phase 2 artifact extraction.
  All extraction is command-output-only — never read full file content into context.

  ## Pattern: Heading Extraction (all groups)

  Extract all headings from a file. Used as the first extraction in every group.

  ```bash
  grep '^#' "$file"
  ```

  ## Pattern: First-N-Lines-Per-Section (Groups A and C)

  Extract the first N non-heading lines under each `##` heading.
  Set `remaining=N` for the desired line count (Group A uses 3; Group C uses 5).

  ```bash
  awk '
    /^## / { in_section=1; remaining=N; next }
    /^#/   { in_section=0 }
    in_section && remaining > 0 { print; remaining-- }
  ' "$file"
  ```

  Replace `N` with `3` for Group A (core workflow) or `5` for Group C (ticket context).

  ## Pattern: Governance Token Count (Group A only)

  Count governance tokens used for traceability reporting.

  ```bash
  for token in REQ ACC TEST DEC IMP DEP RISK; do
    n=$(grep -c "${token}-\|${token}:" "$file" 2>/dev/null || echo 0)
    [ "$n" -gt 0 ] && echo "${token}: $n"
  done
  ```

  ## Pattern: Verdict / Phase Lines (Groups D and Persistent)

  Extract verdict lines, phase markers, and status headers.

  ```bash
  grep -E \
    '^✅|^❌|^Phase [0-9]|^Status:|^Outcome:|\*\*(Verdict|Decision|Result)\*\*' \
    "$file" | head -20
  ```

  ## Pattern: Mermaid Diagram Extraction (all groups — high-value upgrade signal)

  Run after the group's base extraction if the file contains ` ```mermaid `.

  ```bash
  awk '
    /^#/ { last_heading = $0 }
    /^```mermaid/ { in_block=1; print last_heading; print; next }
    in_block { print; if (/^```$/) in_block=0 }
  ' "$file"
  ```

  ## Pattern: Image Reference Extraction (all groups — high-value upgrade signal)

  Run after the group's base extraction if the file contains `![`.

  ```bash
  grep -B2 -A2 '!\[' "$file"
  ```
  ```

- [ ] **Step 3: Verify the knowledge file was written**

  ```bash
  ls -la profile-al-dev-shared/knowledge/consolidate-extraction-patterns.md
  wc -l profile-al-dev-shared/knowledge/consolidate-extraction-patterns.md
  ```

  Expected: file exists, 60+ lines.

- [ ] **Step 4: Replace the repeated extraction blocks in Phase 2 with pattern references**

  In `profile-al-dev-shared/skills/al-dev-consolidate/SKILL.md`, find the start of Phase 2 and the repeated Group A–Persistent extraction blocks:

  ```text
  ## Phase 2 — Extract Per Session

  For each date group and for persistent files, run the extraction commands
  below. Hold only the command outputs — never the full file content.
  ```

  Replace the repeated group bodies with concise pattern references, while keeping any group-specific parameters and selection rules:

  ```text
  ## Phase 2 — Extract Per Session

  For each date group and for persistent files, run the extraction commands
  below. Hold only the command outputs — never the full file content.

  Reusable bash patterns (heading extraction, per-section awk, governance token
  count, verdict lines, mermaid/image signals) are documented in
  `knowledge/consolidate-extraction-patterns.md`. Refer to that file for the
  canonical pattern definitions; the group sections below specify which patterns
  to apply and any group-specific parameters.
  ```

  For each group section, replace the repeated inline command bodies with short
  references such as:

  - `Pattern: Heading Extraction (all groups)`
  - `Pattern: First-N-Lines-Per-Section (Groups A and C)`
  - `Pattern: Verdict / Phase Lines (Groups D and Persistent)`

- [ ] **Step 5: Verify the reference and reduce duplication**

  ```bash
  grep -n "consolidate-extraction-patterns.md" \
    profile-al-dev-shared/skills/al-dev-consolidate/SKILL.md
  ```

  Expected: 1 match at the top of Phase 2.

  ```bash
  grep -c "grep '^#' \"\$file\"" profile-al-dev-shared/skills/al-dev-consolidate/SKILL.md
  ```

  Expected: 0 or 1 matches, depending on whether a short example is retained in a comment.

- [ ] **Step 6: Forbidden pattern scan on both files**

  ```bash
  grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]\|Co-Authored-By\|claude:\|copilot:" \
    profile-al-dev-shared/knowledge/consolidate-extraction-patterns.md \
    profile-al-dev-shared/skills/al-dev-consolidate/SKILL.md
  ```

  Expected: no matches.

- [ ] **Step 7: Commit**

  ```bash
  git add profile-al-dev-shared/knowledge/consolidate-extraction-patterns.md \
          profile-al-dev-shared/skills/al-dev-consolidate/SKILL.md
  git commit -m "fix(skill): extract al-dev-consolidate Phase 2 bash patterns to knowledge/"
  ```

---

## Self-Review

**Spec coverage check:**

| Finding | Task |
|---------|------|
| al-dev-plan: Phase 1 "vague word" undefined | Task 1 |
| al-dev-plan: Phase 2 fallback no ordering | Task 1 |
| al-dev-commit: "AL-affecting staged set" undefined | Task 2 |
| al-dev-commit: 4+4a overlap | Task 3 |
| al-dev-fix: Decision tree missing labels | Task 4 |
| al-dev-interview: "signalling completion" undefined | Task 5 |
| al-dev-investigate: contradictory spawn count | Task 6 |
| al-dev-perf: skill-author instruction in prompt | Task 7 |
| al-dev-ticket: Step 1.5 navigation unclear | Task 8 |
| al-dev-develop: "required" procedure undefined | Task 9 |
| al-dev-develop: Phase 8 loop missing success condition | Task 9 |
| al-dev-develop: Scope Gate missing else clause | Task 9 |
| al-dev-develop: Scope Gate missing blocking language | Task 9 |
| al-dev-develop: Scope Gate duplicated 60+ lines | Task 10 |
| al-dev-develop: Phases 1.5/4.5 dead-branch guards | Task 11 |
| al-dev-consolidate: Phase 2 repeated bash patterns | Task 12 |

All 16 High findings covered. ✅

**Placeholder scan:** No TBD, TODO, or YYYY-MM-DD literal strings used in any task step content above. ✅

**Type consistency:** All skill file paths use consistent `profile-al-dev-shared/skills/<name>/SKILL.md` form. Knowledge paths use `profile-al-dev-shared/knowledge/<name>.md`. ✅
