# AL Dev Plugin Map

> A reference tool for understanding skill relationships, agent patterns, and file handoffs in profile-al-dev-shared. This document is for personal gap analysis and extension planning, not onboarding.

**Last updated:** 2026-05-19 (analysis: 5 new suggestions — stale names, label consistency, develop phase gap, document+commit-recover in Layer 1)
**Scope:** Active skills only. Archived items (al-dev-test, test-engineer agents, al-dev-test-coverage-reviewer) excluded. /align-harness-repos moved to `.claude/skills/` (project-local maintenance tool, not distributed).

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

    Phase4 --> Phase5["Phase 5<br/>Compile + verify"]
    Phase5 --> SkillWork2["(skill itself)"]
    SkillWork2 --> CompileAgent["al-dev-diagnostics-fixer ×1"]
    CompileAgent --> SkillWork3["(skill itself)"]
    SkillWork3 --> Output1(["code-review.md"])
    Output1 --> End([End])

    style Phase1 fill:#fff8e1
    style Phase2 fill:#fff8e1
    style Phase3 fill:#fff8e1
    style Phase4 fill:#fff8e1
    style Phase5 fill:#fff8e1
    style SkillWork1 fill:#ffe082
    style SkillWork2 fill:#ffe082
    style SkillWork3 fill:#ffe082
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

---

## Observations

> Generated by /analyze-skill-design on 2026-05-19.
> Run /review-skill-map first if the skill list has changed since this was written.

### Agents used by only one skill

- **al-dev-ticket-agent** — used only by /al-dev-ticket
- **al-dev-support-agent** — used only by /al-dev-support
- **al-dev-interview** (agent) — used only by /al-dev-interview
- **al-dev-docs-writer** — used only by /al-dev-document
- **al-dev-release-notes-writer** — used only by /al-dev-release-notes
- **al-dev-commit-agent-analysis** — used only by /al-dev-commit (Phase 1; read-only)
- **al-dev-commit-agent-execute** — used only by /al-dev-commit (Phase 2; runs git commits)
- **al-dev-diagnostics-fixer** — primary caller is /al-dev-lint; also invoked by /al-dev-develop in its compile-verify phase (not shown in drill-down — see Connect suggestion below)
- **al-dev-commit-recover-verifier** — used only by /commit-recover (mislabelled as `commit-learn-verifier` in current drill-down — see Map accuracy suggestion below)

### Skills with no dedicated agent (skill does the work itself)

- **/align-harness-repos** — runs an external Python alignment script; all logic is inline (project-local, not distributed)
- **/al-dev-handoff** — file copy + prompt assembly; purely shell/file operations
- **/al-dev-help** — reads `.dev/` context files and presents guidance inline

### Potential shared agents (documented patterns)

- **Explore subagent** — invoked by /al-dev-investigate (×2 parallel), /al-dev-explore (×1), /al-dev-perf (×1); canonical template in `knowledge/explore-subagent-pattern.md` ← implemented
- **al-dev-developer** — spawned by /al-dev-fix (×1), /al-dev-develop (×2-3); patterns in `knowledge/architect-invocation-patterns.md` ← implemented
- **al-dev-solution-architect** — spawned by /al-dev-plan (×2-3 competitive debate) and /al-dev-fix (×1 quick analysis); patterns in `knowledge/architect-invocation-patterns.md` ← implemented
- **Three-reviewer panel** (al-dev-security-reviewer + al-dev-expert-reviewer + al-dev-performance-reviewer) — parallel composition in /al-dev-develop; canonical definition in `knowledge/review-panel-pattern.md` ← implemented

### Previously implemented suggestions

three-reviewer panel extract, /al-dev-autonomous merge into --autonomous flag, explore backbone + architect invocation patterns, integrated ticket lookup, /align-harness-repos move to project-local, Layer 1 pre-plan tributaries (explore/interview/perf), post-commit nodes (release-notes/handoff), lint→fix feedback loop, inventory clarity update.

### Architectural suggestions

**Map accuracy: stale agent and skill names in two drill-downs** ← highest leverage
Observation: Two agent renames are not reflected in the map. (1) The skill was renamed from `/commit-learn` to `/commit-recover` and the agent from `commit-learn-verifier` to `al-dev-commit-recover-verifier` (confirmed by git history and `agents/al-dev-commit-recover-verifier.md`). The drill-down heading still reads `### /commit-learn` with label `commit-learn-verifier`. (2) The `al-dev-release-notes` drill-down labels the agent `al-dev-release-notes-agent` but the actual agent file is `al-dev-release-notes-writer.md` (type `al-dev-shared:al-dev-release-notes-writer`).
Suggestion: Rename `### /commit-learn` → `### /commit-recover`, `commit-learn-verifier` → `al-dev-commit-recover-verifier`, and `al-dev-release-notes-agent` → `al-dev-release-notes-writer` in the respective drill-downs. Update inventory entry.
Trade-off: Pure documentation accuracy fix; no architectural change. Wrong names break the map's utility as a navigation aid.

**Connect: Inconsistent Explore subagent labeling across drill-downs**
Observation: /al-dev-investigate labels the spawned agent `al-dev-explore ×2 parallel`, while /al-dev-explore and /al-dev-perf label the same agent type `Explore subagent ×1`. All three callers reference the shared pattern in `knowledge/explore-subagent-pattern.md`, but the inconsistent naming makes the shared relationship harder to spot when reading the map.
Suggestion: Standardise all three drill-downs to use a consistent label — either `al-dev-shared:al-dev-explore ×N` or `Explore subagent ×N` — matching whichever label the knowledge file uses as canonical.
Trade-off: Cosmetic fix only; no functional change. Makes the shared-agent relationship immediately visible.

**Connect: /al-dev-develop — undocumented compile-verify phase**
Observation: The skill body (`SKILL.md` line 495) explicitly spawns `al-dev-diagnostics-fixer` during its compile-lint phase. The Layer 2 drill-down ends at Phase 4 "Synthesise" → `code-review.md` without showing this step, making the drill-down inaccurate and the agent inventory entry for `al-dev-diagnostics-fixer` incomplete.
Suggestion: Add a Phase 5 "Compile + verify" node to the /al-dev-develop drill-down showing `al-dev-diagnostics-fixer ×1` between the reviewer synthesis and the final `code-review.md` output.
Trade-off: Drill-down grows one phase and accurately reflects actual skill execution. No functional change.

**Extend: Layer 1 — /al-dev-document as post-commit output**
Observation: /al-dev-document is a full 3-phase skill with its own agent (`al-dev-docs-writer`) but is entirely absent from Layer 1. It has a natural home as a dashed post-commit node alongside /al-dev-release-notes and /al-dev-handoff — all three are optional steps taken after code is committed.
Suggestion: Add a dashed node `al-dev-document` after `✓ git commit` in Layer 1, with a dashed arrow and output node `✓ documentation`. Style to match the existing post-commit nodes.
Trade-off: Layer 1 gains one more post-commit node; the post-development lifecycle becomes complete.

**Extend: Layer 1 — /commit-recover as conditional post-commit recovery path**
Observation: /commit-recover reads `.dev/commit-integrity.log` written by /al-dev-commit during its execution pass, but does not appear anywhere in Layer 1. Unlike release-notes and handoff (always optional), this skill activates only when the integrity log has entries — a conditional recovery path.
Suggestion: Add a conditional dashed node `commit-recover` after `✓ git commit`, labelled `(on integrity error)`. This makes the failure-recovery path visible at the Layer 1 lifecycle level alongside the happy-path post-commit skills.
Trade-off: Adds one post-commit node with a conditional qualifier; minimal visual cost, significant clarity gain for recovery scenarios.

### Extension opportunities

None beyond the five suggestions above. The plugin architecture is well-optimised; remaining gaps are documentation accuracy and Layer 1 completeness for skills that already exist.
