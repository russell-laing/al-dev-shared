# Design: al-dev-consolidate skill

**Date:** 2026-05-28
**Status:** Approved

## Purpose

A skill that consolidates `.dev/` workflow artifacts produced by
`profile-al-dev-shared` into per-session summary notes and a sessions index,
suitable for import into second-brain vaults (e.g. Obsidian). Designed to
handle repositories with large numbers of files from multiple sessions over
weeks without exceeding the context window.

---

## Skill Identity

| Field | Value |
|-------|-------|
| Name | `al-dev-consolidate` |
| Invocation | `/al-dev-consolidate` |
| Argument | none |
| Output location | `.dev/sessions/` within the current repository |

---

## Phases

| Phase | Name | Description |
|-------|------|-------------|
| 0 | Resume check | If `.dev/sessions/sessions-index.md` exists, ask: re-run all / update new sessions only / cancel |
| 1 | Discover & group | `ls .dev/` → group files by YYYY-MM-DD prefix; undated files form a "persistent" group |
| 2 | Extract per session | Classify each file by tier and run tier-appropriate bash extraction |
| 3 | Write session summaries | One `YYYY-MM-DD-session-summary.md` per date group written to `.dev/sessions/` |
| 4 | Write index | `sessions-index.md` written to `.dev/sessions/` — one row per session, links to each summary |

---

## Artifact Tiers

### Ignored (not processed)

These files are operational artifacts only — no analytical value for vault notes:

- `progress.md`
- `*-develop-progress.md`
- `*-develop-checklist.md`
- `*-develop-scope.md`
- `compile-errors.log`
- `investigate-errors.log`

### Standard tier

Headings and key verdict/phase lines only.

Files: `explore-findings`, `investigate-findings`, `interview-requirements`,
`solution-plan`, `perf-analysis`, `handoff-prompt`, `release-notes`

### High-value tier

Deeper extraction triggered by one or more of these signals:

| Signal | Detection | Extra content extracted |
|--------|-----------|------------------------|
| Ticket context | Filename contains `ticket-context` | All headings + first 5 lines per section + Vault Candidates block |
| Diagram | File contains ` ```mermaid ` | Full mermaid block(s) + the heading immediately above each block |
| Image reference | File contains `![` | Full paragraph (±2 lines) surrounding each image reference |

A single file may qualify under multiple signals; all applicable extractions are combined.

---

## Extraction Logic

### Standard tier

```bash
# Headings
grep '^#' "$file"

# Key decision lines
grep -E '^\*\*|^- \*\*|^✅|^❌|^Phase [0-9]|^Status:|^Outcome:' "$file" | head -20
```

### Ticket-context tier

```bash
# Headings + first 5 lines per section
grep '^#' "$file"
awk '/^#/{if(NR>1)count=0} count<5{print; count++}' "$file"
```

### Mermaid extraction

```bash
awk '
  /^#/ { last_heading = $0 }
  /^```mermaid/ { in_block=1; print last_heading; print; next }
  in_block { print; if (/^```$/) in_block=0 }
' "$file"
```

### Image reference extraction

```bash
grep -B2 -A2 '!\[' "$file"
```

### Vault Candidates detection (ticket-context files only)

Flag sections containing feedback/user/customer language:

```bash
grep -i 'customer\|feedback\|user reported\|workaround\|pain point\|request\|complaint' "$file" | head -10
```

---

## Output Format

### Per-session summary

Path: `.dev/sessions/YYYY-MM-DD-session-summary.md`

```markdown
---
date: YYYY-MM-DD
artifacts: [ticket-context, explore-findings, solution-plan, develop-code-review]
vault_promote: true
---

# Session Summary — YYYY-MM-DD

## Artifacts Present
✅ ticket-context | ✅ explore-findings | ✅ solution-plan | ✅ code-review | ❌ lint-report

## Key Content

### ticket-context
[headings + first-5-lines-per-section extraction]

### solution-plan
[headings + verdict lines]

## Diagrams
[mermaid blocks with source heading, grouped by originating artifact]

## Image References
[paragraph context around each `![` reference]

## Vault Candidates
[grep hits for feedback/customer/user language from ticket-context]
```

`vault_promote: true` is set when the Vault Candidates section is non-empty.

### Sessions index

Path: `.dev/sessions/sessions-index.md`

```markdown
# Session Index — [repo name]

| Date | Artifacts Present | Vault Candidates |
|------|-------------------|-----------------|
| [[2026-05-19-session-summary\|2026-05-19]] | ticket, plan, code-review | ✅ |
| [[2026-05-12-session-summary\|2026-05-12]] | explore, plan | ❌ |
```

Obsidian wiki-link syntax (`[[file|label]]`) so links resolve natively in the vault.

---

## Persistent Artifacts Group

Undated files (`project-context.md`, `learnings.md`, `source-*.md`) do not
belong to a session date. They are processed as a single "persistent" group:

- Written to `.dev/sessions/persistent-summary.md` using the same tier rules
  (ticket-context signals apply to `source-ticket-context.md`)
- Added as a pinned first row in `sessions-index.md`:

```markdown
| [[persistent-summary\|Persistent]] | project-context, learnings | — |
```

`learnings.md` is treated as standard tier (headings + verdict lines).

---

## Context Window Strategy

All artifact content is extracted via bash commands — file content is never
read into LLM context. The skill only holds:

- The bash command outputs (excerpts, not full files)
- The assembled summary text for the current session being written

This keeps context consumption constant per session regardless of how many
total sessions exist or how large source artifacts are.

---

## Repo Name Resolution

For the sessions index header, resolve repo name in this order:

1. `app.json` → `"name"` field
2. Directory name of current working directory
3. Fallback: `"this repository"`

```bash
REPO_NAME=$(python3 -c "import json; print(json.load(open('app.json'))['name'])" 2>/dev/null || basename "$PWD")
```

---

## Resume Behaviour (Phase 0)

If `.dev/sessions/sessions-index.md` already exists:

```
Sessions index found (N sessions previously consolidated).

Options:
  1. Re-run all — regenerate every session summary from scratch
  2. Update — process only session dates not already in the index
  3. Cancel
```

"Update" mode: compare date groups from `ls .dev/` against dates already
present in `sessions-index.md` and process only the new ones.

---

## Skill Placement

The skill lives in `profile-al-dev-shared/skills/al-dev-consolidate/SKILL.md`.
It is a standalone skill — not part of the main development workflow chain —
so it does not appear in the Layer 1 lifecycle diagram as a mandatory step.
It should be noted in `docs/al-dev-plugin-map.md` as a utility/archive skill.
