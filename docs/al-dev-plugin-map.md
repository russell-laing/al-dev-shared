# AL Dev Plugin Map

> A reference tool for understanding skill relationships, agent patterns, and file handoffs in profile-al-dev-shared. This document is for personal gap analysis and extension planning, not onboarding.

**Last updated:** 2026-05-16  
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
    Develop -->|code-review.md| Commit
    
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
    style Fix fill:#e8f5e9
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
