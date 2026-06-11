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
  next: [implement-health-plan]
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

## Phase 0: Read loop state

Read `.dev/health-loop-state.md` if it exists (schema:
`.claude/knowledge/health-loop-state-contract.md`). If its `next_command` names
this skill, adopt its `next_inputs` as the dossier/ledger inputs. If it names a
different loop step, tell the user the pointer expects `<that command>` and ask
whether to continue here anyway. If the file is absent, proceed normally.

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
and issue essence:

- Findings marked `accepted` are the primary planning input — keep them.
  **Capture the `#NNN` ID from the ID column** of each accepted row
  (the machine-readable identifier in the leftmost column). Carry this ID
  forward to Phase 3 so each plan task can record which ledger rows
  it closes.
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

Run the staleness check per `.claude/knowledge/health-findings-staleness-gate.md`.
For each finding, resolve its subject to a file path and run:

```bash
# DOSSIER_DATE from the dossier filename; SUBJECT_PATH per finding
git log --since="$DOSSIER_DATE 00:00" --oneline -- "$SUBJECT_PATH"
```

- **Non-empty output** → label the finding **`⚠ possibly stale`** and record the commit(s).
- **Empty output** → the subject is unchanged since the audit; rubber-duck normally.

If a finding's subject cannot be resolved to a single file, skip the gate for it and rubber-duck normally.

Report the stale-labelled count before Phase 2. Handle by tier:

| Stale ratio | Action |
|---|---|
| 100% (all findings) | Advise re-running `/plugin-health-audit`; do not proceed |
| ≥80% | Report ratio; offer (a) re-run audit or (b) proceed with heightened scrutiny; only proceed if user chooses (b) |
| <80% | Proceed; mark stale findings `⚠ possibly stale` in the worklist |

See `.claude/knowledge/health-findings-staleness-gate.md` for full tier-handling logic.

---

## Phase 2: Rubber Duck

For **every** suggestion, run the checks and record the result. Do not write any
plan content until all suggestions are rubber-ducked.

> **The rubber duck is a blocker, not a suggestion.** If a check finds a
> mismatch or gap, resolve it before moving to the next suggestion.
> See `knowledge/rubber-duck.md` for the underlying protocol.

**Before running checks:** read `.claude/knowledge/rubber-duck-orchestration.md`
(the maintainer-tooling orchestration layer). It covers progress tracking, the
independence/parallel-exploration rule, and cross-layer (skill↔agent)
verification. This skill keeps only the check pointer and the record format.

### Checks

> All per-check procedures (Universal U1–U3 and type-specific: Connect, Extend,
> Merge, Move, Promote, Trim, Remodel, Split, Inline, Align) are in
> `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`.

### Rubber duck record

After each suggestion, write a record using the format in
`profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md` (Rubber-Duck Record Format section).

> **Verdict vocabulary:** `proceed` (claim substantiated), `skip` (claim refuted),
> `modify` (partially substantiated — adjust scope). Maps from duck-check:
> `ACCEPT` → `proceed`, `REJECT` → `skip`, `DEFER` → `skip`.

If the verdict is `skip [reason]`, exclude that suggestion from Phase 3 entirely.
Record skipped suggestions in a `## Skipped` section at the end of the plan file
with the reason noted.

Every generated plan header must include a `health_filters:` block listing the
active surfaces and dimensions (e.g. `surfaces: [plugin]`, `dimensions: [quality, naming]`).

---

## Phase 3: Write the Implementation Plan

After all suggestions are rubber-ducked, invoke:

**REQUIRED SUB-SKILL: Use superpowers:writing-plans**

Pass as context to writing-plans all items listed in
`.claude/knowledge/health-plan-context-template.md`.

> **Survival caveat:** After writing-plans completes, run
> `grep -c "closes_rows:" <plan-path>` and confirm the count equals the number
> of plan tasks. A count of 0 means the sub-skill dropped the field — fix manually.

- **Suppress your Execution Handoff.** Do not present the "Subagent-Driven /
  Inline" prompt or ask "Which approach?".

Plan saves to:
`docs/superpowers/plans/YYYY-MM-DD-plugin-map-<short-label>.md`

---

## Phase 4: Hand off to implement (overrides the writing-plans Execution Handoff)

`superpowers:writing-plans` ends with its own **Execution Handoff** offering
"Subagent-Driven" or "Inline" execution. **Those endings do not apply in the
health loop** — executing the plan through them skips `/implement-health-plan`
Phase 3, so the `closes_rows:` rows are never written `fixed` and the loop
never closes. Phase 3 already instructed `writing-plans` to suppress that
handoff; this phase is the authoritative ending. If the "Which approach?"
prompt appeared anyway, do **not** answer it — supersede it by running the
steps below.

1. **Confirm the plan carries `closes_rows:`** — `grep -c "closes_rows:" <plan-path>`.
   If the count is 0, the survival caveat in Phase 3 was violated; fix the plan
   before handing off.

2. **Write `.dev/health-loop-state.md`** (schema:
   `.claude/knowledge/health-loop-state-contract.md`):

   - `stage_completed: plan-health-findings`
   - `completed_at:` today's ISO date
   - `next_command: /implement-health-plan --plan <plan-path>`
   - `next_inputs:` the `<plan-path>` plus `docs/health/dispositions.md`
   - `fresh_session_recommended: true`
   - `note:` run `/implement-health-plan` to execute AND close the ledger; do
     NOT use the writing-plans Subagent-Driven/Inline options — they skip
     ledger close-back.

3. **Stop and hand off (do not auto-execute).** Tell the user: "Plan written to
   `<plan-path>` with `closes_rows:` for ledger close-back. This transition is
   context-heavy — start a **fresh session** and run
   `/implement-health-plan --plan <plan-path>` to execute the plan and close the
   ledger. (Ignore the writing-plans Subagent-Driven/Inline prompt — it bypasses
   ledger close-back.) The pointer is saved in `.dev/health-loop-state.md`."
   Do not invoke `superpowers:subagent-driven-development` or
   `superpowers:executing-plans` from this skill.
