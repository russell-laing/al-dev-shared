# AL Dev Plugin Map

> A reference tool for understanding skill relationships, agent patterns, and file handoffs in profile-al-dev-shared. This document is for personal gap analysis and extension planning, not onboarding.

**Last updated:** 2026-06-01 (24 active skill directories in `profile-al-dev-shared/skills`: 20 primary lifecycle skills + 1 distributed utility + 3 maintainer-only tools)
**Scope:** Active skill directories only. Archived items (`al-dev-test`, test-engineer agents, `al-dev-test-coverage-reviewer`, `al-dev-align`) excluded. Layer 1 contains 20 primary lifecycle skills. Layer 2 includes 1 additional distributed utility (`/al-dev-help`). Maintainer-only tools (`/al-dev-diagram-generator`, `/al-dev-map-suggestions-verify`, `/plugin-health-audit`) are documented for reference but not part of the distributed plugin surface.

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

    %% Ticket reply chain (full mode)
    Ticket -.->|--mode=full chains to| SupportReply("al-dev-support-reply")
    SupportReply -.->|.dev/ticket-reply.md| Reply(["✓ customer reply"])

    %% Plan preflight chain
    Preflight("al-dev-plan-preflight") -.->|.dev/preflight-context.md| Plan

    %% Investigation path branches
    Investigate -->|.dev/*-al-dev-investigate-findings.md| Decision1{Needs<br/>full plan?}
    Decision1 -->|Yes| Plan("al-dev-plan")
    Decision1 -->|No| FixDirect

    %% Main development spine
    Plan -->|.dev/*-al-dev-plan-solution-plan.md| Develop("al-dev-develop")
    Develop -->|.dev/*-al-dev-develop-phase4-handoff.md| ReviewDevelop("al-dev-review-develop")
    ReviewDevelop -->|.dev/*-al-dev-develop-code-review.md| Commit

    %% Optional plan red-teaming
    Plan -.->|optional red-team| CriticSwarm("al-dev-plan-swarm-validate")
    CriticSwarm -.->|.dev/plan-critique-YYYYMMDD.md| Develop

    %% Lint feedback loop
    Develop -.->|optional compile cleanup| Lint("al-dev-lint")
    Lint -.->|.dev/*-al-dev-lint-lint-report.md| FixDirect

    %% Complexity gate within plan
    Note["Trivial requests<br/>route to /fix"] -.-> Plan

    %% Outputs
    Commit --> Verify("verify-commits")
    Verify -->|commits match plan| Git(["✓ git commit"])
    Git -.-> ReleaseNotes("al-dev-release-notes")
    ReleaseNotes --> Notes(["✓ release notes"])
    Git -.-> Handoff("al-dev-handoff")
    Handoff --> HandoffOut(["✓ .dev/*-al-dev-handoff-handoff-prompt.md"])
    Git -.->|on integrity error| Recover("commit-recover")
    Recover --> RecoverOut(["✓ recovered files"])
    Git -.-> Document("al-dev-document")
    Document --> DocOut(["✓ documentation"])
    Git -.-> Consolidate("al-dev-consolidate")
    Consolidate --> ConsolidateOut(["✓ .dev/sessions/\nsession-summary.md\nsessions-index.md"])

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
    style Consolidate fill:#e8eaf6
    style ConsolidateOut fill:#c8e6c9
    style Decision1 fill:#ffe0b2
    style CriticSwarm fill:#f8bbd0
    style Verify fill:#e0f2f1
    style SupportReply fill:#e1f5ff
    style Preflight fill:#fff3e0
```

---

## Layer 2: Per-Skill Drill-Downs

Each skill is shown with its internal phases, spawned agents, and key outputs. Agents are referenced by their full type name (for example, `al-dev-shared:al-dev-developer-tdd`).

### Notation

- **Phase**: Numbered step inside the skill
- **Agent**: Which agent (or skill itself) executes the phase
- **Pattern**: ×1 (serial), ×2-3 (parallel), ×N (variable count)
- **Output**: File written to `.dev/` or code generated

### /al-dev-ticket

**Two modes:** `--mode=context-only` (default fetch/context only) and `--mode=full` (fetch context then chains to `/al-dev-support-reply`). Research and reply drafting are handled by `/al-dev-support-reply`.

```mermaid
flowchart LR
    Start([Start]) --> Phase05["Phase 0.5<br/>Resolve mode<br/>(context-only|full)"]
    Phase05 --> SkillWork05["(skill itself)"]
    SkillWork05 --> Phase1["Steps 1-4<br/>Resolve ticket +<br/>fetch context"]
    Phase1 --> Agent1["al-dev-ticket-agent ×1"]
    Agent1 --> Output1F([".dev/*-al-dev-ticket-ticket-context.md"])
    Output1F --> Phase5{Mode?}

    Phase5 -->|context-only| End1([End])
    Phase5 -->|full| Chain["Phase 5<br/>Chain to<br/>/al-dev-support-reply"]
    Chain --> End2(["→ /al-dev-support-reply"])

    style Phase05 fill:#e3f2fd
    style Phase1 fill:#e3f2fd
    style Phase5 fill:#fff9c4
    style Chain fill:#e3f2fd
    style SkillWork05 fill:#bbdefb
    style Agent1 fill:#bbdefb
    style Output1F fill:#90caf9
    style End2 fill:#90caf9
```

Agents spawned: `al-dev-shared:al-dev-ticket-agent`

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
    Phase1T --> DevAgent["al-dev-developer-traditional<br/>or -tdd ×1"]
    DevAgent --> Phase2T["Phase 2<br/>Compile + lint"]
    Phase2T --> SkillT["(skill itself)"]
    SkillT --> End([End])

    Decision -->|Non-trivial| Phase1C["Phase 1<br/>Analyse"]
    Phase1C --> ArchAgent["al-dev-solution-architect<br/>×1 (5 min)"]
    ArchAgent --> Phase2C["Phase 2<br/>Implement"]
    Phase2C --> DevAgent2["al-dev-developer-traditional<br/>or -tdd ×1"]
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

Agents spawned: `al-dev-shared:al-dev-developer-traditional` (trivial path), `al-dev-shared:al-dev-developer-tdd` (non-trivial path when test plan present), `al-dev-shared:al-dev-solution-architect` (non-trivial path only)

### /al-dev-plan

**Competitive design phase:** Dispatches `/al-dev-plan-preflight` first (context assembly + complexity triage), then multiple architects propose approaches in parallel; the skill synthesises the winner into a solution plan. Includes user approval gate before handing off to `/al-dev-develop`.

```mermaid
flowchart LR
    Start([Start]) --> Phase0["Phase 0<br/>Resume check"]
    Phase0 --> Preflight["Dispatch<br/>/al-dev-plan-preflight"]
    Preflight --> PreflightSkill(["PREFLIGHT_CONTEXT<br/>(.dev/preflight-context.md)"])
    PreflightSkill --> Phase2["Phase 2<br/>Spawn architect team"]
    Phase2 --> ArchAgents["al-dev-solution-architect<br/>×2-3 parallel"]
    ArchAgents --> Phase3["Phase 3<br/>Facilitate debate"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Phase4["Phase 4<br/>Evaluate + select<br/>winning approach"]
    Phase4 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Phase5["Phase 5<br/>Write solution plan"]
    Phase5 --> SkillWork4["(skill itself)"]
    SkillWork4 --> Output1([".dev/*-al-dev-plan-solution-plan.md"])
    Output1 --> Phase6["Phase 6<br/>Validate plan"]
    Phase6 --> SkillWork5["(skill itself)"]
    SkillWork5 --> Phase7["Phase 7<br/>Present to user<br/>(USER_GATE)"]
    Phase7 --> End([End])

    style Phase0 fill:#fff3e0
    style Phase2 fill:#fff3e0
    style Phase3 fill:#fff3e0
    style Phase4 fill:#fff3e0
    style Phase5 fill:#fff3e0
    style Phase6 fill:#fff3e0
    style Phase7 fill:#fff3e0
    style Preflight fill:#ffe0b2
    style PreflightSkill fill:#ffcc80
    style SkillWork2 fill:#ffe0b2
    style SkillWork3 fill:#ffe0b2
    style SkillWork4 fill:#ffe0b2
    style SkillWork5 fill:#ffe0b2
    style ArchAgents fill:#ffcc80
    style Output1 fill:#ffb74d
```

Agents spawned: `al-dev-shared:al-dev-solution-architect` (×2-3 parallel in Phase 2); `/al-dev-plan-preflight` dispatched in Phase 0 for context assembly

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
    Phase3 --> DevAgent["al-dev-developer-tdd or<br/>al-dev-developer-traditional ×1-4<br/>(scaled by object count)"]
    DevAgent --> Phase4["Phase 4<br/>Verify completion<br/>+ optional static validation"]
    Phase4 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Handoff(["Phase 4 handoff<br/>(.dev/*-al-dev-develop-phase4-handoff.md)"])
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

**Post-implementation review orchestration:** Consumes Phase 4 handoff from `/al-dev-develop`. Runs compilation verification first (Phase 2) — the review panel is only dispatched if compile passes. Pre-review staging (Phase 3) confirms all prerequisites before the three-specialist panel runs in parallel. Writes code-review artifact and presents findings to user. Phases use local numbering 1–6.

```mermaid
flowchart LR
    Start([Handoff<br/>Phase 4]) --> Phase1["Phase 1<br/>Prepare review<br/>context"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Compile verify<br/>(gates panel)"]
    Phase2 --> SkillWork2["(skill itself + optional<br/>al-dev-developer-traditional<br/>for --autonomous error fix)"]
    SkillWork2 --> Phase3["Phase 3<br/>Pre-review<br/>staging"]
    Phase3 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Phase4["Phase 4<br/>Review panel<br/>in parallel"]

    Phase4 --> SecReview["al-dev-security-reviewer<br/>×1"]
    Phase4 --> ExpertReview["al-dev-expert-reviewer<br/>×1"]
    Phase4 --> PerfReview["al-dev-performance-reviewer<br/>×1"]

    SecReview --> Phase5["Phase 5<br/>Write code review"]
    ExpertReview --> Phase5
    PerfReview --> Phase5

    Phase5 --> SkillWork4["(skill itself)"]
    SkillWork4 --> Output1([".dev/*-al-dev-develop-code-review.md"])
    Output1 --> Phase6["Phase 6<br/>Present findings"]
    Phase6 --> End([End])

    style Phase1 fill:#ff8a65
    style Phase2 fill:#ff8a65
    style Phase3 fill:#ff8a65
    style Phase4 fill:#ff8a65
    style Phase5 fill:#ff8a65
    style Phase6 fill:#ff8a65
    style SkillWork1 fill:#ff7043
    style SkillWork2 fill:#ff7043
    style SkillWork3 fill:#ff7043
    style SkillWork4 fill:#ff7043
    style SecReview fill:#ff5722
    style ExpertReview fill:#ff5722
    style PerfReview fill:#ff5722
    style Output1 fill:#d84315
```

Agents spawned: `al-dev-shared:al-dev-security-reviewer`, `al-dev-shared:al-dev-expert-reviewer`, `al-dev-shared:al-dev-performance-reviewer` (all in Phase 4 parallel), `al-dev-shared:al-dev-developer-traditional` (Phase 2 `--autonomous` mode only)

### /al-dev-commit

**Multi-pass execution:** Setup and validation (Phase 0) checks project context, file integrity, staged files, acceptance criteria, and advisory alignment; analysis pass (Phase 1) builds manifests and proposes commit groups with message drafting; confirmation pass (Phase 2) gates user approval; preflight pass (Phase 3) runs lint fixes and OOXML validation; execution pass (Phase 4) runs the commits with hook support and presents the final summary. Five agents with focused responsibilities.

```mermaid
flowchart LR
    Start([Start]) --> Phase0["Phase 0<br/>Setup & Validation<br/>(context, integrity,<br/>staged files, AC check)"]
    Phase0 --> SkillWork0["(skill itself)"]
    SkillWork0 --> Phase1["Phase 1<br/>Analysis &<br/>Message Drafting"]
    Phase1 --> Agent1["al-dev-commit-agent-analysis ×1<br/>(manifest only)"]
    Agent1 --> Interim1["(per-file manifests<br/>+ group proposals)"]
    Interim1 --> Agent2["al-dev-commit-message-drafter ×1"]
    Agent2 --> Interim2["(commit messages)"]
    Interim2 --> Phase2["Phase 2<br/>Confirmation"]
    Phase2 --> SkillWork2["(skill itself)<br/>(USER_GATE)"]
    SkillWork2 --> Phase3["Phase 3<br/>Preflight"]
    Phase3 --> Agent4["al-dev-commit-lint-fixer ×1"]
    Agent4 --> Agent5["al-dev-commit-ooxml-validator ×1"]
    Agent5 --> Phase4["Phase 4<br/>Execution & Summary"]
    Phase4 --> Agent3["al-dev-commit-agent-execute ×1<br/>(haiku)"]
    Agent3 --> Output1(["(git commits)"])
    Output1 --> End([End])

    style Phase0 fill:#e0f2f1
    style Phase1 fill:#e0f2f1
    style Phase2 fill:#e0f2f1
    style Phase3 fill:#e0f2f1
    style Phase4 fill:#e0f2f1
    style SkillWork0 fill:#80cbc4
    style SkillWork2 fill:#80cbc4
    style Agent1 fill:#80cbc4
    style Agent2 fill:#4db8a8
    style Agent3 fill:#80cbc4
    style Agent4 fill:#4db8a8
    style Agent5 fill:#4db8a8
    style Interim1 fill:#b2dfdb
    style Interim2 fill:#b2dfdb
    style Output1 fill:#26a69a
```

Agents spawned: `al-dev-shared:al-dev-commit-agent-analysis` (Phase 1), `al-dev-shared:al-dev-commit-message-drafter` (Phase 1), `al-dev-shared:al-dev-commit-lint-fixer` (Phase 3), `al-dev-shared:al-dev-commit-ooxml-validator` (Phase 3), `al-dev-shared:al-dev-commit-agent-execute` (Phase 4)

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
    Start([Start]) --> Phase1["Phase 1<br/>Pre-research<br/>(AL symbols lookup)"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Interview"]
    Phase2 --> Agent1["al-dev-interview ×1"]
    Agent1 --> Phase3["Phase 3<br/>Write requirements"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1([".dev/*-al-dev-interview-requirements.md"])
    Output1 --> Phase4["Phase 4<br/>Summary"]
    Phase4 --> SkillWork3["(skill itself)"]
    SkillWork3 --> End([End])

    style Phase1 fill:#e8f5e9
    style Phase2 fill:#e8f5e9
    style Phase3 fill:#e8f5e9
    style Phase4 fill:#e8f5e9
    style SkillWork1 fill:#c8e6c9
    style SkillWork2 fill:#c8e6c9
    style SkillWork3 fill:#c8e6c9
    style Agent1 fill:#a5d6a7
    style Output1 fill:#81c784
```

Agents spawned: `al-dev-shared:al-dev-interview`

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
    SkillWork1 --> Phase15["Phase 1.5<br/>Read project context"]
    Phase15 --> SkillWork15["(skill itself)"]
    SkillWork15 --> Phase2["Phase 2<br/>Generate notes"]
    Phase2 --> Agent1["al-dev-release-notes-writer ×1"]
    Agent1 --> Output1([".dev/YYYY-MM-DD-[app-id]-al-dev-release-notes-[short-hash].md"])
    Output1 --> Phase3["Phase 3<br/>Present to user<br/>(handle AMBIGUOUS)"]
    Phase3 --> SkillWork3["(skill itself)"]
    SkillWork3 --> End([End])

    style Phase1 fill:#e3f2fd
    style Phase15 fill:#e3f2fd
    style Phase2 fill:#e3f2fd
    style Phase3 fill:#e3f2fd
    style SkillWork1 fill:#bbdefb
    style SkillWork15 fill:#bbdefb
    style SkillWork3 fill:#bbdefb
    style Agent1 fill:#90caf9
    style Output1 fill:#64b5f6
```

Agents spawned: `al-dev-shared:al-dev-release-notes-writer`

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
    SkillWork3 --> Output1([".dev/*-al-dev-handoff-handoff-prompt.md"])
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

Spawns one fixer per corrupted-file incident found in `.dev/commit-integrity.log`.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Step 1<br/>Parse incidents"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Step 2<br/>Analyse + recover"]
    Phase2 --> Agent1["al-dev-commit-recover-fixer<br/>×N (per incident)"]
    Agent1 --> Phase3["Step 3<br/>Update learnings"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1([".dev/learnings.md"])
    Output1 --> End([End])

    style Phase1 fill:#e0f2f1
    style Phase2 fill:#e0f2f1
    style Phase3 fill:#e0f2f1
    style SkillWork1 fill:#b2dfdb
    style SkillWork2 fill:#b2dfdb
    style Agent1 fill:#80cbc4
    style Output1 fill:#26a69a
```

### /al-dev-plan-swarm-validate

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

### /al-dev-consolidate

Standalone utility skill. No agents spawned. Consolidates `.dev/` artifacts
into vault-ready session summaries and an Obsidian-compatible sessions index,
using only bash extraction — file content is never read into LLM context.

```mermaid
flowchart LR
    Start([Start]) --> Phase0["Phase 0\nResume check"]
    Phase0 --> SkillWork0["(skill itself)"]
    SkillWork0 --> Decision{Index\nexists?}
    Decision -->|No index| Phase1["Phase 1\nDiscover & group"]
    Decision -->|Re-run all| Phase1
    Decision -->|Update| Phase1
    Decision -->|Cancel| End1([End])
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2\nExtract per session"]
    Phase2 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Phase3["Phase 3\nWrite summaries"]
    Phase3 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Phase4["Phase 4\nWrite index"]
    Phase4 --> SkillWork4["(skill itself)"]
    SkillWork4 --> Output1([".dev/sessions/\nsession-summary.md\nsessions-index.md"])
    Output1 --> End([End])

    style Phase0 fill:#e8eaf6
    style Phase1 fill:#e8eaf6
    style Phase2 fill:#e8eaf6
    style Phase3 fill:#e8eaf6
    style Phase4 fill:#e8eaf6
    style SkillWork0 fill:#c5cae9
    style SkillWork1 fill:#c5cae9
    style SkillWork2 fill:#c5cae9
    style SkillWork3 fill:#c5cae9
    style SkillWork4 fill:#c5cae9
    style Decision fill:#fff9c4
    style Output1 fill:#9fa8da
```

### /al-dev-diagram-generator

**Maintainer tool — not part of the main development lifecycle.** Dispatched by `/analyze-agent-design` and `/analyze-skill-design` after their analysis phases complete. Does not appear in the Layer 1 lifecycle diagram because it is called from project-local maintainer tooling (`.claude/skills/`), not from distributed plugin skills.

Generates Mermaid flowchart diagrams showing how the plugin's skills, agents, and knowledge files connect. Writes `docs/al-dev-workflow-diagrams.md`.

| Field | Value |
|---|---|
| Triggered by | `--caller-name <skill-name>` argument from `/analyze-agent-design` or `/analyze-skill-design` |
| Agents spawned | None — skill does all work itself |
| Inputs | Repo source files (grepped via bash); `markdown/md-mermaid-helper.md` style guide |
| Outputs | `docs/al-dev-workflow-diagrams.md` |

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1\nStatic analysis\n(4 grep passes)"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2\nComplexity check\n(node/edge count)"]
    Phase2 --> Decision{Combined\nor split?}
    Decision -->|"≤25 nodes, ≤35 edges"| Phase3a["Phase 3\nGenerate one\ncombined diagram"]
    Decision -->|Larger| Phase3b["Phase 3\nGenerate two\nfocused diagrams"]
    Phase3a --> Phase4["Phase 4\nWrite output file"]
    Phase3b --> Phase4
    Phase4 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1(["docs/al-dev-workflow-diagrams.md"])
    Output1 --> End([End])

    style Phase1 fill:#e8eaf6
    style Phase2 fill:#e8eaf6
    style Phase3a fill:#e8eaf6
    style Phase3b fill:#e8eaf6
    style Phase4 fill:#e8eaf6
    style SkillWork1 fill:#c5cae9
    style SkillWork2 fill:#c5cae9
    style Decision fill:#fff9c4
    style Output1 fill:#9fa8da
```

### /al-dev-map-suggestions-verify

**Maintainer tool — not part of the main development lifecycle.** Rubber-ducks architectural suggestions from the map Observations sections using parallel remote agent teams. Reduces session token burn from 1-1.5 hours to 40-50 minutes via async verification and multi-session checkpoint/resume workflow.

Writes `.dev/YYYY-MM-DD-al-dev-plan-plan.md` (generated by `superpowers:writing-plans`).

```mermaid
flowchart LR
    Start([Start]) --> Decision{--resume?}
    Decision -->|No| Phase1["Phase 1<br/>Extract suggestions<br/>from map Observations"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> SizeCheck{1-2 or 3+<br/>suggestions?}
    SizeCheck -->|1-2| Phase2a["Phase 2A<br/>Inline verify"]
    SizeCheck -->|3+| Phase2b["Phase 2B<br/>Dispatch remote<br/>duck-worker team"]
    Phase2a --> Phase3["Phase 3<br/>Collect + plan"]
    Phase2b --> ReturnUser(["Return to user<br/>(async; run --resume when ready)"])
    Decision -->|--resume| Phase3
    Phase3 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Output1([".dev/YYYY-MM-DD-al-dev-plan-plan.md"])
    Output1 --> End([End])

    style Phase1 fill:#e8eaf6
    style Phase2a fill:#e8eaf6
    style Phase2b fill:#e8eaf6
    style Phase3 fill:#e8eaf6
    style SkillWork1 fill:#c5cae9
    style SkillWork3 fill:#c5cae9
    style SizeCheck fill:#fff9c4
    style Decision fill:#fff9c4
    style ReturnUser fill:#9fa8da
    style Output1 fill:#9fa8da
```

Agents spawned: `al-dev-shared:al-dev-map-suggestions-verify-duck-worker` (×N parallel, Phase 2B remote path only)

### /plugin-health

**Maintainer tool — not part of the main development lifecycle.** Parallelized health sweep of the al-dev-shared plugin surfaces (skills and agents). Dispatches remote design and quality lenses, ranks findings, and writes dossiers to `docs/health/`. Supports resume workflow to collect results in a separate session.

```mermaid
flowchart LR
    Start([Start]) --> Decision{--resume?}
    Decision -->|No| Phase1["Phase 1<br/>Parse args +<br/>build work queue"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Dispatch["Spawn remote<br/>lens agent team"]
    Dispatch --> Checkpoint([".dev/plugin-health-team-checkpoint.json"])
    Checkpoint --> ReturnUser(["Return to user<br/>(async; run --resume when ready)"])
    Decision -->|--resume| Phase3["Phase 3<br/>Collect findings +<br/>write dossiers"]
    Phase3 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Output1(["docs/health/<surface>-dossier.md"])
    Output1 --> End([End])

    style Phase1 fill:#e8eaf6
    style Phase3 fill:#e8eaf6
    style SkillWork1 fill:#c5cae9
    style SkillWork3 fill:#c5cae9
    style Decision fill:#fff9c4
    style Dispatch fill:#c5cae9
    style Checkpoint fill:#9fa8da
    style ReturnUser fill:#9fa8da
    style Output1 fill:#9fa8da
```

Agents spawned: Remote lens agents (×N parallel, dispatched in Phase 1; agent names defined in `knowledge/plugin-health-lenses.md`)

---

## Observations

> Generated by /analyze-skill-design on 2026-05-27 with five parallel lenses: Shared Execution Backbone, Complexity Outliers, Near-Duplicate Shapes, Handoff Chain Gaps, Pre-planning Skills.
> Previous analysis (2026-05-22): Three implemented moves (/al-dev-ticket+support consolidation, /al-dev-commit split, architect patterns documented). Current sweep (2026-05-27): Five lenses identify four remaining future-facing suggestions plus four confirmed current-state checks.

### Agents used by only one skill

- **al-dev-ticket-agent** — used by /al-dev-ticket (`--mode=context-only|full`)
- **al-dev-support-researcher** — used only by /al-dev-ticket (`--mode=full`)
- **al-dev-support-reply-drafter** — used only by /al-dev-ticket (`--mode=full`)
- **al-dev-commit-message-drafter** — used only by /al-dev-commit (message-drafting phase)
- **al-dev-interview** (agent) — used only by /al-dev-interview
- **al-dev-docs-writer** — used only by /al-dev-document
- **al-dev-release-notes-writer** — used only by /al-dev-release-notes
- **al-dev-commit-agent-analysis** — used only by /al-dev-commit (Phase 1; read-only)
- **al-dev-commit-agent-execute** — used only by /al-dev-commit (Phase 4; runs git commits)
- **al-dev-commit-lint-fixer** — used only by /al-dev-commit (Phase 3; lint pre-flight)
- **al-dev-commit-ooxml-validator** — used only by /al-dev-commit (Phase 3; OOXML validation)
- **al-dev-commit-recover-fixer** — used only by /commit-recover
- **al-dev-security-reviewer** — used only by /al-dev-review-develop (dispatched in Phase 4)
- **al-dev-expert-reviewer** — used only by /al-dev-review-develop (dispatched in Phase 4)
- **al-dev-performance-reviewer** — used only by /al-dev-review-develop (dispatched in Phase 4)

### Skills with no dedicated agent (skill does the work itself)

- **/al-dev-handoff** — file copy + prompt assembly; purely shell/file operations
- **/al-dev-help** — reads `.dev/` context files and presents guidance inline
- **/al-dev-consolidate** — bash-only artifact extraction; writes session summaries and sessions index to `.dev/sessions/`
- **/al-dev-diagram-generator** — static grep analysis + Mermaid generation; dispatched by `/analyze-agent-design` and `/analyze-skill-design`; writes `docs/al-dev-workflow-diagrams.md`

### Potential shared agents (with documented patterns)

- **al-dev-ticket-agent** — used by /al-dev-ticket; invocation patterns in `knowledge/ticket-agent-invocation-pattern.md` ← implemented
- **al-dev-developer-tdd / al-dev-developer-traditional** — spawned by /al-dev-fix and /al-dev-develop based on test-plan presence; /al-dev-review-develop autonomous compile-fix loops use the traditional variant. Patterns in `knowledge/developer-invocation-patterns.md` ← implemented
- **al-dev-solution-architect** — spawned by /al-dev-plan, /al-dev-fix; patterns in `knowledge/architect-invocation-patterns.md` ← implemented
- **Explore subagent** — invoked by /al-dev-investigate (×2 parallel), /al-dev-explore (×1), /al-dev-perf (×1); canonical template in `knowledge/explore-subagent-pattern.md` ← implemented
- **al-dev-diagnostics-fixer** — used by /al-dev-lint; /al-dev-develop returns compile corrections to developers instead of dispatching the fixer
- **Three-reviewer panel** (al-dev-security-reviewer + al-dev-expert-reviewer + al-dev-performance-reviewer) — parallel composition in /al-dev-develop; canonical definition in `knowledge/review-panel-pattern.md` ← implemented

### Architectural suggestions

**✅ Implemented: /al-dev-review-develop extracted from /al-dev-develop**

Status: Confirmed in current sweep. The live workflow now splits implementation from review:
- `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` produces a Phase 4 handoff for `/al-dev-review-develop`
- `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` owns the post-implementation review orchestration (Phase 1-6 local numbering)

Impact: This is no longer remaining implementation scope. The map should treat review-workflow independence as current state, not future work.

---

**Connect: Clarify `/al-dev-fix` escalation boundaries**

Observation: The core propagation work is already present. `/al-dev-fix` now:
- loads prior lint findings on the non-trivial path
- dispatches an architect for non-trivial fixes
- explicitly tells that architect to follow `knowledge/al-symbol-pre-flight.md`

The remaining asymmetry is documentation: `profile-al-dev-shared/knowledge/workflow-routing.md` still describes `/al-dev-fix` as if it were always a direct trivial edit with no planning branch.

Suggestion: Treat symbol pre-flight reuse as implemented for the non-trivial `/al-dev-fix` path. The remaining follow-up is to align routing guidance so `/al-dev-fix` is documented as a fast-fix entrypoint that may escalate to quick architect analysis when the issue is ambiguous, multi-file, or integration-heavy.

Trade-off: Slightly more nuanced routing prose. Improvement: removes false expectations about `/al-dev-fix`, makes existing symbol-rigor behavior discoverable, and avoids adding prompt weight to truly trivial fixes without evidence.

---

**Extend: Add /al-dev-publish (post-release workflow)**

Observation: The main development spine ends at /al-dev-commit (which creates git commits), then branches to four post-commit skills: /al-dev-release-notes (generates dated `.dev/*-al-dev-release-notes-*.md` files), /al-dev-handoff (cross-repo context), /commit-recover (integrity checks), and /al-dev-document (write docs). But no skill consumes the release-notes output. Release notes are a complete deliverable with no downstream action: the chain `/al-dev-commit` → `/al-dev-release-notes` → **[ends here]**. This is an orphaned well-established handoff point with an obvious natural next step.

Suggestion: Create `/al-dev-publish` skill that consumes `/al-dev-release-notes` output (dated `.dev/*-al-dev-release-notes-*.md` files) and orchestrates release publishing: copy to changelog, tag repository, notify stakeholders, or trigger CI/CD deployment pipelines. This completes a frequent workflow: plan → develop → commit → release-notes → **publish** → deployed. The skill would (1) read the latest dated release-notes artifact, (2) offer publication targets (changelog, GitHub releases, notification channel), (3) execute the chosen publication method.

Trade-off: Adds scope and infrastructure dependencies (changelog tooling, tagging policy, notification integration). Only valuable if release publishing is a frequent manual task. Medium complexity if publication targets are standardized; high complexity if integration is ad-hoc per project.

**Status:** Deferred to future work pending scope clarification.
See `knowledge/publish-workflow-opportunity.md` for detailed opportunity analysis.
Current recommendation: Do not implement in shared profile until:
1. Publishing is confirmed to be a frequent manual workflow
2. Publication targets are standardized enough to be harness-neutral
3. Required integrations are known and supportable across downstream repos

---

**✅ Implemented: /al-dev-fix consumes prior lint findings**

Status: Confirmed in current sweep. `/al-dev-fix` Step 3 now:
- loads the latest `.dev/*-al-dev-lint-lint-report.md` when present
- extracts unresolved items
- passes them into the architect prompt as `Known linting constraints`

Impact: The Layer 1 lint -> fix feedback loop is implemented in the live skill. No new behavior change is required here; only the map text needed reconciliation.

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

### Move candidates

Three skills scored 2+ signals and qualify as move candidates to `.claude/skills/`:

**Move: /al-dev-map-suggestions-verify → .claude/skills/**
Observation: Plugin-maintenance orchestrator. Reads architectural suggestions from the map Observations sections, rubber-ducks them with remote agent teams, and generates plans. No value to distributed AL developers; only used internally by maintainers analyzing the plugin itself.
Signals: internal path refs (✓), self-audit purpose (✓), no spawned al-dev-shared agents (✓).
Suggestion: Move `profile-al-dev-shared/skills/al-dev-map-suggestions-verify/` to `.claude/skills/al-dev-map-suggestions-verify/` and remove from the plugin scope statement. Update Layer 1 diagram to remove the node.
Trade-off: Skill remains available in this repo for maintainer use; removed from the distributed plugin.

**Move: /al-dev-diagram-generator → .claude/skills/**
Observation: Plugin-analysis tool. Generates Mermaid diagrams showing how the plugin's skills, agents, and knowledge files connect. Dispatched exclusively by `/analyze-agent-design` and `/analyze-skill-design` (both maintainer tools). Produces `docs/al-dev-workflow-diagrams.md`. No use case for distributed AL developers.
Signals: internal path refs (✓), self-audit purpose (✓), no spawned al-dev-shared agents (✓).
Suggestion: Move `profile-al-dev-shared/skills/al-dev-diagram-generator/` to `.claude/skills/al-dev-diagram-generator/` and remove from the plugin scope statement. Update Layer 2 to remove the section or relocate to a maintainer-tools appendix.
Trade-off: Skill remains available for local analysis workflows; removed from the distributed plugin.

**Move: /plugin-health-audit → .claude/skills/**
Observation: Plugin health-check and quality-audit tool. Dispatches remote lens agents to audit design, quality, complexity, and naming across the plugin surfaces; writes dossiers to `docs/health/`. Purely for maintainer use; no value to AL developers.
Signals: self-audit purpose (✓), no spawned al-dev-shared agents (✓).
Suggestion: Move `profile-al-dev-shared/skills/plugin-health-audit/` to `.claude/skills/plugin-health-audit/` and remove from the plugin scope statement. Update Layer 2 to remove the section.
Trade-off: Skill remains available for periodic health sweeps; removed from the distributed plugin.

---

### Completed architectural moves

**✅ Status: /al-dev-align** — Archived in `profile-al-dev-shared/archived/`. Python utility remains available without occupying skill registry slot.

**✅ Status: /maintaining-shared-knowledge** — Moved to `.codex/skills/maintaining-shared-knowledge/` as repo-local Codex maintainer tooling. It remains available for maintaining this repository but is no longer part of the distributed `profile-al-dev-shared` skill surface.


---

### General observations

The plugin maintains healthy separation of concerns:
- All multi-agent patterns are documented in `knowledge/`
- Separable skill consolidation opportunities (explore+perf, develop+review) are identified with cost-benefit clarity
- Single-use agents are appropriately scoped to domain-specific tasks
- Pre-planning skills (interview/explore/perf) form a coherent optional enrichment layer feeding /al-dev-plan
- Post-commit skills (release-notes/handoff/document/recover) handle orthogonal concerns
- Shared agents (ticket-agent, developer, architect) are used strategically with documented patterns
- New meta-skills (al-dev-plan-swarm-validate, verify-commits) are well-integrated

### Status summary

**Previous analysis (2026-05-22):** Five lenses applied; 18 skills documented. Three high-leverage suggestions implemented:
- Consolidated /al-dev-support into /al-dev-ticket (removed deprecated alias)
- Split /al-dev-commit into analysis, message-drafting, execution
- Documented architect and pattern invocations

**Current analysis (2026-05-27):** Five lenses re-applied across the same 18 skills. Current state is:
- **Implemented: /al-dev-review-develop extraction** (review workflow independence is now live)
- **Narrow follow-up: `/al-dev-fix` symbol-rigor wording** (non-trivial path already uses symbol pre-flight; routing docs still need alignment)
- **Deferred: /al-dev-publish** (blocked on scope clarification)
- **Implemented: lint feedback into `/al-dev-fix`** (unresolved lint items already surface to the architect)
- **Confirmed: /al-dev-plan interview guidance already present**
- **Confirmed: /al-dev-develop compile/staging gates already documented**
- **Confirmed: /al-dev-explore integration working** (outdated observation removed)
- **Confirmed: Patterns documented** (architect, explore, ticket-agent, review-panel)

### Extension opportunities

1. **Post-release orchestration**: `/al-dev-publish` remains a deferred opportunity until publication targets, tooling, and audience are standardized.
2. **✅ Confirmed implemented: `/al-dev-fix` routing clarity** (2026-05-29): `workflow-routing.md` lines 40–46 already document the non-trivial architect escalation path explicitly. No prose update needed.
3. **Lint quality gates**: Optional pre-commit lint gating remains separate future work; current lint integration is advisory by design.
