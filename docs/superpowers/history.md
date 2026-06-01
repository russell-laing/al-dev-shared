# Superpowers Planning History

Current source of truth: active implementation guidance lives in the current shared plugin source and knowledge documents.

## 2026-06-01

### Superpowers History Cleanup Implementation Plan

- Path: `docs/superpowers/plans/2026-06-01-superpowers-history-cleanup.md`
- Kind: plan
- Status: superseded
- Summary: Replace tracked historical Superpowers plan/spec clutter with a concise history document, preserving evolution context while removing obsolete execution artifacts from the current tracked surface.

### Historical `.dev` Artifact Cleanup

- Path: `.dev/2026-05-11-al-dev-review-findings.md`, `.dev/2026-05-15-commit-learn-report.md`, `.dev/2026-05-17-skill-test-coverage.md`, `.dev/2026-05-17-skill-test-findings.md`, `.dev/2026-05-17-skill-test-fix-plan.md`, `.dev/2026-05-21-smoke-test-results.txt`, `.dev/2026-05-24-ai-harness-neutral-usage-report.md`, `.dev/2026-05-27-al-dev-develop-phase-analysis.md`, `.dev/2026-05-27-plan-map-changes-rubber-duck.md`, `.dev/AL-LSP-Server-Setup.md`, `.dev/knowledge-audit.md`, `.dev/rubber-duck-records.md`, `.dev/sync-documentation-maps-runs/20260531T115645Z/*`
- Kind: tracked `.dev` report/log cleanup
- Status: historical
- Summary: Remove older `.dev` reports, ad hoc notes, one-off logs, and one completed sync-documentation-maps run after verifying they have no external references outside the historical tree. Keep live workflow state files such as progress checkpoints and current run artifacts.

### Pre-Commit Validation Expansion

- Path: `docs/superpowers/plans/2026-06-01-pre-commit-validation-expansion.md`
- Kind: plan
- Status: implemented
- Summary: Eliminate the three most common sources of batch "fix:" commits by making validation run at write/commit time, not reactively via health sweeps.

### Plugin Health Lens Dispatch Workflow Integration

- Path: `docs/superpowers/plans/2026-06-01-plugin-health-workflow-dispatch.md`
- Kind: plan
- Status: implemented
- Summary: Replace inline Agent spawning in `/plugin-health-discover` Phase 3a with Workflow-based fan-out to isolate lens agent conversations and reduce main-session context growth from ~160KB to ~20KB (87% reduction).

### Plugin Health Fixes — Top 5 Findings

- Path: `docs/superpowers/plans/2026-06-01-plugin-health-fixes.md`
- Kind: plan
- Status: unknown
- Summary: Resolve the 5 highest-impact plugin health findings: 1 critical model mismatch, 20 missing agent name fields, 160+ unlabeled code blocks, 14 agents with unused tool declarations, and 2 agent-map alignment errors.

### Plugin Health Findings Implementation Plan

- Path: `docs/superpowers/plans/2026-06-01-plugin-health-findings-implementation.md`
- Kind: plan
- Status: ready
- Summary: Resolve the top 5 verified plugin health findings (38+ total findings). Reduce code fence errors, clarify skill conditionals, atomise multi-concern skills, and split agent responsibilities.

### Low Priority Plugin Health Fixes Implementation Plan

- Path: `docs/superpowers/plans/2026-06-01-low-priority-plugin-health-fixes.md`
- Kind: plan
- Status: implemented
- Summary: Resolve every low-priority problem listed in `docs/health/2026-06-01-plugin-health-current.md` without taking on medium/high-priority refactors.

### Health Sweep Top 10 Fixes — Implementation Plan

- Path: `docs/superpowers/plans/2026-06-01-health-sweep-top-10-fixes.md`
- Kind: plan
- Status: implemented
- Summary: Address the top 5 highest-leverage findings from each health dossier (plugin and tooling surfaces), prioritized by severity and blast radius.

### Generated Map Sections Implementation Plan

- Path: `docs/superpowers/plans/2026-06-01-generated-map-sections-design.md`
- Kind: plan
- Status: unknown
- Summary: Add a deterministic generator that refreshes marked Mermaid and table sections in the map docs from `profile-al-dev-shared` source without touching authored commentary.

### Cross-Surface Architecture Synchronization Implementation Plan

- Path: `docs/superpowers/plans/2026-06-01-cross-surface-architecture-sync.md`
- Kind: plan
- Status: implemented
- Summary: Implement coordinated changes across skills and agents to resolve model-complexity mismatches, clarify handoff chains, and prepare for skill atomisation.

### Al-Dev-Code-Review Model Alignment Implementation Plan

- Path: `docs/superpowers/plans/2026-06-01-al-dev-code-review-model.md`
- Kind: plan
- Status: implemented
- Summary: Downgrade al-dev-code-review from sonnet to haiku and align all documentation to reflect the change consistently.
