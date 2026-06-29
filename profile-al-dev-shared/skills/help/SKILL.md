---
name: help
description: >-
  Show contextual guidance (Reference, Situation-based routing, Context-driven assessment)
  and recommend workflows.
---

# Command: /help

Contextual guidance for the AL development profile.
Three modes: **Situation** (situation-aware recommendation), **Reference** (capability listing), and **Context** (assess current state and recommend next step).

---

## Usage

```text
/help                          -- assess current state, recommend next step
/help I need to add a feature  -- recommend workflow for your situation
/help commands                 -- list all commands with descriptions
/help skills                   -- list all skills with descriptions
/help agents                   -- list all agents with descriptions
/help all                      -- full capability reference
```

---

## Implementation

### Step 1 — Detect Mode

Parse the user's argument:

- Argument is `commands`, `skills`, `agents`, or `all` → **Reference Mode**
- Argument is a natural language description → **Situation Mode**
- No argument → **Context Mode**

---

### Step 2A — Reference Mode

List capabilities filtered by argument.

**For `commands`:** Output the same table as `skills` mode (an alias for backwards compatibility).

**For `skills`:**

Glob `profile-al-dev-shared/skills/*/SKILL.md` in the profile directory. Extract `description`
from frontmatter of each. Format as a table:

```text
Available Skills (lazy-loaded, invoked with /):

| Skill                 | Description                                           |
|-----------------------|-------------------------------------------------------|
| /interview     | Deep requirements gathering through structured dialog |
| /plan          | Competitive solution design (2-3 architects debate)   |
| /develop-orchestrate | Parallel implementation + 3-specialist code review    |
| /release-notes | End-user release notes from git diff                  |
| /fix           | Lightweight bug fix without approval gates            |
| /commit        | Atomic commit workflow with gitmoji + CC messages     |
| /document      | Generate comprehensive technical documentation        |
| /al-dev-init-context  | Initialize project context document (one-time setup)  |
| /ticket        | Load Freshdesk ticket context for this session        |
| /explore       | Fast codebase exploration with persistent output      |
| /help          | Contextual profile guidance (this skill)              |
```

**For `agents`:**

Glob `profile-al-dev-shared/agents/*.md` in the profile directory. Extract `description` from
frontmatter. Format as a table:

```text
Available Specialist Agents (spawned by lead session via Agent tool):

| Agent                     | Role                                            |
|---------------------------|-------------------------------------------------|
| al-developer              | Implements AL code (tables, pages, codeunits)   |
| solution-architect        | Competitive solution design                     |
| security-reviewer         | Security, permissions, data access review       |
| al-pattern-reviewer       | AL patterns, naming, BC best practices          |
| performance-reviewer      | Query efficiency, N+1, resource usage           |
| interview                 | Deep requirements gathering                     |
| docs-writer               | Technical documentation                         |
| script-engineer    | Python and shell scripts for AL tooling          |
    ```

This agents table is a capability reference. It does not mean
`/help` dispatches every listed agent directly.

**For `all`:** Show all three tables in sequence.

After any reference output, append:

```text
Tip: Run /help <description> for a personalized workflow recommendation.
```

---

### Step 2B — Situation Mode

The user described what they want to do. Recommend the right workflow.

**Step 1: Read description and classify:**

Use `knowledge/workflow-routing.md` to classify complexity before recommending
`/fix`, `/plan`, or `/develop-orchestrate`. Quick reference (full
criteria in that doc): TRIVIAL = single file, obvious fix. SIMPLE = 2-3 files,
pattern exists. MEDIUM = 4-8 files, some design decisions. COMPLEX = new
architecture or unclear requirements.

| Situation | Recommended workflow |
| ----------- | --------------------- |
| Bug, error, wrong behaviour | `/fix` |
| Requirements unclear, exploring ideas | `/interview` |
| Need architecture, multiple objects | `/plan` |
| Have a plan, ready to implement | `/develop-orchestrate` |
| Feature complete, need docs | `/document` |
| Freshdesk ticket for context | `/ticket <id>` first |
| First time in this project | `/al-dev-init-context` first |
| Want to understand existing code | `/explore <question>` |

**Step 2: Check `.dev/` pipeline state to refine:**

Scan for these artifacts (presence/absence informs the recommendation):

- `.dev/project-context.md` — project initialized
- `$(ls .dev/*-interview-requirements.md 2>/dev/null | sort | tail -1)` — requirements gathered
- `$(ls .dev/*-plan-solution-plan.md 2>/dev/null | sort | tail -1)` — solution designed
- `$(ls .dev/*-develop-code-review.md 2>/dev/null | sort | tail -1)` — implementation reviewed

Apply these refinements:

- No `project-context.md` and project has AL files → suggest
  `/al-dev-init-context` before anything else
- `*-interview-requirements.md` exists → skip `/interview`,
  suggest `/plan`
- `*-plan-solution-plan.md` exists → skip `/plan`,
  suggest `/develop-orchestrate`
- Else, if no `.dev/` artifact narrows the path, recommend based on the user's
  stated goal: bug/error → `/fix`; existing-code question → `/explore`;
  design or multi-object feature work → `/plan`

**Step 3: Output recommendation:**

```text
Recommended workflow: /plan

Why: Your request involves multiple objects and design decisions
     (MEDIUM complexity).

Current state:
  .dev/project-context.md                         ✅ found
  *-interview-requirements.md              ❌ not found

Suggested sequence:
  1. /interview "credit limit validation"  -- gather requirements
  2. /plan                                 -- design solution
  3. /develop-orchestrate                  -- implement + review

Or skip to /plan directly if requirements are already clear.
```

---

### Step 2C — Context Mode (no argument)

**Step 1:** Scan `.dev/` for existing workflow artifacts.

**Step 2:** Determine pipeline position and recommend the next step:

| State | Recommendation |
| ------- | --------------- |
| No `.dev/` directory | Run `/al-dev-init-context` to set up project context |
| `project-context.md` only | Describe your goal and run `/help <description>` |
| `*-interview-requirements.md` present | Run `/plan` to design the solution |
| `*-plan-solution-plan.md` present | Run `/develop-orchestrate` to implement |
| `*-develop-code-review.md` present | Run `/commit` for final validation and commit execution, then optionally `/document` for reference documentation |

**Step 3: Output:**

```text
Current project state:

  .dev/project-context.md                              ✅ found
  .dev/2026-05-19-interview-requirements.md     ✅ found (12 REQ: tokens)
  .dev/2026-05-19-plan-solution-plan.md         ✅ found
  .dev/2026-05-19-develop-code-review.md        ❌ not found

Recommendation: Run /develop-orchestrate to implement the solution plan.

The plan exists — the next step is parallel implementation
followed by 3-specialist code review.
```

**Step 4: Always append the quick-reference table:**

```text
Quick reference:
  /fix           -- bug fix, single file, fast iteration
  /interview     -- structured requirements gathering
  /plan          -- competitive architecture design
  /develop-orchestrate -- parallel implementation + code review
  /document      -- generate technical documentation
  /ticket <id>   -- load Freshdesk ticket context
  /al-dev-init-context  -- initialize project context (one-time)
  /commit        -- atomic gitmoji commit workflow
  /explore <q>   -- fast codebase exploration
  /help          -- this skill
```

---

### When a session goes wrong

- **A skill run seems stuck or is heading the wrong way:** stop the current run
  and re-invoke the skill. Multi-phase skills checkpoint to `.dev/` after each
  phase and offer a resume option on the next run, so progress is not lost.
- **A skill name is not recognised:** run `/help` with no argument to list
  the available skills and their entry points rather than guessing a name.
- **You are unsure which step comes next:** run `/help` with no argument
  (Context Mode) to read the current `.dev/` state and get a recommended next step.
