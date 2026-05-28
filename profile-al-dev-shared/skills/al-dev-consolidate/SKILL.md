---
name: al-dev-consolidate
description: >-
  Consolidate .dev/ workflow artifacts into per-session summary notes and a
  sessions index for import into second-brain vaults (e.g. Obsidian). Use
  after any multi-session development workflow to archive findings and create
  vault-ready session notes. Handles repositories with large artifact counts
  by extracting only bash excerpts — never reads full file content into context.
argument-hint: ""
---

# `/al-dev-consolidate` — Artifact Consolidation

Consolidates `.dev/` workflow artifacts produced by `profile-al-dev-shared`
into per-session summary notes and a sessions index. Designed to handle
repositories with large numbers of files from multiple sessions over weeks
without exceeding the context window.

All artifact content is extracted via bash commands — file content is never
read into LLM context. Working memory holds only bash command outputs
(excerpts) and the assembled summary text for the current session being written.

---

## Phase 0 — Resume Check

Check whether a sessions index already exists:

```bash
if [ -f ".dev/sessions/sessions-index.md" ]; then
  echo "exists"
  grep '^\|' .dev/sessions/sessions-index.md \
    | grep -v '^| Date' | grep -v '^|---' | wc -l
fi
```

If `.dev/sessions/sessions-index.md` exists, count the rows (N) and ask:

```
Sessions index found (N sessions previously consolidated).

Options:
  1. Re-run all — regenerate every session summary from scratch
  2. Update — rebuild changed summaries and add newly discovered sessions
  3. Cancel
```

- **1 (Re-run all)** — proceed to Phase 1; process all sessions
- **2 (Update)** — proceed to Phase 1; in Phase 3 skip any dated session
  summary whose source files are all older than the existing summary file;
  always rebuild `persistent-summary.md`
- **3 (Cancel)** — stop immediately

If no index exists, proceed directly to Phase 1.

---

## Phase 1 — Discover & Group

### Step 1: Discover .dev/ files

```bash
find .dev -maxdepth 1 -name "*.md" | sort
```

### Step 2: Resolve repo name

```bash
REPO_NAME=$(python3 -c \
  "import json; print(json.load(open('app.json'))['name'])" \
  2>/dev/null || basename "$PWD")
echo "$REPO_NAME"
```

Hold `REPO_NAME` in working memory.

### Step 3: Filter out ignored files

Remove from the discovered list any file whose basename exactly matches, or
glob-matches, any of the following:

- Exact names: `progress.md`, `session-log.md`
- Glob patterns: `*-develop-progress.md`, `*-develop-checklist.md`,
  `*-develop-scope.md`
- Log files: `compile-errors*.log`, `investigate-errors.log`
- Dotfiles: `.DS_Store`

Also skip any path that contains a directory component named `archive/`,
`templates/`, or `attachments/`.

### Step 4: Classify remaining files into groups

For each remaining file, assign exactly one group using these rules in
priority order:

| Group | Rule |
|-------|------|
| **A — Core workflow** | Basename matches `^[0-9][0-9]-` (e.g. `00-interview.md`, `02-solution-plan-option-b.md`) |
| **B — Test delivery** | Basename is ALL-CAPS-WITH-HYPHENS (e.g. `UNIT-TEST-QUICK-REFERENCE.md`) |
| **C — Ticket context** | Basename contains `ticket-context` |
| **D — Dated artifact** | Basename starts with a `YYYY-MM-DD` date and does not match A–C |
| **Persistent** | Undated file not matching A, B, or C |

For Group D files, extract the leading `YYYY-MM-DD` as the **session date**.
Group all files sharing the same session date together.

Multiple Group A variants at the same numeric prefix (e.g.
`02-solution-plan.md` and `02-solution-plan-option-b.md`) are presented
together with a `(variant)` label — not treated as separate entries.

Dated solution-plan variants (e.g. `2026-05-19-solution-plan-option-b.md`)
belong to their base session date with a `(variant)` label — not separate
sessions.

Hold in working memory:
- `DATE_GROUPS`: list of `(date, [file paths])` pairs, sorted newest-first
- `PERSISTENT_FILES`: list of file paths in the persistent group

---

## Phase 2 — Extract Per Session

For each date group and for persistent files, run the extraction commands
below. Hold only the command outputs — never the full file content.

### Group A — Core workflow documents

```bash
file="<path>"

# All headings
grep '^#' "$file"

# First 3 non-heading lines under each ## heading
awk '
  /^## / { in_section=1; remaining=3; next }
  /^#/   { in_section=0 }
  in_section && remaining > 0 { print; remaining-- }
' "$file"

# Governance token counts
for token in REQ ACC TEST DEC IMP DEP RISK; do
  n=$(grep -c "${token}-\|${token}:" "$file" 2>/dev/null || echo 0)
  [ "$n" -gt 0 ] && echo "${token}: $n"
done
```

### Group B — Test delivery documents

```bash
file="<path>"

# All headings
grep '^#' "$file"

# TEST token lines with type classifiers
grep -E 'TEST-[0-9]+|UNIT\||INTEGRATION\||SCENARIO\||PERFORMANCE\|' \
  "$file" | head -20
```

### Group C — Ticket-context files

```bash
file="<path>"

# All headings
grep '^#' "$file"

# First 5 non-heading lines per section
awk '
  /^#/ { in_section=1; remaining=5; next }
  in_section && /^#/ { in_section=0 }
  in_section && remaining > 0 { print; remaining-- }
' "$file"
```

Also run Vault Candidates detection:

```bash
grep -i \
  'customer\|feedback\|user reported\|workaround\|pain point\|request\|complaint' \
  "$file" | head -10
```

Set `vault_promote: true` for this session if Vault Candidates extraction
returns any non-empty lines.

### Group D — Dated session artifacts

```bash
file="<path>"

# All headings
grep '^#' "$file"

# Key verdict / phase lines
grep -E \
  '^✅|^❌|^Phase [0-9]|^Status:|^Outcome:|\*\*(Verdict|Decision|Result)\*\*' \
  "$file" | head -20
```

### Persistent files

Apply Group D extraction to each persistent file, **except** any whose
basename contains `ticket-context` — apply Group C extraction (including
Vault Candidates detection) to those.

`learnings.md` is treated as Group D standard tier (headings + verdict lines).

### High-value upgrade signals (apply on top of any group)

After running the group-appropriate extraction, check each file for:

**Mermaid diagram** — if the file contains ` ```mermaid `:

```bash
awk '
  /^#/ { last_heading = $0 }
  /^```mermaid/ { in_block=1; print last_heading; print; next }
  in_block { print; if (/^```$/) in_block=0 }
' "$file"
```

**Image reference** — if the file contains `![`:

```bash
grep -B2 -A2 '!\[' "$file"
```

Both signals may match the same file — combine all extra extractions with
the group's base excerpts.

---

## Phase 3 — Write Session Summaries

For each date group, assemble a session summary and write it to
`.dev/sessions/YYYY-MM-DD-session-summary.md`.

### Update mode: staleness check

In Update mode (Phase 0 option 2), before writing, check whether any source
file is newer than the existing summary:

```bash
existing=".dev/sessions/${DATE}-session-summary.md"
if [ -f "$existing" ]; then
  needs_rebuild=0
  for src in <source-files-for-this-date>; do
    [ "$src" -nt "$existing" ] && needs_rebuild=1 && break
  done
  [ "$needs_rebuild" -eq 0 ] && echo "skip"
fi
```

Skip writing if no source file is newer and the summary already exists.
For newly discovered session dates not yet in the existing index, always
write.

Always rebuild `persistent-summary.md` regardless of mode — undated files
can change without introducing a new session date.

### Artifacts present table

Scan the session's file list for these substrings to determine presence:

`ticket-context`, `solution-plan`, `code-review`, `explore-findings`,
`investigate-findings`, `interview-requirements`, `release-notes`,
`handoff-prompt`, `perf-analysis`

Build a presence line with ✅ / ❌ for each type.

### Summary template

```markdown
---
date: YYYY-MM-DD
artifacts: [ticket-context, solution-plan, code-review]
vault_promote: true
---

# Session Summary — YYYY-MM-DD

## Artifacts Present
✅ ticket-context | ✅ solution-plan | ✅ code-review | ❌ explore-findings | ...

## Core Workflow Documents
[Group A excerpts: headings, governance token counts, first-3-lines-per-section]

## Test Coverage
[Group B excerpts: headings, TEST token type summary]

## Ticket Context
[Group C excerpts: headings, first-5-lines-per-section]

## Session Artifacts
[Group D excerpts: one subsection per artifact — headings + verdict lines]

## Diagrams
[Mermaid blocks with source heading; omit section if none found]

## Image References
[Paragraph context around each image reference; omit section if none found]

## Vault Candidates
[Feedback/customer/user language from ticket-context; omit section if empty]
```

**Omit any section entirely when no files of that group are present for the
session.** Set `vault_promote: false` when the Vault Candidates section is
empty.

### Ensure output directory

```bash
mkdir -p .dev/sessions
```

### Write persistent summary

Apply the same assembly process to `PERSISTENT_FILES` and write to
`.dev/sessions/persistent-summary.md`. Always rebuild (never skip in Update
mode).

---

## Phase 4 — Write Sessions Index

Assemble and write `.dev/sessions/sessions-index.md`.

### Index template

```markdown
# Session Index — [REPO_NAME]

| Date | Artifacts Present | Vault Candidates |
|------|-------------------|-----------------|
| [[persistent-summary\|Persistent]] | project-context, learnings | — |
| [[2026-05-19-session-summary\|2026-05-19]] | ticket, plan, code-review | ✅ |
| [[2026-05-12-session-summary\|2026-05-12]] | explore, plan | ❌ |
```

Rules:
- Persistent row is always first (pinned)
- Dated rows ordered newest-first
- Artifacts Present: comma-separated short names of matched artifact types
- Vault Candidates: ✅ if `vault_promote: true`, ❌ otherwise, `—` for the Persistent row
- Use Obsidian wiki-link syntax: `[[filename-without-extension\|display-label]]`

### Present to user

After writing the index:

```
Consolidation complete → .dev/sessions/

Sessions processed: N
  [YYYY-MM-DD] ✅ vault_promote
  [YYYY-MM-DD] ❌
  ...

Persistent: .dev/sessions/persistent-summary.md
Index:      .dev/sessions/sessions-index.md
```
