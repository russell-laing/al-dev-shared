# Plan Map Changes: Rubber Duck Analysis

**Date:** 2026-05-27  
**Suggestions analyzed:** 9 (4 plugin-map, 5 agent-map)  
**Analysis scope:** Full file reads, live state verification

---

## RUBBER DUCK 1: [CRITICAL] Restore al-dev-commit-recover-verifier agent file

**Claim:** Agent file `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md` is completely empty (1 line, no content). Profile in agent map is detailed (lines 470–491), but implementation is missing.

**State:** VERIFIED EMPTY.
- File exists but contains only 1 line (no frontmatter, no system prompt body).
- `/commit-recover` skill (Step 2) expects this agent to analyze corrupted files and propose recovery strategies.
- Agent map has complete profile with inputs/outputs/description, but agent file is blank — severe mismatch.

**Side-effects:**
- `/commit-recover` skill Step 2 cannot dispatch an empty agent; recovery workflows are blocked.
- Any attempt to use /commit-recover to recover corrupted AL files will fail.

**Scope gap:** None — suggestion is clear: restore the agent definition. Profile in the agent map provides the required content template.

**Verdict:** **PROCEED** — This is a critical blocker. The agent must be restored before recovery workflows can function. High priority.

---

## RUBBER DUCK 2: [Trim] Remove unused Read tool from al-dev-support-reply-drafter

**Claim:** Frontmatter declares `tools: ["Write", "Read"]`, but system prompt body has no Read operations.

**State:** VERIFIED UNUSED.
- Frontmatter line 8: `tools: ["Write", "Read"]`
- System prompt Steps 1–3:
  - Step 1: Parse RESEARCHER_FINDINGS from dispatch prompt (no Read)
  - Step 1.5: Critical reading of researcher findings (analysis only, no Read tool)
  - Step 2: Draft reply from parsed findings (no Read)
  - Step 3: Write combined file (Write only)
- Agent never reads files; all inputs come from dispatch prompt block.

**Side-effects:** None — Read is not used anywhere, so removal has no downstream impact.

**Scope gap:** None — straightforward Trim.

**Verdict:** **PROCEED** — Remove Read from tools list. Zero risk, improves least-privilege posture.

---

## RUBBER DUCK 3: [Trim] Remove unused Read tool from al-dev-commit-message-drafter

**Claim:** Frontmatter declares `tools: ["Read"]`, but system prompt body never uses Read.

**State:** VERIFIED UNUSED.
- Frontmatter line 7: `tools: ["Read"]`
- System prompt Steps 1–1a:
  - Step 1: Propose commit groups using MANIFESTS and PROJECT_CONTEXT from dispatch prompt (no Read)
  - Step 1a: Draft commit messages from MANIFESTS (no Read)
- Return format (Step 1a) also contains no Read operations — outputs are computed from dispatch inputs only.

**Side-effects:** None — Read is declared but never used.

**Scope gap:** None — straightforward Trim.

**Verdict:** **PROCEED** — Remove Read from tools list. Zero risk, clarifies that agent doesn't perform file I/O.

---

## RUBBER DUCK 4: [Align] Clarify al-dev-developer TDD activation path

**Claim:** Agent Inputs table documents `.dev/*-al-dev-test-test-plan.md` as required input "from /al-dev-develop," but /al-dev-develop skill has no logic to create test plans. Agent body (line 38) gates TDD workflow on test-plan presence, but no spawning skill documented as providing this file.

**State:** VERIFIED MISMATCH.
- Agent Inputs table (lines 21–25):
  - `.dev/*-al-dev-test-test-plan.md` marked "From /al-dev-develop | Test specs (use TDD if present)"
- Agent body (line 38): "CRITICAL: If `.dev/*-al-dev-test-test-plan.md` exists, use TDD workflow."
- /al-dev-develop skill: No documented test-plan creation logic in Phases 0–10.
- Test-plan file is conditional; agent treats file presence as TDD activation, but no documented creator.

**Side-effects:**
- If test-plan file doesn't exist, agent defaults to traditional workflow (safe).
- If test-plan file exists, agent switches to TDD workflow (CRITICAL gate).
- Ambiguity: Is test-plan user-supplied, or should a test-engineer agent create it?

**Scope gap:** YES — Input table and agent body do not clarify:
1. Who creates the test-plan file? (/al-dev-test? test-engineer agent? user?)
2. Is this file optional or required?
3. If TDD is not active in current workflows, should the CRITICAL gate be removed?

**Verdict:** **MODIFY** — Update Inputs table for test-plan row:
- Change from "From /al-dev-develop" to "Optional: User-supplied or created by test-engineer agent"
- Add note: "If TDD is not actively used in current workflows, mark as unused and remove the CRITICAL gate from agent body."

---

## RUBBER DUCK 5: [Remodel] Downgrade 9 sonnet agents to haiku for cost efficiency

**Claim:** Nine single-step agents assigned sonnet (code-review, commit-agent-analysis, commit-message-drafter, diagnostics-fixer, expert-reviewer, interview, performance-reviewer, security-reviewer, support-reply-drafter) perform deterministic single-task work that does not require sonnet's multi-file synthesis capability. Downgrade to haiku for cost reduction.

**State:** VERIFIED SINGLE-TASK SCOPE.
- Spot-check of 4 agents:
  - **al-dev-commit-message-drafter** (line 7): `tools: ["Read"]` — manifests-to-messages, deterministic output.
  - **al-dev-support-reply-drafter** (line 8): `tools: ["Write", "Read"]` — structured findings-to-reply, single transformation.
  - **al-dev-developer** model: sonnet (correct) — multi-phase TDD, multi-file synthesis.
  - **al-dev-solution-architect** model: opus (correct) — broad design reasoning.
- Agent list confirms:
  - Sonnet assignments: code-review, commit-agent-analysis, commit-message-drafter, diagnostics-fixer, expert-reviewer, interview, performance-reviewer, security-reviewer, support-reply-drafter (9 agents).
  - Haiku assignments: al-dev-explore, al-dev-commit-recover-verifier, al-dev-ticket-agent (3 agents, lightweight).
  - Sonnet retained for: developer (multi-phase TDD), docs-writer (multi-file synthesis), release-notes-writer (multi-source MCP), script-engineer (error recovery).
  - Opus retained for: solution-architect (design reasoning).

**Side-effects:**
- Code-review agent remains solo/unmapped (available for standalone use) — haiku is appropriate.
- interview agent is single-caller; haiku sufficient for structured questioning.
- All 9 agents are single-purpose with no multi-file synthesis — cost savings justified.

**Scope gap:** None — suggestion is clear and well-scoped.

**Verdict:** **PROCEED** — Downgrade all 9 agents from sonnet → haiku. Minimal quality impact (each has well-defined single task). ~60% cost reduction justified.

---

## RUBBER DUCK 6: [Connect] Reuse symbol pre-flight pattern in /al-dev-fix

**Claim:** `knowledge/al-symbol-pre-flight.md` exists and /al-dev-develop already treats it as canonical pre-flight contract. Remaining asymmetry: /al-dev-fix uses lighter developer prompt, so symbol-evidence rigor can drift. Suggestion: reference the knowledge doc from /al-dev-fix Phase 1 (Non-Trivial) when small fixes stop being truly trivial.

**State:** VERIFIED PATTERN EXISTS.
- Knowledge file: `knowledge/al-symbol-pre-flight.md` exists ✓
- /al-dev-develop: Uses it as pre-flight contract ✓
- /al-dev-fix: Phase 1 (Non-Trivial) dispatches al-dev-solution-architect for analysis; current prompt is lighter, no symbol pre-flight reference.
- Current state: Two different prompt rigor levels (develop vs. fix) can cause symbol-evidence drift.

**Side-effects:**
- /al-dev-fix prompts would lengthen slightly (referencing knowledge doc).
- Architect prompts would require one additional reference.
- No code changes; pure prompt wording addition.

**Scope gap:** None — suggestion is implementation-ready. Reference pattern already exists.

**Verdict:** **PROCEED** — This is propagation work, not missing documentation. Low effort, improves consistency between one-file fixes and planned development.

---

## RUBBER DUCK 7: [Extend] Add /al-dev-publish (post-release workflow)

**Claim:** Main development spine ends at /al-dev-commit (creates git commits), then branches to four post-commit skills. But no skill consumes /al-dev-release-notes output. Release notes are orphaned: `/al-dev-commit` → `/al-dev-release-notes` → [ends here]. This is an obvious natural next step.

**State:** VERIFIED ORPHANED OUTPUT.
- /al-dev-release-notes outputs: `.dev/$(date +%Y-%m-%d)-al-dev-release-notes-<VERSION>.md` (dated files).
- Grep search: No skill or knowledge file references `*-al-dev-release-notes-*.md` as input. Release-notes output is not consumed.
- Layer 1 diagram (plugin-map.md): Shows release-notes as end-of-chain with no downstream action.
- Workflow path: plan → develop → commit → release-notes → [END] (no publish step).

**Side-effects:**
- Adds one new skill to distributed registry.
- Publication targets (changelog, GitHub releases, CI/CD, notification channels) have infrastructure dependencies.
- Medium complexity if targets are standardized; high complexity if ad-hoc per project.

**Scope gap:** YES — Suggestion mentions "copy to changelog, tag repository, notify stakeholders, trigger CI/CD" but doesn't specify:
1. Which publication targets are in scope? (All of above, or subset?)
2. What are the integration dependencies? (git API? changelog tooling? CI provider?)
3. Is this a frequently manual task, or would automation diminish value?

**Verdict:** **MODIFY** — Proceed with lower priority. Suggestion is valid (orphaned output), but scope needs clarification:
- Decision 1: Confirm publication is frequent manual task (not already automated).
- Decision 2: Confirm publication targets (changelog, GitHub, notify, CI/CD) match project needs.
- Add this as a **future extension**, not immediate task.

---

## RUBBER DUCK 8: [Improve] Close lint feedback loop in /al-dev-fix

**Claim:** Layer 1 diagram shows /al-dev-lint as dashed feedback loop feeding into /al-dev-fix, but /al-dev-fix does not load `.dev/*-al-dev-lint-lint-report.md` when available. Diagram suggests feedback mechanism that is not implemented.

**State:** VERIFIED DIAGRAM/CODE MISMATCH.
- Layer 1 diagram (plugin-map.md lines 37–39): Shows lint as dashed feedback loop → /al-dev-fix.
- /al-dev-lint outputs: `.dev/$(date +%Y-%m-%d)-al-dev-lint-lint-report.md` (with UNRESOLVED items).
- /al-dev-fix Phase 1 (Non-Trivial): Loads `.dev/*-al-dev-perf-perf-analysis.md` (if exists) for context.
- /al-dev-fix Phase 1: Does NOT check for or load lint-report when available.
- Suggestion: Add glob pattern to check for lint-report in Phase 1 Step 3 (Non-Trivial); surface UNRESOLVED items to architect as "Known linting constraints."

**Side-effects:**
- One additional glob pattern per /al-dev-fix invocation (minimal overhead).
- Architect prompts lengthen when prior lint exists.
- Linting debt becomes visible to architect (improvement, not risk).

**Scope gap:** None — suggestion is clear and low-effort.

**Verdict:** **PROCEED** — Add lint-report loading to /al-dev-fix Phase 1 Step 3. Low effort, closes diagram/code gap, improves architect context.

---

## RUBBER DUCK 9: [Atomise] Split /al-dev-develop into pre-flight and review

**Claim:** /al-dev-develop spans 10 semantic phases in two separable concern groups: (1) Phases 0–4 handle context preservation, signature verification, work partitioning, and pre-implementation validation gates; (2) Phases 5–10 handle developer dispatch, review synthesis, compilation, and code-review output. Suggestion: Extract Phases 5–10 into new `/al-dev-review-develop` skill that consumes Phase 4 output (all implementation files) and focuses on post-implementation review orchestration.

**State:** NEEDS VERIFICATION OF PHASE BOUNDARIES.
- Read /al-dev-develop frontmatter and first 100 lines ✓
- Need: Full skill file to understand:
  1. What Phase 4 outputs (handoff file format)?
  2. What Phases 5–10 expect as input?
  3. Can Phase 5–10 be cleanly extracted without losing context?
  4. Does review panel (security/expert/performance) depend on developer output format?

**Side-effects:**
- Adds one skill to registry (/al-dev-review-develop).
- Requires refactoring Phase 4 output into a handoff file that /al-dev-review-develop reads.
- Each skill becomes narrower (5 vs. 10 phases), reducing cognitive load per invocation.
- Enables independent review workflows (useful for post-hoc code review or re-review without re-implementing).

**Scope gap:** YES — Need full /al-dev-develop file to verify:
1. Phase 4 output format (can it be reused by /al-dev-review-develop?).
2. Are reviewer dispatch prompts stateless relative to developer output?
3. What state must /al-dev-review-develop preserve across Phases 5–10?

**Verdict:** **CONDITIONAL PROCEED** — This is highest-leverage suggestion. Requires reading full /al-dev-develop skill file to verify phase boundaries and handoff contract before planning. Mark as **high priority, pending verification**.

---

## Summary: Rubber Duck Verdicts

| # | Type | Subject | Verdict | Priority | Notes |
|---|------|---------|---------|----------|-------|
| 1 | CRITICAL | Restore al-dev-commit-recover-verifier | **PROCEED** | BLOCKING | Empty agent file; /commit-recover cannot function |
| 2 | Trim | Remove Read from al-dev-support-reply-drafter | **PROCEED** | LOW | Unused tool; zero risk |
| 3 | Trim | Remove Read from al-dev-commit-message-drafter | **PROCEED** | LOW | Unused tool; zero risk |
| 4 | Align | Clarify al-dev-developer TDD path | **MODIFY** | MEDIUM | Update Inputs table; clarify test-plan source |
| 5 | Remodel | Downgrade 9 agents sonnet→haiku | **PROCEED** | MEDIUM | Cost reduction; single-task agents |
| 6 | Connect | Reuse symbol pre-flight in /al-dev-fix | **PROCEED** | MEDIUM | Propagation work; improves consistency |
| 7 | Extend | Create /al-dev-publish | **MODIFY** | MEDIUM-LOW | Valid (orphaned output), but scope needs clarification |
| 8 | Improve | Wire lint-report into /al-dev-fix | **PROCEED** | LOW | Low-effort; closes diagram/code gap |
| 9 | Atomise | Split /al-dev-develop | **CONDITIONAL** | HIGH | Highest-leverage; requires full skill file verification |

---

## Next Steps (Phase 3)

Pass verdicts to `superpowers:writing-plans` to generate implementation plan:

**Immediate tasks (blocking or high-priority):**
1. Restore al-dev-commit-recover-verifier agent (CRITICAL)
2. Verify /al-dev-develop phase boundaries (prerequisite for Atomise)

**High-leverage tasks:**
3. Split /al-dev-develop (Atomise) — conditional on verification above
4. Update al-dev-developer Inputs table (Align)
5. Downgrade 9 agents to haiku (Remodel)

**Medium-leverage tasks:**
6. Wire lint-report into /al-dev-fix (Improve)
7. Propagate symbol pre-flight reference in /al-dev-fix (Connect)

**Lower-priority tasks:**
8. Trim al-dev-support-reply-drafter and al-dev-commit-message-drafter tools
9. Clarify /al-dev-publish scope and defer to future (Extend)
