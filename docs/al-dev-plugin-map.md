# AL Dev Plugin Map

> A reference tool for understanding skill relationships, agent patterns, and file handoffs in profile-al-dev-shared. This document is for personal gap analysis and extension planning, not onboarding.

**Last updated:** 2026-05-18 (all 2026-05-18 architectural suggestions implemented; observations cleaned up)  
**Scope:** Active skills only. Archived items (al-dev-test, test-engineer agents, al-dev-test-coverage-reviewer) excluded. /al-dev-align moved to `.claude/skills/` (project-local maintenance tool, not distributed).

---

## Layer 1: Lifecycle Overview

This diagram shows pre-planning tributaries (dashed, optional), the three main entry points, and the development spine through to post-commit output.

```mermaid
flowchart TD
    %% Pre-planning tributaries (optional)
    Explore("al-dev-explore") -.->|explore-findings.md| Investigate
    Explore -.->|explore-findings.md| Plan
    Interview("al-dev-interview") -.->|interview-requirements.md| Plan

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
    Git -.-> ReleaseNotes("al-dev-release-notes")
    ReleaseNotes --> Notes(["✓ release notes"])
    Support --> Reply(["✓ customer reply"])

    style Ticket fill:#e1f5ff
    style Support fill:#e1f5ff
    style Investigate fill:#f3e5f5
    style Explore fill:#f3e5f5
    style Interview fill:#e8f5e9
    style Plan fill:#fff3e0
    style Develop fill:#fff3e0
    style FixDirect fill:#e8f5e9
    style Commit fill:#e8f5e9
    style Git fill:#c8e6c9
    style Notes fill:#c8e6c9
    style Reply fill:#c8e6c9
    style ReleaseNotes fill:#e3f2fd
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

> Generated by /analyze-plugin-design on 2026-05-16.
> Run /review-plugin-map first if the skill list has changed since this was written.

### Agents used by only one skill

- **al-dev-support-agent** — used only by /al-dev-support
- **al-dev-interview** (agent) — used only by /al-dev-interview
- **al-dev-docs-writer** — used only by /al-dev-document
- **al-dev-release-notes-agent** — used only by /al-dev-release-notes
- **al-dev-commit-agent** — used only by /al-dev-commit (dispatched twice per invocation)
- **al-dev-diagnostics-fixer** — primary caller is /al-dev-lint; also invoked internally by /al-dev-develop in its compile-verify phase (not shown in drill-down)
- **commit-learn-verifier** — used only by /commit-learn

### Skills with no dedicated agent (skill does the work itself)

- **/al-dev-align** — runs an external Python alignment script; all logic is inline
- **/al-dev-handoff** — file copy + prompt assembly; purely shell/file operations
- **/al-dev-help** — reads `.dev/` context files and presents guidance inline

### Potential shared agents not yet extracted

- **Explore subagent** — independently invoked by /al-dev-investigate (×2 parallel), /al-dev-explore (×1), /al-dev-perf (×1); each skill defines its own spawn invocation
- **al-dev-developer** — spawned by /al-dev-fix (×1), /al-dev-develop (×2-3); usage pattern varies by context
- **al-dev-solution-architect** — spawned by /al-dev-plan (×2-3 for competitive debate) and /al-dev-fix (×1 for quick analysis); different usage patterns
- **Three-reviewer panel** (al-dev-security-reviewer + al-dev-expert-reviewer + al-dev-performance-reviewer) — parallel composition in /al-dev-develop; canonical definition in `knowledge/review-panel-pattern.md`
- **al-dev-ticket-agent** — invoked by both /al-dev-ticket (primary) and /al-dev-support (as a prerequisite step)

### Architectural suggestions

**Connect: /al-dev-develop — three-reviewer panel** ← implemented  
Observation: The three-reviewer panel (security + expert + performance in parallel) is now documented in `knowledge/review-panel-pattern.md` and referenced from /al-dev-develop Phase 5. Previously defined independently in both /al-dev-develop and /al-dev-autonomous.  
Status: Done — /al-dev-autonomous archived; single canonical panel definition.

**Merge: /al-dev-autonomous → /al-dev-develop --autonomous** ← implemented  
Observation: /al-dev-autonomous phases (1A signature verification, 4A static validation, 5-attempt compile loop) merged into /al-dev-develop as an `--autonomous` flag. /al-dev-autonomous archived to `archived/skills/`.  
Status: Done — skill list reduced from 18 to 17.

**Connect: /al-dev-explore and /al-dev-perf — shared exploration backbone** ← implemented  
Observation: Both skills share an identical spawn structure.  
Status: Done — `knowledge/explore-subagent-pattern.md` created; al-dev-explore, al-dev-perf, and al-dev-investigate all reference it.

**Promote: Explore subagent spawn pattern** ← implemented  
Observation: Three skills independently authored their Explore subagent invocation.  
Status: Done — `knowledge/explore-subagent-pattern.md` is the canonical template; all three callers reference it.

### Move candidates

**Move: /al-dev-align → .claude/skills/** ← implemented  
Observation: Maintenance-only skill with no value to distributed plugin consumers.  
Status: Done — SKILL.md moved to `.claude/skills/al-dev-align/`; Python script stays in plugin for path resolution.

### Extension opportunities

**Extend: Layer 1 — /al-dev-explore and /al-dev-interview as pre-plan tributaries** ← implemented  
Status: Done — both appear in Layer 1 as dashed tributary arrows feeding Investigate and Plan.

**Extend: Layer 1 — /al-dev-release-notes as post-commit output** ← implemented  
Status: Done — /al-dev-release-notes appears in Layer 1 as a dashed post-commit node after `✓ git commit`.
