---
name: plan-health-findings
description: >-
  Verify and plan accepted health-audit findings (formerly
  verify-map-suggestions). Reads accepted rows from
  docs/health/dispositions.md, runs a deterministic disposition matcher in
  Phase 1 to classify findings before rubber-ducking proceeds, rubber-ducks each
  finding against the live codebase before any plan content is written, then produces a verified
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
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|naming|all] [optional: --agents | --skills] [optional: trim|remodel|split|inline|align|connect|merge|promote|move|extend] [or: all]"
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

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md`: before reporting
any phase complete, advancing to the next phase, or updating
`.dev/health-loop-state.md`, emit a phase-proof block (observed command output
or file-existence check) binding to that phase's deliverable. A restated
intention is not proof.

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

Also read `docs/superpowers/history.md` if it exists. Scan the last five
lines matching the format `<date> | <topic> | implemented; rows closed: [...]`
(the tail-appended history entries; not the older `- Summary:` bullet lines).
For a single-dimension run, warn if any matched line's topic contains both the
current surface keyword (e.g. `tooling` or `plugin`) and the current dimension
keyword (e.g. `design` or `quality`). For a `--dimension all` run, warn if the
topic contains the current surface keyword and any concrete dimension keyword
(`design`, `quality`, or `naming`). Emit:

> Note: `<surface>/<dimension>` findings were recently implemented on `<date>`
> (plan: `<topic>`). Verify that `docs/health/dispositions.md` reflects those
> closures before planning again.

This is an informational check — do not block planning.

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

Then consult the disposition ledger using the deterministic matcher. Locate the
findings file corresponding to the dossier (same date and surface, `findings`
kind — or derive from the dossier path by substituting `health` → `findings`),
then run:

```bash
python3 scripts/health_disposition_store.py match \
  --findings docs/health/YYYY-MM-DD-<surface>-findings.md
```

The matcher returns a **high-precision candidate shortlist** classifying each
finding as `suppress`, `verify`, or `keep`. Confirm each `suppress`/`verify`
candidate against the cited ledger row before acting. Read only the specific
rows the matcher flags — do not read the full `docs/health/dispositions.md`
ledger.

- **`keep` with `accepted` status:** the primary planning input — keep it.
  **Capture the `#NNN` ID from the ID column** of each accepted row
  (the machine-readable identifier in the leftmost column). Carry this ID
  forward to Phase 4 so each plan task can record which ledger rows it closes.
- **`suppress`** (declined/grandfathered match): skip (note the skip count).
- **`verify`** (fixed match): skip (note the skip count).
- **No matched row** (`keep` with no ledger entry): undispositioned — list
  them and ask the user whether to include them or record dispositions first
  via `/record-health-dispositions`.
- Append new rows with `scripts/health_disposition_store.py append_row`; never hand-edit `docs/health/dispositions.md`.
- If a step needs closure chronology, query the history store via `scripts/health_disposition_store.py iter_history_rows`.
- Verification must confirm both artifacts changed together:
  - one history shard appended under `docs/health/dispositions-history/`
  - `docs/health/dispositions.md` regenerated

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

## Phase 2: Staleness Gate (mandatory)

Run the staleness check per `.claude/knowledge/health-findings-staleness-gate.md`.
Resolve all finding subjects to file paths, then run a **single batched check** —
one `git log` per distinct path, all in one pass — to produce a compact
stale/fresh table before Phase 3 begins:

```bash
# DOSSIER_DATE from the dossier filename
# Run once per distinct SUBJECT_PATH resolved from the finding list
git log --since="$DOSSIER_DATE 00:00" --oneline -- "$SUBJECT_PATH"
```

- **Non-empty output** → label the finding **`⚠ possibly stale`** and note the commit count.
- **Empty output** → the subject is unchanged since the audit.

Run all distinct subject paths in a single pass and collect results as a compact
table (`STALE | FRESH` per path). Do not run git log inline per finding —
batch all paths and read back only the summary.

If a finding's subject cannot be resolved to a single file, skip the gate for it and proceed normally.

Report the stale-labelled count before Phase 3. Handle by tier:

Define **stale ratio** = (count of findings labelled `⚠ possibly stale`) ÷
(count of all findings rubber-ducked this run).

| Stale ratio | Action |
|---|---|
| 100% (all findings) | Advise re-running `/plugin-health-audit`; do not proceed |
| ≥80% | Report ratio; offer (a) re-run audit or (b) proceed with heightened scrutiny; only proceed if user chooses (b) |
| <80% | Proceed; mark stale findings `⚠ possibly stale` in the worklist |

See `.claude/knowledge/health-findings-staleness-gate.md` for full tier-handling logic.

---

## Phase 3: Rubber Duck

For **every** suggestion, dispatch a `health-rubber-duck` verification agent
and collect the returned record. Do not write any plan content until all
records are collected.

> **The rubber duck is a blocker, not a suggestion.** A `skip` verdict from an
> agent excludes that suggestion from Phase 4 entirely. Record skipped
> suggestions in a `## Skipped` section at the end of the plan file with the
> reason noted.

### Dispatch

Invoke `superpowers:dispatching-parallel-agents`. Dispatch **one
`health-rubber-duck` agent per finding**, batching findings that share the same
`subject_path` into a single agent call. Pass in each dispatch:

- `mode: rubber-duck`
- `findings:` the finding(s) as `Type — Subject — proposed change`
- `subject_path:` the absolute path(s) to the subject file(s)
- `findings_date:` the `YYYY-MM-DD` from the dossier filename

The agent reads subject files in its own context and returns only compact
rubber-duck records. The parent **must not** read any subject source file itself
during Phase 3.

Sequential inline rubber-ducking is the fallback only when
`superpowers:dispatching-parallel-agents` is genuinely unavailable.

### Cross-layer verification (conditional)

When the accepted worklist contains both skill and agent findings, verify the
two layers together over the returned records and documentation maps (no
additional source-file reads):

1. Trace each affected skill-to-agent handoff through the live skill callers
   and agent "Spawned by" references. Record missing, stale, or contradictory
   caller relationships in the relevant records.
2. Compare skill complexity with agent model assignments using the current maps.
3. Identify skill and agent changes that must land together — record each
   coupled pair as one plan task or as explicit task dependencies.

### Verdict vocabulary

`proceed` (claim substantiated), `skip` (claim refuted), `modify` (partially
substantiated — adjust scope). Maps from the agent's duck-check verdicts:
`ACCEPT → proceed`, `REJECT → skip`, `DEFER → skip`.

Every generated plan header must include a `health_filters:` block listing the
active surfaces and dimensions (e.g. `surfaces: [plugin]`, `dimensions: [quality, naming]`).

### Decision-logic verification

When a plan task changes this skill's **Phase 1–3 decision logic** — filter ordering
(Argument Routing / Phase 1), classification boundaries (staleness tier table / Phase 2),
or verdict-vocabulary mappings (Phase 3) — grep-only structural checks are insufficient. That task's
verification MUST include a case-walkthrough (or scenario test) that traces at
least one concrete input through the changed logic and confirms the expected
branch or verdict. Keep grep as a structural assertion only, consistent with
CLAUDE.md's Plan Task Verification Standard.

---

## Phase 4: Write the Implementation Plan

After all suggestions are rubber-ducked, invoke:

**REQUIRED SUB-SKILL: Use superpowers:writing-plans**

Pass as context to writing-plans all items listed in
`.claude/knowledge/health-plan-context-template.md`.

> **Survival caveat:** After writing-plans completes, run
> `grep -c "closes_rows:" <plan-path>` and confirm the count equals the number
> of plan tasks. A count of 0 means the sub-skill dropped the field — fix manually by adding a
> `closes_rows: [...]` line inside each task's verification block before handoff.

- **Suppress your Execution Handoff.** Do not present the "Subagent-Driven / Inline" prompt
  or ask "Which approach?" — the health loop overrides those endings. After writing-plans
  completes, this skill's Phase 5 routes execution to `/implement-health-plan` so the
  ledger entries are properly closed. Writing-plans' own endings bypass that ledger close-back.

Plan saves to:
`docs/superpowers/plans/YYYY-MM-DD-plugin-map-<short-label>.md`

---

## Phase 5: Hand off to implement (overrides the writing-plans Execution Handoff)

`superpowers:writing-plans` ends with its own **Execution Handoff** offering
"Subagent-Driven" or "Inline" execution. **Those endings do not apply in the
health loop** — executing the plan through them skips `/implement-health-plan`
Phase 4, so the `closes_rows:` rows are never written `fixed` and the loop
never closes. Phase 4 already instructed `writing-plans` to suppress that
handoff; this phase is the authoritative ending. If the "Which approach?"
prompt appeared anyway, do **not** answer it — supersede it by running the
steps below.

1. **Confirm the plan carries `closes_rows:`** — `grep -c "closes_rows:" <plan-path>`.
   If the count is 0, the survival caveat in Phase 4 was violated; fix the plan
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
