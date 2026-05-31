# Plugin Health Top 5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the five highest-impact findings from the 2026-05-31 plugin health sweep to improve agent design, skill structure, and code quality.

**Architecture:** The top 5 findings cluster into three implementation categories: (1) Agent model upgrades (Task 1), (2) Skill phase cleanup (Tasks 2, 5), and (3) Agent splitting with shared knowledge (Tasks 3, 4). Work proceeds with minimal cross-task dependencies: Task 1 and 2 are independent, Task 3 creates the knowledge foundation for Task 4, Task 5 touches two major skills.

**Tech Stack:** Markdown, YAML frontmatter (for agent/skill metadata), Bash scripting (for validation).

---

## Task 1: Upgrade al-dev-code-review and al-dev-diagnostics-fixer Models to Sonnet

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md:7`
- Modify: `profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md:6`

**Rationale:** Both agents handle complex multi-file synthesis and judgment tasks (severity matrix construction, rule classification, iterative compile loops). Haiku introduces truncation risk on complex inputs.

- [ ] **Step 1: Read al-dev-code-review agent header**

```bash
head -20 profile-al-dev-shared/agents/al-dev-code-review.md
```

- [ ] **Step 2: Change model from haiku to sonnet**

Edit `profile-al-dev-shared/agents/al-dev-code-review.md`, line 7:

Find:
```yaml
model: haiku
```

Replace with:
```yaml
model: sonnet
```

- [ ] **Step 3: Read al-dev-diagnostics-fixer agent header**

```bash
head -20 profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md
```

- [ ] **Step 4: Change model from haiku to sonnet**

Edit `profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md`, line 6:

Find:
```yaml
model: haiku
```

Replace with:
```yaml
model: sonnet
```

- [ ] **Step 5: Verify both changes**

```bash
grep "^model:" profile-al-dev-shared/agents/al-dev-code-review.md profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md
```

Expected output:
```
profile-al-dev-shared/agents/al-dev-code-review.md:model: sonnet
profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md:model: sonnet
```

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-code-review.md profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md && \
git -C /Users/russelllaing/al-dev-shared commit -m "feat: upgrade al-dev-code-review and al-dev-diagnostics-fixer to sonnet

Justification: Both agents require multi-file synthesis and judgment-dependent
classification (severity matrix, rule grouping, iterative compile fixes). Haiku
truncates on complex inputs; sonnet provides sufficient context for reliable output.

Closes: Design/Model-Fit finding in 2026-05-31 plugin health report."
```

---

## Task 2: Renumber al-dev-review-develop Phases to Sequential Order 1–6

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md:50` (Execution Order section)
- Modify: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` (Phase headers throughout)

**Rationale:** Phases currently execute in non-sequential order (5→8→8.5→6-7→9→10), requiring a dedicated execution-order note. This is the highest-frequency confusing pattern — every develop run uses this skill. Fix: renumber phases 1–6 in execution order, retaining parent-workflow reference in parentheses.

- [ ] **Step 1: Read the current phase headers**

```bash
grep -n "^## Phase" profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Note the current phase numbers and their line positions.

- [ ] **Step 2: Read the Execution Order section (lines 43–48)**

```bash
sed -n '43,48p' profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

- [ ] **Step 3: Update Execution Order section**

Replace lines 43–46 in `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`:

Find:
```markdown
## Execution Order

Phases run in this order: **5 → 8 → 8.5 → 6-7 → 9 → 10** (see Run labels on each header).
Phase headers retain parent-workflow numbering; execute in the order shown, not by header number.
```

Replace with:
```markdown
## Phase Sequence

Phases run in this order: **1 → 2 → 3 → 4 → 5 → 6** (semantically mapped from parent al-dev-develop workflow).
```

- [ ] **Step 4: Renumber Phase 5 header to Phase 1**

Find:
```markdown
## Phase 5 (Run 1st): Prepare Review Context
```

Replace with:
```markdown
## Phase 1: Prepare Review Context
```

- [ ] **Step 5: Renumber Phase 8 header to Phase 2**

Find:
```markdown
## Phase 8 (Run 2nd): Compile Verification
```

Replace with:
```markdown
## Phase 2: Compile Verification
```

- [ ] **Step 6: Renumber Phase 8.5 header to Phase 3**

Find:
```markdown
## Phase 8.5 (Run 3rd): Pre-Review Staging
```

Replace with:
```markdown
## Phase 3: Pre-Review Staging
```

- [ ] **Step 7: Renumber Phase 6-7 header to Phase 4**

Find:
```markdown
## Phase 6-7 (Run 4th): Dispatch Review Panel
```

Replace with:
```markdown
## Phase 4: Dispatch Review Panel
```

- [ ] **Step 8: Renumber Phase 9 header to Phase 5**

Find:
```markdown
## Phase 9 (Run 5th): Write Code-Review Artifact
```

Replace with:
```markdown
## Phase 5: Write Code-Review Artifact
```

- [ ] **Step 9: Renumber Phase 10 header to Phase 6**

Find the Phase 10 header (around line 200+) and replace:

```markdown
## Phase 10 (Run 6th): ...
```

Replace with:
```markdown
## Phase 6: ...
```

- [ ] **Step 10: Verify phase sequence**

```bash
grep "^## Phase" profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md | head -10
```

Expected output:
```
## Phase 1: Prepare Review Context
## Phase 2: Compile Verification
## Phase 3: Pre-Review Staging
## Phase 4: Dispatch Review Panel
## Phase 5: Write Code-Review Artifact
## Phase 6: ...
```

- [ ] **Step 11: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md && \
git -C /Users/russelllaing/al-dev-shared commit -m "refactor: renumber al-dev-review-develop phases to sequential 1–6

Phases are now numbered 1–6 in execution order, eliminating the confusing
5→8→8.5→6-7→9→10 non-sequential pattern. Removed 'Run Nth' labels and execution-order
note. This is the highest-frequency source of confusion on every develop run.

Closes: Quality/Bloat+Clarity finding in 2026-05-31 plugin health report."
```

---

## Task 3: Create knowledge/developer-invocation-patterns.md

**Files:**
- Create: `profile-al-dev-shared/knowledge/developer-invocation-patterns.md`

**Rationale:** al-dev-developer is spawned by 3 skills (al-dev-develop, al-dev-fix, al-dev-review-develop) with materially different dispatch prompts and contexts. When SYMBOL_PREFLIGHT_GATE requirements change, al-dev-fix and al-dev-review-develop won't get updates. Create a shared knowledge file documenting the 3-4 named invocation contexts.

- [ ] **Step 1: Create the knowledge file**

```bash
cat > profile-al-dev-shared/knowledge/developer-invocation-patterns.md << 'EOF'
# Developer Invocation Patterns

Reference document for the three contexts in which `al-dev-developer` is spawned.

## Context 1: Full Scope Implementation (al-dev-develop Phase 4)

**Caller:** `/al-dev-develop` (Phase 4: Developer Dispatch and Implementation)

**Trigger:** User has approved a solution plan and /al-dev-develop is orchestrating parallel developer agents to implement it.

**Developer is responsible for:**
- Reading the full solution plan (`.dev/*-al-dev-plan-solution-plan.md`)
- Implementing a specific module/component assignment
- TDD workflow if test plan exists; traditional workflow otherwise
- Scope Expansion Gate: stopping before out-of-scope edits for user approval
- Compiling after each file or logical group
- Recording session log in `.dev/session-log.md`

**Dispatch prompt structure:**
- Solution plan reference + module assignment
- Object list and object ID range
- AL symbol preflight evidence (AL LSP, AL MCP, text search)
- Scope Expansion Gate rules
- Code quality standards reference
- TDD vs. traditional path decision (test plan present?)

**Success evidence:**
- All assigned objects implemented and compiling cleanly
- Session log updated
- Code ready for review panel (al-dev-security-reviewer, al-dev-expert-reviewer, al-dev-performance-reviewer)

---

## Context 2: Trivial Direct Fix (al-dev-fix Task 3–5)

**Caller:** `/al-dev-fix` (Steps 3–5: Non-Trivial Implementation Path)

**Trigger:** User approved a trivial fix scope (single file, obvious implementation), and /al-dev-fix is dispatching a developer for quick implementation.

**Developer is responsible for:**
- Reading the fix scope and requirements (from /al-dev-fix context)
- Implementing a single, focused change
- No full solution plan; minimal context gathering
- Direct implementation without TDD (test plan typically absent for trivial fixes)
- Compiling once at the end (or immediately if change is complex)
- Returning: files changed, verification that fix resolves the stated issue

**Dispatch prompt structure:**
- Issue description and fix scope
- Single file path or object name
- AL symbol preflight evidence (focused on the changed object)
- Implementation constraints from /al-dev-fix scope check
- Code quality standards (same as Context 1)
- Traditional workflow assumed (no test plan)

**Success evidence:**
- File modified and compiling cleanly
- Fix verified to resolve the stated issue
- Code ready for optional code review (developer quality check, not multi-reviewer panel)

---

## Context 3: Error Correction (al-dev-review-develop Phase 2, Autonomous Mode)

**Caller:** `/al-dev-review-develop` (Phase 2: Compile Verification, --autonomous mode only)

**Trigger:** Compilation has errors after Phase 4 implementation, and /al-dev-review-develop --autonomous is dispatching a developer to fix them before the review panel runs.

**Developer is responsible for:**
- Reading `.dev/compile-errors.log` and identifying root causes
- Applying minimal, targeted fixes
- Re-compiling after each fix (5-cycle limit)
- Returning: files changed, errors resolved (or unresolvable errors for escalation)

**Dispatch prompt structure:**
- Compile error log reference
- Phase 4 handoff context (what was implemented)
- Minimal scope: only fix errors, do not refactor
- AL symbol evidence for changed objects
- Compile-fix-compile cycle discipline
- Stop after 5 failed attempts (escalate to user)

**Success evidence:**
- Zero `error AL` lines in `.dev/compile-errors.log`
- Fixes are minimal (no scope expansion)
- Code ready for review panel

---

## Shared Pattern: SYMBOL_PREFLIGHT_GATE

All three contexts enforce the symbol preflight checklist (`knowledge/al-symbol-pre-flight.md`).

Developer must:
1. Report pre-flight summary before writing any AL code
2. Name the evidence source for each required symbol (AL LSP, AL MCP, text search, or unverified)
3. **Stop before implementation if any required symbol remains unverified**

When dispatching in any context, include:
- `SYMBOL_PREFLIGHT_GATE: pre-flight summary required before implementation starts`

---

## Dispatch Prompt Template

Use this structure when spawning `al-dev-developer` from any of the three contexts:

```
Agent: al-dev-shared:al-dev-developer

Context: [CONTEXT 1 | CONTEXT 2 | CONTEXT 3]

[Context-specific preamble — see Context 1/2/3 above]

Solution Plan / Scope: [reference to .dev/*.md or direct scope statement]

Module Assignment / Object List: [specific objects to implement or fix]

Implementation Notes:
- [Key pattern from solution plan or /al-dev-fix scope]
- [AL symbol evidence from preflight or prior search]
- [Code quality standards: labels for errors, symbol preflight, compile after each file]

[Append SYMBOL_PREFLIGHT_GATE requirement]

Return: files changed, session log entry, any blockers or scope clarifications.
```

EOF
```

- [ ] **Step 2: Verify file was created**

```bash
ls -la profile-al-dev-shared/knowledge/developer-invocation-patterns.md && wc -l profile-al-dev-shared/knowledge/developer-invocation-patterns.md
```

- [ ] **Step 3: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/developer-invocation-patterns.md && \
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add developer-invocation-patterns knowledge file

Documents three distinct contexts for spawning al-dev-developer:
1. Full Scope Implementation (al-dev-develop Phase 4)
2. Trivial Direct Fix (al-dev-fix Steps 3–5)
3. Error Correction (al-dev-review-develop Phase 2 autonomous mode)

Shared pattern: SYMBOL_PREFLIGHT_GATE enforced in all contexts.

This knowledge file serves as the single source of truth for dispatcher consistency
and prevents drift when dispatch prompt requirements change (e.g., symbol preflight
evidence policy).

Closes: Design/Shared-Backbone finding in 2026-05-31 plugin health report."
```

---

## Task 4: Split al-dev-developer into TDD and Traditional Paths

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-developer.md` (archive as base template)
- Create: `profile-al-dev-shared/agents/al-dev-developer-tdd.md`
- Create: `profile-al-dev-shared/agents/al-dev-developer-traditional.md`
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` (Phase 4 dispatch logic)
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` (dispatch logic, reference knowledge file)
- Modify: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` (Phase 2 dispatch logic, reference knowledge file)

**Rationale:** al-dev-developer currently contains two distinct workflows (TDD with RED-GREEN-REFACTOR gates vs. traditional with BUILD_VERIFY_GATE) in a 40+ line conditional. Split into two focused agents; route based on test-plan presence.

### Subpart 4a: Create al-dev-developer-tdd.md

- [ ] **Step 1: Read the current al-dev-developer.md to extract TDD section**

```bash
sed -n '36,50p' profile-al-dev-shared/agents/al-dev-developer.md
```

This is the "TDD Workflow" section.

- [ ] **Step 2: Create al-dev-developer-tdd.md**

```bash
cat > profile-al-dev-shared/agents/al-dev-developer-tdd.md << 'EOF'
---
name: al-dev-developer-tdd
description: >-
  Implement AL code using test-driven development (RED-GREEN-REFACTOR cycle).
  Spawned when al-dev-develop or al-dev-fix detects a test plan.
  Consumes solution plan and test plan from .dev/. Creates AL source and test codeunits.
model: sonnet
tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

# Agent: al-dev-developer-tdd

Implement AL code according to the implementation plan using test-driven development.
Follow the RED-GREEN-REFACTOR cycle with hard gates between each phase.

## Your Mission

Write clean, correct AL code that implements the planned solution. Follow AL coding
standards and TDD discipline. Each test must RED, GREEN, then REFACTOR before moving
to the next test.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` | **Yes** | Implementation plan |
| `.dev/*-al-dev-test-test-plan.md` | **Yes** | Test specifications for TDD workflow |
| `.dev/project-context.md` | No | Project memory and conventions |
| `.dev/*-al-dev-develop-code-review.md` | No | Review findings for iteration |

## Outputs

| Output | Description |
|--------|-------------|
| AL source files | Implemented code in `src/` |
| Test codeunits | Test code in `src/Tests/` |
| `.dev/$(date +%Y-%m-%d)-al-dev-developer-tdd-log.md` | TDD log documenting RED-GREEN-REFACTOR cycles |
| `.dev/session-log.md` | Session log entry per file |

## Workflow

### TDD Workflow (RED-GREEN-REFACTOR Cycle)

1. **Read test specification** — Load `.dev/*-al-dev-test-test-plan.md` in full
2. **Read solution plan** — Load `.dev/*-al-dev-plan-solution-plan.md` in full
3. **Complete AL symbol preflight** — Reference `knowledge/al-symbol-pre-flight.md`. Report pre-flight summary (evidence source: AL LSP, AL MCP, text search, or unverified). **STOP if any required symbol cannot be verified.**
4. **For each test in spec:**

   - **RED Phase:** Write failing test that matches the spec exactly. Invoke `TDD_CYCLE_GATE`:
     - Present the failing test code
     - Show test execution: `al-compile` or test runner output proving RED state
     - Wait for user approval before writing production code

   - **GREEN Phase:** Write minimal production code to make the test pass. Invoke `TDD_CYCLE_GATE`:
     - Present the implementation code
     - Show test execution proving GREEN state (test now passes)
     - Wait for user approval before refactoring

   - **REFACTOR Phase:** Improve code quality without changing behavior. Invoke `TDD_CYCLE_GATE`:
     - Present refactored code and rationale
     - Show test execution proving code still passes
     - Wait for user approval before next test

5. **Document cycles** in TDD log (`.dev/$(date +%Y-%m-%d)-al-dev-developer-tdd-log.md`):
   - Test name
   - RED output (failing test)
   - GREEN output (passing test with production code)
   - REFACTOR changes applied (if any)

6. **After all tests pass:**
   - Verify clean compilation: `al-compile --output .dev/compile-errors.log`
   - Update session log: document file count, test count, any refactoring themes
   - Mark TDD complete in log

## Standards

### AL Code Patterns

Before writing any AL code, complete the symbol pre-flight checklist
(`knowledge/al-symbol-pre-flight.md`). This is enforced by
`SYMBOL_PREFLIGHT_GATE` — report your pre-flight summary before implementation
begins. The summary must name the evidence source for each required symbol:
`AL LSP`, `AL MCP`, `text search`, or `unverified`.

Prefer `AL LSP` semantic navigation when the active harness exposes it for
definition lookup, references, document symbols, hover/type information, and
rename/refactor impact checks. If unavailable, use AL MCP. Use scoped text
search only as a weaker fallback with exact file:line evidence. Stop before
implementation if a required symbol remains `unverified`.

Reference `knowledge/al-developer-patterns.md` for standard AL patterns, common mistakes to avoid, error handling rules, and naming conventions. Key principles:
- Use labels instead of StrSubstNo for error messages
- Use proper event subscriber signatures
- Avoid N+1 query patterns
- Keep procedures ≤30 lines, single responsibility

### Code Quality (DRY/SOLID)
- Does this already exist? → Reuse it
- Will this be needed elsewhere? → Put in shared codeunit
- Is this doing multiple things? → Split it
- Compile after test group or logical progression

### Compilation

Always use `al-compile` after completing refactoring in each cycle. Fix syntax errors immediately.

### Compile Output — Critical Safeguard

When running `al-compile --output .dev/compile-errors.log`:

**DO:**
- Run the command without pipes: `al-compile --output .dev/compile-errors.log`
- Always include a `description` parameter on the Bash tool call
- Use the Read tool to inspect the log file afterward if needed
- Use file-based grep if you need to filter results: `grep -E "pattern" .dev/compile-errors.log`

**DO NOT:**
- Pipe output to terminal viewers: `al-compile ... 2>&1 | head/tail/grep` ❌
- Omit the `description` parameter on Bash calls
- Run `al-compile` without the `--output` flag

**Why:** Piping compile output causes the entire log (4.7MB+) to be captured in session context, triggering context compacts.

### Error Handling
- Always validate input at boundaries
- Use clear error messages with context
- Include proper DataClassification and ApplicationArea in fields

### Performance Best Practices
- Use SetLoadFields to load only needed columns
- Filter before loading; avoid N+1 loops
- Batch operations instead of record-by-record processing

## Governance Tokens

| Token | Gate | Action |
|-------|------|--------|
| `PLAN_READ_GATE` | Before writing code | Read solution plan and test plan first |
| `SYMBOL_PREFLIGHT_GATE` | Before writing any AL code | Complete `knowledge/al-symbol-pre-flight.md` checklist — report pre-flight summary before coding starts; stop if any item cannot be verified |
| `TDD_CYCLE_GATE` | After each RED, GREEN, REFACTOR phase | Hard stop — user must approve before next phase. Present code and test output. |
| `FIX_ITERATION_LIMIT` | After 5 compile failures | Stop and escalate |
EOF
```

- [ ] **Step 3: Verify file was created and has content**

```bash
ls -la profile-al-dev-shared/agents/al-dev-developer-tdd.md && wc -l profile-al-dev-shared/agents/al-dev-developer-tdd.md
```

### Subpart 4b: Create al-dev-developer-traditional.md

- [ ] **Step 4: Create al-dev-developer-traditional.md**

```bash
cat > profile-al-dev-shared/agents/al-dev-developer-traditional.md << 'EOF'
---
name: al-dev-developer-traditional
description: >-
  Implement AL code following an implementation plan without test-driven development.
  Spawned when al-dev-develop or al-dev-fix runs without a test plan.
  Consumes solution plan from .dev/. Creates AL source files.
model: sonnet
tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

# Agent: al-dev-developer-traditional

Implement AL code according to the implementation plan. Creates and
modifies AL files. Spawned by al-dev-develop and al-dev-fix skills when no test plan exists.

## Your Mission

Write clean, correct AL code that implements the planned solution. Follow AL coding standards.
Compile frequently to catch errors early.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` | **Yes** | Implementation plan |
| `.dev/project-context.md` | No | Project memory |
| `.dev/*-al-dev-develop-code-review.md` | No | Review findings for iteration |

## Outputs

| Output | Description |
|--------|-------------|
| AL source files | Implemented code in `src/` |
| `.dev/session-log.md` | Session log entry per file |

## Workflow

1. **Read project context** — Check `.dev/project-context.md` if exists
2. **Read solution plan** — Load `.dev/*-al-dev-plan-solution-plan.md` in full
3. **Complete AL symbol preflight** — Reference `knowledge/al-symbol-pre-flight.md`. Report pre-flight summary (evidence source: AL LSP, AL MCP, text search, or unverified). **STOP if any required symbol cannot be verified.**
4. **Implement code** — Follow plan, compile after each file or logical group
5. **Update logs** — Session log and project context

## Standards

### AL Code Patterns
Before writing any AL code, complete the symbol pre-flight checklist
(`knowledge/al-symbol-pre-flight.md`). This is enforced by
`SYMBOL_PREFLIGHT_GATE` — report your pre-flight summary before implementation
begins. The summary must name the evidence source for each required symbol:
`AL LSP`, `AL MCP`, `text search`, or `unverified`.

Prefer `AL LSP` semantic navigation when the active harness exposes it for
definition lookup, references, document symbols, hover/type information, and
rename/refactor impact checks. If unavailable, use AL MCP. Use scoped text
search only as a weaker fallback with exact file:line evidence. Stop before
implementation if a required symbol remains `unverified`.

Reference `knowledge/al-developer-patterns.md` for standard AL patterns, common mistakes to avoid, error handling rules, and naming conventions. Key principles:
- Use labels instead of StrSubstNo for error messages
- Use proper event subscriber signatures
- Avoid N+1 query patterns
- Keep procedures ≤30 lines, single responsibility

### Code Quality (DRY/SOLID)
- Does this already exist? → Reuse it
- Will this be needed elsewhere? → Put in shared codeunit
- Is this doing multiple things? → Split it
- Compile after each file or logical group (logical group = tables + their extensions, or a codeunit + its subscribers)

### Compilation

Always use `al-compile` after each file. Fix syntax errors immediately; don't accumulate errors.

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

### Error Handling
- Always validate input at boundaries
- Use clear error messages with context
- Include proper DataClassification and ApplicationArea in fields

### Performance Best Practices
- Use SetLoadFields to load only needed columns
- Filter before loading; avoid N+1 loops
- Batch operations instead of record-by-record processing

## Governance Tokens

| Token | Gate | Action |
|-------|------|--------|
| `PLAN_READ_GATE` | Before writing code | Read solution plan first |
| `BUILD_VERIFY_GATE` | After implementation | Run `al-compile` — must pass before done |
| `FIX_ITERATION_LIMIT` | After 5 compile failures | Stop and escalate |
| `SYMBOL_PREFLIGHT_GATE` | Before writing any AL code | Complete `knowledge/al-symbol-pre-flight.md` checklist — report pre-flight summary before coding starts; stop if any item cannot be verified |
EOF
```

- [ ] **Step 5: Verify file was created**

```bash
ls -la profile-al-dev-shared/agents/al-dev-developer-traditional.md && wc -l profile-al-dev-shared/agents/al-dev-developer-traditional.md
```

### Subpart 4c: Archive original al-dev-developer.md

- [ ] **Step 6: Move original al-dev-developer.md to archived/**

```bash
mkdir -p profile-al-dev-shared/archived && \
mv profile-al-dev-shared/agents/al-dev-developer.md profile-al-dev-shared/archived/al-dev-developer-original.md.archived
```

- [ ] **Step 7: Verify original was archived**

```bash
ls -la profile-al-dev-shared/archived/al-dev-developer-original.md.archived && \
! test -f profile-al-dev-shared/agents/al-dev-developer.md && echo "Original removed from active agents"
```

### Subpart 4d: Update al-dev-develop dispatcher (Phase 4)

- [ ] **Step 8: Read al-dev-develop Phase 4 section**

Find and read the "Phase 4: Developer Dispatch and Implementation" section in `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`. This section contains the developer spawn logic.

- [ ] **Step 9: Update dispatcher to route based on test plan presence**

In the Phase 4 developer dispatch instructions, add this decision logic:

Find the section that says:
```
Spawn developers for each module assignment in the solution plan:
```

Update it to:

```
Before spawning each developer, check for a test plan:

1. Check for test plan:
   ```bash
   TEST_PLAN=$(ls .dev/*-al-dev-test-test-plan.md 2>/dev/null | sort | tail -1)
   ```

2. If test plan exists, spawn `al-dev-developer-tdd`:
   ```
   Agent: al-dev-shared:al-dev-developer-tdd
   ```
   Include in prompt: reference to test plan, TDD cycle expectations, gates.

3. If no test plan, spawn `al-dev-developer-traditional`:
   ```
   Agent: al-dev-shared:al-dev-developer-traditional
   ```
   Include in prompt: traditional build-verify workflow, single compilation at end (or per-file).

Dispatch context reference: `knowledge/developer-invocation-patterns.md` (Context 1: Full Scope Implementation).
```

Add the knowledge file reference at the top of Phase 4:

```
See knowledge/developer-invocation-patterns.md for dispatcher consistency across all developer spawns.
```

- [ ] **Step 10: Verify changes to al-dev-develop**

```bash
grep -n "developer-invocation-patterns" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Should find at least one reference.

### Subpart 4e: Update al-dev-fix dispatcher

- [ ] **Step 11: Read al-dev-fix implementation section**

Find the step in `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` that dispatches al-dev-developer for non-trivial fixes.

- [ ] **Step 12: Add knowledge file reference to al-dev-fix**

Add this reference near the top of the developer dispatch logic:

```
See knowledge/developer-invocation-patterns.md (Context 2: Trivial Direct Fix) for
dispatcher consistency when spawning al-dev-developer.

For non-trivial fixes: check for test plan (same as /al-dev-develop), then dispatch
al-dev-developer-tdd or al-dev-developer-traditional accordingly.
```

### Subpart 4f: Update al-dev-review-develop Phase 2 dispatcher

- [ ] **Step 13: Read al-dev-review-develop Phase 2 (renamed to Phase 2 in Task 2)**

Find the Phase 2 section (originally Phase 8) that handles compile errors in autonomous mode.

- [ ] **Step 14: Add knowledge file reference to al-dev-review-develop**

In the Phase 2 step that spawns al-dev-developer for error fixes, add:

```
See knowledge/developer-invocation-patterns.md (Context 3: Error Correction) for dispatcher
consistency. This is autonomous error-fixing mode — no test plan, minimal scope (fix only
compile errors, do not refactor).

Spawn al-dev-developer-traditional for error fixes (compile errors don't require TDD).
```

- [ ] **Step 15: Commit Task 4 changes**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/agents/al-dev-developer-tdd.md \
  profile-al-dev-shared/agents/al-dev-developer-traditional.md \
  profile-al-dev-shared/archived/al-dev-developer-original.md.archived \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/skills/al-dev-fix/SKILL.md \
  profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md && \
git -C /Users/russelllaing/al-dev-shared commit -m "feat: split al-dev-developer into TDD and traditional paths

Creates two focused agents:
- al-dev-developer-tdd: RED-GREEN-REFACTOR workflow with TDD_CYCLE_GATE approval gates
- al-dev-developer-traditional: traditional build-verify workflow for non-TDD scenarios

Routing logic added to al-dev-develop Phase 4, al-dev-fix dispatcher, and
al-dev-review-develop Phase 2. Routes based on test-plan presence in .dev/.

All three dispatchers now reference knowledge/developer-invocation-patterns.md for
consistency and future maintenance.

Original al-dev-developer archived for reference.

Closes: Design/Scope-Isolation finding in 2026-05-31 plugin health report."
```

---

## Task 5: Consolidate al-dev-develop and al-dev-plan Phase Structure

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` (remove Glossary, label optional phases, extract spawn prompt)
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` (remove Phase Numbering Rationale, consolidate Phase 1 sub-steps, add explicit gate for 1.5/1.6)
- Create: `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md` (extracted spawn prompt)
- Create: `profile-al-dev-shared/knowledge/al-dev-plan-phase-routing.md` (extracted complexity routing logic from Phase 0.5)

**Rationale:** al-dev-develop has 11 phases with invisible dead branches and a 73-line inline spawn prompt. al-dev-plan has a "Phase Numbering Rationale" comment that belongs in git history and implicit Phases 1.5/1.6 activation. Both are entry-point skills used on every feature task. Fix: label optional phases explicitly, extract spawn prompt and routing logic to knowledge files.

### Subpart 5a: Extract al-develop-develop spawn prompt to knowledge file

- [ ] **Step 1: Read the current spawn prompt section in al-dev-develop**

Search for the "Developer Spawn Prompt" section (around line 54–60) and the full spawn prompt that follows. This is typically a large inline text block.

- [ ] **Step 2: Create al-dev-develop-spawn-prompt.md**

```bash
cat > profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md << 'EOF'
# Developer Spawn Prompt Template

This knowledge file documents the structured prompt dispatched to each `al-dev-developer` agent
spawned during al-dev-develop Phase 4.

## Prompt Structure

Each developer dispatch includes:

1. **Module assignment** — which objects/features is this developer responsible for?
2. **Object list** — explicit table/codeunit/page names from the solution plan
3. **Object ID range** — from project-context.md (if available)
4. **Naming conventions** — prefix/suffix rules from project context
5. **AL code patterns** — reference to `knowledge/al-developer-patterns.md`
6. **Scope Expansion Gate rules** — from `knowledge/scope-expansion-gate.md`
7. **Symbol preflight evidence** — AL LSP / AL MCP / text search findings collected in Phase 1
8. **Test plan indication** — is `.dev/*-al-dev-test-test-plan.md` present?

## Template

```
Agent: [al-dev-developer-tdd OR al-dev-developer-traditional — based on test plan presence]

Module Assignment:
[Module name] — responsible for these objects:
  - [Table name]
  - [Codeunit name]
  - [Page name]

Implementation Plan Reference:
.dev/[dated-solution-plan-filename]

Object ID Range:
[From project-context.md, or "unspecified" if not available]

AL Code Patterns & Standards:
- Reference: knowledge/al-developer-patterns.md
- Use labels for error messages (not StrSubstNo)
- Keep procedures ≤30 lines, single responsibility
- Compile after each file or logical group

Scope Expansion Gate:
Do NOT edit files or objects outside the list above without asking first.
Reference: knowledge/scope-expansion-gate.md

Symbol Preflight:
Complete the checklist at knowledge/al-symbol-pre-flight.md.
Evidence collected during planning:
  [Symbol 1]: [AL LSP / AL MCP / text search]
  [Symbol 2]: [AL LSP / AL MCP / text search]
  ... (any unverified symbols: STOP and escalate before coding)

[If test plan exists:]
Test Plan:
.dev/[dated-test-plan-filename]
Use RED-GREEN-REFACTOR workflow with TDD_CYCLE_GATE approvals.
Reference: al-dev-developer-tdd agent description.

[If no test plan:]
Workflow:
Traditional build-verify approach. Compile after each file. Reference: al-dev-developer-traditional agent description.

Expected Output:
- AL source files (src/)
- Session log entries (.dev/session-log.md)
[If TDD:]
- TDD log (.dev/[dated]-al-dev-developer-tdd-log.md)
```

## Usage in al-dev-develop

During Phase 4, for each module assignment in the solution plan:

1. Gather module-specific context (objects, ID range, patterns)
2. Instantiate the template above
3. Include test-plan detection (`ls .dev/*-al-dev-test-test-plan.md`)
4. Dispatch the appropriate developer agent with the instantiated prompt

This knowledge file ensures consistent developer dispatch across multiple sessions and changes.
EOF
```

- [ ] **Step 3: Verify file creation**

```bash
ls -la profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md && wc -l profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md
```

### Subpart 5b: Extract al-dev-plan complexity routing to knowledge file

- [ ] **Step 4: Create al-dev-plan-phase-routing.md**

```bash
cat > profile-al-dev-shared/knowledge/al-dev-plan-phase-routing.md << 'EOF'
# Plan Complexity Routing

Reference for routing planning decisions in al-dev-plan Phase 0.5.

## Complexity Classification

Classify the request before gathering full context using these signals:

| Signal | SIMPLE | MEDIUM / COMPLEX |
|--------|--------|------------------|
| Estimated file count | ≤ 3 | 4+ or unclear |
| Pattern in codebase (if known) | Yes | No / unclear |
| New architecture needed | No | Yes |
| Requirements ambiguous | No | Yes |

"SIMPLE" maps to TRIVIAL or SIMPLE in `knowledge/workflow-routing.md`.
"MEDIUM / COMPLEX" maps to MEDIUM or COMPLEX.

## Model Assignment

Route based on complexity classification:

- **SIMPLE** → `architect_model = sonnet`
  - Simpler problem, shorter architect debate, faster resolution
  - Suitable when pattern is known and requirements are clear

- **MEDIUM / COMPLEX** → `architect_model = opus`
  - Larger scope, architectural novelty, requirement ambiguity
  - Supports deeper analysis and debate with higher token budget

**When in doubt, default to `opus`.** Over-provisioning is safer than under-provisioning for architecture work. Do not surface this decision to the user — it is internal routing.

## Phase 0.5 Routing Logic

Use this logic in al-dev-plan Phase 0.5:

```
1. Extract signals from user request:
   - File count (explicit? estimated? unclear?)
   - Is pattern known in codebase? (check project context, codebase structure)
   - New architecture? (novel problem? existing templates?)
   - Clear requirements? (specific spec? vague ask?)

2. Score complexity:
   - ≤ 1 signal for SIMPLE → SIMPLE path
   - 2+ signals for MEDIUM / COMPLEX → MEDIUM / COMPLEX path
   - If unclear: ask clarifying question OR default to MEDIUM / COMPLEX + opus

3. Record decision:
   - Note complexity tier (SIMPLE / MEDIUM / COMPLEX) for Phase 1
   - Set architect_model accordingly
   - Continue with architect dispatch in Phase 2
```

## Architect Debate Configuration

Based on complexity tier:

- **SIMPLE** (sonnet):
  - Dispatch 2 architects (vs. 3 for COMPLEX)
  - Shorter debate window (may abbreviate if quick consensus)
  - Single architect evaluation for synthesis

- **MEDIUM / COMPLEX** (opus):
  - Dispatch 2-3 architects (full competitive debate)
  - No abbreviation — full debate
  - Synthesis may require evaluation or panel judgment

## Glossary

**Competitive design debate:** Multiple architects generate independent solution approaches. The agent synthesizes the winner and grafts best ideas from runners-up.

**Abbreviate:** If 2 architects reach consensus quickly, skip the 3rd architect and proceed to synthesis.

**Synthesis:** Single chosen agent writes the final solution plan, optionally incorporating non-core ideas from other architect proposals.
EOF
```

- [ ] **Step 5: Verify file creation**

```bash
ls -la profile-al-dev-shared/knowledge/al-dev-plan-phase-routing.md && wc -l profile-al-dev-shared/knowledge/al-dev-plan-phase-routing.md
```

### Subpart 5c: Update al-dev-develop.SKILL.md

- [ ] **Step 6: Read the Glossary section in al-dev-develop**

Find and note the line numbers of the "Glossary" section (around line 47–72).

- [ ] **Step 7: Remove the Glossary section from al-dev-develop**

In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, delete the entire Glossary section (lines ~47–72). This is historical commentary that belongs in git history, not the skill body.

- [ ] **Step 8: Add "(Autonomous Mode Only)" labels to optional phases**

Add explicit labels to Phase 1.5 and Phase 4.5 headers:

Find:
```markdown
**Phase 1.5 (Autonomous):** Optional signature verification phase
```

Replace with:
```markdown
**Phase 1.5 (Autonomous Mode Only):** Optional signature verification phase
```

Similarly for Phase 4.5.

- [ ] **Step 9: Replace inline spawn prompt with knowledge file reference**

In the Phase 4 "Developer Dispatch" section, find the large inline spawn prompt block (typically 70+ lines). Replace it with:

```markdown
See `knowledge/al-dev-develop-spawn-prompt.md` for the developer spawn prompt template and instructions for instantiating it per module assignment.

For each module in the solution plan:
1. Gather module-specific context (objects, ID range, symbols)
2. Instantiate the spawn prompt template
3. Detect test plan: `ls .dev/*-al-dev-test-test-plan.md`
4. Dispatch al-dev-developer-tdd (if test plan) or al-dev-developer-traditional (if no test plan)
```

- [ ] **Step 10: Verify al-dev-develop changes**

```bash
grep -c "knowledge/al-dev-develop-spawn-prompt.md" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Should output: `1` (or more if multiple references).

### Subpart 5d: Update al-dev-plan.SKILL.md

- [ ] **Step 11: Remove Phase Numbering Rationale section from al-dev-plan**

Find the "Phase Numbering Rationale" section (around line 41–43) and delete it entirely.

- [ ] **Step 12: Add knowledge file reference to Phase 0.5**

In the Phase 0.5 "Complexity Triage" section, replace or supplement the inline table with:

```markdown
Classify the request before gathering full context.
See `knowledge/al-dev-plan-phase-routing.md` for full complexity classification rules and model assignment logic.

Quick reference:

| Signal | SIMPLE | MEDIUM / COMPLEX |
| --- | --- | --- |
| Estimated file count | ≤ 3 | 4+ or unclear |
| Pattern in codebase (if known) | Yes | No / unclear |
| New architecture needed | No | Yes |
| Requirements ambiguous | No | Yes |

When in doubt, default to `opus` (MEDIUM / COMPLEX tier).
```

- [ ] **Step 13: Add explicit gates for Phases 1.5 and 1.6**

Find the Phase 1.5 and Phase 1.6 descriptions. Update them to include explicit activation conditions:

For Phase 1.5, add:
```markdown
**Phase 1.5 (Optional — External Claims Verification):**
If the user request references a findings file, codeburn output, lint report, or third-party analysis, execute this phase to verify claims before forwarding to architects. Otherwise, skip to Phase 2.
```

For Phase 1.6, add:
```markdown
**Phase 1.6 (Optional — Pre-Research Base App):**
If Phase 1's pre-research via AL LSP or MCP returns results, consolidate findings. If no results, skip to Phase 2. If results are incomplete and a required symbol remains unverified, note it for architect input in Phase 2.
```

- [ ] **Step 14: Consolidate Phase 1 sub-steps**

Phase 1 currently has 6 sub-steps (1–6, spanning ~57 lines). Consolidate the detailed steps into a more concise structure:

1. **Input Validation Gate** (mandatory)
2. **Load requirements and context files** (project-context.md, prior interview requirements)
3. **Gather symbol evidence** (via AL LSP, MCP, or text search)
4. **Load performance and exploration findings** (if available)

Replace the 6 detailed sub-steps with this 4-step structure.

- [ ] **Step 15: Verify al-dev-plan changes**

```bash
grep -c "knowledge/al-dev-plan-phase-routing.md" profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

Should output: `1` (or more).

- [ ] **Step 16: Commit Task 5 changes**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md \
  profile-al-dev-shared/knowledge/al-dev-plan-phase-routing.md \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/skills/al-dev-plan/SKILL.md && \
git -C /Users/russelllaing/al-dev-shared commit -m "refactor: consolidate al-dev-develop and al-dev-plan phase structure

## al-dev-develop changes:
- Removed Glossary section (historical commentary moved to git)
- Labeled Phase 1.5 and 4.5 as '(Autonomous Mode Only)' for clarity
- Extracted 73-line inline spawn prompt to knowledge/al-dev-develop-spawn-prompt.md
- Phase 4 dispatcher now references knowledge file for consistency

## al-dev-plan changes:
- Removed 'Phase Numbering Rationale' section (historical commentary)
- Extracted complexity routing logic to knowledge/al-dev-plan-phase-routing.md
- Phase 0.5 now references knowledge file with full classification rules
- Added explicit gates for optional Phases 1.5 and 1.6
- Consolidated Phase 1 from 6 sub-steps to 4 consolidated steps (~25 line reduction)

These are entry-point skills used on every feature task. Cleaner structure reduces
friction and improves maintainability.

Closes: Quality/Bloat+Clarity finding in 2026-05-31 plugin health report."
```

---

## Final Verification

After all 5 tasks are complete, run a final validation:

- [ ] **Step 1: Verify all 5 commits were created**

```bash
git -C /Users/russelllaing/al-dev-shared log --oneline -n 5
```

Should show 5 commits (one per task).

- [ ] **Step 2: Verify no syntax errors in modified skills/agents**

```bash
python3 -m py_compile scripts/validate-lens-agents.py 2>&1 | head -5
```

(Or run the actual validation if available)

- [ ] **Step 3: Check file persistence**

```bash
wc -l profile-al-dev-shared/knowledge/developer-invocation-patterns.md \
      profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md \
      profile-al-dev-shared/knowledge/al-dev-plan-phase-routing.md \
      profile-al-dev-shared/agents/al-dev-developer-tdd.md \
      profile-al-dev-shared/agents/al-dev-developer-traditional.md
```

All files should exist and have non-zero line counts.

- [ ] **Step 4: Verify archived file**

```bash
ls -la profile-al-dev-shared/archived/al-dev-developer-original.md.archived && \
! test -f profile-al-dev-shared/agents/al-dev-developer.md && \
echo "Original archived successfully"
```

---

## Summary

This plan implements all five top-ranked findings from the 2026-05-31 plugin health report:

1. **Task 1** — Model upgrades (haiku → sonnet for code-review and diagnostics-fixer)
2. **Task 2** — Phase renumbering (5→8→8.5→6-7→9→10 becomes 1→2→3→4→5→6)
3. **Task 3** — Shared knowledge (developer-invocation-patterns.md for 3 dispatch contexts)
4. **Task 4** — Agent splitting (al-dev-developer-tdd and -traditional with smart routing)
5. **Task 5** — Structure consolidation (removed glossaries and historical commentary, extracted spawn prompt and routing logic)

**Dependencies:** Task 3 must complete before Task 4 references it. All other tasks are independent or have loose ordering (Task 1, 2, 5 can proceed in any order).

**Effort estimate:** 4–6 hours for careful execution including testing.

