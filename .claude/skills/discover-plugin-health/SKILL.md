---
name: discover-plugin-health
description: >-
  Discovery phase of the plugin health sweep. Builds file lists, aggregates
  context from documentation maps, dispatches design, quality, and naming lenses
  (surface-scoped — one design lens is excluded per surface; see Phase 3 for
    the per-surface exclusion conditions),
  and writes RAW (unranked) lens findings to
  docs/health/YYYY-MM-DD-<surface>-findings.md, which also carries a
  `## Failed lenses` section and a `## Resume information` block tracking
  completion status. The ranked dossier is produced
  separately by /report-plugin-health. Called by /audit-plugin-health; can also
  be run standalone to refresh findings without re-running the report phase, but it requires the same
  pre-conditions as a full audit run. Discovery is via parallel lens dispatch
  (not direct file scanning).
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|naming|all] [--resume] [--since <ref>]"
workflow:
  stage: discover
  invoked-by: both
  repeatable: true
  inputs:
    - docs/al-dev-skills-map.md
    - docs/al-dev-agent-map.md
    - profile-al-dev-shared/knowledge/lens-invocation-patterns.md
  outputs:
    - docs/health/<date>-<surface>-findings.md
  next: [report-plugin-health]
---

# Skill: /discover-plugin-health

Discovery phase of the health sweep. Dispatches lenses and writes findings files
that `/report-plugin-health` consumes.

Read `.claude/knowledge/health-filter-contract.md` first and treat it as the
canonical source of truth for surface values, dimension values, defaults,
findings metadata, legacy `unknown`, and resume mismatch handling.

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md` — emit a phase-proof block at each phase boundary before reporting completion or updating `.dev/health-loop-state.md`.

## Dispatch policy

This skill's agent dispatch follows `../../knowledge/dispatch-fallback-contract.md`:
declare the preferred path (the `Agent` tool), run preflight (tool available,
arguments valid against the receiving contract), fall back deterministically on
failure, and log `preferred → outcome → fallback → reason`.

## Phase 0 — Parse arguments

- `--surface` ∈ `plugin` | `tooling` | `both` (default `both`)
- `--dimension` ∈ `design` | `quality` | `naming` | `all` (default `all`)
- `--resume` ∈ present | absent (default absent)
- `--since <ref>` ∈ any git ref (commit SHA, branch, tag, or `HEAD~N`); absent by default

**`--since` semantics:** when present, `git diff --name-only <ref>` is used to build
the changed-files set (working-tree-vs-`<ref>` — captures committed, staged, and
unstaged changes in a single pass). If only *committed* changes since `<ref>` are
wanted, use the two-dot form `<ref>..HEAD` manually. The changed-files set is used
to narrow file lists for **scopable lenses only** (see Phase 1 scopability table);
non-scopable lenses always receive the full corpus. The Phase 2 run manifest is
always built from the **full** corpus so cross-file mappings stay correct.

Surface → directory mapping:

- `plugin` → `profile-al-dev-shared/`
- `tooling` → `.claude/`

**Pre-conditions (per requested surface):** Run the full pre-condition orchestration in
`.claude/knowledge/health-audit-preconditions.md` — cadence guard, stale-open check,
dossier disposition-coverage test, user override, and the `--resume` exemption. If a
check blocks the run (and no override/`--resume` applies), report the condition and stop.

**Happy path:** when Disposition coverage exists and is dated on or after the dossier
date, proceed to the stale-open check, then dispatch normally.

## Phase 1 — Build file lists (per requested surface)

For each requested surface, glob both object types. All paths are absolute;
set `REPO` first so the commands work on any machine:

```bash
REPO=$(git rev-parse --show-toplevel)
# plugin surface
find "$REPO/profile-al-dev-shared/agents" -name "*.md" | sort
find "$REPO/profile-al-dev-shared/skills" -name "SKILL.md" | sort
# tooling surface
find "$REPO/.claude/agents" -name "*.md" ! -path "*/archived/*" | sort
# workflow-contracted skills only; adjacent tools (no workflow: block) are excluded to avoid noise and cost
find "$REPO/.claude/skills" -name "SKILL.md" ! -path "*/archived/*" \
  | while read f; do grep -q "^workflow:" "$f" && echo "$f"; done \
  | sort
```

Keep the agent list and skill list separate — different lenses target each.

### Lens scopability classification

When `--since` is present, only **scopable** lenses have their file list narrowed
to changed files. **Non-scopable** lenses always receive the full corpus (they
compare across files and would produce wrong results on a partial list).

| Scopable — narrow to changed files | Non-scopable — always full corpus |
|------------------------------------|-----------------------------------|
| All `quality-agent-lens-*` | `design-skill-lens-near-duplicates` |
| All `quality-skill-lens-*` | `design-skill-lens-shared-backbone` |
| `design-agent-lens-scope-isolation` | `design-skill-lens-handoff-gaps` |
| `design-agent-lens-model-fit` | `design-skill-lens-preplanning` |
| `design-agent-lens-caller-alignment` | |
| `design-agent-lens-usage-patterns` | |
| `design-agent-lens-tool-hygiene` | |
| `design-skill-lens-complexity` | |
| `design-skill-lens-surface-placement` | |
| `design-skill-lens-maintainer-handoff` | |
| `naming-convention-lens` | |

Rationale: scopable lenses make per-file or per-object judgements; the mapping
context in the run manifest (Phase 2) encodes cross-file facts, so per-object
findings remain correct even on a narrowed list. Non-scopable lenses compare
*across* the corpus (duplicate shapes, shared backbone, handoff chains, preplanning
diagram placement) and cannot produce correct results against a partial file list.

### `--since` path normalization (load-bearing)

`git diff --name-only <ref>` emits **repo-root-relative** paths (e.g.
`profile-al-dev-shared/agents/foo.md`), while the glob commands above produce
**absolute** paths (e.g. `/Users/dev/repo/profile-al-dev-shared/agents/foo.md`).
A naive set intersection of the two yields the **empty set**, which silently
reads as "nothing to check → no findings" — a correctness bug that masquerades as
a clean pass.

**Required normalization:** before intersecting, resolve each `git diff` output
path to absolute by prepending `$REPO/`:

```bash
REPO=$(git rev-parse --show-toplevel)
# Build changed-files set as absolute paths
CHANGED=$(git diff --name-only "$SINCE_REF" | sed "s|^|$REPO/|")
```

Then intersect the globbed absolute list against the absolute `$CHANGED` set.
Both sides are now absolute — the intersection is correct.

### `--since` empty-intersection skip behavior

After narrowing a scopable lens's file list:

- **Non-empty result:** dispatch the lens against the narrowed list as normal.
- **Empty result** (no changed files in scope for that lens's object type): **skip
  dispatching that lens** and log a skip note instead of dispatching against an
  empty list. A no-file dispatch wastes a call and can emit a spurious "no findings"
  block. Log format: `<lens-name>: skipped (no changed files in scope)`.

Non-scopable lenses are **never** skipped — they always run against the full corpus.

## Phase 2 — Pre-dispatch aggregation

Before dispatching lenses, extract context from the documentation maps
(`docs/al-dev-agent-map.md` and `docs/al-dev-skills-map.md`) following the full
procedure in `.claude/knowledge/health-discover-aggregation.md`. It defines the
map-parse steps and the derived dispatch mappings that the Phase 3 lenses
consume. Each mapping is a small projection of the maps:

- `tool_inventory` — declared tools per agent
- `model_assignments` — model tier per agent
- `caller_map` — which skills dispatch each agent
- `layer1_diagram_content` — text of the Layer 1 lifecycle diagram
- `phase_counts` — phase count per skill
- `handoff_chains` — `.dev/` artifact producer→consumer chains
- `preplanning_skills` — the pre-planning tributary skills
- `agent_usage_counts` — number of skills using each agent
- `single_use_agents` — agents used by exactly one skill
- `already_inline_candidates` — single-use agents small enough to inline
- `no_agent_skills` — skills that spawn no agents

The full shape of each mapping is documented in that aggregation doc.

After building the mappings, write the two file lists (agents, skills) and all
context blocks **once** to a single run manifest at
`.dev/<today>-discover-plugin-health-context.md` (layout in
`.claude/knowledge/health-discover-aggregation.md`). Phase 3 points each lens at
this manifest instead of re-inlining the file list into every dispatch prompt,
which keeps the 20-lens fan-out small and avoids flooding this session's context.

## Phase 3 — Dispatch

Execute the following state machine in order:

1. **Build `ALL_LENSES` (surface-scoped):** Start with the full lens set, then
   apply the two mirror-image surface bindings:
   - For surface `tooling`, exclude `design-skill-lens-surface-placement` — it
     targets distributed skills and produces only non-actionable Move false
     positives against tooling-surface files.
   - For surface `plugin`, exclude `design-skill-lens-maintainer-handoff` — it
     traces `docs/health/` maintainer chains that exist only on the tooling
     surface, so it produces no actionable findings against distributed skills.

   Net effect: `surface-placement` runs for `plugin` only, and
   `maintainer-handoff` runs for `tooling` only; every other lens runs for both.
   Beyond these formal bindings, several remaining design-skill lenses carry
   reduced semantic signal for tooling skills — see the effective-coverage note
   in `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`.

2. **Filter `remaining_lenses` and dispatch:**
   - If `--resume` is absent: `remaining_lenses = ALL_LENSES`.
   - If `--resume` is present: scan `.dev/` for completed lens output files:

     ```bash
     find .dev -maxdepth 1 -name '*-plugin-health-lens-*.json' 2>/dev/null
     ```

     Parse the `"lens"` field from each `.json` file. Compute
     `remaining_lenses = ALL_LENSES − completed_lenses` (set difference —
     no script). Log: `"Resuming: X lenses already completed, Y remaining"`.

   - If `remaining_lenses` is empty: log all-complete and skip to Phase 4.
     Phase 4 then resolves exactly one of two explicit cases:
     - **case (a) — empty + lens `.json` files on disk:** assemble findings from
       the lens `.json` files already present on disk (a prior session completed
       them).
     - **case (b) — empty + no lens `.json` files on disk:** write a findings
       file containing only `## Raw lens output: _No lenses ran this session._`
       with status `INCOMPLETE`.

   - Otherwise: first confirm the Phase 2 run manifest exists
     (`ls -la .dev/<today>-discover-plugin-health-context.md`); if it is absent,
     halt with an error naming the missing manifest instead of dispatching
     lenses against a nonexistent path. Then dispatch all remaining lenses
     simultaneously (parallel, isolated subagents). Use
     `superpowers:dispatching-parallel-agents` when 3+ lenses remain. Keep each
     dispatch prompt small: point the lens at the Phase 2 run manifest
     (`.dev/<today>-discover-plugin-health-context.md`) for its file list and
     required context fields (per the per-lens table in
     `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`) instead of
     inlining the file list into the prompt. Append the **Finding evidence
     contract** and the **Response format contract** verbatim from
     `profile-al-dev-shared/knowledge/lens-invocation-patterns.md` to every lens
     prompt. Do not paraphrase — copy the canonical text so it cannot drift.

     As each subagent returns, write its findings block to
     `.dev/<today>-plugin-health-lens-<lens-name>.json` with fields `lens`,
     `findings`, `suggestion_count`, and `completed_at` (ISO timestamp).

3. **Check for missing lenses:** Compare returned identifiers against
   `remaining_lenses`. Record any missing lens in a `## Failed lenses`
   section at the top of the findings file:
   `- <lens-name>: not returned (no findings block)`

## Phase 4 — Assemble findings file from disk

For each surface that had lenses run:

1. **Collect all lens output files from `.dev/`:**

   ```bash
   find .dev -maxdepth 1 -name '*-plugin-health-lens-*.json' | sort
   ```

2. **Read and assemble findings:**
   - For each `.json` file, load and extract `"findings"` field
   - Parse any "Failed lenses" entries (returned by failed lens agents)
   - Build findings markdown blocks in order

3. **Write findings file:**
   `docs/health/YYYY-MM-DD-<surface>-findings.md` (substitute today's date and
   `plugin`/`tooling`)

   Structure:

   ```markdown
   ---
   surface: tooling
   dimensions:
     - quality
   source_contract: .claude/knowledge/health-filter-contract.md
   resume_mode: false
   ---

   # <Surface> Findings — YYYY-MM-DD

   ## Raw lens output

   ### <Lens Name> Findings
   [findings block from .dev/ file]

   ---

   ### <Lens Name> Findings
   [next block]

   ---

   ## Failed lenses
   [one line per failed lens, or "None" if all returned results]
   
   ## Resume information
   - Total lenses in scope: N
   - Completed this session: M
   - Completed in prior sessions: P (from --resume)
   - Status: [COMPLETE / INCOMPLETE — call with --resume to finish]
   ```

Use this explicit mapping:

- `design` → design lenses only
- `quality` → quality lenses only
- `naming` → `naming-convention-lens`
- `all` → union of the three concrete dimensions

4. **Clean up disk files after assembly** — run only after the assembled
   findings file has been written in the previous step; if a cleanup command
   fails, skipping it is acceptable (leftover `.dev/` scratch files are
   harmless and never block the run):

   ```bash
   find .dev -maxdepth 1 -name '*-plugin-health-lens-*.json' -delete
   find .dev -maxdepth 1 -name '*-discover-plugin-health-context.md' -delete
   ```

5. **Return to caller:**
   Print the findings file path, line count, and resume status. Then run the
   **backlog guard**:
   `python3 scripts/health_disposition_store.py list-open --status accepted`.
   If the count is non-trivial (≥ 10), also print:

   > ⚠ N open `accepted` rows (oldest `<date>`) carried over from earlier
   > sweeps. They will not all re-appear in this dossier — run
   > `/plan-plugin-findings --backlog` to drain the full backlog.

   This is informational and never blocks the sweep.

6. **Write `.dev/health-loop-state.md`** (schema:
   `.claude/knowledge/health-loop-state-contract.md`):

   - `stage_completed: discover-plugin-health`
   - `completed_at:` today's ISO date
   - `next_command: /report-plugin-health --findings <findings_file_path>`
     (list the first findings path; all paths are in `next_inputs`)
   - `next_inputs:` all findings file paths written this session (one per surface)
   - `fresh_session_recommended: true`
   - `note:` discover phase is context-heavy; start a fresh session before running
     the report to avoid compaction. Phase 0 resumes from the checkpoint on fresh
     invocation — the pointer in `.dev/health-loop-state.md` carries `next_inputs`
     so the new session re-enters at the correct step rather than restarting Phase 1
     from scratch.

7. **Stop — do not auto-invoke `/report-plugin-health`.** Tell the user (as plain
   assistant text, not wrapped in bash/echo): "Findings written to `<path>`. Start a
   **fresh session** and re-run `/audit-plugin-health` (or invoke
   `/report-plugin-health --findings <path>` directly) to generate the dossier —
   the pointer is saved in `.dev/health-loop-state.md`."
