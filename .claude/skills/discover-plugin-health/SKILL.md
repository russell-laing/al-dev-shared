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
  completion status. Before lens dispatch, a deterministic static-lens phase
  (Phase 2.5) runs the non-LLM lenses via scripts/health_static_lenses.py,
  emitting the same findings JSON as the dispatched lenses. The ranked dossier
  is produced separately by /report-plugin-health. Called by /audit-plugin-health; can also
  be run standalone to refresh findings without re-running the report phase, but it requires the same
  pre-conditions as a full audit run. Discovery is via parallel lens dispatch
  (not direct file scanning).
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|naming|all] [--resume] [--since <ref>]"
workflow:
  stage: discover
  invoked-by: both
  repeatable: true
  inputs:
    - docs/skills_map.md
    - docs/agent_map.md
    - profile-al-dev-shared/knowledge/lens-invocation-patterns.md
    - .dev/health-loop-state.md
  outputs:
    - docs/health/<date>-<surface>-findings.md
    - .dev/health-loop-state.md
  next: [report-plugin-health]
---

# Skill: /discover-plugin-health

Discovery phase of the health sweep. Dispatches lenses and writes findings files
that `/report-plugin-health` consumes.

Read `.claude/knowledge/health-filter-contract.md` first and treat it as the
canonical source of truth for surface values, dimension values, defaults,
findings metadata, legacy `unknown`, and resume mismatch handling.

## Maintainer Contracts

Apply `../../knowledge/phase-proof-contract.md` at every phase boundary before
reporting completion or updating `.dev/health-loop-state.md`.

Apply `../../knowledge/dispatch-fallback-contract.md` before every agent
dispatch. Declare the preferred path, run preflight, fall back
deterministically, and log `preferred → outcome → fallback → reason`.

Read `../../knowledge/false-positive-classes.md` before every lens dispatch
wave. Treat any `Suppress` rows in that tracker as known noise context and pass
them into the dispatched prompts so repeated false-positive classes stay in
scope as background information instead of new findings.

## Phase 0 — Parse arguments

- `--surface` ∈ `plugin` | `tooling` | `both` (default `both`)
- `--dimension` ∈ `design` | `quality` | `naming` | `all` (default `all`)
- `--resume` ∈ present | absent (default absent)
- `--since <ref>` ∈ any git ref (commit SHA, branch, tag, or `HEAD~N`); absent by default

**`--since` semantics:** when present, `git diff --name-only <ref>` is used to build
the changed-files set (working-tree-vs-`<ref>` — captures committed, staged, and
unstaged changes in a single pass). To restrict to *committed-only* changes,
pass the two-dot form as the `--since` value, e.g. `--since HEAD~3..HEAD`. The
changed-files set is used to narrow file lists for **scopable lenses only** (see
Phase 1 scopability table); non-scopable lenses always receive the full corpus. The
Phase 2 run manifest is always built from the **full** corpus so cross-file
mappings stay correct.

Bind the `--since` value to `SINCE_REF` immediately after parsing:

```bash
SINCE_REF="<value passed to --since>"   # e.g. HEAD~1, HEAD~3..HEAD, abc1234
```

This variable is used in the Phase 1 normalization snippet below.

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
| --- | --- |
| All `quality-agent-lens-*` | `design-skill-lens-near-duplicates` |
| All `quality-skill-lens-*` | `design-skill-lens-shared-backbone` |
| `quality-agent-multilens` | |
| `quality-skill-multilens` | |
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
# SINCE_REF was bound in Phase 0 arg parsing (see above).
# Build changed-files set as absolute paths.
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

**Dimension gate (token saver):** If `--dimension` is `quality` or `naming`,
**skip the map-parsing subagent entirely** — these dimensions' lenses (the quality
combined readers and the static naming lens) consume no derived context. Write the
Phase 1 globbed agent and skill file lists directly into the run manifest
(`## Agent file list` and `## Skill file list`) and proceed to Phase 2.5.
**When `--since` is active, also write the mandatory `## --since scoped file
lists` section** (scoped agents and skills, derived by intersecting the full
corpus lists against `$CHANGED` — see Phase 1 normalization), exactly as the
non-gated path does. The scoped lists are **not** derived map context, and the
scopable quality/static lenses depend on them; skip only the map-parsing
subagent's derived-context mappings, **never the scoped file lists**. Run the
subagent map-parse described below only for `--dimension design` or
`--dimension all`.

**Dispatch the map parse to a subagent — do not read the maps inline.** The two
documentation maps total ~1800 lines; reading them into the orchestrating session
front-loads context and risks compaction before the ~12-lens fan-out. Instead,
dispatch one subagent (Agent tool) whose task is to read `docs/agent_map.md`
and `docs/skills_map.md` in ITS OWN context, build the derived dispatch
mappings, and write the run manifest (per the layout below). Pass it the full
procedure in `.claude/knowledge/health-discover-aggregation.md`. The subagent
returns only a terse confirmation (manifest path + line count); the maps never
enter this session. If the Agent tool is unavailable, fall back to reading the
maps inline per `../../knowledge/dispatch-fallback-contract.md` and log
`preferred → outcome → fallback → reason`.

The subagent extracts the derived dispatch mappings that the Phase 3 lenses
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
which keeps the ~12-lens fan-out small and avoids flooding this session's context.

**`--since` scoped lists (mandatory when `--since` is active):** When `--since`
is active, append a clearly-labelled section to the manifest immediately after the
full corpus lists:

```markdown
## --since scoped file lists
<!-- These lists contain only files changed since SINCE_REF.
     Phase 3 scopable lenses use these lists instead of the full corpus. -->

### --since scoped agents
<one absolute path per line — empty section if no agent files changed>

### --since scoped skills
<one absolute path per line — empty section if no skill files changed>
```

These scoped lists are derived by intersecting the full corpus lists against
`$CHANGED` (see Phase 1 normalization). The full corpus sections remain untouched.
When `--since` is absent, omit the `## --since scoped file lists` section
entirely.

## Phase 2.5 — Deterministic static lenses (per surface, before dispatch)

Four lenses are fully/mostly deterministic and are produced by a single Python
pass instead of LLM agents: `naming-convention-lens`,
`quality-agent-lens-structure`, `quality-skill-lens-structure`, and
`design-agent-lens-tool-hygiene`. They write the **same** per-lens
`.dev/<today>-plugin-health-lens-<lens-name>.json` artifacts the LLM lenses
write (schema `{lens, findings, suggestion_count, completed_at}`), so Phase 4
assembly and `--resume` treat them identically to agent findings.

For each requested surface, run the static runner **once for that surface**,
immediately before that surface's Phase 3 dispatch:

```bash
python3 scripts/health_static_lenses.py \
  --surface <plugin|tooling> \
  --dimension <design|quality|naming|all> \
  --date <today> \
  [--since "$SINCE_REF"]
```

**Load-bearing ordering and serialization:**

- The lens-output filename carries **no surface token**, so the script must be
  invoked with a **single** `--surface`, **never `both`**. Discover already
  processes surfaces one at a time (Phase 1→4 for `plugin` completes — including
  the Phase 4 `.dev/` cleanup — before `tooling` starts), so calling the script
  once per surface inside that per-surface loop keeps the surface-less JSON
  filenames from colliding.
- Phase 2.5 runs **before** Phase 3 step 2's empty-`remaining_lenses`
  short-circuit. This matters most for `--dimension naming`: after conversion the
  only naming lens is the (removed) `naming-convention-lens`, so
  `remaining_lenses` is empty and **zero LLM lenses dispatch** — the script having
  already written its naming JSON in Phase 2.5 is what makes a `--dimension
  naming` run produce findings, assembled by Phase 4 case (a).
- Phase 2.5 **always re-runs on `--resume`** (it is cheap and idempotent —
  re-running overwrites its own JSON). Phase 4 cleanup deletes the `.dev/` lens
  JSONs at the end of a completed run, so a fresh resume after interruption must
  re-emit them. The script honors `--since` for all four checks (they are all
  classified scopable; see the Phase 1 scopability table), using the same
  absolute-vs-repo-relative path normalization as Phase 1.

**Corpus asymmetry:** The static runner examines all non-archived skills regardless
of `workflow:` block. LLM lenses examine only workflow:-contracted skills. A
structural finding on a non-contracted skill (one without a `workflow:` block in its
frontmatter) is valid but should be tagged `[non-contracted]` in the findings file and
verified for relevance before planning, since no LLM lens reviewed that skill's logic.

## Phase 3 — Dispatch

Execute the following state machine in order:

1. **Build `ALL_LENSES` (surface-scoped):** Start with the full LLM lens set
   (the 13 lens agents on disk in `.claude/agents/` — the four deterministic
   lenses `naming-convention-lens`, `quality-agent-lens-structure`,
   `quality-skill-lens-structure`, and `design-agent-lens-tool-hygiene` are
   **not** in this set; they are produced by the Phase 2.5 static runner and are
   never dispatched as agents). Then apply the two mirror-image surface bindings:
   - For surface `tooling`, exclude `design-skill-lens-surface-placement` — it
     targets distributed skills and produces only non-actionable Move false
     positives against tooling-surface files.
   - For surface `plugin`, exclude `design-skill-lens-maintainer-handoff` — it
     traces `docs/health/` maintainer chains that exist only on the tooling
     surface, so it produces no actionable findings against distributed skills.

   Net effect: `surface-placement` runs for `plugin` only, and
   `maintainer-handoff` runs for `tooling` only; every other LLM lens runs for
   both. Beyond these formal bindings, tooling skills carry reduced semantic signal
   unless they serve >3 active use cases in the current corpus. Apply design lenses
   to these skills to identify ambiguity and scope drift.

   **Quality-dimension bundling:** When the requested dimension includes
   `quality`, the four agent-quality lenses and four skill-quality lenses are NOT
   dispatched individually. Instead dispatch two combined readers —
   `quality-agent-multilens` (against the agent file list) and
   `quality-skill-multilens` (against the skill file list). Each reads its corpus
   once and returns four `<!-- lens: … -->` blocks. The design lenses are
   unchanged. (Net: a `--dimension quality` run dispatches 2 LLM agents, not 8; a
   `--dimension all` run dispatches 2 combined + the design lenses.)

   **Response format for combined readers.** A combined reader replies in its own
   four-block Output Format — one `<!-- lens: … -->` marker per lens, each clean
   lens emitting its heading + `_No issues found._`. It must emit **all four
   markers even when every lens is clean**: a marker-less "no issues" reply makes
   the Phase 4 splitter raise `ValueError` and aborts the (common) all-clean
   sweep. So when appending the canonical **Response format contract** to a
   combined reader's prompt (the "Append … verbatim to every lens prompt"
   instruction later in Phase 3), use the combined-reader variant from
   `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`, **not** the
   singular "reply with exactly the lens heading" no-issues clause, which would
   suppress the markers.

   **Dispatch vs. on-disk counts:** 13 LLM lens agents exist on disk (11 design +
   2 combined quality). For the quality dimension, the 2 combined readers replace
   what were 8 individual lenses and still produce 8 per-lens result-sets (via the
   Phase 4 split). The four deterministic lenses run as the Phase 2.5 script. The
   on-disk 13 is the count `scripts/validate_lens_agents.py` asserts.

2. **Filter `remaining_lenses` and dispatch:**
   - If `--resume` is absent: `remaining_lenses = ALL_LENSES`.
   - If `--resume` is present: scan `.dev/` for completed lens output files:

     ```bash
     find .dev -maxdepth 1 -name '*-plugin-health-lens-*.json' 2>/dev/null
     ```

     Parse the `"lens"` field from each into `completed_child_lenses`. Then
     **collapse the child quality lenses into their combined reader** before the
     set difference, using this fixed mapping:

     - `quality-agent-multilens` ⇐ all of `quality-agent-lens-{bloat,clarity,description,name-fit}`
     - `quality-skill-multilens` ⇐ all of `quality-skill-lens-{bloat,clarity,description,name-fit}`

     A combined reader is **completed** iff *all four* of its child-lens JSONs are
     present, **or** its
     `.dev/<today>-plugin-health-multilens-<agent|skill>.raw.md` is present **and
     passes the same completeness check used at write time** (all four expected
     markers, or the explicit all-clean signature). A *partial* set of child JSONs,
     or a malformed/truncated `.raw.md`, ⇒ the reader is **not** complete and is
     re-dispatched (its child JSONs are overwritten on re-run, which is safe).

     Build `completed_lenses` = every non-quality lens name in
     `completed_child_lenses`, plus each combined reader completed by the rule
     above. Compute `remaining_lenses = ALL_LENSES − completed_lenses` (set
     difference — no script). Log: `"Resuming: X lenses already completed, Y remaining"`.

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
     lenses against a nonexistent path. Then dispatch the remaining lenses in
     **bounded waves of at most 5 concurrent subagents** — never all ~12 at once,
     which overruns the session's parallel-dispatch limit (two lenses were lost to
     this in production). Dispatch a wave, wait for every lens in it to return and
     write its `.json`, then start the next wave. Use
     `superpowers:dispatching-parallel-agents` for each wave of 3+ lenses. Because
     each lens writes its own `.dev/<today>-plugin-health-lens-<lens>.json` as it
     returns, an interrupted run resumes cleanly via `--resume` (Phase 3 step 2 set
     difference). Keep each dispatch prompt small: point the lens at the Phase 2 run manifest
     (`.dev/<today>-discover-plugin-health-context.md`) for its context fields (per
     the per-lens table in
     `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`).

     **File list selection per lens (load-bearing when `--since` is active):**
     For each lens in `remaining_lenses`, choose the file list to supply in the
     dispatch prompt as follows:

     - **Scopable lens** (see Phase 1 scopability table) **and `--since` active:**
       supply the `--since` scoped list from the `## --since scoped file lists`
       section of the run manifest. If the scoped list for that lens's object type
       (agents or skills) is **empty**, **skip** dispatching that lens and log
       `<lens-name>: skipped (no changed files in scope)`. Do not dispatch against
       an empty list.
     - **Non-scopable lens** (`near-duplicates`, `shared-backbone`, `handoff-gaps`,
       `preplanning`) **or `--since` absent:** supply the full corpus list from the
       run manifest.

     This ensures scopable lenses see only the narrowed set while non-scopable
     lenses always run against the full corpus — satisfying acceptance test A.V.1.

     Append the **Finding evidence contract** and the **Response format contract**
     verbatim from `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`
     to every lens prompt. Do not paraphrase — copy the canonical text so it cannot
     drift.

     **Snippet self-verification (in-lens, confirm-only at orchestrator):** Each
     lens already reads its subject files in its own context, so snippet
     verification belongs there — not in costly orchestrator re-`grep` round-trips.
     Add this instruction to every lens dispatch prompt:

    > Before emitting any finding with a `snippet:` block, confirm the
    > `snippet.text` appears verbatim at the cited `snippet.file:line` in the file
    > you already read. If it does not, drop the `snippet:` field (or the finding)
    > — do not emit an unverified snippet.

     Also include the current suppressed false-positive classes from
     `../../knowledge/false-positive-classes.md` as known noise context for the
     lens so the sweep does not re-litigate already-classified patterns.

     The orchestrator does **not** re-`grep` each snippet. It trusts the lens
     self-verification and lets the report-phase evidence gate
     (`verify-health-finding` in evidence mode) act as the backstop for any snippet
     that slips through. This removes one grep round-trip per snippet finding from
     the orchestrating session.

     As each subagent returns, write its findings block to
     `.dev/<today>-plugin-health-lens-<lens-name>.json` with fields `lens`,
     `findings`, `suggestion_count`, and `completed_at` (ISO timestamp).

     **Exception — combined multi-lens readers.** For `quality-agent-multilens`
     and `quality-skill-multilens` do **not** write a single
     `…-lens-<reader>.json`. These readers return four `<!-- lens: … -->` blocks,
     not one lens block. Instead persist the raw return to a **temporary** path
     first, validate it, then rename it atomically to
     `.dev/<today>-plugin-health-multilens-<agent|skill>.raw.md` (`agent` for
     `quality-agent-multilens`, `skill` for `quality-skill-multilens`). Treat the
     raw return as valid only when one of these holds:

     - it contains all four expected `<!-- lens: … -->` markers for that object
       type, or
     - it is the explicit all-clean form for that object type: no markers,
       contains `_No issues found._`, and contains no `- **` findings bullets.

     If neither condition holds, treat the dispatch as failed, record the reader
     under `## Failed lenses`, and do **not** leave a stable `.raw.md` on disk.
     Phase 4 step 0 splits a validated `.raw.md` into the four child-lens JSONs
     the rest of assembly and `--resume` consume.

3. **Check for missing lenses:** Compare returned identifiers against
   `remaining_lenses`. Record any missing lens in a `## Failed lenses`
   section at the top of the findings file:
   `- <lens-name>: not returned (no findings block)`

## Phase 4 — Assemble findings file from disk

For each surface that had lenses run:

0. **Split combined multi-lens returns.** For each
   `.dev/<today>-plugin-health-multilens-<agent|skill>.raw.md` present (written by
   the Phase 3 step 2 combined-reader exception, including any left by an
   interrupted prior session), run:

   ```bash
   python3 scripts/split_multilens_findings.py \
     --input .dev/<today>-plugin-health-multilens-<agent|skill>.raw.md \
     --date <today> --out-dir .dev
   ```

   This produces the four per-lens `.dev/<today>-plugin-health-lens-<lens>.json`
   files for that object type. After this step the `.dev/` directory contains the
   same eight quality lens JSONs a pre-bundling run produced, so the rest of
   Phase 4 assembly and `--resume` are unchanged. Then delete each consumed
   `.raw.md`.

   **All-clean fallback (defensive).** If a `.raw.md` contains no
   `<!-- lens: … -->` markers but does contain `_No issues found._` (a reader that
   reported all-clean without markers despite the Step 1 contract), do **not**
   abort: write the four empty-block child JSONs for that object type directly —
   `quality-<agent|skill>-lens-{bloat,clarity,description,name-fit}`, each with
   `findings` = the heading + `_No issues found._`, `suggestion_count: 0`, and
   `completed_at` = the same ISO timestamp used for the surrounding Phase 4
   assembly — instead of invoking the splitter (which raises `ValueError` on a
   marker-less input by design).

   **Malformed raw fallback.** If a `.raw.md` is present but matches neither the
   four-marker form nor the explicit all-clean signature, do **not** silently
   assemble partial data. Record the combined reader in `## Failed lenses`, delete
   the malformed `.raw.md`, and leave the corresponding quality reader in the
   "not completed" state for the next `--resume` run.

1. **Collect all lens output files from `.dev/`:**

   ```bash
   find .dev -maxdepth 1 -name '*-plugin-health-lens-*.json' | sort
   ```

2. **Assemble the findings file deterministically.** Do **not** read the lens
   JSONs back into this session and re-emit them. Run the assembler, which reads
   `.dev/<today>-plugin-health-lens-*.json`, orders the blocks canonically, and
   writes the findings file with frontmatter, a `<!-- lens: <name> -->` marker per
   block, the `## Failed lenses` section, and the `## Resume information` block:

   ```bash
   python3 scripts/assemble_health_findings.py assemble \
     --lens-dir .dev \
     --date <today> \
     --surface <plugin|tooling> \
     --dimensions <comma-separated concrete dimensions for this run> \
     --failed-lenses <comma-separated failed lens names, or none> \
     --total-lenses <N> \
     --completed-session <M> \
     --completed-prior <P> \
     --skipped <S> \
     --out docs/health/<today>-<surface>-findings.md
   ```

   Pass the `--failed-lenses` and the four count values from the Phase 3 missing-lens
   check and the `--resume` set difference. The assembler computes `Status:
   COMPLETE` iff `completed-session + completed-prior + skipped >= total-lenses`.

3. **Confirm the file was written** (the assembler prints its path on success):

   ```bash
   ls -la docs/health/<today>-<surface>-findings.md && wc -l docs/health/<today>-<surface>-findings.md
   ```

If `scripts/assemble_health_findings.py` is missing or errors, fall back to the
manual assembly per `../../knowledge/dispatch-fallback-contract.md` — read each
`.dev/<today>-plugin-health-lens-*.json` **whose lens name belongs to this run's
`--dimensions`** (ignore same-date JSONs from other dimensions, e.g. a stale
design lens left by an interrupted run), concatenate the `findings` fields in the
canonical order with a `<!-- lens: <name> -->` marker and a `---` between blocks,
**uniquifying any duplicate `###` heading by appending an object-type suffix
(`(agents)`/`(skills)`) so the file passes markdownlint MD024**, and write the
same frontmatter + Failed-lenses + Resume-information structure — and log
`preferred → outcome → fallback → reason`.

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
   find .dev -maxdepth 1 -name '*-plugin-health-multilens-*.raw.md' -delete
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
