# Claude Code Profile Aliases Design

**Date:** 2026-05-21
**Status:** Approved

## Problem

All plugins load in every Claude Code session regardless of project type. AL-specific plugins (al-dev-shared, profile-claude-al-dev) consume context budget in non-AL projects; the vault plugin is never loaded because it sits dormant with no activation path.

## Goal

Reduce context load per session by activating only the plugins relevant to the current work context. Use shell aliases so switching is a one-word decision at session start.

## Mechanism

Claude Code's `--settings <file>` flag merges additional settings on top of the global `~/.claude/settings.json`. Profile files contain only `enabledPlugins`; all other global settings (env vars, hooks, statusLine, extraKnownMarketplaces) remain in the global file and are inherited automatically.

## File Layout

```
~/.claude/
  settings.json               ← env vars, hooks, statusLine, extraKnownMarketplaces, model
                                 enabledPlugins removed entirely
  profiles/
    al.json                   ← AL development profile
    code.json                 ← general code profile
    obsidian.json             ← vault/Obsidian profile
```

## Plugin Assignments

| Plugin | al.json | code.json | obsidian.json |
|---|---|---|---|
| `al-dev-shared@al-dev-shared` | ✓ | — | — |
| `profile-claude-al-dev@stefan-maron` | ✓ | — | — |
| `context7@claude-plugins-official` | ✓ | ✓ | ✓ |
| `pyright-lsp@claude-plugins-official` | ✓ | ✓ | — |
| `skill-creator@claude-plugins-official` | ✓ | ✓ | — |
| `profile-vault-shared@vault-shared` | — | — | ✓ |

**Rationale:**
- `al-dev-shared` + `profile-claude-al-dev`: AL-specific, not useful outside BC projects
- `context7`: useful for any code or documentation lookup; included in obsidian for library reference when writing technical notes
- `pyright-lsp`: Python linting, relevant in coding contexts only
- `skill-creator`: generic skill creation tool, relevant wherever skills are authored (AL and general code); not needed in vault sessions
- `profile-vault-shared`: vault-specific; currently dormant in global settings

## Shell Aliases

```bash
# ~/.zshrc
alias claude='claude --settings ~/.claude/profiles/al.json'        # AL default
alias claudec='claude --settings ~/.claude/profiles/code.json'     # general code
alias claudev='claude --settings ~/.claude/profiles/obsidian.json' # vault/Obsidian
```

`claude` retains AL as the default (majority use case). `claudec` and `claudev` are short, distinct, and low-typo-risk.

## Implementation Steps

1. Create `~/.claude/profiles/` directory
2. Write `al.json`, `code.json`, `obsidian.json` profile files
3. Strip `enabledPlugins` from `~/.claude/settings.json`
4. Add aliases to `~/.zshrc` and reload shell
5. Smoke-test each alias: verify correct skills appear in session start

## Out of Scope

- Automatic project-type detection (kept manual; aliases are intentional)
- Per-project `.claude/settings.json` overrides (unaffected; still work on top of the active profile)
