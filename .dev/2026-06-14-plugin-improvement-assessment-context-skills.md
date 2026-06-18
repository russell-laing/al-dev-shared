# Plugin Improvement Assessment

## Source

- Artifact: `.dev/2026-06-14-harness-improvement-research-context-skills.md`
- Reporting window: not stated
- Assessment date: 2026-06-14

## Executive Summary

The research briefing correctly identified context freshness as the strongest shared-surface gap, but it understated three live repo issues that are more immediate: missing artifact-contract coverage for `al-dev-investigate` and `al-dev-handoff`, inconsistent ticket-artifact naming across `al-dev-ticket`, `al-dev-support-reply`, and `artifact-contracts.md`, and unclear shared guidance around harness-specific ownership of `al-dev-init-context`. The briefing’s repo-local candidates around compaction and indexing are still plausible, but they do not yet clear the shared-plugin merit gate. The MCP export idea does not fit the shared plugin surface and should be rejected at this stage. The strongest next step is a focused implementation plan for shared contract fixes, ticket-artifact alignment, dependency-clarity fixes, and freshness gating.

## Evidence-Backed Findings

| Finding | Evidence | Existing Coverage |
|---|---|---|
| Context freshness is a documented live problem, not a speculative improvement. | `profile-al-dev-shared/knowledge/handoff-chain-map.md` explicitly flags stale `al-dev-explore` findings and stale lint artifacts as current deployment gaps. | `profile-al-dev-shared/knowledge/compile-lint-procedure.md` already implements a freshness check for compile logs, showing the pattern exists but is not generalized. |
| `al-dev-investigate` and `al-dev-handoff` write durable context artifacts but are missing from the artifact-contract source of truth. | `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md` writes `.dev/*-al-dev-investigate-findings.md`; `profile-al-dev-shared/skills/al-dev-handoff/SKILL.md` writes copied `source-*` files plus `.dev/*-al-dev-handoff-handoff-prompt.md`; neither skill appears in `profile-al-dev-shared/knowledge/artifact-contracts.md`. | `profile-al-dev-shared/knowledge/handoff-chain-map.md` documents both skills in handoff chains and states artifact contracts should expand as skills atomize. |
| Runtime artifact validation currently covers only ticket, interview, and explore artifacts. | `scripts/validate_artifact_contracts.py` defines runtime tests only for `al-dev-ticket`, `al-dev-interview`, and `al-dev-explore`. | `profile-al-dev-shared/knowledge/artifact-contracts.md` is the structural source of truth, but runtime checks are incomplete. |
| The ticket workflow does not agree on reply-artifact and summary-artifact names. | `al-dev-ticket` says full mode writes `.dev/YYYY-MM-DD-al-dev-ticket-reply.md`, `al-dev-support-reply` says it writes `.dev/ticket-reply.md`, and `artifact-contracts.md` lists `.dev/ticket-context.md` and `.dev/ticket-reply.md` while the main ticket context artifact is date-prefixed. | Ticket-context naming is consistent in `ticket-agent-invocation-pattern.md` and the validator glob, but reply and summary naming are not aligned across the workflow docs. |
| The shared surface routes users to `/al-dev-init-context`, but the implementation lives in harness-specific companion repos rather than `profile-al-dev-shared`. | The user clarified that `al-dev-init-context` is provided by companion repos such as `codex-configs/codex-al-dev/skills/al-dev-init-context/SKILL.md` and `claude-configs/profile-claude-al-dev/skills/al-dev-init-context/SKILL.md`. Shared files in this repo still reference the command without explaining that ownership boundary. | `project-context.md` is treated as important shared context by `al-dev-explore`, `al-dev-plan-preflight`, `al-dev-develop`, and `workflow-routing.md`, but shared guidance does not currently make the companion-repo dependency explicit. |
| Long-run compaction and machine-readable context inventory are useful ideas, but current evidence supports repo-local experimentation before shared adoption. | OpenAI conversation-state and GPT-5.5 reasoning guidance recommend explicit continuation state and compaction; MCP resources support metadata-rich context objects. | The live repo already uses durable `.dev/` artifacts and resume packs, but no shared contract currently requires compaction or a manifest. |

## Candidate Improvements

| Candidate | Classification | Reason |
|---|---|---|
| Add a shared freshness gate for reusable context artifacts (`ticket`, `explore`, `investigate`, `handoff`, `lint`) | keep | Strong live evidence of stale-artifact risk, existing compile-log freshness precedent, and clear shared-workflow value. |
| Expand `artifact-contracts.md` and `validate_artifact_contracts.py` to cover `al-dev-investigate` and `al-dev-handoff` | keep | These skills already produce durable context and participate in downstream routing, but their contracts and runtime checks are missing. |
| Align ticket-workflow artifact naming across `al-dev-ticket`, `al-dev-support-reply`, `artifact-contracts.md`, and related validators | keep | The current shared workflow disagrees about the canonical reply and summary artifact names, which weakens downstream discovery and review gates. |
| Clarify companion-repo ownership and fallback behavior for `al-dev-init-context` and `project-context.md` | keep | Multiple live shared skills route through a harness-specific companion capability, but the shared guidance does not explain that boundary or the correct fallback when the companion skill is unavailable. |
| Add `compact-session-context` as a shared skill | defer | Real need for long-running sessions, but current evidence points first to repo-local maintainer tooling rather than a shared AL/BC workflow contract. |
| Add `index-context-artifacts` as a shared skill | defer | Useful for `.dev/` discoverability, but the strongest fit is repo-local tooling or a small manifest pattern after contract coverage is fixed. |
| Add `refresh-handoff-pack` as a separate shared skill | defer | The underlying problem is real, but most of the value may be captured by freshness gating plus formal handoff contracts. |
| Export `.dev/` context via MCP resources/prompts | reject | Useful in harness-specific tooling, but not a shared authored plugin change. |
| Create a prompt-caching skill | reject | Prompt caching is an orchestration or API concern, not a shared skill contract. |

## Rubber-Duck Gate for Kept Items

| Candidate | Evidence | Existing Coverage | Shared-Plugin Fit | Risk Reduced | Test or Review Strategy |
|---|---|---|---|---|---|
| Shared freshness gate for reusable context artifacts | `handoff-chain-map.md` documents stale `explore` and lint artifacts; OpenAI guidance recommends deliberate continuation state and compaction rather than blind history reuse. | `compile-lint-procedure.md` already performs freshness checks for compile logs; `artifact-contracts.md` already defines success-evidence semantics. | Freshness of reusable workflow artifacts is durable, harness-neutral behavior across planning, investigation, and handoff flows. | Stale debugging context, stale planning input, wrong downstream routing, and false “ready” claims based on old artifacts. | Add trigger corpus or scenario coverage for stale findings reuse, expand artifact-contract validation rules, and manual review against `handoff-chain-map.md` gap rows. |
| Expand artifact contracts and runtime tests to `al-dev-investigate` and `al-dev-handoff` | Both skills write durable artifacts today, but `artifact-contracts.md` and `validate_artifact_contracts.py` omit them. `handoff-chain-map.md` explicitly expects artifact-contract expansion. | `artifact-contracts.md` already governs analogous skills; `validate_artifact_contracts.py` already has the runtime pattern for ticket, interview, and explore. | This is shared workflow contract hygiene for existing shared skills, not repo-local tooling. | Untracked handoff artifacts, missing success-evidence gates, and consumers using undocumented files implicitly. | Extend `artifact-contracts.md`, add validator coverage, and add or update `tests/scenarios.yaml` for both skills. |
| Align ticket-workflow artifact naming | `al-dev-ticket` documents a date-prefixed reply artifact, `al-dev-support-reply` documents a non-prefixed reply artifact, and `artifact-contracts.md` mixes date-prefixed ticket context with non-prefixed summary and reply names. | `ticket-agent-invocation-pattern.md` already stabilizes the date-prefixed ticket-context artifact, and `validate_artifact_contracts.py` already validates the context-file glob pattern. | Canonical artifact naming for a shared workflow is durable, harness-neutral contract behavior. | Broken downstream file lookup, incorrect handoff expectations, and validators or follow-on skills reading the wrong ticket artifact. | Add or update `artifact-contracts.md`, add a validator or scenario for reply-artifact naming, and review all ticket-workflow references for one canonical naming scheme. |
| Clarify companion-repo ownership and fallback behavior for `project-context.md` | The user confirmed that `al-dev-init-context` lives in harness-specific companion repos, while shared files here still route users to it without saying so. Several shared skills still depend on `project-context.md`. | `workflow-routing.md`, `al-dev-explore`, `al-dev-plan-preflight`, and `al-dev-develop` already assume `project-context.md` exists or can be created. | The shared plugin should document durable workflow intent and dependency boundaries even when the concrete implementation is harness-specific. | Dead command recommendations, unclear setup expectations, missing project bootstrap context, and drift between shared consumers and companion producers. | Add a trigger-corpus or filesystem-existence guard for routed skills, and review all shared references to `/al-dev-init-context` so they explain companion-repo ownership and the fallback path when unavailable. |

## Recommended Next Step

- Write an implementation plan: scope a narrow shared-surface fix covering freshness gating, `investigate` and `handoff` contract expansion, ticket-artifact naming alignment, and explicit companion-repo ownership plus fallback guidance for `project-context.md`.

## Out of Scope

- This assessment did not edit `profile-al-dev-shared`.
- This assessment did not regenerate projections.
- This assessment did not commit changes.
