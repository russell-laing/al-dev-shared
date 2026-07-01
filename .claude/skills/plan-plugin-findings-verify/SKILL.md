---
name: plan-plugin-findings-verify
description: >-
  Phase 1-3 verification portion of health-finding planning. Extracts findings from dossier/backlog,
  runs staleness gate, and rubber-ducks each finding. Writes verified findings checkpoint and hands
  off to plan-plugin-findings for Phase 4-5 (plan writing and handoff). Scoped by surface and dimension
  (accepts --skills/--agents, --surface plugin|tooling, --dimension design|quality|naming|all, --backlog flags).
argument-hint: "[--surface plugin|tooling] [--dimension design|quality|naming|all] [--skills|--agents] [--backlog]"
workflow:
  stage: decide
  invoked-by: user
  repeatable: true
  inputs:
    - docs/health/dispositions_open.md
    - docs/health/dispositions_index.json
    - docs/health/<date>-<surface>-health.md
    - profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md
    - .dev/health-loop-state.md
  outputs:
    - .dev/plan-plugin-findings-verify-checkpoint.jsonl
    - .dev/health-loop-state.md
  next: [plan-plugin-findings]
---

# Plan Health Findings — Verification Phase

Verifies findings from the latest health dossier by rubber-ducking each claim against the live codebase.
Writes verified findings checkpoint and stops; does not write a plan. See `plan-plugin-findings` for Phase 4-5.

**Outputs:** `.dev/plan-plugin-findings-verify-checkpoint.jsonl` (one object per verified finding with verdict, reason, plan_anchor, fix_scope_delta)

**MUST READ before Phase 1:** Read `../../knowledge/health-filter-contract.md` and treat it as the canonical source of truth for surface values, dimension values, plan provenance, legacy `unknown`, and filter ordering.

---

## Maintainer Contracts

Apply `../../knowledge/phase-proof-contract.md` at every phase boundary before reporting completion or updating `.dev/health-loop-state.md`.

Apply `../../knowledge/dispatch-fallback-contract.md` before every agent dispatch. Declare the preferred path, run preflight, fall back deterministically, and log `preferred → outcome → fallback → reason`.

## Prerequisites

- At least one health dossier (`docs/health/YYYY-MM-DD-<surface>-health.md`) exists with open findings
- Run `/audit-plugin-health` first if the plugin or tooling surface has changed since the dossier was generated — stale findings produce wrong plans
- At least one dossier section (Design suggestions, Quality findings, or Naming violations) has an open finding

---

## Argument Routing

The health dossier spans both skills and agents within a surface, so routing filters findings by **verb**, not by source file.

**Default (no argument):** collect every open finding from the latest dossier(s) and rubber-duck them together before writing a checkpoint.

**`--backlog`:** source the worklist from the **open `accepted` ledger backlog** instead of the latest dossier — every accepted row still awaiting implementation, regardless of which dossier first raised it. This drains rows that a later sweep's lenses never re-emitted (and so never re-entered a dossier). It composes with `--surface`/`--dimension`/`--skills`/`--agents`: those filters narrow the accepted rows returned by `list-open` using the same verb/object routing as a dossier run. See the `--backlog` branch in Phase 1.

**`--skills`:** keep only skill-design findings.

- **Verb vocabulary:**
  - **Atomise** — Break a large agent/skill into smaller, focused units
  - **Absorb** — Merge related content into an existing agent/skill
  - **Connect** — Link a new knowledge doc into existing workflow
  - **Merge** — Combine two similar skills or agents
  - **Promote** — Elevate a sub-skill or helper agent to top-level
  - **Move** — Relocate a file between surfaces (plugin ↔ tooling)
  - **Extend** — Add new downstream consumer or output stage
- **Rubber-duck reads:** `.claude/skills/<name>/SKILL.md` (tooling); if not found, read `profile-al-dev-shared/skills/<name>/SKILL.md` (distributed)
- **Plan task file paths:** reference skill file paths

**`--agents`:** keep only agent-design findings.

- **Verb vocabulary:**
  - **Trim** — Remove unused tool declarations or dead code sections
  - **Remodel** — Change a field value, frontmatter contract, or signature
  - **Split** — Extract distinct concerns into separate agents/skills
  - **Inline** — Remove a single-use wrapper skill; fold into caller
  - **Align** — Update documented Inputs/Outputs or field definitions for consistency
- **Rubber-duck reads:** `profile-al-dev-shared/agents/<name>.md` (not skills/)
- **Plan task file paths:** reference agent file paths

Quality findings (Bloat, Clarity, Structure, Name-fit, Description) and Naming violations apply to whichever object the finding names; include them under the matching `--skills`/`--agents` filter, or all of them by default.

Everything else — the rubber-duck protocol, checkpoint output format, verification checklist — stays identical across all routing modes.

Apply filters in this order:

1. surface
2. dimension
3. object-type routing (`--skills` or `--agents`)
4. finding-type routing

---

## Phase 0: Read loop state

Read `.dev/health-loop-state.md` if it exists (schema: `../../knowledge/health-loop-state-contract.md`). If its `next_command` names this skill, adopt its `next_inputs` as the dossier/ledger inputs. If it names a different loop step, tell the user the pointer expects `<that command>` and ask whether to continue here anyway. If the file is absent, proceed normally.

Also read `docs/superpowers/history.md` if it exists. Scan the last five lines matching the format `<date> | <topic> | implemented; rows closed: [...]` (the tail-appended history entries; not the older `- Summary:` bullet lines). For a single-dimension run, warn if any matched line's topic contains both the current surface keyword (e.g. `tooling` or `plugin`) and the current dimension keyword (e.g. `design` or `quality`). For a `--dimension all` run, warn if the topic contains the current surface keyword and any concrete dimension keyword (`design`, `quality`, or `naming`). Emit:

> Note: `<surface>/<dimension>` findings were recently implemented on `<date>` (plan: `<topic>`). Verify that `docs/health/dispositions_open.md` and `docs/health/dispositions_index.json` reflect those closures before planning again.

This is an informational check — do not block planning.

---

## Phase 1: Extract Findings

**If `--backlog` is set**, skip dossier location, the dossier read, and the `match` step below. Instead, draw the worklist straight from the open accepted backlog:

```bash
python3 scripts/health_disposition_store.py list-open --status accepted
# add --surface <surface> and/or --dimension <dimension> when those filters are active
```

Each emitted JSON row is already an accepted finding. Use its `object` + `finding` as the planning input and its `#NNN` `id` as the close-back ID for Phase 3 — no dossier read and no re-matching are needed (the rows are the ledger's own decided state). Then apply object-type (`--skills`/`--agents`) and `FILTER_TYPE` routing to these rows exactly as for a dossier run, and continue to Phase 2. (`list-open` already returns the deduplicated current-view rows, so an `accepted` row here has no later `fixed`/`declined` superseding it.) The rest of this phase — dossier location, dossier read, and the disposition matcher — applies only to a non-`--backlog` run.

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

- **Exactly one surface returns no path:** report `No <surface> health dossier found. Run /audit-plugin-health for that surface first.`, skip only that surface (do not substitute the other surface's dossier or a legacy `both` artifact), and continue with the surface that did return a path.
- **Neither surface returns a path:** stop with `No health dossier found for either surface; run /audit-plugin-health first.` Write no checkpoint.
- **Both surfaces return a path:** proceed with both.

Read the latest dossier(s). Collect every open finding from these sections:

- `## Design suggestions` — line format `finding | rationale | fix` (verbs: Atomise, Absorb, Connect, Merge, Promote, Move, Extend, Trim, Remodel, Split, Inline, Align)
- `## Quality findings` — line format `finding | rationale | fix` (with file:line)
- `## Naming violations` — actual name/path vs convention-expected

Skip any section marked `_No issues found._` and any finding already marked `← implemented`, `← completed`, or `← already implemented`.

Then consult the disposition ledger using the deterministic matcher. Locate the findings file corresponding to the dossier (same date and surface, `findings` kind — or derive from the dossier path by substituting `health` → `findings`), then run:

```bash
python3 scripts/health_disposition_store.py match \
  docs/health/YYYY-MM-DD-<surface>-findings.md \
  docs/health/dispositions_open.md
```

The matcher returns a **high-precision candidate shortlist** classifying each finding as `suppress`, `verify`, or `keep`. Confirm each `suppress`/`verify` candidate against the cited ledger row before acting. Read the specific flagged events from the JSONL event store by event ID (e.g., `grep -r '"event_id": "disp_YYYYMMDD_NNNNNN"' docs/health/dispositions_events/`) — do not read the full event store or the generated dispositions.md view directly.

Read `docs/health/dispositions_index.json` first. If `open_accepted` is zero, stop: there are no accepted findings to verify. If it is nonzero, read `docs/health/dispositions_open.md` and carry only the relevant `event_id` values as close-back IDs into the checkpoint.

- **`keep` with `accepted` status:** the primary input — keep it. **Capture the `event_id`** from `docs/health/dispositions_open.md` for each accepted event. Carry this `event_id` forward to the checkpoint so each verified finding can record which event it closes.
- **`suppress`** (declined/grandfathered match): before skipping, check `docs/health/dispositions_open.md` for an `accepted`-status row whose `(surface, dimension, object)` triple matches the candidate. If such a row exists, override the verdict to `keep` and use that row's `event_id` as the close-back ID (the finding was re-accepted after the prior decline/grandfather). If no override row exists, skip (note the skip count).
- **`verify`** (fixed match): apply the same override check — if a later `accepted` row for the same `(surface, dimension, object)` triple exists in `dispositions_open.md`, override to `keep` and use its `event_id`. If no override, skip (note the skip count).
- **No matched event** (`keep` with no ledger entry): undispositioned — list them and ask the user whether to include them or record dispositions first via `/record-plugin-dispositions`.

Apply filters in this order:

1. surface
2. dimension
3. object-type routing (`--skills` or `--agents`)
4. `FILTER_TYPE`, if the user passed a finding type such as `connect`, `merge`, or `trim`

List each collected item as: **type — subject — proposed change**.

If no type argument was passed, set `FILTER_TYPE=all` and keep the routed set.
Note both the active object-type route and the active `FILTER_TYPE` before proceeding to Phase 2.

If no accepted rows remain after filtering, stop with: "No accepted findings matched the requested surface/dimension filters; no checkpoint written."

---

## Phase 2: Staleness Gate (mandatory)

Run the staleness check per `../../knowledge/health-findings-staleness-gate.md`. Resolve all finding subjects to file paths, then run a **single batched check** — one `git log` per distinct path, all in one pass — to produce a compact stale/fresh table before Phase 3 begins:

```bash
# DOSSIER_DATE from the dossier filename
# Run once per distinct SUBJECT_PATH resolved from the finding list
git log --since="$DOSSIER_DATE 00:00" --oneline -- "$SUBJECT_PATH"
```

In `--backlog` mode there is no dossier date: use **each row's own `date`** (the acceptance date from the ledger) as that finding's `--since` baseline. Backlog rows span many dates, so resolve the baseline per finding rather than once for the whole batch.

- **Non-empty output** → label the finding **`⚠ possibly stale`** and note the commit count.
- **Empty output** → the subject is unchanged since the audit.

Run all distinct subject paths in a single pass and collect results as a compact table (`STALE | FRESH` per path). Do not run git log inline per finding — batch all paths and read back only the summary.

If a finding's subject cannot be resolved to a single file, skip the gate for it and proceed normally.

Report the stale-labelled count before Phase 3. Handle by tier:

Define **stale ratio** = (count of findings labelled `⚠ possibly stale`) ÷ (count of findings dispatched to Phase 3 rubber-ducking this run — i.e. the findings remaining after Phase 1 disposition filtering, excluding any `suppress`/`verify`/skipped findings).

| Stale ratio | Action |
| --- | --- |
| 100% (all findings) | Advise re-running `/audit-plugin-health`; do not proceed |
| ≥80% | Report ratio; offer (a) re-run audit or (b) proceed with heightened scrutiny; only proceed if user chooses (b) |
| <80% | Proceed; mark stale findings `⚠ possibly stale` in the worklist |

See `../../knowledge/health-findings-staleness-gate.md` for full tier-handling logic.

---

## Phase 3: Rubber Duck

For **every** suggestion, dispatch a `verify-health-finding` verification agent and collect the returned record. Do not write any checkpoint content until all records are collected. If any dispatched agent fails or returns no usable record, stop Phase 3 and do not proceed to checkpoint write — report which findings are missing records and resolve them (re-dispatch or escalate) before continuing.

> **The rubber duck is a blocker, not a suggestion.** A `skip` verdict from an agent excludes that suggestion from the checkpoint. Record skipped suggestions in a `## Skipped` section at the end of the checkpoint with the reason noted.

### Static-lens carve-out (partition before dispatch)

Before the parallel dispatch below, partition the rubber-duck worklist by each finding's source lens (see `../../knowledge/static-lens-carveout.md` for lens identification and the re-verify command):

- **Static-lens findings** (`quality-agent-lens-structure`, `quality-skill-lens-structure`, `naming-convention-lens`, `design-agent-lens-tool-hygiene`) **skip** the `verify-health-finding` agent. Re-verify them deterministically with a single `health_static_lenses.py` pass per active `(surface, dimension)` and apply the doc's **rubber-duck-mode** consumer rule: a finding that reappears takes a `proceed` verdict whose Phase 4 fix is the lens's own canned remediation; a finding that does not reappear is recorded in `## Skipped` as `static re-verify: claim no longer reproduces` and is **not** auto-declined — surface it to the user as a candidate stale-close via `/record-plugin-dispositions`.
- **Reasoning-class findings** (Bloat, Prompt Clarity, Description Drift, Name Fit, and every design lens except tool-hygiene) go to the `verify-health-finding` dispatch below unchanged — their fix needs judgement the static runner cannot supply.

This carve-out adds **no** gate reordering. Phase 1's `match` step already runs disposition suppression before this phase, so suppress-before-gate (no LLM verify on ledger-closed findings) already holds; the partition only diverts deterministic findings away from the LLM agent.

### Citation-Bearing Findings Pre-Gate

Before dispatching agents, verify findings that cite specific `file:line` locations. This gate rejects stale citations without LLM cost.

For each finding with a `file:line` citation (e.g., "at line 340-351"):

1. Extract the file path and line number(s)
2. Run: `sed -n '<line>p' <file>` (or `sed -n '<start>,<end>p'` for ranges)
3. If the output does not substantiate the cited claim, mark the finding **`⚠ cite-stale`** and skip dispatch (the LLM agent would also skip it after reading the file)
4. If output matches, proceed to dispatch

**Example:**

```bash
# Finding cites "line 340-351 contains JSONL fallback"
# Verify:
sed -n '340,351p' implement-plugin-health.md | grep -q 'JSONL'
# If match, proceed; else skip
```

Only dispatch findings that pass this gate (or lack citations entirely).

### Dispatch

See `../../knowledge/cross-file-rubber-duck-batching.md` for batching strategy.

Invoke `superpowers:dispatching-parallel-agents`. Dispatch agents grouped by `subject_path` (batching K≈5 findings per file). Pass in each dispatch:

- `mode: rubber-duck`
- `findings:` the finding(s) as `Type — Subject — proposed change`
- `subject_path:` the absolute path(s) to the subject file(s)
- `findings_date:` the `YYYY-MM-DD` from the dossier filename

The agent reads subject files in its own context and returns only compact rubber-duck records. The parent **must not** read any subject source file itself during Phase 3.

The agent returns one line per finding:
`<finding_object> | <verdict> | <reason> | <plan_anchor> | <fix_scope_delta>`

Extract each field to populate the checkpoint.

In `--backlog` mode, pass each finding's own ledger `date` as `findings_date:` (there is no dossier filename). Backlog rows carry only the ledger `finding` text and may lack a `file:line` citation — that is expected; they take the standard object-based U1–U3 rubber-duck. If a row's `object` no longer resolves to a live file (the skill or agent was renamed or removed since acceptance), the agent returns `skip`; record it in the `## Skipped` section and surface it to the user as a candidate stale-close. **Do not** auto-write a ledger row to close it — closing is the user's decision via `/record-plugin-dispositions`.

Sequential inline rubber-ducking is the fallback only when `superpowers:dispatching-parallel-agents` is genuinely unavailable.

### Cross-layer verification (conditional)

When the accepted worklist contains both skill and agent findings, verify the two layers together over the returned records and documentation maps (no additional source-file reads):

1. Trace each affected skill-to-agent handoff through the live skill callers and agent "Spawned by" references. Record missing, stale, or contradictory caller relationships in the relevant records.
2. Compare skill complexity with agent model assignments using the current maps.
3. Identify skill and agent changes that must land together — record each coupled pair as one checkpoint entry or as explicit dependencies.

### Verdict vocabulary

`proceed` (claim substantiated), `skip` (claim refuted), `modify` (partially substantiated — adjust scope). Maps from the agent's duck-check verdicts: `ACCEPT → proceed`, `REJECT → skip`, `DEFER → skip`. A `skip` (from either `REJECT` or `DEFER`) writes no checkpoint entry for the finding; refuted-skip findings are handled separately by plan-plugin-findings Phase 3.

---

## Phase 3 Output: Write verified findings checkpoint

After all findings are rubber-ducked and verdicts collected, write the checkpoint file. Each finding object captures the verification state for use by plan-plugin-findings Phase 4:

```bash
python3 << 'CHECKPOINT'
import json
import sys
from pathlib import Path

# Findings verified in this run (collected from dispatch returns or static re-verify)
# Each finding was dispatched and returned a verdict (proceed | skip | modify)
# Collect the full set here before writing

findings = [
    # Example structure (populated from Phase 3 dispatch):
    # {
    #   "object": "skill-or-agent-name",
    #   "surface": "plugin|tooling",
    #   "dimension": "design|quality|naming",
    #   "finding": "the finding description",
    #   "verdict": "proceed|skip|modify",
    #   "reason": "rubber-duck verdict reason",
    #   "plan_anchor": "where in the code the fix applies",
    #   "fix_scope_delta": "scope impact",
    #   "event_id": "disp_YYYYMMDD_NNNNNN"
    # }
]

checkpoint_path = Path(".dev/plan-plugin-findings-verify-checkpoint.jsonl")
checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

with checkpoint_path.open("w", encoding="utf-8") as f:
    for finding in findings:
        f.write(json.dumps(finding) + "\n")

print(f"Checkpoint written: {len(findings)} verified findings")
CHECKPOINT
```

---

## Phase 4: Hand off to plan-plugin-findings

Write `.dev/health-loop-state.md`:

```yaml
stage_completed: plan-plugin-findings-verify
completed_at: 2026-07-01
next_command: /plan-plugin-findings
next_inputs:
  - .dev/plan-plugin-findings-verify-checkpoint.jsonl
  - docs/health/dispositions_open.md
fresh_session_recommended: false
note: Phase 1-3 verification complete. Findings verified and checkpoint written. Run /plan-plugin-findings to execute Phase 4-5 (plan writing and implementation handoff).
```

Then tell the user: "Verification phase complete. Findings checkpoint written to `.dev/plan-plugin-findings-verify-checkpoint.jsonl`. Run `/plan-plugin-findings` with the checkpoint in context to write the plan."
