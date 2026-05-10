# Design: Harness-Agnostic al-dev-shared Plugin

**Date:** 2026-05-11
**Status:** Approved

---

## Problem

`al-dev-shared` is the shared skill/agent library for AL/BC development, consumed by both
`profile-claude-al-dev` (Claude Code) and `profile-copilot-al-dev` (Copilot CLI). Currently
its skill and agent bodies contain deep Claude Code-specific assumptions:

- `~/.claude/` paths for plugins, settings, tasks, and session transcripts
- Claude Code tool names (`AskUserQuestion`, `Read`, `Write`, `Edit`, etc.)
- `CLAUDE.md` by name as the project instructions file
- Claude Code MCP naming convention (`mcp__plugin_profile-claude-al-dev_*`)
- `subagent_type: Explore` spawn syntax
- "Restart Claude Code" user messages

This prevents the shared library from being used unmodified by Copilot CLI or any future
AI coding agent harness.

---

## Goal

Make `al-dev-shared` skill and agent **bodies** harness-agnostic so they can be loaded and
executed correctly by any AI coding agent that has a compliant profile plugin.

Agent **frontmatter** (tool lists, model names) remains harness-specific and is out of scope.

---

## Architecture

```
al-dev-shared                        # Harness-agnostic domain library
  profile-al-dev-shared/
    skills/                          # AL/BC workflow logic, abstract references
    agents/                          # AL/BC specialist agents, abstract language
    knowledge/
      harness-concepts.md            # NEW: abstraction vocabulary contract
      ... (domain knowledge)

profile-claude-al-dev                # Claude Code wiring
  CLAUDE.md                          # Harness mapping section + project instructions
  skills/
    al-dev-init-context/             # MOVED from al-dev-shared
    al-dev-review/                   # MOVED from al-dev-shared
  agents/
    al-dev-session-analyst.md        # MOVED from al-dev-shared
  knowledge/
    task-coordination.md             # MOVED from al-dev-shared

profile-copilot-al-dev               # Copilot CLI wiring
  AGENTS.md                          # Harness mapping section + project instructions
  skills/
    al-dev-init-context/             # NEW: Copilot equivalent
    al-dev-review/                   # NEW: Copilot equivalent
  agents/
    al-dev-session-analyst.md        # NEW: Copilot equivalent
```

**Key principle:** When a skill in `al-dev-shared` references a generic concept such as
"project instructions file" or "USER_GATE", the profile's always-loaded instructions file
(CLAUDE.md / AGENTS.md) defines the concrete harness mapping. Skills never name the harness.

---

## Abstraction Contract — `knowledge/harness-concepts.md`

A new file defining the generic vocabulary that all `al-dev-shared` skills and agents write to.
Profile repos implement the concrete mappings in their instructions files.

### Generic Concepts

| Concept | Description | Claude Code | Copilot CLI |
|---|---|---|---|
| **project instructions file** | The file that provides the AI agent with project-specific instructions | `CLAUDE.md` | `AGENTS.md` |
| **harness settings file** | The file where harness-wide settings (e.g. API keys) are stored | `~/.claude/settings.json` | `~/.copilot/settings.json` |
| **plugin path** (`AL_DEV_SHARED_PLUGIN_ROOT`) | The installed path of the al-dev-shared plugin | `~/.claude/plugins/al-dev-shared/profile-al-dev-shared` | `~/.copilot/installed-plugins/<id>/profile-al-dev-shared` |
| **USER_GATE** | A blocking user-confirmation point; never continue past this without a user response | `AskUserQuestion` tool | `ask_user` tool |
| **explore agent** | A fast parallel exploration agent | `subagent_type: Explore` | `agent_type: "explore"` |
| **restart the agent** | Instruction to the user to start a new AI coding session | "Restart Claude Code" | "start a new Copilot CLI session" |
| **MCP: al-mcp-server** | AL symbol lookup, object definitions, references | `mcp__plugin_profile-claude-al-dev_al-mcp-server__<tool>` | `al-mcp-server-<tool>` |
| **MCP: bc-code-intelligence** | BC knowledge, specialist consultation, code analysis | `mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp__<tool>` | `bc-code-intelligence-mcp-<tool>` |
| **MCP: microsoft-docs** | Microsoft documentation search and fetch | `mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__<tool>` | `microsoft_docs_mcp-<tool>` |

### USER_GATE Semantics

`USER_GATE` is a hard blocking point. Regardless of harness:

- The agent MUST stop and present the question/choice to the user
- The agent MUST NOT continue until a user response is received
- The question SHOULD include options where applicable
- There is no timeout — wait indefinitely

### AL_DEV_SHARED_PLUGIN_ROOT

Each profile's instructions file defines `AL_DEV_SHARED_PLUGIN_ROOT`. Skills use it for
validator script discovery:

```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/<skill-name>/validate-*.py"
```

### Skill Author Guidelines

When writing skills for `al-dev-shared`:

- Use generic concept names from this table — never harness-specific names
- Use `USER_GATE` for any blocking approval or confirmation point
- Use `AL_DEV_SHARED_PLUGIN_ROOT` for any path into the plugin
- Reference MCP tools by capability name ("call the al-mcp-server MCP tool") — never
  by raw harness-specific tool ID
- Use plain English for file operations ("read the file", "write to disk")

---

## What Moves Out of al-dev-shared

### Moved to `profile-claude-al-dev`

These items depend on Claude Code-specific infrastructure and have no generic equivalent.

| Item | Reason |
|---|---|
| `skills/al-dev-init-context/` | Creates `.claude/rules/` symlinks; Claude Code session setup |
| `skills/al-dev-review/` | Reads `~/.claude/projects/*.jsonl` session transcripts |
| `agents/al-dev-session-analyst.md` | Analyses Claude Code `.jsonl` signal data |
| `knowledge/task-coordination.md` | Claude Code Tasks system (`~/.claude/tasks/`, `CLAUDE_CODE_TASK_LIST_ID`) |

Content moved verbatim. References to `al-dev-session-analyst` within Claude profile skills
updated to use `profile-claude-al-dev:al-dev-session-analyst` namespace.

### New Equivalents in `profile-copilot-al-dev`

#### `skills/al-dev-init-context/SKILL.md`

Deliverables:
1. Check for and create root `AGENTS.md` (project instructions file) if absent, using project
   metadata (publisher, object ID range, app name, description)
2. Validate or create `.dev/project-context.md` with tech stack, naming conventions,
   object number ranges, architecture patterns, and build/test commands
3. Check MCP availability (al-mcp-server, bc-code-intelligence-mcp, microsoft-docs-mcp)
4. Ensure `.dev/` is gitignored
5. Confirm publisher/app metadata (app.json or equivalent)
6. Report summary of what was set up and what still needs manual attention

#### `skills/al-dev-review/SKILL.md`

Queries the Copilot CLI SQL `session_store` database to analyse friction patterns from
recent sessions on this project.

Data sources and what they reveal:
- `turns` (user_message, assistant_response) — clarification requests, repeated questions,
  scope confusion, rejected outputs
- `checkpoints` — phase completion patterns, what was completed vs. abandoned
- `session_files` — which files were frequently edited (churn signals)
- `search_index` FTS — error, failure, blocked, retry, unclear patterns

Explicitly **not** equivalent to Claude's JSONL review for:
- Raw tool call/result errors
- Permission denial counts
- Live skill attribution

The skill should acknowledge this scope difference in its output.

Spawns `profile-copilot-al-dev:al-dev-session-analyst` agent.

#### `agents/al-dev-session-analyst.md`

Receives:
- Current project repository path
- SQL query results from session_store (passed in prompt by skill)

Produces `.dev/$(date)-al-dev-review-findings.md` with:
- Friction patterns identified from session data
- Frequently edited files / churn signals
- Repeated clarification / error patterns
- Recommendations targeting project `AGENTS.md` and `.dev/` artifacts

---

## In-Place Changes to al-dev-shared

### Skill Bodies

#### `al-dev-commit`

- Every reference to `CLAUDE.md` → "project instructions file"
- Load sequence (`~/claude-configs/CLAUDE.md`, `~/claude-configs/profile-claude-al-dev/CLAUDE.md`,
  `./CLAUDE.md`) → "load the project instructions file from your harness's standard locations"
- Remove "Generated with Claude Code" from commit message rules

#### `al-dev-handoff`

- "new Claude Code session" → "new AI coding agent session"
- `.claude` path check → omit harness-specific path; check for project instructions file instead
- "Paste this into a new Claude Code session" → "paste this into a new session in your AI
  coding harness"

#### `al-dev-support`, `al-dev-ticket`

- `~/.claude/settings.json` → "harness settings file"
- "Restart Claude Code after saving" → "restart your AI coding agent session after saving"
- Reference to `profile-claude-al-dev/freshdesk-readonly-setup.md` → "see your harness
  profile's Freshdesk setup guide"

#### `al-dev-autonomous`, `al-dev-develop`, `al-dev-plan`, `al-dev-test`, `al-dev-interview`

- `find ~/.claude/plugins -name "validate-*.py"` →
  ```bash
  VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/<skill-name>/validate-<name>.py"
  ```
- `subagent_type: Explore` (where present in plan) → "spawn an explore agent"

#### `al-dev-explore`, `al-dev-investigate`, `al-dev-perf`

- `subagent_type: Explore` in spawn blocks → replace with harness-neutral spawn template:
  ```
  Spawn an explore agent:
    purpose: <purpose>
    prompt: <prompt>
    output: <expected output>
  ```

#### `al-dev-init-context`, `al-dev-review`

- **Removed** from al-dev-shared (moved to profile repos)

### Agent Bodies

#### `al-dev-developer`

- All `AskUserQuestion` references → "**USER_GATE** — ask the user [question/options]"
- "Follow AL coding standards from profile CLAUDE.md" →
  "Follow AL coding standards from the project instructions file"

#### `al-dev-interview`

- All `AskUserQuestion` references → "**USER_GATE** — ask the user [question/options]"
- Agent body requirement "Use AskUserQuestion for EVERY question" →
  "Use USER_GATE for every question"

#### `al-dev-solution-architect`

- All `mcp__plugin_profile-claude-al-dev_al-mcp-server__*` → "call the al-mcp-server MCP tool: `<function>`"
- All `mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp__*` → "call the bc-code-intelligence MCP tool: `<function>`"
- All `mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__*` → "call the microsoft-docs MCP tool: `<function>`"
- "See CLAUDE.md" / "See CLAUDE.md section X" → "See the project instructions file section X"
- `Tools Available: Read, Write, Glob, Grep` → keep as abstract English description

#### `al-dev-support-agent`

- Same MCP name abstraction as al-dev-solution-architect

#### `al-dev-commit-agent`

- Remove "Generated with Claude Code" and "Co-Authored-By Copilot" from commit message rules
  (harness-specific trailer rules belong in each profile)

### Knowledge Files

#### `knowledge/tdd-workflow.md`

- All `AskUserQuestion` references → "USER_GATE"

#### `knowledge/feedback-resolution.md`

- "See Loop Governance in CLAUDE.md" → "See Loop Governance in the project instructions file"

#### `knowledge/task-coordination.md`

- **Removed** from al-dev-shared (moved to profile-claude-al-dev)

---

## Profile Harness Mapping Sections

Each profile's instructions file gets a new "Harness Mapping" section that defines the
concrete values for `al-dev-shared` generic concepts. This ensures the AI always has the
mapping in context.

### `profile-claude-al-dev/CLAUDE.md` addition

```markdown
## Harness Mapping (al-dev-shared concepts → Claude Code)

| Generic concept            | Claude Code concrete                                  |
|----------------------------|-------------------------------------------------------|
| project instructions file  | CLAUDE.md                                             |
| harness settings file      | ~/.claude/settings.json                               |
| AL_DEV_SHARED_PLUGIN_ROOT  | ~/.claude/plugins/al-dev-shared/profile-al-dev-shared |
| USER_GATE                  | AskUserQuestion tool                                  |
| explore agent              | subagent_type: Explore                                |
| restart the agent          | Restart Claude Code                                   |
| MCP: al-mcp-server         | mcp__plugin_profile-claude-al-dev_al-mcp-server__*   |
| MCP: bc-code-intelligence  | mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp__* |
| MCP: microsoft-docs        | mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__* |
```

### `profile-copilot-al-dev/AGENTS.md` addition

```markdown
## Harness Mapping (al-dev-shared concepts → Copilot CLI)

| Generic concept            | Copilot CLI concrete                                                          |
|----------------------------|-------------------------------------------------------------------------------|
| project instructions file  | AGENTS.md                                                                     |
| harness settings file      | ~/.copilot/settings.json                                                      |
| AL_DEV_SHARED_PLUGIN_ROOT  | ~/.copilot/installed-plugins/<plugin-id>/profile-al-dev-shared                |
| USER_GATE                  | ask_user tool                                                                 |
| explore agent              | agent_type: "explore" in task tool                                            |
| restart the agent          | start a new Copilot CLI session                                               |
| MCP: al-mcp-server         | al-mcp-server-<tool>                                                          |
| MCP: bc-code-intelligence  | bc-code-intelligence-mcp-<tool>                                               |
| MCP: microsoft-docs        | microsoft_docs_mcp-<tool>                                                     |
```

---

## Agent Namespace Rules

| Agent location | Reference syntax |
|---|---|
| Shared agents (remain in al-dev-shared) | `al-dev-shared:<agent-name>` |
| Claude Code-only agents | `profile-claude-al-dev:<agent-name>` |
| Copilot CLI-only agents | `profile-copilot-al-dev:<agent-name>` |

Skills referencing moved agents must use the profile-namespaced form.

---

## Implementation Sequence

Steps are ordered to eliminate broken intervals: profile repos receive content
**before** it is removed from al-dev-shared.

1. **al-dev-shared** — Create `knowledge/harness-concepts.md`
2. **profile-claude-al-dev** — Add `skills/al-dev-init-context/`, `skills/al-dev-review/`,
   `agents/al-dev-session-analyst.md`, `knowledge/task-coordination.md` (copied from shared)
3. **profile-copilot-al-dev** — Create `skills/` directory; add new `al-dev-init-context`,
   `al-dev-review`, `agents/al-dev-session-analyst.md`
4. **profile-claude-al-dev** — Add Harness Mapping section to `CLAUDE.md`
5. **profile-copilot-al-dev** — Add Harness Mapping section to `AGENTS.md`
6. **al-dev-shared** — Apply all in-place changes to skill and agent bodies
   (CLAUDE.md refs, AskUserQuestion, MCP names, validator paths, subagent_type, etc.)
7. **al-dev-shared** — Remove moved items: `al-dev-init-context`, `al-dev-review`,
   `al-dev-session-analyst`, `task-coordination.md`
8. **al-dev-shared** — Commit with forbidden-token audit (see below)

Each repo gets its own atomic commit. Steps 6 and 7 are in the same al-dev-shared commit.

---

## Forbidden Token Audit

Before declaring al-dev-shared migration complete, verify none of these tokens remain
in skill/agent bodies (frontmatter excluded):

```
CLAUDE.md
.claude
~/.claude
AskUserQuestion
mcp__plugin_profile-claude
subagent_type:
CLAUDE_CODE
Generated with Claude Code
~/claude-configs
Restart Claude Code
profile-claude-al-dev
```

Each occurrence found must be classified as: replaced by abstraction, or moved to profile repo.

---

## Out of Scope

- Agent frontmatter (tool lists, model names) — remains harness-specific per design decision
- Template rendering / compiled profile output — future consideration
- Migration smoke tests / CI checks — future consideration
