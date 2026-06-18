# Harness Improvement Research

## Research Question

How should `al-dev-shared` respond to the finding in
`/Users/russelllaing/.claude/usage-data/report.html` that the main recurring
friction is phantom execution, dispatch fragility, and subagent scope creep in
maintainer workflows?

## Scope And Method

- In scope: workflow contracts for phase verification, dispatch fallback,
  delegated-task scope control, and continuation or compaction aids relevant to
  this repository's maintainer workflows.
- Compared ecosystems: the local Claude usage report, live repo behavior in
  `al-dev-shared`, current OpenAI first-party guidance, and recent research on
  agentic coding configuration and recursive agent harnesses.
- Recency window: current sources accessed on 2026-06-15; research papers from
  2025-09-18, 2026-02-16, and 2026-06-11.
- Exclusions: no shared-surface edits, no generated-artifact edits, no broad
  harness audit outside the report's execution-fidelity finding, and no attempt
  to turn Claude-specific tool failures into shared harness-neutral rules
  without a durable underlying pattern.

## Live Repository Baseline

Coverage after live repo inspection:

- Phase checkpoints and resumability: `complete`
  - `profile-al-dev-shared/knowledge/workflow-resilience.md`
  - `.claude/knowledge/health-loop-state-contract.md`
- Durable artifact and read-after-write verification: `partial to complete`
  - `profile-al-dev-shared/knowledge/artifact-contracts.md`
  - `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`
  - `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`
- Delegated-task scope control: `partial`
  - `profile-al-dev-shared/knowledge/scope-expansion-gate.md`
  - `profile-al-dev-shared/knowledge/al-dev-develop-spawn-prompt.md`
  - strong in shared AL workflows, not consistently surfaced in repo-local
    maintainer execution lanes
- Dispatch fallback behavior: `partial`
  - `profile-al-dev-shared/knowledge/workflow-resilience.md` handles empty
    output and usage-limit fallback
  - no uniform preflight or automatic fallback contract for schema failures,
    permission failures, or wrong-dispatch tool choice in maintainer workflows
- Continuation and context carry-forward: `complete for artifact-based flows`
  - `profile-al-dev-shared/skills/al-dev-handoff/SKILL.md`
  - `.dev/progress.md` contract
  - `.dev/health-loop-state.md` breadcrumb pattern
  - no named "compaction" feature, but artifact-backed continuation already
    serves the same operational purpose for many repo workflows

## Evidence-Backed Findings

1. The local report's strongest concrete finding is not "missing workflow
   structure"; it is that some workflows report progress before execution is
   proven. The report explicitly recommends a "prove it ran" gate using file
   existence or command output and repeats that recommendation in its friction,
   feature, and horizon sections.
2. The live repo already contains several strong verification primitives, so a
   generic "add verification" recommendation would be duplicate. The narrower
   gap is phase-level proof in maintainer health or execution wrappers, where a
   workflow may have a final artifact contract but still lack a mandatory
   mid-phase proof block before progress is reported.
3. The report's RemoteTrigger failure is real but not portable as written.
   The reusable lesson is not "ban RemoteTrigger everywhere"; it is "dispatch
   lanes need deterministic preflight and fallback behavior when the preferred
   delegation mechanism fails."
4. Subagent scope creep is already recognized in shared knowledge via the
   scope-expansion gate, but the report suggests the repo still needs more
   executable scope packaging for delegated plan execution, especially explicit
   do-not-touch constraints and post-task diff sanity checks.
5. Current external guidance and recent research align on four durable patterns:
   structured tool execution, evaluation loops, persistent continuation state,
   and explicit orchestration for delegated agents. That supports tightening
   repo contracts around proof, fallback, and scope. It does not yet justify a
   jump to unattended self-healing orchestration as the next move.

## Repository Comparison

| Pattern | External Evidence | Existing Repo Coverage | Gap | Portability |
| --- | --- | --- | --- | --- |
| Phase-level proof-of-execution before reporting progress | OpenAI's AI-native engineering guide emphasizes structured tool execution, evaluation loops, and explicitly checking whether agent-run commands succeeded. The local report recommends a "prove it ran" gate with file existence and command output. | Final artifact contracts and several read-after-write checks already exist. Health and maintainer workflows have evidence gates, but not a uniform phase-proof contract. | Narrow but real: mid-phase status can still be weaker than end-of-run verification. | repo-local |
| Deterministic dispatch preflight and fallback | OpenAI tools and orchestration guidance treats tool use, handoffs, guardrails, and structured outputs as first-class workflow design. The local report shows repeated wasted cycles from failed dispatch attempts before falling back manually. | `workflow-resilience.md` covers some subagent failure fallback after execution starts. No shared repo-local wrapper standardizes input preflight plus fallback path selection for maintainer flows. | Missing wrapper-level contract for "preferred path failed, now do X and log it." | repo-local |
| Explicit delegated-task scope packs | Recent configuration studies show advanced skills and subagents remain shallowly adopted, which makes explicit workflow constraints more important. The local report shows extra rows, validator edits, and partial renames slipping through. | Shared AL workflows already have `scope-expansion-gate.md` and developer spawn guidance. Repo-local maintainer execution surfaces do not consistently package a do-not-touch boundary with each delegated task. | Partial propagation gap, not a conceptual gap. | shared |
| Compaction or continuation summaries for long-running work | OpenAI documents compaction as summarizing older context so long-running work can continue, and its reliability cookbook frames compaction plus memory as a way to preserve state while keeping a human-reviewed memo as source of truth. | This repo already externalizes most long-running state into `.dev/` artifacts, health breadcrumbs, and handoff files. | Small gap at most; the artifact-based continuation model already covers the main need. | reject |
| Recursive or unattended orchestrator harnesses | The Recursive Agent Harnesses paper shows gains from explicit harness recursion, and the report imagines nightly discover-to-fixed loops. | The repo already has loop breadcrumbs and worktree-oriented execution skills, but correctness and boundedness are still more important than more autonomy here. | Too early; correctness gates should tighten before orchestration expands. | reject |

## Candidate Patterns

| Pattern | Evidence | Likely Surface | Portability | Risk Reduced |
| --- | --- | --- | --- | --- |
| Add a repo-local phase-proof contract for maintainer health and execution workflows | The local report repeatedly highlights phantom execution; OpenAI guidance reinforces executable evaluation loops and checking real command success. | `.codex/skills/*` and `.claude/skills/*` maintainer workflows that currently report multi-phase progress | repo-local | Premature "phase complete" claims and invisible no-op runs |
| Add a repo-local dispatch wrapper or dispatch policy note that logs preferred path, fallback path, and reason | The local report shows repeated failed dispatch attempts before a manual pivot; external orchestration guidance favors explicit handoffs and structured tool ownership. | repo-local maintainer tooling under `.codex/skills/` and `.claude/knowledge/` | repo-local | Repeated retry loops, slow pivots, and ambiguous execution state |
| Generalize the existing shared scope gate into an explicit delegated-task scope pack pattern | The report's scope-creep examples map directly to the risk already named in `scope-expansion-gate.md`. The gap is propagation and enforcement shape, not policy intent. | `profile-al-dev-shared/knowledge/` plus shared delegated-agent prompt patterns | shared | Extra ledger writes, validator drift, partial renames, and hidden out-of-scope edits |

## Rejected Or Non-Portable Patterns

- Reject: "Standardize on the Agent tool" as a shared recommendation.
  - This is a Claude-side local tool-failure workaround, not a harness-neutral
    workflow rule.
- Reject: adding a new shared compaction feature as an immediate priority.
  - The repo already persists continuation state into `.dev/` artifacts and
    breadcrumbs, which is the more auditable fit for these workflows.
- Reject: unattended end-to-end self-healing orchestration as the next step.
  - The current evidence points to tightening correctness gates first, not
    increasing autonomy.

## Evidence Ledger

| ID | Claim | Source | Source Type | Published or Updated | Accessed | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | The dominant local friction is phantom execution, dispatch fragility, and scope creep; the report recommends a "prove it ran" gate and explicit subagent boundaries. | `/Users/russelllaing/.claude/usage-data/report.html` | local artifact | report window 2026-05-15 to 2026-06-14 | 2026-06-15 | high |
| E2 | Durable coding-agent workflows benefit from structured tool execution, persistent memory, evaluation loops, and explicit checking that commands succeed. | https://developers.openai.com/codex/guides/build-ai-native-engineering-team | first-party documentation | undated page | 2026-06-15 | high |
| E3 | Agent workflows should model tools, specialist handoffs, guardrails, and ownership explicitly instead of hiding them in one prompt. | https://developers.openai.com/api/docs/guides/tools | first-party documentation | undated page | 2026-06-15 | high |
| E4 | OpenAI documents compaction as a first-class way to summarize older context for long-running work, and its reliability guidance pairs compaction with memory while keeping a human-reviewed memo as source of truth. | https://developers.openai.com/api/docs/guides/conversation-state#compaction and https://developers.openai.com/cookbook/examples/agents_sdk/building_reliable_agents_memory_compaction | first-party documentation | undated pages | 2026-06-15 | medium |
| E5 | Across 2,926 repositories, context files dominate and advanced skills or subagents are still shallowly adopted; explicit workflow constraints remain valuable because most skill systems are still instruction-heavy. | https://arxiv.org/abs/2602.14690 | original research paper | 2026-02-16 | 2026-06-15 | medium |
| E6 | AGENTS-style manifest files tend to concentrate operational commands, technical notes, and architecture in shallow structures, reinforcing the need for precise, executable operational guidance rather than broad prose alone. | https://arxiv.org/abs/2509.14744 | original research paper | 2025-09-18 | 2026-06-15 | medium |
| E7 | Recursive harness designs can improve long-context delegated coding performance, but they are harness-level orchestration advances rather than evidence that a given repo should immediately automate more. | https://arxiv.org/abs/2606.13643 | original research paper | 2026-06-11 | 2026-06-15 | medium |

## Gaps And Uncertainty

- I did not find a current official Anthropic documentation page during this
  run that was more relevant than the local report plus live repo evidence, so
  the first-party external evidence here is OpenAI-heavy.
- The local report is about Claude-side maintainer behavior, not the shared
  plugin alone, so the strongest candidates skew repo-local rather than shared.
- The compaction recommendation is an inference from OpenAI guidance plus the
  repo's existing breadcrumb artifacts; it is not a direct statement that this
  repo should add a new compaction feature.
- The recursive-harness evidence is useful for horizon scanning, but it does
  not by itself justify a near-term implementation change in this repository.

## Recommended Next Step

run `review-improvement-reports` on this briefing
