---
name: al-dev-help
description: Show contextual guidance and recommend workflows.
argument-hint: "[workflow name or situation description]"
---

# Command: /al-dev-help

Contextual guidance for the AL development profile.
Two modes: **situation-aware recommendation** and **capability reference**.

---

## Usage

```text
/al-dev-help                          -- assess current state, recommend next step
/al-dev-help I need to add a feature  -- recommend workflow for your situation
/al-dev-help commands                 -- list all commands with descriptions
/al-dev-help skills                   -- list all skills with descriptions
/al-dev-help agents                   -- list all agents with descriptions
/al-dev-help all                      -- full capability reference
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

**For `commands`:**

Glob `skills/*/SKILL.md` in the profile directory. For each file, read the
`description` field from YAML frontmatter. Format as a table:

```text
Available Skills:

| Skill                 | Description                                          |
|-----------------------|------------------------------------------------------|
| /al-dev-fix           | Lightweight bug fix without approval gates           |
| /al-dev-commit        | Atomic commit workflow with gitmoji + CC messages    |
| /al-dev-document      | Generate comprehensive technical documentation       |
| /al-dev-init-context  | Initialize project context document (one-time setup) |
| /al-dev-ticket        | Load Freshdesk ticket context for this session       |
| /al-dev-help          | Contextual profile guidance (this skill)             |
| /al-dev-explore       | Fast codebase exploration with persistent output     |
| /al-dev-interview     | Deep requirements gathering through structured dialog |
| /al-dev-plan          | Competitive solution design (2-3 architects debate)  |
| /al-dev-develop       | Parallel implementation + 4-specialist code review   |
| /al-dev-test          | Comprehensive test suite with 4 parallel engineers   |
| /al-dev-release-notes | End-user release notes from git diff                 |
```

**For `skills`:**

Glob `skills/*/SKILL.md` in the profile directory. Extract `description`
from frontmatter of each. Format as a table:

```text
Available Skills (lazy-loaded, invoked with /):

| Skill                 | Description                                           |
|-----------------------|-------------------------------------------------------|
| /al-dev-interview     | Deep requirements gathering through structured dialog |
| /al-dev-plan          | Competitive solution design (2-3 architects debate)   |
| /al-dev-develop       | Parallel implementation + 4-specialist code review    |
| /al-dev-test          | Comprehensive test suite with 4 parallel engineers    |
| /al-dev-release-notes | End-user release notes from git diff                  |
| /al-dev-fix           | Lightweight bug fix without approval gates            |
| /al-dev-commit        | Atomic commit workflow with gitmoji + CC messages     |
| /al-dev-document      | Generate comprehensive technical documentation        |
| /al-dev-init-context  | Initialize project context document (one-time setup)  |
| /al-dev-ticket        | Load Freshdesk ticket context for this session        |
| /al-dev-explore       | Fast codebase exploration with persistent output      |
| /al-dev-help          | Contextual profile guidance (this skill)              |
```

**For `agents`:**

Glob `agents/*.md` in the profile directory. Extract `description` from
frontmatter. Format as a table:

```text
Available Specialist Agents (spawned by lead session via Agent tool):

| Agent                     | Role                                            |
|---------------------------|-------------------------------------------------|
| al-developer              | Implements AL code (tables, pages, codeunits)   |
| solution-architect        | Competitive solution design                     |
| security-reviewer         | Security, permissions, data access review       |
| al-expert-reviewer        | AL patterns, naming, BC best practices          |
| performance-reviewer      | Query efficiency, N+1, resource usage           |
| test-coverage-reviewer    | Test adequacy and missing scenarios             |
| unit-test-engineer        | Unit test development                           |
| integration-test-engineer | Cross-object integration tests                  |
| scenario-test-engineer    | End-to-end scenario test development            |
| edge-case-test-engineer   | Boundary and error case test development        |
| interview                 | Deep requirements gathering                     |
| docs-writer               | Technical documentation                         |
| python-script-engineer    | Python scripts for AL tooling                   |
```

**For `all`:** Show all three tables in sequence.

After any reference output, append:

```text
Tip: Run /al-dev-help <description> for a personalized workflow recommendation.
```

---

### Step 2B — Situation Mode

The user described what they want to do. Recommend the right workflow.

**Step 1: Read description and classify:**

| Situation | Recommended workflow |
| ----------- | --------------------- |
| Bug, error, wrong behaviour | `/al-dev-fix` |
| Requirements unclear, exploring ideas | `/al-dev-interview` |
| Need architecture, multiple objects | `/al-dev-plan` |
| Have a plan, ready to implement | `/al-dev-develop` |
| Implementation done, need tests | `/al-dev-test` |
| Feature complete, need docs | `/al-dev-document` |
| Freshdesk ticket for context | `/al-dev-ticket <id>` first |
| First time in this project | `/al-dev-init-context` first |
| Want to understand existing code | `/al-dev-explore <question>` |

**Step 2: Check `.dev/` pipeline state to refine:**

Scan for these artifacts (presence/absence informs the recommendation):

- `.dev/project-context.md` — project initialized
- `.dev/01-requirements.md` — requirements gathered
- `.dev/02-solution-plan.md` — solution designed
- `.dev/03-code-review.md` — implementation reviewed
- `.dev/05-test-plan.md` — tests written

Apply these refinements:

- No `project-context.md` and project has AL files → suggest
  `/al-dev-init-context` before anything else
- `01-requirements.md` exists → skip `/al-dev-interview`,
  suggest `/al-dev-plan`
- `02-solution-plan.md` exists → skip `/al-dev-plan`,
  suggest `/al-dev-develop`
- `03-code-review.md` exists but no `05-test-plan.md` → suggest
  `/al-dev-test`

**Step 3: Output recommendation:**

```text
Recommended workflow: /plan

Why: Your request involves multiple objects and design decisions
     (MEDIUM complexity).

Current state:
  .dev/project-context.md  ✅ found
  .dev/01-requirements.md  ❌ not found

Suggested sequence:
  1. /al-dev-interview "credit limit validation"  -- gather requirements
  2. /al-dev-plan                                 -- design solution
  3. /al-dev-develop                              -- implement + review
  4. /al-dev-test                                 -- if business-critical

Or skip to /al-dev-plan directly if requirements are already clear.
```

---

### Step 2C — Context Mode (no argument)

**Step 1:** Scan `.dev/` for existing workflow artifacts.

**Step 2:** Determine pipeline position and recommend the next step:

| State | Recommendation |
| ------- | --------------- |
| No `.dev/` directory | Run `/al-dev-init-context` to set up project context |
| `project-context.md` only | Describe your goal and run `/al-dev-help <description>` |
| `01-requirements.md` present | Run `/al-dev-plan` to design the solution |
| `02-solution-plan.md` present | Run `/al-dev-develop` to implement |
| `03-code-review.md` present | Run `/al-dev-test` if coverage matters |
| `05-test-plan.md` present | Run `/al-dev-document` for reference documentation |

**Step 3: Output:**

```text
Current project state:

  .dev/project-context.md   ✅ found
  .dev/01-requirements.md   ✅ found (12 REQ: tokens)
  .dev/02-solution-plan.md  ✅ found
  .dev/03-code-review.md    ❌ not found
  .dev/05-test-plan.md      ❌ not found

Recommendation: Run /al-dev-develop to implement the solution plan.

The plan exists — the next step is parallel implementation
followed by 4-specialist code review.
```

**Step 4: Always append the quick-reference table:**

```text
Quick reference:
  /al-dev-fix           -- bug fix, single file, fast iteration
  /al-dev-interview     -- structured requirements gathering
  /al-dev-plan          -- competitive architecture design
  /al-dev-develop       -- parallel implementation + code review
  /al-dev-test          -- 4-engineer parallel test suite
  /al-dev-document      -- generate technical documentation
  /al-dev-ticket <id>   -- load Freshdesk ticket context
  /al-dev-init-context  -- initialize project context (one-time)
  /al-dev-commit        -- atomic gitmoji commit workflow
  /al-dev-explore <q>   -- fast codebase exploration
  /al-dev-help          -- this skill
```
