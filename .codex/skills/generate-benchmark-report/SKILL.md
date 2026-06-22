---
name: generate-benchmark-report
description: Use when creating a benchmark baseline report from live health artifacts, JSONL disposition views, and loop-state evidence, especially when the result must separate measured token efficiency from historical inference before it is trusted.
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

## Workflow

### Phase 1: Capture baseline state

Before writing the report:

1. Snapshot existing health artifacts:

   ```bash
   find docs/health -maxdepth 3 -type f -print | sort > /tmp/pre-benchmark-health-files.txt
   ```

2. Capture the canonical disposition state:

   ```bash
   python3 -m json.tool docs/health/dispositions-index.json
   python3 scripts/health_disposition_store.py list-open
   python3 scripts/health_disposition_store.py list-open | wc -l
   python3 scripts/check_ledger_staleness.py
   ```

3. Treat nonzero JSONL or legacy checker values as live evidence. Do not write
   a zero-open claim from stale memory.

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

### Phase 4: Live-State Validation Loop

After drafting, re-run the live repo checks behind the strongest claims,
compare them to the text, and patch drift.

Run:

```bash
rg -n "^## (Scope|Executive Summary|Rubric|Evidence Inventory|Scores|Precision Notes|Loop Quality Notes|Token Efficiency Findings|Best-Practice Alignment|Harness Follow-Up|Recommendations)$" [report-path]
rg -n "Initial scaffold created|Evidence inventory is added|Scores are added|Precision notes are added|Loop quality notes are added|Best-practice alignment is added|Harness follow-up fields are added|Recommendations are added|[T]ODO|[T]BD|\\.\\.\\." [report-path]
find docs/health -maxdepth 3 -type f -print | sort > /tmp/post-benchmark-health-files.txt
comm -13 /tmp/pre-benchmark-health-files.txt /tmp/post-benchmark-health-files.txt
python3 -m json.tool docs/health/dispositions-index.json
python3 scripts/health_disposition_store.py list-open
python3 scripts/health_disposition_store.py list-open | wc -l
python3 scripts/check_ledger_staleness.py
git diff --check -- [report-path]
```

Interpretation:

- if heading or placeholder checks fail, fix the report structure
- if `comm` prints new `docs/health` files, stop and determine whether the
  benchmark work created them
- if live JSONL or legacy checker values changed, update the report so key
  claims match the live counts
- if token-efficiency findings rely on historical or indirect evidence, keep
  that label explicit after the re-check
- if the live state still supports the report, leave the text unchanged and
  record that validation produced no diff

### Phase 5: Final quality check

Before reporting completion:

```bash
npx --yes markdownlint-cli2 [report-path]
git status --short --ignored=matching docs/health .dev/health-loop-state.md [report-path]
```

Confirm markdown is valid, placeholders are gone, no tracked health artifacts
were created, and only the intended report file changed among tracked relevant
files.

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
