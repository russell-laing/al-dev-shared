# Harness-Agnostic Plugin Design Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `al-dev-shared` skill and agent bodies harness-agnostic so they work correctly under any compliant profile plugin (Claude Code, Copilot CLI, or future harnesses).

**Architecture:** A new `knowledge/harness-concepts.md` defines the generic vocabulary (USER_GATE, project instructions file, explore agent, etc.). Profile repos (profile-claude-al-dev, profile-copilot-al-dev) implement concrete harness mappings in their always-loaded instructions file. Skill bodies are edited in-place to use only the generic vocabulary. Items that depend on Claude Code-specific infrastructure (init-context, review, session-analyst, task-coordination) are moved to profile repos before being removed from al-dev-shared.

**Tech Stack:** Bash (sed, grep, git), Markdown

**Repo paths:**
- `SHARED` = `/Users/russelllaing/al-dev-shared/profile-al-dev-shared`
- `CLAUDE_PROFILE` = `/Users/russelllaing/claude-configs/profile-claude-al-dev`
- `COPILOT_PROFILE` = `/Users/russelllaing/copilot-configs/profile-copilot-al-dev`

---

## Forbidden Token Reference

These tokens must not appear in skill/agent bodies after migration (agent frontmatter excluded):

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

Verification command (run in `profile-al-dev-shared/`):
```bash
grep -rn "CLAUDE\.md\|\.claude\|AskUserQuestion\|subagent_type:\|mcp__plugin_profile-claude\|CLAUDE_CODE\|Generated with Claude Code\|claude-configs\|Restart Claude Code\|profile-claude-al-dev" \
  skills/ agents/ knowledge/ \
  --include="*.md" \
  | grep -v "^Binary"
```
Expected: no output (zero matches)

---

## Task 1: Create `knowledge/harness-concepts.md`

**Files:**
- Create: `$SHARED/knowledge/harness-concepts.md`

- [ ] **Step 1: Create the harness-concepts knowledge file**

```bash
cat > /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/harness-concepts.md << 'EOF'
# Harness Concepts — Abstraction Contract

This file defines the generic vocabulary used across all `al-dev-shared`
skills and agents. Each profile repo implements concrete mappings in its
always-loaded instructions file (CLAUDE.md, AGENTS.md, etc.).

## Skill Author Guidelines

When writing skills for `al-dev-shared`:

- Use generic concept names from the table below — never harness-specific names
- Use `USER_GATE` for any blocking approval or confirmation point
- Use `AL_DEV_SHARED_PLUGIN_ROOT` for any path into the plugin
- Reference MCP tools by capability name — never by raw harness-specific tool ID
- Use plain English for file operations ("read the file", "write to disk")
- When dispatching a named agent, write: `Dispatch agent: <namespace>:<agent-name>`

## Generic Concept Vocabulary

| Concept | Description | Claude Code | Copilot CLI |
|---|---|---|---|
| **project instructions file** | The file that provides the AI agent with project-specific instructions | `CLAUDE.md` | `AGENTS.md` |
| **harness settings file** | The file where harness-wide settings (e.g. API keys) are stored | `~/.claude/settings.json` | `~/.copilot/settings.json` |
| **AL_DEV_SHARED_PLUGIN_ROOT** | The installed path of the al-dev-shared plugin | `~/.claude/plugins/al-dev-shared/profile-al-dev-shared` | `~/.copilot/installed-plugins/<plugin-id>/profile-al-dev-shared` |
| **USER_GATE** | A blocking user-confirmation point; never continue past this without a user response | `AskUserQuestion` tool | `ask_user` tool |
| **explore agent** | A fast parallel exploration agent | `subagent_type: Explore` | `agent_type: "explore"` in task tool |
| **restart the agent** | Instruction to the user to start a new AI coding session | "Restart Claude Code" | "start a new Copilot CLI session" |
| **MCP: al-mcp-server** | AL symbol lookup, object definitions, references | `mcp__plugin_profile-claude-al-dev_al-mcp-server__<tool>` | `al-mcp-server-<tool>` |
| **MCP: bc-code-intelligence** | BC knowledge, specialist consultation, code analysis | `mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp__<tool>` | `bc-code-intelligence-mcp-<tool>` |
| **MCP: microsoft-docs** | Microsoft documentation search and fetch | `mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__<tool>` | `microsoft_docs_mcp-<tool>` |

## USER_GATE Semantics

`USER_GATE` is a hard blocking point. Regardless of harness:

- The agent MUST stop and present the question/choice to the user
- The agent MUST NOT continue until a user response is received
- The question SHOULD include options where applicable
- There is no timeout — wait indefinitely

## AL_DEV_SHARED_PLUGIN_ROOT

Each profile's instructions file defines `AL_DEV_SHARED_PLUGIN_ROOT`. Skills use it for
validator script discovery:

```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/<skill-name>/validate-*.py"
```

## Agent Dispatch Syntax

Skills reference agents using a harness-neutral format. The profile's harness
mapping defines the concrete dispatch mechanism:

```
Dispatch agent: <namespace>:<agent-name>
  description: "<short description>"
  prompt: "<prompt text>"
```

For explore agents, use:

```
Spawn an explore agent:
  purpose: <purpose>
  prompt: <prompt>
  output: <expected output>
```

## Agent Namespace Rules

| Agent location | Reference syntax |
|---|---|
| Shared agents (in al-dev-shared) | `al-dev-shared:<agent-name>` |
| Claude Code-only agents | `profile-claude-al-dev:<agent-name>` |
| Copilot CLI-only agents | `profile-copilot-al-dev:<agent-name>` |
EOF
```

- [ ] **Step 2: Verify the file was created**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/harness-concepts.md
```
Expected: ~80 lines (non-zero)

- [ ] **Step 3: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/harness-concepts.md
git -C /Users/russelllaing/al-dev-shared commit -m "✨ feat(knowledge): add harness-concepts abstraction contract"
```

---

## Task 2: Copy Moved Items to profile-claude-al-dev

Items that depend on Claude Code infrastructure are copied verbatim before removal from al-dev-shared.

**Files:**
- Create: `$CLAUDE_PROFILE/skills/al-dev-init-context/SKILL.md`
- Create: `$CLAUDE_PROFILE/skills/al-dev-review/SKILL.md`
- Create: `$CLAUDE_PROFILE/agents/al-dev-session-analyst.md`
- Create: `$CLAUDE_PROFILE/knowledge/task-coordination.md`

- [ ] **Step 1: Create directory structure and copy files**

```bash
SHARED=/Users/russelllaing/al-dev-shared/profile-al-dev-shared
CLAUDE=/Users/russelllaing/claude-configs/profile-claude-al-dev

mkdir -p "$CLAUDE/skills/al-dev-init-context"
mkdir -p "$CLAUDE/skills/al-dev-review"
mkdir -p "$CLAUDE/agents"
mkdir -p "$CLAUDE/knowledge"

cp -r "$SHARED/skills/al-dev-init-context/." "$CLAUDE/skills/al-dev-init-context/"
cp -r "$SHARED/skills/al-dev-review/." "$CLAUDE/skills/al-dev-review/"
cp "$SHARED/agents/al-dev-session-analyst.md" "$CLAUDE/agents/al-dev-session-analyst.md"
cp "$SHARED/knowledge/task-coordination.md" "$CLAUDE/knowledge/task-coordination.md"

echo "Done"
ls "$CLAUDE/skills/al-dev-init-context/"
ls "$CLAUDE/skills/al-dev-review/"
ls "$CLAUDE/agents/al-dev-session-analyst.md"
ls "$CLAUDE/knowledge/task-coordination.md"
```
Expected: all 4 paths print without error

- [ ] **Step 2: Commit to profile-claude-al-dev**

```bash
git -C /Users/russelllaing/claude-configs add \
  profile-claude-al-dev/skills/al-dev-init-context \
  profile-claude-al-dev/skills/al-dev-review \
  profile-claude-al-dev/agents/al-dev-session-analyst.md \
  profile-claude-al-dev/knowledge/task-coordination.md
git -C /Users/russelllaing/claude-configs commit -m "✨ feat: migrate init-context, review, session-analyst, task-coordination from al-dev-shared"
```

---

## Task 3: Create profile-copilot-al-dev `al-dev-init-context` Skill

New Copilot CLI-native skill: AGENTS.md-based setup, no Claude Code symlinks.

**Files:**
- Create: `$COPILOT_PROFILE/skills/al-dev-init-context/SKILL.md`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p /Users/russelllaing/copilot-configs/profile-copilot-al-dev/skills/al-dev-init-context
```

- [ ] **Step 2: Create the skill file**

```bash
cat > /Users/russelllaing/copilot-configs/profile-copilot-al-dev/skills/al-dev-init-context/SKILL.md << 'EOF'
---
name: al-dev-init-context
description: Initialize project context document for faster workflows.
---

# Command: /al-dev-init-context

Initialize the project for AL development and create the project context document.

## Purpose

**Six-part setup:**

1. **Create AGENTS.md** — Project-specific instructions if absent
2. **Create project context** — Documents project structure for faster agent workflows
3. **Check MCP availability** — Verify al-mcp-server, bc-code-intelligence-mcp, microsoft-docs-mcp
4. **Ensure `.dev/` is gitignored** — Add to `.gitignore` if missing
5. **Confirm publisher/app metadata** — Validate `app.json` or equivalent
6. **Report setup summary** — What was set up and what still needs manual attention

Creates `.dev/project-context.md` by exploring the project once and documenting:
- Project structure
- Key objects and their purposes
- Architectural patterns
- Base app integration points
- Common code locations
- Build and test commands

This document is then used by ALL agents to avoid redundant exploration,
reducing workflow runtime by 40–60%.

---

## Implementation

### Step 1: Check for Project Instructions File

Check if `AGENTS.md` exists at the project root:

```bash
ls AGENTS.md 2>/dev/null && echo "EXISTS" || echo "ABSENT"
```

**If absent**, gather project metadata from `app.json`:

```bash
cat app.json 2>/dev/null || echo "app.json not found"
```

If `app.json` exists, extract:
- `publisher` — publisher name
- `name` — app name
- `description` — app description
- `idRanges` — object ID ranges

If `app.json` is absent, **USER_GATE** — ask the user:
```
I need some project metadata to create AGENTS.md.
Please provide:
1. Publisher name
2. App name
3. App description
4. Object ID range (e.g. 50001–50100)
```

Create `AGENTS.md` with this template:

```markdown
# [App Name] — Project Instructions

**Publisher:** [publisher]
**App:** [app name]
**Object ID range:** [range]

## Description

[App description]

## AL Coding Standards

- Follow BC naming conventions
- Prefix all objects with the publisher's object ID prefix
- Use meaningful, descriptive names for fields and procedures

## Object ID Range

Objects in this project MUST use IDs in the range: [range]

## Key Files

- `app.json` — App manifest
- `.dev/project-context.md` — Project context for agent workflows
```

---

### Step 2: Validate or Create `.dev/project-context.md`

Check if it exists:

```bash
ls .dev/project-context.md 2>/dev/null && echo "EXISTS" || echo "ABSENT"
```

**If absent**, explore the project to gather information:

```bash
# Count AL objects by type
echo "=== AL Object Types ==="
find . -name "*.al" -not -path "./.alpackages/*" | \
  xargs grep -l "^table \|^tableextension \|^page \|^pageextension \|^codeunit \|^report \|^enum \|^interface " 2>/dev/null | \
  head -5

# Check for test codeunits
echo "=== Test Codeunits ==="
grep -rl "Subtype = Test" . --include="*.al" 2>/dev/null | head -5

# Check build scripts
echo "=== Build/Test Commands ==="
ls Makefile scripts/ *.sh 2>/dev/null

# Check dependencies
echo "=== App Dependencies ==="
cat app.json 2>/dev/null | grep -A20 '"dependencies"'
```

Write `.dev/project-context.md`:

```markdown
# Project Context — [App Name]

**Generated:** [date]

## Tech Stack

- AL / Business Central
- Publisher: [publisher]
- App ID: [app id from app.json]
- Target: BC[version]

## Object ID Range

[range] — prefix [publisher prefix]

## Architecture Patterns

[Describe key patterns found: event-based, integration, UI-only, etc.]

## Key Objects

| Object | Type | Purpose |
|---|---|---|
| [Name] | Table/Page/Codeunit | [purpose] |

## Base App Integration Points

[List key base app tables/pages extended or subscribed to]

## Build and Test Commands

```bash
# Build
al-compile

# Run tests
# [describe how tests are run]
```

## Common Code Locations

- AL source: `src/` or root `.al` files
- Tests: [test folder path]
- Scripts: [scripts folder if any]
```

---

### Step 3: Check MCP Availability

Report which MCPs are available by attempting to use each:

```bash
echo "Checking MCP tools..."
# The agent checks tool availability by looking at its available tools
```

Report:
```
MCP Status:
  al-mcp-server          — [available / not available]
  bc-code-intelligence   — [available / not available]
  microsoft-docs-mcp     — [available / not available]
```

---

### Step 4: Ensure `.dev/` is Gitignored

```bash
grep -q "^\.dev/" .gitignore 2>/dev/null && echo "Already gitignored" || \
  (echo ".dev/" >> .gitignore && echo "Added .dev/ to .gitignore")
```

---

### Step 5: Confirm Publisher/App Metadata

```bash
cat app.json 2>/dev/null | grep -E '"publisher"|"name"|"version"|"id"' | head -8
```

If `app.json` is missing, tell the user: "No `app.json` found. Please create it or ensure the project root is correct."

---

### Step 6: Report Summary

Present to user:

```
/al-dev-init-context complete

Setup summary:
  AGENTS.md              — [created / already existed]
  .dev/project-context.md — [created / already existed]
  .dev/ gitignore        — [added / already present]

MCP availability:
  al-mcp-server          — [status]
  bc-code-intelligence   — [status]
  microsoft-docs-mcp     — [status]

[If anything needs manual attention:]
Needs manual attention:
  - [item]
```
EOF
```

- [ ] **Step 3: Verify the file exists and has content**

```bash
wc -l /Users/russelllaing/copilot-configs/profile-copilot-al-dev/skills/al-dev-init-context/SKILL.md
```
Expected: ~150+ lines

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/copilot-configs add profile-copilot-al-dev/skills/al-dev-init-context
git -C /Users/russelllaing/copilot-configs commit -m "✨ feat: add al-dev-init-context skill for Copilot CLI profile"
```

---

## Task 4: Create profile-copilot-al-dev `al-dev-review` Skill

New skill using Copilot CLI SQL `session_store` database to analyse friction patterns.

**Files:**
- Create: `$COPILOT_PROFILE/skills/al-dev-review/SKILL.md`

- [ ] **Step 1: Create directory**

```bash
mkdir -p /Users/russelllaing/copilot-configs/profile-copilot-al-dev/skills/al-dev-review
```

- [ ] **Step 2: Create the skill file**

```bash
cat > /Users/russelllaing/copilot-configs/profile-copilot-al-dev/skills/al-dev-review/SKILL.md << 'EOF'
---
name: al-dev-review
description: >-
  Analyse recent sessions for friction patterns in this project.
  Queries the Copilot CLI session_store database and produces a
  structured findings report with improvement recommendations.
  Manually triggered — run at the end of a session you want to review.
---

# Skill: /al-dev-review

Analyse recent sessions for this project and produce improvement
recommendations for the plugin configuration and workflow.

> **Scope note:** This skill uses the Copilot CLI `session_store` SQL
> database. It can identify friction patterns from conversation turns,
> checkpoint history, and file churn. It cannot report raw tool call/result
> errors, permission denial counts, or live skill attribution — those are
> only available in Claude Code's JSONL session transcripts.

---

## Step 1 — Identify Project Repository

Determine the current project repository:

```bash
git remote get-url origin 2>/dev/null || \
  basename "$(git rev-parse --show-toplevel 2>/dev/null)" || \
  basename "$(pwd)"
```

Hold the repository identifier as `REPO_ID` (e.g. `owner/repo` or directory name).

---

## Step 2 — Query session_store for Recent Sessions

Query the Copilot CLI session_store database for sessions from this project.
Use the SQL tool with `database: "session_store"`:

```sql
-- Find recent sessions for this project
SELECT s.id, s.branch, s.summary, s.created_at,
       COUNT(t.turn_index) as turn_count
FROM sessions s
LEFT JOIN turns t ON t.session_id = s.id
WHERE s.repository LIKE '%[REPO_ID]%'
   OR s.cwd LIKE '%[project directory name]%'
ORDER BY s.created_at DESC
LIMIT 20;
```

If zero sessions found, report: "No sessions found for this project in the session_store. This skill requires at least one previous session."

---

## Step 3 — Extract Friction Signals

Run these queries to build the signals package:

```sql
-- Clarification requests and repeated questions
SELECT t.session_id, t.turn_index, substr(t.user_message, 1, 300) as msg,
       substr(t.assistant_response, 1, 200) as response
FROM turns t
JOIN sessions s ON t.session_id = s.id
WHERE (s.repository LIKE '%[REPO_ID]%' OR s.cwd LIKE '%[project dir]%')
  AND (t.user_message LIKE '%unclear%'
    OR t.user_message LIKE '%wrong%'
    OR t.user_message LIKE '%again%'
    OR t.user_message LIKE '%not what I%'
    OR t.assistant_response LIKE '%clarif%')
ORDER BY t.timestamp DESC
LIMIT 30;
```

```sql
-- File churn signals (frequently edited files)
SELECT sf.file_path, COUNT(DISTINCT sf.session_id) as session_count,
       COUNT(*) as edit_count
FROM session_files sf
JOIN sessions s ON sf.session_id = s.id
WHERE (s.repository LIKE '%[REPO_ID]%' OR s.cwd LIKE '%[project dir]%')
  AND sf.tool_name IN ('edit', 'create')
GROUP BY sf.file_path
ORDER BY edit_count DESC
LIMIT 20;
```

```sql
-- Error and failure patterns
SELECT content, session_id, source_type
FROM search_index
WHERE search_index MATCH 'error OR failure OR blocked OR retry OR unclear OR wrong'
  AND session_id IN (
    SELECT id FROM sessions
    WHERE repository LIKE '%[REPO_ID]%'
       OR cwd LIKE '%[project dir]%'
  )
LIMIT 40;
```

```sql
-- Checkpoint completion patterns (what was completed vs abandoned)
SELECT c.session_id, c.title, c.overview,
       substr(c.work_done, 1, 500) as work_done,
       substr(c.next_steps, 1, 300) as next_steps
FROM checkpoints c
JOIN sessions s ON c.session_id = s.id
WHERE s.repository LIKE '%[REPO_ID]%'
   OR s.cwd LIKE '%[project dir]%'
ORDER BY c.session_id DESC, c.checkpoint_number DESC
LIMIT 20;
```

---

## Step 4 — Dispatch Session Analyst Agent

Package the query results and dispatch:

```
Dispatch agent: profile-copilot-al-dev:al-dev-session-analyst
  description: "Analyse session friction for [REPO_ID]"
  prompt: |
    REPO: [REPO_ID]
    PROJECT_DIR: [current working directory]
    OUTPUT_FILE: .dev/[date]-al-dev-review-findings.md

    SIGNALS:

    RECENT_SESSIONS:
    [paste session query results]

    CLARIFICATION_TURNS:
    [paste clarification query results]

    FILE_CHURN:
    [paste file churn results]

    ERROR_PATTERNS:
    [paste error/failure search results]

    CHECKPOINT_PATTERNS:
    [paste checkpoint results]

    Analyse these signals and write the findings report to OUTPUT_FILE.
    Follow your agent definition instructions exactly.
```

---

## Step 5 — Present Result

After the agent completes:

```text
Session analysis complete →
.dev/[date]-al-dev-review-findings.md

[Agent summary: N friction patterns identified, M files with churn]

Review the report and apply recommendations to AGENTS.md
and .dev/project-context.md.
```
EOF
```

- [ ] **Step 3: Verify**

```bash
wc -l /Users/russelllaing/copilot-configs/profile-copilot-al-dev/skills/al-dev-review/SKILL.md
```
Expected: ~130+ lines

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/copilot-configs add profile-copilot-al-dev/skills/al-dev-review
git -C /Users/russelllaing/copilot-configs commit -m "✨ feat: add al-dev-review skill for Copilot CLI profile (SQL session_store)"
```

---

## Task 5: Create profile-copilot-al-dev `al-dev-session-analyst` Agent

New agent that receives SQL query results (not JSONL signals) and produces findings.

**Files:**
- Create: `$COPILOT_PROFILE/agents/al-dev-session-analyst.md`

- [ ] **Step 1: Create directory and file**

```bash
mkdir -p /Users/russelllaing/copilot-configs/profile-copilot-al-dev/agents
cat > /Users/russelllaing/copilot-configs/profile-copilot-al-dev/agents/al-dev-session-analyst.md << 'EOF'
---
description: >-
  Analyses Copilot CLI session_store data for friction patterns in
  an AL development project. Receives SQL query results from the
  al-dev-review skill and produces a structured findings report.
tools: ["bash", "view", "edit", "create"]
---

# Agent: al-dev-session-analyst (Copilot CLI)

Analyse session data and produce a structured findings report
identifying improvement opportunities for the project configuration.

## Inputs

The dispatch prompt contains:

- `REPO`: repository identifier (e.g. `owner/repo`)
- `PROJECT_DIR`: current working directory
- `OUTPUT_FILE`: path for the findings report
- `SIGNALS`: structured SQL query results from session_store

  Sections: `RECENT_SESSIONS`, `CLARIFICATION_TURNS`, `FILE_CHURN`,
  `ERROR_PATTERNS`, `CHECKPOINT_PATTERNS`

> **Scope note:** This agent works from Copilot CLI's session_store SQL data.
> It cannot report raw tool call/result errors, permission denial counts, or
> live skill attribution — those are only in Claude Code's JSONL transcripts.
> The report acknowledges this scope difference.

## Analysis Process

### 1. Session Overview

From `RECENT_SESSIONS`:
- Count total sessions and total turns
- Identify the date range covered
- Note average turns per session (high averages may indicate friction)

### 2. Friction Pattern Analysis

From `CLARIFICATION_TURNS`:
- Group by theme: scope confusion, output rejection, unclear instructions, repeated questions
- For each theme: count occurrences, note which sessions, quote 1-2 representative messages
- Flag any pattern appearing in 3+ sessions as a systemic issue

### 3. File Churn Analysis

From `FILE_CHURN`:
- List top 10 files by edit_count
- Flag files edited in 3+ sessions as high-churn
- For high-churn files: infer why (volatile spec, unclear requirements, missing tests)

### 4. Error Pattern Analysis

From `ERROR_PATTERNS`:
- Identify recurring error types
- Group by error category (compile, runtime, tool failure, blocked)
- Note which sessions show the most errors

### 5. Checkpoint Pattern Analysis

From `CHECKPOINT_PATTERNS`:
- Identify phases frequently abandoned (next_steps contains incomplete work)
- Identify phases always completed (work_done is thorough)
- Flag any checkpoint with no work_done as a potential skill failure

### 6. Recommendations

For each systemic friction pattern, produce one targeted recommendation:

- **Target**: AGENTS.md, `.dev/project-context.md`, or a specific skill
- **Finding**: what the data shows
- **Recommendation**: specific text to add/change in the target file
- **Priority**: HIGH / MEDIUM / LOW

## Output Format

Write `OUTPUT_FILE` with this structure:

```markdown
# Session Friction Analysis — [REPO]

**Date:** [today]
**Sessions analysed:** [N] sessions ([date range])
**Data source:** Copilot CLI session_store (SQL)

> **Scope:** This report is based on conversation turns, checkpoints,
> and file edits. Raw tool errors and permission denials are not
> captured in this data source.

---

## Summary

[2-3 sentence overview of main findings]

---

## Friction Patterns

### [Pattern Name] — [HIGH/MEDIUM/LOW]

**Evidence:** [N occurrences across [M] sessions]
> "[Representative quote from clarification turn]"

**Recommendation:** Add to AGENTS.md:
\`\`\`
[Specific text to add]
\`\`\`

[Repeat for each pattern]

---

## File Churn

| File | Sessions | Edits | Inferred Cause |
|---|---|---|---|
| [path] | [N] | [N] | [cause] |

**High-churn recommendation:** [specific action]

---

## Checkpoint Gaps

[List phases frequently incomplete, with recommendations]

---

## Action Items

Priority order:

1. **[AGENTS.md / project-context.md / skill name]** — [specific change]
2. ...
```

After writing the file, print:
```
FINDINGS_FILE: [OUTPUT_FILE]
PATTERNS_FOUND: [N]
HIGH_PRIORITY: [N]
SUMMARY: [one sentence]
```
EOF
```

- [ ] **Step 2: Verify**

```bash
wc -l /Users/russelllaing/copilot-configs/profile-copilot-al-dev/agents/al-dev-session-analyst.md
```
Expected: ~120+ lines

- [ ] **Step 3: Commit**

```bash
git -C /Users/russelllaing/copilot-configs add profile-copilot-al-dev/agents/al-dev-session-analyst.md
git -C /Users/russelllaing/copilot-configs commit -m "✨ feat: add al-dev-session-analyst agent for Copilot CLI profile"
```

---

## Task 6: Add Harness Mapping to profile-claude-al-dev/CLAUDE.md

**Files:**
- Modify: `$CLAUDE_PROFILE/CLAUDE.md`

- [ ] **Step 1: Append the Harness Mapping section**

```bash
cat >> /Users/russelllaing/claude-configs/profile-claude-al-dev/CLAUDE.md << 'EOF'

---

## Harness Mapping (al-dev-shared concepts → Claude Code)

When `al-dev-shared` skills and agents use generic concept names, map them as follows:

| Generic concept            | Claude Code concrete                                                          |
|----------------------------|-------------------------------------------------------------------------------|
| project instructions file  | CLAUDE.md                                                                     |
| harness settings file      | ~/.claude/settings.json                                                       |
| AL_DEV_SHARED_PLUGIN_ROOT  | ~/.claude/plugins/al-dev-shared/profile-al-dev-shared                        |
| USER_GATE                  | AskUserQuestion tool                                                          |
| explore agent              | subagent_type: Explore                                                        |
| restart the agent          | Restart Claude Code                                                           |
| Dispatch agent: X          | Agent tool with subagent_type: X                                              |
| MCP: al-mcp-server         | mcp__plugin_profile-claude-al-dev_al-mcp-server__*                           |
| MCP: bc-code-intelligence  | mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp__*                |
| MCP: microsoft-docs        | mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__*                      |
EOF
```

- [ ] **Step 2: Verify the section was appended**

```bash
tail -20 /Users/russelllaing/claude-configs/profile-claude-al-dev/CLAUDE.md
```
Expected: ends with the Harness Mapping table

- [ ] **Step 3: Commit**

```bash
git -C /Users/russelllaing/claude-configs add profile-claude-al-dev/CLAUDE.md
git -C /Users/russelllaing/claude-configs commit -m "📝 docs: add harness mapping section to CLAUDE.md"
```

---

## Task 7: Add Harness Mapping to profile-copilot-al-dev/AGENTS.md

**Files:**
- Modify: `$COPILOT_PROFILE/AGENTS.md`

- [ ] **Step 1: Append the Harness Mapping section**

```bash
cat >> /Users/russelllaing/copilot-configs/profile-copilot-al-dev/AGENTS.md << 'EOF'

---

## Harness Mapping (al-dev-shared concepts → Copilot CLI)

When `al-dev-shared` skills and agents use generic concept names, map them as follows:

| Generic concept            | Copilot CLI concrete                                                          |
|----------------------------|-------------------------------------------------------------------------------|
| project instructions file  | AGENTS.md                                                                     |
| harness settings file      | ~/.copilot/settings.json                                                      |
| AL_DEV_SHARED_PLUGIN_ROOT  | ~/.copilot/installed-plugins/<plugin-id>/profile-al-dev-shared                |
| USER_GATE                  | ask_user tool                                                                 |
| explore agent              | agent_type: "explore" in task tool                                            |
| restart the agent          | start a new Copilot CLI session                                               |
| Dispatch agent: X          | task tool with agent_type: X                                                  |
| MCP: al-mcp-server         | al-mcp-server-<tool>                                                          |
| MCP: bc-code-intelligence  | bc-code-intelligence-mcp-<tool>                                               |
| MCP: microsoft-docs        | microsoft_docs_mcp-<tool>                                                     |
EOF
```

- [ ] **Step 2: Verify**

```bash
tail -20 /Users/russelllaing/copilot-configs/profile-copilot-al-dev/AGENTS.md
```
Expected: ends with the Harness Mapping table

- [ ] **Step 3: Commit**

```bash
git -C /Users/russelllaing/copilot-configs add profile-copilot-al-dev/AGENTS.md
git -C /Users/russelllaing/copilot-configs commit -m "📝 docs: add harness mapping section to AGENTS.md"
```

---

## Task 8: In-Place Changes — `al-dev-commit` Skill

**Files:**
- Modify: `$SHARED/skills/al-dev-commit/SKILL.md`

- [ ] **Step 1: Replace CLAUDE.md check with project instructions file check**

In the Step 1 guard block, replace:
```
Old:
  ls CLAUDE.md 2>/dev/null

Old message:
  No `CLAUDE.md` found in this repository.
  Project context is required to generate correct commit
  messages. Would you like me to create it now via
  `/al-dev-init-context`? (yes / no)"

  - **yes** — invoke the `al-dev-init-context` skill via the
    Skill tool (not a subagent), wait for it to complete, then
    proceed to Step 2 to load the newly created `CLAUDE.md`
  - **init-context fails** — stop with: "Could not create
    `CLAUDE.md` automatically. Please run
    `/al-dev-init-context` or create it manually, then re-run
    `/al-dev-commit`."
  - **no** — stop with: "Please create `CLAUDE.md` manually or
    run `/al-dev-init-context`, then re-run `/al-dev-commit`."
```

```
New:
  Check for the project instructions file (CLAUDE.md, AGENTS.md,
  or equivalent for your harness).

New message:
  No project instructions file found in this repository.
  Project context is required to generate correct commit
  messages. Would you like me to create it now via
  `/al-dev-init-context`? (yes / no)"

  - **yes** — invoke the `al-dev-init-context` skill via the
    Skill tool (not a subagent), wait for it to complete, then
    proceed to Step 2 to load the newly created project
    instructions file
  - **init-context fails** — stop with: "Could not create
    the project instructions file automatically. Please run
    `/al-dev-init-context` or create it manually, then re-run
    `/al-dev-commit`."
  - **no** — stop with: "Please create the project
    instructions file manually or run `/al-dev-init-context`,
    then re-run `/al-dev-commit`."
```

Use the edit tool on `$SHARED/skills/al-dev-commit/SKILL.md`:

Replace:
```
ls CLAUDE.md 2>/dev/null
```
With:
```
Check for the project instructions file (CLAUDE.md, AGENTS.md,
or equivalent for your harness):

ls CLAUDE.md AGENTS.md 2>/dev/null | head -1
```

- [ ] **Step 2: Replace the load sequence (Step 2 of the skill)**

Replace:
```
Read the following files in order (later values override earlier):

1. `~/claude-configs/CLAUDE.md` — global defaults (if present)
1. `~/claude-configs/profile-claude-al-dev/CLAUDE.md` — AL
   profile defaults (if present)
1. `./CLAUDE.md` — project-specific overrides (required)
```
With:
```
Load the project instructions file from your harness's standard
locations (earlier files provide defaults, later files override):

1. Global defaults location (if present, per harness mapping)
2. AL profile defaults location (if present, per harness mapping)
3. `./[project instructions file]` — project-specific (required)
```

- [ ] **Step 3: Replace all remaining `CLAUDE.md` references with "project instructions file"**

```bash
sed -i '' \
  's/`CLAUDE\.md`/the project instructions file/g;
   s/CLAUDE\.md/project instructions file/g' \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

- [ ] **Step 4: Abstract subagent_type references in dispatch blocks**

Replace:
```
  subagent_type: al-dev-shared:al-dev-commit-agent
```
With:
```
  agent: al-dev-shared:al-dev-commit-agent
```

```bash
sed -i '' \
  's/subagent_type: al-dev-shared:/agent: al-dev-shared:/g' \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

- [ ] **Step 5: Verify no forbidden tokens remain**

```bash
grep -n "CLAUDE\.md\|~/claude-configs\|subagent_type:" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```
Expected: no output

---

## Task 9: In-Place Changes — `al-dev-handoff` Skill

**Files:**
- Modify: `$SHARED/skills/al-dev-handoff/SKILL.md`

- [ ] **Step 1: Replace Claude Code-specific path check**

Replace:
```
ls "[target-repo-path]/.claude" 2>/dev/null || \
  ls "[target-repo-path]/src" 2>/dev/null || \
  echo "Path not found — verify target repo path"
```
With:
```
ls "[target-repo-path]/src" 2>/dev/null || \
  ls "[target-repo-path]/app.json" 2>/dev/null || \
  echo "Path not found — verify target repo path"
```

- [ ] **Step 2: Replace Claude Code session references in handoff prompt template**

Replace:
```
Paste this into a new Claude Code session opened in [target repo name].
```
With:
```
Paste this into a new session in your AI coding harness, opened in [target repo name].
```

Replace:
```
/al-dev-plan [specific fix description based on confirmed root cause]
```
(Keep as-is — skill commands are harness-neutral)

- [ ] **Step 3: Replace any remaining `.claude` or "Claude Code" session references**

```bash
grep -n "\.claude\|Claude Code session\|new Claude Code" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-handoff/SKILL.md
```

For each match, edit using the edit tool to replace with neutral language:
- "new Claude Code session" → "new AI coding agent session"
- `/.claude` path check → omit (already replaced in Step 1)

- [ ] **Step 4: Verify no forbidden tokens remain**

```bash
grep -n "CLAUDE\.md\|\.claude\|Restart Claude Code\|claude-configs" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-handoff/SKILL.md
```
Expected: no output

---

## Task 10: In-Place Changes — `al-dev-support` and `al-dev-ticket` Skills

**Files:**
- Modify: `$SHARED/skills/al-dev-support/SKILL.md`
- Modify: `$SHARED/skills/al-dev-ticket/SKILL.md`

- [ ] **Step 1: Fix al-dev-support — settings.json reference**

Replace in `al-dev-support/SKILL.md`:
```
Add to ~/.claude/settings.json (never committed):

  "env": {
    "FRESHDESK_API_KEY": "your-api-key",
    "FRESHDESK_DOMAIN": "yoursubdomain.freshdesk.com"
  }

Restart Claude Code after saving.
```
With:
```
Add to your harness settings file (never committed):

  "env": {
    "FRESHDESK_API_KEY": "your-api-key",
    "FRESHDESK_DOMAIN": "yoursubdomain.freshdesk.com"
  }

Restart your AI coding agent session after saving.
```

- [ ] **Step 2: Fix al-dev-support — subagent_type references**

```bash
sed -i '' \
  's/subagent_type: al-dev-shared:/agent: al-dev-shared:/g' \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-support/SKILL.md
```

- [ ] **Step 3: Fix al-dev-ticket — settings.json and Restart references**

Replace in `al-dev-ticket/SKILL.md`:
```
Add to ~/.claude/settings.json (global user settings, never committed):
```
With:
```
Add to your harness settings file (global user settings, never committed):
```

Replace:
```
Restart Claude Code after saving.
See profile-claude-al-dev/freshdesk-readonly-setup.md for details.
```
With:
```
Restart your AI coding agent session after saving.
See your harness profile's Freshdesk setup guide for details.
```

- [ ] **Step 4: Fix al-dev-ticket — subagent_type references**

```bash
sed -i '' \
  's/subagent_type: al-dev-shared:/agent: al-dev-shared:/g' \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-ticket/SKILL.md
```

- [ ] **Step 5: Verify no forbidden tokens in both files**

```bash
grep -n "CLAUDE\.md\|\.claude\|Restart Claude Code\|profile-claude-al-dev\|subagent_type:" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-support/SKILL.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-ticket/SKILL.md
```
Expected: no output

---

## Task 11: In-Place Changes — Validator Paths (5 Skills)

Replace `find ~/.claude/plugins -name "validate-*.py"` with `$AL_DEV_SHARED_PLUGIN_ROOT` path in `al-dev-autonomous`, `al-dev-develop`, `al-dev-plan`, `al-dev-test`, `al-dev-interview`.

**Files:**
- Modify: `$SHARED/skills/al-dev-autonomous/SKILL.md`
- Modify: `$SHARED/skills/al-dev-develop/SKILL.md`
- Modify: `$SHARED/skills/al-dev-plan/SKILL.md`
- Modify: `$SHARED/skills/al-dev-test/SKILL.md`
- Modify: `$SHARED/skills/al-dev-interview/SKILL.md`

- [ ] **Step 1: Fix al-dev-autonomous validator path**

View the exact lines around line 470:
```bash
sed -n '465,480p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
```

Replace:
```bash
VALIDATOR=$(find ~/.claude/plugins \
  -name "validate-code-review.py" \
```
With:
```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-autonomous/validate-code-review.py"
if [ ! -f "$VALIDATOR" ]; then
```

(Adjust the surrounding `if` block to match the new one-liner path pattern)

- [ ] **Step 2: Fix al-dev-autonomous AskUserQuestion references (2 occurrences)**

```bash
grep -n "AskUserQuestion" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
```

For each occurrence, use the edit tool to replace:
```
Use AskUserQuestion with options:
```
With:
```
USER_GATE — ask the user with options:
```

- [ ] **Step 3: Fix al-dev-develop validator path and AskUserQuestion**

```bash
sed -n '250,270p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Replace the `find ~/.claude/plugins` block with:
```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-develop/validate-code-review.py"
if [ ! -f "$VALIDATOR" ]; then
```

Replace `Use AskUserQuestion with options:` with `USER_GATE — ask the user with options:`

- [ ] **Step 4: Fix al-dev-plan validator path and AskUserQuestion**

```bash
sed -n '248,260p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

Replace the `find ~/.claude/plugins -name "validate-plan.py"` block with:
```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-plan/validate-plan.py"
if [ ! -f "$VALIDATOR" ]; then
```

Replace `Use AskUserQuestion with options:` with `USER_GATE — ask the user with options:`

- [ ] **Step 5: Fix al-dev-test validator path and AskUserQuestion**

```bash
sed -n '208,225p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-test/SKILL.md
```

Replace the `find ~/.claude/plugins -name "validate-test-plan.py"` block with:
```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-test/validate-test-plan.py"
if [ ! -f "$VALIDATOR" ]; then
```

Replace `Use AskUserQuestion with options:` with `USER_GATE — ask the user with options:`

- [ ] **Step 6: Fix al-dev-interview validator path**

```bash
sed -n '98,110p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-interview/SKILL.md
```

Replace the `find ~/.claude/plugins -name "validate-requirements.py"` block with:
```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-interview/validate-requirements.py"
if [ ! -f "$VALIDATOR" ]; then
```

- [ ] **Step 7: Verify no forbidden tokens in all 5 files**

```bash
grep -n "\.claude\|AskUserQuestion" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-test/SKILL.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-interview/SKILL.md
```
Expected: no output

---

## Task 12: In-Place Changes — Explore Agent Spawn (3 Skills)

Replace `subagent_type: Explore` with harness-neutral spawn template.

**Files:**
- Modify: `$SHARED/skills/al-dev-explore/SKILL.md`
- Modify: `$SHARED/skills/al-dev-investigate/SKILL.md`
- Modify: `$SHARED/skills/al-dev-perf/SKILL.md`

- [ ] **Step 1: View exact context around subagent_type: Explore in each file**

```bash
grep -n -B3 -A3 "subagent_type: Explore" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-explore/SKILL.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-investigate/SKILL.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-perf/SKILL.md
```

- [ ] **Step 2: Replace in al-dev-explore**

For each spawn block containing `subagent_type: Explore`, use the edit tool to replace:
```
subagent_type: Explore
```
With:
```
Spawn an explore agent:
```

Ensure the resulting block looks like:
```
Spawn an explore agent:
  purpose: <purpose>
  prompt: <prompt>
  output: <expected output>
```

- [ ] **Step 3: Replace in al-dev-investigate**

Same pattern as Step 2. Replace `subagent_type: Explore` with:
```
Spawn an explore agent:
```

- [ ] **Step 4: Replace in al-dev-perf**

Same pattern. Replace `subagent_type: Explore` with:
```
Spawn an explore agent:
```

- [ ] **Step 5: Fix al-dev-release-notes — subagent_type for named agent**

```bash
sed -i '' \
  's/subagent_type: al-dev-shared:/agent: al-dev-shared:/g' \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-release-notes/SKILL.md
```

- [ ] **Step 6: Verify no subagent_type: remains in any skill**

```bash
grep -rn "subagent_type:" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/ \
  --include="*.md"
```
Expected: no output

---

## Task 13: In-Place Changes — `al-dev-developer` Agent

**Files:**
- Modify: `$SHARED/agents/al-dev-developer.md`

- [ ] **Step 1: Replace all AskUserQuestion with USER_GATE**

```bash
AGENT=/Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
grep -c "AskUserQuestion" "$AGENT"
```
Expected: 12+ occurrences (note the count for verification)

```bash
sed -i '' 's/AskUserQuestion/USER_GATE/g' "$AGENT"
```

- [ ] **Step 2: Update USER_GATE description in agent body**

Find the line:
```
At each TDD phase gate, you MUST use AskUserQuestion to block:
```
(After Step 1, this will be:)
```
At each TDD phase gate, you MUST use USER_GATE to block:
```
This is already correct after the sed. Verify:

```bash
grep -n "USER_GATE" "$AGENT" | head -5
```
Expected: multiple occurrences at phase gate descriptions

- [ ] **Step 3: Fix CLAUDE.md references**

```bash
grep -n "CLAUDE\.md" "$AGENT"
```

Replace each occurrence using the edit tool:
- `"Follow AL coding standards from profile CLAUDE.md"` → `"Follow AL coding standards from the project instructions file"`
- Any other `CLAUDE.md` reference → `"project instructions file"`

- [ ] **Step 4: Verify**

```bash
grep -n "AskUserQuestion\|CLAUDE\.md\|profile-claude" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
```
Expected: no output

---

## Task 14: In-Place Changes — `al-dev-interview` Agent

**Files:**
- Modify: `$SHARED/agents/al-dev-interview.md`

> Note: The frontmatter `tools: ["Read", "Write", "AskUserQuestion"]` is harness-specific
> and is left as-is per spec (frontmatter is out of scope). Only the agent body changes.

- [ ] **Step 1: Replace AskUserQuestion in agent body (not frontmatter)**

```bash
AGENT=/Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-interview.md
```

View line 7 (frontmatter tools) to identify where body starts:
```bash
head -15 "$AGENT"
```

Replace body occurrences only (lines after frontmatter `---`):

```bash
# Count body occurrences (lines 15+)
sed -n '15,$p' "$AGENT" | grep -c "AskUserQuestion"
```

Use the edit tool to replace each body occurrence:
- `**AskUserQuestion** | Conduct interview with user (REQUIRED for all questions)` → `**USER_GATE** | Conduct interview with user (REQUIRED for all questions)`
- `**CRITICAL REQUIREMENT**: Use \`AskUserQuestion\` tool for EVERY question.` → `**CRITICAL REQUIREMENT**: Use **USER_GATE** for EVERY question.`
- `**ONLY** ask via AskUserQuestion tool` → `**ONLY** ask via USER_GATE`
- `2-4 per AskUserQuestion call` → `2-4 per USER_GATE call`

- [ ] **Step 2: Verify body has no AskUserQuestion (frontmatter may still have it)**

```bash
# Check body only (skip frontmatter block)
awk '/^---$/{n++} n>=2{print}' "$AGENT" | grep "AskUserQuestion"
```
Expected: no output

---

## Task 15: In-Place Changes — `al-dev-solution-architect` Agent

**Files:**
- Modify: `$SHARED/agents/al-dev-solution-architect.md`

> Note: Frontmatter `tools:` array is left as-is (harness-specific, out of scope).

- [ ] **Step 1: Count MCP name occurrences**

```bash
grep -c "mcp__plugin_profile-claude-al-dev" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md
```
Note the count.

- [ ] **Step 2: Replace al-mcp-server MCP calls in body**

Pattern: `mcp__plugin_profile-claude-al-dev_al-mcp-server__<function>`
Replace with: `al-mcp-server MCP tool: <function>`

```bash
AGENT=/Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md
sed -i '' \
  's/mcp__plugin_profile-claude-al-dev_al-mcp-server__/al-mcp-server MCP tool: /g' \
  "$AGENT"
```

- [ ] **Step 3: Replace bc-code-intelligence MCP calls in body**

```bash
sed -i '' \
  's/mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp__/bc-code-intelligence MCP tool: /g' \
  "$AGENT"
```

- [ ] **Step 4: Replace microsoft-docs MCP calls in body**

```bash
sed -i '' \
  's/mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__/microsoft-docs MCP tool: /g' \
  "$AGENT"
```

- [ ] **Step 5: Replace CLAUDE.md references**

```bash
grep -n "CLAUDE\.md" "$AGENT"
```

For each occurrence, use the edit tool to replace `CLAUDE.md` with `the project instructions file`.

- [ ] **Step 6: Verify no forbidden tokens remain in body**

```bash
# Skip frontmatter (first 15 lines)
awk '/^---$/{n++} n>=2{print}' "$AGENT" | \
  grep "mcp__plugin_profile-claude\|CLAUDE\.md\|profile-claude-al-dev"
```
Expected: no output

---

## Task 16: In-Place Changes — `al-dev-support-agent` and `al-dev-commit-agent`

**Files:**
- Modify: `$SHARED/agents/al-dev-support-agent.md`
- Modify: `$SHARED/agents/al-dev-commit-agent.md`

- [ ] **Step 1: Fix al-dev-support-agent MCP names in body**

```bash
AGENT=/Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md
grep -n "mcp__plugin" "$AGENT"
```

```bash
sed -i '' \
  's/mcp__plugin_profile-claude-al-dev_al-mcp-server__/al-mcp-server MCP tool: /g;
   s/mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__/microsoft-docs MCP tool: /g' \
  "$AGENT"
```

Note: Frontmatter `tools:` array lines (lines 9-10) are left as-is.

- [ ] **Step 2: Verify al-dev-support-agent body**

```bash
awk '/^---$/{n++} n>=2{print}' "$AGENT" | grep "mcp__plugin_profile-claude"
```
Expected: no output

- [ ] **Step 3: Fix al-dev-commit-agent — remove "Generated with Claude Code" rule**

```bash
AGENT=/Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent.md
grep -n "Generated with Claude Code\|Co-Authored-By Copilot" "$AGENT"
```

View the surrounding context:
```bash
grep -n -B2 -A2 "Generated with Claude Code" "$AGENT"
```

Use the edit tool to remove the "Generated with Claude Code" mention from the commit message rules. The rule about `Co-Authored-By` trailers stays if it's already about NEVER appending them (that's correct behaviour). Remove only references that say to INCLUDE "Generated with Claude Code".

- [ ] **Step 4: Verify al-dev-commit-agent**

```bash
grep -n "Generated with Claude Code\|Co-Authored-By Copilot" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent.md
```
Expected: no output (or only lines that say "never append")

---

## Task 17: In-Place Changes — Knowledge Files

**Files:**
- Modify: `$SHARED/knowledge/tdd-workflow.md`
- Modify: `$SHARED/knowledge/feedback-resolution.md`

- [ ] **Step 1: Fix tdd-workflow.md — AskUserQuestion → USER_GATE**

```bash
KNOW=/Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/tdd-workflow.md
grep -c "AskUserQuestion" "$KNOW"
```
Expected: 5 occurrences

```bash
sed -i '' 's/AskUserQuestion/USER_GATE/g' "$KNOW"
```

- [ ] **Step 2: Verify tdd-workflow.md**

```bash
grep -n "AskUserQuestion" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/tdd-workflow.md
```
Expected: no output

- [ ] **Step 3: Fix feedback-resolution.md — CLAUDE.md reference**

```bash
KNOW=/Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/feedback-resolution.md
grep -n "CLAUDE\.md" "$KNOW"
```
Expected: 1 occurrence (line 69)

Use the edit tool to replace:
```
See Loop Governance in CLAUDE.md.
```
With:
```
See Loop Governance in the project instructions file.
```

- [ ] **Step 4: Verify feedback-resolution.md**

```bash
grep -n "CLAUDE\.md" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/feedback-resolution.md
```
Expected: no output

---

## Task 18: Commit All al-dev-shared In-Place Changes

- [ ] **Step 1: Stage all modified files**

```bash
cd /Users/russelllaing/al-dev-shared
git add \
  profile-al-dev-shared/skills/al-dev-commit/SKILL.md \
  profile-al-dev-shared/skills/al-dev-handoff/SKILL.md \
  profile-al-dev-shared/skills/al-dev-support/SKILL.md \
  profile-al-dev-shared/skills/al-dev-ticket/SKILL.md \
  profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/skills/al-dev-plan/SKILL.md \
  profile-al-dev-shared/skills/al-dev-test/SKILL.md \
  profile-al-dev-shared/skills/al-dev-interview/SKILL.md \
  profile-al-dev-shared/skills/al-dev-explore/SKILL.md \
  profile-al-dev-shared/skills/al-dev-investigate/SKILL.md \
  profile-al-dev-shared/skills/al-dev-perf/SKILL.md \
  profile-al-dev-shared/skills/al-dev-release-notes/SKILL.md \
  profile-al-dev-shared/agents/al-dev-developer.md \
  profile-al-dev-shared/agents/al-dev-interview.md \
  profile-al-dev-shared/agents/al-dev-solution-architect.md \
  profile-al-dev-shared/agents/al-dev-support-agent.md \
  profile-al-dev-shared/agents/al-dev-commit-agent.md \
  profile-al-dev-shared/knowledge/tdd-workflow.md \
  profile-al-dev-shared/knowledge/feedback-resolution.md
git status
```

- [ ] **Step 2: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared commit \
  -m "♻️ refactor: make skill/agent bodies harness-agnostic

- Replace CLAUDE.md refs with 'project instructions file'
- Replace AskUserQuestion with USER_GATE
- Replace find ~/.claude/plugins with AL_DEV_SHARED_PLUGIN_ROOT
- Replace subagent_type: Explore with neutral explore spawn syntax
- Replace subagent_type: al-dev-shared:* with 'agent: al-dev-shared:*'
- Replace mcp__plugin_profile-claude refs with abstract MCP capability names
- Replace Restart Claude Code with 'restart your AI coding agent session'
- Replace freshdesk-readonly-setup.md ref with harness-neutral reference
- Remove Generated with Claude Code from commit agent rules"
```

---

## Task 19: Remove Moved Items from al-dev-shared

Items were already copied to profile-claude-al-dev in Task 2. Now remove from al-dev-shared.

**Files:**
- Remove: `$SHARED/skills/al-dev-init-context/` (directory)
- Remove: `$SHARED/skills/al-dev-review/` (directory)
- Remove: `$SHARED/agents/al-dev-session-analyst.md`
- Remove: `$SHARED/knowledge/task-coordination.md`

- [ ] **Step 1: Confirm copies exist in profile-claude-al-dev before deleting**

```bash
ls /Users/russelllaing/claude-configs/profile-claude-al-dev/skills/al-dev-init-context/SKILL.md
ls /Users/russelllaing/claude-configs/profile-claude-al-dev/skills/al-dev-review/SKILL.md
ls /Users/russelllaing/claude-configs/profile-claude-al-dev/agents/al-dev-session-analyst.md
ls /Users/russelllaing/claude-configs/profile-claude-al-dev/knowledge/task-coordination.md
```
Expected: all 4 paths exist without error

- [ ] **Step 2: Remove the items**

```bash
SHARED=/Users/russelllaing/al-dev-shared/profile-al-dev-shared
rm -rf "$SHARED/skills/al-dev-init-context"
rm -rf "$SHARED/skills/al-dev-review"
rm "$SHARED/agents/al-dev-session-analyst.md"
rm "$SHARED/knowledge/task-coordination.md"
```

- [ ] **Step 3: Stage removals and commit**

```bash
git -C /Users/russelllaing/al-dev-shared add -u \
  profile-al-dev-shared/skills/al-dev-init-context \
  profile-al-dev-shared/skills/al-dev-review \
  profile-al-dev-shared/agents/al-dev-session-analyst.md \
  profile-al-dev-shared/knowledge/task-coordination.md
git -C /Users/russelllaing/al-dev-shared commit \
  -m "🔥 feat: remove Claude Code-specific items (moved to profile-claude-al-dev)

Moved: skills/al-dev-init-context, skills/al-dev-review,
       agents/al-dev-session-analyst, knowledge/task-coordination"
```

---

## Task 20: Forbidden Token Audit

Verify zero forbidden tokens remain in al-dev-shared skill/agent bodies.

**Files:**
- Verify: all `.md` files in `$SHARED/skills/`, `$SHARED/agents/`, `$SHARED/knowledge/`

- [ ] **Step 1: Run the full forbidden token audit**

```bash
grep -rn \
  "CLAUDE\.md\|\.claude\|AskUserQuestion\|subagent_type:\|mcp__plugin_profile-claude\|CLAUDE_CODE\|Generated with Claude Code\|claude-configs\|Restart Claude Code\|profile-claude-al-dev" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/ \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/ \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/ \
  --include="*.md"
```
Expected: **zero output** (no matches)

- [ ] **Step 2: If any matches found, classify each**

For each remaining match:
- If it's a body reference to a forbidden concept → fix it (use edit tool, re-run audit)
- If it's in frontmatter (tools list, description) → acceptable, per spec (frontmatter is out of scope)
- If it's in a comment explaining what the old token was → remove or rephrase

Iterate until zero body matches remain.

- [ ] **Step 3: Final audit pass — verify profile-claude-al-dev files still have forbidden tokens (expected)**

```bash
# Confirm the Claude profile's moved files do have Claude-specific content (correct)
grep -l "CLAUDE\.md\|AskUserQuestion\|subagent_type:" \
  /Users/russelllaing/claude-configs/profile-claude-al-dev/skills/al-dev-init-context/SKILL.md \
  /Users/russelllaing/claude-configs/profile-claude-al-dev/skills/al-dev-review/SKILL.md \
  /Users/russelllaing/claude-configs/profile-claude-al-dev/agents/al-dev-session-analyst.md
```
Expected: all 3 paths listed (they correctly contain Claude Code-specific content)

- [ ] **Step 4: Push all three repos**

```bash
git -C /Users/russelllaing/al-dev-shared push
git -C /Users/russelllaing/claude-configs push
git -C /Users/russelllaing/copilot-configs push
```
Expected: each push succeeds

---

## Self-Review Checklist

Ran spec against plan:

**Spec requirement → Task coverage:**
- `knowledge/harness-concepts.md` created → Task 1 ✓
- Copy to profile-claude-al-dev → Task 2 ✓
- New profile-copilot-al-dev skills → Tasks 3, 4, 5 ✓
- Harness mapping in CLAUDE.md → Task 6 ✓
- Harness mapping in AGENTS.md → Task 7 ✓
- al-dev-commit in-place → Task 8 ✓
- al-dev-handoff in-place → Task 9 ✓
- al-dev-support, al-dev-ticket in-place → Task 10 ✓
- Validator paths (5 skills) → Task 11 ✓
- subagent_type: Explore (3 skills + release-notes) → Task 12 ✓
- al-dev-developer agent → Task 13 ✓
- al-dev-interview agent → Task 14 ✓
- al-dev-solution-architect agent → Task 15 ✓
- al-dev-support-agent, al-dev-commit-agent → Task 16 ✓
- tdd-workflow.md, feedback-resolution.md → Task 17 ✓
- Remove moved items → Task 19 ✓
- Forbidden token audit → Task 20 ✓

**Type consistency:**
- All skills use `USER_GATE` (not `AskUserQuestion`)
- All validator paths use `$AL_DEV_SHARED_PLUGIN_ROOT` (not `~/.claude/plugins`)
- All agent dispatches use `agent: al-dev-shared:*` (not `subagent_type: al-dev-shared:*`)
- All explore spawns use `Spawn an explore agent:` block format
- Harness mapping tables in both profile repos use consistent concept names matching harness-concepts.md
