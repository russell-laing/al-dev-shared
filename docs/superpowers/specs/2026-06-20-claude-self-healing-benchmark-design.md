# Claude Self-Healing Benchmark Design

## Goal

Create a first benchmark for the Claude Code self-healing tooling in this
repository. The benchmark starts with a human-readable baseline report over
recent historical artifacts, then uses that report to define a later rerunnable
harness.

The first pass prioritizes:

1. External best-practice alignment.
2. Precision and false-positive visibility.
3. End-to-end loop quality.
4. Recall signals.

Recall is intentionally last because the current repository evidence can show
many false-positive and loop-quality signals, but cannot prove a complete set of
missed findings without controlled fixtures or a fresh adversarial sweep.

## Context

The Claude self-healing loop currently spans:

- `.claude/skills/plugin-health-audit/SKILL.md`
- `.claude/skills/plugin-health-discover/SKILL.md`
- `.claude/skills/plugin-health-report/SKILL.md`
- `.claude/skills/record-health-dispositions/SKILL.md`
- `.claude/skills/plan-health-findings/SKILL.md`
- `.claude/skills/implement-health-plan/SKILL.md`
- `.claude/agents/*lens*.md`
- `.claude/agents/health-rubber-duck.md`
- `.claude/knowledge/*health*.md`
- `docs/health/`
- `.dev/health-loop-state.md`
- `scripts/health_disposition_store.py`
- `scripts/check_ledger_staleness.py`

The benchmark is for the Claude Code self-healing tooling, but it includes both
tooling-surface and plugin-surface health runs because both exercise the same
Claude loop.

The current disposition store is still Markdown-backed from the benchmark's
point of view. `docs/superpowers/plans/2026-06-19-disposition-jsonl-store.md`
is expected to replace the large Markdown read path with a JSONL event store and
generated compact views. The benchmark design must therefore isolate disposition
access behind a small evidence adapter in the later harness instead of coupling
directly to today's Markdown table shape.

## External Rubric Anchors

The report rubric should lean toward external agent-evaluation practice, then
translate it into repo-observable evidence.

Use these external ideas as anchors:

- Reliability under repeated or stressed execution: consistency, robustness to
  equivalent task variants, and fault tolerance.
- Procedure-aware evaluation: successful outcomes are not enough if the agent
  skipped required observations, gates, or integrity checks.
- Safety-aware workflow and system scoring: evaluate not only task completion,
  but also oversight, risk controls, integration reliability, and hidden failure
  modes.

Suggested references:

- ReliabilityBench: <https://arxiv.org/abs/2601.06112>
- Procedure-Aware Evaluation: <https://arxiv.org/abs/2603.03116>
- Safety-aware agent evaluation for high-risk domains:
  <https://arxiv.org/abs/2502.15865>

## Baseline Scope

The first baseline uses recent historical artifacts only. It should not run a
fresh health sweep.

Primary evidence window: June 18-20, 2026.

Primary input artifacts:

- `docs/health/archived/2026-06-19-plugin-health.md`
- `docs/health/archived/2026-06-19-tooling-health.md`
- `docs/health/2026-06-18-plugin-health.md`
- `docs/health/archived/2026-06-18-tooling-health.md`
- `docs/superpowers/plans/archived/2026-06-19-plugin-map-health-fixes.md`
- `.dev/health-loop-state.md`
- `docs/health/dispositions.md`
- `docs/health/dispositions-history/2026/2026-06.md`

Older artifacts may be referenced only for context when a recent artifact names
a recurring issue, stale finding, or disposition row. They are not part of the
main score.

## Evidence Model

The baseline report should be explicit about which evidence was extracted from
which artifact. It should not infer unavailable counts.

Use dossier summary lines where available for:

- raw lens findings
- verified findings
- dropped unverified findings
- stale dropped findings
- disposition-suppressed findings
- failed lenses
- new versus recurring findings

Use plan, loop-state, and disposition artifacts for:

- whether accepted findings reached a plan
- whether the plan carried close-back identifiers
- whether the implementation loop closed the ledger
- whether `.dev/health-loop-state.md` ended at `next_command: none`
- whether `check_ledger_staleness.py` reports open accepted rows

Interpretation rules:

- `Dropped (unverified)`, `Stale (dropped)`, and `Dispositioned (suppressed)`
  are precision signals.
- failed lenses, missing handoff state, unclosed accepted rows, stale plan rows,
  and evidence-gate bypasses are loop-quality risks.
- recurring later findings, friction-ingest findings, and backlog rows are
  recall signals only. They should not be treated as definitive false negatives
  without a controlled fixture or fresh adversarial check.
- if an artifact lacks a count, record `not available` and lower confidence
  rather than inventing a denominator.

## Baseline Report Output

Write the first report under `docs/reviews/`, for example:

`docs/reviews/2026-06-20-claude-self-healing-benchmark-baseline.md`

The report should use this structure:

```markdown
# Claude Self-Healing Benchmark Baseline

## Scope

## Executive Summary

## Rubric

## Evidence Inventory

## Scores

| Dimension | Score | Confidence | Evidence | Main Risk |
|---|---:|---|---|---|
| Best-practice alignment | 1-5 | high/medium/low | concise artifact-backed summary | strongest risk or gap |
| Precision | 1-5 | high/medium/low | concise artifact-backed summary | strongest risk or gap |
| Loop quality | 1-5 | high/medium/low | concise artifact-backed summary | strongest risk or gap |
| Recall signal | 1-5 | high/medium/low | concise artifact-backed summary | strongest risk or gap |

## Precision Notes

## Loop Quality Notes

## Best-Practice Alignment

## Harness Follow-Up

## Recommendations
```

Scoring is deliberately lightweight: 1-5 per dimension, with a confidence label
and evidence notes. This is not an audit-grade traceability matrix. The report
must still include enough concrete artifact references for the user to challenge
or revise a score.

## Scoring Guidance

### Best-Practice Alignment

Score how well the recent loop reflects external agent-evaluation practice:

- evidence verification before ranking
- human disposition gates before implementation
- explicit procedure and phase-proof contracts
- durable state handoff
- suppression of known declined, grandfathered, or fixed findings
- ability to identify stale and unverified claims
- visibility into corrupt-success risks, where the final state looks good but
  required procedure may have been skipped

### Precision

Score based on recent raw-to-verified behavior and the clarity of false-positive
handling:

- percentage of raw findings removed by evidence verification
- number and type of stale or suppressed findings
- whether false-positive root causes are named
- whether the loop prevents re-litigation of fixed or settled rows

High precision does not require zero dropped findings. A high drop count can be
healthy if the evidence gate catches them and the report explains why they were
dropped.

### Loop Quality

Score the integrity of the end-to-end workflow:

- discover writes findings and state correctly
- report verifies, filters, and ranks findings
- dispositions are recorded through the store boundary
- accepted rows feed planning
- implementation plans carry close-back IDs
- implementation closes the ledger and updates loop state
- recent completed loop ends with zero effective-open accepted rows

Procedure violations should reduce the score even if the final visible outcome
looks clean.

### Recall Signal

Score only the available signal quality:

- recent recurring findings
- accepted backlog rows not present in the latest dossier
- friction findings that reveal surface-mapping or ingestion blind spots
- later findings that appear to have been missed by an earlier run

The report should state that recall is not fully measured in the baseline.

## Future Harness Path

The rerunnable harness should be derived from the baseline report's useful
fields. It should not be built before the baseline has established which metrics
are worth preserving.

Initial harness scope:

- parse recent health dossiers for raw, verified, dropped, stale, suppressed,
  failed-lens, new, and recurring counts
- parse loop-state and disposition views through an adapter that supports
  today's Markdown artifacts and the planned JSONL-backed views
- emit a compact Markdown or JSON scorecard with the same four dimensions
- keep recall sampling manual at first
- add fixture tests only after the baseline identifies recurring false-positive
  classes worth encoding

Non-goals for the first implementation plan:

- no fresh Claude health sweep
- no synthetic fixture suite
- no full May and early-June trend report
- no direct changes to the health loop unless the benchmark report identifies a
  separate approved follow-up

## Acceptance Criteria

- A baseline report exists under `docs/reviews/`.
- The report scores best-practice alignment, precision, loop quality, and recall
  signal using 1-5 scores with confidence labels.
- The report cites the recent artifacts it used.
- The report distinguishes evidence-backed counts from unavailable counts.
- The report notes the in-progress JSONL disposition-store migration and avoids
  designing the later harness around only the current Markdown ledger table.
- The report includes a follow-up harness schema or field list.
- No Claude health sweep is run as part of the baseline.
