---
name: plugin-health
description: >-
  Suggestions-only health sweep of the al-dev-shared plugin surfaces. Dispatches
  design + quality + naming lenses with a per-surface file list, ranks findings,
  and writes one dossier per surface to docs/health/. Always refreshes the
  dependency graph for the plugin surface. Never auto-edits source. Triggers on:
  "plugin health", "health sweep", "audit the plugin", "check plugin health".
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|all]"
---

# Skill: /plugin-health

Standing self-healing entry point. Detects drift across both plugin surfaces and
consolidates suggestions into one ranked dossier per surface. Nothing is
auto-edited — the loop is: `/plugin-health` (detect) → dossier (review) →
`/plan-map-changes` (rubber-duck accepted items) → plan → execute.

## Phase 0 — Parse arguments

- `--surface` ∈ `plugin` | `tooling` | `both` (default `both`)
- `--dimension` ∈ `design` | `quality` | `all` (default `all`)

Surface → directory mapping:
- `plugin` → `profile-al-dev-shared/` → dossier `docs/health/YYYY-MM-DD-plugin-health.md`
- `tooling` → `.claude/` → dossier `docs/health/YYYY-MM-DD-tooling-health.md`

## Phase 1 — Build file lists (per requested surface)

For each requested surface, glob both object types:

```bash
# plugin surface
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" | sort
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills -name "SKILL.md" | sort
# tooling surface
find /Users/russelllaing/al-dev-shared/.claude/agents -name "*.md" | sort
find /Users/russelllaing/al-dev-shared/.claude/skills -name "SKILL.md" | sort
```

Keep the agent list and the skill list separate — different lenses target each.

## Phase 2 — Parallel lens dispatch (per surface)

Dispatch in a single response (parallel Agent tool calls). Choose lenses by the
object type and the `--dimension` argument:

**Agent file list** receives:
- `design`/`all`: `design-agent-lens-tool-hygiene`, `design-agent-lens-model-fit`,
  `design-agent-lens-scope-isolation`, `design-agent-lens-caller-alignment`,
  `design-agent-lens-usage-patterns`
- `quality`/`all`: `quality-agent-lens-clarity`, `quality-agent-lens-structure`,
  `quality-agent-lens-description`, `quality-agent-lens-bloat`,
  `quality-agent-lens-name-fit`

**Skill file list** receives:
- `design`/`all`: `design-skill-lens-shared-backbone`, `design-skill-lens-complexity`,
  `design-skill-lens-near-duplicates`, `design-skill-lens-handoff-gaps`,
  `design-skill-lens-preplanning`
- `quality`/`all`: `quality-skill-lens-clarity`, `quality-skill-lens-structure`,
  `quality-skill-lens-description`, `quality-skill-lens-bloat`,
  `quality-skill-lens-name-fit`

**Both object lists** additionally receive `naming-convention-lens`, with
`docs/al-dev-naming-convention.md` passed as the convention doc.

Dispatch prompt template (substitute real paths):

```
Analyze the following files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Convention doc (naming-convention-lens only):
/Users/russelllaing/al-dev-shared/docs/al-dev-naming-convention.md
```

## Phase 3 — Collect findings (fault-tolerant)

Collect each lens's findings block. A lens that returns a malformed or empty
block is recorded as `lens <name>: no result` and the run continues — a failed
lens NEVER aborts the sweep.

Parse each finding line: `- **[name]** | [Severity] | [observation] | [fix]`.

## Phase 4 — Rank

Order findings High → Medium → Low, grouped by dimension (design before quality
before naming), then by object (agent before skill). Pick the top 5 ranked
actions for the summary.

## Phase 5 — Write ONE dossier per surface

Write `docs/health/YYYY-MM-DD-<surface>-health.md` (substitute today's date and
`plugin`/`tooling`). The dossier MUST use generic vocabulary (no harness-specific
tokens). Structure:

```markdown
# <Surface> Health — YYYY-MM-DD

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | <n>    | <n>     | <n>    | <n>   |
| Medium   | <n>    | <n>     | <n>    | <n>   |
| Low      | <n>    | <n>     | <n>    | <n>   |

Top 5 ranked actions:
1. ...

## Design suggestions

[Atomise / Merge / Trim / Split / Align findings — each: finding | rationale | fix]
_No issues found._  ← if empty

## Quality findings

[Bloat / Clarity / Structure / Name-fit / Description — with file:line]
_No issues found._  ← if empty

## Naming violations

[actual name/path vs convention-expected — from naming-convention-lens]
_No issues found._  ← if empty

## Graph deltas

[orphans, dead links, off-path skills, missing refs — plugin surface only;
 omit this section for the tooling surface]
_No issues found._  ← if empty
```

Record any `lens <name>: no result` notes at the foot of the Summary section.

## Phase 6 — Refresh the dependency graph (plugin surface only)

If the plugin surface was swept, run the generator and source the "Graph deltas"
section from its health callouts (single source of truth for both the picture and
those findings):

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate-plugin-graph.py
```

The generator writes `docs/al-dev-plugin-graph.md` and exits 0 even on a parse
error (partial graph + "incomplete" banner).

## Phase 7 — Present to user

Print, per surface: dossier path + severity counts + the top action. List any
`no result` lenses. Ask: "Review the dossier and run `/plan-map-changes` on the
items you accept?" Do not edit any source file.
