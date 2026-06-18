# Plugin Improvement Assessment

## Source

- Artifact: `.dev/2026-06-15-harness-improvement-research.md`
- Reporting window: not stated
- Assessment date: 2026-06-15

## Executive Summary

The source briefing is substantive and evidence-backed, but its strongest
improvement candidates are repo-local rather than shared-profile changes. The
two clearest recommendations, phase-level proof-of-execution gates and
deterministic dispatch fallback behavior, target maintainer workflows under
`.codex/` and `.claude/`, not durable harness-neutral AL/BC guidance. The only
plausible shared candidate, stronger delegated-task scope packaging, is already
substantially covered by the existing Scope Expansion Gate and developer spawn
contracts in `profile-al-dev-shared`. The correct outcome for the shared plugin
surface is `No action`.

## Evidence-Backed Findings

| Finding | Evidence | Existing Coverage |
|---|---|---|
| The source report's strongest execution-fidelity gap is phase progress being reported before execution is proven. | The research briefing cites the Claude usage report's repeated "prove it ran" recommendation and identifies a narrow gap in phase-level proof, not a missing global verification system. | `profile-al-dev-shared/knowledge/artifact-contracts.md`, `profile-al-dev-shared/knowledge/rubber-duck.md`, and `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` already require current-run evidence and read-after-write checks for several shared workflows. |
| The dispatch-fragility finding is real, but the portable lesson is wrapper fallback policy, not a shared rule about one harness tool. | The research briefing explicitly marks "standardize on the Agent tool" as non-portable and reframes it as deterministic dispatch preflight and fallback after preferred delegation fails. | `profile-al-dev-shared/knowledge/workflow-resilience.md` already covers some subagent fallback behavior, but the missing behavior lives in repo-local maintainer wrappers rather than shipped shared AL workflows. |
| Shared delegated-task scope control is already present in the live plugin surface. | The research briefing identifies this as only a partial propagation gap, not a missing concept. Live repo search confirms the Scope Expansion Gate is propagated into `al-dev-develop`, `al-dev-fix`, `developer-invocation-patterns.md`, and `al-dev-develop-spawn-prompt.md`. | `profile-al-dev-shared/knowledge/scope-expansion-gate.md`, `profile-al-dev-shared/knowledge/developer-invocation-patterns.md`, `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md`, and `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`. |

## Candidate Improvements

| Candidate | Classification | Reason |
|---|---|---|
| Add a shared-profile phase-proof contract for maintainer health and execution workflows. | reject | The evidence is real, but the affected surfaces are repo-local maintainer workflows under `.codex/` and `.claude/`, not shared `profile-al-dev-shared` behavior. |
| Add a shared-profile dispatch wrapper or fallback policy. | reject | The source evidence arises from Claude-side dispatch failures and wrapper behavior. The durable action belongs in repo-local tooling, and a shared plugin rule would overfit one harness failure mode. |
| Generalize delegated-task scope control into a new shared scope-pack pattern. | reject | Existing shared files already define and propagate the Scope Expansion Gate with explicit stop, approval, and propagation rules. The current evidence does not demonstrate a missing shared contract, only a repo-local enforcement gap. |

## Rubber-Duck Gate for Kept Items

| Candidate | Evidence | Existing Coverage | Shared-Plugin Fit | Risk Reduced | Test or Review Strategy |
|---|---|---|---|---|---|
| none | No candidate passed the `keep` threshold. The strongest issues are repo-local, and the only shared candidate is already materially covered. | `profile-al-dev-shared/knowledge/scope-expansion-gate.md`, `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md`, `profile-al-dev-shared/knowledge/developer-invocation-patterns.md` | none | none | none |

## Recommended Next Step

- No action: the current evidence does not justify a new shared-plugin change. If the user wants to improve the observed failure modes, the next work should target repo-local maintainer tooling rather than `profile-al-dev-shared`.

## Out of Scope

- This assessment did not edit `profile-al-dev-shared`.
- This assessment did not regenerate projections.
- This assessment did not commit changes.
