# AL Dev Plugin Map

> A reference tool for understanding skill relationships, agent patterns, and file handoffs in profile-al-dev-shared. This document is for personal gap analysis and extension planning, not onboarding.

**Last updated:** 2026-05-16 (synced all 18 active skills)  
**Scope:** Active skills only. Archived items (al-dev-test, test-engineer agents, al-dev-test-coverage-reviewer) excluded.

---

## Layer 1: Lifecycle Overview

This diagram shows the three entry paths and how they connect through the main development spine.

```mermaid
flowchart TD
    %% Entry points
    Ticket("al-dev-ticket") -->|ticket-context.md| Support("al-dev-support")
    Investigate("al-dev-investigate")
    FixDirect("al-dev-fix") -->|AL code| Commit("al-dev-commit")
    
    %% Investigation path branches
    Investigate -->|explore-findings.md| Decision1{Needs<br/>full plan?}
    Decision1 -->|Yes| Plan("al-dev-plan")
    Decision1 -->|No| FixDirect
    
    %% Main development spine
    Plan -->|solution-plan.md| Develop("al-dev-develop")
    Plan -->|solution-plan.md| Autonomous("al-dev-autonomous")
    Develop -->|code-review.md| Commit
    Autonomous -->|code-review.md| Commit
    
    %% Complexity gate within plan
    Note["Trivial requests<br/>route to /fix"] -.-> Plan
    
    %% Outputs
    Commit --> Git(["✓ git commit"])
    Support --> Reply(["✓ customer reply"])
    
    style Ticket fill:#e1f5ff
    style Support fill:#e1f5ff
    style Investigate fill:#f3e5f5
    style Plan fill:#fff3e0
    style Develop fill:#fff3e0
    style Autonomous fill:#fff3e0
    style FixDirect fill:#e8f5e9
    style Commit fill:#e8f5e9
    style Git fill:#c8e6c9
    style Reply fill:#c8e6c9
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

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Fetch & write context"]
    Phase1 --> Agent1["al-dev-ticket-agent ×1"]
    Agent1 --> Output1(["ticket-context.md"])
    Output1 --> End([End])
    
    style Phase1 fill:#e3f2fd
    style Agent1 fill:#bbdefb
    style Output1 fill:#90caf9
```

### /al-dev-support

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Research & draft reply"]
    Phase1 --> Agent1["al-dev-support-agent ×1"]
    Agent1 --> Output1(["customer reply"])
    Output1 --> End([End])
    
    style Phase1 fill:#e3f2fd
    style Agent1 fill:#bbdefb
    style Output1 fill:#90caf9
```

### /al-dev-investigate

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Form hypotheses"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Test hypotheses"]
    Phase2 --> Agent1["al-dev-explore ×2<br/>parallel"]
    Agent1 --> Phase3["Phase 3<br/>Synthesise findings"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1(["explore-findings.md"])
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
    SkillWork2 --> Output1(["solution-plan.md"])
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

**Three-reviewer panel:** Security, AL expert, and performance reviewers run in parallel, then the skill synthesises findings.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Read plan"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Implement"]
    Phase2 --> DevAgent["al-dev-developer ×2-3<br/>parallel"]
    DevAgent --> Phase3["Phase 3<br/>Review<br/>in parallel"]
    
    Phase3 --> SecReview["al-dev-security-reviewer<br/>×1"]
    Phase3 --> ExpertReview["al-dev-expert-reviewer<br/>×1"]
    Phase3 --> PerfReview["al-dev-performance-reviewer<br/>×1"]
    
    SecReview --> Phase4["Phase 4<br/>Synthesise"]
    ExpertReview --> Phase4
    PerfReview --> Phase4
    
    Phase4 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1(["code-review.md"])
    Output1 --> End([End])
    
    style Phase1 fill:#fff8e1
    style Phase2 fill:#fff8e1
    style Phase3 fill:#fff8e1
    style Phase4 fill:#fff8e1
    style SkillWork1 fill:#ffe082
    style SkillWork2 fill:#ffe082
    style DevAgent fill:#ffd54f
    style SecReview fill:#ffca28
    style ExpertReview fill:#ffca28
    style PerfReview fill:#ffca28
    style Output1 fill:#fbc02d
```

### /al-dev-commit

**Two-pass execution:** Analysis pass builds commit groups and messages; execution pass runs the commits with hook support.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Analysis pass"]
    Phase1 --> Agent1["al-dev-commit-agent ×1"]
    Agent1 --> Interim["(commit groups<br/>+ messages)"]
    Interim --> Phase2["Phase 2<br/>Execution pass"]
    Phase2 --> Agent2["al-dev-commit-agent ×1"]
    Agent2 --> Output1(["(git commits)"])
    Output1 --> End([End])
    
    style Phase1 fill:#e0f2f1
    style Phase2 fill:#e0f2f1
    style Agent1 fill:#80cbc4
    style Agent2 fill:#80cbc4
    style Output1 fill:#26a69a
```

### /al-dev-autonomous

**Extends al-dev-develop** with pre-generation signature verification (Phase 1A) and static validation (Phase 4A) before the review team runs.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Read plan +<br/>verify signatures"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Output0(["signatures.md"])
    Output0 --> Phase2["Phase 2<br/>Implement"]
    Phase2 --> DevAgent["al-dev-developer ×1-3<br/>parallel"]
    DevAgent --> Phase3["Phase 3<br/>Static validation"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1(["static-validation.md"])
    Output1 --> Phase4["Phase 4<br/>Review<br/>in parallel"]

    Phase4 --> SecReview["al-dev-security-reviewer<br/>×1"]
    Phase4 --> ExpertReview["al-dev-expert-reviewer<br/>×1"]
    Phase4 --> PerfReview["al-dev-performance-reviewer<br/>×1"]

    SecReview --> Phase5["Phase 5<br/>Compile + lint"]
    ExpertReview --> Phase5
    PerfReview --> Phase5

    Phase5 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Output2(["code-review.md"])
    Output2 --> End([End])

    style Phase1 fill:#fff8e1
    style Phase2 fill:#fff8e1
    style Phase3 fill:#fff8e1
    style Phase4 fill:#fff8e1
    style Phase5 fill:#fff8e1
    style SkillWork1 fill:#ffe082
    style SkillWork2 fill:#ffe082
    style SkillWork3 fill:#ffe082
    style DevAgent fill:#ffd54f
    style SecReview fill:#ffca28
    style ExpertReview fill:#ffca28
    style PerfReview fill:#ffca28
    style Output0 fill:#fbc02d
    style Output1 fill:#fbc02d
    style Output2 fill:#fbc02d
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
    SkillWork2 --> Output1(["explore-findings.md"])
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
    SkillWork2 --> Output1(["interview-requirements.md"])
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
    SkillWork2 --> Output1(["lint-report.md"])
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
    Phase2 --> Agent1["al-dev-release-notes-agent ×1"]
    Agent1 --> Output1(["release-notes-{version}.md"])
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
    SkillWork2 --> Output1(["perf-analysis.md"])
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

### /al-dev-align

Runs a Python alignment script; no agents spawned. Reports forbidden-token violations and harness mapping gaps.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Step 1<br/>Run alignment script"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Step 2<br/>Handle results"]
    Phase2 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1(["alignment report"])
    Output1 --> End([End])

    style Phase1 fill:#e8eaf6
    style Phase2 fill:#e8eaf6
    style SkillWork1 fill:#c5cae9
    style SkillWork2 fill:#c5cae9
    style Output1 fill:#9fa8da
```

### /commit-learn

Spawns one verifier per corrupted-file incident found in `.dev/commit-integrity.log`.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Step 1<br/>Parse incidents"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Step 2<br/>Analyse + recover"]
    Phase2 --> Agent1["commit-learn-verifier<br/>×N (per incident)"]
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

---

## Observations

This section is a placeholder for personal gap analysis. Fill in as you review the map.

### Agents used by only one skill

-

### Skills with no dedicated agent (skill does the work itself)

-

### Potential shared agents not yet extracted

-

### Extension opportunities

-
