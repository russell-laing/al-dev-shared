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
| `al-dev-interview` | `requirements.md` | `al-dev-plan` | Optional | Req |
| `al-dev-explore` | `findings.md` | `al-dev-plan` | Optional | Ctx |
| `al-dev-perf` | `perf-analysis.md` | `al-dev-plan` | Optional | Perf |
| `al-dev-plan` | `solution-plan.md` | `al-dev-develop` | **Mandatory** | Sp |

---

### Development Chain: Plan Execution → Code Review → Commit

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| `al-dev-plan` | `solution-plan.md` | `al-dev-develop` | **Mandatory** | Sp |
| `al-dev-develop` (P4) | `phase4-handoff.md` | review | **Mandatory** | St |
| `al-dev-lint` | `lint-report.md` | `al-dev-fix` | Optional | Fix |
| review-develop | `code-review.md` | commit | **Mandatory** | Rev |
| `al-dev-commit` | Staged diff | verify | **Mandatory** | Msg |

---

### Review Chain: Post-Implementation Quality Gates

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| `al-dev-develop` (P4) | `phase4-handoff.md` | review | **Mandatory** | Files |
| (Compile) | `compile-errors.log` | review | **Mandatory** | Sts |
| `al-dev-review-develop` (P6) | Synthesized | User | **Mandatory** | Out |

---

### Commit Chain: Staged Changes → Git Commit → Verification

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| `al-dev-review-develop` | `code-review.md` | commit | Optional | Ctx |
| (Staged state) | Staged diff | commit | **Mandatory** | Val |
| `al-dev-commit` | (Commit) | verify | **Mandatory** | Chk |
| `verify-commits` | (Verified) | Git | **Final** | Rdy |

---

### Post-Commit Chain: Outputs to Downstream Systems

| Source | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| (Git) | Commit msg | `al-dev-release-notes` | Optional | Notes |
| (Git) | Metadata | `al-dev-handoff` | Optional | Handoff |
| (Git) | Diff | `al-dev-document` | Optional | Docs |
| (Git err) | History | `commit-recover` | Conditional | Recover |

---

### Investigation Chain: Investigation-Driven Handoffs

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| `al-dev-investigate` | `findings.md` | `al-dev-plan` | Optional | Inv |
| `al-dev-investigate` | `findings.md` | `al-dev-fix` | Optional | Inv |

---

### Ticket Chain: Support Entry Point (Conditional)

| Skill | Artifact | Consumes | Type | Notes |
|---|---|---|---|---|
| `al-dev-ticket` | `ticket-context.md` | `al-dev-plan` | Optional | Esc |
| `al-dev-ticket` | `context.md` | drafter | **Mandatory** | Drft |
| drafter | Research draft | User | Output | Out |

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

**Issue:** `/al-dev-perf` produces `perf-analysis.md` which is optionally consumed by `/al-dev-plan`. However, when findings are routed downstream to `/al-dev-fix`, the connection is implicit with no gating ensuring performance findings are validated against the plan before fix workflow begins.

**Impact:** Performance-critical recommendations may be acted upon without validation that they align with the solution plan or architectural decisions. Risk of fixing performance issues in ways that contradict planned refactoring, or applying unnecessary optimizations that introduce unreviewed code changes.

**Mitigation Status:** None documented. Current workflow relies on manual user judgment to surface perf findings in fix context.

#### 2. Explore Findings Staleness

**Issue:** `/al-dev-explore` produces `findings.md` which persists across session boundaries without explicit refresh or invalidation checks. Phase 0 logic does not flag whether findings are stale relative to recent code changes or time elapsed.

**Impact:** Plans built on outdated exploration may miss recent architectural changes, bug fixes, or refactoring. Users may commit decisions based on findings that no longer apply, leading to rework or technical debt.

**Mitigation Status:** None documented. No session-boundary check or freshness validation in consuming skills.

#### 3. Investigate Findings Dual Route

**Issue:** `/al-dev-investigate` produces `findings.md` that can route to both `/al-dev-plan` and `/al-dev-fix` (see chains, row: Investigate findings to fix). No documented criteria distinguish which downstream path is appropriate, and no artifact-level gating prevents misrouting.

**Impact:** Complex findings appropriate for full planning may be sent directly to fix, resulting in narrow patches instead of systemic solutions. Conversely, simple investigation results may be over-engineered through full planning when direct fixing would suffice.

**Mitigation Status:** None documented. Routing decision is implicit and relies entirely on user request routing.

#### 4. Post-Development Review Feedback Loop

**Issue:** If `/al-dev-review-develop` discovers blocking issues (compilation errors, architectural violations, out-of-scope changes), there is no documented handoff back to `/al-dev-develop` to signal rework. The artifact flow is one-directional: develop → review → commit.

**Impact:** Blocking review findings may force manual rework or commitment of flawed code. No automated path exists to re-engage development with reviewer feedback; workflow may stall or fork into ad-hoc repair paths outside the documented chain.

**Mitigation Status:** None documented. Review findings are presented to user but have no formal downstream consumer.

#### 5. Lint Report Accumulation

**Issue:** Multiple lint runs may accumulate reports in `.dev/` with no documented cleanup or versioning strategy. Old reports from prior sessions can coexist with new ones, and Phase 0 logic does not distinguish current from stale lint output.

**Impact:** Resume logic may act on old lint findings that have already been addressed; users see conflicting guidance when multiple reports exist. Accumulation can create ambiguity about which issues remain unresolved.

**Mitigation Status:** None documented. Lint reports are optional consumption; no cleanup or consolidation step exists.

## Future Enhancement Gaps

The following gaps represent desired improvements and Phase B/C architectural enhancements.

#### 1. Lint Report Optional Consumption

**Issue:** `al-dev-lint` produces `.dev/*-al-dev-lint-lint-report.md`, but no
downstream skill has a mandatory dependency on it. The feedback loop
(`al-dev-lint` → `al-dev-fix`) is optional.

**Impact:** Lint reports produced but not guaranteed to flow to fixing.
Risk of accumulating unresolved diagnostics.

**Mitigation (Phase B/C):**

- Lint report should trigger prompt: "Run `/fix` to address lint
  issues?"
- Future: integrate lint reporting into Phase 0 resumption logic to
  flag stale reports across sessions.

#### 2. Commit Manifest Missing (Phase B/C)

**Issue:** `al-dev-commit` performs analysis (scope creep detection,
hallucination checks) but produces no durable artifact for downstream
verification. The staged state is authoritative, but no manifest file
documents what was validated.

**Impact:** Post-commit verification (`verify-commits`) cannot replay
the analysis; checks message-to-plan alignment only.

**Mitigation (Phase B/C):**

- Create `.dev/*-al-dev-commit-analysis.md` documenting:
  - Staged files (size delta)
  - Out-of-scope changes (if any)
  - Compile status
  - Readiness verdict
- Enable resume of interrupted workflows and historical audit.

#### 3. Interview Requirements Optional (Phase B/C)

**Issue:** `al-dev-interview` is optional upstream; many plans proceed without
running it. No gating enforces interview-first discipline for MEDIUM/COMPLEX
work.

**Impact:** Plans built on assumptions vs. explicit requirements;
increases rework risk.

**Mitigation (Phase B/C):**

- `al-dev-plan` routing should suggest `/interview` for MEDIUM/COMPLEX
  requests.
- Phase 0 can suggest interview completion if missing for complex
  scope.

#### 4. Release Notes Orphaned (Phase B/C)

**Issue:** `al-dev-release-notes` is optional post-commit and produces no
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
| `al-dev-plan` | Plan exists | `*-solution-plan.md` | Continue/restart |
| `al-dev-develop` | Progress + plan | Phase 4 OR plan | Resume |
| `al-dev-review-develop` | Phase 4 | `*-phase4-handoff.md` | Run develop |
| `al-dev-commit` | Staged state | None | Check diff |
| `al-dev-fix` | (None) | None | Ad-hoc |
| `al-dev-lint` | Log exists | Errors log | Fresh or path |

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

Example: If `al-dev-plan` is split into `al-dev-plan-architect`
(debate) + `al-dev-plan-synthesize` (decision), the handoff is:

```text
al-dev-plan-architect → .dev/*-al-dev-plan-debate-summary.md → al-dev-plan-synthesize
```

---

## Reference

- **Artifact Contracts:** `knowledge/artifact-contracts.md`
  (durable output matrix)
- **Skills Map:** `docs/al-dev-skills-map.md` (relationships & sequences)
- **Workflow Resilience:** `knowledge/workflow-resilience.md`
  (Phase 0 checkpointing)
- **Scope Expansion Gate:** `knowledge/scope-expansion-gate.md`
  (prevents out-of-scope pollution)
