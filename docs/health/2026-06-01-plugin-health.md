# Plugin Health — 2026-06-01

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 0      | 11      | 1      | **12** |
| Medium   | 10     | 20      | 3      | **33** |
| Low      | 2      | 13      | 0      | **15** |
| **Total** | **12** | **44**  | **4**  | **60** |

**Failed lenses (4):** quality-agent-lens-bloat, design-agent-lens-caller-alignment, quality-agent-lens-name-fit, naming-convention-lens. Call `/plugin-health --resume` to complete.

### Top 5 Ranked Actions

1. **al-dev-commit** | High bloat + clarity issues | Consolidate 11 steps into 5 phases (analysis → drafting → confirmation → preflight → execution); deduplicate confirmation logic.
2. **al-dev-develop** | High bloat + clarity issues | Reduce 9 phases to 5 by moving autonomous-mode routing to Phase 1 decision gate.
3. **plan-map-changes** | High bloat + clarity issues | Extract 1800+ lines of pseudocode to `extract-suggestions.py` and `validate-suggestions.py`; add timeout fallback logic.
4. **al-dev-support** | High naming issue + medium clarity/structure | Remove deprecated alias entirely or consolidate into `/al-dev-ticket` frontmatter only.
5. **Quality clarity issues (11 agents)** | High + medium | Define ambiguous qualifiers: "best existing analogue", "if necessary", "if available", "before implementation", "equal-weight analysis", "match the plan", etc.

---

## Design Suggestions

### Scope Isolation (3 findings)

- **al-dev-commit-lint-fixer** | Low | Trailing whitespace and lint fixes bundled with corruption detection. Consider moving corruption detection to pre-commit validation step in al-dev-commit workflow.

- **al-dev-support-reply-drafter** | Medium | Split into two agents: (1) findings analyzer (extracts/validates findings, assesses customer opinion vs. technical reality) and (2) reply writer (generates customer-facing text).

- **al-dev-commit-recover-verifier** | Medium | Split into two agents: (1) recovery executor (applies fallback strategies, returns recovered state) and (2) recovery reporter (verifies success, writes report).

### Shared Backbone (3 findings)

- **al-dev-developer-tdd** | Medium | Identical spawn pattern across `/al-dev-develop` and `/al-dev-fix`. Document the test-plan conditional routing and unified dispatch template in `knowledge/developer-invocation-patterns.md`.

- **al-dev-developer-traditional** | Medium | Identical spawn pattern across `/al-dev-develop`, `/al-dev-fix`, and `/al-dev-review-develop`. Formalize dispatch template in `knowledge/developer-invocation-patterns.md` with conditional logic (test-plan presence → TDD vs traditional).

- **al-dev-solution-architect** | Medium | Two distinct invocation patterns masked by same agent: (a) competitive debate (Phase 2 of /al-dev-plan: 2-3 parallel agents, full proposal/critique/falsification) and (b) quick analysis (Phase 1 of /al-dev-fix: 1 serial agent, time-bounded, root-cause only). Create separate knowledge files: `architect-competitive-debate-pattern.md` and `architect-quick-analysis-pattern.md`.

### Complexity Outliers (3 findings)

- **al-dev-commit** | High | 10+ numbered steps spanning 5 concern phases (analysis, drafting, confirmation, preflight, execution). Consider extracting message-drafting (steps 7–8) into separate `/al-dev-commit-draft` entry point that produces PROPOSED_GROUPS only. Tradeoff: two calls instead of one; benefit: 40% complexity reduction.

- **al-dev-plan** | Medium | 7 core phases with natural clustering (context gathering + competitive design + synthesis). No split recommended; if complexity remains high, add `--quick` flag to bypass Phases 1.5–1.6 (external verification) for simpler requests.

- **plan-with-critic-swarm** | Medium | Zero-agent, 6-step skill functionally a variant of `/al-dev-plan` with added parallel critic review. Consider absorbing as `/al-dev-plan --with-swarm` option (Phase 4 dispatches 6 parallel critics instead of facilitating debate). Benefit: unified planning entry point; tradeoff: al-dev-plan grows to 8 effective phases.

### Handoff Gaps (2 findings)

- **commit → release/deploy workflow** | Medium | Well-established chain `plan → develop → review-develop → commit` has obvious next step for release management. `al-dev-release-notes` exists but is not dispatched from `al-dev-commit`. Add release dispatch step in `al-dev-commit` Phase 11 (after commit completion) that auto-detects commit range and optionally spawns release-notes writer.

- **`.dev/commit-integrity.log` source orphaned** | Low | File read by `commit-recover` but no skill writes it. Appears to be external git hook output. Document as hook-generated artifact in `knowledge/artifact-contracts.md`, or integrate pre-commit validation phase into `al-dev-commit` workflow to make chain self-contained.

### Near-Duplicates (1 finding)

- **al-dev-plan + plan-with-critic-swarm** | Medium | Both spawn 2-3 solution architect agents and run multi-phase competitive design debates. Phase counts: 7 vs 6 (within threshold). Critic layer could be expressed as `--with-swarm` flag on `al-dev-plan` instead of separate skill, unifying design workflows and reducing cognitive load for users choosing between nearly-identical entry points.

---

## Quality Findings

### Clarity Issues (High Severity: 11)

- **al-dev-solution-architect** | High | Ambiguous interpretation of "pattern references" research task — "best existing analogue" is undefined operationally. Define explicitly: "the code that performs the same business function or uses the same event/table extension pattern, even if variable/field names differ."

- **al-dev-commit-agent-execute** | High | Incomplete conditional: "If commit fails" branch stated, but success path is implicit. Add explicit: "If commit succeeds on first attempt, record SHA and move to next group."

- **plan-map-changes-duck-worker** | High | Incomplete decision tree in type-specific checks. Add explicit branches: "If zero references → ACCEPT. If references only in markdown → ACCEPT. If in active code → REJECT. If mixed → inspect and REJECT if active use found."

- **al-dev-commit** | High | Double-negative instruction contradicts preceding steps; condition "before success evidence read" is underspecified. Rephrase: "After completing Step X, read the success evidence file. Only claim staged set is ready after confirming this file exists and contains required verification data."

- **al-dev-develop** | High | Incomplete conditional: if required procedure is NOT VERIFIED, action is undefined. Add missing branch: "If any required external procedure is NOT VERIFIED, stop and report to user. Wait for confirmation to proceed or retry verification."

- **al-dev-fix** | High | Ambiguous reference to another skill ("same as /al-dev-develop") without explaining the check inline. Include the inline check: "`TEST_PLAN=$(ls .dev/*-al-dev-test-test-plan.md 2>/dev/null | sort | tail -1)`. If found, spawn tdd; otherwise spawn traditional."

- **al-dev-interview** | High | Incomplete conditional: "INTERVIEW COMPLETE" gate defined, but missing fallback if agent does NOT state this. Add: "If agent does not report INTERVIEW COMPLETE or is missing categories, ask agent to resume and cover missing categories. Re-confirm INTERVIEW COMPLETE before proceeding."

- **al-dev-plan** | High | Incomplete conditional: "Once a description is given, resume from step 1" implies one retry only. Add termination rule: "If revised description still too vague, repeat clarification up to 2 times total, then escalate with required information: '(1) business goal, (2) key workflows, (3) affected BC objects.'"

- **al-dev-review-develop** | High | Orphaned sentence fragment duplicating al-dev-develop routing logic ("If no test plan exists, spawn al-dev-developer-traditional"). Remove this fragment; it creates maintainability risk. If review-develop has independent routing logic, define it explicitly.

- **al-dev-ticket** | High | Incomplete conditional: "If yes, dispatch al-dev-ticket-agent (download phase)" but no "if no" branch for user decline. Add: "If no, proceed directly to Step 5 without downloading. Note: Steps 6-7 may be incomplete without attachments if they contain critical context."

- **plan-map-changes** | High | Incomplete conditional: no fallback for inline verification timeout or dispatch failure. Add: "If verification stalls (>5 min per suggestion), escalate to user with: 'Verification stalled on [suggestion]. Retry inline, skip, or abort?' and wait for choice."

### Clarity Issues (Medium Severity: 8 agents + 14 skills)

Agents: al-dev-developer-traditional, al-dev-developer-tdd, al-dev-interview, al-dev-release-notes-writer, al-dev-commit-message-drafter, al-dev-diagnostics-fixer, al-dev-support-reply-drafter

Skills: al-dev-consolidate, al-dev-develop, al-dev-diagram-generator, al-dev-document, al-dev-handoff, al-dev-help, al-dev-investigate, al-dev-lint, al-dev-perf, al-dev-support, commit-recover, plan-map-changes, plan-with-critic-swarm, plugin-health

[See findings file for details — all involve vague qualifiers like "if necessary", "if available", undefined terms like "equal-weight analysis", or incomplete procedures.]

### Clarity Issues (Low Severity: 6 skills)

Skills: al-dev-diagram-generator, al-dev-help, al-dev-release-notes, al-dev-support, verify-commits, plan-map-changes

[Low-priority pseudo-code issues and minor vague qualifiers.]

### Bloat Issues (High Severity: 3 skills)

- **al-dev-commit** | High | 11 steps exceed 8-step threshold; Step 9 contains 3 repetitive confirmation blocks. Consolidate Steps 7, 7a, 8 into single "Verification & Dispatch" phase; deduplicate confirmation logic.

- **al-dev-develop** | High | 9 phases exceed 8 threshold; Phases 1.5 and 4.5 are autonomous-mode branches that duplicate non-autonomous logic. Move autonomous routing to Phase 1 as single decision gate; conditionally execute branches without separate phase numbers.

- **plan-map-changes** | High | 1800+ lines of pseudocode in Step 2B. Extract to `plan-map-changes/extract-suggestions.py` and `plan-map-changes/validate-suggestions.py`; skill body references scripts with invocation patterns only.

### Bloat Issues (Medium Severity: 3 skills)

- **al-dev-fix** | Medium | Step 3 (non-trivial fix) spans 160+ lines with duplicate compile/lint patterns. Consolidate patterns into single referenced section; reduce Step 3 to 50 lines by referencing procedure document only.

- **al-dev-ticket** | Medium | 8 phases can be consolidated: Phases 2–4 (context gathering) into single "Load & Validate" phase; Phases 6–7 (research + reply) with conditional execution inside a single Phase 3.

- **al-dev-plan** | Medium | Phase 2 architect dispatch repeats identical context blocks three times without abstraction. Create shared "Architect Prompt Template" in knowledge/ or reusable block in skill; consolidate decision gates.

### Description Drift Issues (Medium Severity: 6 skills + 3 agents)

Agents: al-dev-code-review, al-dev-commit-recover-verifier, al-dev-ticket-agent

Skills: al-dev-consolidate, al-dev-document, al-dev-plan, al-dev-review-develop, al-dev-support, commit-recover

[All involve missing or conflicting details: RTM omission, model routing not documented, compile verification gate not documented, missing feature descriptions, or stale deprecation notices.]

### Structure Issues (Multiple agents + skills)

- Multiple agents | Low | Missing bash language tags on 7 code blocks; missing python tags on plan-map-changes pseudocode (1800+ lines).

- Multiple skills | Low | Missing bash/python language tags on 18+ code blocks.

- al-dev-commit-message-drafter | Medium | Tools field contains empty array `[]` without documented reason why tool-less operation is correct.

- Multiple agents | Medium | Inconsistent use of explicit `name:` field in frontmatter.

- al-dev-develop | Low | Inconsistent phase numbering (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.0, 4, 4.5).

- al-dev-diagram-generator | Low | Phase headings mix "Phase N" and "Sub-step" labeling.

- al-dev-document | Medium | Missing or truncated frontmatter `description`; references template files at `knowledge/doc-templates/[AUDIENCE].md` without documenting in argument-hint.

- al-dev-interview | Medium | Body references optional interview categories (11 total) but `argument-hint` does not document category filtering or scope control.

- al-dev-release-notes | Low | Output file naming uses variable placeholder `[short-hash]` inconsistent with `.dev/YYYY-MM-DD-<skill>-*.md` convention.

- al-dev-support | Medium | Deprecated skill with outdated `argument-hint` documenting replaced behavior; should be removed or consolidated into `/al-dev-ticket` frontmatter only.

- plan-with-critic-swarm | Medium | Body content is minimal (stub/outline); missing full Phase 1–6 steps matching description.

---

## Naming Violations

- **al-dev-consolidate** | Medium | Name implies "merging/combining" but skill actually "archives and summarizes workflow artifacts". Scope narrower than name suggests. Consider rename to `al-dev-archive-sessions`.

- **al-dev-diagram-generator** | Medium | Name implies general diagram generation but skill only generates workflow relationship diagrams. Very narrow scope. Consider rename to `al-dev-diagram-workflow`.

- **plan-map-changes** | Medium | Verb "plan" implies design/architecture but skill actually "verifies and collects architectural suggestions from existing maps". Primary action is verification/orchestration, not planning. Consider rename to `verify-map-suggestions`.

- **al-dev-support** | High | Deprecated alias still listed as active skill; actively misleads users into thinking it is standalone operation. Name conflict and deprecation ambiguity. **Recommend: remove entirely or archive.**

---

## Graph Deltas

Running dependency graph refresh...

