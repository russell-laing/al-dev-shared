# Commit Conventions

Authoritative spec for commit message format across all projects.
Referenced by `al-dev-commit-agent.md` and each project's `CLAUDE.md`.

---

## Universal Subject Format

Every commit uses this format, regardless of project type:

```
<emoji> <type>(<scope>): <subject>
```

| Field | Rule |
|---|---|
| **emoji** | Required. Must match the canonical table below. Never free-hand. |
| **type** | Required. Lowercase word from the canonical type list. |
| **scope** | Required. Lowercase. Valid values depend on project type (see below). |
| **subject** | Imperative mood ("add field", not "added field"). Max 72 chars total including emoji and type. No trailing period. |

**No AI attribution.** Never append `Co-Authored-By`, `Generated with Claude Code`, or any AI footer to commit messages.

**Freshdesk references.** `#FD<number>` goes in the commit body only — never in the subject line.

---

## Canonical Emoji-Type Table

One emoji per type. Use only these. Choosing the wrong emoji for a type is a format violation.

| Emoji | Type | When to use |
|---|---|---|
| ✨ | `feat` | New feature or capability |
| 🐛 | `fix` | Bug fix |
| 🚑️ | `hotfix` | Critical production fix |
| ♻️ | `refactor` | Code restructure without behaviour change |
| ⚡ | `perf` | Performance improvement |
| 🔧 | `config` | Configuration / settings change |
| 📝 | `docs` | Documentation only |
| ✅ | `test` | Adding or updating tests |
| 🎨 | `style` | Formatting, no logic change |
| 🚚 | `move` | Move or rename files/objects |
| 🙈 | `gitignore` | .gitignore changes |
| 📦 | `chore` | Build tasks, dependency updates, mechanical work |
| 🔀 | `merge` | Merge commit |
| ⏪ | `revert` | Revert a previous commit |
| 🚧 | `wip` | Work in progress (must be squashed before merge to main) |
| 🔥 | `remove` | Delete dead code or files |
| ⬆️ | `upgrade` | Bump dependencies / versions |
| 💥 | `breaking` | Breaking change |
| 🔒 | `security` | Security fix or improvement |
| 🚨 | `lint` | Lint / compiler warning fix |
| 🩹 | `minor` | Small, obvious fix not worth a full `fix` entry |
| ➕ | `deps-add` | Add a dependency |
| ➖ | `deps-remove` | Remove a dependency |
| 🌐 | `i18n` | Internationalisation / translation |
| 📘 | `distil` | Distil a draft into a permanent knowledge note (vault projects only) |

---

## Project Types

Every project declares its type in its `CLAUDE.md` as `project-type: <type>`.

### `al` — AL/Business Central Extensions

Projects: client AL extensions (nzpg, mml, client-abc, etc.)

**Scope:** Functional module name — e.g. `price`, `rebate`, `ui`, `config`, `docs`, `vendor`, `customer`. Match the module vocabulary in the project's CLAUDE.md.

**Body:** Required for `feat`, `fix`, `refactor`, `hotfix`. Optional for `chore`, `docs`, `style`.

```
<emoji> <type>(<scope>): <subject>

WHY: <one sentence explaining motivation>

CHANGED COMPONENTS
- FileName.ObjectType.al [ObjectID] [marker]
- non-al-file.ext [marker]

[#FD<number> — only when a Freshdesk ticket exists]
```

Marker key: `[+]` added · `[m]` modified · `[-]` deleted · `[>] OldName → NewName [ID]` renamed.
Filenames only — no directory paths.

**Atomic unit:** Files that compile together commit together. Configuration changes (`app.json`, version bumps) always in their own commit — never bundled with feature or fix changes. One logical change = one commit.

---

### `vault` — Obsidian Knowledge Vaults

Projects: nzpg vault, mml vault, second-brain, client-abc vault.

**Scope:** Project/workflow name — e.g. `nzpg-core`, `vault-weave`, `distil`, `mml-anz-fileactive`, `mml-bunnings`, `archive`. Use the project slug, not a generic word.

**Body:** Subject line only. No WHY block, no CHANGED COMPONENTS.

**Atomic unit:** One topic or project area per commit. All notes for a single integration, or one complete workflow pass (e.g. a full `vault-sweep` run or a full `vault-weave` run), is one atomic unit. Do not batch changes across unrelated project areas in a single commit.

**Type guidance for vault:**

| Action | Type |
|---|---|
| Distil a draft into a permanent note | `distil` |
| Add a new project, index, or template | `feat` |
| Add vault-weave cross-links | `feat` |
| Archive or delete notes | `chore` |
| Vault sweep pass | `chore` |
| Fix a broken link or incorrect content | `fix` |
| Update obsidian plugin config | `config` |

---

### `tool` — Standalone Tools and Plugin Repos

Projects: al-dev-shared, al-smart-compile, claude-configs, copilot-configs.

**Scope:** Component or module name — e.g. `al-dev-align`, `al-dev-commit`, `skills`, `agents`, `knowledge`, `markdown`. Match the directory or skill name.

**Body:** Subject line only. No CHANGED COMPONENTS.

**Atomic unit:** One functional change = one commit. A skill update + its companion knowledge file commit together. A skill update + an unrelated agent fix = two commits. Tests that accompany a fix commit together with the fix.

---

## Atomic Commit Principles (Universal)

A commit is atomic when reverting it leaves the repo in a fully valid, consistent state — no broken references, no half-implemented features, no file-A-without-file-B.

1. **One concern per commit.** Don't bundle a feature change with an unrelated chore.
2. **Config changes are isolated.** Version bumps and settings-only changes never share a commit with code changes.
3. **Tests travel with their change.** New tests for a fix go in the same commit as the fix.
4. **`wip` commits are temporary.** Squash before merging to the main branch.

---

## Examples

**AL — feature with body:**
```
✨ feat(price): add base price override field

WHY: Customers need to override calculated base price for promotional contracts without modifying the price formula.

CHANGED COMPONENTS
- PriceList.Table.al [50910] [m]
- PriceListMgt.Codeunit.al [50911] [m]

#FD42273
```

**AL — chore (no body required):**
```
📦 chore(config): bump app version to 2.1.0
```

**Vault — distillation:**
```
📘 distil(nzpg-core): SLA date revalidation
```

**Vault — sweep pass:**
```
📦 chore(archive): vault-sweep archive/delete pass 2026-05-14
```

**Tool — skill fix:**
```
🐛 fix(al-dev-align): handle Unicode apostrophe in prohibition check
```

**Tool — new skill:**
```
✨ feat(al-dev-commit): add advisory alignment check to commit workflow
```
