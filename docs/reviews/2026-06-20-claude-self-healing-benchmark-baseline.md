# Claude Self-Healing Benchmark Baseline

## Scope

This baseline scores the recent Claude Code self-healing loop using historical artifacts from June 18-20, 2026. It includes both plugin-surface and tooling-surface health runs because both exercise the same Claude health loop. It does not run a fresh health sweep, does not create synthetic fixtures, and does not score the full May or early-June history.

The current disposition evidence is JSONL-backed. Canonical disposition events live under `docs/health/dispositions-events/`, and the generated JSONL views `docs/health/dispositions-open.md`, `docs/health/dispositions-current.md`, and `docs/health/dispositions-index.json` are the current baseline for open/current counts. `docs/health/dispositions.md` is treated as a temporary generated legacy compatibility view, not as the source of truth.

## Executive Summary

Initial scaffold created. Later tasks in this implementation plan replace this line with the final score summary after evidence has been extracted.

## Rubric

| External practice | Repo-observable benchmark check |
| --- | --- |
| Reliability under repeated or stressed execution | Check whether recent artifacts expose failed lenses, recurring findings, backlog rows, and state handoff behavior that would affect rerun consistency. |
| Procedure-aware evaluation | Check whether the loop followed required evidence gates, disposition gates, planning handoff, close-back IDs, JSONL open-row checks, and loop-state closure instead of judging only the final clean state. |
| Risk-aware workflow and system scoring | Check whether the loop reduces hidden risks such as stale claims, re-litigation of fixed findings, unverified evidence, unclosed accepted rows, and surface-mapping errors. |

External anchors:

- ReliabilityBench: <https://arxiv.org/abs/2601.06112>
- Procedure-Aware Evaluation: <https://arxiv.org/abs/2603.03116>
- Risk-aware agent evaluation: <https://arxiv.org/abs/2502.15865>

## Evidence Inventory

| Artifact | Role in benchmark | Extracted evidence |
| --- | --- | --- |
| `docs/health/archived/2026-06-19-plugin-health.md` | Main recent plugin-surface dossier | 45 raw lens findings, 24 verified, 20 failed evidence verification, 1 stale/fixed dropped, 24 new, 0 recurring, 0 failed lenses. |
| `docs/health/archived/2026-06-19-tooling-health.md` | Main recent tooling-surface dossier | 29 raw lens findings, 16 verified, 9 failed evidence verification, 1 stale/fixed dropped, 3 disposition-suppressed, 16 new, 0 recurring after one recurring object was suppressed, 0 failed lenses. |
| `docs/health/2026-06-18-plugin-health.md` | Friction-ingest mapping check | Raw/candidate count not available, 0 verified findings, 6 dropped unverified because the ingest mapped profile-claude-al-dev findings to structurally different shared-profile files, 0 new, 0 recurring. |
| `docs/health/archived/2026-06-18-tooling-health.md` | Recent tooling quality check | Raw/candidate count not available, 11 retained findings, 25 dropped unverified, 11 new, 0 recurring, no failed lenses. |
| `docs/superpowers/plans/archived/2026-06-19-plugin-map-health-fixes.md` | Implementation and close-back evidence | 46 accepted rows addressed, 33 planned, 13 re-dispositioned, close-back via `closes_rows`. |
| `.dev/health-loop-state.md` | Durable loop pointer | Loop closed at `implement-health-plan`, `next_command: none`, and notes 0 effective-open accepted rows. |
| `docs/health/dispositions-index.json` | Generated JSONL disposition index | `open_accepted` is 0 and `integrity_warnings` is 0. |
| `docs/health/dispositions-open.md` | Generated JSONL open-row view | Contains no open accepted events according to `health_disposition_store.py list-open`. |
| `scripts/check_ledger_staleness.py` output | Legacy effective-open closure check | Reports 0 effective-open accepted row(s). |
| `docs/health/dispositions.md` | Legacy compatibility view | Temporary generated compatibility output only; not the current source of truth for benchmark extraction. |

Directly reported June 19 aggregate signal:

| Measure | Count |
| --- | ---: |
| Raw lens findings with explicit raw-to-verified summary | 74 |
| Verified findings retained from explicit raw-to-verified summaries | 40 |
| Dropped as unverified from explicit raw-to-verified summaries | 29 |
| Dropped as stale/fixed or re-litigation from explicit raw-to-verified summaries | 2 |
| Suppressed by disposition ledger from explicit raw-to-verified summaries | 3 |
| Failed lenses reported in the June 19 summaries | 0 |

Additional June 18 component signals:

| Artifact | Raw/candidate denominator | Retained/new signal | Dropped unverified signal |
| --- | --- | ---: | ---: |
| `docs/health/2026-06-18-plugin-health.md` | not available | 0 | 6 |
| `docs/health/archived/2026-06-18-tooling-health.md` | not available | 11 | 25 |

The June 18 component counts are useful precision and recurrence evidence, but they are excluded from the primary raw/candidate denominator because the approved benchmark design says unavailable counts must be recorded as `not available` rather than inferred.

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
