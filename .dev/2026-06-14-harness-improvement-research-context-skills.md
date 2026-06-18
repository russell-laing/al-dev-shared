# Harness Improvement Research

## Research Question

Which other context-producing and context-maintaining skill patterns would be useful alongside `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md`?

## Scope And Method

- Components in scope: shared skills, repo-local skills, and knowledge contracts that produce durable context, maintain resumable state, or package handoff context.
- Harnesses or ecosystems compared: live `al-dev-shared` skill surface, current OpenAI Responses guidance, and the current MCP specification.
- Recency window: live repo state on 2026-06-14; external sources accessed 2026-06-14 UTC.
- Exclusions: direct implementation changes, generated projections, and non-context workflow audits.
- Method: establish live repo coverage first, then compare only against current primary sources.

## Live Repository Baseline

Current live coverage is stronger than `al-dev-ticket` alone:

- `al-dev-ticket`: durable ticket context loader with optional reply drafting and explicit artifact contract.
- `al-dev-interview`: converts raw Q&A into authoritative requirements artifacts.
- `al-dev-explore`: writes durable findings and can refresh `project-context.md`.
- `al-dev-plan-preflight`: assembles a reusable normalized context block in `.dev/preflight-context.md`.
- `al-dev-develop`: maintains a resume pack with progress, checklist, scope, and a Phase 4 handoff artifact.
- `al-dev-handoff`: packages cross-repo context into renamed source artifacts plus a continuation prompt.

Coverage status by pattern:

- context capture: complete
- context normalization for downstream consumers: complete
- resumable checkpoints: partial
- cross-repo handoff packaging: complete
- freshness or invalidation of old context: partial
- compaction or continuation summaries for very long runs: none found as a dedicated skill
- machine-readable context inventory or manifest for `.dev/` artifacts: partial

## Evidence-Backed Findings

1. The shared surface already has multiple distinct context roles, not one generic “context” skill. `artifact-contracts.md` defines ticket context, requirements, exploration findings, preflight context, plan artifacts, develop resume packs, and review handoffs as separate contracts. This argues for adding narrow context skills rather than broad “session memory” workflows.
2. The repo already knows freshness matters, but enforcement is uneven. `handoff-chain-map.md` explicitly flags stale `al-dev-explore` findings and accumulated lint artifacts as current gaps, while `compile-lint-procedure.md` already implements a freshness check for compile logs. Inference: freshness gating is a real missing capability, not a theoretical improvement.
3. Current OpenAI guidance favors deliberate state handling over ever-growing raw transcripts. The current conversation-state and GPT-5.5 guidance recommend `previous_response_id` or conversations for multi-turn state, intentional compaction for long-running agents, and preserving completed actions, assumptions, IDs, tool outcomes, blockers, and the next concrete goal during compaction.
4. Current OpenAI prompt-caching guidance favors stable prefixes and moving dynamic context later in the request. That supports skills that normalize or compact context into stable reusable blocks instead of repeatedly re-sending ad hoc large histories.
5. The current MCP spec distinguishes three context-delivery primitives that map well to maintainer workflows: resources for durable data, prompts for reusable parameterized instructions, and roots for explicit filesystem boundaries and boundary-change notifications. Inference: if this repo ever exports `.dev/` context through MCP, it should separate data artifacts from prompt templates rather than collapsing both into one server feature.

## Repository Comparison

| Pattern | External Evidence | Existing Repo Coverage | Gap | Portability |
| --- | --- | --- | --- | --- |
| Deliberate multi-turn state with explicit continuation points | OpenAI conversation-state and reasoning guidance | `al-dev-plan-preflight`, `al-dev-develop`, `workflow-resilience.md` | Good coverage for plan and develop, weaker coverage for lighter skills like explore and investigate | shared |
| Context compaction that preserves durable facts, blockers, IDs, and next action | OpenAI compaction guidance | No dedicated compaction skill; only ad hoc summaries and handoff prompts | Missing dedicated continuation-summary workflow | repo-local |
| Stable reusable prompt blocks with dynamic context appended later | OpenAI prompt caching guidance | Some structured artifacts exist, but no skill optimizes or normalizes for stable-prefix reuse | Missing explicit context normalization or trimming pass | repo-local |
| Standardized data resources with recency metadata and change signals | MCP resources spec | Artifacts exist on disk but are not exposed as machine-readable resources or manifests beyond isolated cases | Missing inventory layer for `.dev/` context artifacts | harness-specific |
| User-invoked prompt templates with arguments | MCP prompts spec | Skills already act like prompts, but durable generated context packs are not surfaced as parameterized prompt artifacts | Partial | harness-specific |
| Explicit filesystem boundary declarations and change handling | MCP roots spec | Repo relies on harness/workspace boundaries, not skill-level boundary manifests | Cross-repo handoff exists, but freshness and boundary change tracking are not explicit | repo-local |
| Freshness and invalidation gates for stale context artifacts | Repo evidence plus OpenAI state discipline | Present for compile logs; absent or partial for findings, ticket summaries, and handoff packs | High-value missing guardrail | shared |

## Candidate Patterns

1. `validate-context-freshness`
Evidence: `handoff-chain-map.md` already documents stale-findings risk, and MCP resources include `lastModified` plus change notifications while OpenAI guidance favors deliberate state handling.
Likely surface: shared skill plus shared knowledge contract.
Portability: `shared`.
Risk reduced: planning or fixing from outdated findings, ticket summaries, or handoff packs.

2. `compact-session-context`
Evidence: OpenAI now documents intentional compaction for long-running agents and specifies what must survive compaction.
Likely surface: repo-local Codex and Claude maintainer tooling first.
Portability: `repo-local`.
Risk reduced: context bloat, restart friction, and lossy human-written handoff summaries.

3. `index-context-artifacts`
Evidence: MCP resources formalize discoverable context objects with metadata, while the repo already has many `.dev/` artifacts but no unified manifest.
Likely surface: repo-local skill that writes a machine-readable `.dev/context-manifest.json` plus markdown index.
Portability: `repo-local`.
Risk reduced: downstream skills choosing the wrong file, stale resume artifacts, or hidden duplicate context packs.

4. `export-context-via-mcp`
Evidence: MCP separates resources and prompts, and this repo already has durable artifacts plus slash-command-style skills.
Likely surface: harness-specific tooling or a dedicated MCP server layer, not shared authored skill prose.
Portability: `harness-specific`.
Risk reduced: repeated file-glob logic and inconsistent context pickup across harnesses.

5. `refresh-handoff-pack`
Evidence: `al-dev-handoff` copies source artifacts well, but there is no documented revalidation pass when the source repo changes after packaging.
Likely surface: shared or repo-local skill adjacent to `al-dev-handoff`.
Portability: `repo-local`.
Risk reduced: cross-repo continuation on stale copied context.

## Rejected Or Non-Portable Patterns

- A single monolithic “memory skill” that replaces ticket, interview, explore, preflight, and handoff artifacts. Rejected because the repo’s contract matrix is intentionally artifact-specific and downstream consumers expect narrow file types.
- Treating prompt caching itself as a skill. Rejected because caching is an API or harness orchestration concern, not a shared authored workflow contract.
- Moving all `.dev/` context into shared generated agent projections. Rejected because that would mix maintainer infrastructure with the shared authored plugin surface.

## Evidence Ledger

| ID | Claim | Source | Source Type | Published or Updated | Accessed | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | `al-dev-ticket`, `al-dev-interview`, `al-dev-explore`, `al-dev-plan-preflight`, `al-dev-develop`, and `al-dev-handoff` already form a layered context workflow | local files under `profile-al-dev-shared/skills/` and `profile-al-dev-shared/knowledge/artifact-contracts.md` | live repo | live repo state | 2026-06-14 | high |
| E2 | The repo already documents stale `findings.md` and stale lint-report risks as current gaps | `profile-al-dev-shared/knowledge/handoff-chain-map.md` | live repo | live repo state | 2026-06-14 | high |
| E3 | OpenAI recommends `previous_response_id` or conversation objects for multi-turn state and explicit compaction for long-running agents | https://developers.openai.com/api/docs/guides/conversation-state and https://developers.openai.com/api/docs/guides/latest-model#using-reasoning-models | first-party docs | current docs page on access date | 2026-06-14 | high |
| E4 | OpenAI recommends stable prefixes first, dynamic context later, and consistent `prompt_cache_key` use for repeated traffic | https://developers.openai.com/api/docs/guides/latest-model#using-reasoning-models and https://developers.openai.com/cookbook/examples/prompt_caching_201 | first-party docs | current docs page on access date | 2026-06-14 | medium |
| E5 | MCP resources expose durable context objects with metadata such as `lastModified`, audience, priority, and change notifications | https://modelcontextprotocol.io/specification/2025-06-18/server/resources | primary specification | Version 2025-06-18 | 2026-06-14 | high |
| E6 | MCP prompts expose parameterized prompt templates discoverable by the client | https://modelcontextprotocol.io/specification/2025-06-18/server/prompts | primary specification | Version 2025-06-18 | 2026-06-14 | high |
| E7 | MCP roots formalize filesystem boundaries and list-change notifications | https://modelcontextprotocol.io/specification/2025-06-18/client/roots | primary specification | Version 2025-06-18 | 2026-06-14 | high |

## Gaps And Uncertainty

- I did not find a live shared `profile-al-dev-shared/skills/al-dev-init-context/SKILL.md` in this repo. After the initial draft, the user clarified that `al-dev-init-context` is intentionally owned by harness-specific companion repos such as `codex-configs/codex-al-dev` and `claude-configs/profile-claude-al-dev`. That means the shared-surface issue is dependency clarity and fallback behavior, not missing capability.
- I did not perform a broad cross-vendor crawl beyond current OpenAI docs and the current MCP specification because the repo gaps were already clear from those primary sources plus live repo evidence.
- The recommendation that freshness validation belongs in a shared skill is an inference from the shared artifact-contract surface and existing stale-artifact gaps, not a direct statement from any source.

## Recommended Next Step

run `review-improvement-reports` on this briefing
