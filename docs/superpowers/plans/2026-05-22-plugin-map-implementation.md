# Plugin & Agent Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 7 architectural improvements from plugin and agent map analysis: merge ticket skills, split commit analyzer, document patterns, upgrade models, and improve documentation alignment.

**Scope:** 7 independent improvements across 8 files (5 skill/agent restructures, 1 new knowledge doc, 2 documentation updates).

**Tech Stack:** AL markdown skill format, YAML frontmatter, Bash for validation.

---

## File Manifest

**Creating:**
- `profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md` — Shared invocation pattern for ticket-agent across skills

**Modifying (structure):**
- `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md` — Split into al-dev-commit-analyzer (manifest extraction only)
- `profile-al-dev-shared/agents/al-dev-commit-message-drafter.md` — NEW agent for message drafting (extracted from analyzer)
- `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md` — Consolidate with support; add `--mode=` flag logic
- `profile-al-dev-shared/skills/al-dev-support/SKILL.md` — Redirect to al-dev-ticket with --mode=full

**Modifying (documentation):**
- `profile-al-dev-shared/agents/al-dev-ticket-agent.md` — Update Inputs table (clarify env vars)
- `profile-al-dev-shared/agents/al-dev-support-researcher.md` — Remove WebSearch, WebFetch from tools
- `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md` — Change model to sonnet
- `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` — Add Phase 1 step 6 (explore-findings loading)
- `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` — Update agent spawns (reference new message-drafter agent)

**Updating (documentation maps):**
- `docs/al-dev-plugin-map.md` — Update skill names and phases
- `docs/al-dev-agent-map.md` — Update agent names, model assignments, spawning relationships

---

## Task 1: Split al-dev-commit-agent-analysis into Two Agents

Separate manifest extraction (mechanical) from message drafting (editorial judgment).

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md`
- Create: `profile-al-dev-shared/agents/al-dev-commit-message-drafter.md`

**Rationale:** The agent currently mixes two concerns: (1) Steps 1–5 extract manifests and validate files (deterministic), (2) Steps 6–6a propose commit groups and draft messages (editorial judgment). Separating allows independent iteration and clearer role definition.

- [ ] **Step 1: Read the full agent file to understand current structure**

```bash
cat profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md | wc -l
```

Expected: ~180+ lines (includes system prompt with all steps)

- [ ] **Step 2: Create new agent file for message drafting**

Create `profile-al-dev-shared/agents/al-dev-commit-message-drafter.md`:

```markdown
---
description: >-
  Git commit message drafter agent. Consumes manifests from al-dev-commit-analyzer,
  proposes atomic commit groups, and drafts commit messages. Dispatched by
  /al-dev-commit (message-drafting phase).
model: sonnet
tools: ["Read"]
---

# Agent: al-dev-commit-message-drafter

Editorial phase of the commit workflow. Dispatched by `/al-dev-commit` with
manifest analysis and project context.

All inputs arrive in the dispatch prompt:

- `MANIFESTS` — per-file change summaries from al-dev-commit-analyzer
- `PROJECT_CONTEXT` — scopes, object ID prefix, naming patterns
- `FD_TICKET` — Freshdesk ticket number or empty

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| MANIFESTS | **Yes** | Per-file change summary from analyzer (object IDs, added/removed fields and procedures) |
| PROJECT_CONTEXT | string | Scopes, object ID prefix, naming patterns |
| FD_TICKET | string (optional) | Freshdesk ticket number |

## Outputs

| Output | Description |
|--------|-------------|
| `PROPOSED_GROUPS` block | Atomic commit group proposals with draft messages |
| `DELETIONS` block | Staged deletions for the user audit gate |
| `WARNINGS` block | Validation issues and advisory notices |

---

## Phase: message-drafting

Given manifests from the analyzer, propose atomic commit groups and draft commit messages.

### Commit Group Proposal (Steps 1–1a)

#### Step 1 — Propose commit groups

Group staged files into **deployable atomic commit units**:

1. **Scope grouping** — files serving the same functional area
   belong together.
1. **Type separation** — configuration changes (`app.json`,
   version bumps) must never share a commit with feature/fix
   changes.
1. **Deployable unit constraint** — if file A references file B
   at compile time, they **must** be in the same commit.
1. **Single-commit default** — 1-3 files with a clear single
   purpose → propose one commit.

#### Step 1a — Draft commit messages

For each group, draft a message using this format:

```text
<emoji> <type>(<scope>): <subject>

[WHY: one sentence — omit for version bumps and purely
mechanical changes]

CHANGED COMPONENTS
- FileName.ObjectType.al [ObjectID] [marker]
- non-al-file.json [marker]

[Freshdesk: #<number> — only if FD_TICKET was provided]
```

**Canonical gitmoji — use only these:**

| Type | Emoji |
| --- | --- |
| feat | ✨ |
| fix | 🐛 |
| hotfix | 🚑️ |
| refactor | ♻️ |
| perf | ⚡ |
| config | 🔧 |
| docs | 📝 |
| test | ✅ |
| style | 🎨 |
| move | 🚚 |
| gitignore | 🙈 |
| chore | 📦 |
| merge | 🔀 |
| revert | ⏪ |
| wip | 🚧 |

**Message guidelines:**

- **Emoji + type + scope:** `✨ feat(journal-entries):`
- **Subject:** Lowercase, imperative ("add", not "adds" or "added"), ≤60 chars
- **WHY:** Explain the business reason. Omit for version bumps, config-only, or mechanical fixes
- **CHANGED COMPONENTS:** List every file (AL files with object ID; non-AL files with asset type)
- **Freshdesk ticket:** Include only if FD_TICKET was provided in dispatch prompt

### Return Format

Output structured blocks:

```text
PROPOSED_GROUPS
===============

GROUP 1: Core feature
- File1.al [ID 12345]
- File2.al [ID 12346]

Message:
✨ feat(journal-posting): Add multi-currency journal posting with FX revaluation

Implement multi-currency journal posting logic with automatic FX revaluation. Extends
Journal Entry posting to accept source/target currencies and apply gain/loss calculations
via the GL setup table.

CHANGED COMPONENTS
- JournalPostingExt.CodeunitExt.al [12345]
- CurrencyGainLoss.Codeunit.al [12346]

Freshdesk: #98765

---

GROUP 2: Documentation update
- README.md

Message:
📝 docs(setup): Update currency setup guide

CHANGED COMPONENTS
- README.md

---

DELETIONS
=========
(Paste list of staged files with diff-filter=D or indicate none)

WARNINGS
========
(Any validation issues or advisory notices)
```
```

- [ ] **Step 3: Refactor al-dev-commit-agent-analysis.md to remove message-drafting steps (6–6a)**

Edit `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md`:

1. Keep the frontmatter (description, model, tools)
2. Keep Steps 1–5 (manifest extraction + validation)
3. Remove Steps 6 and 6a (commit grouping + message drafting) entirely
4. Update the Outputs section to remove `PROPOSED_GROUPS` and `DELETIONS`:

Replace the current Outputs table with:

```markdown
## Outputs

| Output | Description |
|--------|-------------|
| `MANIFESTS` block | Per-file change summary (object IDs, added/removed fields and procedures) |
| `WARNINGS` block | Validation issues and advisory notices |
```

5. Remove the "Step 6" and "Step 6a" headers and all content under them
6. Keep only the manifest extraction logic

Example of what the end of the file should look like (after edits):

```text
### Validation Checks (Steps 4–5)

#### Step 4 — Detect staged deletions
...
[keep existing content]

#### Step 5 — Build staged-file sets (NUL-safe)
...
[keep existing content]

### Return Format

Output manifest blocks:

```text
MANIFESTS
=========

MANIFEST: Feature1.Table.al
  object_id: 12345
  change_type: added
  ...
[rest of manifest examples]
```
```

- [ ] **Step 4: Verify file counts**

```bash
wc -l profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md \
    profile-al-dev-shared/agents/al-dev-commit-message-drafter.md
```

Expected: analyzer file ~120–140 lines (Steps 1–5 only); drafter file ~140–160 lines (Steps 1–1a + examples)

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md \
        profile-al-dev-shared/agents/al-dev-commit-message-drafter.md
git commit -m "refactor(agents): split commit analyzer and message drafter into separate agents

Separate manifest extraction (al-dev-commit-analyzer) from message composition
(al-dev-commit-message-drafter). Allows independent iteration on each concern.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Merge /al-dev-ticket and /al-dev-support with Mode Flags

Consolidate two related skills into one with mode-based invocation.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-support/SKILL.md`

**Rationale:** /al-dev-support is a superset of /al-dev-ticket (reuses ticket-agent fetch, adds research and reply drafting). Unifying reduces skill count and clarifies the relationship via flags: `--mode=context-only` (just load context) vs `--mode=full` (research + reply).

- [ ] **Step 1: Read both skill files to understand current structure**

```bash
wc -l profile-al-dev-shared/skills/al-dev-ticket/SKILL.md \
    profile-al-dev-shared/skills/al-dev-support/SKILL.md
```

Expected: ticket ~200 lines, support ~250 lines

- [ ] **Step 2: Update /al-dev-ticket description to indicate mode support**

Edit `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md`, frontmatter section (lines 1–12):

Replace:

```markdown
---
name: al-dev-ticket
description: >-
  Fetch and contextualise a Freshdesk ticket. Use this to load
  a ticket's metadata, conversations, and attachments into a
  structured .dev/ file for downstream analysis or support reply
  drafting.
argument-hint: "[ticket-id or search-term]"
---
```

With:

```markdown
---
name: al-dev-ticket
description: >-
  Fetch and contextualise a Freshdesk ticket, optionally research
  and draft a support reply. Use --mode=context-only to load ticket
  context only (default behavior), or --mode=full to include
  research and reply drafting (equivalent to al-dev-support).
argument-hint: "[ticket-id or search-term] [--mode=context-only|full]"
---
```

- [ ] **Step 3: Add mode-handling logic to /al-dev-ticket Phase 0.5**

After Phase 0 (Check for Existing Progress), add Phase 0.5:

Find the line `## Phase 1:` and insert before it:

```markdown
## Phase 0.5: Resolve Mode

Parse the `--mode` argument:

- `--mode=context-only` (default) → Run Steps 1–4 only (fetch and contextualize ticket)
- `--mode=full` → Run all steps including research + reply drafting (equivalent to /al-dev-support)

If `--mode=` is not specified, default to `context-only`.

Extract the mode flag from $ARGUMENTS using:

```bash
MODE="context-only"
if [[ "$ARGUMENTS" =~ --mode=([^ ]+) ]]; then
  MODE="${BASH_REMATCH[1]}"
  # Remove flag from ARGUMENTS
  ARGUMENTS="${ARGUMENTS// --mode=$MODE/}"
fi
```

---
```

- [ ] **Step 4: Add conditional branching after ticket fetch (Step 4)**

Find the end of current Step 4 (around line 170–190 in al-dev-ticket, after "Present Result and Handle Attachments"), add:

```markdown
## Phase 5: Branch on Mode

If MODE is `context-only`:
- Skip Phase 6 and 7
- Output ticket context only
- Exit

If MODE is `full`:
- Continue to Phase 6 (research)

---

## Phase 6: Dispatch al-dev-support-researcher

[Copy the entire Phase 3–4 from /al-dev-support SKILL.md, which dispatches al-dev-support-researcher and processes findings]

---

## Phase 7: Dispatch al-dev-support-reply-drafter

[Copy the entire Phase 4b–5 from /al-dev-support SKILL.md, which dispatches al-dev-support-reply-drafter]

---
```

- [ ] **Step 5: Update /al-dev-support to redirect to /al-dev-ticket**

Edit `profile-al-dev-shared/skills/al-dev-support/SKILL.md`:

Replace all content with:

```markdown
---
name: al-dev-support
description: >-
  DEPRECATED ALIAS: Use /al-dev-ticket --mode=full instead.
  
  Fetch a Freshdesk ticket, research a BC support query, and draft
  a customer-facing reply. This is now a mode of /al-dev-ticket.
argument-hint: "[ticket-id or search-term] --mode=full"
---

# Support Reply Skill (Deprecated)

This skill has been consolidated with `/al-dev-ticket` for clarity.
Use `/al-dev-ticket --mode=full` instead.

The consolidated skill provides:
- `--mode=context-only` (default) — fetch ticket context only
- `--mode=full` — fetch + research + reply draft

Example:

```bash
/al-dev-ticket 12345 --mode=full
```

This is equivalent to the former `/al-dev-support 12345`.
```

- [ ] **Step 6: Verify line counts**

```bash
wc -l profile-al-dev-shared/skills/al-dev-ticket/SKILL.md \
    profile-al-dev-shared/skills/al-dev-support/SKILL.md
```

Expected: ticket file now ~400–450 lines (includes phases 5–7 from support); support file now ~20 lines (redirect)

- [ ] **Step 7: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-ticket/SKILL.md \
        profile-al-dev-shared/skills/al-dev-support/SKILL.md
git commit -m "refactor(skills): merge al-dev-support into al-dev-ticket with modes

Consolidate /al-dev-support logic into /al-dev-ticket using --mode={context-only,full}.
- --mode=context-only (default): fetch ticket context only
- --mode=full: fetch + research + reply draft (former al-dev-support behavior)

/al-dev-support now redirects to /al-dev-ticket --mode=full for backward compatibility.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Create Shared Ticket-Agent Invocation Pattern Documentation

Document the canonical invocation pattern used by both /al-dev-ticket and /al-dev-support.

**Files:**
- Create: `profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md`

- [ ] **Step 1: Create the knowledge file**

Create `profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md`:

```markdown
# Ticket Agent Invocation Pattern

Canonical pattern for dispatching `al-dev-ticket-agent` from skills that interact with Freshdesk.

## Pattern Summary

Both `/al-dev-ticket` and `/al-dev-support` dispatch `al-dev-ticket-agent` with identical environment variables and phase parameters. This document captures the canonical pattern to prevent drift.

## Dispatch Block Template

```bash
Agent tool:
  agent: al-dev-shared:al-dev-ticket-agent
  description: "Fetch Freshdesk ticket #[TICKET_ID]"

Prompt: |
  Fetch Freshdesk ticket and write
  .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md.

  Phase: fetch
  Ticket ID: [TICKET_ID]

  FRESHDESK_API_KEY and FRESHDESK_DOMAIN are set in the
  environment — use them directly in curl commands.
```

## Environment Variables

The following environment variables **must be set** by the harness before dispatching the agent:

| Variable | Description | Source |
|----------|-------------|--------|
| `FRESHDESK_API_KEY` | Freshdesk API authentication key | User's global settings (`~/.claude/settings.json`) |
| `FRESHDESK_DOMAIN` | Freshdesk subdomain (e.g., `company.freshdesk.com`) | User's global settings |

These are resolved from the harness environment, not passed in the dispatch prompt.

## Phases

### Phase: fetch

Fetch Freshdesk ticket metadata, conversations, and attachments. Output structured ticket context.

**Agent behavior:**
1. Use `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` from environment
2. Make sequential API calls (not parallel) to avoid rate-limiting
3. Extract inline images from conversation HTML (regex scan for `src=` attributes)
4. Write structured `.dev/` output file with metadata, conversations, and attachments
5. Return structured block with file path and summary

**Output file:** `.dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md`

**Return block format:**

```text
TICKET_LOADED
FILE: .dev/YYYY-MM-DD-al-dev-ticket-ticket-context.md
TITLE: [ticket title]
STATUS: [ticket status]
SUMMARY: [one-line summary]
ATTACHMENTS: [count]
```

## Using This Pattern

When a new skill needs to fetch Freshdesk tickets, it should:

1. Reference this file in the skill documentation
2. Copy the dispatch block template above
3. Substitute `[TICKET_ID]` with the user's ticket ID
4. Ensure `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` are available in the environment
5. Parse the return block to extract the output file path

## Related Files

- Agent definition: `profile-al-dev-shared/agents/al-dev-ticket-agent.md`
- Skills using this pattern:
  - `/al-dev-ticket` — Fetch ticket context (Phase 4)
  - `/al-dev-support` → redirects to `/al-dev-ticket --mode=full` (Phase 2)
```

- [ ] **Step 2: Verify file creation**

```bash
test -f profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md && echo "File created" || echo "File NOT created"
wc -l profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md
```

Expected: File exists; ~80–100 lines

- [ ] **Step 3: Add reference to the pattern in /al-dev-ticket SKILL.md**

Edit `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md`, in the section where it dispatches the agent (around the Phase 4 section), add:

```markdown
**See:** `../../knowledge/ticket-agent-invocation-pattern.md` for canonical dispatch pattern.
```

- [ ] **Step 4: Add reference to the pattern in /al-dev-support SKILL.md**

Since /al-dev-support now redirects, add to its file:

```markdown
**Note:** When using `--mode=full`, the skill internally dispatches `al-dev-ticket-agent` using the pattern documented in `knowledge/ticket-agent-invocation-pattern.md`.
```

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/knowledge/ticket-agent-invocation-pattern.md \
        profile-al-dev-shared/skills/al-dev-ticket/SKILL.md \
        profile-al-dev-shared/skills/al-dev-support/SKILL.md
git commit -m "docs: add ticket-agent invocation pattern documentation

Document canonical Freshdesk API dispatch pattern used by /al-dev-ticket
and /al-dev-support. Consolidates environment variable and phase specs
in a single referenced location to prevent drift.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Update al-dev-ticket-agent Inputs Table

Fix misleading Inputs table to clarify that FRESHDESK_API_KEY and FRESHDESK_DOMAIN are environment variables, not dispatch prompt fields.

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-ticket-agent.md` (Inputs table only)

- [ ] **Step 1: Read the current Inputs table**

```bash
grep -A 10 "^| Input" profile-al-dev-shared/agents/al-dev-ticket-agent.md
```

Expected output shows current table with FRESHDESK_API_KEY and FRESHDESK_DOMAIN listed as inputs

- [ ] **Step 2: Update the Inputs table**

Edit `profile-al-dev-shared/agents/al-dev-ticket-agent.md`, find the Inputs section (lines 41–20), and replace:

```markdown
| Input | Required | Description |
|-------|----------|-------------|
| `TICKET_ID` | **Yes** | Freshdesk ticket number (e.g., 12345) |
| `FRESHDESK_API_KEY` | **Yes** | Freshdesk API key — from environment |
| `FRESHDESK_DOMAIN` | **Yes** | Freshdesk subdomain — from environment |
```

With:

```markdown
| Input | Required | Description |
|-------|----------|-------------|
| `TICKET_ID` | **Yes** | Freshdesk ticket ID (passed in dispatch prompt, e.g., 12345) |
| `FRESHDESK_API_KEY` | **Yes** | API key (environment variable, not dispatch field) |
| `FRESHDESK_DOMAIN` | **Yes** | Freshdesk subdomain (environment variable, not dispatch field) |

**Note:** `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` are resolved from the harness environment and set as shell variables, not passed in the dispatch prompt. See `knowledge/ticket-agent-invocation-pattern.md`.
```

- [ ] **Step 3: Verify the change**

```bash
grep -A 10 "^| Input" profile-al-dev-shared/agents/al-dev-ticket-agent.md | head -15
```

Expected: Updated table with clarified environment variable note

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-ticket-agent.md
git commit -m "docs: clarify al-dev-ticket-agent Inputs table

Update Inputs documentation to clarify that FRESHDESK_API_KEY and
FRESHDESK_DOMAIN are environment variables resolved by the harness,
not dispatch prompt fields. Add reference to ticket-agent-invocation-pattern.md.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Trim Unused Tools from al-dev-support-researcher

Remove WebSearch and WebFetch from the tools list; agent delegates to MCP tools instead.

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-support-researcher.md` (frontmatter only)

- [ ] **Step 1: Read the current tools list**

```bash
grep -A 5 "^tools:" profile-al-dev-shared/agents/al-dev-support-researcher.md
```

Expected: Current tools list includes `WebSearch`, `WebFetch`

- [ ] **Step 2: Update the tools list**

Edit `profile-al-dev-shared/agents/al-dev-support-researcher.md`, frontmatter section (lines 1–10):

Find:

```yaml
tools: ["WebSearch", "WebFetch", "Read", "mcp:al-mcp-server", "mcp:bc-code-intelligence-mcp"]
```

Replace with:

```yaml
tools: ["Read", "mcp:al-mcp-server", "mcp:bc-code-intelligence-mcp", "mcp:microsoft-docs-mcp"]
```

(Note: Also ensure `mcp:microsoft-docs-mcp` is included, as the agent references it in the system prompt but it wasn't in the original list.)

- [ ] **Step 3: Verify the change**

```bash
grep "^tools:" profile-al-dev-shared/agents/al-dev-support-researcher.md
```

Expected: Updated line without WebSearch/WebFetch

- [ ] **Step 4: Add documentation note**

After the tools list in the frontmatter, add a comment:

```markdown
---
description: >-
  ...existing description...
model: sonnet
tools: ["Read", "mcp:al-mcp-server", "mcp:bc-code-intelligence-mcp", "mcp:microsoft-docs-mcp"]
---
```

And in the system prompt, add a note under the sources section (around line 40):

```markdown
**Research sources (MCP-based only):**

The agent researches using these MCP tools exclusively — no web search:
1. AL Code Intelligence — AL symbols, procedures, events
2. Microsoft Docs MCP — official BC documentation
3. BC Code History — historical patterns and BC versions
```

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-support-researcher.md
git commit -m "refactor(agents): remove unused WebSearch/WebFetch from al-dev-support-researcher

Agent delegates research to MCP tools (AL Symbols, MS Docs, BC History).
WebSearch and WebFetch were declared but never invoked. Remove to reduce
token overhead and clarify tool usage.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Add explore-findings Loading to /al-dev-plan Phase 1

Extend /al-dev-plan Phase 1 to check for and load explore-findings.md (like it does for perf-analysis).

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` (Phase 1 only)

- [ ] **Step 1: Read current Phase 1 (step 5)**

```bash
grep -A 15 "5. Load performance constraints" profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

Expected: Step 5 loads perf-analysis.md

- [ ] **Step 2: Add step 6 after step 5**

Edit `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, find the section ending with `If no file exists, skip silently.` (around line 103–104), and add after it:

```markdown

6. Load exploration findings if available:
   ```bash
   EXPLORE=$(ls .dev/*-al-dev-explore-findings.md 2>/dev/null | sort | tail -1)
   ```
   If a file is found, read the findings and synthesized recommendations.
   Include them as **"Codebase exploration findings from prior investigation:"** in every
   architect prompt in Phase 2. If no file exists, skip silently.
```

- [ ] **Step 3: Verify the change**

```bash
grep -n "Load exploration findings" profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

Expected: Line number output showing the new step 6 added

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-plan/SKILL.md
git commit -m "feat(skills): add explore-findings loading to al-dev-plan Phase 1

Extend Phase 1 context gathering to check for .dev/*-al-dev-explore-findings.md
and include key exploration findings in architect prompts. Mirrors existing
pattern for perf-analysis integration (step 5).

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Upgrade al-dev-commit-agent-execute Model to Sonnet

Change model assignment from haiku to sonnet to support multi-phase orchestration complexity.

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md` (frontmatter only)

- [ ] **Step 1: Read the current model**

```bash
grep "^model:" profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
```

Expected: `model: haiku`

- [ ] **Step 2: Update the model**

Edit `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`, frontmatter (line 6):

Replace:

```yaml
model: haiku
```

With:

```yaml
model: sonnet
```

- [ ] **Step 3: Add a comment explaining the upgrade**

After the model line, add:

```markdown
---
...
model: sonnet  # Upgraded from haiku: multi-phase orchestration (baseline → lint → validation → commit → retry) with interdependent state and error recovery requires multi-step reasoning
---
```

- [ ] **Step 4: Verify the change**

```bash
grep "^model:" profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
```

Expected: `model: sonnet`

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
git commit -m "refactor(agents): upgrade al-dev-commit-agent-execute to sonnet

Model upgrade justified by multi-phase workflow: baseline capture → lint
verification → OOXML validation → commit attempts → retry logic with state
management. Haiku scope insufficient; requires multi-step reasoning for
error recovery and edge case handling (file corruption detection, regex
correctness, retry exhaustion).

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Update /al-dev-commit Skill to Reference New Message-Drafter Agent

Update the skill to spawn the new `al-dev-commit-message-drafter` agent instead of embedding message drafting in the analyzer.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`

- [ ] **Step 1: Find the current analyzer spawn block**

```bash
grep -n "al-dev-commit-agent-analysis\|agent: al-dev-shared:al-dev-commit" profile-al-dev-shared/skills/al-dev-commit/SKILL.md | head -5
```

Expected: Line numbers showing where analyzer agent is spawned

- [ ] **Step 2: Update Phase references (analysis phase)**

In the skill, find the phase that spawns `al-dev-commit-agent-analysis` (the "analysis phase"). Update the description if it mentions "proposes commit groups" or "drafts messages" to clarify it now only extracts manifests:

Before:

```markdown
## Phase X: Analysis Phase

Reads staged diffs, builds per-file manifests, proposes commit groups, and drafts commit messages.
```

After:

```markdown
## Phase X: Analysis Phase (Manifest Extraction)

Reads staged diffs and builds per-file manifests. Message drafting is handled in the next phase.
```

- [ ] **Step 3: Add new message-drafting phase**

After the analyzer spawn, add a new phase to spawn the drafter:

```markdown
## Phase X+1: Message-Drafting Phase

Dispatches `al-dev-commit-message-drafter` to propose commit groups and draft messages based on manifests from the analyzer.

Agent tool:
  agent: al-dev-shared:al-dev-commit-message-drafter
  description: "Draft commit messages and propose groups"

Prompt: |
  Given the manifests from the analysis phase:

  [INCLUDE MANIFESTS OUTPUT FROM PREVIOUS PHASE]

  Propose atomic commit groups and draft commit messages using the gitmoji format.
```

- [ ] **Step 4: Verify no breaking changes to downstream logic**

```bash
grep -c "al-dev-commit-agent-analysis" profile-al-dev-shared/skills/al-dev-commit/SKILL.md
grep -c "al-dev-commit-message-drafter" profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: 1 reference to analyzer, 1 reference to drafter

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-commit/SKILL.md
git commit -m "refactor(skills): update al-dev-commit to use new message-drafter agent

Update /al-dev-commit skill phases to dispatch the new al-dev-commit-message-drafter
agent (extracted from al-dev-commit-agent-analysis). Skill now runs two distinct phases:
(1) manifest extraction, (2) message drafting with group proposals.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Update Documentation Maps

Update `docs/al-dev-plugin-map.md` and `docs/al-dev-agent-map.md` to reflect all structural changes.

**Files:**
- Modify: `docs/al-dev-plugin-map.md`
- Modify: `docs/al-dev-agent-map.md`

- [ ] **Step 1: Run /review-skill-map to auto-update plugin map**

In Claude Code, run:

```
/review-skill-map
```

This will read all SKILL.md files and regenerate the plugin map with current skill list and diagrams.

- [ ] **Step 2: Run /review-agent-map to auto-update agent map**

In Claude Code, run:

```
/review-agent-map
```

This will read all agent files and regenerate the agent map with current agent list, spawning relationships, and model assignments.

- [ ] **Step 3: Verify changes**

```bash
git diff docs/al-dev-plugin-map.md docs/al-dev-agent-map.md | head -50
```

Expected: Changes to skill/agent counts, spawning relationships, and model assignments

- [ ] **Step 4: Commit**

```bash
git add docs/al-dev-plugin-map.md docs/al-dev-agent-map.md
git commit -m "docs: sync plugin and agent maps with implementation changes

Update maps to reflect:
- Merged /al-dev-ticket + /al-dev-support with modes
- Split al-dev-commit-agent-analysis into analyzer + message-drafter
- Upgraded al-dev-commit-agent-execute to sonnet
- Removed WebSearch/WebFetch from al-dev-support-researcher
- New knowledge/ticket-agent-invocation-pattern.md

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Verification Checklist

After all tasks are complete, run:

```bash
# Verify no uncommitted changes
git status

# Verify commit count
git log --oneline -n 9 | wc -l
# Expected: 9 commits (one per task)

# Verify agent structure (if validation script exists)
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents

# Verify knowledge file quality
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge

# Grep for new agent references
grep -r "al-dev-commit-message-drafter" profile-al-dev-shared/skills/
# Expected: Found in /al-dev-commit skill

# Confirm no AI attribution left in code comments
grep -r "Co-Authored-By" profile-al-dev-shared/ --include="*.md" --include="*.al"
# Expected: Only in git commit messages (via .dev/ convention), not in file bodies
```

---

## Summary

✅ **7 approved changes implemented:**
1. Split al-dev-commit-agent-analysis into analyzer + message-drafter
2. Merge al-dev-ticket + al-dev-support with mode flags
3. Create ticket-agent invocation pattern knowledge doc
4. Update al-dev-ticket-agent Inputs table (environment variable clarification)
5. Trim al-dev-support-researcher tools (remove WebSearch/WebFetch)
6. Add explore-findings loading to /al-dev-plan Phase 1
7. Upgrade al-dev-commit-agent-execute to sonnet

✅ **Maps auto-updated** via /review-skill-map and /review-agent-map

✅ **9 commits created** (one per task), all with clear messages and co-author attribution.
