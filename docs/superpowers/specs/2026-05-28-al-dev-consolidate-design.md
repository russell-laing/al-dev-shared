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
| 1 | Discover & group | `find .dev -maxdepth 1 -name "*.md"` → skip ignored files/dirs; classify into Groups A–D + persistent; group dated files by YYYY-MM-DD prefix; group solution-plan variants under base date |
| 2 | Extract per session | Classify each file by tier and run tier-appropriate bash extraction |
| 3 | Write session summaries | One `YYYY-MM-DD-session-summary.md` per date group written to `.dev/sessions/` |
| 4 | Write index | `sessions-index.md` written to `.dev/sessions/` — one row per session, links to each summary |

---

## Artifact Tiers

### Ignored (not processed)

These files are operational artifacts only — no analytical value for vault notes:

- `progress.md`, `session-log.md`
- `*-develop-progress.md`, `*-develop-checklist.md`, `*-develop-scope.md`
- `compile-errors*.log`, `investigate-errors.log`
- `*.html`
- `.DS_Store`
- Subdirectories: `archive/`, `templates/`, `attachments/`

### Group A — Core workflow documents

Undated files with a numeric prefix (`00-` through `09-`), e.g.
`00-interview.md`, `01-requirements.md`, `02-solution-plan.md`,
`03-code-review.md`, `05-test-plan.md`.

**High-value.** Extract:
- All headings
- Governance token counts: `REQ-`, `ACC-`, `TEST-`, `DEC-`, `IMP-`, `DEP-`, `RISK:`
- First 3 lines under each `##`-level heading

Multiple solution-plan variants at the same numbered prefix (e.g.
`02-solution-plan.md`, `02-solution-plan-option-b.md`) are grouped together
under Group A with a `(variant)` label rather than treated as separate entries.

### Group B — Test delivery documents

Undated files with ALL-CAPS names, e.g. `UNIT-TEST-QUICK-REFERENCE.md`,
`EDGE-CASE-TEST-DELIVERABLES.md`, `FINAL-VERIFICATION-CHECKLIST.md`.

**Medium-value.** Extract:
- All headings
- `TEST-` token count and classifier types (UNIT|INTEGRATION|SCENARIO|PERFORMANCE)

### Group C — Ticket-context files

Filename contains `ticket-context` (dated or undated).

**High-value.** Extract:
- All headings + first 5 lines per section
- Vault Candidates detection (feedback/user/customer language)
- Sets `vault_promote: true` in frontmatter when non-empty

### Group D — Dated session artifacts (standard tier)

Covers dated files not already matched by Groups A–C:
`explore-findings`, `investigate-findings`, `interview-requirements`,
`solution-plan` (+ `-option-a`, `-option-b` variants), `code-review`,
`review-findings`, `autonomous-*`, `perf-analysis`, `handoff-prompt`,
`release-notes`, `develop-phase4-handoff`

Solution plan variants (`*-option-a.md`, `*-option-b.md`) are grouped under
their base session date with a `(variant)` label — not treated as separate
sessions.

Headings and key verdict/phase lines only.

### High-value upgrade signals (apply on top of any group)

| Signal | Detection | Extra content extracted |
|--------|-----------|------------------------|
| Diagram | File contains ` ```mermaid ` | Full mermaid block(s) + the heading immediately above each block |
| Image reference | File contains `![` | Full paragraph (±2 lines) surrounding each image reference |

A single file may qualify under multiple signals; all applicable extractions
are combined on top of the group's base extraction.

---

## Extraction Logic

### Group D standard tier

```bash
# Headings
grep '^#' "$file"

# Key decision lines
grep -E '^✅|^❌|^Phase [0-9]|^Status:|^Outcome:|\*\*(Verdict|Decision|Result)\*\*' "$file" | head -20
```

### Group A — Core workflow docs (governance tokens)

```bash
# Headings
grep '^#' "$file"

# First 3 lines under each ## heading
awk '/^## /{if(NR>1)count=0} count<=3{print; count++}' "$file"

# Governance token summary (count occurrences of each type)
for token in REQ ACC TEST DEC IMP DEP RISK; do
  n=$(grep -c "${token}-\|${token}:" "$file" 2>/dev/null || echo 0)
  [ "$n" -gt 0 ] && echo "${token}: $n"
done
```

### Group B — Test delivery docs

```bash
# Headings
grep '^#' "$file"

# TEST token lines with type classifiers
grep -E 'TEST-[0-9]+|UNIT\||INTEGRATION\||SCENARIO\||PERFORMANCE\|' "$file" | head -20
```

### Group C — Ticket-context

```bash
# Headings + first 5 lines per section
grep '^#' "$file"
awk '/^#/{if(NR>1)count=0} count<5{print; count++}' "$file"
```

### Mermaid upgrade

```bash
awk '
  /^#/ { last_heading = $0 }
  /^```mermaid/ { in_block=1; print last_heading; print; next }
  in_block { print; if (/^```$/) in_block=0 }
' "$file"
```

### Image reference upgrade

```bash
grep -B2 -A2 '!\[' "$file"
```

### Vault Candidates detection (Group C only)

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
artifacts: [ticket-context, solution-plan, develop-code-review]
vault_promote: true
---

# Session Summary — YYYY-MM-DD

## Artifacts Present
✅ ticket-context | ✅ solution-plan | ✅ code-review | ❌ explore-findings

## Core Workflow Documents
[Group A content — headings + governance token counts + first-3-lines-per-section]

## Test Coverage
[Group B content — headings + TEST token type summary]

## Ticket Context
[Group C content — headings + first-5-lines-per-section]

## Session Artifacts
[Group D content — one subsection per artifact with headings + verdict lines]

## Diagrams
[Mermaid blocks with source heading, if any]

## Image References
[Paragraph context around each image reference, if any]

## Vault Candidates
[Feedback/customer/user language from ticket-context; section omitted if empty]
```

`vault_promote: true` is set when the Vault Candidates section is non-empty.
Sections are omitted entirely when no files fall into that group for the session.

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

Undated files that are not Group A (numeric prefix), Group B (ALL-CAPS), or
Group C (ticket-context) form the persistent group. Typical members:
`project-context.md`, `learnings.md`, `source-*.md`.

- Written to `.dev/sessions/persistent-summary.md` using Group D standard
  extraction (Group C signals apply to `source-ticket-context.md` if present)
- Added as a pinned first row in `sessions-index.md`:

```markdown
| [[persistent-summary\|Persistent]] | project-context, learnings | — |
```

`learnings.md` is treated as Group D standard tier (headings + verdict lines).

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
