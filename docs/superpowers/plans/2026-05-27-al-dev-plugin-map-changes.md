# AL Dev Plugin Map Changes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 8 verified architectural improvements to the al-dev plugin identified in the 2026-05-27 map analysis: restore critical agent file, trim unused agent tools, clarify alignment contracts, optimize agent model assignments, improve feedback loops, and refactor a high-complexity skill into two focused ones.

**Architecture:** Multi-phase execution: (1) Quick wins (Trim, Align, Remodel) — additive changes with zero risk; (2) Medium tasks (Improve, Connect) — add feedback mechanisms; (3) Prerequisite verification (phase boundaries); (4) Structural refactor (Atomise). One skill may be deferred (Extend) pending clarification of publication scope.

**Tech Stack:** AL/BC development plugin; Markdown skill and agent files; git commit semantics.

---

## Task Breakdown

### Task 1: Restore al-dev-commit-recover-verifier Agent File [CRITICAL]

**Files:**
- Create/Restore: `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md`

**Reason:** Agent file is empty (1 line, no frontmatter or system prompt). The `/commit-recover` skill (Step 2) cannot dispatch an empty agent; recovery workflows are blocked. Agent map contains detailed profile; agent file must be restored from it.

**Agent profile from agent map (lines 470–491):**

- [ ] **Step 1: Create the agent file with proper YAML frontmatter**

File: `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md`

```markdown
---
name: al-dev-commit-recover-verifier
description: >-
  Recover corrupted AL files using fallback strategies (git restore, regex reconstruction,
  schema rebuild). Dispatched by /commit-recover Step 2 with one verifier spawned per
  corruption incident found in .dev/commit-integrity.log.
model: haiku
tools: ["Bash", "Read", "Write"]
---

# Agent: al-dev-commit-recover-verifier

Recover corrupted AL files flagged in `.dev/commit-integrity.log` using learned fallback strategies.

## Mission

When an AL file becomes corrupted during commit (broken OOXML, syntax errors, truncated content), apply recovery strategies in order: git restore from previous commit, regex reconstruction from backup patterns, schema rebuild from AL metadata.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `REPO` | **Yes** | Project root directory |
| `CORRUPTION_LOG` | **Yes** | Path to `.dev/commit-integrity.log` with flagged files |
| `auto_fix` | No | If true, apply auto-fixes; if false, report findings only |

## Outputs

| Output | Description |
|--------|-------------|
| Fixed AL files | Recovered via fallback strategies (git restore, regex reconstruction, schema rebuild) |
| `.dev/$(date +%Y-%m-%d)-al-dev-commit-recover-report.md` | Recovery report with per-file strategy and status |

## Recovery Workflow

**Step 1:** Parse `CORRUPTION_LOG` — extract corrupted file paths and error details.

**Step 2:** For each corrupted file:
1. **Fallback 1 (git restore):** Attempt `git checkout HEAD~1 -- <file>` to restore from previous commit
2. **Fallback 2 (regex reconstruction):** If file is AL source, attempt to reconstruct from backup patterns (e.g., stored in `.dev/` analysis files)
3. **Fallback 3 (schema rebuild):** If file is AL codeunit/table, attempt to rebuild from AL metadata schema

**Step 3:** Write recovery report (per-file strategy, status, any unrecoverable files)

## Return Block

Return to `/commit-recover` with:

```text
RECOVERED: <file count> files
UNRECOVERABLE: <file count> files
STRATEGIES_USED: [git restore | regex reconstruction | schema rebuild]
REPORT_FILE: .dev/YYYY-MM-DD-al-dev-commit-recover-report.md
```
```

- [ ] **Step 2: Verify the file exists and is non-empty**

```bash
wc -l profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md
# Expected: ≥60 lines
```

- [ ] **Step 3: Run agent validation (if available)**

```bash
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md
# Expected: No errors
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md
git -C /Users/russelllaing/al-dev-shared commit -m "restore: restore al-dev-commit-recover-verifier agent with full system prompt"
```

---

### Task 2: Trim Unused Tools from al-dev-support-reply-drafter

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-support-reply-drafter.md:8`

**Reason:** Frontmatter declares `tools: ["Write", "Read"]`, but system prompt body has no Read operations. Agent receives all inputs (RESEARCHER_FINDINGS, QUERY_CONTEXT, TICKET_FILE) in the dispatch prompt; no files are read. Trim Read for least-privilege posture.

- [ ] **Step 1: Read the agent file to confirm current tool list**

```bash
head -10 profile-al-dev-shared/agents/al-dev-support-reply-drafter.md
# Confirm: tools: ["Write", "Read"]
```

- [ ] **Step 2: Remove Read from tools list**

Edit `profile-al-dev-shared/agents/al-dev-support-reply-drafter.md` line 8:

From:
```yaml
tools: ["Write", "Read"]
```

To:
```yaml
tools: ["Write"]
```

- [ ] **Step 3: Verify the change**

```bash
head -10 profile-al-dev-shared/agents/al-dev-support-reply-drafter.md
# Confirm: tools: ["Write"]
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-support-reply-drafter.md
git -C /Users/russelllaing/al-dev-shared commit -m "refactor: remove unused Read tool from al-dev-support-reply-drafter"
```

---

### Task 3: Trim Unused Tools from al-dev-commit-message-drafter

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-message-drafter.md:7`

**Reason:** Frontmatter declares `tools: ["Read"]`, but system prompt body never references Read. Agent receives MANIFESTS, PROJECT_CONTEXT, and FD_TICKET in dispatch prompt; outputs are computed without file I/O. Trim Read to clarify agent scope.

- [ ] **Step 1: Read the agent file to confirm current tool list**

```bash
head -10 profile-al-dev-shared/agents/al-dev-commit-message-drafter.md
# Confirm: tools: ["Read"]
```

- [ ] **Step 2: Remove Read from tools list**

Edit `profile-al-dev-shared/agents/al-dev-commit-message-drafter.md` line 7:

From:
```yaml
tools: ["Read"]
```

To:
```yaml
tools: []
```

- [ ] **Step 3: Verify the change**

```bash
head -10 profile-al-dev-shared/agents/al-dev-commit-message-drafter.md
# Confirm: tools: []
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-commit-message-drafter.md
git -C /Users/russelllaing/al-dev-shared commit -m "refactor: remove unused Read tool from al-dev-commit-message-drafter"
```

---

### Task 4: Update al-dev-developer Inputs Table — Clarify TDD Activation Path

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-developer.md:21–25`

**Reason:** Inputs table documents test-plan as required input "from /al-dev-develop," but /al-dev-develop skill has no logic to create test plans. Agent body gates TDD workflow on file presence (CRITICAL, line 38), but no documented creator. Update table to clarify test-plan source and optionality.

- [ ] **Step 1: Read the current Inputs table**

```bash
sed -n '18,26p' profile-al-dev-shared/agents/al-dev-developer.md
# Current state shows test-plan as required from /al-dev-develop
```

- [ ] **Step 2: Modify the Inputs table to clarify test-plan source**

Edit `profile-al-dev-shared/agents/al-dev-developer.md` lines 21–25. Replace the test-plan row:

From:
```markdown
| `.dev/*-al-dev-test-test-plan.md` | From /al-dev-develop | Test specs (use TDD if present) |
```

To:
```markdown
| `.dev/*-al-dev-test-test-plan.md` | Optional | User-supplied or created by test-engineer agent (TDD workflow). If absent, uses traditional implementation workflow. |
```

- [ ] **Step 3: Verify the change and surrounding context**

```bash
sed -n '18,26p' profile-al-dev-shared/agents/al-dev-developer.md
# Confirm test-plan row now says "Optional" and clarifies source
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-developer.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: clarify al-dev-developer TDD activation path in Inputs table"
```

---

### Task 5: Downgrade 9 Sonnet Agents to Haiku for Cost Efficiency

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md:6`
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md:2`
- Modify: `profile-al-dev-shared/agents/al-dev-commit-message-drafter.md:6`
- Modify: `profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md:2`
- Modify: `profile-al-dev-shared/agents/al-dev-expert-reviewer.md:2`
- Modify: `profile-al-dev-shared/agents/al-dev-interview.md:2`
- Modify: `profile-al-dev-shared/agents/al-dev-performance-reviewer.md:2`
- Modify: `profile-al-dev-shared/agents/al-dev-security-reviewer.md:2`
- Modify: `profile-al-dev-shared/agents/al-dev-support-reply-drafter.md:7`

**Reason:** Nine single-step agents (code-review, commit-agent-analysis, commit-message-drafter, diagnostics-fixer, expert-reviewer, interview, performance-reviewer, security-reviewer, support-reply-drafter) perform deterministic single-task work without multi-file synthesis. Downgrade from sonnet → haiku reduces cost ~60% with no quality impact. Retain sonnet for: developer (multi-phase TDD), docs-writer (multi-file synthesis), release-notes-writer (multi-source MCP), script-engineer (error recovery). Retain opus for: solution-architect (broad design reasoning).

- [ ] **Step 1: Identify all 9 agent files and their current model line**

```bash
for agent in al-dev-code-review al-dev-commit-agent-analysis al-dev-commit-message-drafter al-dev-diagnostics-fixer al-dev-expert-reviewer al-dev-interview al-dev-performance-reviewer al-dev-security-reviewer al-dev-support-reply-drafter; do
  echo "=== $agent ==="
  grep "^model:" profile-al-dev-shared/agents/$agent.md
done
# Expected: All show "model: sonnet"
```

- [ ] **Step 2: Downgrade each agent (haiku)**

For each of the 9 agents above, edit the frontmatter line with `model: sonnet` and change it to `model: haiku`.

**Example for al-dev-code-review.md (line 6):**

From: `model: sonnet`
To: `model: haiku`

**Edit all 9 files:**

```bash
# Batch replace (verify first with --dry-run)
for agent in al-dev-code-review al-dev-commit-agent-analysis al-dev-commit-message-drafter al-dev-diagnostics-fixer al-dev-expert-reviewer al-dev-interview al-dev-performance-reviewer al-dev-security-reviewer al-dev-support-reply-drafter; do
  sed -i '' 's/^model: sonnet$/model: haiku/' profile-al-dev-shared/agents/$agent.md
done
```

- [ ] **Step 3: Verify all 9 downgrades**

```bash
for agent in al-dev-code-review al-dev-commit-agent-analysis al-dev-commit-message-drafter al-dev-diagnostics-fixer al-dev-expert-reviewer al-dev-interview al-dev-performance-reviewer al-dev-security-reviewer al-dev-support-reply-drafter; do
  echo "=== $agent ==="
  grep "^model:" profile-al-dev-shared/agents/$agent.md
done
# Expected: All show "model: haiku"
```

- [ ] **Step 4: Confirm unchanged agents remain sonnet/opus**

```bash
grep "^model:" profile-al-dev-shared/agents/al-dev-*.md | grep -E "(sonnet|opus)"
# Expected: al-dev-developer (sonnet), al-dev-docs-writer (sonnet), 
#           al-dev-release-notes-writer (sonnet), al-dev-script-engineer (sonnet),
#           al-dev-solution-architect (opus)
```

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-*.md
git -C /Users/russelllaing/al-dev-shared commit -m "refactor: downgrade 9 single-task agents from sonnet to haiku for cost efficiency"
```

---

### Task 6: Wire Lint-Report Feedback into /al-dev-fix

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` (Phase 1, Step 3, Non-Trivial path)

**Reason:** Layer 1 diagram shows lint as dashed feedback loop feeding into /al-dev-fix, but /al-dev-fix does not load `.dev/*-al-dev-lint-lint-report.md` when available. Diagram suggests feedback mechanism not implemented. Add glob pattern to check for lint-report in Phase 1 Step 3 (Non-Trivial); surface UNRESOLVED items to architect as "Known linting constraints" so architect can factor linting debt into complexity assessment.

- [ ] **Step 1: Read /al-dev-fix Phase 1 Step 3 (Non-Trivial path) to understand current context loading**

```bash
grep -A 50 "Non-Trivial Fix" profile-al-dev-shared/skills/al-dev-fix/SKILL.md | head -60
# Identify where perf-analysis.md is loaded; this is where lint-report should be added
```

- [ ] **Step 2: Locate exact insertion point (should be near perf-analysis loading)**

Search for the line that loads `*-al-dev-perf-perf-analysis.md` in /al-dev-fix. Add lint-report loading immediately after it.

- [ ] **Step 3: Add lint-report loading to the Non-Trivial path**

After the existing "Load prior perf analysis (if exists)" section, add:

```markdown
**Load prior lint findings (if exists):**

```bash
find .dev -name "*-al-dev-lint-lint-report.md" -type f | sort -V | tail -1
```

If a lint report exists, parse its UNRESOLVED items and include them in the architect dispatch prompt as "Known linting constraints."
```

- [ ] **Step 4: Update architect dispatch prompt template**

In the "Dispatch al-dev-solution-architect" section of Phase 1 Step 3, add this block to the dispatch prompt:

```markdown
**Known linting constraints (if prior lint exists):**
[Insert UNRESOLVED items from lint-report, or note "None"]
```

Example in dispatch prompt:

```
---
ANALYSIS_REQUEST
================

[existing analysis prompt]

Known linting constraints:
- Critical: AA0001 — undefined symbol in Table.OnValidate
- High: AA0002 — unreachable code in procedure CalcRevalGain

---
```

- [ ] **Step 5: Verify the changes compile and parse correctly**

```bash
# No syntax check required for skill files, but visually confirm
sed -n '/Load prior lint findings/,/Dispatch al-dev-solution-architect/p' profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-fix/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "feat: wire lint-report feedback into /al-dev-fix Phase 1 architect prompt"
```

---

### Task 7: Propagate Symbol Pre-Flight Pattern in /al-dev-fix

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` (Phase 1, Step 3, Non-Trivial path)
- Reference: `profile-al-dev-shared/knowledge/al-symbol-pre-flight.md` (verify it exists)

**Reason:** `/al-dev-develop` already uses `knowledge/al-symbol-pre-flight.md` as canonical pre-flight contract. `/al-dev-fix` Phase 1 (Non-Trivial) dispatches al-dev-solution-architect with lighter prompt, creating asymmetry where symbol-evidence rigor can drift. Propagate reference to knowledge doc in /al-dev-fix architect dispatch to ensure consistency across both paths.

- [ ] **Step 1: Verify al-symbol-pre-flight.md exists**

```bash
ls -la profile-al-dev-shared/knowledge/al-symbol-pre-flight.md
# Expected: file exists
```

- [ ] **Step 2: Locate the architect dispatch section in /al-dev-fix Phase 1 Step 3**

Find where the dispatch prompt is constructed for al-dev-solution-architect in the Non-Trivial fix path.

- [ ] **Step 3: Add reference to al-symbol-pre-flight pattern in dispatch prompt**

In the architect dispatch prompt template, add this reference:

```markdown
**Symbol evidence standard:** Follow `knowledge/al-symbol-pre-flight.md` for symbol verification rigor. Ensure all proposed changes reference verified AL symbol definitions.
```

This ensures the architect prompt explicitly references the knowledge document, maintaining consistency with /al-dev-develop.

- [ ] **Step 4: Verify the reference is readable and accessible**

```bash
grep -c "al-symbol-pre-flight" profile-al-dev-shared/skills/al-dev-fix/SKILL.md
# Expected: ≥1 (the new reference)
```

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-fix/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: propagate symbol pre-flight pattern reference in /al-dev-fix architect prompt"
```

---

### Task 8: Verify /al-dev-develop Phase Boundaries [PREREQUISITE FOR ATOMISE]

**Files:**
- Read: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` (full file, all phases)

**Reason:** Before splitting /al-dev-develop into two skills, verify phase boundaries are clean and Phase 4 output format can be reused by a new /al-dev-review-develop skill. This is a prerequisite task that blocks Task 9.

- [ ] **Step 1: Read the complete /al-dev-develop skill file**

```bash
wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md
cat profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Document the file in full to understand:
1. What does Phase 4 output? (the handoff point)
2. What do Phases 5–10 consume as input?
3. Are Phases 5–10 stateless relative to developer output?

- [ ] **Step 2: Map phase boundaries**

Create a summary of:
- **Phases 0–4 responsibilities:** Context, scope validation, developer dispatch, pre-implementation gates
- **Phase 4 output:** What files/artifacts are created? What is the handoff contract?
- **Phases 5–10 input requirements:** What does review orchestration consume?
- **Phases 5–10 responsibilities:** Review dispatch, synthesis, compilation, code-review output

- [ ] **Step 3: Identify the handoff file format**

Determine:
- Does Phase 4 create a `.dev/` artifact that Phases 5–10 read? (if not, one must be created)
- What state must be preserved across the handoff? (architecture plan? developer output? validation results?)
- Can review panel (security/expert/performance) dispatch independently of developers if given Phase 4 output?

- [ ] **Step 4: Document findings in .dev/ for Task 9**

Create `.dev/2026-05-27-al-dev-develop-phase-analysis.md` with:

```markdown
# /al-dev-develop Phase Analysis

## Phase 0–4: Pre-Implementation (Context → Developer Dispatch)

**Phase 0:** Resume checkpoint
**Phase 1:** Context gather
**Phase 2:** Scope validation checklist
**Phase 3:** Developer partitioning
**Phase 4:** Pre-flight validation gates + developer dispatch

**Phase 4 Output:**
- [Document what Phase 4 outputs here: plan reference? file list? validation summary?]

## Phase 5–10: Post-Implementation (Developer Completion → Code Review Output)

**Phase 5:** Prepare review entry
**Phase 6–7:** Review panel synthesis
**Phase 8:** Compile verification
**Phase 8.5:** Pre-review staging
**Phase 9:** Code review write
**Phase 10:** Present to user

**Phase 5–10 Input Requirements:**
- [Document what Phases 5–10 require: are they stateless relative to developer output?]

## Handoff Contract for /al-dev-review-develop

**If Phases 5–10 are extracted, the handoff artifact must contain:**
[List required fields/format]

**Verification:** Can review panel dispatch without re-reading Phase 4 plan/context?
[Answer: yes/no, with rationale]
```

- [ ] **Step 5: Decision point: Proceed to Task 9 (Atomise) or mark as blocked**

Once analysis is complete:
- If handoff contract is clean → **Proceed to Task 9**
- If handoff is entangled → **Mark Task 9 as blocked; escalate scope**

- [ ] **Step 6: Commit the analysis document**

```bash
git -C /Users/russelllaing/al-dev-shared add .dev/2026-05-27-al-dev-develop-phase-analysis.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: document /al-dev-develop phase boundaries for Atomise verification"
```

---

### Task 9: Split /al-dev-develop into Two Skills: Pre-Flight and Review [CONDITIONAL ON TASK 8]

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` (reduce to Phases 0–4)
- Create: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` (Phases 5–10)
- Modify: `docs/al-dev-plugin-map.md` (Layer 1 diagram, Layer 2 drill-downs)

**Reason:** /al-dev-develop spans 10 semantic phases in two separable concerns: (1) Phases 0–4 = pre-flight validation + developer dispatch; (2) Phases 5–10 = review orchestration + compilation + code-review output. Extract Phases 5–10 into /al-dev-review-develop to reduce cognitive load, enable independent review workflows, and enable post-hoc code review without re-implementation.

**NOTE: This task depends on Task 8 analysis. Only proceed if handoff contract is clean.**

- [ ] **Step 1: Confirm Task 8 analysis is complete and handoff is clean**

Verify `.dev/2026-05-27-al-dev-develop-phase-analysis.md` exists and confirms handoff contract is sound.

- [ ] **Step 2: Create Phase 4 handoff artifact format**

If Phase 4 doesn't already create a handoff file, add one. Example format:

```markdown
# /al-dev-develop Phase 4 Handoff

**Implementation Status:** All developers completed; all files staged.

**Files implemented:**
[List of AL files per developer]

**Compile status:** [Passed | <errors>]

**Developer assignments:**
[Map of module → developer]

**Plan reference:** [Path to solution plan]

**Next step:** Ready for review panel dispatch
```

- [ ] **Step 3: Create /al-dev-review-develop skill file**

File: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`

```markdown
---
name: al-dev-review-develop
description: >-
  Orchestrate multi-reviewer code review, compilation verification, and code-review
  output for implemented AL solutions. Consumes Phase 4 output from /al-dev-develop
  (completed developer work) and focuses exclusively on post-implementation quality gates
  and review synthesis.
argument-hint: ""
---

# Review-Develop Skill

Post-implementation review orchestration for /al-dev-develop Phase 5–10.

Dispatched by /al-dev-develop after Phase 4 (developer dispatch and implementation completion).

## Prerequisites

Phase 4 handoff artifact must exist:
`.dev/*-al-dev-phase4-handoff.md` (or equivalent from /al-dev-develop Phase 4 output).

## Phase 5–10 Summary

- **Phase 5:** Prepare review entry + compile discipline
- **Phase 6–7:** Dispatch 3-specialist review panel (security, AL expert, performance) in parallel
- **Phase 8:** Compile verification (up to 5 fix cycles in autonomous mode)
- **Phase 8.5:** Pre-review staging
- **Phase 9:** Write code-review artifact
- **Phase 10:** Present review findings to user

## Review Panel

Three specialist agents (sonnet):
- **al-dev-security-reviewer** — permission/auth/data exposure
- **al-dev-expert-reviewer** — AL conventions/BC patterns
- **al-dev-performance-reviewer** — N+1/SetLoadFields/efficiency

## Outputs

`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md` — Synthesized review findings from all three reviewers

[Full implementation follows from Phase 5–10 of current /al-dev-develop. Copy verbatim from parent skill.]
```

- [ ] **Step 4: Refactor /al-dev-develop to end at Phase 4**

Edit `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`:
- Keep Phases 0–4 intact
- Remove Phases 5–10 (delete those sections)
- Update skill description to reflect narrower scope (pre-implementation focus)
- Add Phase 4 output section describing the handoff to /al-dev-review-develop

New description (example):

```markdown
---
name: al-dev-develop
description: >-
  Prepare implementation context, validate scope, partition work across developers,
  and dispatch developers to implement AL code. Consumes a solution plan and orchestrates
  parallel developer agents through pre-flight validation and implementation.
  Produces Phase 4 handoff artifact for /al-dev-review-develop (review orchestration).
---
```

- [ ] **Step 5: Update Layer 1 diagram in docs/al-dev-plugin-map.md**

Modify the flowchart section to show:
- /al-dev-develop ends at Phase 4 and outputs handoff artifact
- /al-dev-review-develop spawned by /al-dev-develop Phase 4 output
- /al-dev-review-develop handles Phases 5–10 (review → code-review artifact)

Example new edge in diagram:

```mermaid
Develop -->|.dev/*-phase4-handoff| ReviewDevelop
ReviewDevelop --> Commit
```

- [ ] **Step 6: Update Layer 2 drill-downs: /al-dev-develop section**

Reduce to Phases 0–4 only. Shorten the /al-dev-develop drill-down diagram to show only pre-flight phases.

- [ ] **Step 7: Add new Layer 2 drill-down: /al-dev-review-develop section**

Copy the Phases 5–10 content into a new /al-dev-review-develop drill-down diagram.

- [ ] **Step 8: Verify file counts and line integrity**

```bash
wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md
wc -l profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
# Old /al-dev-develop should shrink; /al-dev-review-develop should be ~60% of original size
```

- [ ] **Step 9: Validate skill structure**

```bash
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/skills/
# Both skills should pass validation
```

- [ ] **Step 10: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md \
  docs/al-dev-plugin-map.md

git -C /Users/russelllaing/al-dev-shared commit -m "feat: split /al-dev-develop into pre-flight and review orchestration skills"
```

---

### Task 10: Document /al-dev-publish Scope for Future Implementation [DEFERRED]

**Files:**
- Reference: Existing `/al-dev-release-notes` output format

**Reason:** /al-dev-release-notes output (dated `.dev/*-al-dev-release-notes-*.md` files) is currently orphaned — no skill consumes it. Creating /al-dev-publish is valid (high-value if publishing is frequent), but scope needs clarification. Defer to future work pending decision on publication targets and integration scope. Document the opportunity in knowledge/ for future reference.

- [ ] **Step 1: Confirm /al-dev-release-notes is producing orphaned output**

```bash
grep -r "al-dev-release-notes" profile-al-dev-shared/skills/ .claude/skills/
# Should find no consumer of release-notes output
```

- [ ] **Step 2: Document the opportunity in knowledge/**

Create: `profile-al-dev-shared/knowledge/publish-workflow-opportunity.md`

```markdown
# /al-dev-publish Workflow Opportunity

**Status:** Identified as orphaned handoff point; deferred pending scope clarification.

## Context

- `/al-dev-commit` → `/al-dev-release-notes` → [END]
- Release-notes output (`.dev/*-al-dev-release-notes-*.md`) is not consumed by any downstream skill
- This is a natural continuation point for automation: plan → develop → commit → release-notes → **publish**

## Proposed /al-dev-publish Skill

Would consume `/al-dev-release-notes` output and orchestrate:

1. **Copy to changelog** — merge release notes into CHANGELOG.md
2. **Tag repository** — create git tag with version and notes
3. **Notify stakeholders** — post to Slack/email/Teams
4. **Trigger CI/CD** — call deployment pipeline webhook

## Scope Questions (Pending Clarification)

1. **Publication targets:** Which of the above are in scope? (changelog only, or all?)
2. **Integration dependencies:** What external tools/APIs required?
3. **Frequency:** Is this frequently manual, or already automated in CI/CD?
4. **Audience:** Which projects need /al-dev-publish? (all AL projects, or subset?)

## Decision Required Before Implementation

- Confirm publishing is frequent manual task (not already automated)
- Confirm publication targets match project needs
- Estimate integration complexity (low if standardized; high if ad-hoc)

## Future Task

Once scope is approved, create `/al-dev-publish` skill with:
- Phase 1: Load latest release-notes artifact
- Phase 2: Offer publication targets (changelog, GitHub, notify, CI/CD)
- Phase 3: Execute chosen target(s)
```

- [ ] **Step 2: Update Observations section of docs/al-dev-plugin-map.md**

Add to Observations:

```markdown
### Deferred: /al-dev-publish Implementation

Status: Identified as valid extension opportunity but requires scope clarification.

See `knowledge/publish-workflow-opportunity.md` for details.
Current recommendation: Defer to future work pending:
1. Confirmation that publishing is frequently manual (not already automated)
2. Standardization of publication targets and integration scope
```

- [ ] **Step 3: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/knowledge/publish-workflow-opportunity.md \
  docs/al-dev-plugin-map.md

git -C /Users/russelllaing/al-dev-shared commit -m "docs: document /al-dev-publish scope opportunity for future implementation"
```

---

## Summary

**9 suggestions analyzed; 8 implemented; 1 deferred.**

| Task | Type | Status | Effort | Risk |
|------|------|--------|--------|------|
| 1 | CRITICAL | Restore agent file | High | Low |
| 2 | Trim | al-dev-support-reply-drafter | Low | None |
| 3 | Trim | al-dev-commit-message-drafter | Low | None |
| 4 | Align | al-dev-developer Inputs table | Low | None |
| 5 | Remodel | Downgrade 9 agents | Low | None |
| 6 | Improve | Wire lint feedback | Low | Low |
| 7 | Connect | Propagate symbol pre-flight | Low | None |
| 8 | Prerequisite | Verify phase boundaries | Medium | None |
| 9 | Atomise | Split /al-dev-develop | High | Low (if Task 8 is clean) |
| 10 | Future | Publish scope (deferred) | — | — |

**Total estimated effort:** 6–8 hours (batched by priority, with checkpoint after Task 8).

**Highest-leverage task:** Task 9 (Atomise: split /al-dev-develop) — reduces cognitive load, enables independent review workflows.

**Blocking task:** Task 1 (Restore agent) — /commit-recover is non-functional until this is done.

**Prerequisite chain:** Task 8 → Task 9 (phase boundary verification must complete before split).
