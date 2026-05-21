# Claude Code Profile Aliases Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable context-aware plugin loading via shell aliases, reducing session context load for non-AL projects.

**Architecture:** Create three profile files in `~/.claude/profiles/` with context-specific plugin enablement, remove `enabledPlugins` from global settings, and add shell aliases for quick profile switching.

**Tech Stack:** Claude Code settings.json configuration files, zsh shell aliases.

---

## File Structure

```
~/.claude/
  settings.json                    (modify: remove enabledPlugins key)
  profiles/                        (create directory)
    al.json                        (create: AL development profile)
    code.json                      (create: general code profile)
    obsidian.json                  (create: vault/Obsidian profile)
~/.zshrc                           (modify: add three aliases, update existing cc alias)
```

---

## Task 1: Create profiles directory

- [ ] **Step 1: Create ~/.claude/profiles/ directory**

Run:
```bash
mkdir -p ~/.claude/profiles
```

- [ ] **Step 2: Verify directory exists**

Run:
```bash
ls -ld ~/.claude/profiles
```

Expected: Directory exists with 755 permissions (or similar).

---

## Task 2: Create al.json profile (AL development)

- [ ] **Step 1: Write al.json with AL-specific plugins**

Create file: `~/.claude/profiles/al.json`

```json
{
  "enabledPlugins": [
    "al-dev-shared@al-dev-shared",
    "profile-claude-al-dev@stefan-maron",
    "context7@claude-plugins-official",
    "pyright-lsp@claude-plugins-official",
    "skill-creator@claude-plugins-official"
  ]
}
```

- [ ] **Step 2: Verify file is valid JSON**

Run:
```bash
jq empty ~/.claude/profiles/al.json && echo "Valid JSON"
```

Expected: Outputs "Valid JSON" with no errors.

---

## Task 3: Create code.json profile (general code)

- [ ] **Step 1: Write code.json with general-purpose plugins**

Create file: `~/.claude/profiles/code.json`

```json
{
  "enabledPlugins": [
    "context7@claude-plugins-official",
    "pyright-lsp@claude-plugins-official",
    "skill-creator@claude-plugins-official"
  ]
}
```

- [ ] **Step 2: Verify file is valid JSON**

Run:
```bash
jq empty ~/.claude/profiles/code.json && echo "Valid JSON"
```

Expected: Outputs "Valid JSON" with no errors.

---

## Task 4: Create obsidian.json profile (vault/Obsidian)

- [ ] **Step 1: Write obsidian.json with vault-specific plugins**

Create file: `~/.claude/profiles/obsidian.json`

```json
{
  "enabledPlugins": [
    "context7@claude-plugins-official",
    "profile-vault-shared@vault-shared"
  ]
}
```

- [ ] **Step 2: Verify file is valid JSON**

Run:
```bash
jq empty ~/.claude/profiles/obsidian.json && echo "Valid JSON"
```

Expected: Outputs "Valid JSON" with no errors.

---

## Task 5: Remove enabledPlugins from global settings.json

- [ ] **Step 1: Read current settings.json**

Run:
```bash
cat ~/.claude/settings.json
```

Note the current `enabledPlugins` array (for reference if needed).

- [ ] **Step 2: Remove enabledPlugins key**

Run:
```bash
jq 'del(.enabledPlugins)' ~/.claude/settings.json > ~/.claude/settings.json.tmp && mv ~/.claude/settings.json.tmp ~/.claude/settings.json
```

- [ ] **Step 3: Verify enabledPlugins is removed**

Run:
```bash
jq 'has("enabledPlugins")' ~/.claude/settings.json
```

Expected: Outputs `false`.

- [ ] **Step 4: Verify other keys are intact**

Run:
```bash
jq 'keys | length' ~/.claude/settings.json
```

Expected: Outputs a number > 0 (should show other keys like env, hooks, statusLine, etc. remain).

---

## Task 6: Add shell aliases to ~/.zshrc

- [ ] **Step 1: Read current ~/.zshrc**

Run:
```bash
cat ~/.zshrc | grep -A2 "alias claude"
```

Note: Check if existing `cc` alias exists and its current definition.

- [ ] **Step 2: Back up ~/.zshrc**

Run:
```bash
cp ~/.zshrc ~/.zshrc.backup
```

- [ ] **Step 3: Remove or update existing cc alias if present**

If the output from Step 1 shows an existing `cc` alias:

Run:
```bash
grep -n "alias cc=" ~/.zshrc
```

If found, remove that line. Otherwise, proceed to Step 4.

- [ ] **Step 4: Add the three new aliases to ~/.zshrc**

Append to `~/.zshrc`:

```bash
# Claude Code profile aliases (2026-05-21)
alias claude='claude --settings ~/.claude/profiles/al.json'        # AL development
alias claudec='claude --settings ~/.claude/profiles/code.json'     # general code
alias claudev='claude --settings ~/.claude/profiles/obsidian.json' # vault/Obsidian
```

- [ ] **Step 5: Verify aliases are in the file**

Run:
```bash
grep "alias claude" ~/.zshrc | tail -3
```

Expected: Shows three lines with `claude=`, `claudec=`, `claudev=` aliases.

- [ ] **Step 6: Reload shell to activate aliases**

Run:
```bash
exec zsh
```

---

## Task 7: Verify aliases work correctly

- [ ] **Step 1: Test AL profile alias (claude)**

Run:
```bash
type claude
```

Expected: Shows `claude is aliased to 'claude --settings ~/.claude/profiles/al.json'`.

- [ ] **Step 2: Test general code alias (claudec)**

Run:
```bash
type claudec
```

Expected: Shows `claudec is aliased to 'claude --settings ~/.claude/profiles/code.json'`.

- [ ] **Step 3: Test vault alias (claudev)**

Run:
```bash
type claudev
```

Expected: Shows `claudev is aliased to 'claude --settings ~/.claude/profiles/obsidian.json'`.

- [ ] **Step 4: Verify profile files are readable**

Run:
```bash
for f in ~/.claude/profiles/*.json; do jq empty "$f" && echo "✓ $f"; done
```

Expected: Shows three ✓ marks for al.json, code.json, obsidian.json.

---

## Task 8: Smoke-test plugins in each profile

- [ ] **Step 1: Start a session with AL profile and verify plugins load**

Run:
```bash
claude help superpowers
```

(Or any AL-specific skill like `/al-dev-plan`)

Expected: AL-specific skills (al-dev-shared, profile-claude-al-dev) are available; vault skills are NOT available.

- [ ] **Step 2: Start a session with code profile and verify plugins load**

Run:
```bash
claudec help superpowers
```

Expected: General plugins (context7, pyright-lsp, skill-creator) are available; AL-specific and vault plugins are NOT available.

- [ ] **Step 3: Start a session with vault profile and verify plugins load**

Run:
```bash
claudev help obsidian
```

(Or reference the vault plugin)

Expected: Vault plugin (profile-vault-shared) and context7 are available; AL-specific plugins are NOT available.

---

## Self-Review Checklist

✓ **Spec coverage:** 
- File layout created as specified (profiles/ directory, three JSON files)
- enabledPlugins removed from global settings.json
- Aliases added to ~/.zshrc matching spec (claude, claudec, claudev)
- Each alias points to correct profile file
- Existing "cc" alias handling documented and handled
- Smoke tests verify correct plugins per profile

✓ **Placeholder scan:** No "TBD", "TODO", or incomplete steps. All code blocks include actual content.

✓ **Type consistency:** Profile file structures consistent across all three files. All JSON valid and follows Claude Code settings format.

✓ **Complete instructions:** Every step includes exact commands, expected output, and file paths.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-21-claude-profile-aliases.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
