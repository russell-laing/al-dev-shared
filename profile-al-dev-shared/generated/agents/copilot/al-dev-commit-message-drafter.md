---
name: "al-dev-commit-message-drafter"
description: "Git commit message drafter agent. Consumes manifests from al-dev-commit-agent-analysis, proposes atomic commit groups, and drafts commit messages. Dispatched by /al-dev-commit (message-drafting phase)."
tools: []
---


# Agent: al-dev-commit-message-drafter (Message-Drafting Phase)

Message-drafting phase of the commit workflow. Dispatched by `/al-dev-commit` with
manifest analysis and project context.

**Tools:** None — all inputs arrive in the dispatch prompt; no external tool calls are required.

All inputs arrive in the dispatch prompt:

- `MANIFESTS` — per-file change summaries from al-dev-commit-agent-analysis
- `PROJECT_CONTEXT` — scopes, object ID prefix, naming patterns
- `FD_TICKET` — Freshdesk ticket number or empty

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| MANIFESTS | **Yes** | Per-file change summary from al-dev-commit-agent-analysis (object IDs, added/removed fields and procedures) |
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
