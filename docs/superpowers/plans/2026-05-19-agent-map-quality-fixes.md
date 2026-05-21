# Agent Map Quality Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix four quality issues in agent definitions (missing Write step, unused tools, misleading description) identified by `/analyze-agent-design`.

**Architecture:** Four independent agent file edits. Changes are surgical: add explicit Write step + return block to al-dev-support-agent, trim unused Bash tool from two agents, clarify al-dev-code-review's role as standalone (not team member).

**Tech Stack:** Agent markdown files with YAML frontmatter; verification via `wc -l`, `grep`, `git diff`.

---

### Task 1: Add Write step and return block to al-dev-support-agent

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-support-agent.md:102-108`

- [ ] **Step 1: Read current file to verify line count**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md
```

Expected: `109 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md` (or close)

- [ ] **Step 2: Insert Write step and return block section**

Add **after line 101** (after the closing triple backticks of Output Format) and **before line 103** (before Env Var Handling).

Insert this exact text:

```markdown

## Write Output

After synthesizing findings, write the combined internal + customer-facing document to disk:

```bash
FILE_PATH=".dev/$(date +%Y-%m-%d)-support-<slug>.md"
# Where <slug> is:
# - Ticket ID if TICKET_FILE was provided (e.g., "T-12345")
# - Query-type slug for freetext queries (e.g., "connection-error", "perf-issue")
```

Write both the **Internal Findings** and **Draft Customer Reply** sections (formatted as shown in Output Format above) to this file.

## Return Block

Return to `/al-dev-support` with:

```
FILE: .dev/YYYY-MM-DD-support-<slug>.md
QUERY_TYPE: [ticket|file|freetext]
BC_VERSION_SCOPE: [identified BC versions or "not specified"]
SOURCES: [AL Symbols|MS Docs|BC History|combinations thereof]
SUMMARY: [one-sentence summary of root cause or workaround]
```
```

- [ ] **Step 3: Verify line count increased by correct amount**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md
```

Expected: `136` lines (109 + 27 for the new section)

- [ ] **Step 4: Verify Write is now referenced in the new content**

```bash
grep -n "Write" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md | tail -5
```

Expected: Output should show "Write" mention in the new "Write Output" section around line 104–105

- [ ] **Step 5: Verify no forbidden patterns in modified file**

```bash
grep -E "TODO|TBD|YYYY-MM-DD" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md
```

Expected: `grep` returns only the literal `YYYY-MM-DD` pattern in the return block documentation (which is correct — it's a template example), not an actual unrendered date.

- [ ] **Step 6: Commit**

```bash
cd /Users/russelllaing/al-dev-shared && git add profile-al-dev-shared/agents/al-dev-support-agent.md && git commit -m "feat(al-dev-support-agent): add explicit Write step and return block contract"
```

Expected: Commit succeeds, shows 1 file changed

---

### Task 2: Remove unused Bash tool from al-dev-support-agent

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-support-agent.md:7-11` (frontmatter tools list)

- [ ] **Step 1: Read current frontmatter to identify tool line**

```bash
head -12 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md
```

Expected: Shows tools array with `"Bash"` in the list (line 8)

- [ ] **Step 2: Remove "Bash" from tools list**

Current lines 7–11:
```
tools: [
  "WebSearch", "WebFetch", "Bash", "Write", "Read",
  "mcp__plugin_profile-claude-al-dev_al-mcp-server",
  "mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp"
]
```

Replace with:
```
tools: [
  "WebSearch", "WebFetch", "Write", "Read",
  "mcp__plugin_profile-claude-al-dev_al-mcp-server",
  "mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp"
]
```

(Remove `"Bash", ` from line 8, including the comma and space)

- [ ] **Step 3: Verify "Bash" is removed from tools**

```bash
grep -A 4 "^tools:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md | head -5
```

Expected: No "Bash" in the output; tools array shows only WebSearch, WebFetch, Write, Read, and the MCP servers

- [ ] **Step 4: Verify line count unchanged from Task 1**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-agent.md
```

Expected: Still `136` lines (same as after Task 1, since we only removed text from one line, not a full line)

- [ ] **Step 5: Commit**

```bash
cd /Users/russelllaing/al-dev-shared && git add profile-al-dev-shared/agents/al-dev-support-agent.md && git commit -m "fix(al-dev-support-agent): remove unused Bash tool from frontmatter"
```

Expected: Commit succeeds, shows 1 file changed

---

### Task 3: Remove unused Bash tool from al-dev-docs-writer

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-docs-writer.md:7` (frontmatter tools list)

- [ ] **Step 1: Read current frontmatter**

```bash
head -8 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-docs-writer.md
```

Expected: Line 7 shows `tools: ["Read", "Write", "Glob", "Grep", "Bash"]`

- [ ] **Step 2: Remove "Bash" from tools list**

Current line 7:
```
tools: ["Read", "Write", "Glob", "Grep", "Bash"]
```

Replace with:
```
tools: ["Read", "Write", "Glob", "Grep"]
```

(Remove `", Bash"` from the end of the array)

- [ ] **Step 3: Verify "Bash" is removed**

```bash
grep "^tools:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-docs-writer.md
```

Expected: `tools: ["Read", "Write", "Glob", "Grep"]` (no Bash)

- [ ] **Step 4: Verify line count is unchanged (removing text from one line doesn't remove a line)**

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-docs-writer.md
```

Expected: Same as before (120 or 121 lines, depending on starting state)

- [ ] **Step 5: Commit**

```bash
cd /Users/russelllaing/al-dev-shared && git add profile-al-dev-shared/agents/al-dev-docs-writer.md && git commit -m "fix(al-dev-docs-writer): remove unused Bash tool from frontmatter"
```

Expected: Commit succeeds, shows 1 file changed

---

### Task 4: Update al-dev-code-review description and role statement

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md:2-5` (frontmatter description)
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md:18` (role statement)

- [ ] **Step 1: Read current description and role**

```bash
head -20 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-code-review.md
```

Expected: Shows old description mentioning "3-specialist team" and role saying "You may be spawned as part of a 3-reviewer team"

- [ ] **Step 2: Update frontmatter description (lines 2–5)**

Current:
```
description: >-
  General code review specialist — finds bugs, logic errors, and security
  issues with high signal-to-noise ratio. Standalone reviewer or part of
  the automated /al-dev-develop 3-specialist team.
```

Replace with:
```
description: >-
  General code review specialist — finds bugs, logic errors, and security
  issues with high signal-to-noise ratio. Available for standalone use;
  not integrated into /al-dev-develop (which uses specialist reviewers
  for security, patterns, and performance).
```

- [ ] **Step 3: Update role statement (line 18)**

Current line 18:
```
You may be spawned as part of a 3-reviewer team (security, expert patterns, performance) or independently for standalone reviews. When part of a team, focus on general code quality — leave specialized concerns to other reviewers.
```

Replace with:
```
This agent is available for standalone use as a general code reviewer. It is not integrated into the /al-dev-develop review pipeline, which dispatches specialized reviewers (security, patterns, performance) instead.
```

- [ ] **Step 4: Verify description no longer mentions team membership**

```bash
grep -i "3-specialist\|3-reviewer\|part of the automated" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-code-review.md
```

Expected: No matches (all mentions removed)

- [ ] **Step 5: Verify new clarifying text is present**

```bash
grep "standalone use\|not integrated" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-code-review.md
```

Expected: Output shows both phrases present in the file

- [ ] **Step 6: Commit**

```bash
cd /Users/russelllaing/al-dev-shared && git add profile-al-dev-shared/agents/al-dev-code-review.md && git commit -m "docs(al-dev-code-review): clarify agent is standalone, not part of /al-dev-develop team"
```

Expected: Commit succeeds, shows 1 file changed

---

## Self-Review Checklist

✓ **Spec coverage:** All four rubber-ducked items addressed:
  - Task 1: Align — al-dev-support-agent missing Write step
  - Task 2: Trim — al-dev-support-agent Bash unused
  - Task 3: Trim — al-dev-docs-writer Bash unused
  - Task 4: Align — al-dev-code-review description misleading

✓ **Placeholder scan:** No "TODO", "TBD", unrendered dates, or incomplete steps.

✓ **Type consistency:** File paths are exact; no signature mismatches.
