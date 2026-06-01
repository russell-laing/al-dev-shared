# Handoff Chain Map

Unified view of skill artifact handoffs showing the complete flow from production-input skill through to final output. This document maps all skill → output artifact → consuming skill relationships across the active AL Dev Plugin surface.

---

## Handoff Chains

### Planning Chain: Upstream Inputs → Plan Production

| Input Skill | Input Artifact | Consuming Skill | Consumption Type | Notes |
|---|---|---|---|---|
| `al-dev-interview` | `.dev/*-al-dev-interview-requirements.md` | `al-dev-plan` | Optional | Supplies user requirements; plan provides fallback reasoning if missing |
| `al-dev-explore` | `.dev/*-al-dev-explore-findings.md` | `al-dev-plan` | Optional | Supplies architectural/codebase context; plan integrates findings as constraints |
| `al-dev-perf` | `.dev/*-al-dev-perf-perf-analysis.md` | `al-dev-plan` | Optional | Supplies performance constraints (CRITICAL/HIGH findings); plan respects them |
| `al-dev-plan` | `.dev/*-al-dev-plan-solution-plan.md` | `al-dev-develop` | **Mandatory** | Handoff artifact per `artifact-contracts.md` |

---

### Development Chain: Plan Execution → Code Review → Commit

| Input Skill | Input Artifact | Consuming Skill | Consumption Type | Notes |
|---|---|---|---|---|
| `al-dev-plan` | `.dev/*-al-dev-plan-solution-plan.md` | `al-dev-develop` | **Mandatory** | Authoritative implementation spec |
| `al-dev-develop` (Phase 4) | `.dev/*-al-dev-develop-phase4-handoff.md` | `al-dev-review-develop` | **Mandatory** | Contains module assignments, developer status, changed files |
| `al-dev-develop` | `.dev/*-al-dev-lint-lint-report.md` (if lint runs) | `al-dev-fix` | Optional | Feedback loop for auto-fixable lint issues |
| `al-dev-review-develop` | `.dev/*-al-dev-develop-code-review.md` | `al-dev-commit` | **Mandatory** | Synthesized review findings (security, expertise, performance) |
| `al-dev-commit` | Staged git state + analysis context | (implicit) | **Mandatory** | Commit message synthesis uses review + plan context |

---

### Review Chain: Post-Implementation Quality Gates

| Input Skill | Input Artifact | Consuming Skill | Consumption Type | Notes |
|---|---|---|---|---|
| `al-dev-develop` (Phase 4) | `.dev/*-al-dev-develop-phase4-handoff.md` | `al-dev-review-develop` | **Mandatory** | Identifies changed AL files, module assignments |
| (Compile verification) | `.dev/compile-errors.log` | `al-dev-review-develop` | **Mandatory** | Success evidence for clean compilation |
| `al-dev-review-develop` (Phase 6) | Synthesized review (Phase 6 output) | User via skill output | **Mandatory** | Code review panel writes `.dev/*-al-dev-develop-code-review.md` |

---

### Commit Chain: Staged Changes → Git Commit → Verification

| Input Skill | Input Artifact | Consuming Skill | Consumption Type | Notes |
|---|---|---|---|---|
| `al-dev-review-develop` | `.dev/*-al-dev-develop-code-review.md` | `al-dev-commit` | **Mandatory** | Informs commit message synthesis; reviewed artifacts are part of context |
| (Staged state) | Git staged diff | `al-dev-commit` | **Mandatory** | Stage validation gate; detects scope creep, hallucinations |
| `al-dev-commit` | (Commit created) | `verify-commits` | **Mandatory** | Verifies commit message matches plan scope |
| `verify-commits` | (Verified commit) | Git object store | **Final** | Ready for deployment |

---

### Post-Commit Chain: Outputs to Downstream Systems

| Input Skill | Input Artifact | Consuming Skill | Consumption Type | Notes |
|---|---|---|---|---|
| (Git commit) | Commit hash/message | `al-dev-release-notes` | Optional | Generates release notes from commit range |
| (Git commit) | Commit metadata | `al-dev-handoff` | Optional | Generates handoff prompt for downstream repos |
| (Git commit) | Commit diff/context | `al-dev-document` | Optional | Generates documentation from code changes |
| (Git commit) | Session context | `al-dev-consolidate` | Optional | Aggregates session summary into index |
| (Git commit on error) | Commit history | `commit-recover` | Conditional | Runs on integrity error; recovers file state |

---

### Ticket Chain: Support Entry Point (Conditional)

| Input Skill | Input Artifact | Consuming Skill | Consumption Type | Notes |
|---|---|---|---|---|
| `al-dev-ticket` | `.dev/*-al-dev-ticket-ticket-context.md` | `al-dev-plan` (optional) | Optional | Only flows if user escalates ticket to full feature implementation |
| `al-dev-ticket` (--mode=full) | `.dev/*-al-dev-ticket-ticket-context.md` | `al-dev-support-reply-drafter` | **Mandatory** (when full mode) | Context for drafting customer reply |
| `al-dev-ticket` (--mode=full) | Research + reply draft | User | Output | Customer reply (no downstream handoff) |

---

### Direct Fix Chain: Fast Iteration Path

| Input Skill | Input Artifact | Consuming Skill | Consumption Type | Notes |
|---|---|---|---|---|
| `al-dev-fix` | (implicit: bug description + repo context) | (No explicit handoff file) | N/A | Fix outputs directly to staging or `.dev/compile-errors.log` |
| `al-dev-fix` | `.dev/compile-errors.log` (if verification runs) | `al-dev-commit` | Optional | Verification result passed to commit analysis |
| `al-dev-perf` | `.dev/*-al-dev-perf-perf-analysis.md` | `al-dev-fix` | Optional | Perf findings can inform fix scope |

---

## Gap Analysis

### Identified Handoff Gaps

#### 1. Lint Report Optional Consumption

**Issue:** `al-dev-lint` produces `.dev/*-al-dev-lint-lint-report.md`, but no downstream skill has a mandatory dependency on it. The feedback loop (`al-dev-lint` → `al-dev-fix`) is optional.

**Impact:** Lint reports are produced but not guaranteed to flow to fixing. Risk of accumulating unresolved diagnostics.

**Mitigation (Phase B/C):**

- Lint report should trigger an automatic prompt: "Unresolved lint issues found. Run `/fix` to address them?"
- Future: integrate lint reporting into the Phase 0 resumption logic to flag stale reports across sessions.

#### 2. Commit Manifest Missing

**Issue:** `al-dev-commit` performs analysis (scope creep detection, hallucination checks) but produces no durable artifact for downstream verification. The staged state is authoritative, but no manifest file documents what was validated.

**Impact:** Post-commit verification (`verify-commits`) cannot replay the analysis; it only checks message-to-plan alignment.

**Mitigation (Phase B/C):**

- Create `.dev/*-al-dev-commit-analysis.md` documenting:
  - Files staged (with size delta)
  - Out-of-scope changes rejected (if any)
  - Compilation status pre-commit
  - Commit readiness verdict
- Allows resume of interrupted commit workflows and enables historical audit.

#### 3. Interview Requirements Optional

**Issue:** `al-dev-interview` is optional upstream; many plans proceed without running it. No gating enforces interview-first discipline for MEDIUM/COMPLEX work.

**Impact:** Plans can be built on user assumptions rather than explicit requirements, increasing rework risk.

**Mitigation (Phase B/C):**

- `al-dev-plan` complexity routing should strongly suggest `/interview` for MEDIUM/COMPLEX (not SIMPLE) requests.
- Phase 0 logic can resume and suggest interview completion if missing for complex scope.

#### 4. Release Notes Orphaned

**Issue:** `al-dev-release-notes` is optional post-commit and produces no artifact that blocks or gates downstream deployment. It is purely informational.

**Impact:** Release notes are generated ad-hoc and not integrated into deployment workflows.

**Mitigation (Phase B/C):**

- Integrate release-notes generation into `al-dev-consolidate` (session summary) so notes are always present in the session artifacts.
- Future: tie release-notes artifact to deployment gating (e.g., `al-dev-publish-to-marketplace`).

#### 5. Compile Errors Log Not Cleared on Success

**Issue:** `.dev/compile-errors.log` persists across runs. A successful compile can be masked by a stale error log from a prior session.

**Impact:** Resume logic may misinterpret old errors as current issues; false positives in validation gates.

**Mitigation (Phase B):**

- Phase 0 resume logic should explicitly check log timestamp against current session start time.
- Alternately: always truncate compile log at skill entry if no new compile is requested.

---

## Phase B Additions: Phase 0 Handoff Documentation

Phase B extends all lifecycle skills with explicit Phase 0 handoff checks:

| Skill | Phase 0 Check | Artifact to Resume | Action if Missing |
|---|---|---|---|
| `al-dev-plan` | Check for existing plan | `.dev/*-al-dev-plan-solution-plan.md` | Ask if user wants to continue, restart, or create new |
| `al-dev-develop` | Check develop progress + plan | `.dev/*-al-dev-develop-phase4-handoff.md` OR latest plan | Resume from last phase or fetch plan if only plan exists |
| `al-dev-review-develop` | Check for Phase 4 handoff | `.dev/*-al-dev-develop-phase4-handoff.md` | Stop and tell user to run `al-dev-develop` first |
| `al-dev-commit` | Check staged state + prior analysis | None (staged state is authority) | Read staged diff; ask if user wants to amend/abort/commit |
| `al-dev-fix` | (No formal resume today) | None | Ad-hoc; future may add progress checkpoint |
| `al-dev-lint` | Check for existing log | `.dev/compile-errors.log` (with timestamp check) | Compile fresh or use provided path |

---

## Phase C Integration: Skill Atomisation Impact

When skills are atomised (decomposed into smaller, reusable units):

- **Handoff boundaries become explicit contracts** — each sub-skill must name its input artifact and output artifact
- **Artifact contracts must cover all new boundaries** — `knowledge/artifact-contracts.md` expands with entries for each new skill
- **Optional vs. mandatory flows clarify** — Phase C design allows "skill A does not exist on this harness" and documents what artifacts are missing
- **Multi-harness support improves** — generated projections can skip conditional skills and map artifact names to harness-native alternatives

Example: If `al-dev-plan` is split into `al-dev-plan-architect` (debate) + `al-dev-plan-synthesize` (decision), the handoff is:

```text
al-dev-plan-architect → .dev/*-al-dev-plan-debate-summary.md → al-dev-plan-synthesize
```

---

## Reference

- **Artifact Contracts:** `knowledge/artifact-contracts.md` (authoritative durable output matrix)
- **Skills Map:** `docs/al-dev-skills-map.md` (skill relationships and phase sequences)
- **Workflow Resilience:** `knowledge/workflow-resilience.md` (Phase 0 checkpointing protocol)
- **Scope Expansion Gate:** `knowledge/scope-expansion-gate.md` (prevents out-of-scope handoff pollution)
