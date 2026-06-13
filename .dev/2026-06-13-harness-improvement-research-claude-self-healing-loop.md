# Harness Improvement Research

## Research Question

How should the repo-local `.claude` self-healing loop be hardened for correctness around orchestration, resume behavior, handoff boundaries, and ledger close-back, using current external harness guidance rather than stale internal assumptions?

## Scope And Method

- In scope:
  - `.claude` self-healing loop orchestration only
  - loop-state persistence, resume semantics, delegated-work boundaries, compaction, stale-state detection, and close-back invariants
  - current Anthropic Claude Code docs and current OpenAI agent/runtime docs
- Compared ecosystems:
  - Anthropic Claude Code
  - OpenAI Agents SDK / Responses runtime guidance
- Recency window:
  - current vendor docs accessed on 2026-06-13
- Exclusions:
  - lens redesign
  - broad plugin-health quality findings
  - shared `profile-al-dev-shared` changes unless clearly justified by a harness-neutral gap
  - implementation changes; this is a research briefing only

Method:

1. Established a live repo baseline from the active `.claude` self-healing loop and related scripts/contracts.
2. Checked current Anthropic docs for memory, hooks, subagent isolation/resume, and checkpointing behavior.
3. Checked current OpenAI docs for run-state, approvals, resumable sandbox sessions, memory, compaction, and orchestration boundaries.
4. Compared only patterns that reduce correctness risk in this repo’s current `.claude` loop.

## Live Repository Baseline

Active loop surfaces reviewed:

- `.claude/skills/plugin-health-audit/SKILL.md`
- `.claude/skills/plugin-health-discover/SKILL.md`
- `.claude/skills/plugin-health-report/SKILL.md`
- `.claude/skills/record-health-dispositions/SKILL.md`
- `.claude/skills/plan-health-findings/SKILL.md`
- `.claude/skills/implement-health-plan/SKILL.md`
- `.claude/skills/revise-health-plan/SKILL.md`
- `.claude/knowledge/health-loop-state-contract.md`
- `.claude/knowledge/health-audit-preconditions.md`
- `.claude/knowledge/health-disposition-rules.md`
- `.claude/knowledge/health-filter-contract.md`
- `.claude/knowledge/health-disposition-storage-contract.md`
- `scripts/check_health_loop_handoffs.py`
- `scripts/check_ledger_staleness.py`

Current live loop status:

- `.dev/health-loop-state.md` currently says `stage_completed: implement-health-plan` and `next_command: none`.
- `python3 scripts/check_ledger_staleness.py` reports `ledger-check: 0 effective-open accepted row(s)`.

Coverage assessment:

| Concern | Existing coverage | Notes |
| --- | --- | --- |
| Loop pointer and ordered handoff | complete | Explicit contract in `.claude/knowledge/health-loop-state-contract.md` plus text in each loop skill |
| Handoff override for `plan-health-findings -> implement-health-plan` | complete | Static guard in `scripts/check_health_loop_handoffs.py` |
| Accepted-row close-back rule | complete | Explicit rule in `.claude/knowledge/health-disposition-rules.md` and implement skill |
| Stale-open accepted-row detection | complete | `scripts/check_ledger_staleness.py` plus precondition docs |
| Discovery resume semantics | partial | `--resume` exists for audit/discover only, but resumed state is artifact-based rather than richer run-state based |
| Phase-specific resumable state across the whole loop | partial | `implement-health-plan` has its own checkpoint model; the rest of the loop mostly relies on one breadcrumb file and downstream artifacts |
| Compaction/summary contract for long loop continuation | partial | `.dev/health-loop-state.md` captures next step, but not a standardized summary of completed actions, active assumptions, unresolved blockers, and next goal |
| Delegated-work state boundary | partial | Subagent usage is documented, but loop contracts do not sharply distinguish what delegated runs must reload versus what they may assume from parent context |

## Evidence-Backed Findings

1. External harnesses separate control-plane run state from workspace or memory state, and the separation is explicit rather than implied.
   Anthropic distinguishes auto memory, CLAUDE.md, subagent context, and session checkpoints. OpenAI separates harness-side `RunState` from sandbox session state and snapshots. The current `.claude` loop partly mirrors this with a breadcrumb, ledger, and one implement checkpoint, but the boundary is not modeled as a first-class contract across the whole loop.

2. Robust resume behavior is defined as resuming the same paused workflow state, not merely knowing the nominal next command.
   OpenAI approval flows resume from saved `state`, and Anthropic subagents resume by instance rather than by reconstructing from a prompt. In this repo, `implement-health-plan` has explicit restart and mismatch guards, but earlier loop stages mostly reconstruct progress from artifacts and a single `next_command` pointer.

3. Long-running workflows need an intentional compaction payload that preserves decision-relevant facts, not just a generic summary.
   OpenAI explicitly recommends preserving completed actions, assumptions, IDs, tool outcomes, unresolved blockers, and the next concrete goal during compaction. Anthropic’s checkpointing also distinguishes restore versus summarize. The current `.dev/health-loop-state.md` schema is intentionally small, but it is too thin to act as the only compacted state surface for complex interrupted loops. This is an inference from the vendor guidance and the repo’s current schema.

4. Hook systems are positioned as enforcement and pause points, not only observability.
   Anthropic hooks can allow, deny, ask, or defer tool calls, and can run asynchronously in the background. The current self-healing loop primarily relies on prose contracts plus explicit script checks. That works, but it leaves some invariants enforceable only when the right skill text is followed. A hook-backed guard layer is a plausible correctness improvement for loop transitions or stale-state detection.

5. Delegated workers should begin with explicit, limited context, and resume should preserve their exact state when continuation matters.
   Anthropic documents that subagents start in fresh, isolated context windows and only resumed subagents retain prior tool history and reasoning. This aligns with the repo’s caution around fresh-session boundaries and subagent-driven execution, but the self-healing loop docs do not yet spell out a standard “state handoff payload” for delegated self-heal work.

6. Checkpointing or memory alone is not enough for auditable recovery when shell or external file changes matter.
   Anthropic checkpointing does not track bash-modified or external changes, and Anthropic’s memory docs explicitly describe memory as context rather than an enforced control surface. This supports the repo’s current decision to keep ledger and close-back state in explicit files, and argues against replacing loop artifacts with auto memory or chat-only recovery.

## Repository Comparison

| Pattern | External Evidence | Existing Repo Coverage | Gap | Portability |
| --- | --- | --- | --- | --- |
| Separate orchestration state from workspace state | OpenAI sandbox docs split harness/run state from sandbox session state; Anthropic splits memory, checkpoints, and session context | Breadcrumb, ledger, and implement checkpoint exist | No single repo-local contract explains which artifact is authoritative for which class of state | repo-local |
| Resume same paused run, not just next step text | OpenAI approvals resume from `state`; Anthropic resumed subagents retain prior tool history | `implement-health-plan` has strong resume guards; earlier steps mostly do not | Loop stages before implementation lack richer resumable state semantics | repo-local |
| Compact long workflows with preserved actions, blockers, IDs, next goal | OpenAI compaction guidance is explicit; Anthropic checkpointing supports summarize vs restore | Breadcrumb has `note` and `next_inputs` | No standard compacted-state payload for mid-loop continuation | repo-local |
| Enforce risky transitions with hooks or approval controls | Anthropic hook system supports allow/deny/ask/defer and async execution | Current loop uses prose plus scripts run by skills | Some invariants depend on correct manual skill execution rather than background enforcement | harness-specific |
| Keep delegated workers isolated; resume exact worker when needed | Anthropic subagents start fresh and resumed instances preserve history | Subagent use is already constrained in several skills | Loop docs do not define a reusable delegated-state handoff contract | repo-local |
| Treat memory as assistive context, not authoritative workflow state | Anthropic memory docs say memory is context; OpenAI sandbox memory is separate from session/run state | Repo already uses explicit files for ledger and loop close-back | No gap; current direction is consistent | reject |

## Candidate Patterns

1. Add a repo-local “self-heal control-plane state” contract that explicitly separates:
   - loop breadcrumb
   - phase-specific resumable checkpoint
   - auditable ledger/disposition state
   - optional compacted narrative summary
   Evidence: OpenAI’s explicit `RunState` vs sandbox/session/snapshot split, plus Anthropic’s separate memory/checkpoint/subagent state surfaces.
   Likely surface: `.claude/knowledge/` and the active `.claude` self-healing skills.
   Portability: `repo-local`.
   Risk reduced: ambiguous recovery after interruption or fresh session.

2. Expand loop continuation state beyond `next_command` by standardizing a compacted payload for:
   - completed stage(s)
   - accepted IDs or rows in scope
   - unresolved blockers
   - exact next invariant to verify
   - restart boundary reason, when present
   Evidence: OpenAI compaction guidance and Anthropic summarize-vs-restore checkpoint semantics.
   Likely surface: `.claude/knowledge/health-loop-state-contract.md` and loop-writing skills.
   Portability: `repo-local`.
   Risk reduced: wrong resumption after compaction, context loss, or session handoff.

3. Introduce hook-backed correctness gates for one or two narrow loop invariants instead of relying only on skill prose.
   Best candidates are:
   - blocking or warning on a fresh sweep when a later loop step is still in flight
   - surfacing stale-open accepted rows at a tool boundary before a new audit/report step proceeds
   Evidence: Anthropic hook decision control and async hooks.
   Likely surface: `.claude/hooks/` plus loop docs.
   Portability: `harness-specific`.
   Risk reduced: human/operator drift from the intended loop order.

4. Define a standard delegated-work handoff payload for self-heal subagent execution.
   Include the exact files, accepted IDs, active filter provenance, and “must re-read” artifacts rather than assuming parent-session context survives delegation.
   Evidence: Anthropic subagent isolation/resume rules.
   Likely surface: `.claude/knowledge/` and any loop skill that dispatches delegated execution.
   Portability: `repo-local`.
   Risk reduced: subagent decisions made from incomplete or reconstructed context.

5. Document that checkpointing and memory are supportive only, and cannot replace explicit close-back artifacts when shell or external changes matter.
   Evidence: Anthropic checkpointing limits and memory semantics.
   Likely surface: `.claude/knowledge/` self-healing docs.
   Portability: `repo-local`.
   Risk reduced: false confidence in replay/recovery mechanisms that do not capture all relevant state.

## Rejected Or Non-Portable Patterns

1. Replace the ledger or loop breadcrumb with Claude auto memory.
   Rejected. Anthropic documents memory as contextual guidance, not an enforced control surface, and the repo needs auditable close-back state.

2. Replace repo-local loop state with provider-managed sandbox sessions or snapshots.
   Rejected for current scope. OpenAI’s sandbox session model is useful for hosted or application-owned runtimes, but it is heavier than this repo needs for a local `.claude` self-heal loop.

3. Treat Claude checkpointing as sufficient recovery for self-heal implementation work.
   Rejected. Anthropic explicitly notes that bash command changes and external changes are not fully tracked.

4. Promote the candidate patterns directly into shared `profile-al-dev-shared`.
   Rejected for now. The researched gaps are specific to the repo-local `.claude` self-heal loop and its harness-native execution model.

## Evidence Ledger

| ID | Claim | Source | Source Type | Published or Updated | Accessed | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | Claude memory and CLAUDE.md both load every session, but memory is contextual and hooks are the hard block for actions | https://code.claude.com/docs/en/memory | first-party vendor docs | not stated | 2026-06-13 | high |
| E2 | Claude hooks can control tool calls, including allow/deny/ask/defer, and defer is meant for paused non-interactive continuation | https://code.claude.com/docs/en/hooks | first-party vendor docs | not stated | 2026-06-13 | high |
| E3 | Claude subagents start fresh and isolated by default; resumed subagents retain prior history and tool results | https://code.claude.com/docs/en/sub-agents | first-party vendor docs | not stated | 2026-06-13 | high |
| E4 | Claude checkpoints persist across sessions, but bash and external changes are not fully tracked | https://code.claude.com/docs/en/checkpointing | first-party vendor docs | not stated | 2026-06-13 | high |
| E5 | OpenAI recommends explicit state handling for long-running agents, including `previous_response_id`, `phase`, compaction, tool preambles, and preserving completed actions and blockers | https://developers.openai.com/api/docs/guides/latest-model | first-party vendor docs | not stated | 2026-06-13 | high |
| E6 | OpenAI Agents SDK positions results and state as the resumable continuation surface for paused runs | https://developers.openai.com/api/docs/guides/agents/results | first-party vendor docs | not stated | 2026-06-13 | high |
| E7 | OpenAI approvals pause the run and resume the same run from saved state instead of starting a new user turn | https://developers.openai.com/api/docs/guides/agents/guardrails-approvals | first-party vendor docs | not stated | 2026-06-13 | high |
| E8 | OpenAI sandbox agents explicitly separate harness-side run state from sandbox session state, snapshots, and memory | https://developers.openai.com/api/docs/guides/agents/sandboxes | first-party vendor docs | not stated | 2026-06-13 | high |

## Gaps And Uncertainty

- Anthropic’s public docs describe hooks, subagents, checkpointing, and memory clearly, but they do not publish a single first-party “workflow state contract” equivalent to the repo’s self-healing loop. Some cross-surface conclusions here are inference.
- OpenAI’s sandbox/session model targets SDK-owned applications, not local CLI loop skills. The relevance is architectural rather than one-to-one operational.
- I did not find evidence that the current candidate patterns should move into shared `profile-al-dev-shared`; that remains unproven.
- I did not test any live hook or resume flow here; this briefing is based on live repo inspection plus current documentation, not a runtime experiment.

## Recommended Next Step

run `review-improvement-reports` on this briefing
