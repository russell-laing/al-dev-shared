# Commit Conventions Adoption Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adopt `commit-conventions.md` as the single authoritative commit spec across all projects by removing duplicate/conflicting inline rules and adding a `project-type` declaration to each project's CLAUDE.md.

**Architecture:** Nine targeted file edits — one per project. Each edit follows the three-step adoption checklist in `commit-conventions.md`: scan for existing instructions, remove duplicates/conflicts, add project-type declaration. No new files created.

**Tech Stack:** Bash (grep for verification), Edit tool for precise string replacement.

---

## File Map

| File | Action | Reason |
| --- | --- | --- |
| `al-dev-shared/CLAUDE.md:66-71` | Replace inline rules with project-type declaration | Exact duplicate of spec |
| `copilot-configs/.github/copilot-instructions.md:182-199` | Remove "Commit Message Format" section; add canonical reference | Conflicting table (`🔧` for `chore` vs spec's `📦`) |
| `al-smart-compile/CLAUDE.md` | Append project-type: tool | No existing commit section |
| `claude-configs/CLAUDE.md` | Append project-type: tool | No existing commit section |
| `nzpg/CLAUDE.md` | Append project-type: vault | No existing commit section |
| `mml/CLAUDE.md` | Append project-type: vault | No existing commit section |
| `second-brain/CLAUDE.md` | Append project-type: vault | No existing commit section |
| `client-abc/CLAUDE.md` | Append project-type: vault | No existing commit section |
| `~/.claude/CLAUDE.md:9-14` | Remove 3 duplicate bullets; keep git -C convention; add spec reference | Duplicate of spec |

---

## Task 1: al-dev-shared — Replace inline commit rules

**Files:**
- Modify: `/Users/russelllaing/al-dev-shared/CLAUDE.md:66-72`

The existing section duplicates spec rules verbatim. The `git -C` line is already in the global CLAUDE.md. Replace all four bullets with a project-type pointer.

- [ ] **Step 1: Read the current section to confirm exact content**

```bash
grep -n "Commit Conventions" /Users/russelllaing/al-dev-shared/CLAUDE.md
```

Expected output: `66:## Commit Conventions`

- [ ] **Step 2: Apply the edit**

Use the Edit tool with this exact replacement:

Old string:
```
## Commit Conventions

- Gitmoji prefix on every commit (check `git log` for current style)
- Freshdesk tickets as `#FD<number>` in the message body
- No `Co-Authored-By` trailers
- Use `git -C <path>` instead of `cd <path> && git`
```

New string:
```
## Commit Conventions

project-type: tool
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 3: Verify the edit**

```bash
grep -A 3 "## Commit Conventions" /Users/russelllaing/al-dev-shared/CLAUDE.md
```

Expected:
```
## Commit Conventions

project-type: tool
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

Also confirm the old bullets are gone:
```bash
grep "Gitmoji prefix\|Co-Authored\|#FD" /Users/russelllaing/al-dev-shared/CLAUDE.md
```

Expected: no output.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add CLAUDE.md
git -C /Users/russelllaing/al-dev-shared commit -m "📝 docs(claude): adopt commit-conventions spec, remove inline duplicates"
```

---

## Task 2: copilot-configs — Remove conflicting commit format section

**Files:**
- Modify: `/Users/russelllaing/copilot-configs/.github/copilot-instructions.md:182-199`

The existing `## Commit Message Format` section has a 5-type table that uses `🔧` for `chore` — this conflicts with the spec's `📦 chore`. The scope rule on line 198 is project-specific and must be kept. Replace the whole section with a canonical reference that preserves the scope rule.

- [ ] **Step 1: Read lines 180–202 to confirm exact content**

```bash
grep -n "Commit Message Format\|The scope is" /Users/russelllaing/copilot-configs/.github/copilot-instructions.md
```

Expected: `182:## Commit Message Format` and `198:The scope is the plugin name...`

- [ ] **Step 2: Apply the edit**

Use the Edit tool with this exact replacement:

Old string:
```
## Commit Message Format

Every commit must start with a gitmoji, followed by the conventional-commit type:

```text
<emoji> <type>(<scope>): <description>
```

| Type | Emoji | Example |
|------|-------|---------|
| `feat` | ✨ | `✨ feat(copilot-al-dev): add cross-repo sessions rule` |
| `fix` | 🐛 | `🐛 fix(copilot-al-dev): tighten checkpoint wording` |
| `chore` | 🔧 | `🔧 chore(copilot-al-dev): bump version 2.2.0 → 2.2.1` |
| `docs` | 📝 | `📝 docs(copilot-al-dev): update AGENTS.md orchestration notes` |
| `refactor` | ♻️ | `♻️ refactor(copilot-vault): simplify handoff agent prompt` |

The scope is the plugin name (`copilot-al-dev`, `copilot-vault`) or `marketplace` for cross-plugin changes.
```

New string:
```
## Commit Conventions

Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
project-type: tool

**Scope:** Plugin name (`copilot-al-dev`, `copilot-vault`) or `marketplace` for cross-plugin changes.
```

- [ ] **Step 3: Verify the edit**

```bash
grep -A 5 "## Commit Conventions" /Users/russelllaing/copilot-configs/.github/copilot-instructions.md
```

Expected:
```
## Commit Conventions

Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
project-type: tool

**Scope:** Plugin name (`copilot-al-dev`, `copilot-vault`) or `marketplace` for cross-plugin changes.
```

Confirm the conflicting table is gone:
```bash
grep "chore.*🔧\|🔧.*chore" /Users/russelllaing/copilot-configs/.github/copilot-instructions.md
```

Expected: no output.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/copilot-configs add .github/copilot-instructions.md
git -C /Users/russelllaing/copilot-configs commit -m "📝 docs(copilot-al-dev): replace conflicting commit format with canonical spec reference"
```

---

## Task 3: al-smart-compile — Add project-type declaration

**Files:**
- Modify: `/Users/russelllaing/al-smart-compile/CLAUDE.md`

No existing commit section. Append after the last line of the file.

- [ ] **Step 1: Confirm no existing commit section**

```bash
grep -n "Commit\|gitmoji\|emoji" /Users/russelllaing/al-smart-compile/CLAUDE.md
```

Expected: no output (or only unrelated matches).

- [ ] **Step 2: Find the last line number**

```bash
grep -c "" /Users/russelllaing/al-smart-compile/CLAUDE.md
```

Note the line count. The file ends at line 186 with `Both scripts have complete feature parity and automatically detect the correct platform and compiler to use.`

- [ ] **Step 3: Apply the edit**

Use the Edit tool with this exact replacement on the last line:

Old string:
```
Both scripts have complete feature parity and automatically detect the correct platform and compiler to use.
```

New string:
```
Both scripts have complete feature parity and automatically detect the correct platform and compiler to use.

## Commit Conventions

project-type: tool
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 4: Verify the edit**

```bash
grep -A 3 "## Commit Conventions" /Users/russelllaing/al-smart-compile/CLAUDE.md
```

Expected:
```
## Commit Conventions

project-type: tool
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-smart-compile add CLAUDE.md
git -C /Users/russelllaing/al-smart-compile commit -m "📝 docs(claude): add commit-conventions project-type declaration"
```

---

## Task 4: claude-configs — Add project-type declaration

**Files:**
- Modify: `/Users/russelllaing/claude-configs/CLAUDE.md`

No existing commit format section — only a `## Git Workflow` section with generic git commands. Add `## Commit Conventions` after the Security section (the last section, at the end of the file).

- [ ] **Step 1: Confirm no existing commit format section**

```bash
grep -n "## Commit\|gitmoji\|project-type" /Users/russelllaing/claude-configs/CLAUDE.md
```

Expected: no output.

- [ ] **Step 2: Apply the edit**

Use the Edit tool with this exact replacement on the last line of the file:

Old string:
```
- Store auth in project-local `.env` files (gitignored)
```

New string:
```
- Store auth in project-local `.env` files (gitignored)

## Commit Conventions

project-type: tool
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 3: Verify the edit**

```bash
grep -A 3 "## Commit Conventions" /Users/russelllaing/claude-configs/CLAUDE.md
```

Expected:
```
## Commit Conventions

project-type: tool
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/claude-configs add CLAUDE.md
git -C /Users/russelllaing/claude-configs commit -m "📝 docs(claude): add commit-conventions project-type declaration"
```

---

## Task 5: nzpg — Add project-type: vault

**Files:**
- Modify: `/Users/russelllaing/nzpg/CLAUDE.md`

The file is 3 lines. No existing commit section. Append after existing content.

- [ ] **Step 1: Confirm file content**

```bash
grep -c "" /Users/russelllaing/nzpg/CLAUDE.md
```

Expected: 3

- [ ] **Step 2: Apply the edit**

Use the Edit tool with this exact replacement:

Old string:
```
Before responding to any request in this vault, read
`client-protocol.md` from the vault root and apply all
rules within it.
```

New string:
```
Before responding to any request in this vault, read
`client-protocol.md` from the vault root and apply all
rules within it.

## Commit Conventions

project-type: vault
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 3: Verify the edit**

```bash
grep -A 3 "## Commit Conventions" /Users/russelllaing/nzpg/CLAUDE.md
```

Expected:
```
## Commit Conventions

project-type: vault
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/nzpg add CLAUDE.md
git -C /Users/russelllaing/nzpg commit -m "📝 docs(claude): add commit-conventions project-type declaration"
```

---

## Task 6: mml — Add project-type: vault

**Files:**
- Modify: `/Users/russelllaing/mml/CLAUDE.md`

Identical starting content to nzpg. Same append pattern.

- [ ] **Step 1: Confirm file content**

```bash
grep -c "" /Users/russelllaing/mml/CLAUDE.md
```

Expected: 3

- [ ] **Step 2: Apply the edit**

Use the Edit tool with this exact replacement:

Old string:
```
Before responding to any request in this vault, read
`client-protocol.md` from the vault root and apply all
rules within it.
```

New string:
```
Before responding to any request in this vault, read
`client-protocol.md` from the vault root and apply all
rules within it.

## Commit Conventions

project-type: vault
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 3: Verify the edit**

```bash
grep -A 3 "## Commit Conventions" /Users/russelllaing/mml/CLAUDE.md
```

Expected:
```
## Commit Conventions

project-type: vault
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/mml add CLAUDE.md
git -C /Users/russelllaing/mml commit -m "📝 docs(claude): add commit-conventions project-type declaration"
```

---

## Task 7: second-brain — Add project-type: vault

**Files:**
- Modify: `/Users/russelllaing/second-brain/CLAUDE.md`

16-line file ending with a Tool Mappings table. Append after the last row.

- [ ] **Step 1: Confirm no existing commit section**

```bash
grep -n "Commit\|gitmoji\|project-type" /Users/russelllaing/second-brain/CLAUDE.md
```

Expected: no output.

- [ ] **Step 2: Apply the edit**

Use the Edit tool with this exact replacement on the last line:

Old string:
```
| List files in a folder | `Bash` with `find` |
```

New string:
```
| List files in a folder | `Bash` with `find` |

## Commit Conventions

project-type: vault
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 3: Verify the edit**

```bash
grep -A 3 "## Commit Conventions" /Users/russelllaing/second-brain/CLAUDE.md
```

Expected:
```
## Commit Conventions

project-type: vault
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/second-brain add CLAUDE.md
git -C /Users/russelllaing/second-brain commit -m "📝 docs(claude): add commit-conventions project-type declaration"
```

---

## Task 8: client-abc — Add project-type: vault

**Files:**
- Modify: `/Users/russelllaing/client-abc/CLAUDE.md`

16-line file ending with a Tool Mappings table. Append after the last row.

- [ ] **Step 1: Confirm no existing commit section**

```bash
grep -n "Commit\|gitmoji\|project-type" /Users/russelllaing/client-abc/CLAUDE.md
```

Expected: no output (the client-protocol.md has one generic git example but that's in a different file).

- [ ] **Step 2: Apply the edit**

Use the Edit tool with this exact replacement on the last line:

Old string:
```
| Edit frontmatter | `Edit` tool |
| Create a new file | `Write` tool |
| List files | `Bash` with `find` |
```

New string:
```
| Edit frontmatter | `Edit` tool |
| Create a new file | `Write` tool |
| List files | `Bash` with `find` |

## Commit Conventions

project-type: vault
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 3: Verify the edit**

```bash
grep -A 3 "## Commit Conventions" /Users/russelllaing/client-abc/CLAUDE.md
```

Expected:
```
## Commit Conventions

project-type: vault
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md
```

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/client-abc add CLAUDE.md
git -C /Users/russelllaing/client-abc commit -m "📝 docs(claude): add commit-conventions project-type declaration"
```

---

## Task 9: Global CLAUDE.md — Slim to spec reference

**Files:**
- Modify: `/Users/russelllaing/.claude/CLAUDE.md:9-14`

The current section has three bullets that are exact duplicates of the spec. Remove them. Keep the `git -C` convention (tool hint not in the spec). Add a spec reference.

- [ ] **Step 1: Read current section**

```bash
grep -A 5 "## Git Commit Conventions" /Users/russelllaing/.claude/CLAUDE.md
```

Expected:
```
## Git Commit Conventions

- Use Gitmoji prefix on every commit (check `git log` for examples before committing)
- Reference Freshdesk tickets as `#FD<number>` (e.g., `#FD42273`), NOT `Ref: FD #42273`
- Do NOT include `Co-Authored-By` lines in commit messages
- Always use `git -C <path>` instead of `cd <path> && git ...` to avoid approval prompts
```

- [ ] **Step 2: Apply the edit**

Use the Edit tool with this exact replacement:

Old string:
```
## Git Commit Conventions

- Use Gitmoji prefix on every commit (check `git log` for examples before committing)
- Reference Freshdesk tickets as `#FD<number>` (e.g., `#FD42273`), NOT `Ref: FD #42273`
- Do NOT include `Co-Authored-By` lines in commit messages
- Always use `git -C <path>` instead of `cd <path> && git ...` to avoid approval prompts
```

New string:
```
## Git Commit Conventions

Full spec: profile-al-dev-shared/knowledge/commit-conventions.md

- Always use `git -C <path>` instead of `cd <path> && git ...` to avoid approval prompts
```

- [ ] **Step 3: Verify the edit**

```bash
grep -A 4 "## Git Commit Conventions" /Users/russelllaing/.claude/CLAUDE.md
```

Expected:
```
## Git Commit Conventions

Full spec: profile-al-dev-shared/knowledge/commit-conventions.md

- Always use `git -C <path>` instead of `cd <path> && git ...` to avoid approval prompts
```

Confirm the duplicate bullets are gone:
```bash
grep "Gitmoji prefix\|Co-Authored\|FD.*42273" /Users/russelllaing/.claude/CLAUDE.md
```

Expected: no output.

- [ ] **Step 4: Note — global CLAUDE.md is not in a git repo**

`~/.claude/CLAUDE.md` is not tracked by git. No commit needed. The edit is live immediately.

---

## Self-Review

### Spec coverage

| Spec requirement | Covered by task |
| --- | --- |
| Scan for existing commit instructions | Each task Step 1 grep confirms current state |
| Remove duplicates and conflicts | Task 1 (al-dev-shared), Task 2 (copilot-configs), Task 9 (global) |
| Add project-type declaration | Tasks 1–8 |
| Keep project-specific scope rules | Task 2 preserves the plugin scope line |
| Keep non-duplicate rules | Tasks 1 and 9 preserve `git -C` convention (tool hint not in spec) |

### Placeholder scan

No TBDs or TODOs. Every step shows exact old_string/new_string content or exact commands.

### Type consistency

All `project-type` values are from the spec's allowed set: `al`, `vault`, `tool`.
All `Full spec:` paths use the canonical value: `profile-al-dev-shared/knowledge/commit-conventions.md`.
