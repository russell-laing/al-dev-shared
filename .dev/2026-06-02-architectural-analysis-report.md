# Architectural Analysis Report
## al-dev-shared Plugin — 2026-06-02

**Scope:** Full architectural coherence analysis covering 24 active skills, 23 agents, and cross-surface design alignment.

**Methodology:** 
- **Phase 1:** 5 skill design lenses (shared backbone, complexity, near-duplicates, handoff gaps, preplanning)
- **Phase 2:** 5 agent design lenses (tool hygiene, model fit, scope isolation, caller alignment, usage patterns)
- **Phase 3:** Cross-surface synthesis (coupling gaps, model-complexity alignment, shared patterns)

**Original analysis scope:** 60+ architectural issues identified across severity levels (CRITICAL, HIGH, MEDIUM, LOW). The rubber-duck passes below corrected several severities and stale findings without recalculating the original total.

> **Technical accuracy update (Codex rubber-duck pass, 2026-06-02):**
> This report is useful as a triage artifact, but several original findings
> were stale or over-ranked. Treat runtime/projection contract failures and
> generated-map regressions as the first implementation targets. Treat naming,
> phase nomenclature, and broad style cleanup as secondary hygiene unless they
> block a validator or projection contract.

---

## Executive Summary

### Overall Assessment
The plugin exhibits **strong architectural patterns** with well-defined separation of concerns, clear governance gates, and explicit knowledge reuse. The highest-risk issues are concentrated in runtime capability declarations, generated documentation integrity, and incomplete enforcement coverage. Several earlier findings about hidden chaining and tool vocabulary were contradicted by current source.

1. **Runtime Capability Contract Gaps** — 3 agents declare too few capabilities for the workflows they describe
2. **Generated Map Regression Risk** — refreshed diagrams can drop real skill-agent/phase edges
3. **Artifact Contract Coverage Gap** — only the current contract matrix is enforced; durable-output skills outside the matrix remain uncovered
4. **Implicit Coupling at Skill-Agent Boundaries** — some handoffs need clearer contracts, but not all originally listed examples are valid
5. **Naming and Nomenclature Drift** — useful cleanup, but lower priority than executable contract correctness

### Top 5 High-Leverage Actions

| Priority | Issue | Impact | Effort |
|----------|-------|--------|--------|
| **BLOCKER** | Capability declarations missing/underspecified (3 agents) | Runtime failure or unavailable MCP research | 1 hour |
| **HIGH** | Repair/verify generated map refresh behavior | Documentation drift and false architecture decisions | 2-3 hours |
| **HIGH** | Extend artifact-contract coverage through the existing matrix + validator | Completion uncertainty | 6-8 hours |
| **MEDIUM** | Document valid skill-agent coupling contracts | Debugging complexity | 4 hours |
| **LOW/MEDIUM** | Unify naming and phase/step conventions | Developer friction | 4-6 hours |

---

## Phase 1: Skill Design Analysis

**24 Skills Analyzed | 30+ Findings**

### Original Critical Issues (Corrected)

#### 1. Implicit Skill Chaining (STALE — not critical)
- **Skills Affected:** `al-dev-plan` (chains to `al-dev-plan-preflight`), `al-dev-ticket` (chains to `al-dev-support-reply` via `--mode=full`)
- **Pattern:** Skills invoke other skills internally but descriptions don't mention this
- **Impact:** Users invoking `/al-dev-plan` don't know it internally calls `/al-dev-plan-preflight`; unexpected context jumps
- **Technical accuracy update:** **Stale finding.** Current source already documents both examples. `al-dev-plan` frontmatter and body explicitly say it dispatches `/al-dev-plan-preflight`; `al-dev-ticket` frontmatter, mode parsing, and Phase 5 explicitly document `--mode=full` chaining to `/al-dev-support-reply`.
- **Corrected recommendation:** Remove this from the critical list. Keep only a lower-priority handoff-contract task for examples that remain genuinely implicit after live verification.

#### 2. Inconsistent Checkpoint/Resume Patterns (OVERSTATED — medium)
- **Skills Affected:** `al-dev-plan-preflight` (uses `--resume` flag + `.dev/preflight-context.md`), `al-dev-develop` (uses `.dev/progress.md`)
- **Pattern:** Multi-phase skills implement resume differently
- **Impact:** Skills can't share checkpoint infrastructure; resume logic diverges
- **Technical accuracy update:** Directionally valid, but over-severe. `al-dev-plan-preflight` also uses the standard `.dev/progress.md` protocol for mid-run resume; `.dev/preflight-context.md` is a handoff artifact, not only a competing checkpoint format.
- **Corrected recommendation:** Document the distinction between checkpoint artifacts and handoff artifacts before changing formats. Do not force every workflow into one file shape if the artifact contract needs a durable handoff document.

#### 3. Intent Preflight Duplication (MEDIUM — maintainability)
- **Skills Affected:** `al-dev-commit`, `al-dev-develop`, `al-dev-fix`, `al-dev-lint`, `al-dev-review-develop` (5+ skills)
- **Pattern:** Identical "Apply intent-preflight" logic repeated in each skill
- **Impact:** Maintenance burden; changes to intent-preflight rules require edits to 5+ files
- **Technical accuracy update:** The concern is maintainability, not an immediate runtime blocker. Several of the named skills already cite `knowledge/intent-preflight.md`.
- **Corrected recommendation:** Prefer a shared knowledge/template convention and validator-backed checks. Do not invent a "callable gate" unless a harness-supported runtime mechanism exists.

#### 4. Brittle Knowledge File References (NEEDS TARGETED EVIDENCE — medium)
- **Skills Affected:** 15+ skills (relative paths like `knowledge/intent-preflight.md`)
- **Pattern:** Mixed usage of relative paths (`../../knowledge/...`), absolute paths, and implicit working directory assumptions
- **Impact:** Skills fail silently if knowledge files move/rename
- **Technical accuracy update:** The risk is real, but the original evidence was not specific enough to justify CRITICAL severity. The repo already has many first-class shared knowledge files and validators; the next step should be a targeted reference audit rather than a broad rewrite.
- **Corrected recommendation:** Add a lightweight knowledge-reference validator or extend map-generation validation to flag missing referenced files.

#### 5. Optional File-Size Baseline Path (LOW/MEDIUM contract issue)
- **Skill:** `al-dev-commit` Phase 0.3
- **Issue:** Checks file line count against `.dev/file-sizes.json` but no skill writes this file
- **Impact:** File integrity verification never triggers; unused code path
- **Technical accuracy update:** Valid as a low/medium implementation-contract issue, not a critical runtime blocker. `artifact-contracts.md` currently names `.dev/file-sizes.json` as optional input for `al-dev-commit`, so removing it requires updating that contract too.
- **Corrected recommendation:** Either add the baseline writer or remove the check and update `artifact-contracts.md` in the same change set.

### Original High-Severity Issues (Corrected)

#### 6. Skill Names Hide Complexity or Use Unclear Actions (LOW/MEDIUM hygiene)
- `al-dev-map-suggestions-verify` (22 chars) — Action "verify" is weak; should be "audit" or "review"
- `al-dev-plan-swarm-validate` (24 chars) — Internal agent-team jargon; users don't know what "swarm" means
- `al-dev-consolidate` (17 chars) — Doesn't signal `.dev/` artifact consolidation; users might think code consolidation
- **Technical accuracy update:** Do not prioritize this above runtime/projection failures. `al-dev-map-suggestions-verify` is already documented as a maintainer-tool move candidate elsewhere in the map docs, so renaming may be the wrong fix.
- **Corrected recommendation:** Decide distributed-vs-maintainer placement first; only rename commands when triggers, generated maps, and projections can be updated together.

#### 7. Bloated Skills (MEDIUM maintainability)
- **`al-dev-commit`** — 611 lines; handles commit orchestration, 4+ validation gates, Freshdesk integration, alignment advisory, knowledge quality checking, 5+ agent dispatches
- **`al-dev-develop`** — 464 lines; orchestrates developers, verifies naming/IDs/scope, handles autonomy modes, signature verification, static validation
- **`al-dev-plan`** — 335 lines; delegates Phases 0–1.6 to `/al-dev-plan-preflight`; skill reads 335 lines but only implements Phases 2–7
- **Technical accuracy update:** Current line counts are close to the claim (`al-dev-commit` 610, `al-dev-develop` 463, `al-dev-plan` 334), but length alone is not a failure mode.
- **Corrected recommendation:** Extract only repeated contract text or validated framework concerns; do not split orchestration solely to reduce line count.

#### 8. Descriptions Hide Architectural Complexity (PARTLY STALE — verify before editing)
- `al-dev-develop` — Describes "orchestrates developers" but actually orchestrates + validates naming/IDs/scope/autonomy modes
- `al-dev-fix` — Claims "lightweight" but triggers architect consultation for non-trivial cases
- `al-dev-plan` — Doesn't mention internal `/al-dev-plan-preflight` chaining
- `al-dev-interview` — Doesn't clarify two-phase structure (interview → requirements writing)
- **Technical accuracy update:** Partly stale. `al-dev-plan` does mention preflight chaining in current frontmatter and body. Re-check each named description before updating.
- **Corrected recommendation:** Patch only descriptions that remain misleading after live inspection; do not bulk-edit all four from this list.

### Medium-Severity Issues

#### 9. Inconsistent Phase/Step Nomenclature (MEDIUM)
- **Affected:** 13+ skills use mixed "Phase", "Step", and fractional phases (0.5, 1.6)
- **Pattern:** Some use `Phase 0, 1, 2...` (linear), others use `Step 1, 2, 3...` (procedural), some mix fractional phases
- **Impact:** Cognitive friction switching between skills with different structural naming; resume logic ambiguity
- **Fix:** Standardize: Phase-based skills use `Phase 0, 1, 2...` (linear); single-phase utilities use `Step 1, 2, 3...`; avoid fractional phases except as documented sub-steps

#### 10. Artifact Contract Coverage Gap (MEDIUM)
- **Skills Missing Contracts:** `al-dev-consolidate`, `al-dev-explore`, `al-dev-handoff`, `al-dev-interview`, `al-dev-investigate`, `al-dev-lint`, `al-dev-perf`, `al-dev-release-notes`, `al-dev-support-reply`, `al-dev-ticket`, `al-dev-document`, `al-dev-perf`, and 2 others (14 total)
- **Pattern:** Skills write `.dev/` artifacts but don't reference artifact-contract.md or verify success evidence before completion claim
- **Impact:** Skill completion gates are weak; no standardized verification
- **Technical accuracy update:** Directionally valid, but the inventory is imprecise (`al-dev-perf` is duplicated) and the repo already has `knowledge/artifact-contracts.md` plus `scripts/validate_artifact_contracts.py`. Current validation passes for the 6 skills listed in the matrix.
- **Corrected recommendation:** Extend the existing Contract Matrix and validator coverage intentionally for durable-output skills. Do not add generic contract text to agents or utility skills unless they produce durable handoff artifacts.

#### 11. Intent Preflight Application Gap (MEDIUM)
- **Skills Missing Gates:** 16 skills that edit files or dispatch agents lack explicit Intent Preflight application
- **Pattern:** 7 skills have gates, 16 don't (despite editing/dispatching)
- **Impact:** Users intending review-only or assessment operation may have mutating actions proceed without confirmation
- **Technical accuracy update:** Useful but should be scoped. Some skills are read-only, maintainer-only, or explicitly conversational, and blanket gate insertion can add noise.
- **Corrected recommendation:** Add intent preflight to skills that can mutate repo-tracked files, stage/commit, dispatch mutating agents, or write durable artifacts outside the user's requested output.

#### 12. Multi-Session Resume Capability Gap (MEDIUM)
- **Skills WITH Resume:** 5 of 24 (`al-dev-consolidate`, `al-dev-develop`, `al-dev-map-suggestions-verify`, `al-dev-plan-preflight`, `al-dev-plan`, `plugin-health-audit`)
- **Skills WITHOUT Resume:** 17 that run 10+ minutes without resume support
- **Impact:** Long-running skills cannot be cleanly split across sessions; timeout forces restart from beginning
- **Technical accuracy update:** The count and examples should be re-derived before implementation. Some long workflows already rely on current-run artifacts rather than explicit resume flags.
- **Corrected recommendation:** First classify skills by expected duration and durable outputs, then add resume support only where interruption is realistic and recovery state is well-defined.

#### 13. Phase Numbering in Child Skills (MEDIUM)
- **Skill:** `al-dev-review-develop`
- **Issue:** Uses "Phases 1–6 (semantically mapped from parent al-dev-develop workflow)" — phases are NOT the same
- **Impact:** Readers assume "Phase 2 in review-develop = Phase 2 in develop" (false)
- **Fix:** Use distinct nomenclature (e.g., "Review Phase 1", "Review Phase 2") or explicit mapping table

### Low-Severity Issues

#### 14. Code Block Syntax Inconsistency (LOW)
- Mix of ` ```bash `, ` ```text `, ` ```al `, and ` ~~~al ` fencing
- **Fix:** Standardize on backtick fencing with language specifiers

#### 15. Placeholder Syntax Inconsistency (LOW)
- `[PLACEHOLDER]` vs `<PLACEHOLDER>` vs `${PLACEHOLDER}` vs `$PLACEHOLDER`
- **Fix:** Pick one convention (suggested: `[PLACEHOLDER]` for user-substituted fields)

#### 16. Sub-Phase Numbering Confusion (LOW)
- `al-dev-commit` Phase 0.2.1 (Freshdesk integration) nests under Phase 0.2 (Load Project Context)
- **Fix:** Standardize to linear numbering or clear hierarchical structure

---

## Phase 2: Agent Design Analysis

**23 Agents Analyzed | 26+ Findings**

### Original Critical Issues (Corrected)

#### 1. Testability Architecture Orphan (MEDIUM — guidance depth)
- **Agent:** `al-dev-solution-architect`
- **Issue:** Mandates `TESTABILITY_COMPLETE: yes|no` output (line 69) but provides only fragmentary guidance on design testability architecture; references external knowledge file without concrete examples of interface design, injection points, or mock strategies
- **Impact:** Architects cannot reliably produce testable designs; test engineers cannot validate testability before implementation
- **Technical accuracy update:** The agent does require dependencies, interfaces, and mocks before returning `TESTABILITY_COMPLETE: yes`; this is guidance-depth debt, not a proven critical runtime failure.
- **Corrected recommendation:** Add or reference a focused testability-design knowledge section with examples; avoid bloating the agent body if a shared reference can stay authoritative.

#### 2. Symbol Pre-Flight Enforcement Gap (STALE — already hard-stopped)
- **Agents:** `al-dev-developer-tdd`, `al-dev-developer-traditional`
- **Issue:** Both require `SYMBOL_PREFLIGHT_GATE` completion but enforcement is implicit ("report your pre-flight summary"); no agent has explicit authority to halt implementation if symbols cannot be verified
- **Impact:** Symbol verification is advisory only; developers can proceed with unverified symbols and fail at compile time
- **Technical accuracy update:** Current developer agents already say to stop before implementation if any required symbol is `unverified`, and `knowledge/al-dev-develop-spawn-prompt.md` repeats the same stop rule.
- **Corrected recommendation:** Remove this from critical findings unless a future validator proves the stop wording regressed.

#### 3. Hook-Fixer Recovery Classification Ambiguity (CRITICAL)
- **Agent:** `al-dev-commit-hook-fixer`
- **Issue:** Classifies "Fixable" failures (AL lint, markdownlint) but lacks quantitative thresholds; missing corruption-detection step after fixes (present in lint-fixer but not here)
- **Impact:** A "fixed" hook failure could mask secondary corruption; execute agent won't see issue until commit is finalized
- **Fix:** Add explicit line-count corruption check after every scripted fix in hook-fixer, parallel to lint-fixer's Step 4

#### 4. Tool Declarations Missing/Incorrect (CRITICAL)
- **`al-dev-commit-recover-fixer`** — Tools: `["Write"]` only, but workflow describes git restore, regex reconstruction, schema rebuild (all require Bash)
- **`al-dev-diagnostics-fixer`** — Tools: `["Read", "Edit"]`, but Step 3 runs `al-compile` to verify (requires Bash)
- **`al-dev-support-researcher`** — Tools: `[]` (empty), but instructions reference MCP-based tools (AL Code Intelligence, Microsoft Docs, BC Code History)
- **Impact:** Agents declare insufficient tools; will fail at runtime or have missing capabilities
- **Technical accuracy update:** Valid blocker, but the summary count must be 3 agents, not 2. For `al-dev-support-researcher`, use canonical shared capability names from `knowledge/agent-tool-projection-policy.md` such as `MCP: bc-code-intelligence` and `MCP: microsoft-docs`. BC Code History is not currently documented as a projection-policy capability, so either add a policy mapping or remove/reframe that source. Do not invent harness-native tool names in shared authored source.
- **Corrected recommendation:** Add `Bash` where commands are described; add canonical MCP capabilities for support research; regenerate projections afterward.

### Original High-Severity Issues (Corrected)

#### 5. Lint-Fixer Baseline Capture Path Ambiguity (HIGH)
- **Agent:** `al-dev-commit-lint-fixer`
- **Issue:** Captures baseline line counts to `.git/.commit-baselines` with fallback to `.dev/commit-baselines`; no validation if both are unavailable
- **Impact:** Silent failure of baseline capture → undetected file corruption
- **Fix:** Validate path writability in Step 1; return `LINT_FIX_FAILED` if neither path is usable

#### 6. OOXML-Validator Silent No-Op Risk (HIGH)
- **Agent:** `al-dev-commit-ooxml-validator`
- **Issue:** Returns `OOXML_FAILURES: NONE` if no OOXML files present; dispatcher may not distinguish between "no files" and "validation skipped"
- **Impact:** Corrupted .docx file can slip through in multi-group commits if validator isn't re-invoked per group
- **Upstream:** `al-dev-commit` dispatcher must re-invoke validator per group, not globally
- **Fix:** Document per-group validator invocation requirement in calling skill

#### 7. Interview Completion Signal Ambiguity (STALE — dispatcher gate exists)
- **Agent:** `al-dev-interview`
- **Issue:** Requires explicit `INTERVIEW COMPLETE` signal (lines 59–71) but dispatcher validation is implicit; fallback behavior is advice to dispatcher, not enforced by agent
- **Impact:** Incomplete interviews slipping through if dispatcher doesn't validate signal
- **Technical accuracy update:** Current `al-dev-interview` skill has an explicit gate requiring `INTERVIEW COMPLETE`, fallback resume prompts, and a stop condition if the signal is not received.
- **Corrected recommendation:** Keep this only as a regression-test candidate; do not implement a duplicate fix in the agent without checking whether the skill-level gate is sufficient.

#### 8. Commit-Message-Drafter Emoji Canonicalization Inconsistency (HIGH)
- **Agent:** `al-dev-commit-message-drafter`
- **Issue:** Defines "Canonical gitmoji" (lines 79–94) but examples show emoji placement inconsistently (`feat: ✨` vs `✨ feat(...)`); `CHANGED_COMPONENTS` uses marker names (`[marker]`) but markers are undefined
- **Impact:** Inconsistent commit messages; developers guess format
- **Fix:** Provide complete before/after examples showing exact emoji placement, marker values, and whitespace

#### 9. Commit Workflow Fragmentation (HIGH)
- **Agents:** 7 sequential agents span commit pipeline (analysis → message-drafting → lint-fixer → ooxml-validator → execute → hook-fixer)
- **Issue:** Complex multi-phase workflows with implicit data-flow dependencies; each agent is independent and caller must maintain consistency
- **Impact:** Debugging commit failures requires context-switching across 6+ agents
- **Fix:** Consider consolidating to 3 coordinated agents: analyzer, drafter, executor (with integrated error handling)

#### 10. Developer Agent Duplication (HIGH)
- **Agents:** `al-dev-developer-tdd` and `al-dev-developer-traditional`
- **Issue:** Structurally identical except TDD cycle gates (RED-GREEN-REFACTOR vs BUILD-VERIFY); share identical symbol pre-flight, AL code patterns, error handling, compilation standards (40+ duplicated lines in each)
- **Impact:** Changes to shared standards require edits to 2 agents; duplication maintenance burden
- **Fix:** Choose: inline TDD as conditional mode flag, or define shared base + specialization fork points, or commit to explicit sync plan

### Medium-Severity Issues

#### 11. Three-Reviewer Team Lacks Orchestration Protocol (OVERSTATED)
- **Agents:** `al-dev-expert-reviewer`, `al-dev-performance-reviewer`, `al-dev-security-reviewer`
- **Issue:** Spawned in parallel with no debate mechanism; each independently states "lead agent will synthesize" but no lead agent owns conflict resolution
- **Impact:** Asynchronous reviews can miss cross-cutting issues (e.g., security fix introduces performance regression)
- **Technical accuracy update:** `/al-dev-review-develop` is the lead orchestrator. It dispatches the three reviewers, collects all outputs, and writes a synthesized code-review artifact.
- **Corrected recommendation:** If cross-reviewer debate is desired, add it as an optional enhancement to `/al-dev-review-develop`; do not add a new lead synthesizer agent before proving the current synthesis is insufficient.

#### 12. Solution Architect Symbol Lookup Incomplete (MEDIUM)
- **Agent:** `al-dev-solution-architect`
- **Issue:** Documents 3-tier symbol lookup (AL LSP → AL MCP → text search) but doesn't address: conflicting versions, deprecated symbols, multiple equally-strong analogues
- **Impact:** Architects make inconsistent pattern references across projects
- **Fix:** Add tiebreaker rules (e.g., "prefer most-recent analogue", "prefer internal pattern over base-app")

#### 13. Tool-Misalignment in Multiple Agents (INCORRECT RECOMMENDATION)
- `al-dev-explore` — Declares `"Glob"` tool (not standard Claude tool; should be Bash find/grep)
- `al-dev-interview` — Lists `"USER_GATE"` as tool (actually a governance token, not tool)
- **Impact:** Tool manifests don't match actual capabilities; dispatch coordination breaks
- **Technical accuracy update:** **Incorrect under current architecture.** `Glob` and `USER_GATE` are canonical shared capabilities in `knowledge/agent-tool-projection-policy.md` and project into harness-native equivalents. Removing them would violate the projection model.
- **Corrected recommendation:** Keep canonical shared tools. If additional governance metadata is desired, add it without removing projection-policy tokens.

#### 14. Support-Researcher Tool Availability Undeclared (MEDIUM)
- **Agent:** `al-dev-support-researcher`
- **Issue:** Tools: `[]` (empty); instructions (lines 40–69) repeatedly reference MCP-based tools but doesn't declare them
- **Impact:** Dispatch contract unclear; callers cannot verify tool availability
- **Technical accuracy update:** `MCP: bc-code-intelligence` and `MCP: microsoft-docs` are already canonical shared capabilities. A distinct BC Code History capability is not currently documented in the projection policy.
- **Corrected recommendation:** Add documented canonical MCP tools for the available sources, and either add a projection-policy mapping for BC Code History or remove/reframe that source from the agent.

#### 15. Return Block Formatting Inconsistency (MEDIUM)
- **Affected:** Multiple commit agents (lint-fixer, ooxml-validator, execute, hook-fixer, message-drafter)
- **Pattern:** Some use square-bracket lists, others use multi-line blocks, some use key-value pairs
- **Impact:** Callers must parse each agent's return block differently; easy to miss fields or misinterpret
- **Fix:** Standardize all return blocks to consistent format (YAML or structured key-value pairs)

#### 16. Knowledge File References Are Fragile (MEDIUM)
- **Affected:** 15+ agents reference external knowledge files (e.g., `knowledge/tdd-workflow.md`, `knowledge/solution-plan-template.md`)
- **Issue:** Agents don't verify knowledge files exist or contain expected sections
- **Impact:** Agents fail silently or provide incorrect guidance if references are stale
- **Recommendation:** Periodically audit knowledge file references; consider inlining critical guidance

---

## Phase 3: Cross-Surface Synthesis

**Analysis of Skill-Agent Coupling and Alignment | 8 Major Gaps Identified**

### Coupling Gaps

#### Gap 1: Naming Drift Across Both Surfaces
- **Skill Issues:** `al-dev-plan-swarm-validate`, `al-dev-consolidate`, `commit-recover`
- **Agent Issues:** `al-dev-commit-agent-*` prefix inconsistent
- **Root Cause:** No unified naming convention enforcement across surfaces
- **Impact:** Developer friction; unclear intent of tools
- **Fix:** Treat as hygiene. First decide whether maintainer-only skills should move out of the distributed surface; then document naming rules if remaining names still create real ambiguity.

#### Gap 2: Incomplete Tool/Artifact Contracts
- **Skill Side:** 14 skills missing artifact-contract references
- **Agent Side:** Weak return contracts (e.g., al-dev-solution-architect doesn't specify return block format)
- **Root Cause:** Contract enforcement not systematized
- **Impact:** Completion gates are weak; success evidence unclear
- **Fix:** Extend the existing `knowledge/artifact-contracts.md` matrix and `scripts/validate_artifact_contracts.py` coverage for durable-output skills. Agent return contracts should use a separate return-block convention, not the skill artifact matrix unless they write durable handoff artifacts.

#### Gap 3: Phase/Step Nomenclature Split at Handoff Boundary
- **Skill Side:** Use "Phase N" (some fractional like 0.5)
- **Agent Side:** Use "Step N" (procedural)
- **Issue:** Cognitive load when skills dispatch agents
- **Root Cause:** No unified structure template
- **Impact:** Resume logic ambiguity; harder to trace workflows
- **Fix:** Treat as readability cleanup. Prefer updating existing templates/guidance if present before creating new `knowledge/skill-structure-template.md` or `knowledge/agent-structure-template.md` files.

#### Gap 4: Intent Preflight Duplication vs. Missing Enforcement
- **Skill Side:** Intent preflight duplicated in 5+ skills (advisory only, no hard gates)
- **Agent Side:** Agents implement no intent preflight; assume intent is pre-validated
- **Mismatch:** Skill-level advisory gates don't align with agent-level assumptions
- **Fix:** Consolidate wording through shared knowledge/templates and validator-backed checks. Do not assume a callable preprocessor exists across harnesses.

#### Gap 5: Commit Workflow Fragmentation vs. Recovery Agent Isolation
- **Skill Side:** `al-dev-commit` spans 7 sequential phases
- **Agent Side:** Recovery agents (`hook-fixer`, `commit-recover-fixer`) own domain-specific error cases but have no visibility into prior agent state
- **Issue:** Root-cause diagnosis of hook/recovery failures requires context-switching across 6+ agents
- **Fix:** Consider consolidating recovery logic or documenting full state chain for debugging

#### Gap 6: Model Allocation Doesn't Track Complexity (PARTLY INACCURATE)
- **al-dev-plan** (7 phases, 150+ lines, MEDIUM-COMPLEX task) uses Sonnet agent (al-dev-solution-architect uses Opus)
- **al-dev-commit** (611 lines, 6+ agents, MEDIUM-COMPLEX task) uses Haiku/Sonnet mix
- **Issue:** Model complexity tier doesn't scale with task scope; some haiku agents handle structural tasks that may need more reasoning
- **Technical accuracy update:** Partly inaccurate. `al-dev-solution-architect` defaults to `opus`, and `al-dev-plan-preflight` routes SIMPLE requests to `sonnet` while MEDIUM/COMPLEX defaults to `opus`.
- **Corrected recommendation:** Keep the architect model-routing finding only as a general audit. Focus any model changes on concrete low-quality output evidence, not static line counts.

#### Gap 7: Implicit Skill-Agent Dependencies (PARTLY STALE)
- **al-dev-plan** expects output from **al-dev-interview** but doesn't document as prerequisite
- **al-dev-develop** → **al-dev-review-develop** handoff isn't visible in either skill's text
- **al-dev-fix** → **al-dev-solution-architect** dispatch has no documented context contract
- **Technical accuracy update:** Partly stale. `al-dev-develop` explicitly produces a Phase 4 handoff for `/al-dev-review-develop`, and `artifact-contracts.md` documents that handoff.
- **Corrected recommendation:** Re-check each coupling before editing. Add missing prerequisites/next steps only where the current skill body and artifact contracts do not already specify them.

#### Gap 8: Shared Compilation Concern Undocumented (STALE)
- **Skills:** `al-dev-commit`, `al-dev-develop`, `al-dev-lint` all invoke Bash for compilation
- **Agents:** Developers and reviewers reference "al-compile" fallback to "al compile"
- **Issue:** Compilation is shared concern with multiple implementations
- **Technical accuracy update:** Stale. `knowledge/compile-lint-procedure.md` and `knowledge/compile-output-safeguard.md` already document the shared compile/lint procedure and output handling.
- **Corrected recommendation:** Consolidate references to those existing files or deliberately rename them; do not create a third compile contract without replacing the old ones.

---

## Recommendations Summary

### Critical (Blockers) — Implement Immediately

1. **Capability Declaration Fixes** (3 agents)
   - Add `Bash` to `al-dev-commit-recover-fixer` tools
   - Add `Bash` to `al-dev-diagnostics-fixer` tools
   - Add canonical shared MCP capability declarations to `al-dev-support-researcher`
   - Regenerate agent projections after authored agent changes
   - **Effort:** 1 hour | **Impact:** Prevents runtime failures

2. **Generated Map Regression Check**
   - The current `docs/al-dev-skills-map.md` diff drops relationships such as `/al-dev-document` -> `al-dev-docs-writer`
   - Fix `generate-map-doc-sections.py` / `map_doc_sections.py` detection before accepting refreshed diagrams
   - **Effort:** 2-3 hours | **Impact:** Prevents generated docs from becoming less accurate

### High-Priority — Implement This Week

3. **Artifact Contract Coverage**
   - Extend `knowledge/artifact-contracts.md` for selected durable-output skills
   - Extend `scripts/validate_artifact_contracts.py` tests/coverage as needed
   - Add success-evidence verification gates
   - **Effort:** 6-8 hours | **Impact:** Strengthens completion gates

4. **Valid Coupling Documentation**
   - Add missing prerequisites/next steps only after live verification
   - Prefer updating existing `artifact-contracts.md`, `handoff-chain-map.md`, and invocation-pattern docs over creating parallel docs
   - **Effort:** 4 hours | **Impact:** Debugging complexity reduction

### Medium-Priority — Implement This Sprint

5. **Commit Workflow Rationalization**
   - Document full data-flow chain for 7 commit agents
   - Consider consolidation vs. modularization
   - **Effort:** 6 hours | **Impact:** Debugging complexity reduction

6. **Intent Preflight Consolidation**
   - Extract duplicated intent-preflight from 5 skills
   - Prefer a reusable shared knowledge section or validator-backed template; avoid inventing a non-existent callable runtime gate unless the harness supports it
   - **Effort:** 4 hours | **Impact:** Maintenance burden reduction

7. **Naming Convention Unification**
   - Create or update a naming convention document only after separating maintainer-only tools from distributed plugin skills
   - Apply renames only when downstream trigger names, maps, and projections can be updated in the same change
   - **Effort:** 4 hours | **Impact:** Developer friction reduction, clarity

8. **Knowledge File Audit & Consolidation**
   - Verify all 20+ referenced knowledge files exist
   - Consolidate duplicated guidance where it actually exists; for compilation, start from existing `compile-lint-procedure.md` and `compile-output-safeguard.md`
   - **Effort:** 3 hours | **Impact:** Reference stability

---

## Detailed Findings Tables

> **Accuracy note:** These tables preserve the original report's issue-count
> inventory. Do not treat the severity totals as final after the rubber-duck
> pass; several original CRITICAL/HIGH labels above were downgraded or marked
> stale without recalculating the aggregate table.

### Skills: Issue Inventory by Category

| Category | Count | Critical | High | Medium | Low |
|----------|-------|----------|------|--------|-----|
| Naming/Convention | 6 | 1 | 2 | 3 | — |
| Scope/Bloat | 5 | 2 | 2 | 1 | — |
| Resume/Checkpoint | 4 | 1 | — | 3 | — |
| Artifact Contracts | 3 | 1 | — | 2 | — |
| Phase Nomenclature | 4 | — | 1 | 2 | 1 |
| Knowledge References | 3 | 1 | — | 1 | 1 |
| Code Quality | 5 | — | — | 2 | 3 |
| **Total** | **30** | **6** | **5** | **14** | **5** |

### Agents: Issue Inventory by Category

| Category | Count | Critical | High | Medium | Low |
|----------|-------|----------|------|--------|-----|
| Tool Hygiene | 5 | 3 | 1 | 1 | — |
| Model Fit | 2 | — | — | 1 | 1 |
| Scope Isolation | 4 | 1 | 1 | 2 | — |
| Caller Alignment | 3 | — | 2 | 1 | — |
| Usage Patterns | 4 | — | 2 | 1 | 1 |
| Documentation | 4 | — | 1 | 2 | 1 |
| **Total** | **26** | **4** | **7** | **8** | **3** |

---

## Supporting Data

> **Accuracy note:** Supporting-data counts below are original analysis
> summaries. Re-run the map/stat generation scripts before using them for
> implementation planning, especially model-allocation and single-use-agent
> decisions.

### Skills Health by Phase Count

| Phase Count | Skills | Status |
|-------------|--------|--------|
| 0 | 13 | ⚠️ Flat-structure utilities (no resume) |
| 2–4 | 8 | ✅ Simple, clear gates |
| 5–7 | 3 | ⚠️ High complexity (al-dev-commit 611L, al-dev-develop 464L, al-dev-plan 335L) |

### Agent Usage Distribution

| Category | Count | Impact |
|----------|-------|--------|
| Single-use agents (1 skill) | 13 | Candidates for inlining if simple |
| Shared agents (2+ skills) | 10 | Good reuse; monitor for alignment |
| Undocumented agents | 0 | ✅ All agents documented |
| Over-allocated models | 1 | `al-dev-commit-message-drafter` could be Haiku |

---

## Generated Artifacts

**Date:** 2026-06-02  
**Generated by:** `/analyze-architectural-design` skill  
**Mermaid Diagrams Refreshed:** Claimed yes (via `generate-map-doc-sections.py`), but the current diff requires review before acceptance because it appears to drop real generated edges.

**Updated Documentation:**
- `docs/al-dev-skills-map.md` — dirty in the inspected working tree, but the current diff appears to include generated diagram changes that need review
- `docs/al-dev-agent-map.md` — Claimed by original report, but not dirty in the inspected working tree
- `docs/al-dev-plugin-graph.md` — Claimed by original report, but not dirty in the inspected working tree

**Related Documents:**
- Phase 1 lens findings (5 agents analyzed 24 skills)
- Phase 2 lens findings (5 agents analyzed 23 agents)
- Daily health audit: `docs/health/2026-06-02-tooling-health.md`

---

## Rubber-Duck Correction Summary

**Do not execute the original ranking blindly.** The corrected implementation order is:

1. Fix runtime capability declarations for `al-dev-commit-recover-fixer`, `al-dev-diagnostics-fixer`, and `al-dev-support-researcher`.
2. Repair or revert the generated skills-map refresh if it removes valid edges.
3. Extend artifact-contract coverage through the existing matrix and validator.
4. Patch only verified coupling gaps; remove stale claims about `al-dev-plan` and `al-dev-ticket` hidden chaining.
5. Defer broad naming and phase/step cleanup until executable contracts are stable.

**Second-sweep corrections added:** The original symbol-preflight and
interview-completion findings are stale because current source already contains
hard stop gates. The three-reviewer orchestration finding is overstated because
`/al-dev-review-develop` is the current lead synthesizer. Support research needs
canonical MCP declarations, but BC Code History also needs either a projection
policy mapping or removal from the declared source list.

**Third-sweep corrections added:** Section headings now mark the critical/high
issue lists as original findings with corrections, because the contained
findings no longer all carry their original severity. The support-researcher
recommendation no longer implies BC Code History is already a documented shared
capability.

**Verification commands used during rubber-duck pass:**

```bash
python3 scripts/validate_artifact_contracts.py
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
git status --short
git diff -- docs/al-dev-skills-map.md docs/al-dev-agent-map.md docs/al-dev-plugin-graph.md .claude/skills/analyze-architectural-design/SKILL.md
```
