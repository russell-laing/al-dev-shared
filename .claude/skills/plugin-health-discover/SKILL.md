---
name: plugin-health-discover
description: >-
  Discovery phase of the plugin health sweep. Builds file lists, aggregates
  context from documentation maps, dispatches all design, quality, and naming
  lenses,
  and writes structured findings to docs/health/YYYY-MM-DD-<surface>-findings.md.
  Called by /plugin-health-audit; can also be run standalone to refresh findings
  without re-running the report phase.
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|all] [--resume]"
---

# Skill: /plugin-health-discover

Discovery phase of the health sweep. Dispatches lenses and writes findings files
that `/plugin-health-report` consumes.

## Phase 0 — Parse arguments

- `--surface` ∈ `plugin` | `tooling` | `both` (default `both`)
- `--dimension` ∈ `design` | `quality` | `all` (default `all`)
- `--resume` ∈ present | absent (default absent)

Surface → directory mapping:

- `plugin` → `profile-al-dev-shared/`
- `tooling` → `.claude/`

### Cadence guard (per requested surface)

Re-sweeping before the prior dossier is dispositioned mostly re-measures
known findings at full lens cost. Before dispatching:

```bash
# Most recent dossier for the surface
ls -t /Users/russelllaing/al-dev-shared/docs/health/*-<surface>-health.md 2>/dev/null | head -1
```

If a dossier exists, check whether `docs/health/dispositions.md` contains
any rows dated on or after that dossier's date. If it does not (or the
ledger is absent), warn:

```text
The latest <surface> dossier (<date>) has no recorded dispositions.
A new sweep will largely re-discover its open findings. Record
accept/decline/fixed rows via /record-health-dispositions first, or
confirm to sweep anyway.
```

Then branch explicitly:

- User confirms → proceed to Phase 1.
- User declines, or gives no clear confirmation → stop. Report "Sweep not
  dispatched — record dispositions via `/record-health-dispositions` and
  re-run." Do not dispatch any lens.

### Stale-open check (per requested surface)

An `accepted` ledger row whose object has since changed in git is often
already implemented but never flipped to `fixed` (the closure write-back
rule in `/record-health-dispositions` was skipped). Before dispatching:

```bash
python3 scripts/check_ledger_staleness.py
```

For each `STALE-OPEN` row in the output, report before dispatch: "Row
`<object>` accepted <row-date> — object changed since (<commit>); possibly
already implemented. Verify and flip the ledger row before sweeping, or
the sweep may re-rank a fixed item." This check warns only; it never
blocks the sweep on its own.

Skip the guard and the stale-open check when `--resume` is present
(resuming an interrupted sweep is not a new sweep).

## Phase 1 — Build file lists (per requested surface)

For each requested surface, glob both object types:

```bash
# plugin surface
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" | sort
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills -name "SKILL.md" | sort
# tooling surface
find /Users/russelllaing/al-dev-shared/.claude/agents -name "*.md" | sort
find /Users/russelllaing/al-dev-shared/.claude/skills -name "SKILL.md" ! -path "*/archived/*" | sort
```

Keep the agent list and skill list separate — different lenses target each.

## Phase 2 — Pre-dispatch aggregation

Extract context from documentation maps before dispatching lenses.

**Read and parse `docs/al-dev-agent-map.md`:**

- Extract the Agent Catalog table
- For each agent row: extract agent name, model, tools list, and "Spawned by" field
- Build: `tool_inventory`, `model_assignments`, `caller_map`
- "Spawned by" may contain comma-separated names or "(none found)" — treat the latter as empty list

**Read and parse `docs/al-dev-skills-map.md`:**

- Extract the Layer 1 diagram block → `layer1_diagram_content`
- For each skill section: extract phase count, agent references, output files
- Build: `phase_counts`, `handoff_chains`, `preplanning_skills` (skills with `-.->` arrows)

**Compute derived mappings:**

- `agent_usage_counts`: agent → count of spawning skills
- `single_use_agents`: agents where `agent_usage_counts == 1`
- `already_inline_candidates`: filter of `single_use_agents`
- `no_agent_skills`: skills with zero spawned agents

## Phase 3 — Resume & dispatch

### 3.1 Resume detection (if --resume flag)

If invoked with `--resume` flag:

1. **Scan `.dev/` directory for existing lens output files:**

   ```bash
   ls -1 .dev/*-plugin-health-lens-*.json 2>/dev/null
   ```

2. **Extract completed lens names:**
   - For each `.json` file, parse the `"lens"` field
   - Build `completed_lenses` set

3. **Filter remaining lenses:**
   - `remaining_lenses = [l for l in ALL_LENSES if l not in completed_lenses]`
   - Log: `"Resuming: X lenses already completed, Y remaining"`
   - If `remaining_lenses` is empty, log: `"Resuming: all lenses already complete; skipping dispatch and assembling findings from disk."`

If NOT invoked with `--resume`:

- `remaining_lenses = ALL_LENSES`

### 3.1b Surface-scoped lenses (mandatory filter)

`ALL_LENSES` is surface-dependent. `design-skill-lens-surface-placement`
exists solely to find **distributed** skills that belong in the repo-local
maintainer surface; aimed at files already in the maintainer surface it can
only emit false "Move" findings (9 per sweep on 2026-06-03 and 2026-06-04).

- Surface `plugin` → all lenses.
- Surface `tooling` → exclude `design-skill-lens-surface-placement` from
  `ALL_LENSES` before computing `remaining_lenses`.

### 3.2 Dispatch lenses in-session (parallel, isolated subagents)

If `remaining_lenses` is empty, skip dispatch and proceed to Phase 4.

Dispatch the `remaining_lenses` as parallel subagents in this session — one
Agent per lens, each an isolated context. Use
`superpowers:dispatching-parallel-agents` when 3+ lenses remain. For each
lens, pass only the context fields it requires (per
`profile-al-dev-shared/knowledge/lens-invocation-patterns.md`): the agent
list or skill list from Phase 1 and the relevant aggregated mappings from
Phase 2.

Each lens subagent returns a findings block. As each returns, write it to
`.dev/<today>-plugin-health-lens-<lens-name>.json` with fields `lens`,
`findings`, `suggestion_count`, and `completed_at` (ISO timestamp), where
`<today>` is the current date used for every `.dev/` output filename.

### 3.3 Confirm returns (check for missing lenses)

Compare the lens identifiers that returned a findings block against
`remaining_lenses`. Any lens in `remaining_lenses` that did not return is a
missing lens.

Record missing lenses in a `## Failed lenses` section at the top of the
findings file, one per line:
`- <lens-name>: not returned (no findings block)`

## Phase 4 — Assemble findings file from disk

For each surface that had lenses run:

1. **Collect all lens output files from `.dev/`:**

   ```bash
   ls -1 .dev/*-plugin-health-lens-*.json | sort
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

4. **Clean up disk files after assembly:**

   ```bash
   rm -f .dev/*-plugin-health-lens-*.json
   ```

5. **Return to caller:**
   Print the findings file path, line count, and resume status.
