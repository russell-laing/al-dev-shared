---
name: generate-benchmark-report
description: Use when creating or validating a benchmark baseline report from live health artifacts, JSONL disposition views, and loop-state evidence, especially when the result must separate measured token efficiency from historical inference and distinguish recovery plumbing, governance controls, and prompt/content changes.
---

# Generate Benchmark Report

Create an evidence-backed benchmark report under `docs/reviews/`, then re-check
live state before claiming it is ready.

## When to Use

Use this skill when the user asks to:

- generate a self-healing benchmark baseline report
- score recent health-loop behavior from historical artifacts
- turn `docs/health`, JSONL disposition views, and `.dev/health-loop-state.md`
  into a durable review report
- include a final live-state validation pass so drift is caught before the
  report is trusted
- analyze token efficiency and record the findings with clear measured versus
  inferred boundaries

Do not use this for:

- recommendation-heavy reports that already exist and only need re-checking
  against live repo state; use `review-self-healing-report`
- usage/session analytics reports; use `generate-usage-report`
- review-only commentary on a plan; use `write-superpowers-plan-commentary`

## Output Convention

Write the final report to
`docs/reviews/YYYY-MM-DD-<topic>-benchmark-baseline.md`, for example
`docs/reviews/2026-06-20-claude-self-healing-benchmark-baseline.md`.

## Required Inputs

Read the benchmark request and identify:

- the benchmark target, such as `Claude self-healing loop`
- the evidence window, such as `June 18-20, 2026`
- the primary report sources under `docs/health/`, `docs/superpowers/`,
  `docs/reviews/`, and `.dev/`
- the canonical disposition source; prefer JSONL event-backed views when both
  JSONL and legacy Markdown artifacts exist
- any direct token-usage or prompt-size evidence, and which claims will be
  measured versus inferred

Follow any approved design or implementation plan unless live validation proves
it drifted.

### Self-Healing Synthesis Lens

When the benchmark concerns self-healing agents, separate the evidence into
two loops:

- recovery loop: detect, classify, recover, and learn from failures
- governance loop: discover, control, monitor, review, and retire agents

Use the source artifacts to capture:

- whether failures are split into semantic failures versus infrastructure
  failures
- what recovery mechanism is used, such as retry, checkpointing, replay logs,
  caching, context compression, sandbox execution, or human escalation
- whether recovery preserves state, reconstructs state, or restarts from
  scratch
- whether failures are surfaced as structured context rather than opaque
  termination events
- whether the system closes the loop from observability to improvement
  proposals, or only reports on failures
- governance signals such as ownership, approved tools, access boundaries,
  runtime control, and retirement criteria

Prefer measured counts, explicit timings, and concrete workflow evidence. If
the source only implies a claim, label it as inference rather than promoting
it to a measured result.

If a matching benchmark report already exists, validate the draft against live
state before rewriting it. Only regenerate from scratch when the draft is
missing or materially stale.

## Workflow

### Phase 1: Capture baseline state

Before writing the report:

1. Snapshot existing health artifacts:

   ```bash
   pre_snapshot=$(mktemp /tmp/benchmark-health-files.XXXXXX.pre)
   post_snapshot="${pre_snapshot%.pre}.post"
   find docs/health -maxdepth 3 -type f -print | sort > "$pre_snapshot"
   printf 'pre_snapshot=%s\npost_snapshot=%s\n' "$pre_snapshot" "$post_snapshot"
   ```

   Keep both printed variable values in your notes for Phase 4 if your shell
   session does not preserve them.

2. Capture the canonical disposition state:

   ```bash
   python3 -m json.tool docs/health/dispositions-index.json
   python3 scripts/health_disposition_store.py list-open
   python3 scripts/health_disposition_store.py list-open | wc -l
   python3 scripts/check_ledger_staleness.py
   python3 scripts/validate_health_loop_state.py
   python3 scripts/health_benchmark_adapter.py --surface both --limit 3 --format markdown
   ```

3. Treat nonzero JSONL or legacy checker values, invalid loop-state output, or
   any failing `procedure_integrity` item from the adapter as live evidence. Do
   not write a zero-open or clean-closure claim from stale memory.

### Phase 2: Extract evidence

Read the named source artifacts directly and preserve exact counts where they
exist. Typical evidence includes:

- raw-to-verified finding summaries
- new versus recurring findings
- stale, dropped, or suppressed counts
- failed-lens counts
- accepted/planned/re-dispositioned backlog counts
- `closes_rows` or equivalent close-back identifiers
- loop-state stage and `next_command`
- token counts, context-size reductions, prompt-size deltas, or explicit
  statements that token data is not available
- failure mode breakdowns, recovery paths, escalation paths, and any reported
  auto-recovery percentage or manual-intervention reduction
- context-preservation signals such as replay logs, checkpoints, persistence
  layers, or compressed memory used to support long-running runs
- governance evidence such as named owners, runtime policy checks, tool access
  limits, or retirement/decommissioning guidance

If a denominator or count is unavailable, record `not available` instead of
inferring it.

For token efficiency:

- prefer measured values from live artifacts, scripts, logs, or source files
- if only proxies exist, label them as inference and explain the proxy
- if no defensible token signal exists, say `not available`

### Phase 3: Write the report

Use this structure unless an approved plan says otherwise:

1. `# <Benchmark Name>`
2. `## Scope`
3. `## Executive Summary`
4. `## Rubric`
5. `## Evidence Inventory`
6. `## Scores`
7. `## Precision Notes`
8. `## Loop Quality Notes`
9. `## Token Efficiency Findings`
10. `## Best-Practice Alignment`
11. `## Harness Follow-Up`
12. `## Recommendations`

Keep claims:

- evidence-backed
- explicit about confidence
- clear about what is historical inference versus live current state
- explicit about what token-efficiency claims are measured versus inferred
- conservative about recall and reliability unless controlled fixtures or fresh
  adversarial runs exist
- explicit about whether a reported improvement comes from recovery plumbing,
  governance controls, or prompt/content changes

### Phase 4: Live-State Validation Loop

After drafting, re-run the live repo checks behind the strongest claims,
compare them to the text, and patch drift.

Run:

```bash
rg -n "^## (Scope|Executive Summary|Rubric|Evidence Inventory|Scores|Precision Notes|Loop Quality Notes|Token Efficiency Findings|Best-Practice Alignment|Harness Follow-Up|Recommendations)$" [report-path]
rg -n "Initial scaffold created|Evidence inventory is added|Scores are added|Precision notes are added|Loop quality notes are added|Best-practice alignment is added|Harness follow-up fields are added|Recommendations are added|[T]ODO|[T]BD|\\.\\.\\." [report-path]
find docs/health -maxdepth 3 -type f -print | sort > "$post_snapshot"
comm -13 "$pre_snapshot" "$post_snapshot"
python3 -m json.tool docs/health/dispositions-index.json
python3 scripts/health_disposition_store.py list-open
python3 scripts/health_disposition_store.py list-open | wc -l
python3 scripts/check_ledger_staleness.py
python3 scripts/validate_health_loop_state.py
python3 scripts/health_benchmark_adapter.py --surface both --limit 3 --format markdown
git diff --check -- [report-path]
```

Interpretation:

- if heading or placeholder checks fail, fix the report structure
- if `comm` prints new `docs/health` files, stop and determine whether the
  benchmark work created them
- if live JSONL or legacy checker values changed, update the report so key
  claims match the live counts
- if `validate_health_loop_state.py` fails, do not claim the loop breadcrumb is
  clean even when `next_command` text appears to be `none`
- if the adapter reports any ❌ `procedure_integrity` item, do not assign or
  preserve a clean loop-quality score until the report reflects that failure
- if token-efficiency findings rely on historical or indirect evidence, keep
  that label explicit after the re-check
- if the live state still supports the report, leave the text unchanged and
  record that validation produced no diff
- if an existing report already matches live evidence, prefer a validation-only
  pass over rewriting the report
- if the report claims a self-healing outcome, verify whether the supporting
  evidence shows actual recovery, reduced manual intervention, or only an
  architecture/design proposal

### Phase 5: Final quality check

Before reporting completion:

```bash
npx --yes markdownlint-cli2 [report-path]
git status --short docs/health .dev/health-loop-state.md [report-path]
git status --short --ignored=matching [report-path]
```

Confirm markdown is valid, placeholders are gone, no tracked health artifacts
were created, and only the intended report file changed among tracked relevant
files. Use the ignored-status check only to confirm the report itself is not
hidden from normal status output.

## Guardrails

- Treat JSONL event-backed disposition views as canonical when they exist; use
  legacy Markdown ledger files as compatibility evidence only.
- Do not trust same-day report counts without re-reading the live files.
- Do not infer missing denominators from retained plus dropped counts.
- Do not claim token savings unless the report names the measured source or the
  inference method.
- Do not overclaim recall from historical artifacts alone.
- Do not call the benchmark a rerunnable harness if the output is still a human
  scorecard.
- If a validator or live grep requires a wording correction that differs
  slightly from a plan block, make the smallest correction needed to satisfy the
  live evidence and note why.

## Validation

Before claiming the report is ready:

1. Re-open the finished report and confirm the final headings are present.
2. Re-run the live-state validation loop.
3. Run markdownlint on the report.
4. Confirm the token-efficiency section uses measured, inferred, or `not
   available` language consistently.
5. Confirm the working tree is clean or that only the intended report file is
   modified.
6. Confirm self-healing claims are grounded in observed recovery behavior or
   clearly marked as design/inference when they come from architecture-only
   sources.
7. Confirm existing matching drafts were validated rather than unnecessarily
   regenerated.
