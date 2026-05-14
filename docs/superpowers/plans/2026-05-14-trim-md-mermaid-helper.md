# Trim md-mermaid-helper.md Context Cost — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the `applyTo` auto-load frontmatter from `md-mermaid-helper.md` and add
explicit discoverability references so agents still load the file when writing diagrams —
saving ~800 tokens in every non-diagram session.

**Architecture:** Option C from the spec — pure on-demand loading. The 4-line frontmatter
block is deleted, a "Diagram Guidance" section is added to both `CLAUDE.md` and `AGENTS.md`,
and the one agent that relied on auto-load (`al-dev-release-notes-agent.md`) is updated to
read the file explicitly. Three agents already carry explicit load instructions
(`al-dev-docs-writer.md`, `al-dev-solution-architect.md`, `al-dev-support-agent.md`) and
require no changes.

**Tech Stack:** Markdown file edits only — no code, no scripts.

---

## File Map

| File | Change |
| --- | --- |
| `profile-al-dev-shared/markdown/md-mermaid-helper.md` | Remove `applyTo` frontmatter (lines 1–4) |
| `CLAUDE.md` | Add `## Diagram Guidance` section with discoverability reference |
| `AGENTS.md` | Add `## Diagram Guidance` section with discoverability reference |
| `profile-al-dev-shared/agents/al-dev-release-notes-agent.md` | Replace implicit session-context note with explicit read instruction |

**Files NOT changed** (already carry explicit load instructions from prior enforcement work):
- `profile-al-dev-shared/agents/al-dev-docs-writer.md`
- `profile-al-dev-shared/agents/al-dev-solution-architect.md`
- `profile-al-dev-shared/agents/al-dev-support-agent.md`

---

### Task 1: Remove auto-load frontmatter from md-mermaid-helper.md

**Files:**
- Modify: `profile-al-dev-shared/markdown/md-mermaid-helper.md:1-4`

- [ ] **Step 1: Verify current line count and frontmatter**

```bash
wc -l profile-al-dev-shared/markdown/md-mermaid-helper.md
head -5 profile-al-dev-shared/markdown/md-mermaid-helper.md
```

Expected output:
```
84 profile-al-dev-shared/markdown/md-mermaid-helper.md
---
applyTo: "**/*.{md,mmd}"
---

# Mermaid Diagram Rules
```

- [ ] **Step 2: Remove the frontmatter block**

Use the Edit tool with this exact replacement:

old_string:
```
---
applyTo: "**/*.{md,mmd}"
---

# Mermaid Diagram Rules
```

new_string:
```
# Mermaid Diagram Rules
```

- [ ] **Step 3: Verify the edit — line count drops by 4, no applyTo remains**

```bash
wc -l profile-al-dev-shared/markdown/md-mermaid-helper.md
grep 'applyTo' profile-al-dev-shared/markdown/md-mermaid-helper.md
head -3 profile-al-dev-shared/markdown/md-mermaid-helper.md
```

Expected:
```
80 profile-al-dev-shared/markdown/md-mermaid-helper.md
(no grep output)
# Mermaid Diagram Rules

1. No HTML tags in node labels. Plain text or quoted labels only.
```

- [ ] **Step 4: Confirm Mermaid diagrams live in .md files, not standalone .mmd**

```bash
grep -rl '```mermaid' profile-al-dev-shared/
find profile-al-dev-shared/ -name '*.mmd'
```

Expected: `grep` returns one or more `.md` paths; `find` returns no output.
This confirms Option A (narrow to `*.mmd`) would have missed all actual usage.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/markdown/md-mermaid-helper.md
git commit -m "$(cat <<'EOF'
⚡ perf(markdown): remove auto-load applyTo from md-mermaid-helper

Converts to pure on-demand knowledge doc (Option C from spec). Saves
~800 tokens per session when no Mermaid diagrams are written. Agents
that produce diagrams load it explicitly instead.
EOF
)"
```

---

### Task 2: Add discoverability references to CLAUDE.md and AGENTS.md

**Files:**
- Modify: `CLAUDE.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Add Diagram Guidance section to CLAUDE.md**

Read `CLAUDE.md`. Then use the Edit tool with this replacement:

old_string:
```
## Commit Conventions

project-type: tool
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md

---
```

new_string:
```
## Commit Conventions

project-type: tool
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md

## Diagram Guidance

When writing Mermaid diagrams, read
`profile-al-dev-shared/markdown/md-mermaid-helper.md` before generating
any diagram blocks.

---
```

- [ ] **Step 2: Verify CLAUDE.md addition**

```bash
grep -A4 'Diagram Guidance' CLAUDE.md
```

Expected:
```
## Diagram Guidance

When writing Mermaid diagrams, read
`profile-al-dev-shared/markdown/md-mermaid-helper.md` before generating
any diagram blocks.
```

- [ ] **Step 3: Add Diagram Guidance section to AGENTS.md**

Read `AGENTS.md`. Then use the Edit tool with this replacement:

old_string:
```
- Use `git -C <path>` instead of `cd <path> && git`

---

## Harness Mapping
```

new_string:
```
- Use `git -C <path>` instead of `cd <path> && git`

## Diagram Guidance

When writing Mermaid diagrams, read
`profile-al-dev-shared/markdown/md-mermaid-helper.md` before generating
any diagram blocks.

---

## Harness Mapping
```

- [ ] **Step 4: Verify AGENTS.md addition**

```bash
grep -A4 'Diagram Guidance' AGENTS.md
```

Expected:
```
## Diagram Guidance

When writing Mermaid diagrams, read
`profile-al-dev-shared/markdown/md-mermaid-helper.md` before generating
any diagram blocks.
```

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md AGENTS.md
git commit -m "$(cat <<'EOF'
📝 docs(plugin): add Diagram Guidance discoverability reference

Points to md-mermaid-helper.md in both CLAUDE.md and AGENTS.md so
Claude Code and Copilot CLI agents know where to find Mermaid rules
now that the file no longer auto-loads.
EOF
)"
```

---

### Task 3: Update al-dev-release-notes-agent.md with explicit load instruction

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-release-notes-agent.md:114-116`

Context: Lines 114–116 currently say "Follow the global Mermaid style guide
(in session context)" — this relied on the `applyTo` auto-injection that no longer
fires. Replace with an explicit read instruction matching the pattern used by the
other three diagram-producing agents.

- [ ] **Step 1: Read the identify-diagrams section to confirm exact current text**

Read `profile-al-dev-shared/agents/al-dev-release-notes-agent.md` lines 110–120.

Expected lines 114–116:
```
Follow the global Mermaid style guide (in session context):
`flowchart TD` for processes, `sequenceDiagram` for system
interactions. Subdued fills from the standard palette.
```

- [ ] **Step 2: Replace implicit reference with explicit read instruction**

Use the Edit tool with this replacement:

old_string:
```
Follow the global Mermaid style guide (in session context):
`flowchart TD` for processes, `sequenceDiagram` for system
interactions. Subdued fills from the standard palette.
```

new_string:
```
Before writing any Mermaid diagram, read
`$AL_DEV_SHARED_PLUGIN_ROOT/markdown/md-mermaid-helper.md`
and apply all rules from it. Use `flowchart TD` for processes,
`sequenceDiagram` for system interactions.
```

- [ ] **Step 3: Verify the change**

```bash
grep -n 'in session context' profile-al-dev-shared/agents/al-dev-release-notes-agent.md
grep -A3 'Before writing any Mermaid diagram' profile-al-dev-shared/agents/al-dev-release-notes-agent.md
```

Expected:
- First command: no output (old text gone)
- Second command:
  ```
  Before writing any Mermaid diagram, read
  `$AL_DEV_SHARED_PLUGIN_ROOT/markdown/md-mermaid-helper.md`
  and apply all rules from it. Use `flowchart TD` for processes,
  ```

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-release-notes-agent.md
git commit -m "$(cat <<'EOF'
📝 docs(agents): explicit mermaid helper load in release-notes agent

Replaces implicit auto-load reference with explicit read instruction,
matching the pattern already used in docs-writer, solution-architect,
and support agents.
EOF
)"
```

---

### Task 4: Final verification

- [ ] **Step 1: Confirm no remaining agent relies on session-context auto-load**

```bash
grep -rn 'in session context' profile-al-dev-shared/agents/ profile-al-dev-shared/skills/
grep 'applyTo' profile-al-dev-shared/markdown/md-mermaid-helper.md
```

Expected: both commands return no output.

- [ ] **Step 2: Confirm all four diagram-writing agents have explicit load instructions**

```bash
grep -rn 'md-mermaid-helper' profile-al-dev-shared/agents/
```

Expected: exactly four matches across these files:
- `al-dev-docs-writer.md`
- `al-dev-solution-architect.md`
- `al-dev-support-agent.md`
- `al-dev-release-notes-agent.md`

- [ ] **Step 3: Confirm discoverability references are in both project instruction files**

```bash
grep -l 'md-mermaid-helper' CLAUDE.md AGENTS.md
```

Expected: both filenames printed.

- [ ] **Step 4: Confirm total commit count for this feature**

```bash
git log --oneline -5
```

Expected: three commits at the top matching the messages from Tasks 1, 2, and 3.
