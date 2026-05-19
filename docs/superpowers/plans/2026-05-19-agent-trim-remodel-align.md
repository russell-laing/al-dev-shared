# Agent Quality Suggestions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply five quality suggestions from `docs/al-dev-agent-map.md` — trim unused Glob tools from three agents, downgrade al-dev-explore to haiku, and fix the misleading al-dev-code-review description.

**Architecture:** All changes are frontmatter-only (tools list or model field) or description-only edits using exact string replacements. No logic changes, no new files, no structural moves. The agent-map catalog and Observations section are updated in the final task to keep the map consistent with the agents.

**Tech Stack:** Edit tool (exact string match); grep/wc-l for verification; git for commits.

---

## File Structure

| File | Change |
|------|--------|
| `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md` | Remove `"Glob"` from `tools:` frontmatter |
| `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md` | Remove `"Glob"` from `tools:` frontmatter |
| `profile-al-dev-shared/agents/al-dev-release-notes-agent.md` | Remove `"Glob"` from `tools:` frontmatter |
| `profile-al-dev-shared/agents/al-dev-explore.md` | Change `model: sonnet` → `model: haiku` |
| `profile-al-dev-shared/agents/al-dev-code-review.md` | Replace frontmatter description (5 lines → 5 lines) |
| `docs/al-dev-agent-map.md` | Update al-dev-explore catalog row model; mark 5 suggestions ← implemented |

---

## Task 1: Trim Glob from Three Agents

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md:7`
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md:8`
- Modify: `profile-al-dev-shared/agents/al-dev-release-notes-agent.md:7-11`

- [ ] **Step 1: Confirm Glob is present in all three agents before editing**

```bash
grep -n '"Glob"' \
  profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md \
  profile-al-dev-shared/agents/al-dev-commit-agent-execute.md \
  profile-al-dev-shared/agents/al-dev-release-notes-agent.md
```

Expected output — 3 matches, one per file:
```
profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md:7:tools: ["Bash", "Read", "Glob"]
profile-al-dev-shared/agents/al-dev-commit-agent-execute.md:8:tools: ["Bash", "Read", "Glob"]
profile-al-dev-shared/agents/al-dev-release-notes-agent.md:8:  "Bash", "Write", "Read", "Glob",
```

If any file shows zero matches, stop and report — the agent may have already been edited.

- [ ] **Step 2: Edit al-dev-commit-agent-analysis.md — remove Glob**

Use the Edit tool with this exact replacement:

```
old_string: tools: ["Bash", "Read", "Glob"]
new_string: tools: ["Bash", "Read"]
```

File: `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md`

- [ ] **Step 3: Edit al-dev-commit-agent-execute.md — remove Glob**

Use the Edit tool with this exact replacement:

```
old_string: tools: ["Bash", "Read", "Glob"]
new_string: tools: ["Bash", "Read"]
```

File: `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`

- [ ] **Step 4: Edit al-dev-release-notes-agent.md — remove Glob from multiline array**

Use the Edit tool with this exact replacement:

```
old_string:
tools: [
  "Bash", "Write", "Read", "Glob",
  "mcp__plugin_profile-claude-al-dev_al-mcp-server",
  "mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp"
]

new_string:
tools: [
  "Bash", "Write", "Read",
  "mcp__plugin_profile-claude-al-dev_al-mcp-server",
  "mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp"
]
```

File: `profile-al-dev-shared/agents/al-dev-release-notes-agent.md`

- [ ] **Step 5: Verify — Glob is gone from all three agents**

```bash
grep -n '"Glob"' \
  profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md \
  profile-al-dev-shared/agents/al-dev-commit-agent-execute.md \
  profile-al-dev-shared/agents/al-dev-release-notes-agent.md
```

Expected: no output (zero matches). If any match remains, re-examine that file and repeat the relevant Edit step.

- [ ] **Step 6: Verify — forbidden patterns and git status**

```bash
# Confirm no forbidden patterns in changed files
grep -E '\[date\]|YYYY-MM-DD|TODO|TBD|Co-Authored-By|claude:|copilot:' \
  profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md \
  profile-al-dev-shared/agents/al-dev-commit-agent-execute.md \
  profile-al-dev-shared/agents/al-dev-release-notes-agent.md || echo "Clean"

# Git status — expect exactly 3 modified files
git status --short
```

Expected: `grep` outputs "Clean"; `git status` shows `M` for all three agent files and nothing else.

- [ ] **Step 7: Commit**

```bash
git add \
  profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md \
  profile-al-dev-shared/agents/al-dev-commit-agent-execute.md \
  profile-al-dev-shared/agents/al-dev-release-notes-agent.md
git commit -m "refactor(agents): remove unused Glob tool from commit and release-notes agents

WHY: Glob was never called in any of the three agent bodies — all file
discovery goes through Bash (git diff commands) or direct Read/Write.
Removing it tightens least-privilege posture.

CHANGED COMPONENTS
- al-dev-commit-agent-analysis.md [m]
- al-dev-commit-agent-execute.md [m]
- al-dev-release-notes-agent.md [m]"
```

---

## Task 2: Remodel al-dev-explore to Haiku + Update Map Catalog

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-explore.md:8`
- Modify: `docs/al-dev-agent-map.md:16` (catalog row)

- [ ] **Step 1: Confirm current model is sonnet**

```bash
grep -n 'model:' profile-al-dev-shared/agents/al-dev-explore.md
```

Expected:
```
8:model: sonnet
```

- [ ] **Step 2: Edit al-dev-explore.md — change model to haiku**

Use the Edit tool with this exact replacement:

```
old_string: model: sonnet
new_string: model: haiku
```

File: `profile-al-dev-shared/agents/al-dev-explore.md`

Note: This file has only one `model:` line (the frontmatter). If the Edit tool reports a non-unique match, read the file to identify which line to target.

- [ ] **Step 3: Confirm current catalog row shows sonnet**

```bash
grep -n 'al-dev-explore' docs/al-dev-agent-map.md | head -5
```

Expected to include a line like:
```
16:| al-dev-explore | sonnet | Read, Glob, Grep | (none found — skill uses built-in Explore type) |
```

- [ ] **Step 4: Edit docs/al-dev-agent-map.md — update catalog row**

Use the Edit tool with this exact replacement:

```
old_string: | al-dev-explore | sonnet | Read, Glob, Grep | (none found — skill uses built-in Explore type) |
new_string: | al-dev-explore | haiku | Read, Glob, Grep | (none found — skill uses built-in Explore type) |
```

File: `docs/al-dev-agent-map.md`

- [ ] **Step 5: Verify both changes**

```bash
grep -n 'model:' profile-al-dev-shared/agents/al-dev-explore.md
grep -n 'al-dev-explore' docs/al-dev-agent-map.md | head -3
```

Expected:
```
8:model: haiku
16:| al-dev-explore | haiku | Read, Glob, Grep | ...
```

- [ ] **Step 6: Verify — forbidden patterns and git status**

```bash
grep -E '\[date\]|YYYY-MM-DD|TODO|TBD|Co-Authored-By|claude:|copilot:' \
  profile-al-dev-shared/agents/al-dev-explore.md \
  docs/al-dev-agent-map.md || echo "Clean"

git status --short
```

Expected: "Clean"; `git status` shows `M` for both files (and the 3 already-committed agent files should be gone from status).

- [ ] **Step 7: Commit**

```bash
git add \
  profile-al-dev-shared/agents/al-dev-explore.md \
  docs/al-dev-agent-map.md
git commit -m "refactor(agents): downgrade al-dev-explore to haiku model

WHY: The 42-line system prompt is search-and-summarize retrieval with no
multi-file synthesis or competitive reasoning — haiku-appropriate. Agent
has no automated callers so this only affects direct spawn usage.

CHANGED COMPONENTS
- al-dev-explore.md [m]
- al-dev-agent-map.md [m]"
```

---

## Task 3: Align al-dev-code-review Description

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md:3-8`

- [ ] **Step 1: Confirm current description contains the misleading "alongside" text**

```bash
grep -n 'alongside' profile-al-dev-shared/agents/al-dev-code-review.md
```

Expected:
```
5:  the 3-specialist parallel review team alongside al-dev-security-reviewer,
```

- [ ] **Step 2: Edit al-dev-code-review.md — replace description**

Use the Edit tool with this exact replacement:

```
old_string:
description: >-
  General code review specialist — finds bugs, logic errors, and security
  issues with high signal-to-noise ratio. Use standalone or as part of
  the 3-specialist parallel review team alongside al-dev-security-reviewer,
  al-dev-expert-reviewer, and al-dev-performance-reviewer.

new_string:
description: >-
  General code review specialist — finds bugs, logic errors, and security
  issues with high signal-to-noise ratio. For standalone manual use only;
  not part of the automated /al-dev-develop pipeline (which uses the
  3-specialist team: security-reviewer, expert-reviewer, performance-reviewer).
```

File: `profile-al-dev-shared/agents/al-dev-code-review.md`

- [ ] **Step 3: Verify — old text is gone, new text is present, line count unchanged**

```bash
# Old text should be gone
grep -n 'alongside' profile-al-dev-shared/agents/al-dev-code-review.md || echo "Removed"

# New text should be present
grep -n 'standalone manual use only' profile-al-dev-shared/agents/al-dev-code-review.md

# Line count — should be 160 (same as before; description is 5 lines → 5 lines)
wc -l profile-al-dev-shared/agents/al-dev-code-review.md
```

Expected: "Removed"; grep finds the new description line; wc -l shows 160.

- [ ] **Step 4: Verify — forbidden patterns and git status**

```bash
grep -E '\[date\]|YYYY-MM-DD|TODO|TBD|Co-Authored-By|claude:|copilot:' \
  profile-al-dev-shared/agents/al-dev-code-review.md || echo "Clean"

git status --short
```

Expected: "Clean"; `git status` shows `M profile-al-dev-shared/agents/al-dev-code-review.md`.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-code-review.md
git commit -m "docs(agents): fix al-dev-code-review description — standalone-only

WHY: Old description said 'as part of the 3-specialist review team' but
no skill spawns this agent — a developer reading it would assume it was
already wired into /al-dev-develop. New wording makes standalone-only
status explicit.

CHANGED COMPONENTS
- al-dev-code-review.md [m]"
```

---

## Task 4: Mark All Five Suggestions as Implemented in Agent Map

**Files:**
- Modify: `docs/al-dev-agent-map.md` Observations section (lines ~482–506)

- [ ] **Step 1: Confirm all five suggestion headers are present and unmarked**

```bash
grep -n '^\*\*Trim:\|^\*\*Remodel:\|^\*\*Align:' docs/al-dev-agent-map.md
```

Expected — 5 lines, none ending in `← implemented`:
```
482:**Trim: al-dev-commit-agent-analysis**
487:**Trim: al-dev-commit-agent-execute**
492:**Trim: al-dev-release-notes-agent**
497:**Remodel: al-dev-explore**
502:**Align: al-dev-code-review**
```

(Line numbers are approximate — confirm from the grep output before editing.)

- [ ] **Step 2: Mark Trim — al-dev-commit-agent-analysis as implemented**

Use the Edit tool with this exact replacement:

```
old_string: **Trim: al-dev-commit-agent-analysis**
new_string: **Trim: al-dev-commit-agent-analysis** ← implemented
```

File: `docs/al-dev-agent-map.md`

- [ ] **Step 3: Mark Trim — al-dev-commit-agent-execute as implemented**

Use the Edit tool with this exact replacement:

```
old_string: **Trim: al-dev-commit-agent-execute**
new_string: **Trim: al-dev-commit-agent-execute** ← implemented
```

File: `docs/al-dev-agent-map.md`

- [ ] **Step 4: Mark Trim — al-dev-release-notes-agent as implemented**

Use the Edit tool with this exact replacement:

```
old_string: **Trim: al-dev-release-notes-agent**
new_string: **Trim: al-dev-release-notes-agent** ← implemented
```

File: `docs/al-dev-agent-map.md`

- [ ] **Step 5: Mark Remodel — al-dev-explore as implemented**

Use the Edit tool with this exact replacement:

```
old_string: **Remodel: al-dev-explore**
new_string: **Remodel: al-dev-explore** ← implemented
```

File: `docs/al-dev-agent-map.md`

- [ ] **Step 6: Mark Align — al-dev-code-review as implemented**

Use the Edit tool with this exact replacement:

```
old_string: **Align: al-dev-code-review**
new_string: **Align: al-dev-code-review** ← implemented
```

File: `docs/al-dev-agent-map.md`

- [ ] **Step 7: Verify — all five are marked**

```bash
grep -n '← implemented' docs/al-dev-agent-map.md | grep -E 'Trim|Remodel|Align'
```

Expected — exactly 5 lines:
```
NNN:**Trim: al-dev-commit-agent-analysis** ← implemented
NNN:**Trim: al-dev-commit-agent-execute** ← implemented
NNN:**Trim: al-dev-release-notes-agent** ← implemented
NNN:**Remodel: al-dev-explore** ← implemented
NNN:**Align: al-dev-code-review** ← implemented
```

- [ ] **Step 8: Verify — forbidden patterns and git status**

```bash
grep -E '\[date\]|YYYY-MM-DD|TODO|TBD|Co-Authored-By|claude:|copilot:' \
  docs/al-dev-agent-map.md || echo "Clean"

git status --short
```

Expected: "Clean"; `git status` shows only `M docs/al-dev-agent-map.md`.

- [ ] **Step 9: Commit**

```bash
git add docs/al-dev-agent-map.md
git commit -m "docs(agent-map): mark 5 quality suggestions as implemented

WHY: Trim ×3, Remodel ×1, and Align ×1 suggestions from the 2026-05-19
analyze-agent-design run are now applied — recording their completion so
the next review cycle starts from a clean baseline.

CHANGED COMPONENTS
- al-dev-agent-map.md [m]"
```
