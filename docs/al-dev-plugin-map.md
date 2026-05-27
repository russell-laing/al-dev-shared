# AL Dev Plugin Map

> A reference tool for understanding skill relationships, agent patterns, and file handoffs in profile-al-dev-shared. This document is for personal gap analysis and extension planning, not onboarding.

**Last updated:** 2026-05-27 (18 distributed skills: 17 primary + 1 deprecated alias skill, `/al-dev-ticket` exposes `--mode=context-only|full`, 5-lens strategic analysis maintained)
**Scope:** Active skills only. Archived items (al-dev-test, test-engineer agents, al-dev-test-coverage-reviewer, al-dev-align, plugin-health-daemon) excluded. `/align-harness-repos` and `/plugin-health-daemon` are project-local maintenance tools in `.claude/skills/`, not distributed in the plugin.

---

## Layer 1: Lifecycle Overview

This diagram shows pre-planning tributaries (dashed, optional), the three main entry points, and the development spine through to post-commit output.

```mermaid
flowchart TD
    %% Pre-planning tributaries (optional)
    Explore("al-dev-explore") -.->|.dev/*-al-dev-explore-findings.md| Investigate
    Explore -.->|.dev/*-al-dev-explore-findings.md| Plan
    Interview("al-dev-interview") -.->|.dev/*-al-dev-interview-requirements.md| Plan
    Perf("al-dev-perf") -.->|.dev/*-al-dev-perf-perf-analysis.md| Plan
    Perf -.->|.dev/*-al-dev-perf-perf-analysis.md| FixDirect

    %% Entry points
    Ticket("al-dev-ticket<br/>(--mode=context-only|full)")
    Investigate("al-dev-investigate")
    FixDirect("al-dev-fix") -->|AL code| Commit("al-dev-commit")

    %% Investigation path branches
    Investigate -->|.dev/*-al-dev-investigate-findings.md| Decision1{Needs<br/>full plan?}
    Decision1 -->|Yes| Plan("al-dev-plan")
    Decision1 -->|No| FixDirect

    %% Main development spine
    Plan -->|.dev/*-al-dev-plan-solution-plan.md| Develop("al-dev-develop")
    Develop -->|.dev/*-phase4-handoff| ReviewDevelop("al-dev-review-develop")
    ReviewDevelop -->|.dev/*-al-dev-develop-code-review.md| Commit

    %% Lint feedback loop
    Develop -.->|optional compile cleanup| Lint("al-dev-lint")
    Lint -.->|.dev/*-al-dev-lint-lint-report.md| FixDirect

    %% Complexity gate within plan
    Note["Trivial requests<br/>route to /fix"] -.-> Plan

    %% Outputs
    Commit --> Git(["✓ git commit"])
    Git -.-> ReleaseNotes("al-dev-release-notes")
    ReleaseNotes --> Notes(["✓ release notes"])
    Git -.-> Handoff("al-dev-handoff")
    Handoff --> HandoffOut(["✓ .dev/*-al-dev-handoff-handoff-prompt.md"])
    Git -.->|on integrity error| Recover("commit-recover")
    Recover --> RecoverOut(["✓ recovered files"])
    Git -.-> Document("al-dev-document")
    Document --> DocOut(["✓ documentation"])
    Ticket -.->|--mode=full| Reply(["✓ customer reply"])

    style Ticket fill:#e1f5ff
    style Investigate fill:#f3e5f5
    style Explore fill:#f3e5f5
    style Interview fill:#e8f5e9
    style Plan fill:#fff3e0
    style Develop fill:#fff3e0
    style ReviewDevelop fill:#ff8a65
    style FixDirect fill:#e8f5e9
    style Commit fill:#e8f5e9
    style Git fill:#c8e6c9
    style Notes fill:#c8e6c9
    style Reply fill:#c8e6c9
    style ReleaseNotes fill:#e3f2fd
    style Perf fill:#fce4ec
    style Lint fill:#e0f2f1
    style Handoff fill:#fff3e0
    style HandoffOut fill:#c8e6c9
    style Recover fill:#e0f2f1
    style RecoverOut fill:#c8e6c9
    style Document fill:#e3f2fd
    style DocOut fill:#c8e6c9
    style Decision1 fill:#ffe0b2
```

---

## Layer 2: Per-Skill Drill-Downs

Each skill is shown with its internal phases, spawned agents, and key outputs. Agents are referenced by their full type name (e.g., `al-dev-shared:al-dev-developer`).

### Notation

- **Phase**: Numbered step inside the skill
- **Agent**: Which agent (or skill itself) executes the phase
- **Pattern**: ×1 (serial), ×2-3 (parallel), ×N (variable count)
- **Output**: File written to `.dev/` or code generated

### /al-dev-ticket

**Two modes:** `--mode=context-only` (default fetch/context only) and `--mode=full` (fetch + research + reply drafting). `/al-dev-support` remains as a deprecated alias that points users to `--mode=full`.

```mermaid
flowchart LR
    Start([Start]) --> Decision{Mode?}
    
    Decision -->|context-only| Phase1F["Phase 1<br/>Fetch ticket"]
    Phase1F --> Agent1F["al-dev-ticket-agent ×1"]
    Agent1F --> Output1F([".dev/*-al-dev-ticket-ticket-context.md"])
    
    Decision -->|full| Phase1S["Phase 1<br/>Fetch ticket"]
    Phase1S --> Agent1S["al-dev-ticket-agent ×1"]
    Agent1S --> Phase2S["Phase 2<br/>Research"]
    Phase2S --> Agent2S["al-dev-support-researcher ×1"]
    Agent2S --> Phase3S["Phase 3<br/>Draft reply"]
    Phase3S --> Agent3S["al-dev-support-reply-drafter ×1"]
    Agent3S --> Output1S(["customer reply"])

    Output1F --> End([End])
    Output1S --> End

    style Decision fill:#fff9c4
    style Phase1F fill:#e3f2fd
    style Phase1S fill:#e3f2fd
    style Agent1F fill:#bbdefb
    style Agent1S fill:#bbdefb
    style Agent2S fill:#bbdefb
    style Agent3S fill:#bbdefb
    style Output1F fill:#90caf9
    style Output1S fill:#90caf9
```

### /al-dev-investigate

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Form hypotheses"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Test hypotheses"]
    Phase2 --> Agent1["Explore subagent<br/>×1–2 (by hypothesis count)"]
    Agent1 --> Phase3["Phase 3<br/>Synthesise findings"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1([".dev/*-al-dev-investigate-findings.md"])
    Output1 --> End([End])

    style Phase1 fill:#f3e5f5
    style Phase2 fill:#f3e5f5
    style Phase3 fill:#f3e5f5
    style SkillWork1 fill:#e1bee7
    style SkillWork2 fill:#e1bee7
    style Agent1 fill:#ce93d8
    style Output1 fill:#ba68c8
```

### /al-dev-fix

**Complexity routing:** Trivial fixes skip the analysis phase; complex fixes route through al-dev-solution-architect.

```mermaid
flowchart LR
    Start([Start]) --> Decision{Complex?}

    Decision -->|Trivial| Phase1T["Phase 1<br/>Implement"]
    Phase1T --> DevAgent["al-dev-developer ×1"]
    DevAgent --> Phase2T["Phase 2<br/>Compile + lint"]
    Phase2T --> SkillT["(skill itself)"]
    SkillT --> End([End])

    Decision -->|Non-trivial| Phase1C["Phase 1<br/>Analyse"]
    Phase1C --> ArchAgent["al-dev-solution-architect<br/>×1 (5 min)"]
    ArchAgent --> Phase2C["Phase 2<br/>Implement"]
    Phase2C --> DevAgent2["al-dev-developer ×1"]
    DevAgent2 --> Phase3C["Phase 3<br/>Compile + lint"]
    Phase3C --> SkillC["(skill itself)"]
    SkillC --> End

    style Decision fill:#fff9c4
    style Phase1T fill:#e8f5e9
    style Phase1C fill:#e8f5e9
    style Phase2T fill:#e8f5e9
    style Phase2C fill:#e8f5e9
    style Phase3C fill:#e8f5e9
    style DevAgent fill:#81c784
    style DevAgent2 fill:#81c784
    style ArchAgent fill:#66bb6a
    style SkillT fill:#4caf50
    style SkillC fill:#4caf50
```

### /al-dev-plan

**Competitive design phase:** Multiple architects propose approaches in parallel; the skill synthesises the winner into a solution plan.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Context gather"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Competing designs"]
    Phase2 --> ArchAgents["al-dev-solution-architect<br/>×2-3 parallel"]
    ArchAgents --> Phase3["Phase 3<br/>Synthesise winner"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1([".dev/*-al-dev-plan-solution-plan.md"])
    Output1 --> End([End])

    style Phase1 fill:#fff3e0
    style Phase2 fill:#fff3e0
    style Phase3 fill:#fff3e0
    style SkillWork1 fill:#ffe0b2
    style SkillWork2 fill:#ffe0b2
    style ArchAgents fill:#ffcc80
    style Output1 fill:#ffb74d
```

### /al-dev-develop

**Pre-implementation orchestration:** Reads solution plan, validates scope, partitions work across developers, and dispatches parallel developers. Passes Phase 4 handoff to `/al-dev-review-develop` for compilation, review, and code-review output.

```mermaid
flowchart LR
    Start([Start]) --> Phase0["Phase 0<br/>Resume check"]
    Phase0 --> Phase1["Phase 1<br/>Read plan"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Partition work"]
    Phase2 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Phase3["Phase 3<br/>Spawn developers"]
    Phase3 --> DevAgent["al-dev-developer ×1-4<br/>(scaled by object count)"]
    DevAgent --> Phase4["Phase 4<br/>Verify completion<br/>+ optional static validation"]
    Phase4 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Handoff(["Phase 4 handoff<br/>(.dev/*-phase4-handoff.md)"])
    Handoff --> ReviewDevelop["→ /al-dev-review-develop<br/>(compilation, review, code review)"]
    ReviewDevelop --> End([End])

    style Phase0 fill:#fff8e1
    style Phase1 fill:#fff8e1
    style Phase2 fill:#fff8e1
    style Phase3 fill:#fff8e1
    style Phase4 fill:#fff8e1
    style SkillWork1 fill:#ffe082
    style SkillWork2 fill:#ffe082
    style SkillWork3 fill:#ffe082
    style DevAgent fill:#ffd54f
    style Handoff fill:#ffb74d
    style ReviewDevelop fill:#ff8a65
```

### /al-dev-review-develop

**Post-implementation review orchestration:** Consumes Phase 4 handoff from `/al-dev-develop`. Runs compilation verification, dispatches three-specialist review panel in parallel, synthesizes findings, and writes code-review artifact.

```mermaid
flowchart LR
    Start([Handoff<br/>Phase 4]) --> Phase5["Phase 5<br/>Prepare review"]
    Phase5 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase6["Phase 6<br/>Compile<br/>+ staging"]
    Phase6 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Phase7["Phase 7<br/>Review panel<br/>in parallel"]

    Phase7 --> SecReview["al-dev-security-reviewer<br/>×1"]
    Phase7 --> ExpertReview["al-dev-expert-reviewer<br/>×1"]
    Phase7 --> PerfReview["al-dev-performance-reviewer<br/>×1"]

    SecReview --> Phase8["Phase 8<br/>Synthesise<br/>+ iterate fixes"]
    ExpertReview --> Phase8
    PerfReview --> Phase8

    Phase8 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Phase9["Phase 9<br/>Write code review"]
    Phase9 --> SkillWork4["(skill itself)"]
    SkillWork4 --> Output1([".dev/*-al-dev-develop-code-review.md"])
    Output1 --> End([End])

    style Phase5 fill:#ff8a65
    style Phase6 fill:#ff8a65
    style Phase7 fill:#ff8a65
    style Phase8 fill:#ff8a65
    style Phase9 fill:#ff8a65
    style SkillWork1 fill:#ff7043
    style SkillWork2 fill:#ff7043
    style SkillWork3 fill:#ff7043
    style SkillWork4 fill:#ff7043
    style SecReview fill:#ff5722
    style ExpertReview fill:#ff5722
    style PerfReview fill:#ff5722
    style Output1 fill:#d84315
```

### /al-dev-commit

**Two-pass execution:** Analysis pass builds manifests and proposes commit groups; message-drafting pass creates commit messages; execution pass runs the commits with hook support. Three agents with focused responsibilities.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Analysis pass"]
    Phase1 --> Agent1["al-dev-commit-agent-analysis ×1<br/>(manifest only)"]
    Agent1 --> Interim1["(per-file manifests<br/>+ group proposals)"]
    Interim1 --> Phase2["Phase 2<br/>Message drafting"]
    Phase2 --> Agent2["al-dev-commit-message-drafter ×1"]
    Agent2 --> Interim2["(commit messages)"]
    Interim2 --> Phase3["Phase 3<br/>Execution pass"]
    Phase3 --> Agent3["al-dev-commit-agent-execute ×1<br/>(sonnet)"]
    Agent3 --> Output1(["(git commits)"])
    Output1 --> End([End])

    style Phase1 fill:#e0f2f1
    style Phase2 fill:#e0f2f1
    style Phase3 fill:#e0f2f1
    style Agent1 fill:#80cbc4
    style Agent2 fill:#4db8a8
    style Agent3 fill:#80cbc4
    style Output1 fill:#26a69a
```

### /al-dev-explore

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Step 1<br/>Load context"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Step 2<br/>Explore"]
    Phase2 --> Agent1["Explore subagent ×1"]
    Agent1 --> Phase3["Step 3<br/>Write findings"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1([".dev/*-al-dev-explore-findings.md"])
    Output1 --> End([End])

    style Phase1 fill:#f3e5f5
    style Phase2 fill:#f3e5f5
    style Phase3 fill:#f3e5f5
    style SkillWork1 fill:#e1bee7
    style SkillWork2 fill:#e1bee7
    style Agent1 fill:#ce93d8
    style Output1 fill:#ba68c8
```

### /al-dev-interview

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Pre-research"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Interview"]
    Phase2 --> Agent1["al-dev-interview ×1"]
    Agent1 --> Phase3["Phase 3<br/>Write requirements"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1([".dev/*-al-dev-interview-requirements.md"])
    Output1 --> End([End])

    style Phase1 fill:#e8f5e9
    style Phase2 fill:#e8f5e9
    style Phase3 fill:#e8f5e9
    style SkillWork1 fill:#c8e6c9
    style SkillWork2 fill:#c8e6c9
    style Agent1 fill:#a5d6a7
    style Output1 fill:#81c784
```

### /al-dev-lint

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Step 1<br/>Compile"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Step 2<br/>Fix diagnostics"]
    Phase2 --> Agent1["al-dev-diagnostics-fixer ×1"]
    Agent1 --> Phase3["Step 3<br/>Present summary"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1([".dev/*-al-dev-lint-lint-report.md"])
    Output1 --> End([End])

    style Phase1 fill:#e0f2f1
    style Phase2 fill:#e0f2f1
    style Phase3 fill:#e0f2f1
    style SkillWork1 fill:#b2dfdb
    style SkillWork2 fill:#b2dfdb
    style Agent1 fill:#80cbc4
    style Output1 fill:#26a69a
```

### /al-dev-document

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Step 1<br/>Select scope"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Step 2<br/>Write docs"]
    Phase2 --> Agent1["al-dev-docs-writer ×1"]
    Agent1 --> Phase3["Step 3<br/>Review + refine"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1(["documentation files"])
    Output1 --> End([End])

    style Phase1 fill:#e3f2fd
    style Phase2 fill:#e3f2fd
    style Phase3 fill:#e3f2fd
    style SkillWork1 fill:#bbdefb
    style SkillWork2 fill:#bbdefb
    style Agent1 fill:#90caf9
    style Output1 fill:#64b5f6
```

### /al-dev-release-notes

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Parse args"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Generate notes"]
    Phase2 --> Agent1["al-dev-release-notes-writer ×1"]
    Agent1 --> Output1([".dev/YYYY-MM-DD-[app-id]-al-dev-release-notes-[short-hash].md"])
    Output1 --> End([End])

    style Phase1 fill:#e3f2fd
    style Phase2 fill:#e3f2fd
    style SkillWork1 fill:#bbdefb
    style Agent1 fill:#90caf9
    style Output1 fill:#64b5f6
```

### /al-dev-perf

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Step 1<br/>Determine scope"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Step 2<br/>Analyse"]
    Phase2 --> Agent1["Explore subagent ×1"]
    Agent1 --> Phase3["Step 3<br/>Write report"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1([".dev/*-al-dev-perf-perf-analysis.md"])
    Output1 --> End([End])

    style Phase1 fill:#fce4ec
    style Phase2 fill:#fce4ec
    style Phase3 fill:#fce4ec
    style SkillWork1 fill:#f8bbd0
    style SkillWork2 fill:#f8bbd0
    style Agent1 fill:#f48fb1
    style Output1 fill:#f06292
```

### /al-dev-handoff

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Step 1<br/>Identify target"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Step 2<br/>Copy context files"]
    Phase2 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Phase3["Step 3<br/>Write prompt"]
    Phase3 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Output1(["handoff-prompt.md"])
    Output1 --> End([End])

    style Phase1 fill:#fff3e0
    style Phase2 fill:#fff3e0
    style Phase3 fill:#fff3e0
    style SkillWork1 fill:#ffe0b2
    style SkillWork2 fill:#ffe0b2
    style SkillWork3 fill:#ffe0b2
    style Output1 fill:#ffb74d
```

### /al-dev-help

No agents spawned; no `.dev/` output. The skill reads available context files and presents contextual guidance inline.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Step 1<br/>Detect mode"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Step 2<br/>Show guidance"]
    Phase2 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1(["contextual guidance"])
    Output1 --> End([End])

    style Phase1 fill:#e8eaf6
    style Phase2 fill:#e8eaf6
    style SkillWork1 fill:#c5cae9
    style SkillWork2 fill:#c5cae9
    style Output1 fill:#9fa8da
```

### /commit-recover

Spawns one verifier per corrupted-file incident found in `.dev/commit-integrity.log`.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Step 1<br/>Parse incidents"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Step 2<br/>Analyse + recover"]
    Phase2 --> Agent1["al-dev-commit-recover-verifier<br/>×N (per incident)"]
    Agent1 --> Phase3["Step 3<br/>Update learnings"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1(["learnings.md"])
    Output1 --> End([End])

    style Phase1 fill:#e0f2f1
    style Phase2 fill:#e0f2f1
    style Phase3 fill:#e0f2f1
    style SkillWork1 fill:#b2dfdb
    style SkillWork2 fill:#b2dfdb
    style Agent1 fill:#80cbc4
    style Output1 fill:#26a69a
```

### /plan-with-critic-swarm

Spawns 6 parallel critic agents (generic Agent tool calls) to red-team a plan. Synthesizes findings into ranked recommendations.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Generate draft plan"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Dispatch critics"]
    Phase2 --> Critics["6 Critic agents<br/>in parallel<br/>(security, testability,<br/>type-safety, rollback,<br/>api-contracts, edge-cases)"]
    Critics --> Phase3["Phase 3<br/>Synthesize + rank"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Phase4["Phase 4<br/>Apply auto-fixes"]
    Phase4 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Output1(["plan-critique-YYYYMMDD.md"])
    Output1 --> End([End])

    style Phase1 fill:#f8bbd0
    style Phase2 fill:#f8bbd0
    style Phase3 fill:#f8bbd0
    style Phase4 fill:#f8bbd0
    style SkillWork1 fill:#f06292
    style SkillWork2 fill:#f06292
    style SkillWork3 fill:#f06292
    style Critics fill:#f06292
    style Output1 fill:#c2185b
```

### /verify-commits

No agents spawned; compares git commits against plan and optionally re-splits combined commits.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Step 1<br/>Read plan"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Step 2<br/>Inspect git log"]
    Phase2 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Decision{Match?}
    Decision -->|Yes| End1([End: OK])
    Decision -->|No| Phase3["Step 3<br/>Re-split commits"]
    Phase3 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Phase4["Step 4<br/>Verify count"]
    Phase4 --> SkillWork4["(skill itself)"]
    SkillWork4 --> End2([End: Fixed])

    style Phase1 fill:#e0f2f1
    style Phase2 fill:#e0f2f1
    style Phase3 fill:#e0f2f1
    style Phase4 fill:#e0f2f1
    style SkillWork1 fill:#b2dfdb
    style SkillWork2 fill:#b2dfdb
    style SkillWork3 fill:#b2dfdb
    style SkillWork4 fill:#b2dfdb
    style Decision fill:#80cbc4
```

---

## Observations

> Generated by /analyze-skill-design on 2026-05-27 with five parallel lenses: Shared Execution Backbone, Complexity Outliers, Near-Duplicate Shapes, Handoff Chain Gaps, Pre-planning Skills.
> Previous analysis (2026-05-22): Three implemented moves (/al-dev-ticket+support consolidation, /al-dev-commit split, architect patterns documented). Current sweep (2026-05-27): Five lenses identify four remaining future-facing suggestions plus four confirmed current-state checks.

### Agents used by only one skill

- **al-dev-ticket-agent** — used by /al-dev-ticket (`--mode=context-only|full`) and /al-dev-support (deprecated alias path to `--mode=full`)
- **al-dev-support-researcher** — used only by /al-dev-ticket (`--mode=full`)
- **al-dev-support-reply-drafter** — used only by /al-dev-ticket (`--mode=full`)
- **al-dev-commit-message-drafter** — used only by /al-dev-commit (message-drafting phase)
- **al-dev-interview** (agent) — used only by /al-dev-interview
- **al-dev-docs-writer** — used only by /al-dev-document
- **al-dev-release-notes-writer** — used only by /al-dev-release-notes
- **al-dev-commit-agent-analysis** — used only by /al-dev-commit (Phase 1; read-only)
- **al-dev-commit-agent-execute** — used only by /al-dev-commit (Phase 3; runs git commits)
- **al-dev-commit-recover-verifier** — used only by /commit-recover
- **al-dev-security-reviewer** — used only by /al-dev-develop
- **al-dev-expert-reviewer** — used only by /al-dev-develop
- **al-dev-performance-reviewer** — used only by /al-dev-develop

### Skills with no dedicated agent (skill does the work itself)

- **/al-dev-handoff** — file copy + prompt assembly; purely shell/file operations
- **/al-dev-help** — reads `.dev/` context files and presents guidance inline

### Potential shared agents (with documented patterns)

- **al-dev-ticket-agent** — used by /al-dev-ticket and the deprecated /al-dev-support alias; invocation patterns in `knowledge/ticket-agent-invocation-pattern.md` ← implemented
- **al-dev-developer** — spawned by /al-dev-fix, /al-dev-develop; patterns in `knowledge/architect-invocation-patterns.md` ← implemented
- **al-dev-solution-architect** — spawned by /al-dev-plan, /al-dev-fix; patterns in `knowledge/architect-invocation-patterns.md` ← implemented
- **Explore subagent** — invoked by /al-dev-investigate (×2 parallel), /al-dev-explore (×1), /al-dev-perf (×1); canonical template in `knowledge/explore-subagent-pattern.md` ← implemented
- **al-dev-diagnostics-fixer** — used by /al-dev-lint; /al-dev-develop returns compile corrections to developers instead of dispatching the fixer
- **Three-reviewer panel** (al-dev-security-reviewer + al-dev-expert-reviewer + al-dev-performance-reviewer) — parallel composition in /al-dev-develop; canonical definition in `knowledge/review-panel-pattern.md` ← implemented

### Architectural suggestions

**Atomise: /al-dev-develop** ← highest leverage

Observation: /al-dev-develop currently spans 10 semantic phases (0–10 with fractional sub-phases) in two clearly separable concern groups: (1) Phases 0–4 handle context preservation, signature verification, work partitioning, and pre-implementation validation gates; (2) Phases 5–10 handle developer dispatch, review synthesis, compilation, and code-review output. The transition from "resource allocation and pre-flight validation" to "quality assurance and finalization" is sharp after Phase 4. A complete, unreviewed implementation exists after Phase 4 (all developers have completed work).

Suggestion: Extract Phases 5–10 (multi-reviewer synthesis, compile-verify, code-review output) into a new `/al-dev-review-develop` skill that consumes /al-dev-develop's intermediate output (all implementation files after Phase 4) and focuses exclusively on post-implementation review orchestration. This splits the 10-phase skill into: (1) `/al-dev-develop` (Phases 0–4): partition work, pre-flight validation, run developers; (2) `/al-dev-review-develop` (Phases 1–3): review coordination, synthesis, compilation verification, code-review write.

Trade-off: Adds one skill to the distributed registry. Each skill becomes narrower (5 vs 10 phases), reducing cognitive load per invocation. Enables independent review workflows (useful for post-hoc code review on completed implementation, or running review multiple times without re-implementing). Requires refactoring Phase 4 output format into a hand-off file format that /al-dev-review-develop reads.

---

**Connect: Reuse the existing symbol pre-flight pattern more broadly**

Observation: `knowledge/al-symbol-pre-flight.md` already exists and /al-dev-develop already treats it as the canonical pre-flight contract. The remaining asymmetry is narrower: /al-dev-fix still uses a lighter developer prompt, so symbol-evidence rigor can still drift between the trivial-fix and planned-development paths.

Suggestion: Treat the knowledge document as complete current-state infrastructure and evaluate a follow-up change that explicitly references it from /al-dev-fix when a "small fix" stops being truly trivial. This is propagation work, not missing documentation.

Trade-off: Slightly longer /al-dev-fix prompts for borderline-simple work. Improvement: stronger consistency between one-file fixes and planned development without inventing another pattern document.

---

**Extend: Add /al-dev-publish (post-release workflow)**

Observation: The main development spine ends at /al-dev-commit (which creates git commits), then branches to four post-commit skills: /al-dev-release-notes (generates dated `.dev/*-al-dev-release-notes-*.md` files), /al-dev-handoff (cross-repo context), /commit-recover (integrity checks), and /al-dev-document (write docs). But no skill consumes the release-notes output. Release notes are a complete deliverable with no downstream action: the chain `/al-dev-commit` → `/al-dev-release-notes` → **[ends here]**. This is an orphaned well-established handoff point with an obvious natural next step.

Suggestion: Create `/al-dev-publish` skill that consumes `/al-dev-release-notes` output (dated `.dev/*-al-dev-release-notes-*.md` files) and orchestrates release publishing: copy to changelog, tag repository, notify stakeholders, or trigger CI/CD deployment pipelines. This completes a frequent workflow: plan → develop → commit → release-notes → **publish** → deployed. The skill would (1) read the latest dated release-notes artifact, (2) offer publication targets (changelog, GitHub releases, notification channel), (3) execute the chosen publication method.

Trade-off: Adds scope and infrastructure dependencies (changelog tooling, tagging policy, notification integration). Only valuable if release publishing is a frequent manual task. Medium complexity if publication targets are standardized; high complexity if integration is ad-hoc per project.

**Status:** Deferred to future work pending scope clarification.
See `knowledge/publish-workflow-opportunity.md` for detailed opportunity analysis.
Current recommendation: Defer implementation until:
1. Confirmation that publishing is frequently manual (not already automated in CI/CD)
2. Standardization of publication targets and integration scope

---

**Improve: Close /al-dev-lint feedback loop in /al-dev-fix**

Observation: Layer 1 diagram shows /al-dev-lint as a dashed feedback loop feeding into /al-dev-fix (line 38-39), but /al-dev-fix does not actually check for or load `.dev/*-al-dev-lint-lint-report.md` when available. The diagram suggests a feedback mechanism that is not implemented: lint findings should inform the architect's complexity analysis, but currently they are ignored.

Suggestion: In /al-dev-fix Step 3 (Non-Trivial Fix), after loading `.dev/*-al-dev-perf-perf-analysis.md`, also check for `.dev/*-al-dev-lint-lint-report.md` and surface any UNRESOLVED items to the architect as "**Known linting constraints**" so complexity assessment can factor in linting debt. This closes the feedback loop shown in the Layer 1 diagram.

Trade-off: One additional glob pattern per /al-dev-fix invocation. Architect prompts become slightly longer when prior lint exists. Improvement: linting debt is visible to the architect instead of hidden.

---

**✅ Confirmed: /al-dev-plan already points unclear requirements to /al-dev-interview**

Status: Confirmed in current sweep. /al-dev-plan Phase 1 explicitly checks for dated `*-al-dev-interview-requirements.md` input and says "If requirements are unclear/complex, suggest /interview." The pre-planning tributary is already discoverable at the right gate.

Impact: No follow-up work needed unless the team wants to refine the exact wording of that suggestion.

---

**✅ Confirmed: /al-dev-develop compile strategy is already explicit**

Status: Confirmed in current sweep. The live skill now states:
- normal mode = one implementation compile pass, one batched developer fix pass, then one more compile
- `--autonomous` = bounded compile-fix loop with up to five attempts
- reviewers are spawned only after Phase 8 compile handling and Phase 8.5 staging both pass

Impact: No clarification task remains. The maintainer opportunity here is optional future refactoring, not missing current-state documentation.

---

**✅ Implemented: Consolidate ticket workflows under /al-dev-ticket**

Status: Completed in Task 4. The live interface is:
- `/al-dev-ticket --mode=context-only` (default) for fetch/context only
- `/al-dev-ticket --mode=full` for fetch + research + reply drafting
- `/al-dev-support` retained as a deprecated alias that points users to `--mode=full`

Impact: Single primary entry point for ticket workflows without removing the compatibility alias.

---

**✅ Implemented: Document shared agent patterns**

Status: Completed in prior cycle. Canonical patterns documented in `knowledge/`:
- `architect-invocation-patterns.md` (competitive vs quick analysis)
- `explore-subagent-pattern.md` (dispatch rules for 1 vs 2 agents)
- `ticket-agent-invocation-pattern.md` (environment verification, API contracts)
- `review-panel-pattern.md` (parallel reviewer composition)

Impact: Single-source-of-truth for invocation patterns prevents drift across skills.

---

**✅ Fixed: /al-dev-explore integration into /al-dev-plan**

Status: Confirmed in current sweep. /al-dev-plan Phase 1 Step 6 correctly loads `.dev/*-al-dev-explore-findings.md`. The prior observation claiming it was NOT loaded was outdated; integration is working.

Impact: Pre-planning tributary is fully integrated; diagram matches implementation.

---

### Completed architectural moves

**✅ Status: /al-dev-align** — Archived in `profile-al-dev-shared/archived/`. Python utility remains available without occupying skill registry slot.

**✅ Status: /plugin-health-daemon** — Moved to `.claude/skills/` as project-local maintenance infrastructure.

---

### General observations

The plugin maintains healthy separation of concerns:
- All multi-agent patterns are documented in `knowledge/`
- Separable skill consolidation opportunities (explore+perf, develop+review) are identified with cost-benefit clarity
- Single-use agents are appropriately scoped to domain-specific tasks
- Pre-planning skills (interview/explore/perf) form a coherent optional enrichment layer feeding /al-dev-plan
- Post-commit skills (release-notes/handoff/document/recover) handle orthogonal concerns
- Shared agents (ticket-agent, developer, architect) are used strategically with documented patterns
- New meta-skills (plan-with-critic-swarm, verify-commits) are well-integrated

### Status summary

**Previous analysis (2026-05-22):** Five lenses applied; 18 skills documented. Three high-leverage suggestions implemented:
- Merged /al-dev-ticket + /al-dev-support
- Split /al-dev-commit into analysis, message-drafting, execution
- Documented architect and pattern invocations

**Current analysis (2026-05-27):** Five lenses re-applied across the same 18 skills. Four future-facing suggestions remain, plus four confirmed current-state checks:
- **Atomise: /al-dev-develop** (split pre-flight from review; highest leverage)
- **Connect: Reuse symbol pre-flight in /al-dev-fix** (propagate existing guidance; medium leverage)
- **Extend: /al-dev-publish** (consume release-notes; medium leverage if deployment is frequent)
- **Improve: Close lint feedback** (wire lint-report into /al-dev-fix; low effort, high clarity)
- **Confirmed: /al-dev-plan interview guidance already present**
- **Confirmed: /al-dev-develop compile/staging gates already documented**
- **Confirmed: /al-dev-explore integration working** (outdated observation removed)
- **Confirmed: Patterns documented** (architect, explore, ticket-agent, review-panel)

### Extension opportunities

1. **Post-release orchestration**: `/al-dev-publish` would consume release-notes and push to channels/changelog/CI (medium priority if deployment is frequently manual; low priority if CI is fully automated).
2. **Review workflow independence**: `/al-dev-review-develop` extracted from `/al-dev-develop` would enable standalone review cycles on completed implementations (medium priority for iterative review workflows; low priority for linear develop-once-review-once patterns).
3. **Lint quality gates**: Optional pre-commit lint check preventing merge if CRITICAL items remain. Currently lint is informational; gating would enforce standards (low priority, lint is advisory by design).
