---
name: plan-plugin-findings
description: >-
  Verify and plan accepted health-audit findings (formerly
  verify-map-suggestions). Reads accepted events from
  docs/health/dispositions-open.md, runs a deterministic disposition matcher in
  Phase 1 to classify findings before rubber-ducking proceeds, rubber-ducks each
  finding against the live codebase before any plan content is written, then produces a verified
  implementation plan via the writing-plans sub-skill (note: `closes_event_ids`
  may need manual repair if writing-plans drops the field — see Phase 4 survival
  caveat). Filter the worklist by
  object type with `--skills` or `--agents` to plan only skill-design or
  agent-design findings, and scope it by surface and dimension with `--surface
  plugin|tooling|both` and `--dimension design|quality|naming|all`. Use when the
  latest health dossier in docs/health/ has
  accepted findings that need implementing. Run /audit-plugin-health first if
  the plugin or tooling surface has changed since the dossier was last
  generated. Triggers on:
  "plan health findings", "implement health findings", "plan architectural
  changes", "plan the suggestions", "create a plan for plugin changes",
  "implement the dossier", "act on health findings", "implement agent
  findings", "plan agent changes", "implement the health audit".
argument-hint: "[--surface plugin|tooling|both] [--dimension design|quality|naming|all] [optional: --agents | --skills] [optional: trim|remodel|split|inline|align|connect|merge|promote|move|extend] [or: all] [optional: --backlog]"
workflow:
  stage: decide
  invoked-by: user
  repeatable: true
  inputs:
    - docs/health/dispositions-open.md
    - docs/health/dispositions-index.json
    - docs/health/<date>-<surface>-health.md
    - profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md
  outputs:
    - docs/superpowers/plans/<date>-<topic>.md
  next: [implement-plugin-health]
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

## Dispatch policy

This skill's agent dispatch follows `../../knowledge/dispatch-fallback-contract.md`:
declare the preferred path (the `Agent` tool), run preflight (tool available,
arguments valid against the receiving contract), fall back deterministically on
failure, and log `preferred → outcome → fallback → reason`.

## Prerequisites

- At least one health dossier (`docs/health/YYYY-MM-DD-<surface>-health.md`)
  exists with open findings
- Run `/audit-plugin-health` first if the plugin or tooling surface has
  changed since the dossier was generated — stale findings produce wrong plans
- At least one dossier section (Design suggestions, Quality findings, or
  Naming violations) has an open finding

---

## Argument Routing

The health dossier spans both skills and agents within a surface, so routing
filters findings by **verb**, not by source file.

**Default (no argument):** collect every open finding from the latest
dossier(s) and rubber-duck them together before writing a single unified plan.

**`--backlog`:** source the worklist from the **open `accepted` ledger
backlog** instead of the latest dossier — every accepted row still awaiting
implementation, regardless of which dossier first raised it. This drains rows
that a later sweep's lenses never re-emitted (and so never re-entered a
dossier). It composes with `--surface`/`--dimension`/`--skills`/`--agents`:
those filters narrow the accepted rows returned by `list-open` using the same
verb/object routing as a dossier run. See the `--backlog` branch in Phase 1.

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
> (plan: `<topic>`). Verify that `docs/health/dispositions-open.md` and
> `docs/health/dispositions-index.json` reflect those closures before planning again.

This is an informational check — do not block planning.

---

## Phase 1: Extract Findings

**If `--backlog` is set**, skip dossier location, the dossier read, and the
`match` step below. Instead, draw the worklist straight from the open accepted
backlog:

```bash
python3 scripts/health_disposition_store.py list-open --status accepted
# add --surface <surface> and/or --dimension <dimension> when those filters are active
```

Each emitted JSON row is already an accepted finding. Use its `object` +
`finding` as the planning input and its `#NNN` `id` as the close-back ID for
Phase 4 — no dossier read and no re-matching are needed (the rows are the
ledger's own decided state). Then apply object-type (`--skills`/`--agents`) and
`FILTER_TYPE` routing to these rows exactly as for a dossier run, and continue
to Phase 2. (`list-open` already returns the deduplicated current-view rows, so
an `accepted` row here has no later `fixed`/`declined` superseding it.) The rest
of this phase — dossier location, dossier read, and the disposition matcher —
applies only to a non-`--backlog` run.

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
  found. Run /audit-plugin-health for that surface first.`, skip only that
  surface (do not substitute the other surface's dossier or a legacy `both`
  artifact), and continue with the surface that did return a path.
- **Neither surface returns a path:** stop with `No health dossier found for
  either surface; run /audit-plugin-health first.` Write no plan.
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
candidate against the cited ledger row before acting. Read the specific flagged events from the JSONL event store by event ID
(e.g., `grep -r '"event_id": "disp_YYYYMMDD_NNNNNN"' docs/health/dispositions-events/`) —
do not read the full event store or the generated dispositions.md view directly.

Read `docs/health/dispositions-index.json` first. If `open_accepted` is zero,
stop: there are no accepted findings to plan. If it is nonzero, read
`docs/health/dispositions-open.md` and carry only the relevant `event_id` values
into plan tasks as `closes_event_ids`.

- **`keep` with `accepted` status:** the primary planning input — keep it.
  **Capture the `event_id`** from `docs/health/dispositions-open.md` for each
  accepted event. Carry this `event_id` forward to Phase 4 so each plan task
  can record which events it closes in `closes_event_ids`.
- **`suppress`** (declined/grandfathered match): skip (note the skip count).
- **`verify`** (fixed match): skip (note the skip count).
- **No matched event** (`keep` with no ledger entry): undispositioned — list
  them and ask the user whether to include them or record dispositions first
  via `/record-plugin-dispositions`.

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

In `--backlog` mode there is no dossier date: use **each row's own `date`** (the
acceptance date from the ledger) as that finding's `--since` baseline. Backlog
rows span many dates, so resolve the baseline per finding rather than once for
the whole batch.

- **Non-empty output** → label the finding **`⚠ possibly stale`** and note the commit count.
- **Empty output** → the subject is unchanged since the audit.

Run all distinct subject paths in a single pass and collect results as a compact
table (`STALE | FRESH` per path). Do not run git log inline per finding —
batch all paths and read back only the summary.

If a finding's subject cannot be resolved to a single file, skip the gate for it and proceed normally.

Report the stale-labelled count before Phase 3. Handle by tier:

Define **stale ratio** = (count of findings labelled `⚠ possibly stale`) ÷
(count of findings dispatched to Phase 3 rubber-ducking this run — i.e. the
findings remaining after Phase 1 disposition filtering, excluding any
`suppress`/`verify`/skipped findings).

| Stale ratio | Action |
|---|---|
| 100% (all findings) | Advise re-running `/audit-plugin-health`; do not proceed |
| ≥80% | Report ratio; offer (a) re-run audit or (b) proceed with heightened scrutiny; only proceed if user chooses (b) |
| <80% | Proceed; mark stale findings `⚠ possibly stale` in the worklist |

See `.claude/knowledge/health-findings-staleness-gate.md` for full tier-handling logic.

---

## Phase 3: Rubber Duck

For **every** suggestion, dispatch a `verify-health-finding` verification agent
and collect the returned record. Do not write any plan content until all
records are collected. If any dispatched agent fails or returns no usable
record, stop Phase 3 and do not proceed to Phase 4 — report which findings are
missing records and resolve them (re-dispatch or escalate) before continuing.

> **The rubber duck is a blocker, not a suggestion.** A `skip` verdict from an
> agent excludes that suggestion from Phase 4 entirely. Record skipped
> suggestions in a `## Skipped` section at the end of the plan file with the
> reason noted.
>
> **Refuted skips must still close the ledger.** A `skip` because the claim was
> *refuted* (or is already-covered) leaves the accepted event open unless the
> plan closes it. In addition to the `## Skipped` prose section, the plan **must
> include a final ledger-action task** that appends a `declined` disposition for
> every refuted-skip event:
>
> ```bash
> python3 scripts/health_disposition_store.py append_event \
>   --event-id <disp_id> --disposition declined \
>   --evidence "declined: rubber-duck refuted — <one-line reason>"
> ```
>
> That task carries a Step 0 that commits any pre-existing dirty `docs/health/`
> first (so a later `git add docs/health/` stages only this task's regenerated
> output). Author Step 0 in the fail-loud conditional form — commit only when the
> tree is dirty and let a real commit failure stop the task — never
> `git add … && git commit … || echo`, whose `|| echo` masks genuine commit errors:
>
> ```bash
> if ! git diff --quiet -- docs/health/ || ! git diff --cached --quiet -- docs/health/; then
>   git add docs/health/
>   git commit -m "<emoji> chore(health): sync ledger before declines"
> fi
> ```
>
> The task also carries a `regenerate` step, a **declined-row presence** check that
> proves a `declined` event row exists for each ID — not merely the pre-existing
> `accepted` row that was always there
> (`grep -rh '"event_id": "<id>"' docs/health/dispositions-events/ | grep -q '"disposition": "declined"'`),
> an **inverted** open-view absence check
> (`if grep -q <id> docs/health/dispositions-open.md; then echo ERROR; exit 1; fi`),
> and `closes_event_ids: []` with a note that `implement-plugin-health` MUST NOT
> write `fixed` for these events (they are closed by `append_event`). The
> **stale-object** skip below
> (object no longer resolves) is the one exception — those stay user-decided via
> `/record-plugin-dispositions`, not auto-declined.

### Dispatch

Invoke `superpowers:dispatching-parallel-agents`. Dispatch **one
`verify-health-finding` agent per finding**, batching findings that share the same
`subject_path` into a single agent call. Pass in each dispatch:

- `mode: rubber-duck`
- `findings:` the finding(s) as `Type — Subject — proposed change`
- `subject_path:` the absolute path(s) to the subject file(s)
- `findings_date:` the `YYYY-MM-DD` from the dossier filename

The agent reads subject files in its own context and returns only compact
rubber-duck records. The parent **must not** read any subject source file itself
during Phase 3.

In `--backlog` mode, pass each finding's own ledger `date` as `findings_date:`
(there is no dossier filename). Backlog rows carry only the ledger `finding`
text and may lack a `file:line` citation — that is expected; they take the
standard object-based U1–U3 rubber-duck. If a row's `object` no longer resolves
to a live file (the skill or agent was renamed or removed since acceptance), the
agent returns `skip`; record it in the `## Skipped` section and surface it to
the user as a candidate stale-close. **Do not** auto-write a ledger row to close
it — closing is the user's decision via `/record-plugin-dispositions`.

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
> `grep -c "closes_event_ids:" <plan-path>` and confirm the count equals the number
> of plan tasks. A count of 0 means the sub-skill dropped the field — fix manually by adding a
> `closes_event_ids:` block as the final item inside each task's verification block
> (after the verification steps — not in the task title or header) before handoff.

- **Pre-empt the known correction patterns.** Before finalizing, consult
  `.claude/knowledge/correction-patterns.md` and author every task so no row applies
  to it. `revise-plugin-plan` checks the same list — anything you author cleanly here is
  one defect the reviewer does not have to send back. The recurring author-side defects
  this gate exists to prevent:
  - **Value-sensitive verification.** Every task's verification grep MUST fail on the
    pre-edit file — assert the new value with a fixed-string `grep -F`, and where the old
    value is known, assert its absence too. A whole-file presence grep that already matches
    the untouched file is not acceptance evidence (`/implement-plugin-health` would mark the
    task verified even if the edit was skipped).
  - **Task-specific commit scopes.** Use `type(<edited-component>)` matching the edited
    skill/agent/directory name (e.g. `fix(al-dev-investigate)`, `chore(generated-agents)`),
    never a generic `type(plugin)`. Subject ≤72 characters, subject-only (tool repo).
  - **Shared-surface validation gate.** When the plan edits `profile-al-dev-shared/` files,
    add a validation-gate task (after the last source edit and any projection regen, before
    ledger close-back) chaining the repo's shared-surface validators with `&&`; it closes no
    events (`closes_event_ids: []`).

- **Spec-only tasks must not earn closure.** When a rubber-duck `modify` verdict reduces
  a finding's scope to "write prerequisite documentation only" (the task body explicitly
  defers the behavior change to a future plan), the task must carry `closes_event_ids: []`
  with a note that the accepted event stays open for that future plan. Do not assign the
  accepted `event_id` to a spec-only task — `implement-plugin-health` would falsely mark it
  `fixed` even though the underlying behavior change has not occurred.

- **Suppress your Execution Handoff.** Do not present the "Subagent-Driven / Inline" prompt
  or ask "Which approach?" — the health loop overrides those endings. After writing-plans
  completes, this skill's Phase 5 routes execution to `/implement-plugin-health` so the
  ledger entries are properly closed. Writing-plans' own endings bypass that ledger close-back.

Plan saves to:
`docs/superpowers/plans/YYYY-MM-DD-plugin-map-<short-label>.md`

---

## Phase 5: Hand off to implement (overrides the writing-plans Execution Handoff)

`superpowers:writing-plans` ends with its own **Execution Handoff** offering
"Subagent-Driven" or "Inline" execution. **Those endings do not apply in the
health loop** — executing the plan through them skips `/implement-plugin-health`
Phase 4, so the `closes_event_ids:` events are never written `fixed` and the loop
never closes. Phase 4 already instructed `writing-plans` to suppress that
handoff; this phase is the authoritative ending. If the "Which approach?"
prompt appeared anyway, do **not** answer it — supersede it by running the
steps below.

1. **Confirm the plan carries `closes_event_ids:`** — `grep -c "closes_event_ids:" <plan-path>`.
   If the count is 0, the survival caveat in Phase 4 was violated; fix the plan
   before handing off.

2. **Commit-subject length check.** Verify all commit subjects are ≤72 characters (`revise-plugin-plan`
   catches violations too, but catching them here is cheaper):

   ```bash
   PLAN=<plan-path>
   grep -oE 'git commit -m "[^"]+"' "$PLAN" | sed -E 's/^git commit -m "//; s/"$//' > /tmp/subjects
   while IFS= read -r s; do n=$(printf '%s' "$s" | wc -m); [ "$n" -gt 72 ] && echo "OVER 72 ($n): $s"; done < /tmp/subjects
   ```

   Any printed line is a violation. Fix the subject in the plan before handing off.
   Character count, not bytes — one emoji counts as one character.

3. **Coverage reconciliation (mandatory gate).** Every accepted event in
   `docs/health/dispositions-open.md` must be resolved **exactly once** across
   `(plan-task closes_event_ids)` ∪ `(decline/grandfather ledger tasks)` — none
   missing, none in both. Compute it explicitly and state the arithmetic in the
   handoff summary (e.g. "15 plan events + 1 grandfathered + 3 declined = 19
   total"). If any accepted event is in neither, the plan has a coverage hole
   (typically a refuted skip with no decline task — see Phase 3); fix it before
   handing off. This mirrors `revise-plugin-plan` Phase 4 so the two skills stay
   in sync.

4. **Write `.dev/health-loop-state.md`** (schema:
   `.claude/knowledge/health-loop-state-contract.md`):

   - `stage_completed: plan-plugin-findings`
   - `completed_at:` today's ISO date
   - `next_command: /implement-plugin-health --plan <plan-path>`
   - `next_inputs:` the `<plan-path>` plus `docs/health/dispositions-open.md`
   - `fresh_session_recommended: true`
   - `note:` run `/implement-plugin-health` to execute AND close the ledger; do
     NOT use the writing-plans Subagent-Driven/Inline options — they skip
     ledger close-back.

5. **Stop and hand off (do not auto-execute).** Tell the user: "Plan written to
   `<plan-path>` with `closes_event_ids:` for ledger close-back. This transition is
   context-heavy — start a **fresh session** and run
   `/implement-plugin-health --plan <plan-path>` to execute the plan and close the
   ledger. (Ignore the writing-plans Subagent-Driven/Inline prompt — it bypasses
   ledger close-back.) The pointer is saved in `.dev/health-loop-state.md`."
   Do not invoke `superpowers:subagent-driven-development` or
   `superpowers:executing-plans` from this skill.
