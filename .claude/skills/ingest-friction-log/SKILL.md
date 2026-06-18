---
name: ingest-friction-log
description: >-
  Ingest friction logs from ~/friction-log/ (curated session-analysis findings
  plus aggregated tool-error signals) into the self-healing health loop as a
  discover-stage source, then archive the consumed logs. Routes findings by the
  surface they implicate; breadcrumb next_command
    construction orders plugin surface first. Writes per-surface
  YYYY-MM-DD-<surface>-friction-findings.md artifacts consumed by
  /plugin-health-report via --findings, and records local runtime provenance in
  docs/health/friction-ingest-log.md (gitignored). Run when friction logs have
  accumulated
  and you want them folded into the plugin health audit.
  Triggers on: "ingest friction logs", "ingest the friction log", "process
  friction logs", "fold friction into the health loop", "archive friction logs".
argument-hint: "[--source <path>] [--surface plugin|tooling|both] [--since YYYY-MM-DD]"
workflow:
  stage: discover
  invoked-by: user
  repeatable: true
  inputs:
    - ~/friction-log/<session>-findings.md
    - ~/friction-log/<session>-signals.json
  outputs:
    - docs/health/<date>-<surface>-friction-findings.md
  next:
    - plugin-health-report
---

# Skill: /ingest-friction-log

Discover-stage source for the self-healing loop. Reads friction logs produced by
the session analyst, turns them into findings files that `/plugin-health-report`
consumes, and archives the consumed logs.

Read `.claude/knowledge/health-filter-contract.md` (especially "## Friction
Source") and `.claude/knowledge/health-loop-state-contract.md` first; both are
canonical for the findings metadata and the loop breadcrumb this skill writes.

This skill never edits plugin or tooling source files. It writes only under
`docs/health/` and `.dev/`, and moves files within the source directory.

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md`: before reporting
any phase complete, advancing to the next phase, or updating
`.dev/health-loop-state.md`, emit a phase-proof block (observed command output
or file-existence check) binding to that phase's deliverable. A restated
intention is not proof.

## Phase 0 — Setup & resume

1. **Parse arguments:**
   - `--source <path>` — friction-log directory; default `~/friction-log`.
   - `--surface plugin|tooling|both` — default `both` (plugin-first ordering).
   - `--since <YYYY-MM-DD>` — optional; ignore logs whose filename date is older.

2. **Read the loop breadcrumb.** If `.dev/health-loop-state.md` exists, read it
   (schema: `.claude/knowledge/health-loop-state-contract.md`). If its
   `next_command` names a *later* loop step (report/dispositions/plan/implement),
   warn the user that a prior loop is still in flight before ingesting.

3. **List un-archived friction logs** (use `find`, never bare globs — zsh errors
   on an empty glob):

   ```bash
   SOURCE="${SOURCE:-$HOME/friction-log}"
   find "$SOURCE" -maxdepth 1 -name '*-findings.md' | sort
   find "$SOURCE" -maxdepth 1 -name '*-signals.json' | sort
   ```

   Logs already under `$SOURCE/archived/` are excluded by `-maxdepth 1`.

4. If no un-archived `*-findings.md` and no `*-signals.json` are found, report
   "No new friction logs to ingest." and stop.

## Phase 1 — Ingest curated findings

For each un-archived `*-findings.md` (read it directly — these are bounded,
curated session-analysis reports):

1. Parse each `### [HIGH|MEDIUM|LOW] <title>` finding and its
   Pattern / Evidence / Root cause / Recommended fix fields.

2. **Surface classification** — by the target path(s) cited in the Recommended
   fix:
   - path under `profile-al-dev-shared/` (or a distributed knowledge file) -> `plugin`
   - path under `.claude/` -> `tooling`
   - a finding citing both surfaces -> emit one finding to each.

3. **Dimension classification:**
   - workflow / handoff / routing gaps -> `design`
   - instruction-quality / safety / clarity / missing-guidance -> `quality`
   - literal naming-convention violations -> `naming` (rare; otherwise fold into `quality`).

4. **Severity:** `HIGH`/`MEDIUM`/`LOW` -> `High`/`Medium`/`Low`.

Hold each result as `(surface, dimension, severity, slug, file_line, snippet, reason, fix)` where:

- `file_line` is the exact `path/to/file:N` cited in the Recommended fix or Evidence
- `snippet` is a short quoted excerpt from that location (collected here for downstream evidence verification by `/plugin-health-report`)
- `reason` is a one-line explanation of why the snippet demonstrates the problem
- `fix` is the recommended correction

## Phase 2 — Aggregate signal patterns

Aggregate `*-signals.json` **without reading any file whole into context** — use
`jq`/`grep` counts only. Example (tool-error tally across all signal files):

```bash
find "$SOURCE" -maxdepth 1 -name '*-signals.json' -print0 \
  | xargs -0 grep -hoE '"(toolUseResult|error)":[^,}]*' 2>/dev/null \
  | sort | uniq -c | sort -rn | head -30
```

Treat any tool-error category recurring across **≥2 distinct sessions** (sessions from different calendar days) as one
systemic finding (e.g. "Write-before-Read across N sessions"). Surface-classify
it by where the erroring skill/tool lives; assign dimension `quality` and a
severity reflecting how often it blocked work.

## Phase 3 — Write findings files, manifest, breadcrumb

1. **Findings files.** For each surface that has at least one finding, write
   `docs/health/<today>-<surface>-friction-findings.md`. If the file already
   exists for today, Read it first (read-before-write), then overwrite.

   Template (consumed by `/plugin-health-report --findings <path>`; block
   headings and the `dimensions:` list MUST follow
   `.claude/knowledge/health-filter-contract.md` "## Friction Source"):

   ```markdown
   ---
   surface: plugin
   dimensions: [design, quality]
   source_contract: .claude/knowledge/health-filter-contract.md
   resume_mode: false
   ---
   # Plugin Friction Findings — <today>

   ## Raw lens output

   ### Friction: Instruction Quality (quality) Findings
   - **[stash-baseline-dataloss]** | High | `profile-al-dev-shared/knowledge/compile-lint-procedure.md:12` `"git stash then git reset --hard"` — permitted as a baseline; destroyed staged work in session cb11c6 | add stash/reset prohibition to Baseline + Diff section

   ### Friction: Workflow (design) Findings
   - **[worktree-loss-recovery]** | Medium | `profile-al-dev-shared/knowledge/workflow-resilience.md:8` `"# Recovery (no content)"` — no guidance for reapplying staged changes lost to a reset | add a recovery sub-section for staged-change loss
   ```

   Only include `dimensions:` entries (and their blocks) that actually have
   findings. Omit a block entirely if its dimension has no findings.

2. **Manifest.** Ensure `docs/health/friction-ingest-log.md` exists; if absent,
   create it with this header:

   ```markdown
   # Friction Ingest Log

   Local runtime provenance for /ingest-friction-log (gitignored — not a durable
   cross-session record). One row per ingested log; an archived log is never
   re-ingested.

   | Date | Source log | Findings → surface | Status |
   | ---- | ---------- | ------------------ | ------ |
   ```

   Append one row per ingested `*-findings.md`, e.g.:

   ```markdown
   | <today> | cb11c6-findings.md | 5 → plugin (3), tooling (2) | archived |
   ```

3. **Breadcrumb.** Write `.dev/health-loop-state.md` (schema:
   `.claude/knowledge/health-loop-state-contract.md`):
   - `stage_completed: ingest-friction-log`
   - `completed_at:` today's ISO date
   - `next_command: /plugin-health-report --findings docs/health/<today>-plugin-friction-findings.md`
     (lead with the plugin path; if only tooling findings exist, use that path)
   - `next_inputs:` every friction findings file written this run
   - `fresh_session_recommended: false`
   - `note:` "Friction ingested as a discover source; report ranks and
     evidence-verifies it. Already-fixed friction will drop under
     'Dropped (unverified)'."

## Phase 4 — Archive & hand off

1. **Archive consumed logs** (create the archive dir with `find`-safe commands):

   ```bash
   mkdir -p "$SOURCE/archived"
   # for each ingested findings/signals file:
   mv "$SOURCE/<session>-findings.md" "$SOURCE/archived/"
   mv "$SOURCE/<session>-signals.json" "$SOURCE/archived/"
   ```

   Move both the `*-findings.md` and its paired `*-signals.json`.

2. **Present a summary**, per surface: friction findings path, High/Medium/Low
   counts, number of systemic signal findings, and number of logs archived.

3. **Hand off** (plain assistant text — do not echo through bash):
   "Friction ingested. Next in the loop:
   `/plugin-health-report --findings docs/health/<today>-plugin-friction-findings.md`.
   The report will rank these and drop any already-fixed friction under
   'Dropped (unverified)'."

Do not edit any source file. Do not run `/plugin-health-report` yourself — the
user (or the loop) invokes it next.
