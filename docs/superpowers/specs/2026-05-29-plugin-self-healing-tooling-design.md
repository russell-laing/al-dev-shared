# Self-Healing Maintainer Tooling — Design

**Date:** 2026-05-29
**Status:** Approved (brainstorming complete; pending implementation plan)

## Purpose

Improve the tooling used to maintain this repo so that it (a) follows modern
best practice, (b) names its tools and its outputs logically and consistently,
(c) focuses improvement effort on `profile-al-dev-shared` while staying
harness-agnostic, (d) generates reviewable artifacts that drive improvement
suggestions, and (e) makes the relationships and workflow paths between plugin
tools visible.

There is no single motivating defect. This is a deliberate modernization and
consolidation of the maintainer surface plus a standing, suggestions-only
self-healing loop.

## Background — current state

Maintainer tooling lives in `.claude/` and `scripts/`, separate from the
distributed plugin surface in `profile-al-dev-shared/`.

- **11 maintainer skills** (`.claude/skills/`): `review-skill-map`,
  `review-agent-map`, `analyze-skill-design`, `analyze-agent-design`,
  `audit-skill-quality`, `audit-agent-quality`, `audit-knowledge-quality`,
  `plan-map-changes`, `projection-sync`, `align-harness-repos`,
  `plugin-health-daemon`.
- **20 lens agents** (`.claude/agents/`): `design-lens-*` (5, target agents),
  `design-skill-lens-*` (5, target skills), `quality-lens-*` (5, target
  agents), `quality-skill-lens-*` (5, target skills). Each is haiku,
  read-only, single-purpose, and emits a findings block.
- **Output docs** (`docs/`): `al-dev-plugin-map.md`, `al-dev-agent-map.md`,
  `al-dev-skill-quality.md`, `al-dev-agent-quality.md`,
  `al-dev-knowledge-quality.md`, `al-dev-workflow-diagrams.md`.
- **Validator scripts** (`scripts/`): `validate_harness_neutrality.py`,
  `validate-lens-agents.py`, `validate-knowledge-quality.py`,
  `validate_artifact_contracts.py`, `generate-agent-projections.py`,
  `plugin-health-daemon.sh`.

Two gaps motivated this design:

1. The lens agents are hardcoded to read `profile-al-dev-shared/`. The
   maintainer tooling in `.claude/` is never audited — the tools that heal the
   plugin do not get healed.
2. `plugin-health-daemon` auto-fixes and opens PRs, which conflicts with a
   review-first (suggestions-only) workflow. It is not in use.

## Decisions

| Decision | Choice |
|---|---|
| Target of the work | One-time cleanup **then** standing self-healing |
| Audit scope | Both surfaces (`profile-al-dev-shared` + `.claude/`), **separate reports** |
| Visualization | New, richer auto-generated dependency graph + workflow overlays |
| Autonomy | **Suggestions only** — nothing is auto-edited |
| Naming | Derive a documented convention, then rename to match (breaking renames OK, references updated) |
| `plugin-health-daemon` | **Removed** (skill + script + doc mentions) — not in use |

## Architecture

The work is two phases, sequenced so renames land before the loop flags
against the new convention.

```
PHASE 1 — Cleanup (one-time, plan-driven)
  1. Write naming-convention reference doc (tool names + output filenames)
  2. Rename the 10 agent lenses to a symmetric convention + update references
  3. Modernize maintainer tooling to best practice (dogfood quality lenses on .claude/)
  4. Remove plugin-health-daemon (skill + script + doc mentions)

PHASE 2 — Self-healing system (standing)
  5. New orchestrator skill  /plugin-health  (suggestions-only)
  6. Richer visualization generator → docs/al-dev-plugin-graph.md
  7. New naming-convention lens (flags drift on every run)
```

### Key structural decision — lenses take a file list, not a target parameter

A maintainer agent file is *structurally* an agent file; a maintainer skill is
structurally a skill. The existing agent-vs-skill lens split therefore already
fits both surfaces. The orchestrator feeds each lens a **different file list**
(profile dir vs `.claude/` dir) and writes a **separate dossier per surface**.
"Audit both, separate reports" falls out with no change to lens internals.

```
/plugin-health
 ├─ surface = profile-al-dev-shared/  → docs/health/YYYY-MM-DD-plugin-health.md
 └─ surface = .claude/ (maintainer)   → docs/health/YYYY-MM-DD-tooling-health.md
```

Consequence: improvement *suggestions* stop being scattered across map
"Observations" sections and `*-quality.md` docs. They consolidate into one
ranked dossier per surface. The maps and graph stay focused purely on structure
and visualization, kept accurate by `review-*` + the graph generator.

## Components

### 1. Naming convention (Phase 1 — signed off first)

```
TOOLS
  Maintainer skills:  {verb}-{object}-{aspect}
      verb   ∈ review | analyze | audit | plan | sync | …
      object ∈ skill | agent | knowledge | map | plugin
    e.g.  audit-skill-quality, review-agent-map        (already conform)

  Lens agents:  {dimension}-{object}-lens-{aspect}
      dimension ∈ design | quality
      object    ∈ agent | skill
    e.g.  design-agent-lens-tool-hygiene, quality-skill-lens-bloat

OUTPUTS
  Living docs (overwritten in place, no date):  al-dev-{object}-{kind}.md
      e.g. al-dev-plugin-map.md, al-dev-skill-quality.md, al-dev-plugin-graph.md
  Point-in-time artifacts (dated):  {dir}/YYYY-MM-DD-{surface}-{kind}.md
      e.g. docs/health/2026-05-29-plugin-health.md
```

The one substantive inconsistency this fixes: agent lenses omit their object
word (`design-lens-tool-hygiene` vs `design-skill-lens-complexity`), so they do
not sort or read symmetrically against the skill lenses.

### 2. Lens renames (Phase 1)

- `design-lens-*` (5) → `design-agent-lens-*`
- `quality-lens-*` (5) → `quality-agent-lens-*`
- Skill lenses already conform — no change.

Reference updates land in: `analyze-agent-design` and `audit-agent-quality`
skills, `validate-lens-agents.py` and its test. (`docs/superpowers/` plans and
specs that mention old names are historical and are not rewritten.)

### 3. Best-practice modernization (Phase 1)

Rather than invent a checklist, run the `quality-*` lenses against `.claude/`
itself and fix what they surface (structure gaps, bloat, clarity, description
drift, name-fit). This is Phase 2's loop pointed at the maintainer surface, so
the cleanup doubles as the system's first real run.

### 4. `/plugin-health` orchestrator skill (Phase 2)

Suggestions-only entry point.

```
/plugin-health [--surface profile|maintainer|both] [--dimension design|quality|all]
  for each requested surface:
    1. Build file lists: glob agents (*.md) + skills (*/SKILL.md) in that dir
    2. Dispatch lenses in parallel (Agent tool), passing file_list:
         agents  → design-agent-lens-* + quality-agent-lens-*
         skills  → design-skill-lens-* + quality-skill-lens-*
         + naming-convention-lens (both objects)
    3. Collect findings blocks; a malformed/failed lens is recorded as
       "lens X: no result" — never aborts the run
    4. Rank: High → Medium → Low, grouped by dimension then object
    5. Write ONE dossier for the surface
  Always (profile surface): run generate-plugin-graph.py → al-dev-plugin-graph.md
```

The loop is: `/plugin-health` (detect) → dossier (review) → `plan-map-changes`
(rubber-duck accepted items) → plan → execute. Nothing is auto-edited.

### 5. Dossier format (Phase 2)

`docs/health/YYYY-MM-DD-<surface>-health.md`:

```markdown
# <Surface> Health — YYYY-MM-DD
## Summary            ← counts by severity & dimension; top 5 ranked actions
## Design suggestions ← Atomise/Merge/Trim/Split/Align… each: finding | rationale | fix
## Quality findings   ← Bloat/Clarity/Structure/Name-fit/Description, with file:line
## Naming violations  ← actual name vs convention-expected name
## Graph deltas       ← orphans, dead links, off-path skills (profile surface only)
```

### 6. Visualization generator (Phase 2)

`scripts/generate-plugin-graph.py` → `docs/al-dev-plugin-graph.md`.
Deterministic (structured grep), not agent-driven; `analyze-skill-design`
already proves the extraction patterns. Reads `markdown/md-mermaid-helper.md`
conventions before emitting Mermaid.

Extracted edges:

```
skill → agent      "al-dev-shared:<agent>" / Agent dispatch in SKILL.md
skill → skill       skill invocations (e.g. plan → develop)
skill → knowledge   ../../knowledge/<file>.md refs
agent → knowledge   knowledge refs in agent bodies
skill → artifact    .dev/ output filenames the skill writes
```

Three rendered views:

```
1. Dependency graph (Mermaid)   — all nodes/edges, color-coded by type
2. Workflow-path overlays       — the 3 flows (ticket / dev-spine / direct-fix)
                                  highlighted as subgraphs
3. Health callouts (text+table) — orphans & dead links:
     • agents spawned by no skill
     • knowledge files referenced by nothing
     • skills not on any workflow path
     • refs pointing at missing files
```

The orphan/dead-link output is the same data the dossier summarizes under
"Graph deltas" — the generator is the single source for both the picture and
those findings.

**Scope:** the graph targets `profile-al-dev-shared` only (goal #5 is about
plugin tools relating to each other). The maintainer surface gets findings in
its dossier but not the workflow-overlay view; its "workflow" is just the audit
loop and does not warrant the same treatment.

### 7. `naming-convention-lens` agent (Phase 2)

New haiku, read-only lens. Reads a file list + the convention doc, flags any
tool name or output path that violates the documented pattern, and emits the
standard findings-block shape so the orchestrator aggregates it identically.
This is what prevents naming drift after the Phase 1 renames.

## Error handling

Suggestions-only bounds the failure modes — the worst case is a stale or
partial report, never a bad edit.

```
- Lens returns malformed/empty block  → dossier records "lens X: no result", run continues
- Graph generator hits a parse error   → writes partial graph + an "incomplete" banner, exits 0
- No findings for a surface             → dossier still written, "No issues found" per section
- Nothing is ever auto-edited           → no source file is mutated by the loop
```

## Testing

```
- validate-lens-agents.py extended to assert the renamed lens names + the new naming lens
- scripts/tests: graph generator fixture (a tiny fake plugin dir) → asserts orphan/dead-link detection
- A convention-checker: assert every file in .claude/agents + .claude/skills matches the naming doc
- /plugin-health dry-run on .claude/ → confirms two-surface separation & dossier sections present
- Reuse the libexpat inline-test fallback (per CLAUDE.md) if pytest misbehaves
```

## Deliverables

1. Naming-convention reference doc + the 10 lens renames & reference updates
2. `plugin-health-daemon` removed (skill + script + doc mentions in `CLAUDE.md`
   and `al-dev-plugin-map.md`)
3. Maintainer tooling modernized via dogfooded quality lenses
4. `/plugin-health` orchestrator skill → two per-surface dossiers
5. `scripts/generate-plugin-graph.py` → `docs/al-dev-plugin-graph.md`
6. `naming-convention-lens` agent
7. Tests + validator extensions

## Harness-neutrality note

All artifacts written to the shared surface or `.dev/`-style outputs must stay
harness-agnostic (per `CLAUDE.md` output-boundary rule). The maintainer tooling
itself may remain Claude-specific, but the dossiers, the graph doc, and the
naming-convention doc must use generic vocabulary. Run
`validate_harness_neutrality.py` on any shared-surface output.
