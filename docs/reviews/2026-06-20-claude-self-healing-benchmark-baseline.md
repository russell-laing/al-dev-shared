# Claude Self-Healing Benchmark Baseline

## Scope

This baseline scores the recent Claude Code self-healing loop using historical artifacts from June 18-20, 2026. It includes both plugin-surface and tooling-surface health runs because both exercise the same Claude health loop. It does not run a fresh health sweep, does not create synthetic fixtures, and does not score the full May or early-June history.

The current disposition evidence is JSONL-backed. Canonical disposition events live under `docs/health/dispositions-events/`, and the generated JSONL views `docs/health/dispositions-open.md`, `docs/health/dispositions-current.md`, and `docs/health/dispositions-index.json` are the current baseline for open/current counts. `docs/health/dispositions.md` is treated as a temporary generated legacy compatibility view, not as the source of truth.

## Executive Summary

Initial scaffold created. Later tasks in this implementation plan replace this line with the final score summary after evidence has been extracted.

## Rubric

| External practice | Repo-observable benchmark check |
|---|---|
| Reliability under repeated or stressed execution | Check whether recent artifacts expose failed lenses, recurring findings, backlog rows, and state handoff behavior that would affect rerun consistency. |
| Procedure-aware evaluation | Check whether the loop followed required evidence gates, disposition gates, planning handoff, close-back IDs, JSONL open-row checks, and loop-state closure instead of judging only the final clean state. |
| Risk-aware workflow and system scoring | Check whether the loop reduces hidden risks such as stale claims, re-litigation of fixed findings, unverified evidence, unclosed accepted rows, and surface-mapping errors. |

External anchors:

- ReliabilityBench: <https://arxiv.org/abs/2601.06112>
- Procedure-Aware Evaluation: <https://arxiv.org/abs/2603.03116>
- Risk-aware agent evaluation: <https://arxiv.org/abs/2502.15865>

## Evidence Inventory

Evidence inventory is added in Task 2 after the recent dossier summaries, JSONL disposition state, loop state, and legacy effective-open checker output are captured.

## Scores

Scores are added in Task 3 after the evidence inventory is complete.

## Precision Notes

Precision notes are added in Task 3 after raw, verified, stale, suppressed, dropped, new, and recurring counts are reconciled.

## Loop Quality Notes

Loop quality notes are added in Task 3 after close-back, JSONL open-row, legacy checker, and loop-state evidence are reconciled.

## Best-Practice Alignment

Best-practice alignment is added in Task 3 after the external rubric anchors are mapped to repo-observable evidence.

## Harness Follow-Up

Harness follow-up fields are added in Task 3 after the baseline report identifies the useful extraction fields.

## Recommendations

Recommendations are added in Task 3 after the scores and follow-up fields are written.
