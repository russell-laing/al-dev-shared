# Plugin Improvement Assessment

## Source

- Artifact: `.dev/2026-06-13-harness-improvement-research-claude-self-healing-loop.md`
- Reporting window: current vendor docs accessed on 2026-06-13
- Assessment date: 2026-06-13

## Executive Summary

The source briefing contains real evidence about correctness risks in the repo-local `.claude` self-healing loop, especially around resume semantics, compacted state, and delegated-work boundaries. Live `profile-al-dev-shared` review shows that the shared surface already covers the portable parts of this space through `knowledge/workflow-resilience.md`, `knowledge/artifact-contracts.md`, `knowledge/background-agent-dispatch.md`, and intent-routing safeguards. The remaining gaps described by the briefing are either explicitly repo-local `.claude` control-plane concerns or harness-specific hook behavior, so the evidence does not currently justify a shared-plugin change. The recommended next step is no shared-profile action from this report; if desired later, write a separate repo-local `.claude` spec for self-healing loop hardening.

## Evidence-Backed Findings

| Finding | Evidence | Existing Coverage |
|---|---|---|
| The source identifies resume-state and orchestration-state risks in the `.claude` self-healing loop, but scopes them to repo-local loop artifacts rather than shared AL/BC workflows. | Source sections `Live Repository Baseline`, `Evidence-Backed Findings`, and `Candidate Patterns` all reference `.claude/knowledge/*`, `.claude/skills/*`, `.dev/health-loop-state.md`, and repo-local scripts as the affected surfaces. | `profile-al-dev-shared/knowledge/workflow-resilience.md` already defines shared checkpointing and resume prompts for multi-phase skills. |
| Shared authored knowledge already covers authoritative resume artifacts, read order, contradiction handling, and success-evidence gates. | The source argues for explicit state boundaries and resume discipline; live repo review shows those rules already exist on the shared surface for shipped workflows. | `profile-al-dev-shared/knowledge/artifact-contracts.md`; `profile-al-dev-shared/knowledge/workflow-resilience.md`; `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`. |
| Shared authored knowledge already covers explicit delegated-agent handoff through artifacts, reducing the merit of a new shared handoff rule derived only from the `.claude` loop. | Source finding 5 proposes a standard delegated-work handoff payload because the self-healing loop docs do not define one. | `profile-al-dev-shared/knowledge/background-agent-dispatch.md` already requires exact inputs, fixed artifact paths, and artifact-based completion gates for delegated work. |
| The hook-backed guard recommendation is harness-specific and therefore not a shared-profile candidate without a deeper harness-neutral rule underneath it. | Source candidate pattern 3 explicitly marks hook-backed correctness gates as `harness-specific`. | `profile-al-dev-shared/knowledge/harness-concepts.md` and the repository boundary in `AGENTS.md` favor harness-neutral shared guidance and repo-local harness infrastructure for native enforcement mechanisms. |
| The source itself does not prove that any candidate should move into `profile-al-dev-shared`. | Source `Gaps And Uncertainty` says it did not find evidence that the candidate patterns should move into shared `profile-al-dev-shared`; source `Rejected Or Non-Portable Patterns` rejects promoting them directly into shared profile for now. | `profile-al-dev-shared/knowledge/intent-preflight.md` already distinguishes review-only assessment from implementation planning, which aligns with keeping this assessment non-mutating. |

## Candidate Improvements

| Candidate | Classification | Reason |
|---|---|---|
| Add a shared-plugin control-plane state contract separating breadcrumb, resumable checkpoint, ledger state, and compacted summary. | reject | The report evidence is specific to the repo-local `.claude` self-healing loop, while the shared profile already has portable resume and artifact-boundary guidance in `workflow-resilience.md` and `artifact-contracts.md`. |
| Expand shared workflow state with a richer compacted payload beyond a simple next-step checkpoint. | defer | The source shows a real correctness concern, but only for one repo-local loop. A shared change would need broader evidence across active shipped workflows and a separate design for how every skill should serialize compacted state. |
| Add hook-backed correctness gates to the shared plugin. | reject | The source explicitly marks this pattern as harness-specific, so it does not pass the shared-plugin fit test. |
| Add a shared delegated-work handoff payload standard. | reject | The shared surface already defines a harness-neutral delegated artifact contract in `background-agent-dispatch.md`; the remaining gap is that the `.claude` loop has not adopted an equivalent repo-local specialization. |
| Add shared guidance stating that memory and checkpointing cannot replace explicit close-back artifacts. | reject | The shared surface already treats artifacts and current-run evidence as authoritative through `artifact-contracts.md` and `workflow-resilience.md`, so this would duplicate existing guidance rather than fill a proven gap. |

## Rubber-Duck Gate for Kept Items

| Candidate | Evidence | Existing Coverage | Shared-Plugin Fit | Risk Reduced | Test or Review Strategy |
|---|---|---|---|---|---|
| none | no candidate passed the keep gate | not applicable | not applicable | not applicable | not applicable |

## Recommended Next Step

- No action: the report supports repo-local `.claude` hardening discussion, but it does not provide enough evidence for a durable shared `profile-al-dev-shared` change.

## Out of Scope

- This assessment did not edit `profile-al-dev-shared`.
- This assessment did not regenerate projections.
- This assessment did not commit changes.
