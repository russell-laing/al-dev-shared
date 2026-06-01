# Superpowers Planning History

Current source of truth: active implementation guidance lives in the current shared plugin source and knowledge documents.

## 2026-06-01

### Agent Model Changes Implementation Plan

- Path: `docs/superpowers/plans/2026-06-01-agent-model-changes.md`
- Kind: plan
- Status: implemented
- Summary: Update three agent model assignments and fix one outputs documentation mismatch based on model-fit analysis.

## 2026-05-31

### Sync Documentation Maps with Agent Teams — Design Spec

- Path: `docs/superpowers/specs/2026-05-31-sync-documentation-maps-agent-teams-design.md`
- Kind: spec
- Status: historical
- Summary: `/sync-documentation-maps` orchestrates two expensive operations (`/review-skill-map` and `/review-agent-map`) in sequence. Each review operation reads 60+ files, performs complex comparisons, and updates documentation maps. On a large plugin surface, this consumes 1–2 hours of session tokens and blocks other work.

### Plugin-Health Agent Teams Parallelization — Design Spec

- Path: `docs/superpowers/specs/2026-05-31-plugin-health-agent-teams-design.md`
- Kind: spec
- Status: historical
- Summary: `/plugin-health` consumes 5+ hours of session tokens daily, making it impossible to do substantive work in the same session. The skill dispatches 15+ design and quality lenses sequentially in batched waves, burning tokens linearly.

### Plan Map Changes with Agent Teams — Design Spec

- Path: `docs/superpowers/specs/2026-05-31-plan-map-changes-agent-teams-design.md`
- Kind: spec
- Status: historical
- Summary: `/plan-map-changes` rubber-ducks architectural suggestions from map Observations sections, then writes an implementation plan. For 5–10 suggestions, rubber-ducking is expensive: each suggestion requires reading affected files, grepping for callers, verifying claims. On a large plugin surface, rubber-ducking alone consumes 30–60 minutes, followed by another 30 minutes for plan writing. Total: 1–1.5 hours per planning session.

### Modern CLI Tooling Adoption for `al-dev-shared` - Design Spec

- Path: `docs/superpowers/specs/2026-05-31-modern-cli-tooling-adoption-design.md`
- Kind: spec
- Status: historical
- Summary: The repo already relies on shell-driven validation, search, and JSON editing, but its guidance is uneven. Some workflows already prefer `rg`, some use ad hoc `grep`/`sed`, and JSON updates are still described inconsistently. The shared plugin surface also does not clearly distinguish between "preferred local CLI tool" and "harness-native capability."

### Tooling & Plugin Surface Improvements Plan

- Path: `docs/superpowers/plans/2026-05-31-tooling-friction-reduction.md`
- Kind: plan
- Status: implemented
- Summary: Reduce friction on subagent execution, pre-commit verification, and parallel job resilience by adding compile gates, permission pre-flights, and checkpointed parallel sweeps.

### Sync Documentation Maps — Async Agent Teams Implementation Plan

- Path: `docs/superpowers/plans/2026-05-31-sync-documentation-maps-agent-teams.md`
- Kind: plan
- Status: implemented
- Summary: Refactor `/sync-documentation-maps` so audit and update operations run asynchronously via remote agent teams, freeing the lead session after dispatch rather than blocking it for 1–2 hours.

### Plugin-Health Agent Teams Implementation Plan

- Path: `docs/superpowers/plans/2026-05-31-plugin-health-agent-teams-implementation.md`
- Kind: plan
- Status: implemented
- Summary: Transform `/plugin-health` from a single 5+-hour session job to a parallelized dispatch-and-resume workflow with 80-90% token savings, keeping durable state under `.dev/` and freeing the user after ~45 minutes.

### Plugin Health Top 5 Implementation Plan

- Path: `docs/superpowers/plans/2026-05-31-plugin-health-top-5.md`
- Kind: plan
- Status: implemented
- Summary: Implement the five highest-impact findings from the 2026-05-31 plugin health sweep to improve agent design, skill structure, and code quality.

### Plan Map Changes with Agent Teams Implementation Plan

- Path: `docs/superpowers/plans/2026-05-31-plan-map-changes-agent-teams-design.md`
- Kind: plan
- Status: implemented
- Summary: Implement `/plan-map-changes` skill that dispatches rubber-ducking to remote agent teams, parallelize verification, and reduce session token burn from 1-1.5 hours to 40-50 minutes.

### Modern CLI Tooling Adoption Implementation Plan

- Path: `docs/superpowers/plans/2026-05-31-modern-cli-tooling-adoption.md`
- Kind: plan
- Status: unknown
- Summary: Standardize `rg` for text search and `jq` for JSON work across repo-facing tooling guidance and shared plugin guidance, while keeping the projection layer harness-neutral.

### AL Dev Map Accuracy Refresh Implementation Plan

- Path: `docs/superpowers/plans/2026-05-31-al-dev-map-accuracy-refresh.md`
- Kind: plan
- Status: implemented
- Summary: Bring `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md`, and `docs/al-dev-plugin-graph.md` back into technical alignment with the current `profile-al-dev-shared` source after today's agent and skill changes.

## 2026-05-30

### Harness-Neutrality Enforcement — Design

- Path: `docs/superpowers/specs/2026-05-30-harness-neutrality-enforcement-design.md`
- Kind: spec
- Status: ready
- Summary: **Date:** 2026-05-30 **Origin:** Rubber-duck of `docs/health/2026-05-29-plugin-health.md` (`~/.claude/plans/rubber-duck-docs-health-2026-05-29-plugi-delightful-comet.md`) **Status:** Approved design — ready for implementation plan

### Tooling Health Top-5 Wave 2 Implementation Plan

- Path: `docs/superpowers/plans/2026-05-30-tooling-health-top-5-wave-2.md`
- Kind: plan
- Status: implemented
- Summary: Implement 4 remaining high-severity actions from `docs/health/2026-05-30-tooling-health.md` (Item 2 — model field for all 21 lens agents — was verified complete before this plan was written: all agents already have `model: haiku`).

### Tooling Health Top-5 Actions Implementation Plan

- Path: `docs/superpowers/plans/2026-05-30-tooling-health-top-5.md`
- Kind: plan
- Status: implemented
- Summary: Fix the five highest-priority findings from the 2026-05-30 tooling health dossier — two targeted text fixes, one dispatch-template restructure across three skills, one suggestion-drafter extraction, and one plugin-health split.

### Plugin Map Connect /al-dev-fix Cleanup Implementation Plan

- Path: `docs/superpowers/plans/2026-05-30-plugin-map-connect-fix-cleanup.md`
- Kind: plan
- Status: superseded
- Summary: Mark the open "Connect: Clarify `/al-dev-fix` escalation boundaries" suggestion in `docs/al-dev-skills-map.md` as confirmed implemented, consistent with the Extension opportunities #2 entry already present in the same file.

### Plugin Health Top 5 — 2026-05-30 Implementation Plan

- Path: `docs/superpowers/plans/2026-05-30-plugin-health-top-5.md`
- Kind: plan
- Status: implemented
- Summary: Address the five highest-ranked findings from the 2026-05-30 plugin health sweep: model fit corrections for five agents, three High-severity clarity gaps in al-dev-solution-architect, targeted clarity fixes in al-dev-develop and al-dev-developer, phase-label clarity in al-dev-review-develop, and splitting al-dev-commit-preflight into two single-concern agents.

### Harness-Neutrality Enforcement Implementation Plan

- Path: `docs/superpowers/plans/2026-05-30-harness-neutrality-enforcement.md`
- Kind: plan
- Status: abandoned
- Summary: This abandoned plan proposed preventing maintainer lens sweeps from recommending harness-specific tokens, finishing the documented haiku downgrade, and backing harness-neutrality with a single canonical reference, hardened validators, and a checked-in pre-commit gate.

## 2026-05-29

### Self-Healing Maintainer Tooling — Design

- Path: `docs/superpowers/specs/2026-05-29-plugin-self-healing-tooling-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-29 **Status:** Approved (brainstorming complete; pending implementation plan)

### Design: Harness Engineering Demo — Three Maintainer Improvements (Wave 2)

- Path: `docs/superpowers/specs/2026-05-29-harness-demo-wave-2-design.md`
- Kind: spec
- Status: unknown
- Summary: Adapt three remaining patterns from `coleam00/harness-engineering-demo` to strengthen `profile-al-dev-shared` solution plan quality and maintainer feedback loops

### Tooling Health Top-5 Actions — Implementation Plan

- Path: `docs/superpowers/plans/2026-05-29-tooling-health-top-5.md`
- Kind: plan
- Status: historical
- Summary: Address the 4 actionable items from the 2026-05-29 tooling health sweep (the 2 Merge suggestions were rubber-ducked and skipped — the pairs have orthogonal structures and incompatible logic).

### Skill Quality High-Priority Fixes Implementation Plan

- Path: `docs/superpowers/plans/2026-05-29-skill-quality-high-priority-fixes.md`
- Kind: plan
- Status: implemented
- Summary: Fix all 16 High-severity findings from `docs/al-dev-skill-quality.md` across 9 skill files.

### Self-Healing Maintainer Tooling Implementation Plan

- Path: `docs/superpowers/plans/2026-05-29-plugin-self-healing-tooling-implementation.md`
- Kind: plan
- Status: implemented
- Summary: Modernize and consolidate the `al-dev-shared` maintainer tooling into a documented naming convention, symmetric lens agents, and a standing suggestions-only self-healing loop (`/plugin-health`) backed by a deterministic dependency-graph generator.

### Plugin and Agent Map Fixes Implementation Plan

- Path: `docs/superpowers/plans/2026-05-29-plugin-agent-map-fixes.md`
- Kind: plan
- Status: implemented
- Summary: Apply 7 open suggestions from the Observations sections of `docs/al-dev-plugin-map.md` and `docs/al-dev-agent-map.md` — 3 documentation-only Align fixes, 1 Connect routing clarity prose update, 1 Remodel for complexity-gated architect dispatch, 1 Split to extract a preflight agent from the execute agent, and 1 implementation of the stub al-dev-review-develop skill.

### Plugin Map Stale Observations Cleanup

- Path: `docs/superpowers/plans/2026-05-29-plugin-map-stale-observations-cleanup.md`
- Kind: plan
- Status: implemented
- Summary: Mark all 6 stale "Quality suggestions" in `docs/al-dev-agent-map.md` and 1 stale "Extension opportunities" entry in `docs/al-dev-plugin-map.md` as already-implemented — rubber-duck verification on 2026-05-29 confirmed every open suggestion is already live in the codebase.

### Plugin Health Fixes — Top 5 Actions Implementation Plan

- Path: `docs/superpowers/plans/2026-05-29-plugin-health-top-5.md`
- Kind: plan
- Status: implemented
- Summary: Address the top 5 harness-agnostic findings from the 2026-05-29 plugin health sweep: agent model downgrades, reviewer template consolidation, tool/frontmatter canonicality, operational clarity gaps, and stale documentation maps.

### Plan: Top 5 Plugin & Tooling Health Actions — 2026-05-29

- Path: `docs/superpowers/plans/2026-05-29-top-5-map-actions.md`
- Kind: plan
- Status: historical
- Summary: Five high-impact improvements identified in health sweeps (2026-05-29): 1. **Remodel 5 agents** → Upgrade code reviewers (haiku → sonnet) for multi-file analytical reasoning

### Harness Demo Wave 2: Three Maintainer Improvements — Implementation Plan

- Path: `docs/superpowers/plans/2026-05-29-harness-demo-wave-2-implementation.md`
- Kind: plan
- Status: implemented
- Summary: Add per-task `Gotcha:` and `Validate:` fields to the solution plan template, create PostToolUse auto-validation hook, and create Stop hook to block on stale projections.

## 2026-05-28

### Design: al-dev-consolidate skill

- Path: `docs/superpowers/specs/2026-05-28-al-dev-consolidate-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-28 **Status:** Approved

### Design: Two Durable Improvements from Harness Engineering Demo

- Path: `docs/superpowers/specs/2026-05-28-harness-demo-three-improvements-design.md`
- Kind: spec
- Status: historical
- Summary: Adapt the strongest reusable planning patterns from `coleam00/harness-engineering-demo`

### Design: Targeted Hybrid Improvements for `profile-al-dev-shared`

- Path: `docs/superpowers/specs/2026-05-28-profile-al-dev-shared-hybrid-improvements.md`
- Kind: spec
- Status: implemented
- Summary: Address three recurring friction patterns from the Claude Code usage review without duplicating guidance that already exists in the shared profile

### Design: Shared Artifact Contracts and Final Gates for `profile-al-dev-shared`

- Path: `docs/superpowers/specs/2026-05-28-shared-artifact-contracts-and-gates-design.md`
- Kind: spec
- Status: abandoned
- Summary: Lift the most portable, high-value ideas from `coleam00/harness-engineering-demo` into the shared plugin surface without introducing harness-specific runtime wiring

### Design: Harness Coverage Model for `profile-al-dev-shared`

- Path: `docs/superpowers/specs/2026-05-28-harness-coverage-model-design.md`
- Kind: spec
- Status: implemented
- Summary: Convert useful harness-engineering ideas into a bounded, repo-specific design for improving the harness-agnostic `profile-al-dev-shared` plugin

### Design: Artifact-Contract Conformance Validator and Skill Scaffold Template

- Path: `docs/superpowers/specs/2026-05-28-artifact-contract-validator-and-skill-template-design.md`
- Kind: spec
- Status: abandoned
- Summary: Lock in the artifact-contract structure that landed earlier today by adding a structural sensor (validator) and lowering the cost of future compliance (template)

### Design (Parked): Validator Self-Correction Message Audit

- Path: `docs/superpowers/specs/2026-05-28-validator-self-correction-messages-design.md`
- Kind: spec
- Status: deferred
- Summary: Audit existing repo-local validators so their failure output instructs self-correction rather than only reporting violations

### Audit Skill Fix Cap Design

- Path: `docs/superpowers/specs/2026-05-28-audit-skill-fix-cap-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-28 **Status:** Approved

### AL Dev Lint Review-Only Regression Design

- Path: `docs/superpowers/specs/2026-05-28-al-dev-lint-review-only-regression-design.md`
- Kind: spec
- Status: unknown
- Summary: Add one focused regression check that keeps `/al-dev-lint` from silently mutating files when the user only asked to inspect diagnostics or summarize compile failures.

### al-dev-consolidate Implementation Plan

- Path: `docs/superpowers/plans/2026-05-28-al-dev-consolidate.md`
- Kind: plan
- Status: implemented
- Summary: Create the `al-dev-consolidate` skill that consolidates `.dev/` workflow artifacts into per-session vault-ready summary notes and a sessions index.

### Validator Self-Correction Messages

- Path: `docs/superpowers/plans/2026-05-28-validator-self-correction-messages.md`
- Kind: plan
- Status: implemented
- Summary: Standardise the failure output of the three existing repo-local validators so every message names the file, the rule-id, the violation, and a single concrete fix — matching the canonical shape already used by `validate_artifact_contracts.py`.

### Shared Artifact Contracts and Final Gates Implementation Plan

- Path: `docs/superpowers/plans/2026-05-28-shared-artifact-contracts-and-gates.md`
- Kind: plan
- Status: ready
- Summary: Add one shared artifact-contract reference, tighten final completion claims across the listed shared skills, and publish one compact example artifact bundle that matches the new contract.

### Profile-al-dev-shared Hybrid Improvements Implementation Plan

- Path: `docs/superpowers/plans/2026-05-28-profile-al-dev-shared-hybrid-improvements.md`
- Kind: plan
- Status: abandoned
- Summary: Strengthen three existing friction points in the shared profile by enforcing compile discipline before commits, tightening investigation guidance, and completing the intent-preflight model across all entry skills.

### Harness Demo Three-Improvements: Planning Enhancements Implementation Plan

- Path: `docs/superpowers/plans/2026-05-28-harness-demo-three-improvements.md`
- Kind: plan
- Status: implemented
- Summary: Adopt two durable planning improvements from `coleam00/harness-engineering-demo`: pattern references in solution plans and constrained acceptance criteria format.

### Harness Coverage Model Implementation Plan

- Path: `docs/superpowers/plans/2026-05-28-harness-coverage-model.md`
- Kind: plan
- Status: implemented
- Summary: Add a maintainer-facing harness coverage model that maps shared-profile behaviors to guides, sensors, enforcement strength, ownership, and gaps.

### Audit Skill Fix Cap Implementation Plan

- Path: `docs/superpowers/plans/2026-05-28-audit-skill-fix-cap.md`
- Kind: plan
- Status: unknown
- Summary: Add a hard 5% per-file content reduction cap to the fix-application step in both audit skills (`/audit-agent-quality` and `/audit-skill-quality`).

### Artifact-Contract Conformance Validator and Skill Scaffold Template

- Path: `docs/superpowers/plans/2026-05-28-artifact-contract-validator-and-skill-template.md`
- Kind: plan
- Status: ready
- Summary: Add a structural sensor (`validate_artifact_contracts.py`) that enforces the artifact-contract matrix, and a scaffold template for new skills that bakes in the contract structure by default.

### AL Dev Lint Review-Only Regression Implementation Plan

- Path: `docs/superpowers/plans/2026-05-28-al-dev-lint-review-only-regression.md`
- Kind: plan
- Status: unknown
- Summary: Add one regression scenario that prevents `/al-dev-lint` from silently mutating files when the user only asked to inspect compile failures or diagnostics.

## 2026-05-27

### AL LSP Guidance Design

- Path: `docs/superpowers/specs/2026-05-27-al-lsp-guidance-design.md`
- Kind: spec
- Status: implemented
- Summary: Update `profile-al-dev-shared` guidance so AL Language Server Protocol support is recognized as a preferred semantic navigation provider when it is exposed by the active harness or adapter.

### Plugin Map Recommendation Triage Implementation Plan

- Path: `docs/superpowers/plans/2026-05-27-plugin-map-recommendation-triage.md`
- Kind: plan
- Status: implemented
- Summary: Reconcile `docs/al-dev-plugin-map.md` with the current repo state, keep only recommendations that still survive the suggestion-of-merit gate, and align related `/al-dev-fix` routing guidance.

### AL LSP Guidance Implementation Plan

- Path: `docs/superpowers/plans/2026-05-27-al-lsp-guidance.md`
- Kind: plan
- Status: implemented
- Summary: Update shared `profile-al-dev-shared` guidance so AL LSP is described as an optional preferred semantic navigation provider while preserving AL MCP and text-search fallbacks.

### AL Dev Plugin Map Changes Implementation Plan

- Path: `docs/superpowers/plans/2026-05-27-al-dev-plugin-map-changes.md`
- Kind: plan
- Status: implemented
- Summary: Implement 8 verified architectural improvements to the al-dev plugin identified in the 2026-05-27 map analysis: restore critical agent file, trim unused agent tools, clarify alignment contracts, optimize agent model assignments, improve feedback loops, and refactor a high-complexity skill into two focused ones.

## 2026-05-26

### Plugin Improvement Review Design

- Path: `docs/superpowers/specs/2026-05-26-plugin-improvement-review-design.md`
- Kind: spec
- Status: abandoned
- Summary: This abandoned design explored using harness usage reports as evidence for improving `profile-al-dev-shared` without letting report-specific recommendations leak directly into the distributed plugin. It framed candidate suggestions as requiring review before becoming shared-profile changes.

### Plugin Improvement Review Implementation Plan

- Path: `docs/superpowers/plans/2026-05-26-plugin-improvement-review.md`
- Kind: plan
- Status: implemented
- Summary: Add a bounded, evidence-based workflow for turning harness usage reports into reviewable shared-plugin improvement candidates without letting report-specific recommendations leak directly into `profile-al-dev-shared`.

## 2026-05-25

### Al-Dev-Develop Session Resilience Improvements Implementation Plan

- Path: `docs/superpowers/plans/2026-05-25-al-dev-develop-session-resilience-improvements.md`
- Kind: plan
- Status: abandoned
- Summary: Make `/al-dev-develop` resume cleanly after context loss, keep review scope and git state explicit, and prevent compile-log context bloat.

## 2026-05-24

### Design: `/projection-sync` Skill

- Path: `docs/superpowers/specs/2026-05-24-projection-sync-skill-design.md`
- Kind: spec
- Status: ready
- Summary: **Date:** 2026-05-24 **Status:** Revised for implementation planning **Author:** Claude Code Brainstorming

### Design: Projection Layer README Restructure

- Path: `docs/superpowers/specs/2026-05-24-projection-layer-readme-restructure-design.md`
- Kind: spec
- Status: unknown
- Summary: Improve document structure and flow to be task-driven and maintainer-focused

### Projection Sync Skill Implementation Plan

- Path: `docs/superpowers/plans/2026-05-24-projection-sync-skill-design.md`
- Kind: plan
- Status: implemented
- Summary: Create a `/projection-sync` maintainer skill that validates shared agent source, regenerates harness-native projections, summarizes changes, and prompts for commit approval.

### Projection Layer README Restructure Implementation Plan

- Path: `docs/superpowers/plans/2026-05-24-projection-layer-readme-restructure.md`
- Kind: plan
- Status: implemented
- Summary: Restructure `docs/projection-layer-readme.md` from architecture-centric to task-driven, maintainer-focused narrative with clear boundary rules and workflows.

### Fix Compile Output Handling Implementation Plan

- Path: `docs/superpowers/plans/2026-05-24-fix-compile-output-handling.md`
- Kind: plan
- Status: implemented
- Summary: Eliminate piping of `al-compile` output to terminal viewers, preventing 4.7MB+ context bloat and forced session compacts.

## 2026-05-23

### Next Phase Spec: Projection Rollout Boundary for `.claude`

- Path: `docs/superpowers/specs/2026-05-23-projection-rollout-claude-boundary-design.md`
- Kind: spec
- Status: unknown
- Summary: This spec framed projection-layer rollout as a shared-plugin integration boundary rather than a broader maintainer-tooling migration. It identified `profile-al-dev-shared/` as the canonical shared plugin surface and valid projection input, while treating `.claude/` as repo-local Claude Code maintainer tooling outside projection, distribution, and downstream harness consumption.

### Shared Profile Harness-Agnostic Remediation Implementation Plan

- Path: `docs/superpowers/plans/2026-05-23-shared-profile-harness-agnostic-remediation.md`
- Kind: plan
- Status: implemented
- Summary: Make the authored `profile-al-dev-shared` surface genuinely harness agnostic for Claude Code, Codex, and Copilot CLI while preserving explicit harness-mapping and generated projection artifacts where they belong.

### Harness-Agnostic Documentation Update Implementation Plan

- Path: `docs/superpowers/plans/2026-05-23-harness-agnostic-documentation-update.md`
- Kind: plan
- Status: implemented
- Summary: Update CLAUDE.md and related documentation to accurately reflect that `al-dev-shared` is a multi-harness plugin consumed by Claude Code, Copilot CLI, and Codex, with equal projection support across all three.

### AI Usage Report Skill Implementation Plan

- Path: `docs/superpowers/plans/2026-05-23-ai-usage-report-skill.md`
- Kind: plan
- Status: implemented
- Summary: Create a repository-local Codex skill that converts harness-specific usage artifacts into an AI-harness-neutral markdown report, with optional Codex-derived observations when local Codex session data is available.

## 2026-05-22

### Design: Harness-Specific Agent Tool Declarations

- Path: `docs/superpowers/specs/2026-05-22-multi-environment-tool-declarations-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-22 **Audience:** Agent authors in `al-dev-shared` **Status:** Revised after claim verification

### Validator False Positive Elimination Plan

- Path: `docs/superpowers/plans/2026-05-22-validator-false-positive-fixes.md`
- Kind: plan
- Status: unknown
- Summary: Reduce validator false positives from 32 of 40 flags (~80%) to near-zero by fixing path resolution, emoji parsing, and intentional-brevity detection.

### Review Findings Implementation Plan

- Path: `docs/superpowers/plans/2026-05-22-implement-review-findings.md`
- Kind: plan
- Status: historical
- Summary: Address 5 identified issues in al-dev-support agents and al-dev-review skill: fix customer opinion uncritical acceptance, project hash mismatch, inline image detection, retraction language in drafts, and bug reference evidence.

### Plugin & Agent Map Implementation Plan

- Path: `docs/superpowers/plans/2026-05-22-plugin-map-implementation.md`
- Kind: plan
- Status: implemented
- Summary: Implement 7 architectural improvements from plugin and agent map analysis: merge ticket skills, split commit analyzer, document patterns, upgrade models, and improve documentation alignment.

### Multi-Environment Tool Declarations Implementation Plan

- Path: `docs/superpowers/plans/2026-05-22-multi-environment-tool-declarations.md`
- Kind: plan
- Status: implemented
- Summary: Implement a shared-agent tool declaration model that keeps `profile-al-dev-shared/agents/*.md` as the canonical source, generates harness-specific Claude/Copilot/Codex projections, and enforces drift checks through the existing alignment validator.

### Knowledge Quality Audit Fixes Implementation Plan

- Path: `docs/superpowers/plans/2026-05-22-knowledge-quality-fixes.md`
- Kind: plan
- Status: implemented
- Summary: Address 8 HIGH severity issues and 8 MEDIUM/LOW severity issues identified in the knowledge-quality audit to improve agent guidance completeness and actionability.

### Context Bloat Prevention Implementation Plan

- Path: `docs/superpowers/plans/2026-05-22-context-bloat-prevention.md`
- Kind: plan
- Status: abandoned
- Summary: Prevent context window bloat from unredirected compiler and build tool output in investigation sessions by adding output capture guidance and safeguards to exploration and investigation workflows.

## 2026-05-21

### Design Spec: Merge /al-dev-ticket + /al-dev-support

- Path: `docs/superpowers/specs/2026-05-21-ticket-support-merge-design.md`
- Kind: spec
- Status: historical
- Summary: **Status:** Draft — run /plan-map-changes after approving this design to generate the implementation plan **Date:** 2026-05-21 **Source:** docs/al-dev-plugin-map.md — Architectural suggestions > Merge

### Design Spec: Merge /al-dev-explore + /al-dev-perf

- Path: `docs/superpowers/specs/2026-05-21-explore-perf-merge-design.md`
- Kind: spec
- Status: historical
- Summary: **Status:** Draft — run /al-dev-plan after approving this design to generate the implementation plan **Date:** 2026-05-21 **Source:** docs/al-dev-plugin-map.md — Architectural suggestions > Merge

### Design Spec: Atomise /al-dev-develop

- Path: `docs/superpowers/specs/2026-05-21-develop-atomise-design.md`
- Kind: spec
- Status: historical
- Summary: **Status:** Draft — run /plan-map-changes after approving this design to generate the implementation plan **Date:** 2026-05-21 **Source:** docs/al-dev-plugin-map.md — Architectural suggestions > Atomise

### Claude Code Profile Aliases Design

- Path: `docs/superpowers/specs/2026-05-21-claude-profile-aliases-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-21 **Status:** Approved

### Plugin Map Improvements — Implementation Plan

- Path: `docs/superpowers/plans/2026-05-21-plugin-map-improvements.md`
- Kind: plan
- Status: implemented
- Summary: Implement 8 verified improvements from the plugin and agent maps: 4 lightweight fixes (tool trims + inputs alignment), 2 maintenance moves, 1 skill connection, 1 agent split — plus 3 design spikes for deferred structural changes.

### Plan: Add Subagents and TodoWrite to plan-map-changes

- Path: `docs/superpowers/plans/2026-05-21-plan-map-changes-subagents-todos.md`
- Kind: plan
- Status: implemented
- Summary: The skill at `.claude/skills/plan-map-changes/SKILL.md` translates Observations sections from plugin/agent maps into verified implementation plans. It currently runs entirely sequentially in the main context: it reads files inline, rubber-ducks each suggestion one-by-one, then invokes `writing-plans`.

### Plan: Add Parallel Exploration and Progress Tracking to audit-knowledge-quality

- Path: `docs/superpowers/plans/2026-05-21-audit-knowledge-quality-parallel-progress.md`
- Kind: plan
- Status: implemented
- Summary: The skill at `.claude/skills/audit-knowledge-quality/SKILL.md` analyzes flagged knowledge files sequentially in Phase 2. It currently processes each of N files through a multi-step checklist:

### Claude Code Profile Aliases Implementation Plan

- Path: `docs/superpowers/plans/2026-05-21-claude-profile-aliases.md`
- Kind: plan
- Status: implemented
- Summary: Enable context-aware plugin loading via shell aliases, reducing session context load for non-AL projects.

### AL-Dev-Shared Performance Improvements Implementation Plan

- Path: `docs/superpowers/plans/2026-05-21-al-dev-shared-performance-improvements.md`
- Kind: plan
- Status: implemented
- Summary: Reduce the two highest-frequency AL session friction patterns identified in the 2026-05-21 insights report: (1) subagent-generated AL code with non-existent field references and missing `var` modifiers, and (2) wasted debugging effort on stale compile logs.

### AL-Dev Compilation Efficiency & Context Management

- Path: `docs/superpowers/plans/2026-05-21-al-dev-compilation-efficiency.md`
- Kind: plan
- Status: implemented
- Summary: Fix compilation output bloat that caused context window exhaustion, reduce iterative compilation loops, and improve error categorization during AL development.

## 2026-05-20

### Usage Report Improvements: Phase 2 Implementation Plan

- Path: `docs/superpowers/plans/2026-05-20-usage-report-improvements-phase-2.md`
- Kind: plan
- Status: implemented
- Summary: Implement 4 high-impact improvements addressing friction patterns from the Claude Code usage report, with focus on automation, quality gates, and bug prevention.

### Usage Report Improvements Implementation Plan

- Path: `docs/superpowers/plans/2026-05-20-usage-report-improvements.md`
- Kind: plan
- Status: implemented
- Summary: Apply 4 low-effort, high-impact improvements identified in the Claude Code usage report to reduce recurring friction in commit workflows, design sessions, and skill invocations.

### Knowledge File Quality Fixes Implementation Plan

- Path: `docs/superpowers/plans/2026-05-20-knowledge-quality-fixes.md`
- Kind: plan
- Status: ready
- Summary: Resolve 19 HIGH and MEDIUM severity knowledge file gaps that block agent guidance, incomplete workflow documentation, and missing code examples.

## 2026-05-19

### Skill and Agent Quality Audit Design

- Path: `docs/superpowers/specs/2026-05-19-skill-agent-quality-audit-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-19 **Status:** Approved **Scope:** Two new project-local skills (`/audit-skill-quality`, `/audit-agent-quality`) that read source files directly and check for prompt clarity, structural conventions, description drift, bloat, and name fit.

### Design: Lens-Agent Parallelization for Project Analysis Skills

- Path: `docs/superpowers/specs/2026-05-19-lens-agent-parallelization-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-19 **Status:** Draft **Scope:** `.claude/skills/` project-level analysis skills

### Skill and Agent Quality Audit Implementation Plan

- Path: `docs/superpowers/plans/2026-05-19-skill-agent-quality-audit.md`
- Kind: plan
- Status: implemented
- Summary: Create two project-local skills — `/audit-skill-quality` and `/audit-agent-quality` — that read plugin source files directly and produce structured per-file quality reports across five lenses.

### Skill Quality Audit Fixes Implementation Plan

- Path: `docs/superpowers/plans/2026-05-19-skill-quality-fixes.md`
- Kind: plan
- Status: implemented
- Summary: Fix all 12 findings from the 2026-05-19 skill quality audit (4 High, 4 Medium, 4 Low severity).

### Plugin Map Improvements Implementation Plan

- Path: `docs/superpowers/plans/2026-05-19-plugin-map-improvements.md`
- Kind: plan
- Status: implemented
- Summary: Fix documentation accuracy and completeness in the AL dev plugin and agent maps by correcting stale agent names, standardizing labeling for shared patterns, documenting a missing skill phase, and adding omitted post-commit workflow nodes.

### Lens-Agent Parallelization Implementation Plan

- Path: `docs/superpowers/plans/2026-05-19-lens-agent-parallelization.md`
- Kind: plan
- Status: implemented
- Summary: Restructure four project-level analysis skills into a three-phase architecture that dispatches one lightweight Haiku lens agent per analytical lens in parallel, replacing sequential in-context analysis.

### Agent Quality Suggestions Implementation Plan

- Path: `docs/superpowers/plans/2026-05-19-agent-trim-remodel-align.md`
- Kind: plan
- Status: implemented
- Summary: Apply five quality suggestions from `docs/al-dev-agent-map.md` — trim unused Glob tools from three agents, downgrade al-dev-explore to haiku, and fix the misleading al-dev-code-review description.

### Agent Quality Audit Fix Implementation Plan

- Path: `docs/superpowers/plans/2026-05-19-agent-quality-fixes.md`
- Kind: plan
- Status: implemented
- Summary: Implement all 65 quality findings from the agent audit (29 High, 26 Medium, 10 Low severity), removing harness-specific notation and fixing structural, clarity, and bloat issues.

### Agent Map Quality Improvements Implementation Plan

- Path: `docs/superpowers/plans/2026-05-19-agent-map-quality-fixes.md`
- Kind: plan
- Status: historical
- Summary: Fix four quality issues in agent definitions (missing Write step, unused tools, misleading description) identified by `/analyze-agent-design`.

### Agent Map Observations: Implementation Plan

- Path: `docs/superpowers/plans/2026-05-19-agent-map-observations.md`
- Kind: plan
- Status: implemented
- Summary: Implement all actionable suggestions from the Observations section of `docs/al-dev-agent-map.md`: trim a stale tool grant, fix stale reviewer-team references, clarify dual-caller inputs, add I/O documentation to undocumented agents, fix commit-learn-verifier frontmatter, and split al-dev-commit-agent into two phase-specific agents.

## 2026-05-18

### Tighten Investigation / Fix Loop — Design Spec

- Path: `docs/superpowers/specs/2026-05-18-tighten-investigation-fix-loop-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-18 **Status:** Approved (design); pending implementation plan **Repo:** `al-dev-shared`

### Design: Add Move Candidate Detection to review-plugin-map

- Path: `docs/superpowers/specs/2026-05-18-review-plugin-map-move-skill-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-18 **Scope:** `review-plugin-map` skill (`al-dev-shared/.claude/skills/review-plugin-map/SKILL.md`) **Status:** Approved

### Agent Map Skills Design

- Path: `docs/superpowers/specs/2026-05-18-agent-map-skills-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-18 **Status:** Approved **Scope:** Two new project-local skills (`/review-agent-map`, `/analyze-agent-design`) plus a targeted extension to `/plan-plugin-map-changes`, producing a new `docs/al-dev-agent-map.md` document.

### Tighten Investigation/Fix Loop Implementation Plan

- Path: `docs/superpowers/plans/2026-05-18-tighten-investigation-fix-loop.md`
- Kind: plan
- Status: abandoned
- Summary: Add three surgical guardrails — regression-timeline gate, scope-lock checks, and Write-persistence verification — to prevent the three failure patterns identified in the 2026-05-18 session insights report.

### Review Plugin Map — Move Candidate Detection (Phase 7) Implementation Plan

- Path: `docs/superpowers/plans/2026-05-18-review-plugin-map-move-skill.md`
- Kind: plan
- Status: unknown
- Summary: Add Phase 7 to the `review-plugin-map` skill so it detects skills that belong in `.claude/skills/` rather than the distributed plugin and reports them as `Move:` suggestions in `docs/al-dev-plugin-map.md`.

### Release Notes Agent: Add MCP Tools to Frontmatter

- Path: `docs/superpowers/plans/2026-05-18-release-notes-mcp-tools.md`
- Kind: plan
- Status: unknown
- Summary: Add `al-mcp-server` and `bc-code-intelligence-mcp` to the `al-dev-release-notes-agent` tools list so its `research-context` phase can actually call AL symbols and BC expert MCP tools.

### Plugin Map Remaining Suggestions — Implementation Plan

- Path: `docs/superpowers/plans/2026-05-18-plugin-map-remaining-suggestions.md`
- Kind: plan
- Status: implemented
- Summary: Implement the 4 remaining unimplemented suggestions from the Observations section of `docs/al-dev-plugin-map.md` — one new knowledge doc with architect invocation patterns, two SKILL.md reference additions, three Layer 1 diagram extensions, and closing out one already-implemented observation.

### Plugin Map Architectural Suggestions — Implementation Plan

- Path: `docs/superpowers/plans/2026-05-18-plugin-map-architectural-suggestions.md`
- Kind: plan
- Status: implemented
- Summary: Implement the five architectural suggestions from the Observations section of `docs/al-dev-plugin-map.md` — a review-panel pattern doc, an explore-subagent pattern doc, moving al-dev-align out of the distributed plugin, updating the Layer 1 diagram, and merging al-dev-autonomous into al-dev-develop.

### Corpus Cleanup, analyze-plugin-design Update, and Plugin Map Housekeeping

- Path: `docs/superpowers/plans/2026-05-18-corpus-and-pluginmap-cleanup.md`
- Kind: plan
- Status: implemented
- Summary: Fix 3 stale test cases in `skill-test-trigger-corpus.yaml`; add pre-planning tributary analysis to `analyze-plugin-design`; and clean up implemented suggestions in `docs/al-dev-plugin-map.md`.

### Agent Map Skills Implementation Plan

- Path: `docs/superpowers/plans/2026-05-18-agent-map-skills.md`
- Kind: plan
- Status: implemented
- Summary: Create two project-local skills (`/review-agent-map`, `/analyze-agent-design`), seed their output document (`docs/al-dev-agent-map.md`), and extend `/plan-plugin-map-changes` with an `--agents` routing mode.

## 2026-05-17

### Skill-Test Harness — Phase A Design

- Path: `docs/superpowers/specs/2026-05-17-skill-test-harness-design.md`
- Kind: spec
- Status: ready
- Summary: **Date:** 2026-05-17 **Status:** Ready for plan authoring **Scope:** Cross-repo. Data + schema in `al-dev-shared` (harness-agnostic); orchestrator + `/skill-test` skill in `claude-configs` (Claude Code-specific). Phase A = findings-only (no auto-fix loop).

### Skill-Test Harness Fix Implementation Plan

- Path: `docs/superpowers/plans/2026-05-17-skill-test-fix.md`
- Kind: plan
- Status: unknown
- Summary: Fix three false-positive failures in the Phase A skill-test harness by patching two bugs in `run.py` and updating one scenario's expectations to match Phase A scope.

### Skill-Test Harness (Phase A) Implementation Plan

- Path: `docs/superpowers/plans/2026-05-17-skill-test-harness.md`
- Kind: plan
- Status: implemented
- Summary: Build a Phase-A skill-test maintenance harness — declarative test data and schema in `al-dev-shared` (harness-agnostic), an orchestrator + `/skill-test` skill in `claude-configs` (Claude Code-specific) — that exercises the 5 highest-blast-radius skills via four detection paths and writes coverage, findings, and a draft fix plan to `.dev/`. Phase A stops at writing the fix plan; the auto-fix loop is Phase B.

## 2026-05-16

### Archive Test-Related Skills and Agents

- Path: `docs/superpowers/specs/2026-05-16-archive-test-skills-design.md`
- Kind: spec
- Status: ready
- Summary: **Date:** 2026-05-16 **Status:** Ready for implementation **Scope:** `profile-al-dev-shared/` only
- External references: `profile-al-dev-shared/archived/README.md`

### AL Dev Plugin Map — Design Spec

- Path: `docs/superpowers/specs/2026-05-16-al-dev-plugin-map-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-16 **Status:** Approved for implementation **Audience:** Plugin author (personal reference for gap analysis and extension planning)

### Archive Test Skills and Agents Implementation Plan

- Path: `docs/superpowers/plans/2026-05-16-archive-test-skills.md`
- Kind: plan
- Status: implemented
- Summary: Move the `al-dev-test` skill and all 5 test-engineer agents out of the active plugin directories into `profile-al-dev-shared/archived/`, then update 4 active skills to remove all references to archived items.

### AL Dev Plugin Map Implementation Plan

- Path: `docs/superpowers/plans/2026-05-16-al-dev-plugin-map.md`
- Kind: plan
- Status: ready
- Summary: Generate `docs/al-dev-plugin-map.md` — a reference document with Mermaid diagrams showing the active skills, agents, and their relationships in the profile-al-dev-shared plugin.

## 2026-05-15

### Plugin Reliability & Quality Improvements — Design Spec

- Path: `docs/superpowers/specs/2026-05-15-plugin-reliability-quality-improvements-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-15 **Status:** Approved **Repos:** `al-dev-shared`, `claude-configs`

### al-dev-commit OOXML Guardrails Implementation Plan

- Path: `docs/superpowers/plans/2026-05-15-al-dev-commit-ooxml-guardrails.md`
- Kind: plan
- Status: unknown
- Summary: Prevent corrupted OOXML files from being committed through `/al-dev-commit` and require explicit human confirmation for risky mixed `.al` + `.docx` commit sets.

### Session Analyst Shared Report Format

- Path: `docs/superpowers/plans/2026-05-15-session-analyst-shared-format.md`
- Kind: plan
- Status: implemented
- Summary: Create a shared report format template in `al-dev-shared` so both harness-specific `al-dev-session-analyst` agents produce consistent, interchangeable findings reports — without merging the agents themselves.

### Plugin Reliability & Quality Improvements Implementation Plan

- Path: `docs/superpowers/plans/2026-05-15-plugin-reliability-quality-improvements.md`
- Kind: plan
- Status: implemented
- Summary: Implement the approved reliability/quality spec across `al-dev-shared` and `claude-configs` by adding closed-loop verification, external-claims validation, target disambiguation gates, and stronger adversarial planning requirements.

### Commit Validation Enforcement Implementation Plan

- Path: `docs/superpowers/plans/2026-05-15-commit-validation-enforcement.md`
- Kind: plan
- Status: implemented
- Summary: Prevent the three commit-convention violations found in the 2026-05-15 session review: missing emoji prefix, wrong AL body structure, and AI attribution footers slipping into commit messages.

## 2026-05-14

### Mermaid Helper Enforcement Design

- Path: `docs/superpowers/specs/2026-05-14-mermaid-helper-enforcement-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-14 **Status:** Approved

### Design: Trim md-mermaid-helper.md Context Cost

- Path: `docs/superpowers/specs/2026-05-14-trim-md-mermaid-helper-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-14 **Status:** Draft **File:** `profile-al-dev-shared/markdown/md-mermaid-helper.md`

### Trim md-mermaid-helper.md Context Cost — Implementation Plan

- Path: `docs/superpowers/plans/2026-05-14-trim-md-mermaid-helper.md`
- Kind: plan
- Status: unknown
- Summary: Remove the `applyTo` auto-load frontmatter from `md-mermaid-helper.md` and add

### Session Friction Remediation Implementation Plan

- Path: `docs/superpowers/plans/2026-05-14-session-friction-remediation.md`
- Kind: plan
- Status: implemented
- Summary: Reduce avoidable friction in AL/BC development sessions by implementing process improvements identified in the 2026-05-11 session friction analysis — quality review protocols, plan self-review requirements, and environment documentation.

### Commit Conventions Adoption Plan

- Path: `docs/superpowers/plans/2026-05-14-commit-conventions-adoption.md`
- Kind: plan
- Status: implemented
- Summary: Adopt `commit-conventions.md` as the single authoritative commit spec across all projects by removing duplicate/conflicting inline rules and adding a `project-type` declaration to each project's CLAUDE.md.

## 2026-05-11

### al-dev-align — Design Spec

- Path: `docs/superpowers/specs/2026-05-11-al-dev-align-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-11 **Status:** Approved for implementation

### Design: Harness-Agnostic al-dev-shared Plugin

- Path: `docs/superpowers/specs/2026-05-11-harness-agnostic-plugin-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-05-11 **Status:** Approved

### al-dev-align Implementation Plan

- Path: `docs/superpowers/plans/2026-05-11-al-dev-align.md`
- Kind: plan
- Status: implemented
- Summary: Build the `/al-dev-align` skill — a Python script plus SKILL.md that audits harness-specific token leaks in shared skill/agent/knowledge files and verifies mapping table completeness in both harness profile repos.

### Review Findings Implementation Plan

- Path: `docs/superpowers/plans/2026-05-11-review-findings-implementation.md`
- Kind: plan
- Status: unknown
- Summary: Apply all HIGH and MEDIUM action items from `.dev/2026-05-11-al-dev-review-findings.md` to `AGENTS.md` and `CLAUDE.md`, and apply the LOW item to the `al-dev-session-analyst` agent.

### Harness-Agnostic Plugin Design Implementation Plan

- Path: `docs/superpowers/plans/2026-05-11-harness-agnostic-plugin.md`
- Kind: plan
- Status: abandoned
- Summary: Make `al-dev-shared` skill and agent bodies harness-agnostic so they work correctly under any compliant profile plugin (Claude Code, Copilot CLI, or future harnesses).
