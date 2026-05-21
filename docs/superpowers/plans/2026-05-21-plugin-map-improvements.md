# Plugin Map Improvements — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 8 verified improvements from the plugin and agent maps: 4 lightweight fixes (tool trims + inputs alignment), 2 maintenance moves, 1 skill connection, 1 agent split — plus 3 design spikes for deferred structural changes.

**Architecture:** Changes are grouped by risk: Tasks 1–4 are frontmatter/documentation-only edits with no behavioral impact; Tasks 5–6 are structural moves within the repo; Tasks 7–8 add/restructure skill behavior; Tasks 9–11 produce design specs for future planning sessions. All changes work against live codebase state verified by rubber-ducking in the /plan-map-changes session.

**Tech Stack:** Markdown, YAML frontmatter, Python (path-fix verification), Bash (git operations + verification)

---

## File Map

| Task | Files Changed |
|------|---------------|
| 1 | `profile-al-dev-shared/agents/al-dev-code-review.md` |
| 2 | `profile-al-dev-shared/agents/al-dev-expert-reviewer.md`, `al-dev-security-reviewer.md`, `al-dev-performance-reviewer.md` |
| 3 | `profile-al-dev-shared/agents/al-dev-support-agent.md` |
| 4 | `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md` |
| 5 | `profile-al-dev-shared/skills/al-dev-align/` → `archived/skills/al-dev-align/` (git mv) + `check-alignment.py` line 322 |
| 6 | `profile-al-dev-shared/skills/plugin-health-daemon/` → `.claude/skills/plugin-health-daemon/` (git mv) + `docs/al-dev-plugin-map.md` |
| 7 | `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` |
| 8 | Create `agents/al-dev-support-researcher.md`, `agents/al-dev-support-reply-drafter.md`; delete `agents/al-dev-support-agent.md`; modify `skills/al-dev-support/SKILL.md` |
| 9–11 | `docs/superpowers/specs/2026-05-21-explore-perf-merge-design.md`, `2026-05-21-ticket-support-merge-design.md`, `2026-05-21-develop-atomise-design.md` |

**Ordering constraints:**
- Tasks 1–6 are fully independent of each other.
- Task 8 depends on Task 3 completing first (avoids editing `al-dev-support-agent.md` twice).
- Tasks 7, 9–11 are independent of all others.

---

## Task 1: Trim al-dev-code-review — remove unused Glob and Grep

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md`

**Why:** Agent body explicitly says "Read all files provided (no Bash — use Read tool)". Glob and Grep are declared but never called.

- [ ] **Step 1: Verify current tools line**

```bash
grep -n "^tools:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-code-review.md
```

Expected: `8:tools: ["Read", "Glob", "Grep"]`

- [ ] **Step 2: Edit frontmatter**

In `profile-al-dev-shared/agents/al-dev-code-review.md`, change:

Old:
```yaml
tools: ["Read", "Glob", "Grep"]
```

New:
```yaml
tools: ["Read"]
```

- [ ] **Step 3: Verify the change**

```bash
grep "^tools:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-code-review.md
```

Expected: `tools: ["Read"]`

- [ ] **Step 4: Check for forbidden patterns**

```bash
grep -n "TODO\|TBD\|\[date\]" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-code-review.md
```

Expected: no output.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-code-review.md
git -C /Users/russelllaing/al-dev-shared commit -m "refactor(agents): trim unused Glob+Grep tools from al-dev-code-review"
```

---

## Task 2: Trim three reviewer agents — remove unused Glob

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-expert-reviewer.md`
- Modify: `profile-al-dev-shared/agents/al-dev-security-reviewer.md`
- Modify: `profile-al-dev-shared/agents/al-dev-performance-reviewer.md`

**Why:** All three receive explicit file lists in the spawn prompt (confirmed in body: "Read all AL files created (provided in spawn prompt)"). Glob is unused. Grep is retained — reviewers may use it for cross-file pattern scanning (naming violations, SetPermission, N+1 patterns).

- [ ] **Step 1: Verify current tools across all three**

```bash
grep "^tools:" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-expert-reviewer.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-security-reviewer.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-performance-reviewer.md
```

Expected: each shows `tools: ["Read", "Grep", "Glob"]`

- [ ] **Step 2: Edit al-dev-expert-reviewer.md**

Old:
```yaml
tools: ["Read", "Grep", "Glob"]
```

New:
```yaml
tools: ["Read", "Grep"]
```

- [ ] **Step 3: Edit al-dev-security-reviewer.md**

Old:
```yaml
tools: ["Read", "Grep", "Glob"]
```

New:
```yaml
tools: ["Read", "Grep"]
```

- [ ] **Step 4: Edit al-dev-performance-reviewer.md**

Old:
```yaml
tools: ["Read", "Grep", "Glob"]
```

New:
```yaml
tools: ["Read", "Grep"]
```

- [ ] **Step 5: Verify all three updated**

```bash
grep "^tools:" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-expert-reviewer.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-security-reviewer.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-performance-reviewer.md
```

Expected: each shows `tools: ["Read", "Grep"]`

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/agents/al-dev-expert-reviewer.md \
  profile-al-dev-shared/agents/al-dev-security-reviewer.md \
  profile-al-dev-shared/agents/al-dev-performance-reviewer.md
git -C /Users/russelllaing/al-dev-shared commit -m "refactor(agents): trim unused Glob tool from three reviewer agents"
```

---

## Task 3: Align al-dev-support-agent — mark BC version as optional

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-support-agent.md`

**Why:** Inputs table marks "BC version" as `**Yes**` (required) but the dispatching skill (/al-dev-support Step 4) passes only `QUERY_TYPE`, `QUERY_CONTEXT`, `TICKET_FILE`. The agent infers BC version from query text (Step 1: "Identify... BC version"). Making it required is misleading.

- [ ] **Step 1: Verify current Inputs row**

```bash
grep -n "BC version" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md
```

Expected: `29:| BC version | **Yes** | Affected BC version (e.g., BC 23, BC 24) |`

- [ ] **Step 2: Update the Inputs row**

In `profile-al-dev-shared/agents/al-dev-support-agent.md`:

Old:
```markdown
| BC version | **Yes** | Affected BC version (e.g., BC 23, BC 24) |
```

New:
```markdown
| BC version | No | Inferred from query context if mentioned; not required from caller |
```

- [ ] **Step 3: Verify the change**

```bash
grep "BC version" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md
```

Expected: `| BC version | No | Inferred from query context if mentioned; not required from caller |`

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-support-agent.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(agents): mark BC version as optional in al-dev-support-agent inputs"
```

---

## Task 4: Align al-dev-commit-recover-verifier — document actual dispatch inputs

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md`

**Why:** Agent's Inputs table documents `REPO`, `CORRUPTION_LOG`, `auto_fix` but the dispatching skill (/commit-recover Step 2) passes: incident file path, baseline line count, current line count, git log output, and learnings.md content. The table headers also differ from the standard agent format.

- [ ] **Step 1: Verify current Inputs table**

```bash
grep -A 7 "## Inputs" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md | head -9
```

Expected:
```
| Field | Type | Description |
|-------|------|-------------|
| REPO | string | Project root directory |
| CORRUPTION_LOG | string | Path to `.dev/commit-integrity.log` with flagged files |
| auto_fix | boolean | If true, apply auto-fixes; if false, report findings only |
```

- [ ] **Step 2: Replace Inputs table**

In `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md`:

Old:
```markdown
| Field | Type | Description |
|-------|------|-------------|
| REPO | string | Project root directory |
| CORRUPTION_LOG | string | Path to `.dev/commit-integrity.log` with flagged files |
| auto_fix | boolean | If true, apply auto-fixes; if false, report findings only |
```

New:
```markdown
| Input | Required | Description |
|-------|----------|-------------|
| incident_file_path | **Yes** | File path of the corrupted file (from integrity log incident) |
| baseline_lines | **Yes** | Original line count from the integrity log |
| current_lines | **Yes** | Current `wc -l` output for the file |
| git_history | **Yes** | `git log` output for last 3–5 commits touching this file |
| learnings_content | No | Content of `.dev/learnings.md` with known corruption patterns |
```

- [ ] **Step 3: Verify the change**

```bash
grep -A 9 "## Inputs" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md | head -10
```

Expected: shows updated table starting with `| Input | Required | Description |` and rows for `incident_file_path`, `baseline_lines`, etc.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(agents): align al-dev-commit-recover-verifier inputs table with actual dispatch"
```

---

## Task 5: Move al-dev-align to archived/skills/

**Files:**
- Move: `profile-al-dev-shared/skills/al-dev-align/` → `profile-al-dev-shared/archived/skills/al-dev-align/`
- Modify: `profile-al-dev-shared/archived/skills/al-dev-align/check-alignment.py` (line 322)

**Why:** The directory has no SKILL.md — it is not a distributed skill, just Python utilities. The `check-alignment.py` script uses `Path(__file__).resolve().parent.parent.parent` to find the plugin root. Moving from `skills/al-dev-align/` to `archived/skills/al-dev-align/` adds one depth level, requiring one additional `.parent` to maintain the same resolution.

- [ ] **Step 1: Confirm no SKILL.md exists**

```bash
ls /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-align/
```

Expected: `__pycache__  check-alignment.py  tests` — no SKILL.md.

- [ ] **Step 2: Move directory using git mv**

```bash
git -C /Users/russelllaing/al-dev-shared mv \
  profile-al-dev-shared/skills/al-dev-align \
  profile-al-dev-shared/archived/skills/al-dev-align
```

- [ ] **Step 3: Verify move**

```bash
ls /Users/russelllaing/al-dev-shared/profile-al-dev-shared/archived/skills/al-dev-align/ \
  && echo "=== old ===" \
  && ls /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-align/ 2>&1
```

Expected: new path shows `check-alignment.py tests`; old path shows "No such file or directory".

- [ ] **Step 4: Fix path reference in check-alignment.py**

In `profile-al-dev-shared/archived/skills/al-dev-align/check-alignment.py` at line 322:

Old:
```python
        plugin_root = Path(__file__).resolve().parent.parent.parent
```

New:
```python
        plugin_root = Path(__file__).resolve().parent.parent.parent.parent
```

Rationale: `archived/skills/al-dev-align/` is 4 levels deep inside `profile-al-dev-shared/`; `skills/al-dev-align/` was 3. One additional `.parent` restores correct resolution.

- [ ] **Step 5: Verify path resolution**

```bash
cd /Users/russelllaing/al-dev-shared && python3 -c "
from pathlib import Path
p = Path('profile-al-dev-shared/archived/skills/al-dev-align/check-alignment.py').resolve()
result = p.parent.parent.parent.parent
expected = Path('profile-al-dev-shared').resolve()
assert result == expected, f'MISMATCH: {result} != {expected}'
print('OK:', result)
"
```

Expected: `OK: /Users/russelllaing/al-dev-shared/profile-al-dev-shared`

- [ ] **Step 6: Stage the Python edit and commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/archived/skills/al-dev-align/check-alignment.py
git -C /Users/russelllaing/al-dev-shared commit -m \
  "refactor: move al-dev-align utilities to archived/skills/ (not a distributed skill — no SKILL.md)"
```

---

## Task 6: Move plugin-health-daemon to .claude/skills/

**Files:**
- Move: `profile-al-dev-shared/skills/plugin-health-daemon/` → `.claude/skills/plugin-health-daemon/`
- Modify: `docs/al-dev-plugin-map.md`

**Why:** plugin-health-daemon operates exclusively on the plugin's own structure (self-audit). Like /align-harness-repos, it is project-maintenance infrastructure, not a service for external consumers. The SKILL.md has no `$AL_DEV_SHARED_PLUGIN_ROOT` path references — it invokes other skills by name, not path.

- [ ] **Step 1: Confirm source exists and only has SKILL.md**

```bash
ls /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/plugin-health-daemon/
```

Expected: `SKILL.md`

- [ ] **Step 2: Confirm destination slot is free**

```bash
ls /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-daemon 2>&1
```

Expected: "No such file or directory"

- [ ] **Step 3: Move directory using git mv**

```bash
git -C /Users/russelllaing/al-dev-shared mv \
  profile-al-dev-shared/skills/plugin-health-daemon \
  .claude/skills/plugin-health-daemon
```

- [ ] **Step 4: Verify move**

```bash
ls /Users/russelllaing/al-dev-shared/.claude/skills/plugin-health-daemon/ \
  && echo "=== old ===" \
  && ls /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/plugin-health-daemon/ 2>&1
```

Expected: new path shows `SKILL.md`; old path shows "No such file or directory".

- [ ] **Step 5: Update plugin map — add project-local scope note**

In `docs/al-dev-plugin-map.md`, find the `/plugin-health-daemon` section heading under Layer 2 and add a scope callout immediately after it:

Old:
```markdown
### /plugin-health-daemon

Autonomous audit sweep that dispatches all plugin review skills in parallel, auto-fixes safe issues, and generates a weekly digest.
```

New:
```markdown
### /plugin-health-daemon

> **Scope: Project-local only.** Moved to `.claude/skills/plugin-health-daemon/` — not distributed in the plugin. Maintained alongside `/align-harness-repos` as internal plugin-maintenance infrastructure.

Autonomous audit sweep that dispatches all plugin review skills in parallel, auto-fixes safe issues, and generates a weekly digest.
```

- [ ] **Step 6: Verify map update**

```bash
grep -A 4 "### /plugin-health-daemon" /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md | head -6
```

Expected: shows "Scope: Project-local only" line immediately after the heading.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  .claude/skills/plugin-health-daemon \
  docs/al-dev-plugin-map.md
git -C /Users/russelllaing/al-dev-shared commit -m \
  "refactor: move plugin-health-daemon to .claude/skills/ (project-local maintenance tool, not distributed)"
```

---

## Task 7: Connect perf-analysis output to /al-dev-plan and /al-dev-fix

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` (Phase 1, after line 95)
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` (Step 3, Non-Trivial Fix, before current step 1)

**Why:** /al-dev-perf is shown as a pre-planning tributary in Layer 1 (feeding /al-dev-plan and /al-dev-fix with `perf-analysis.md`), but neither downstream skill checks for this output. Adding an optional load step closes this gap.

**Note:** The glob pattern `*-al-dev-perf-perf-analysis.md` matches the current /al-dev-perf output filename. If the Merge/explore+perf design spike (Task 9) is later implemented with a different output name, update this pattern.

- [ ] **Step 1: Confirm insertion point in al-dev-plan**

```bash
grep -n "Do not stop\." /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

Expected: line 95

- [ ] **Step 2: Insert perf load step in al-dev-plan Phase 1**

In `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, change:

Old (lines 93–97):
```markdown
   If the MCP server is unavailable or returns no results
   (e.g., no BC workspace is active), proceed directly to
   Phase 2 using general AL knowledge. Do not stop.

## Phase 1.5: Verify External Claims
```

New:
```markdown
   If the MCP server is unavailable or returns no results
   (e.g., no BC workspace is active), proceed directly to
   Phase 2 using general AL knowledge. Do not stop.

5. Load performance constraints if available:
   ```bash
   PERF=$(ls .dev/*-al-dev-perf-perf-analysis.md 2>/dev/null | sort | tail -1)
   ```
   If a file is found, read the CRITICAL and HIGH severity findings.
   Include them as **"Performance constraints from prior analysis:"** in every
   architect prompt in Phase 2. If no file exists, skip silently.

## Phase 1.5: Verify External Claims
```

- [ ] **Step 3: Verify insertion in al-dev-plan**

```bash
grep -A 8 "Do not stop\." /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md | head -10
```

Expected: "Do not stop." followed by blank line, then the new step 5 block.

- [ ] **Step 4: Confirm insertion point in al-dev-fix**

```bash
grep -n "For non-trivial fixes" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Expected: line 150

- [ ] **Step 5: Insert perf load step in al-dev-fix Step 3**

In `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`, change:

Old (lines 149–153):
```markdown
```text
For non-trivial fixes:

1. Spawn al-dev-shared:al-dev-solution-architect for quick analysis.
```

New:
```markdown
```text
For non-trivial fixes:

0. Load performance constraints if available:
   PERF=$(ls .dev/*-al-dev-perf-perf-analysis.md 2>/dev/null | sort | tail -1)
   If found: read CRITICAL/HIGH findings. Pass them as
   "Known performance constraints: [findings]" in the architect prompt (step 1).
   If not found: skip this step.

1. Spawn al-dev-shared:al-dev-solution-architect for quick analysis.
```

- [ ] **Step 6: Verify both files have the perf-analysis glob pattern**

```bash
grep -c "perf-analysis" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-plan/SKILL.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Expected: each file shows `1`.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-plan/SKILL.md \
  profile-al-dev-shared/skills/al-dev-fix/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m \
  "feat(skills): wire perf-analysis findings into al-dev-plan + al-dev-fix context"
```

---

## Task 8: Split al-dev-support-agent into researcher + reply-drafter

**Prerequisite:** Task 3 must be complete (al-dev-support-agent.md already has BC version marked as optional).

**Files:**
- Create: `profile-al-dev-shared/agents/al-dev-support-researcher.md`
- Create: `profile-al-dev-shared/agents/al-dev-support-reply-drafter.md`
- Delete: `profile-al-dev-shared/agents/al-dev-support-agent.md`
- Modify: `profile-al-dev-shared/skills/al-dev-support/SKILL.md` (Step 4)

**Why:** The agent has two separable concerns serving different audiences: (1) research and internal technical findings, (2) customer-facing reply drafting. Splitting enables independent reuse of the researcher (e.g., internal troubleshooting without drafting a reply).

**Confirmed:** `al-dev-support-agent` is referenced only by `/al-dev-support/SKILL.md` — no other callers.

- [ ] **Step 1: Create al-dev-support-researcher.md**

Create `profile-al-dev-shared/agents/al-dev-support-researcher.md` with this exact content:

```markdown
---
name: al-dev-support-researcher
description: >-
  Research a BC support query using AL symbols, MS Docs, and BC Code History.
  Produces internal technical findings. Dispatched by /al-dev-support (research
  phase). Pairs with al-dev-support-reply-drafter.
model: sonnet
tools: [
  "WebSearch", "WebFetch", "Read",
  "mcp__plugin_profile-claude-al-dev_al-mcp-server",
  "mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp"
]
---

# Agent: al-dev-support-researcher

Research BC support queries and produce internal technical findings.

## Mission

When a customer reports a BC/AL issue, research across AL symbols, MS Docs, and BC code history to find root causes and workarounds. Produce internal findings only — the customer reply is handled by al-dev-support-reply-drafter.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| QUERY_TYPE | **Yes** | `ticket`, `file`, or `freetext` — in dispatch prompt |
| QUERY_CONTEXT | **Yes** | The customer's question or symptom |
| TICKET_FILE | No | Path to ticket context file from `/al-dev-ticket`, or `NONE` |
| BC version | No | Inferred from query context if mentioned; not required from caller |

## Outputs

| Output | Description |
|--------|-------------|
| Return block | Structured internal findings returned inline to /al-dev-support |

## Research Process

**Step 1:** Parse customer query — Identify problem statement, affected features, error messages, BC version.

**Step 2: Research** — Investigate across 3 sources:

### Source 1: AL Symbols
Use AL Code Intelligence to search for relevant symbols:
- Search for error messages or class names mentioned in the issue
- Find related procedures, tables, fields
- Check procedure signatures and documentation

### Source 2: MS Docs
Use Microsoft Docs MCP to search official documentation:
- Search for the feature or error mentioned in the ticket
- Look for known issues or breaking changes
- Find configuration/setup requirements
- Search for API documentation if relevant

### Source 3: BC Code History
If available, search BC history for:
- Recent changes to related functionality
- Known bugs or fixes in specific versions
- Patterns from similar issues

**Step 3:** Synthesize findings — Combine evidence from all 3 sources into:
1. Root cause (if identifiable)
2. Workaround(s) if available
3. Recommended resolution path

## Return Block

Return to `/al-dev-support` with:

```text
RESEARCH_COMPLETE: yes
QUERY_TYPE: [ticket|file|freetext]
BC_VERSION_SCOPE: [identified BC versions or "not specified"]
SOURCES: [AL Symbols (<n> objects) | MS Docs (<n> pages) | BC History (<n> commits or NONE)]
SUMMARY: [one-sentence root cause or workaround]

## Internal Findings

### Root Cause
[Technical analysis of what's causing the issue]

### Evidence
- AL Symbol: [findings from code intelligence]
- MS Docs: [findings from official docs]
- BC History: [findings from code history, if available]

### Workarounds
[If available, actionable workarounds]

### Recommended Resolution
[Recommended path to fix]
```
```

- [ ] **Step 2: Verify researcher file exists and is non-empty**

```bash
ls -la /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-researcher.md \
  && wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-researcher.md
```

Expected: file exists with >50 lines.

- [ ] **Step 3: Create al-dev-support-reply-drafter.md**

Create `profile-al-dev-shared/agents/al-dev-support-reply-drafter.md` with this exact content:

```markdown
---
name: al-dev-support-reply-drafter
description: >-
  Draft a customer-facing reply from internal BC support research findings.
  Writes the combined findings + reply file. Dispatched by /al-dev-support
  (reply phase). Pairs with al-dev-support-researcher.
model: sonnet
tools: ["Write", "Read"]
---

# Agent: al-dev-support-reply-drafter

Draft customer-facing reply documents from internal support research findings.

## Mission

Take structured research findings from al-dev-support-researcher and produce a clear, actionable customer reply. Write both the internal findings and the draft reply to a single `.dev/` file.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| QUERY_TYPE | **Yes** | `ticket`, `file`, or `freetext` |
| QUERY_CONTEXT | **Yes** | Original customer question or symptom |
| TICKET_FILE | No | Path to ticket context file, or `NONE` |
| RESEARCHER_FINDINGS | **Yes** | Full structured output block from al-dev-support-researcher |

## Outputs

| Output | Description |
|--------|-------------|
| `.dev/<date>-support-<slug>.md` | **Primary** — Internal findings + draft customer reply |
| Return block | `FILE`, `QUERY_TYPE`, `BC_VERSION_SCOPE`, `SOURCES`, `SUMMARY` |

## Process

**Step 1:** Parse `RESEARCHER_FINDINGS` — extract root cause, evidence, workarounds, recommended resolution, BC_VERSION_SCOPE, SOURCES.

**Step 2:** Draft customer reply — translate technical findings into clear, actionable customer-facing content:
- Non-technical explanation of the root cause
- Step-by-step solution or workaround
- Escalation path if issue persists

**Step 3:** Write combined file:

```bash
FILE_PATH=".dev/$(date +%Y-%m-%d)-support-<slug>.md"
# <slug> is:
# - Ticket ID if TICKET_FILE was provided (e.g., "T-12345")
# - Query-type slug for freetext queries (e.g., "connection-error", "perf-issue")
```

Write both **Internal Findings** and **Draft Customer Reply** sections to this file.

## Output Format

```markdown
# Internal Findings

## Root Cause
[From researcher findings]

## Evidence
- AL Symbol: [from researcher]
- MS Docs: [from researcher]
- BC History: [from researcher]

## Workarounds
[From researcher findings]

---

# Draft Customer Reply

## Issue Summary
[Restate customer's problem in clear terms]

## Root Cause
[Non-technical explanation]

## Solution
[Step-by-step fix or workaround]

## If Issue Persists
[Escalation path, support contacts, debug steps]
```

## Return Block

Return to `/al-dev-support` with:

```text
FILE: .dev/YYYY-MM-DD-support-<slug>.md
QUERY_TYPE: [ticket|file|freetext]
BC_VERSION_SCOPE: [from researcher findings]
SOURCES: [from researcher findings]
SUMMARY: [one-sentence summary of root cause or workaround]
```
```

- [ ] **Step 4: Verify reply-drafter file exists and is non-empty**

```bash
ls -la /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-reply-drafter.md \
  && wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-reply-drafter.md
```

Expected: file exists with >50 lines.

- [ ] **Step 5: Update /al-dev-support SKILL.md — replace Step 4 with two-phase dispatch**

In `profile-al-dev-shared/skills/al-dev-support/SKILL.md`, replace the entire Step 4 section:

Old:
```markdown
## Step 4 — Dispatch al-dev-support-agent

Assemble the prompt envelope:

```text
QUERY_TYPE: [ticket | file | freetext]
QUERY_CONTEXT: <customer question, ticket summary, or file content>
TICKET_FILE: <.dev path if loaded, else NONE>
```

Dispatch:

```text
Agent tool:
  agent: al-dev-shared:al-dev-support-agent
  description: "BC support research: <60-char query summary>"

Prompt: <assembled prompt envelope above>
```
```

New:
```markdown
## Step 4 — Dispatch al-dev-support-researcher (research phase)

Assemble the research prompt:

```text
QUERY_TYPE: [ticket | file | freetext]
QUERY_CONTEXT: <customer question, ticket summary, or file content>
TICKET_FILE: <.dev path if loaded, else NONE>
```

Dispatch:

```text
Agent tool:
  agent: al-dev-shared:al-dev-support-researcher
  description: "BC support research: <60-char query summary>"

Prompt: <assembled prompt above>
```

## Step 4b — Dispatch al-dev-support-reply-drafter (reply phase)

Assemble the reply prompt using the researcher's output:

```text
QUERY_TYPE: [ticket | file | freetext]
QUERY_CONTEXT: <original customer question>
TICKET_FILE: <.dev path if loaded, else NONE>
RESEARCHER_FINDINGS: <full structured output block from al-dev-support-researcher>
```

Dispatch:

```text
Agent tool:
  agent: al-dev-shared:al-dev-support-reply-drafter
  description: "Draft customer reply: <60-char query summary>"

Prompt: <assembled prompt above>
```
```

- [ ] **Step 6: Delete the old combined agent**

```bash
git -C /Users/russelllaing/al-dev-shared rm profile-al-dev-shared/agents/al-dev-support-agent.md
```

- [ ] **Step 7: Confirm no remaining references to al-dev-support-agent**

```bash
grep -r "al-dev-support-agent" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/ \
  /Users/russelllaing/al-dev-shared/.claude/ 2>/dev/null
```

Expected: no output.

- [ ] **Step 8: Confirm new agent references in al-dev-support skill**

```bash
grep "al-dev-support-researcher\|al-dev-support-reply-drafter" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-support/SKILL.md
```

Expected: both agent names appear.

- [ ] **Step 9: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/agents/al-dev-support-researcher.md \
  profile-al-dev-shared/agents/al-dev-support-reply-drafter.md \
  profile-al-dev-shared/skills/al-dev-support/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m \
  "refactor(agents): split al-dev-support-agent into researcher + reply-drafter"
```

---

## Task 9: Design spike — Merge /al-dev-explore + /al-dev-perf

**Files:**
- Create: `docs/superpowers/specs/2026-05-21-explore-perf-merge-design.md`

**Why:** The plugin map suggests merging these skills, but rubber-ducking found 4 structural differences not captured in the suggestion. This spec documents them and proposes a concrete unified design before implementation is attempted.

- [ ] **Step 1: Read both skill files in full**

Read these files before writing the spec:
- `profile-al-dev-shared/skills/al-dev-explore/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-perf/SKILL.md`

Note the exact content of the spawn prompts, Step 1a metadata gathering, and output filenames from each.

- [ ] **Step 2: Create the design spec**

Create `docs/superpowers/specs/2026-05-21-explore-perf-merge-design.md` with this structure. Fill each bracketed section with actual content from the skill files:

```markdown
# Design Spec: Merge /al-dev-explore + /al-dev-perf

**Status:** Draft — run /plan-map-changes after approving this design to generate the implementation plan
**Date:** 2026-05-21
**Source:** docs/al-dev-plugin-map.md — Architectural suggestions > Merge

---

## Problem Statement

Both /al-dev-explore and /al-dev-perf spawn a single Explore subagent and write a dated `.dev/`
output file. The plugin map suggests merging into a unified skill with a mode flag. However,
rubber-ducking found 4 structural differences that must be explicitly resolved in this design.

## Structural Differences (verified by rubber-ducking)

| Aspect | /al-dev-explore | /al-dev-perf |
|--------|-----------------|--------------|
| Pre-spawn MCP step | None | Step 1a: al_get_object_summary + al_search_object_members classify each codeunit |
| Spawn prompt template | [paste the Step 2 prompt summary from al-dev-explore] | [paste the Step 2 prompt summary from al-dev-perf] |
| Anti-patterns reference | None | Reads knowledge/perf-anti-patterns-prompt.md and pastes full content into spawn prompt |
| Output filename | *-al-dev-explore-findings.md | *-al-dev-perf-perf-analysis.md |
| Context integration | Step 4: offers to update project-context.md | None |

## Proposed Unified Interface

```
/al-dev-explore [question]       # general mode (default)
/al-dev-explore --perf [scope]   # performance mode
/al-dev-explore --perf scan all  # performance scan, all codeunits
```

Flag: `--perf` (boolean) — avoids collision with the existing file/directory scope argument
that /al-dev-perf already uses.

## Step Mapping

| Step | General mode | Performance mode (--perf) |
|------|-------------|--------------------------|
| Step 0 | — | MCP classification: al_get_object_summary + al_search_object_members for each codeunit |
| Step 1 | Load context (project-context.md, ticket context) | Determine scope (codeunit files) |
| Step 2 | Spawn Explore subagent with general prompt | Spawn Explore subagent with perf prompt + classification + anti-patterns content |
| Step 3 | Write findings | Write perf analysis |
| Step 4 | Context integration (offer project-context.md update) | Present result + suggest /al-dev-plan |

## Output Filenames

- General mode: `.dev/$(date +%Y-%m-%d)-al-dev-explore-findings.md`  
- Performance mode: `.dev/$(date +%Y-%m-%d)-al-dev-perf-perf-analysis.md`

Performance mode preserves the existing filename so that the Connect wiring added in
docs/superpowers/plans/2026-05-21-plugin-map-improvements.md Task 7 continues to work without
changes. The glob pattern `*-al-dev-perf-perf-analysis.md` in /al-dev-plan and /al-dev-fix
remains valid.

## Spawn Prompt Templates

### General mode prompt
[Paste the full Step 2 spawn prompt from al-dev-explore/SKILL.md here]

### Performance mode prompt
[Paste the full Step 2 spawn prompt from al-dev-perf/SKILL.md here, including the
perf-anti-patterns-prompt.md reference instruction]

## Files to Change (when this design is approved)

- Modify `profile-al-dev-shared/skills/al-dev-explore/SKILL.md` — add --perf mode
- Delete `profile-al-dev-shared/skills/al-dev-perf/SKILL.md`
- Update `docs/al-dev-plugin-map.md` — remove /al-dev-perf from Layer 1 tributary and Layer 2

## Open Questions

1. Should Step 4 (context integration) run in performance mode? Recommendation: No — current
   /al-dev-perf does not do context integration; keep behaviour consistent.
2. Should the anti-patterns file be embedded in the unified skill or always read at runtime?
   Recommendation: keep as a runtime read (`knowledge/perf-anti-patterns-prompt.md`) so the
   anti-patterns can be updated without changing the skill.
```

- [ ] **Step 3: Verify spec file exists and has no forbidden patterns**

```bash
ls -la /Users/russelllaing/al-dev-shared/docs/superpowers/specs/2026-05-21-explore-perf-merge-design.md \
  && grep -n "TODO\|TBD\|\[date\]\|YYYY-MM-DD" \
     /Users/russelllaing/al-dev-shared/docs/superpowers/specs/2026-05-21-explore-perf-merge-design.md
```

Expected: file exists; no forbidden patterns.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  docs/superpowers/specs/2026-05-21-explore-perf-merge-design.md
git -C /Users/russelllaing/al-dev-shared commit -m \
  "docs: design spike for merging /al-dev-explore + /al-dev-perf"
```

---

## Task 10: Design spike — Merge /al-dev-ticket + /al-dev-support

**Files:**
- Create: `docs/superpowers/specs/2026-05-21-ticket-support-merge-design.md`

**Why:** The plugin map suggests consolidating via a `--mode` flag, but rubber-ducking revealed that input type routing (ticket#/file/freetext) is orthogonal to action level (context-only vs research+reply). The mode flag alone is insufficient without a clear input routing design.

- [ ] **Step 1: Read both skill files in full**

Read these files before writing the spec:
- `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-support/SKILL.md`

Note the keyword search step (Step 1.5 in /al-dev-ticket), the three input types handled by /al-dev-support, and where each dispatches al-dev-ticket-agent.

- [ ] **Step 2: Create the design spec**

Create `docs/superpowers/specs/2026-05-21-ticket-support-merge-design.md` with this structure:

```markdown
# Design Spec: Merge /al-dev-ticket + /al-dev-support

**Status:** Draft — run /plan-map-changes after approving this design to generate the implementation plan
**Date:** 2026-05-21
**Source:** docs/al-dev-plugin-map.md — Architectural suggestions > Merge

---

## Problem Statement

/al-dev-support is a superset of /al-dev-ticket for the ticket-fetch use case — it already
dispatches al-dev-ticket-agent internally. The plugin map suggests consolidating into one skill.
However, input type (ticket# vs file vs freetext) is orthogonal to action level (context-only vs
research+reply). A unified design must handle both dimensions.

## What Each Skill Does Today

### /al-dev-ticket (steps summarised)
[Summarise the 4-step flow from the SKILL.md, highlighting Step 1.5 keyword search and the
optional attachment download as unique capabilities]

### /al-dev-support (steps summarised)
[Summarise the 5-step flow from the SKILL.md, highlighting the three input types and how each
feeds into the agent dispatch]

## Key Observation: Two Orthogonal Dimensions

1. **Input type** (what you provide): ticket#, keyword search, file path, free text, or nothing
2. **Action level** (what you want): context-only (load ticket) vs full research + reply

The mode flag controls action level. Input type is determined by argument shape.

## Proposed Unified Interface

```
/al-dev-support [input]           # full research + reply (default)
/al-dev-support [input] --fetch   # context-only (ticket fetch)
```

Where `[input]` follows the same routing as today:
| Input pattern | Treatment |
|---------------|-----------|
| Numeric / FD-NNNN | Freshdesk ticket |
| `search <terms>` | Keyword search → user picks ticket |
| File path | Read file as query body |
| No argument | Branch auto-detect → ticket or prompt |
| Other text | Free-text query |

The keyword search capability (currently in /al-dev-ticket Step 1.5) is preserved in the unified skill.

## Action Routing

| Flag | Action |
|------|--------|
| (none) | Full research + reply via al-dev-support-researcher + al-dev-support-reply-drafter |
| `--fetch` | Context-only via al-dev-ticket-agent; write ticket-context.md; stop |

## Alias Recommendation

Keep `/al-dev-ticket` as a one-line redirecting alias:

```
/al-dev-ticket redirects to /al-dev-support --fetch [args]
```

This preserves muscle memory without maintaining duplicate logic.

## Files to Change (when this design is approved)

- Modify `profile-al-dev-shared/skills/al-dev-support/SKILL.md` — add --fetch routing + keyword search
- Keep `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md` — replace body with redirect notice
- No agent changes needed (al-dev-ticket-agent and the split researcher/drafter agents are unchanged)
- Update `docs/al-dev-plugin-map.md` — note /al-dev-ticket as alias

## Open Questions

1. Should `--fetch` be `--fetch-only` or `--context-only`? Recommendation: `--fetch` — short, matches
   the agent's "phase: fetch" wording, unambiguous.
2. Should /al-dev-ticket be deleted entirely or kept as an alias? Recommendation: keep as alias for
   one release cycle, then remove.
```

- [ ] **Step 3: Verify spec file exists and has no forbidden patterns**

```bash
ls -la /Users/russelllaing/al-dev-shared/docs/superpowers/specs/2026-05-21-ticket-support-merge-design.md \
  && grep -n "TODO\|TBD\|\[date\]\|YYYY-MM-DD" \
     /Users/russelllaing/al-dev-shared/docs/superpowers/specs/2026-05-21-ticket-support-merge-design.md
```

Expected: file exists; no forbidden patterns.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  docs/superpowers/specs/2026-05-21-ticket-support-merge-design.md
git -C /Users/russelllaing/al-dev-shared commit -m \
  "docs: design spike for merging /al-dev-ticket + /al-dev-support"
```

---

## Task 11: Design spike — Atomise /al-dev-develop

**Files:**
- Create: `docs/superpowers/specs/2026-05-21-develop-atomise-design.md`

**Why:** The plugin map suggests extracting Phases 5–6 but rubber-ducking found the real extract is Phases 5–10 (6 phases, not 2). Autonomous mode adds interleaved phases (1.5 stays in implementation half; 4.5 moves to review half). A handoff contract must be defined before this refactor is planned.

- [ ] **Step 1: Read the skill file and note all phase headers**

```bash
grep -n "^## Phase" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: shows Phase 0, 0.5, 1, 1.5, 2, 3, 4, 4.5, 5, 6, 7, 8, 9, 10.

Read the full skill file before writing the spec.

- [ ] **Step 2: Create the design spec**

Create `docs/superpowers/specs/2026-05-21-develop-atomise-design.md` with this structure:

```markdown
# Design Spec: Atomise /al-dev-develop

**Status:** Draft — run /plan-map-changes after approving this design to generate the implementation plan
**Date:** 2026-05-21
**Source:** docs/al-dev-plugin-map.md — Architectural suggestions > Atomise

---

## Problem Statement

/al-dev-develop spans ~14 phases with two separable concern groups. Splitting enables the review
pipeline to run independently (e.g., post-hoc code review, iterative review gates). The plugin map
suggests extracting "Phases 5–6" but rubber-ducking found the real extract is Phases 5–10 with
autonomous-mode phases 4.5 also moving to the review half.

## Phase Inventory and Split

| Phase | Name | Belongs to |
|-------|------|------------|
| 0 | Check for Existing Progress | /al-dev-develop |
| 0.5 | Context Preservation Checkpoint | /al-dev-develop |
| 1 | Read Context | /al-dev-develop |
| 1.5 | Signature Verification (--autonomous) | /al-dev-develop |
| 2 | Partition Work | /al-dev-develop |
| 3 | Spawn Developer Team | /al-dev-develop |
| 4 | Verify on Completion | /al-dev-develop |
| 4.5 | Static Validation (--autonomous) | /al-dev-review-develop (pre-review check) |
| 5 | Spawn Review Team | /al-dev-review-develop |
| 6 | Synthesise Review Findings | /al-dev-review-develop |
| 7 | Manage Review Iteration | /al-dev-review-develop |
| 8 | Compilation & Error Handling | /al-dev-review-develop |
| 9 | Validate and Write Code Review | /al-dev-review-develop |
| 10 | Present to User for Approval | /al-dev-review-develop |

## Handoff Contract

After Phase 4 completes, /al-dev-develop writes:
`.dev/$(date +%Y-%m-%d)-al-dev-develop-implementation-complete.md`

Content:
```markdown
# Implementation Complete — Handoff for Review

## Summary
- Developers spawned: [N]
- Files implemented: [list]
- Object IDs used: [ranges]

## Context
- Solution plan: [path from ls glob]
- Project context: .dev/project-context.md (if exists)
- Compilation: not yet run (review half runs compile in Phase 8)

## Autonomous (if --autonomous flag was used)
- Verified signatures: .dev/*-al-dev-autonomous-signatures.md
- Static validation: Phase 4.5 will run as first step of /al-dev-review-develop
```

/al-dev-review-develop starts by reading the latest handoff marker to establish context.

## Autonomous Mode Split

| Phase | --autonomous trigger | Location |
|-------|---------------------|----------|
| 1.5 | Signature Verification | /al-dev-develop |
| 4.5 | Static Validation | /al-dev-review-develop (first step) |

Both skills gate their autonomous phases on the `--autonomous` flag passed at invocation.
Users run `/al-dev-develop --autonomous` then `/al-dev-review-develop --autonomous`.

## Validator Relocation

`profile-al-dev-shared/skills/al-dev-develop/validate-code-review.py` is referenced in Phase 9.
When Phase 9 moves to /al-dev-review-develop:

1. Copy validator to `profile-al-dev-shared/skills/al-dev-review-develop/validate-code-review.py`
2. Update the VALIDATOR path in Phase 9 to use the new skill directory
3. Keep original in `skills/al-dev-develop/` for now (remove in a follow-up once stable)

## New Skill Interfaces

`/al-dev-develop [--autonomous] [scope]`
- Phases 0–4 only
- Final phase 4 message: "Implementation complete → run /al-dev-review-develop to run review pipeline."

`/al-dev-review-develop [--autonomous]`
- Reads latest `*-al-dev-develop-implementation-complete.md`
- Phases 4.5 (if --autonomous) through 10
- Produces code-review.md as today

## Files to Change (when this design is approved)

- Modify `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` — truncate at Phase 4, add handoff write
- Create `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` — Phases 4.5–10
- Create `profile-al-dev-shared/skills/al-dev-review-develop/validate-code-review.py` — copy from al-dev-develop
- Update `docs/al-dev-plugin-map.md` — add /al-dev-review-develop in Layer 1 and Layer 2

## Risk: User Workflow Change

Current: `/al-dev-develop` is a complete end-to-end command.
After: users run two commands sequentially.

Mitigation: Phase 4 final message must explicitly name the next command. Consider adding a
`/al-dev-review-develop` shortcut that checks for an unreviewed handoff marker and auto-invokes.
```

- [ ] **Step 3: Verify spec file exists and has no forbidden patterns**

```bash
ls -la /Users/russelllaing/al-dev-shared/docs/superpowers/specs/2026-05-21-develop-atomise-design.md \
  && grep -n "TODO\|TBD\|\[date\]\|YYYY-MM-DD" \
     /Users/russelllaing/al-dev-shared/docs/superpowers/specs/2026-05-21-develop-atomise-design.md
```

Expected: file exists; no forbidden patterns.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  docs/superpowers/specs/2026-05-21-develop-atomise-design.md
git -C /Users/russelllaing/al-dev-shared commit -m \
  "docs: design spike for atomising /al-dev-develop into implementation + review skills"
```

---

## Self-Review Notes

**Spec coverage:**
- A1 (Trim code-review) → Task 1 ✓
- A2 (Trim reviewers) → Task 2 ✓
- B1 (Align support-agent) → Task 3 ✓
- B2 (Align commit-recover-verifier) → Task 4 ✓
- C1 (Move al-dev-align) → Task 5 ✓
- C2 (Move plugin-health-daemon) → Task 6 ✓
- D1 (Connect perf-analysis) → Task 7 ✓
- E1 (Split support-agent) → Task 8 ✓
- F1 (Explore+Perf merge spike) → Task 9 ✓
- F2 (Ticket+Support merge spike) → Task 10 ✓
- F3 (Atomise develop spike) → Task 11 ✓
- Skipped (Trim docs-writer/script-engineer/support-agent) → correctly excluded ✓
- Skipped (Extend /al-dev-deploy) → correctly excluded ✓

**Placeholder scan:** No TBD, TODO, YYYY-MM-DD literal, or `[date]` patterns in plan body.

**Type consistency:**
- Agent names used consistently: `al-dev-support-researcher`, `al-dev-support-reply-drafter`
- All git commands use `git -C /Users/russelllaing/al-dev-shared` (never bare `cd` + git)
- File paths consistent throughout
