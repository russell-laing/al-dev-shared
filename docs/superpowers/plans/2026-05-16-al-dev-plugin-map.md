# AL Dev Plugin Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate `docs/al-dev-plugin-map.md` — a reference document with Mermaid diagrams showing the active skills, agents, and their relationships in the profile-al-dev-shared plugin.

**Architecture:** Two-layer visual approach: a lifecycle overview showing entry points and main development flow, then seven per-skill drill-down diagrams detailing internal phases, agent spawns, and file outputs. Observations section with placeholder annotations ready for analysis.

**Tech Stack:** Mermaid flowcharts (TD for overview, LR for skill detail), GitHub-flavored Markdown, Mermaid syntax validation.

---

## File Structure

- **Create:** `docs/al-dev-plugin-map.md` — main plugin map document
- **Reference:** `profile-al-dev-shared/markdown/md-mermaid-helper.md` — Mermaid diagram conventions
- **Verify:** Line count and diagram syntax after creation

---

### Task 1: Read Mermaid Helper and Establish Diagram Conventions

**Files:**
- Reference: `profile-al-dev-shared/markdown/md-mermaid-helper.md`

- [ ] **Step 1: Read Mermaid helper guide**

Run: `cat docs/../profile-al-dev-shared/markdown/md-mermaid-helper.md | head -100`

This will establish:
- Naming conventions for node types (rounded rectangles for skills, diamonds for decisions, stadium shapes for outputs)
- Spacing/indentation rules for Mermaid code blocks
- Cross-diagram linking patterns (if any)
- Color/styling guidelines for diagram consistency

- [ ] **Step 2: Document observations**

Note the key conventions in a comment at the top of the document draft:
- Skills always use rounded rectangle syntax: `(skill-name)`
- Decision gates use diamond: `{question?}`
- File outputs use stadium/pill: `([filename.md])`
- Flowchart TD (top-down) for lifecycle, LR (left-to-right) for skill detail

---

### Task 2: Create Document Structure and Lifecycle Overview Diagram

**Files:**
- Create: `docs/al-dev-plugin-map.md`

- [ ] **Step 1: Write document header and introduction**

```markdown
# AL Dev Plugin Map

> A reference tool for understanding skill relationships, agent patterns, and file handoffs in profile-al-dev-shared. This document is for personal gap analysis and extension planning, not onboarding.

**Last updated:** 2026-05-16  
**Scope:** Active skills only. Archived items (al-dev-test, test-engineer agents, al-dev-test-coverage-reviewer) excluded.

---

## Layer 1: Lifecycle Overview

This diagram shows the three entry paths and how they connect through the main development spine.
```

- [ ] **Step 2: Write lifecycle overview diagram**

```markdown
```mermaid
flowchart TD
    %% Entry points
    Ticket["(al-dev-ticket)"] -->|ticket-context.md| Support["(al-dev-support)"]
    Investigate["(al-dev-investigate)"]
    FixDirect["(al-dev-fix)"]
    
    %% Investigation path branches
    Investigate -->|explore-findings.md| Decision1{Needs<br/>full plan?}
    Decision1 -->|Yes| Plan["(al-dev-plan)"]
    Decision1 -->|No| Fix["(al-dev-fix)"]
    
    %% Main development spine
    Plan -->|solution-plan.md| Develop["(al-dev-develop)"]
    Fix -->|AL code| Commit["(al-dev-commit)"]
    Develop -->|code-review.md| Commit
    
    %% Complexity gate within plan
    Note["Trivial requests<br/>route to /fix"] -.-> Plan
    
    %% Outputs
    Commit --> Git["✓ git commit"]
    Support --> Reply["✓ customer reply"]
    
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

- [ ] **Step 3: Add Layer 2 introduction**

```markdown
---

## Layer 2: Per-Skill Drill-Downs

Each skill is shown with its internal phases, spawned agents, and key outputs. Agents are referenced by their full type name (e.g., `al-dev-shared:al-dev-developer`).

### Notation

- **Phase**: Numbered step inside the skill
- **Agent**: Which agent (or skill itself) executes the phase
- **Pattern**: ×1 (serial), ×2-3 (parallel), ×N (variable count)
- **Output**: File written to `.dev/` or code generated
```

---

### Task 3: Write Per-Skill Drill-Down Diagrams (Part 1: Lightweight Skills)

**Files:**
- Modify: `docs/al-dev-plugin-map.md` (append drill-down diagrams)

- [ ] **Step 1: Write al-dev-ticket skill diagram**

```markdown
### /al-dev-ticket

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Fetch & write context"]
    Phase1 --> Agent1["al-dev-ticket-agent ×1"]
    Agent1 --> Output1["([ticket-context.md])"]
    Output1 --> End([End])
    
    style Phase1 fill:#e3f2fd
    style Agent1 fill:#bbdefb
    style Output1 fill:#90caf9
```
- [ ] **Step 2: Write al-dev-support skill diagram**

```markdown
### /al-dev-support

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Research & draft reply"]
    Phase1 --> Agent1["al-dev-support-agent ×1"]
    Agent1 --> Output1["([customer reply])"]
    Output1 --> End([End])
    
    style Phase1 fill:#e3f2fd
    style Agent1 fill:#bbdefb
    style Output1 fill:#90caf9
```

---

### Task 4: Write Per-Skill Drill-Down Diagrams (Part 2: Investigation and Fix)

**Files:**
- Modify: `docs/al-dev-plugin-map.md` (append drill-down diagrams)

- [ ] **Step 1: Write al-dev-investigate skill diagram**

```markdown
### /al-dev-investigate

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Form hypotheses"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Test hypotheses"]
    Phase2 --> Agent1["al-dev-explore ×2 parallel"]
    Agent1 --> Phase3["Phase 3<br/>Synthesise findings"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1["([explore-findings.md])"]
    Output1 --> End([End])
    
    style Phase1 fill:#f3e5f5
    style Phase2 fill:#f3e5f5
    style Phase3 fill:#f3e5f5
    style SkillWork1 fill:#e1bee7
    style SkillWork2 fill:#e1bee7
    style Agent1 fill:#ce93d8
    style Output1 fill:#ba68c8
```

- [ ] **Step 2: Write al-dev-fix skill diagram showing both paths**

```markdown
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
    Phase1C --> ArchAgent["al-dev-solution-architect ×1<br/>5 min"]
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

---

### Task 5: Write Per-Skill Drill-Down Diagrams (Part 3: Planning and Development)

**Files:**
- Modify: `docs/al-dev-plugin-map.md` (append drill-down diagrams)

- [ ] **Step 1: Write al-dev-plan skill diagram**

```markdown
### /al-dev-plan

**Competitive design phase:** Multiple architects propose approaches in parallel; the skill synthesises the winner into a solution plan.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Context gather"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Competing designs"]
    Phase2 --> ArchAgents["al-dev-solution-architect ×2-3<br/>parallel"]
    ArchAgents --> Phase3["Phase 3<br/>Synthesise winner"]
    Phase3 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1["([solution-plan.md])"]
    Output1 --> End([End])
    
    style Phase1 fill:#fff3e0
    style Phase2 fill:#fff3e0
    style Phase3 fill:#fff3e0
    style SkillWork1 fill:#ffe0b2
    style SkillWork2 fill:#ffe0b2
    style ArchAgents fill:#ffcc80
    style Output1 fill:#ffb74d
```

- [ ] **Step 2: Write al-dev-develop skill diagram**

```markdown
### /al-dev-develop

**Three-reviewer panel:** Security, AL expert, and performance reviewers run in parallel, then the skill synthesises findings.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Read plan"]
    Phase1 --> SkillWork1["(skill itself)"]
    SkillWork1 --> Phase2["Phase 2<br/>Implement"]
    Phase2 --> DevAgent["al-dev-developer ×2-3<br/>parallel"]
    DevAgent --> Phase3["Phase 3<br/>Review<br/>in parallel"]
    
    Phase3 --> SecReview["al-dev-security-reviewer ×1"]
    Phase3 --> ExpertReview["al-dev-expert-reviewer ×1"]
    Phase3 --> PerfReview["al-dev-performance-reviewer ×1"]
    
    SecReview --> Phase4["Phase 4<br/>Synthesise"]
    ExpertReview --> Phase4
    PerfReview --> Phase4
    
    Phase4 --> SkillWork2["(skill itself)"]
    SkillWork2 --> Output1["([code-review.md])"]
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

---

### Task 6: Write Per-Skill Drill-Down Diagrams (Part 4: Commit)

**Files:**
- Modify: `docs/al-dev-plugin-map.md` (append drill-down diagram)

- [ ] **Step 1: Write al-dev-commit skill diagram**

```markdown
### /al-dev-commit

**Two-pass execution:** Analysis pass builds commit groups and messages; execution pass runs the commits with hook support.

```mermaid
flowchart LR
    Start([Start]) --> Phase1["Phase 1<br/>Analysis pass"]
    Phase1 --> Agent1["al-dev-commit-agent ×1"]
    Agent1 --> Interim["(commit groups<br/>+ messages)"]
    Interim --> Phase2["Phase 2<br/>Execution pass"]
    Phase2 --> Agent2["al-dev-commit-agent ×1"]
    Agent2 --> Output1["(git commits)"]
    Output1 --> End([End])
    
    style Phase1 fill:#e0f2f1
    style Phase2 fill:#e0f2f1
    style Agent1 fill:#80cbc4
    style Agent2 fill:#80cbc4
    style Output1 fill:#26a69a
```

---

### Task 7: Add Observations Section with Placeholder Annotations

**Files:**
- Modify: `docs/al-dev-plugin-map.md` (append observations section)

- [ ] **Step 1: Add observations section structure**

```markdown
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
```

---

### Task 8: Verify Document Structure and Syntax

**Files:**
- Verify: `docs/al-dev-plugin-map.md`

- [ ] **Step 1: Check file exists and has expected sections**

Run: `grep -c "^### /" docs/al-dev-plugin-map.md`

Expected output: `7` (seven skills: ticket, support, investigate, fix, plan, develop, commit)

- [ ] **Step 2: Verify Mermaid code blocks are well-formed**

Run: `grep -c "^'mermaid$" docs/al-dev-plugin-map.md`

Expected: At least 8 blocks (1 lifecycle + 7 skills)

- [ ] **Step 3: Check for excluded items (must not appear)**

Run: `grep -E "(al-dev-test|test-engineer|test-coverage-reviewer|al-dev-align|al-dev-autonomous|al-dev-document|al-dev-explore|al-dev-handoff|al-dev-help|al-dev-interview|al-dev-lint|al-dev-perf|al-dev-release-notes|commit-learn)" docs/al-dev-plugin-map.md`

Expected: No output (no exclusions present)

- [ ] **Step 4: Count lines and verify non-empty**

Run: `wc -l docs/al-dev-plugin-map.md`

Expected: ~300+ lines (comprehensive diagrams + text)

---

### Task 9: Commit the Plugin Map Document

**Files:**
- Commit: `docs/al-dev-plugin-map.md` (new file)

- [ ] **Step 1: Stage the file**

Run: `git -C /Users/russelllaing/al-dev-shared add docs/al-dev-plugin-map.md`

- [ ] **Step 2: Create commit**

Run:
```bash
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add al-dev plugin map with lifecycle and skill diagrams"
```

Expected: Commit succeeds with message about plugin map creation.

- [ ] **Step 3: Verify commit**

Run: `git -C /Users/russelllaing/al-dev-shared log --oneline -1`

Expected: Latest commit shows plugin map commit message.

---

## Self-Review Checklist

Before submitting for execution, verify:

1. **Spec coverage:**
   - ✓ Lifecycle overview diagram (Layer 1) with three entry paths (ticket, investigate, fix)
   - ✓ Main development spine (plan → develop → commit)
   - ✓ Seven per-skill drill-downs (ticket, support, investigate, fix, plan, develop, commit)
   - ✓ File handoffs labelled on edges (ticket-context.md, explore-findings.md, solution-plan.md, code-review.md)
   - ✓ Terminal nodes (git commit, customer reply)
   - ✓ Complexity gate on plan routing trivial to fix
   - ✓ Observations section with placeholders

2. **Exclusions verified:**
   - ✓ al-dev-test excluded
   - ✓ Test-engineer agents excluded
   - ✓ al-dev-test-coverage-reviewer excluded
   - ✓ Peripheral skills excluded (align, autonomous, document, explore, handoff, help, interview, lint, perf, release-notes, commit-learn)

3. **Diagram syntax:**
   - ✓ All diagrams use Mermaid syntax (flowchart TD/LR)
   - ✓ Node shapes follow conventions (rounded = skills, diamond = decisions, stadium = outputs)
   - ✓ Phase numbering consistent and sequential

4. **No placeholders:**
   - ✓ All diagram content complete
   - ✓ No "TBD", "TODO", or "fill in" in Mermaid code
   - ✓ Observations section intentionally has placeholders (by spec requirement)

5. **File structure:**
   - ✓ Document saved to correct location: `docs/al-dev-plugin-map.md`
   - ✓ Sections ordered: Header → Lifecycle → Per-skill diagrams → Observations
