# Release Notes Agent: Add MCP Tools to Frontmatter

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `al-mcp-server` and `bc-code-intelligence-mcp` to the `al-dev-release-notes-agent` tools list so its `research-context` phase can actually call AL symbols and BC expert MCP tools.

**Architecture:** Single frontmatter edit to `al-dev-release-notes-agent.md` — the agent body already has the correct MCP call instructions, but the harness only gives agents access to tools they've explicitly declared. Without the declaration, the entire research-context phase silently fails. Also update `docs/al-dev-agent-map.md` to keep the map accurate.

**Tech Stack:** Markdown frontmatter (YAML), no code changes.

---

### Task 1: Add MCP Tools to Agent Frontmatter

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-release-notes-agent.md:7`

The current tools list on line 7:

```yaml
tools: ["Bash", "Write", "Read", "Glob"]
```

- [ ] **Step 1: Edit the frontmatter tools list**

Replace the tools line with the expanded list that matches the pattern used in `al-dev-solution-architect.md` (lines 6–11 of that file — verified working MCP format):

```yaml
tools: [
  "Bash", "Write", "Read", "Glob",
  "mcp__plugin_profile-claude-al-dev_al-mcp-server",
  "mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp"
]
```

- [ ] **Step 2: Verify the edit**

Run:
```bash
head -12 profile-al-dev-shared/agents/al-dev-release-notes-agent.md
```

Expected output shows the tools array spanning lines 7–11 with both MCP entries present and no other frontmatter lines disturbed.

- [ ] **Step 3: Scan for forbidden patterns**

```bash
grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]" profile-al-dev-shared/agents/al-dev-release-notes-agent.md
```

Expected: no output (zero matches).

---

### Task 2: Update Agent Map

**Files:**
- Modify: `docs/al-dev-agent-map.md`

Two sections need updating:

**Layer 1 table (around line 18):**  
Current:
```
| al-dev-release-notes-agent | sonnet | Bash, Write, Read, Glob | /al-dev-release-notes |
```
Update to:
```
| al-dev-release-notes-agent | sonnet | Bash, Write, Read, Glob, mcp:al-mcp-server, mcp:bc-code-intelligence-mcp | /al-dev-release-notes |
```

**Layer 2 profile (around lines 190–198):**  
Current:
```
**Tools:** Bash, Write, Read, Glob
```
Update to:
```
**Tools:** Bash, Write, Read, Glob, mcp:al-mcp-server, mcp:bc-code-intelligence-mcp
```

- [ ] **Step 1: Edit the Layer 1 table row for al-dev-release-notes-agent**

Find the exact row in the table and update the Tools column to include the two MCP entries.

- [ ] **Step 2: Edit the Layer 2 profile Tools line for al-dev-release-notes-agent**

Update the `**Tools:**` line in the `### al-dev-release-notes-agent` section.

- [ ] **Step 3: Verify both edits**

```bash
grep -n "release-notes-agent\|al-mcp-server\|bc-code-intelligence" docs/al-dev-agent-map.md
```

Expected: both the Layer 1 table row and the Layer 2 profile line show the MCP tools.

---

### Task 3: Commit

- [ ] **Step 1: Check git status**

```bash
git status
```

Expected: two modified files — `profile-al-dev-shared/agents/al-dev-release-notes-agent.md` and `docs/al-dev-agent-map.md`. No unintended extras.

- [ ] **Step 2: Verify line counts haven't shrunk**

```bash
wc -l profile-al-dev-shared/agents/al-dev-release-notes-agent.md docs/al-dev-agent-map.md
```

Expected: agent file increases by ~2 lines (single-line tools becoming multi-line); agent map stays same or increases by 0–1 lines.

- [ ] **Step 3: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-release-notes-agent.md docs/al-dev-agent-map.md
git commit -m "$(cat <<'EOF'
fix(agents): add MCP tools to al-dev-release-notes-agent frontmatter

The research-context phase calls al_get_object_summary,
al_get_object_definition, and ask_bc_expert, but the harness
only grants agents access to declared tools. Without the
declaration, the entire AL context enrichment phase silently
fails on every release notes run.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

Expected: commit succeeds, hooks pass.
