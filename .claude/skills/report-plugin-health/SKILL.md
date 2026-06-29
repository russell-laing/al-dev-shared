---
name: report-plugin-health
description: >-
  Report phase of the plugin health sweep. Reads a findings file written by
  /discover-plugin-health, filters out stale and disposition-suppressed
  findings, runs an evidence-verification gate (dispatching verify-health-finding
  in evidence mode to drop unverified findings), ranks the remainder, writes the
  dossier, and presents results to the user.
  Called by /audit-plugin-health; can also be run standalone against an existing
  findings file to re-rank or reformat without re-dispatching lenses.
argument-hint: "[--findings <path>] [--surface plugin|tooling]"
workflow:
  stage: discover
  invoked-by: both
  repeatable: true
  inputs:
    - docs/health/<date>-<surface>-findings.md
    - docs/health/<date>-<surface>-friction-findings.md
    - docs/health/dispositions-open.md
    - .dev/health-loop-state.md
  outputs:
    - docs/health/<date>-<surface>-health.md
    - .dev/health-loop-state.md
  next: [record-plugin-dispositions]
---

# Skill: /report-plugin-health

Report phase of the health sweep. Reads a findings file and writes the dossier.

Read `.claude/knowledge/health-filter-contract.md` first and treat it as the
canonical source of truth for filter metadata, dimension values, dossier
wording, and legacy `unknown` handling. `/report-plugin-health` preserves and
validates upstream dimension metadata; it does not expose a public
`--dimension` argument.

Read `../../knowledge/false-positive-classes.md` before applying the evidence
gate so the report phase carries the same suppression context as discovery.

## Maintainer Contracts

Apply `../../knowledge/phase-proof-contract.md` at every phase boundary before
reporting completion or updating `.dev/health-loop-state.md`.

Apply `../../knowledge/dispatch-fallback-contract.md` before every agent
dispatch. Declare the preferred path, run preflight, fall back
deterministically, and log `preferred → outcome → fallback → reason`.

## Phase 0 — Locate findings file

If `--findings <path>` is passed, read that file.

Otherwise, select the most recent findings independently for each requested
surface. Run only the command(s) matching `--surface`; when `--surface` is
omitted, run both:

```bash
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind findings \
  --surface plugin
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind findings \
  --surface tooling
```

If a requested surface returns no path, report: "No `<surface>` findings file
found. Run /audit-plugin-health for that surface first." Skip only that surface.
If neither requested surface returns a path, stop.

## Phase 1 — Parse findings

Read the findings file. Extract each `### <Lens Name> Findings` block.
Parse each finding line: `- **[name]** | [Severity] | [observation] | [fix]`

When a block is preceded by a `<!-- lens: <name> -->` marker (written by the
discover assembler), record that lens name as the block's source lens — it is
authoritative and disambiguates the two `Structural Conventions Findings` blocks.
Fall back to the heading text only when no marker is present.

Before parsing the finding blocks, read and preserve any findings metadata near
the top of the file:

```yaml
---
surface: tooling
dimensions:
  - quality
---
```

Validate that the findings file surface matches the selected surface and that
the concrete `dimensions:` list matches the dispatched lenses present in the
artifact.

Complexity Outliers are findings from the `design-skill-lens-complexity` lens agent.

**Complexity Outliers exception:** These findings carry an extra `verdict=` field.
See the "Complexity Outliers — Verdict Field" section in
`profile-al-dev-shared/knowledge/lens-invocation-patterns.md` for the field definition
and per-verdict action. A Complexity line missing the verdict field is a lens
regression — count it as **Medium** severity and flag as "verdict missing".

Note any "Failed lenses" listed at the foot of the file.

## Phase 2 — Filter and verify findings

Full procedures are in `.claude/knowledge/report-input-gates.md`.

**Gate order (token efficiency):** Execute the Phase 2 gates in this order —
**(1) disposition suppression** (the deterministic `health_disposition_store.py
match` step below), dropping `declined`/`grandfathered` findings; **(2) staleness
spot-check**; **(3) evidence verification** over only the survivors. The evidence
gate dispatches one sonnet `verify-health-finding` agent per subject file, so
verifying findings the ledger has already closed is wasted spend. The sub-sections
below are written in discovery order for reference; this directive governs
execution order.

### Recurrence annotation

Apply the canonical procedure in `report-input-gates.md §2 — Recurrence annotation`.

### Staleness spot-check, evidence verification, and disposition suppression

Follow the canonical procedure in `report-input-gates.md §1c — Staleness spot-check` (includes the evidence verification gate and disposition suppression logic).

## Phase 3 — Rank and Write Dossier

Order findings High → Medium → Low, grouped by dimension (design before quality
before naming), then by object (agent before skill). Pick the top 5 ranked actions
for the summary — excluding `verdict=None` findings (Phase 1), applying
the staleness spot-check rule (Phase 1c), and excluding suppressed
dispositions (Phase 1d).

List verdict-missing complexity findings in the **Failed / anomalous lenses**
note at the foot of the Summary — include the lens name, the finding subject,
and the label "verdict field absent — lens regression likely." Do not place
them in the quality findings section.

Write `docs/health/YYYY-MM-DD-<surface>-health.md` (substitute today's date and
`plugin`/`tooling` from the findings filename). **If a dossier already exists at
that path** (e.g. a re-run or `--force` sweep on the same day), Read it first to
satisfy the read-before-write contract, then overwrite it — the newest dossier
is authoritative; never append. The dossier must use generic vocabulary (no
harness-specific tokens). Structure:

```markdown
# <Surface> Health — YYYY-MM-DD

surface: tooling
dimensions:
  - quality

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | <n>    | <n>     | <n>    | <n>   |
| Medium   | <n>    | <n>     | <n>    | <n>   |
| Low      | <n>    | <n>     | <n>    | <n>   |

New this sweep: <n> · Recurring from prior sweeps: <n> (annotated inline) ·
Stale (dropped): <n> · Dropped (unverified): <n>

<!-- benchmark-metrics
raw_count: <n | not available>
verified_count: <n>
dropped_unverified_count: <n>
stale_dropped_count: <n>
suppressed_count: <n>
failed_lens_count: <n>
new_count: <n>
recurring_count: <n>
-->

<!-- token-usage
token_data_available: false
prompt_tokens: not available
completion_tokens: not available
context_compaction_events: not available
-->

Top 5 ranked actions:
1. ...

## Design suggestions

[Atomise / Merge / Trim / Split / Align findings — each: finding | rationale | fix]
_No issues found._  ← if requested and empty
_Not requested in this run._  ← if outside the requested dimensions

## Quality findings

[Bloat / Clarity / Structure / Name-fit / Description — with file:line]
_No issues found._  ← if requested and empty
_Not requested in this run._  ← if outside the requested dimensions

## Naming violations

[actual name/path vs convention-expected — from naming-convention-lens output]
_No issues found._  ← if requested and empty
_Not requested in this run._  ← if outside the requested dimensions

## Graph deltas

[orphans, dead links, off-path skills, missing refs — plugin surface only;
 omit this section for the tooling surface]
_No issues found._  ← if requested and empty
_Not requested in this run._  ← if outside the requested dimensions
```

(The `dimensions:` block may be rewritten by the session formatter from the
indented form above to loose unindented form after Write; both are valid YAML
and `health_benchmark_adapter.py` parses either. No parser changes are
needed.)

Record any failed lenses at the foot of the Summary section.

The `<!-- benchmark-metrics -->` block and the `<!-- token-usage -->` block are
the canonical, machine-readable sources for benchmark extraction
(`scripts/health_benchmark_adapter.py`); the human-facing `New this sweep: …`
line stays as-is for readers. Populate them from the Phase 2 evidence-gate
counts and token accounting. `verified_count` is the count retained after
evidence verification, `dropped_unverified_count` / `stale_dropped_count` /
`suppressed_count` / `failed_lens_count` are the corresponding filtered sets,
and `raw_count` is the pre-gate lens-finding total. All benchmark fields are
mandatory. When a count is genuinely unknown (e.g. a friction-ingest dossier
with no raw candidate denominator), write the literal `not available` — never
infer `raw_count` from `verified_count + dropped_unverified_count`, and never
omit the token-usage block because a value is unavailable.

**Compute the table and metrics block deterministically.** Rather than
hand-counting, write the Phase 2 tallies to a small JSON (`severity` breakdown
plus the eight metric fields) and run:

```bash
python3 scripts/assemble_health_findings.py metrics --counts <counts.json>
```

Paste its output as the Summary severity table + `New this sweep:` line +
`<!-- benchmark-metrics -->` block. The script raises if any of the eight fields
is missing, enforcing the "all eight fields are mandatory" rule.

Add the `<!-- token-usage -->` block immediately after the benchmark-metrics
block in the dossier. Use `token_data_available: false` plus `not available`
placeholders unless the current run exposes measured token counts.

## Precision-gate fixture run

For benchmark fixture validation, a maintainer may run this skill against
`scripts/tests/fixtures/benchmark/precision-gate-findings.md` copied to
`docs/health/<date>-tooling-findings.md`. This tests whether the evidence gate
retains valid findings that already entered the report phase; it does not test
whether discovery lenses find upstream defects. Use fixture-only target files
so the claims do not go stale when the live skill files are fixed by earlier
tasks.

After the dossier is written, verify retained fixture IDs with:

```bash
python3 scripts/precision_gate_fixture.py \
  --dossier docs/health/<date>-tooling-health.md \
  --expected scripts/tests/fixtures/benchmark/precision-gate-expected-retained.txt
```

Expected: `precision-gate fixture: PASS`.

## Phase 4 — Present to user

Read `.dev/health-loop-state.md` first (schema:
`.claude/knowledge/health-loop-state-contract.md`). If it exists and its
`next_command` names a *later* loop step (e.g. `/implement-plugin-health`), warn
the user that a prior loop is still in flight and unclosed before presenting a
fresh dossier.

Print, per surface: dossier path + severity counts (new vs recurring) + the
top action.
List any failed lenses.

Write `.dev/health-loop-state.md` (schema:
`.claude/knowledge/health-loop-state-contract.md`):

- `stage_completed: report-plugin-health`
- `completed_at:` today's ISO date
- `next_command: /record-plugin-dispositions`
- `next_inputs:` the dossier path(s) just written, plus
  `docs/health/dispositions-index.json` and `docs/health/dispositions-open.md`
- `fresh_session_recommended: false`
- `note:` recording dispositions is what stops the next sweep from re-ranking
  the same findings as new.

Then tell the user (as plain assistant text — do not wrap this in a bash
`echo` or heredoc; the backticks and nested punctuation will trip
unmatched-quote errors): "Dossier ready. Next in the loop:
`/record-plugin-dispositions` to triage accept/decline decisions (the pointer
is saved in `.dev/health-loop-state.md`). After that, `/plan-plugin-findings`
plans the accepted items."
Do not edit any source file.
