# AL Dev Plugin Map

> A reference tool for understanding skill relationships, agent patterns, and file handoffs in profile-al-dev-shared. This document is for personal gap analysis and extension planning, not onboarding.

**Last updated:** 2026-05-21 (full architectural analysis: 6 improvement suggestions, 2 maintenance moves)
**Scope:** Active skills only. Archived items (al-dev-test, test-engineer agents, al-dev-test-coverage-reviewer) excluded. /align-harness-repos in `.claude/skills/` (project-local maintenance tool, not distributed).

---

## Layer 1: Lifecycle Overview

This diagram shows pre-planning tributaries (dashed, optional), the three main entry points, and the development spine through to post-commit output.

```mermaid
flowchart TD
    %% Pre-planning tributaries (optional)
    Explore("al-dev-explore") -.->|explore-findings.md| Investigate
    Explore -.->|explore-findings.md| Plan
    Interview("al-dev-interview") -.->|interview-requirements.md| Plan
    Perf("al-dev-perf") -.->|perf-analysis.md| Plan
    Perf -.->|perf-analysis.md| FixDirect

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

    %% Lint feedback loop
    Develop -.-> Lint("al-dev-lint")
    Lint -.->|lint-report.md| FixDirect

    %% Complexity gate within plan
    Note["Trivial requests<br/>route to /fix"] -.-> Plan

    %% Outputs
    Commit --> Git(["✓ git commit"])
    Git -.-> ReleaseNotes("al-dev-release-notes")
    ReleaseNotes --> Notes(["✓ release notes"])
    Git -.-> Handoff("al-dev-handoff")
    Handoff --> HandoffOut(["✓ handoff-prompt.md"])
    Git -.->|on integrity error| Recover("commit-recover")
    Recover --> RecoverOut(["✓ recovered files"])
    Git -.-> Document("al-dev-document")
    Document --> DocOut(["✓ documentation"])
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
    Phase2 --> Agent1["Explore subagent ×2<br/>parallel"]
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

**Three-reviewer panel:** Security, AL expert, and performance reviewers run in parallel, then the skill synthesises findings. Compile-verify loop (with diagnostics fixer) runs before final code review output.

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

    Phase4 --> Phase5["Phase 5<br/>Compile + verify"]
    Phase5 --> SkillWork2["(skill itself)"]
    SkillWork2 --> CompileAgent["al-dev-diagnostics-fixer ×1"]
    CompileAgent --> SkillWork3["(skill itself)"]
    SkillWork3 --> Phase6["Phase 6<br/>Write code review"]
    Phase6 --> SkillWork4["(skill itself)"]
    SkillWork4 --> Output1(["code-review.md"])
    Output1 --> End([End])

    style Phase1 fill:#fff8e1
    style Phase2 fill:#fff8e1
    style Phase3 fill:#fff8e1
    style Phase4 fill:#fff8e1
    style Phase5 fill:#fff8e1
    style Phase6 fill:#fff8e1
    style SkillWork1 fill:#ffe082
    style SkillWork2 fill:#ffe082
    style SkillWork3 fill:#ffe082
    style SkillWork4 fill:#ffe082
    style DevAgent fill:#ffd54f
    style CompileAgent fill:#ffd54f
    style SecReview fill:#ffca28
    style ExpertReview fill:#ffca28
    style PerfReview fill:#ffca28
    style Output1 fill:#fbc02d
```

### /al-dev-commit

**Two-pass execution:** Analysis pass builds commit groups and messages; execution pass runs the commits with hook support. Each phase uses a distinct agent.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Analysis pass"]
    Phase1 --> Agent1["al-dev-commit-agent-analysis ×1"]
    Agent1 --> Interim["(commit groups<br/>+ messages)"]
    Interim --> Phase2["Phase 2<br/>Execution pass"]
    Phase2 --> Agent2["al-dev-commit-agent-execute ×1"]
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
    Phase2 --> Agent1["al-dev-release-notes-writer ×1"]
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

### /align-harness-repos

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

### /plugin-health-daemon

> **Scope: Project-local only.** Moved to `.claude/skills/plugin-health-daemon/` — not distributed in the plugin. Maintained alongside `/align-harness-repos` as internal plugin-maintenance infrastructure.

Autonomous audit sweep that dispatches all plugin review skills in parallel, auto-fixes safe issues, and generates a weekly digest.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Dispatch audits"]
    Phase1 --> Audits["6 Audit skills<br/>in parallel<br/>(audit-skill-quality,<br/>audit-agent-quality,<br/>review-skill-map,<br/>analyze-skill-design,<br/>review-agent-map,<br/>analyze-agent-design)"]
    Audits --> Phase2["Phase 2<br/>Aggregate findings"]
    Phase2 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase3["Phase 3<br/>Auto-fix safe issues"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Phase4["Phase 4<br/>Generate reports"]
    Phase4 --> SkillWork3["(skill itself)"]
    SkillWork3 --> Output1(["PR + digest"])
    Output1 --> End([End])

    style Phase1 fill:#c8e6c9
    style Phase2 fill:#c8e6c9
    style Phase3 fill:#c8e6c9
    style Phase4 fill:#c8e6c9
    style SkillWork1 fill:#81c784
    style SkillWork2 fill:#81c784
    style SkillWork3 fill:#81c784
    style Audits fill:#66bb6a
    style Output1 fill:#4caf50
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

> Generated by /analyze-skill-design on 2026-05-21 with four parallel lenses: Shared Execution Backbone, Complexity Outliers, Near-Duplicate Shapes, Handoff Chain Gaps, Pre-planning Skills.
> Run /review-skill-map first if the skill list has changed since this was written.

### Agents used by only one skill

- **al-dev-ticket-agent** — used only by /al-dev-ticket
- **al-dev-support-agent** — used only by /al-dev-support
- **al-dev-interview** (agent) — used only by /al-dev-interview
- **al-dev-docs-writer** — used only by /al-dev-document
- **al-dev-release-notes-writer** — used only by /al-dev-release-notes
- **al-dev-commit-agent-analysis** — used only by /al-dev-commit (Phase 1; read-only)
- **al-dev-commit-agent-execute** — used only by /al-dev-commit (Phase 2; runs git commits)
- **al-dev-diagnostics-fixer** — primary caller is /al-dev-lint; also invoked by /al-dev-develop in its compile-verify phase (Phase 5)
- **al-dev-commit-recover-verifier** — used only by /commit-recover

### Skills with no dedicated agent (skill does the work itself)

- **/align-harness-repos** — runs an external Python alignment script; all logic is inline (project-local, not distributed)
- **/al-dev-handoff** — file copy + prompt assembly; purely shell/file operations
- **/al-dev-help** — reads `.dev/` context files and presents guidance inline

### Potential shared agents (documented patterns)

- **Explore subagent** — invoked by /al-dev-investigate (×2 parallel), /al-dev-explore (×1), /al-dev-perf (×1); canonical template in `knowledge/explore-subagent-pattern.md` ← implemented
- **al-dev-developer** — spawned by /al-dev-fix (×1), /al-dev-develop (×2-3); patterns in `knowledge/architect-invocation-patterns.md` ← implemented
- **al-dev-solution-architect** — spawned by /al-dev-plan (×2-3 competitive debate) and /al-dev-fix (×1 quick analysis); patterns in `knowledge/architect-invocation-patterns.md` ← implemented
- **Three-reviewer panel** (al-dev-security-reviewer + al-dev-expert-reviewer + al-dev-performance-reviewer) — parallel composition in /al-dev-develop; canonical definition in `knowledge/review-panel-pattern.md` ← implemented

### Architectural suggestions

**Atomise: /al-dev-develop** ← highest leverage

Observation: /al-dev-develop has 6 phases with two clearly separable concern groups: (1) Phases 1–4 handle context gathering and developer partitioning (who builds what), (2) Phases 5–6 handle specialist review synthesis and compilation (what did they build). The work pattern shifts from "resource allocation" to "quality assurance" after Phase 4. A complete (though unreviewed) implementation workflow exists after Phase 4.

Suggestion: Extract Phases 5–6 (review synthesis + compile-verify + code-review output) into a new `/al-dev-review-develop` skill that consumes `/al-dev-develop` code-review output and focuses on post-implementation review orchestration. This splits the monolithic 6-phase skill into two 3–4-phase tools: (1) `/al-dev-develop` focuses on implementation coordination, (2) `/al-dev-review-develop` focuses on multi-reviewer synthesis and final validation.

Trade-off: Adds one skill to learn; enables review workflows to run independently (useful for post-hoc code review, or iterative review gates during development). Each skill becomes narrower and easier to maintain. Requires minor refactoring to split Phase 4 output hand-off.

---

**Merge: /al-dev-explore + /al-dev-perf (as modes of a unified skill)**

Observation: Both /al-dev-explore and /al-dev-perf have identical structure (3 steps, single Explore subagent spawn, dated `.dev/` output), with only one difference: /al-dev-perf adds Step 1a (performance metrics gathering) before spawning the agent. Users must choose between two similar skills when they might naturally combine exploratory investigation with performance scoping.

Suggestion: Unify into `/al-dev-explore --scope={general|performance|refactor}` with mode-specific context preparation. Move perf-specific metadata gathering into the Explore agent's initial context (can be passed as a flag). This reduces the skill list and prevents code duplication of the explore-subagent spawn pattern.

Trade-off: Single skill with three modes; users learn one invoke pattern. Performance exploration becomes a natural option rather than a separate skill. Requires minimal refactoring to Explore agent invocation signature.

---

**Connect: /al-dev-perf integration with downstream skills**

Observation: /al-dev-perf is shown in Layer 1 diagram as a dashed tributary feeding /al-dev-plan and /al-dev-fix with `perf-analysis.md`, but neither downstream skill explicitly loads or consumes this output. /al-dev-plan reads interview-requirements and context but makes no mention of perf findings; /al-dev-fix references only ticket context. The pre-planning skill output is available but unused.

Suggestion: Extend /al-dev-plan Phase 1 (context gathering) to check for `.dev/*-al-dev-perf-perf-analysis.md` and include key performance constraints in architect prompts. Similarly, extend /al-dev-fix non-trivial path to load perf findings when available and pass them to the architect as performance context.

Trade-off: Downstream skills become slightly larger; potential for unused perf context if not available. Improvement in discoverability of performance constraints during planning and quick-fix decisions.

---

**Merge: /al-dev-ticket and /al-dev-support (as modes)**

Observation: Both skills load external ticket data (Freshdesk) and dispatch a single agent, but /al-dev-support is a superset that adds research + reply drafting. The extra functionality could be conditional on a flag. Users manually choose between two related skills when a single skill with options would be clearer.

Suggestion: Consolidate into `/al-dev-ticket --mode={fetch,support,quick}` where `fetch` loads ticket context only, `support` adds research and reply drafting, and `quick` generates a brief summary. This reduces skill count and clarifies the relationship between the two operations.

Trade-off: Skill interface becomes slightly broader; two separate entry points collapse into one. Reduces cognitive load when choosing between ticket workflows.

---

**Extend: Add /al-dev-deploy (post-release workflow)**

Observation: The main development spine ends at /al-dev-commit (git commits), then branches to /al-dev-release-notes, /al-dev-handoff, /commit-recover, and /al-dev-document. But no skill consumes release notes and orchestrates actual deployment to UAT→Prod environments, version tagging, or rollback safeguards. Release notes are generated but no downstream workflow manages the deployment lifecycle.

Suggestion: Create `/al-dev-deploy` skill to consume `/al-dev-release-notes` output and manage environment progression (UAT→Staging→Prod), version tagging, rollback gates, and deployment verification. This completes the workflow chain: `/al-dev-commit` → `/al-dev-release-notes` → `/al-dev-deploy` → environment verification.

Trade-off: Adds scope; only worth building if BC deployment management is a frequent manual task. Requires integration with deployment infrastructure (CI/CD, app centers, environment promotion).

---

**Move: `profile-al-dev-shared/skills/al-dev-align/` → archived or external utility**

Observation: The `al-dev-align/` directory in the skills folder contains only Python code (`check-alignment.py`) and tests, with NO `SKILL.md` file. This makes it an invalid skill and should not occupy a slot in the distributed plugin's skill registry.

Signals: internal path refs (✓), self-audit purpose (✓), no spawned agents (✓).

Suggestion: Move `profile-al-dev-shared/skills/al-dev-align/` to `profile-al-dev-shared/archived/utilities/al-dev-align/` or maintain it as a standalone Python utility outside the plugin structure.

Trade-off: Utility remains available for internal use; removed from the distributed plugin skill catalog.

---

**Move: `/plugin-health-daemon` → `.claude/skills/plugin-health-daemon/`**

Observation: The plugin-health-daemon is an autonomous audit sweep for plugin maintenance (drift detection, quality checks, PR generation). It operates exclusively on the distributed plugin's structure and has no value to external consumers. Like /align-harness-repos, it is a plugin-maintenance tool, not an AL development service.

Signals: internal path refs (✓ — operates on profile-al-dev-shared/), self-audit purpose (✓ — audits the plugin itself), no spawned agents (✓ — calls audit skills, not agents).

Suggestion: Move `profile-al-dev-shared/skills/plugin-health-daemon/` to `.claude/skills/plugin-health-daemon/` alongside /align-harness-repos as project-local maintenance infrastructure.

Trade-off: Skill remains available for internal plugin maintenance; removed from the distributed plugin skill catalog, improving clarity that external consumers should not depend on it.

---

### General observations

The plugin maintains healthy separation of concerns:
- All multi-agent patterns are documented in `knowledge/`
- Separable skill consolidation opportunities (explore+perf, ticket+support) are syntax/mode variations, not architectural conflicts
- Single-use agents are appropriately scoped to domain-specific tasks
- Pre-planning skills (interview/explore/perf) form a coherent optional enrichment layer feeding /al-dev-plan
- Post-commit skills (release-notes/document/handoff/recover) handle orthogonal concerns
- New meta-skills (plan-with-critic-swarm, verify-commits) are well-integrated

### Status summary

**Previous analysis (2026-05-19):** Identified 5 mapping accuracy issues, reported status as resolved.
**Current analysis (2026-05-21):** Full architectural lens analysis across all 20 skills. Identified 6 actionable improvement suggestions (3 high-leverage, 3 medium-leverage). Two low-impact architectural moves also documented. No correctness issues found; plugin design is sound.

### Extension opportunities

1. **Performance remediation workflow**: Perf analysis is discovered but not systematically remediated. Consider `/al-dev-perf-remediation` to consume perf reports and track fix progress (medium priority).
2. **Lint quality gates**: No automation prevents merge if CRITICAL lint items remain. Optional lint-gate check in /al-dev-commit would improve quality assurance (low priority, lint is advisory).
3. **Deployment orchestration**: Post-release management is manual. `/al-dev-deploy` skill would complete the workflow (medium priority if deployment is frequently manual).
