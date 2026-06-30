# Handoff Chain Map

Unified view of skill artifact handoffs showing the complete flow from
production-input skill through to final output. This document maps all skill
→ output artifact → consuming skill relationships across the active AL Dev
Plugin surface.

---

## Handoff Chains

### Planning Chain: Upstream Inputs → Plan Production

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| `interview` | `.dev/*-interview-requirements.md` | `plan` | Optional | Req |
| `explore` | `.dev/*-explore-findings.md` | `plan` | Optional | Ctx |
| `perf` | `perf-analysis.md` | `plan` | Optional | Perf |
| `plan` | `.dev/*-plan-solution-plan.md` | `develop-orchestrate` | **Mandatory** | Sp |

---

### Development Chain: Plan Execution → Code Review → Commit

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| `plan` | `.dev/*-plan-solution-plan.md` | `develop-orchestrate` | **Mandatory** | Sp |
| `develop-orchestrate` (P4) | `.dev/*-develop-phase4-handoff.md` | review | **Mandatory** | St |
| `lint` | `.dev/*-lint-lint-report.md` | `fix` | Optional | Fix |
| review-develop | `.dev/*-develop-code-review.md` | commit | **Mandatory** | Rev |
| `commit` | Staged diff | verify | **Mandatory** | Msg |

---

### Review Chain: Post-Implementation Quality Gates

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| `develop-orchestrate` (P4) | `.dev/*-develop-phase4-handoff.md` | review | **Mandatory** | Files |
| (Compile) | `compile-errors.log` | review | **Mandatory** | Sts |
| `review-develop` (P6) | Synthesized | User | **Mandatory** | Out |

---

### Commit Chain: Staged Changes → Git Commit → Verification

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| `review-develop` | `.dev/*-develop-code-review.md` | commit | Optional | Ctx |
| (Staged state) | Staged diff | commit | **Mandatory** | Val |
| `commit` | (Commit) | verify | **Mandatory** | Chk |
| `verify-commits` | (Verified) | Git | **Final** | Rdy |

---

### Post-Commit Chain: Outputs to Downstream Systems

| Source | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| (Git) | Commit msg | `release-notes` | Optional | Notes |
| (Git) | Metadata | `handoff` | Optional | Handoff |
| (Git) | Diff | `document` | Optional | Docs |
| (Git err) | History | `commit-recover` | Conditional | Recover |

---

### Investigation Chain: Investigation-Driven Handoffs

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| `investigate` | `.dev/*-investigate-findings.md` | `plan` | Optional | Inv |
| `investigate` | `.dev/*-investigate-findings.md` | `fix` | Optional | Inv |

---

### Ticket Chain: Support Entry Point (Conditional)

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| `ticket` | `.dev/*-ticket-ticket-context.md` | `plan` | Optional | Esc |
| `ticket` | `.dev/*-ticket-ticket-context.md` | `support-reply` | **Mandatory** | Drft |
| `support-reply` | `.dev/*-plugin-support-reply-<slug>.md` | User | Output | Out |

---

### Direct Fix Chain: Fast Iteration Path

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| fix | (implicit) | (none) | N/A | Out |
| fix | `compile-errors.log` | commit | Optional | Chk |
| perf | `perf-analysis.md` | fix | Optional | Scp |

---

## Gap Analysis

### Identified Handoff Gaps

A handoff gap occurs when an artifact produced by one skill is not guaranteed to be consumed by its intended downstream consumer, or when a critical dependency is missing from the chain. These gaps represent points where workflow continuity may be interrupted, creating risk of lost context or unprocessed outputs.

## Current Deployment Gaps

These gaps exist in the currently active, deployed skill chains and require immediate attention to prevent workflow disruption.

#### 1. Performance Analysis Optional Route

**Issue:** `/perf` produces `perf-analysis.md` which is optionally consumed by `/plan`. However, when findings are routed downstream to `/fix`, the connection is implicit with no gating ensuring performance findings are validated against the plan before fix workflow begins.

**Impact:** Performance-critical recommendations may be acted upon without validation that they align with the solution plan or architectural decisions. Risk of fixing performance issues in ways that contradict planned refactoring, or applying unnecessary optimizations that introduce unreviewed code changes.

**Mitigation Status:** None documented. Current workflow relies on manual user judgment to surface perf findings in fix context.

#### 2. Explore Findings Staleness

**Issue:** `/explore` produces `.dev/*-explore-findings.md`, which persists across session boundaries without explicit refresh or invalidation checks. Phase 0 logic does not flag whether those findings are stale relative to recent code changes or time elapsed.

**Impact:** Plans built on outdated exploration may miss recent architectural changes, bug fixes, or refactoring. Users may commit decisions based on findings that no longer apply, leading to rework or technical debt.

**Mitigation Status:** Addressed by `knowledge/artifact-freshness-gate.md`, which generalises the compile-log freshness check to explore findings and is required via rule 6 of `artifact-contracts.md`.

#### 3. Investigate Findings Dual Route

**Issue:** `/investigate` produces `.dev/*-investigate-findings.md` that can route to both `/plan` and `/fix` (see chains, row: Investigate findings to fix). No documented criteria distinguish which downstream path is appropriate, and no artifact-level gating prevents misrouting.

**Impact:** Complex findings appropriate for full planning may be sent directly to fix, resulting in narrow patches instead of systemic solutions. Conversely, simple investigation results may be over-engineered through full planning when direct fixing would suffice.

**Mitigation Status:** None documented. Routing decision is implicit and relies entirely on user request routing.

#### 4. Post-Development Review Feedback Loop

**Issue:** If `/review-develop` discovers blocking issues (compilation errors, architectural violations, out-of-scope changes), there is no documented handoff back to `/develop-orchestrate` to signal rework. The artifact flow is one-directional: develop → review → commit.

**Impact:** Blocking review findings may force manual rework or commitment of flawed code. No automated path exists to re-engage development with reviewer feedback; workflow may stall or fork into ad-hoc repair paths outside the documented chain.

**Mitigation Status:** None documented. Review findings are presented to user but have no formal downstream consumer.

#### 5. Lint Report Accumulation

**Issue:** Multiple lint runs may accumulate reports in `.dev/` with no documented cleanup or versioning strategy. Old reports from prior sessions can coexist with new ones, and Phase 0 logic does not distinguish current from stale lint output.

**Impact:** Resume logic may act on old lint findings that have already been addressed; users see conflicting guidance when multiple reports exist. Accumulation can create ambiguity about which issues remain unresolved.

**Mitigation Status:** Freshness now governed by `knowledge/artifact-freshness-gate.md` (lint reports are stale once any source file changes after the report); reuse is gated by rule 6 of `artifact-contracts.md`.

## Future Enhancement Gaps

The following gaps represent desired improvements and Phase B/C architectural enhancements.

#### 1. Lint Report Optional Consumption

**Issue:** `lint` produces `.dev/*-lint-lint-report.md`, but no
downstream skill has a mandatory dependency on it. The feedback loop
(`lint` → `fix`) is optional.

**Impact:** Lint reports produced but not guaranteed to flow to fixing.
Risk of accumulating unresolved diagnostics.

**Mitigation (Phase B/C):**

- Lint report should trigger prompt: "Run `/fix` to address lint
  issues?"
- Future: integrate lint reporting into Phase 0 resumption logic to
  flag stale reports across sessions.

#### 2. Commit Manifest Missing (Phase B/C)

**Issue:** `commit` performs analysis (scope creep detection,
hallucination checks) but produces no durable artifact for downstream
verification. The staged state is authoritative, but no manifest file
documents what was validated.

**Impact:** Post-commit verification (`verify-commits`) cannot replay
the analysis; checks message-to-plan alignment only.

**Mitigation (Phase B/C):**

- Create `.dev/*-commit-analysis.md` documenting:
  - Staged files (size delta)
  - Out-of-scope changes (if any)
  - Compile status
  - Readiness verdict
- Enable resume of interrupted workflows and historical audit.

#### 3. Interview Requirements Optional (Phase B/C)

**Issue:** `interview` is optional upstream; many plans proceed without
running it. No gating enforces interview-first discipline for MEDIUM/COMPLEX
work.

**Impact:** Plans built on assumptions vs. explicit requirements;
increases rework risk.

**Mitigation (Phase B/C):**

- `plan` routing should suggest `/interview` for MEDIUM/COMPLEX
  requests.
- Phase 0 can suggest interview completion if missing for complex
  scope.

#### 4. Release Notes Orphaned (Phase B/C)

**Issue:** `release-notes` is optional post-commit and produces no
artifact that blocks or gates downstream deployment. It is purely
informational.

**Impact:** Release notes generated ad-hoc, not integrated into
deployment workflows.

**Mitigation (Phase B/C):**

- Future: tie release-notes to deployment gating
  (`al-dev-publish-to-marketplace`).

#### 5. Compile Errors Log Not Cleared on Success (Phase B)

**Issue:** `.dev/compile-errors.log` persists across runs. A successful
compile can be masked by a stale error log from a prior session.

**Impact:** Resume logic may misinterpret old errors as current issues; false
positives in validation gates.

**Mitigation (Phase B):**

- Phase 0 should check log timestamp against session start time.
- Alternately: truncate compile log at skill entry if no new compile
  is requested.

---

## Phase B Additions: Phase 0 Handoff Documentation

Phase B extends all lifecycle skills with explicit Phase 0 handoff checks:

| Skill | Check | Artifact | Action |
|---|---|---|---|
| `plan` | Plan exists | `*-plan-solution-plan.md` | Continue/restart |
| `develop-orchestrate` | Progress + plan | Phase 4 OR plan | Resume |
| `review-develop` | Phase 4 | `*-develop-phase4-handoff.md` | Run develop |
| `commit` | Staged state | None | Check diff |
| `fix` | (None) | None | Ad-hoc |
| `lint` | Log exists | Errors log | Fresh or path |

---

## Phase C Integration: Skill Atomisation Impact

When skills are atomised (decomposed into smaller, reusable units):

- **Handoff boundaries become explicit contracts** — each sub-skill
  names its input and output artifact
- **Artifact contracts expand** — `knowledge/artifact-contracts.md`
  covers each new skill
- **Optional vs. mandatory flows clarify** — Phase C design documents
  skill availability across harnesses
- **Multi-harness support improves** — generated projections skip
  conditional skills and map names to harness-native alternatives

Example: If `plan` is split into `plan-architect`
(debate) + `plan-synthesize` (decision), the handoff is:

```text
plan-architect → .dev/*-plan-debate-summary.md → plan-synthesize
```

---

## Reference

- **Artifact Contracts:** `knowledge/artifact-contracts.md`
  (durable output matrix)
- **Skills Map:** `docs/skills_map.md` (relationships & sequences)
- **Workflow Resilience:** `knowledge/workflow-resilience.md`
  (Phase 0 checkpointing)
- **Scope Expansion Gate:** `knowledge/scope-expansion-gate.md`
  (prevents out-of-scope pollution)
