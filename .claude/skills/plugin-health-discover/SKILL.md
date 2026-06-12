---
name: plugin-health-discover
description: >-
  Discovery phase of the plugin health sweep. Builds file lists, aggregates
  context from documentation maps, dispatches design, quality, and naming lenses
  (surface-scoped — one design lens excluded for the tooling surface; see Phase 3),
  and writes RAW (unranked) lens findings to
  docs/health/YYYY-MM-DD-<surface>-findings.md. The ranked dossier is produced
  separately by /plugin-health-report. Called by /plugin-health-audit; can also
  be run standalone to refresh findings without re-running the report phase, but it requires the same
  pre-conditions as a full audit run.
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|naming|all] [--resume]"
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
  next: [plugin-health-report]
---

# Skill: /plugin-health-discover

Discovery phase of the health sweep. Dispatches lenses and writes findings files
that `/plugin-health-report` consumes.

Read `.claude/knowledge/health-filter-contract.md` first and treat it as the
canonical source of truth for surface values, dimension values, defaults,
findings metadata, legacy `unknown`, and resume mismatch handling.

## Phase 0 — Parse arguments

- `--surface` ∈ `plugin` | `tooling` | `both` (default `both`)
- `--dimension` ∈ `design` | `quality` | `naming` | `all` (default `all`)
- `--resume` ∈ present | absent (default absent)

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

### Derived dispatch context

**Compute derived mappings:**

- `agent_usage_counts`: agent → count of spawning skills
- `single_use_agents`: agents where `agent_usage_counts == 1`
- `already_inline_candidates`: filter of `single_use_agents`
- `no_agent_skills`: skills with zero spawned agents

## Phase 3 — Dispatch

Execute the following state machine in order:

1. **Build `ALL_LENSES` (surface-scoped):** Start with the full lens set.
   For surface `tooling`, exclude `design-skill-lens-surface-placement` — it
   targets distributed skills and produces only non-actionable Move false
   positives against tooling-surface files. For surface `plugin`, use all
   lenses unchanged.

2. **Apply `--resume` filter:** If `--resume` is present, scan `.dev/` for
   completed lens output files and build `completed_lenses`:

   ```bash
   ls -1 .dev/*-plugin-health-lens-*.json 2>/dev/null
   ```

   Parse the `"lens"` field from each `.json` file.
   Compute `remaining_lenses` as the lenses in `ALL_LENSES` that are not in
   `completed_lenses` (set difference). This is a filtering step you perform
   directly — no script is invoked here.
   Log: `"Resuming: X lenses already completed, Y remaining"`. If
   `remaining_lenses` is empty, log all-complete and skip to Phase 4.
   If `--resume` is absent, `remaining_lenses = ALL_LENSES`.

3. **Dispatch remaining lenses simultaneously (parallel, isolated subagents):**
   If `remaining_lenses` is empty, skip dispatch and proceed to Phase 4.
   Use `superpowers:dispatching-parallel-agents` when 3+ lenses remain.
   Dispatch one Agent per lens; pass only the context fields it requires (per
   `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`): agent/skill
   list from Phase 1 and relevant aggregated mappings from Phase 2. As each
   subagent returns, write its findings block to
   `.dev/<today>-plugin-health-lens-<lens-name>.json` with fields `lens`,
   `findings`, `suggestion_count`, and `completed_at` (ISO timestamp).

4. **Check for missing lenses:** Compare returned identifiers against
   `remaining_lenses`. Record any missing lens in a `## Failed lenses`
   section at the top of the findings file:
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

4. **Clean up disk files after assembly:**

   ```bash
   rm -f .dev/*-plugin-health-lens-*.json
   ```

5. **Return to caller:**
   Print the findings file path, line count, and resume status.
