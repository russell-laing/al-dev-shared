---
name: plan-health-findings
description: >-
  Verify and plan accepted health-audit findings (formerly
  verify-map-suggestions). Reads accepted rows from
  docs/health/dispositions.md, rubber-ducks each finding against the live
  codebase before any plan content is written, then produces a verified
  implementation plan via the writing-plans sub-skill. Filter the worklist by
  object type with `--skills` or `--agents` to plan only skill-design or
  agent-design findings, and scope it by surface and dimension with `--surface
  plugin|tooling|both` and `--dimension design|quality|naming|all`. Use when the
  latest health dossier in docs/health/ has
  accepted findings that need implementing. Run /plugin-health-audit first if
  the plugin or tooling surface has changed since the dossier was last
  generated. Triggers on:
  "plan health findings", "implement health findings", "plan architectural
  changes", "plan the suggestions", "create a plan for plugin changes",
  "implement the dossier", "act on health findings", "implement agent
  findings", "plan agent changes", "implement the health audit".
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|naming|all] [optional: --agents | --skills] [optional: trim | remodel | split | inline | align | connect | merge | promote | move | extend | all]"
workflow:
  stage: decide
  invoked-by: user
  repeatable: true
  inputs:
    - docs/health/dispositions.md
    - docs/health/<date>-<surface>-health.md
    - profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md
  outputs:
    - docs/superpowers/plans/<date>-<topic>.md
  next: [projection-sync, align-harness-repos, audit-knowledge-quality]
  manual-followup: implement accepted plan
---

# Plan Health Findings

Translates findings from the latest health
dossier in `docs/health/` into a verified implementation plan. The rubber-ducking phase is **mandatory** — no
plan task is written until the live codebase state behind each finding is
confirmed. This prevents plans based on finding text that diverges from actual
code.

**MUST READ before Phase 1:** Read `.claude/knowledge/health-filter-contract.md`
and treat it as the canonical source of truth for surface values, dimension
values, plan provenance, legacy `unknown`, and filter ordering.

---

## Prerequisites

- At least one health dossier (`docs/health/YYYY-MM-DD-<surface>-health.md`)
  exists with open findings
- Run `/plugin-health-audit` first if the plugin or tooling surface has
  changed since the dossier was generated — stale findings produce wrong plans
- At least one dossier section (Design suggestions, Quality findings, or
  Naming violations) has an open finding

---

## Argument Routing

The health dossier spans both skills and agents within a surface, so routing
filters findings by **verb**, not by source file.

**Default (no argument):** collect every open finding from the latest
dossier(s) and rubber-duck them together before writing a single unified plan.

**`--skills`:** keep only skill-design findings.

- **Verb vocabulary:** Atomise, Absorb, Connect, Merge, Promote, Move, Extend
- **Rubber-duck reads:** `profile-al-dev-shared/skills/<name>/SKILL.md`
- **Plan task file paths:** reference skill file paths

**`--agents`:** keep only agent-design findings.

- **Verb vocabulary:** Trim, Remodel, Split, Inline, Align
- **Rubber-duck reads:** `profile-al-dev-shared/agents/<name>.md` (not skills/)
- **Plan task file paths:** reference agent file paths

Quality findings (Bloat, Clarity, Structure, Name-fit, Description) and Naming
violations apply to whichever object the finding names; include them under the
matching `--skills`/`--agents` filter, or all of them by default.

Everything else — the rubber-duck protocol, plan output format, verification
checklist — stays identical across all routing modes.

Apply filters in this order:

1. surface
2. dimension
3. object-type routing (`--skills` or `--agents`)
4. finding-type routing

---

## Phase 1: Extract Findings

Locate the most recent health dossier per surface:

```bash
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind health \
  --surface plugin
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind health \
  --surface tooling
```

Branch on the two `select_health_artifacts.py` results:

- **Exactly one surface returns no path:** report `No <surface> health dossier
  found. Run /plugin-health-audit for that surface first.`, skip only that
  surface (do not substitute the other surface's dossier or a legacy `both`
  artifact), and continue with the surface that did return a path.
- **Neither surface returns a path:** stop with `No health dossier found for
  either surface; run /plugin-health-audit first.` Write no plan.
- **Both surfaces return a path:** proceed with both.

Read the latest dossier(s). Collect every open finding from these sections:

- `## Design suggestions` — line format `finding | rationale | fix`
  (verbs: Atomise, Absorb, Connect, Merge, Promote, Move, Extend, Trim,
  Remodel, Split, Inline, Align)
- `## Quality findings` — line format `finding | rationale | fix` (with file:line)
- `## Naming violations` — actual name/path vs convention-expected

Skip any section marked `_No issues found._` and any finding already marked
`← implemented`, `← completed`, or `← already implemented`.

Then consult `docs/health/dispositions.md` (if present), matching by object

- issue essence:

- Findings marked `accepted` are the primary planning input — keep them.
- Skip findings marked `declined`, `grandfathered`, or `fixed` (note the
  skip count).
- Findings with no ledger row are undispositioned: list them and ask the
  user whether to include them in this plan or record dispositions first
  via `/record-health-dispositions`.

Apply filters in this order:

1. surface
2. dimension
3. object-type routing (`--skills` or `--agents`)
4. `FILTER_TYPE`, if the user passed a finding type such as `connect`,
   `merge`, or `trim`

List each collected item as: **type — subject — proposed change**.

If no type argument was passed, set `FILTER_TYPE=all` and keep the routed set.
Note both the active object-type route and the active `FILTER_TYPE` before
proceeding to Phase 2.

If no accepted rows remain after filtering, stop with:
"No accepted findings matched the requested surface/dimension filters; no plan
written."

---

## Phase 1b: Staleness Gate (mandatory)

A dossier is a point-in-time snapshot. Findings are routinely implemented
piecemeal between the audit and this planning step, so any finding whose
subject file changed *after* the dossier was generated is likely already
addressed (or has drifted out from under the finding text). The
staleness command below uses `--since="$DOSSIER_DATE 00:00"`, so any commit on or
after 00:00 on the dossier date counts as "after" (e.g. for a `2026-06-10`
dossier, a commit at `2026-06-10 08:29` is in scope). Flag these before
spending rubber-duck effort on them.

For each dossier, take its date from the filename (`YYYY-MM-DD-<surface>-health.md`).
For each collected finding, resolve its subject to a file path:

- skill → `profile-al-dev-shared/skills/<name>/SKILL.md` or `.claude/skills/<name>/SKILL.md`
- agent → `profile-al-dev-shared/agents/<name>.md` or `.claude/agents/<name>.md`

Then check whether that file changed since the dossier date:

```bash
# DOSSIER_DATE from the dossier filename; SUBJECT_PATH per finding
git log --since="$DOSSIER_DATE 00:00" --oneline -- "$SUBJECT_PATH"
```

- **Non-empty output** → label the finding **`⚠ possibly stale`** and record the
  commit(s). In Phase 2, rubber-duck it by reading the entire subject file from
  start to finish before checking the claim; expect the claim may no longer
  match (verdict `skip [already implemented]` is common here).
- **Empty output** → the subject is unchanged since the audit; rubber-duck
  normally.

If a finding's subject cannot be resolved to a single file (e.g. a cross-surface
or handoff finding), skip the gate for it and rubber-duck normally.

Report the stale-labelled count before Phase 2 (e.g. "3 of 10 findings flagged
possibly-stale — their subjects changed after the dossier date"). If **all**
findings are flagged stale, advise re-running `/plugin-health-audit` for the
affected surface before continuing.

---

## Phase 2: Rubber Duck

For **every** suggestion, run the checks and record the result. Do not write any
plan content until all suggestions are rubber-ducked.

> **The rubber duck is a blocker, not a suggestion.** If a check finds a
> mismatch or gap, resolve it before moving to the next suggestion.
> See `knowledge/rubber-duck.md` for the underlying protocol.

### Progress tracking

Before rubber-ducking any suggestion, create one TodoWrite todo per suggestion
named `[Type] [Subject]`. Mark each todo in-progress when rubber-ducking begins,
complete when the rubber duck record is written.

### Parallel exploration

Two suggestions are **independent** iff (a) the file sets they would modify are
disjoint, AND (b) neither suggestion's subject file is read during the other's
rubber-duck checks. Build a directed edge A→B when B's checks must read a file A
produces or modifies; dispatch in topological order, parallelising any set with
no incoming edges.

When any topological layer (a set of suggestions with no incoming edges) contains
3+ suggestions, dispatch that layer to parallel exploration agents before starting
rubber-ducking (in Claude Code, invoke `superpowers:dispatching-parallel-agents`),
dispatching one Explore subagent per suggestion. Each agent should: read the
affected file(s) in full, run U2 artifact checks, run the type-specific grep(s),
and return a structured rubber duck record. Collect all records before writing any
plan content. If parallel dispatch is unavailable, rubber-duck the layer
sequentially instead.

When every layer contains ≤2 suggestions, the sequential inline path is fine.

### Checks

> **Design note:** All per-check procedures are delegated to
> `knowledge/map-change-rubber-duck-checks.md` (the canonical check registry).
> This skill orchestrates the rubber-duck flow; the knowledge file owns the
> per-check logic. This is intentional separation of concerns — do not inline
> check procedures here.

For all checks — Universal (U1–U3) and type-specific (Connect, Extend, Merge,
Move, Promote, Trim, Remodel, Split, Inline, Align) — see:

`profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`

### Cross-layer verification (conditional)

When the accepted worklist contains both skill and agent findings, verify the
two layers together before writing any verdicts:

1. Trace each affected skill-to-agent handoff through the live skill callers
   (a *live skill caller* is a skill file that spawns the agent — search active
   skill bodies for the agent's `al-dev-shared:<agent-name>` invocation) and
   agent "Spawned by" references. Record missing, stale, or contradictory
   caller relationships in the relevant rubber duck records.
2. Compare skill complexity with agent model assignments using the current
   maps, then confirm disputed values against the live skill and agent source.
   Do not rely on dossier-era assignments when the source has changed.
3. Identify skill and agent changes that must land together to preserve a
   handoff, model fit, or shared pattern. Record each coupled pair either as one
   plan task or as explicit task dependencies.

This verification creates no standalone synthesis artifact. Its evidence stays
in the rubber duck records and the resulting implementation plan.

### Rubber duck record

After each suggestion, write:

```text
RUBBER DUCK: [Type — Subject]
Claim:        [what the suggestion says]
State:        [what reading the code reveals]
Side-effects: [files/scripts that depend on what's being changed]
Scope gap:    [anything the suggestion underspecifies, or "none"]
Verdict:      proceed | modify [reason] | skip [reason]
```

> **Verdict vocabulary:** Use `proceed | modify | skip` here; do not conflate with the duck-check `ACCEPT | DEFER | REJECT` in `map-change-rubber-duck-checks.md`.

If the verdict is `skip [reason]`, exclude that suggestion from Phase 3 entirely — do
not write plan content for it.

Every generated plan header must include:

```yaml
health_filters:
  surfaces:
    - plugin
  dimensions:
    - quality
    - naming
```

not create a plan task for it. Record skipped suggestions in a `## Skipped` section at
the end of the plan file with the reason noted.

---

## Phase 3: Write the Implementation Plan

After all suggestions are rubber-ducked, invoke:

**REQUIRED SUB-SKILL: Use superpowers:writing-plans**

Pass as context to writing-plans:

- All rubber duck records
- Corrected flag names, file paths, and scope (use these, not the
  original suggestion wording where rubber ducking found a mismatch)
- Cross-layer coupling constraints, including changes that must share a task or
  be linked by explicit task dependencies
- Task ordering: additive changes first (new knowledge docs, diagram
  extensions), structural changes last (merges, archives, moves)
- The verification pattern for each task, mapped by finding verb:

  | Verb | Evidences | Command |
  | --- | --- | --- |
  | Atomise / Split | New phase/file boundaries exist | `grep -n '## Phase'` + `wc -l` |
  | Absorb / Merge / Inline | Source folded in, original removed | `wc -l` (delta) + `ls` (absence) |
  | Connect / Promote | Knowledge doc created and referenced | `ls` (new doc) + `grep` (reference) |
  | Move | File relocated to target surface | `ls` (new path) + `ls` (old path gone) |
  | Extend | New downstream consumer reads the artifact | `grep` (read site) |
  | Trim / Remodel / Align | Field/tool removed or value changed | `grep` (presence/absence) |

Plan saves to:
`docs/superpowers/plans/YYYY-MM-DD-plugin-map-<short-label>.md`
