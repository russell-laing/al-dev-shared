# Claude Self-Healing Benchmark Baseline

## Scope

This baseline scores the recent Claude Code self-healing loop using historical artifacts from June 18-20, 2026. It includes both plugin-surface and tooling-surface health runs because both exercise the same Claude health loop. It does not run a fresh health sweep, does not create synthetic fixtures, and does not score the full May or early-June history.

The scorecard remains historical, but its live-state claims were revalidated on
June 29, 2026 against the current JSONL disposition views, the legacy
staleness checker, the benchmark adapter, and the current loop-state breadcrumb.
The latest generated disposition index is from June 28, 2026 and still reports a
closed loop.

The current disposition evidence is JSONL-backed. Canonical disposition events live under `docs/health/dispositions-events/`, and the generated JSONL views `docs/health/dispositions-open.md`, `docs/health/dispositions-current.md`, and `docs/health/dispositions-index.json` are the current baseline for open/current counts. `docs/health/dispositions.md` is treated as a temporary generated legacy compatibility view, not as the source of truth.

## Executive Summary

The current Claude self-healing loop is strongest at procedure and precision control: recent June 19 runs show a directly reported evidence gate that removed 34 of 74 raw lens findings before implementation consideration, and the current JSONL disposition index and legacy checker both report zero open accepted rows. Best-practice alignment is good because the loop uses evidence verification, human disposition, durable state, close-back checks, and generated JSONL open-row views, but it does not yet measure repeated-run reliability, perturbation robustness, or controlled tool-failure tolerance. Precision is materially visible now; recall remains weakly measured and should not be overclaimed until the benchmark adds fixtures or a fresh adversarial sampling pass.

Top improvement themes:

1. Use the existing JSONL-aware adapter on future benchmark refreshes so the evidence inventory can be regenerated consistently before scoring.
2. Add a small recurrence/fixture suite only for false-positive classes that appear repeatedly in reports.
3. Keep a procedure-integrity checklist in future benchmark refreshes so clean ledger closure cannot hide skipped evidence or phase-proof steps.

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
| `.dev/health-loop-state.md` | Durable loop pointer | Current live breadcrumb shows `stage_completed: implement-plugin-health`, `completed_at: 2026-06-28`, `next_command: none`, and a note that 13 implementation tasks completed with 17 fixed disposition events appended. |
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

| Dimension | Score | Confidence | Evidence | Main Risk |
| --- | ---: | --- | --- | --- |
| Best-practice alignment | 4 | Medium | The loop has evidence verification, human disposition gates, durable loop state, close-back IDs, stale/fixed suppression, JSONL open-row checks, and legacy effective-open closure checks. | Reliability stress testing is not measured yet; rerun consistency and fault tolerance are inferred from artifacts rather than tested. |
| Precision | 4 | Medium | June 19 dossiers directly report 74 raw lens findings, 40 verified, 29 dropped unverified, 2 stale/fixed dropped, 3 ledger-suppressed, and 0 failed lenses. June 18 artifacts add 31 dropped-unverified component signals but lack explicit raw denominators. | The loop still produces many raw false positives, especially from friction mapping and subjective clarity lenses, and the June 18 denominator is unavailable. |
| Loop quality | 4 | High | The June 19 plan addressed 46 accepted rows, planned 33, re-dispositioned 13, used `closes_rows`, the JSONL index reports `open_accepted: 0`, and the current live loop state is still closed at `next_command: none` with 0 effective-open accepted rows after the June 28 close-back. | The clean final state depends on correct procedure; the report should still watch for corrupt success where close-back happens without sufficient phase proof. |
| Recall signal | 2 | Low | Backlog rows, recurrence fields, and friction-ingest mapping issues show recall-relevant signals, but the baseline does not run a fresh adversarial sweep or controlled fixture set. | False negatives cannot be measured rigorously from recent historical artifacts alone. |

## Precision Notes

Recent reports show strong visibility into false positives:

- June 19 plugin: 45 raw lens findings became 24 verified findings; 20 failed evidence verification and 1 previously-fixed finding was confirmed not regressed.
- June 19 tooling: 29 raw lens findings became 16 verified findings; 9 failed evidence verification, 1 re-litigated fixed finding was dropped, and 3 were suppressed by the disposition ledger.
- June 18 plugin friction: the raw/candidate denominator is not available; all 6 findings were dropped because the ingest mapped findings from `profile-claude-al-dev/` to structurally different `profile-al-dev-shared/` files.
- June 18 tooling quality: the raw/candidate denominator is not available; 11 findings were retained while 25 were dropped unverified.

This is healthy precision behavior at the report gate: many raw findings are noisy, but the loop exposes and removes them before they become implementation work. The main precision risk is upstream cost and reviewer fatigue from raw false positives, not silent acceptance of every lens claim. Precision confidence is medium because two June 18 artifacts provide useful component counts but not comparable raw denominators.

## Loop Quality Notes

The recent loop shows good end-to-end closure:

- Findings were ranked only after evidence verification and disposition suppression.
- The June 19 implementation plan says 46 accepted rows were addressed, 33 were planned, and 13 were re-dispositioned.
- Plan tasks carried `closes_rows` identifiers for ledger close-back.
- `docs/health/dispositions-index.json` reports `open_accepted: 0` and `integrity_warnings: 0`.
- `python3 scripts/health_disposition_store.py list-open` prints no open accepted events.
- `.dev/health-loop-state.md` now reports `stage_completed: implement-plugin-health`, `completed_at: 2026-06-28`, and `next_command: none`.
- `python3 scripts/check_ledger_staleness.py` reports 0 effective-open accepted row(s).
- `python3 scripts/validate_health_loop_state.py` reports `health-loop-state: PASS`.
- `python3 scripts/health_benchmark_adapter.py --surface both --limit 3 --format markdown` reports every `procedure_integrity` item as passing, `list-open accepted: 0`, and 784 close-back events.

The updated `generate-benchmark-report` skill was exercised on June 29, 2026
against this report. Its adapter-first validation path sampled the latest
machine-readable dossier metrics: latest plugin evidence included 20 raw / 17
verified / 2 dropped-unverified findings from
`docs/health/archived/2026-06-28-plugin-health.md`, while latest tooling
evidence included 4 raw / 3 verified / 1 dropped-unverified finding from
`docs/health/archived/2026-06-27-tooling-health.md`. Those newer samples support
the existing clean loop-quality score, but they do not change the historical
June 18-20 baseline scores.

The main procedure-aware risk is corrupt success: a clean final ledger is not enough if a future run skips phase-proof blocks, evidence verification, disposition gates, JSONL view regeneration, or close-back validation. The benchmark should therefore keep procedure-integrity checks alongside outcome checks.

## Token Efficiency Findings

Measured token-efficiency data is not available for the June 18-20, 2026
historical artifact window. The reviewed dossiers, implementation plan, loop
state, JSONL disposition views, and legacy staleness checker expose precision
and closure quality, but they do not record prompt-token counts, completion
token counts, context-window utilization, or per-phase token deltas.

The only defensible token-related inference is indirect: strong evidence
verification and disposition suppression reduced the number of findings that
reached planning or implementation, which likely reduced downstream token spend.
That remains an inference, not a measured efficiency claim, and it should not be
scored as a token-saving result until future runs capture direct usage data.

## Best-Practice Alignment

The loop aligns well with the external evaluation ideas selected for this baseline:

- ReliabilityBench-style reliability: partially covered. The artifacts expose failed lenses, recurrence, stale findings, and backlog closure, but they do not measure repeated execution, perturbation robustness, or controlled tool/API failures.
- Procedure-aware evaluation: strongly covered. The loop records evidence verification, disposition gating, planning handoff, close-back identifiers, generated JSONL open-row views, legacy effective-open checks, and final loop state rather than judging task completion alone.
- Risk-aware workflow/system scoring: strongly covered for current artifacts. The loop identifies stale claims, suppresses grandfathered or declined findings, drops unverified claims, records implementation decisions, and closes accepted rows.

The benchmark should not call this production-grade reliability testing yet. It is a baseline scorecard over historical artifacts, with a path toward a rerunnable harness.

## Harness Follow-Up

The later rerunnable harness should extract these fields:

| Field | Source now | JSONL/current source expectation |
| --- | --- | --- |
| `artifact_path` | health dossier path | unchanged |
| `surface` | dossier metadata or filename | unchanged |
| `dimensions` | dossier metadata | unchanged |
| `raw_count` | evidence-verification summary; `not available` when absent | unchanged |
| `verified_count` | evidence-verification summary or retained section count | unchanged |
| `dropped_unverified_count` | `Dropped (unverified)` section and summary | unchanged |
| `stale_dropped_count` | `Stale (dropped)` section and summary | unchanged |
| `suppressed_count` | `Dispositioned (suppressed)` section and summary | unchanged |
| `failed_lens_count` | `Failed lenses` section | unchanged |
| `new_count` | `New this sweep` summary field | unchanged |
| `new_raw_text` | raw `New this sweep` summary text | unchanged |
| `recurring_count` | parsed count from `Recurring from prior sweeps` summary field | unchanged |
| `recurring_raw_text` | raw `Recurring from prior sweeps` summary text | unchanged |
| `accepted_rows_planned` | implementation plan summary and disposition views | JSONL open/current view adapter |
| `closed_rows` | `closes_rows`, JSONL close events, and legacy checker | JSONL event close-back adapter |
| `jsonl_open_accepted_count` | `docs/health/dispositions-index.json` and `health_disposition_store.py list-open` | unchanged |
| `legacy_effective_open_count` | `check_ledger_staleness.py` | unchanged until legacy checker is retired |
| `integrity_warning_count` | `docs/health/dispositions-index.json` | unchanged |
| `loop_stage_completed` | `.dev/health-loop-state.md` | unchanged |
| `next_command` | `.dev/health-loop-state.md` | unchanged |

First automation should parse and report these fields without changing scores automatically. Human review should keep control of the 1-5 score until the extraction has passed on several runs.

## Recommendations

1. Run the evidence adapter before future benchmark refreshes so `jsonl_open_accepted_count`, `closed_rows`, `integrity_warning_count`, and legacy `effective_open_count` are regenerated from live surfaces before manual scoring.
2. Extend the adapter or a companion parser to cover dossier summary blocks and dropped-finding sections more fully, then use that output to regenerate the evidence inventory before each manual score.
3. Preserve unavailable counts as `not available` rather than deriving primary denominators from retained plus dropped component counts.
4. Keep recall manual until there is a fixture set or fresh adversarial sweep. The current historical window is not enough to prove false-negative rates.
5. Keep one benchmark checklist item for procedure integrity: evidence gate run, disposition gate run, JSONL views generated, close-back IDs present, loop state closed, JSONL open count zero, and legacy staleness checker clean.
6. Track false-positive classes by source, especially friction surface-mapping errors and subjective clarity/name-fit findings, before deciding which classes deserve synthetic fixtures.

## Implementation Status

Live repo check on June 29, 2026:

- Recommendation 1 is implemented. There is no automated benchmark-report
  workflow (the scorecard is authored by hand), so the adapter invocation is now
  documented as the mandatory first step of the Benchmark Refresh Procedure below
  and is regression-guarded by the `build_report` smoke test in
  `scripts/tests/test_health_benchmark_adapter.py`. The public CLI path remains
  `scripts/health_benchmark_adapter.py`; the implementation now lives in the
  packaged module `scripts/al_dev_tools/health/health_benchmark_adapter.py`.
- Recommendation 2 is implemented. The adapter's extraction contract now has a
  fixture/test surface: `scripts/tests/test_health_benchmark_adapter.py` with
  three fixtures under `scripts/tests/fixtures/benchmark/` covering the full
  metrics block, a partial block (missing field and `not available` literal), and
  a no-block dossier.
- Recommendation 3 is implemented. The dossier-writing contract and the adapter
  both preserve literal `not available` values instead of inferring missing
  denominators.
- Recommendation 4 is implemented as a guardrail. Recall remains manual, and
  there is still no benchmark fixture set or fresh adversarial sweep in the repo.
- Recommendation 5 is implemented. The adapter emits a concrete
  `procedure_integrity` checklist covering JSONL views, loop closure, close-back
  IDs, and staleness/index cleanliness.
- The `generate-benchmark-report` skill now requires both
  `scripts/validate_health_loop_state.py` and
  `scripts/health_benchmark_adapter.py --surface both --limit 3 --format markdown`
  before preserving clean loop-quality claims, so future refreshes should catch
  invalid breadcrumbs or failing `procedure_integrity` items before scoring.
- Recommendation 6 is not yet implemented as a dedicated mechanism. The report
  still names the important false-positive classes, but the repo does not yet
  contain a standalone tracker or benchmark-specific fixture coverage for them.

The earlier follow-up plan
`docs/superpowers/plans/2026-06-20-claude-self-healing-benchmark-evals-memory-handoff.md`
is **superseded**: its parser/eval/fixture role is now covered by
`scripts/health_benchmark_adapter.py` and
`scripts/tests/test_health_benchmark_adapter.py`, so the prose-scraping
`scripts/benchmark_self_healing.py` it proposed is not built (one benchmark
parser is kept). Its memory-boundary guidance remains valid reference.

## Adapter Status & Deferred Work

`scripts/health_benchmark_adapter.py` is the rerunnable extractor for the
Harness Follow-Up fields. It reads the machine-readable loop surfaces (the JSONL
disposition index, `list-open`, the legacy staleness checker, the loop-state
breadcrumb, and the `<!-- benchmark-metrics -->` block now emitted into each
dossier by `/plugin-health-report`) and reports one JSON record per dossier plus
a procedure-integrity checklist (Recommendation 5). It reports only — the 1-5
scores remain human-assigned until the extractor has passed cleanly on several
runs.

As of the June 29, 2026 recheck, `scripts/health_benchmark_adapter.py` is a
compatibility wrapper over `scripts/al_dev_tools/health/health_benchmark_adapter.py`.
That packaging change does not change the documented CLI contract.

Recommendation 3 is enforced at the source: dossiers written before the
metrics block existed carry no machine-readable counts, so the adapter surfaces
their raw/verified/dropped fields as `not available` rather than inferring a
denominator from `verified + dropped`.

The following remain deferred:

- **Recall (Recommendation 4)** stays manual. There is no fixture set and no
  fresh adversarial sweep, so false-negative rates must not be claimed from the
  historical artifact window alone.
- **False-positive-class tracking (Recommendation 6)** is deferred. Track
  false-positive classes by source — friction surface-mapping errors and
  subjective clarity/name-fit findings — manually for now, and revisit synthetic
  fixtures only once a class recurs across sweeps.

## Benchmark Refresh Procedure

Before any future manual scoring run, regenerate the evidence fields from live
surfaces first (Recommendation 1). Run:

```bash
python3 scripts/validate_health_loop_state.py
python3 scripts/health_benchmark_adapter.py --surface both --limit 1 --format markdown
```

Do not assign or revise the 1-5 scores until the loop-state validator passes,
every `procedure_integrity` checklist item reads ✅, and the footer shows
`list-open accepted: 0`. A validator failure or ❌ checklist item means the loop
state is not closed (open accepted rows, missing JSONL views, stale ledger,
invalid breadcrumb, or absent close-back IDs) and the scorecard must not report a
clean closure.

The adapter's extraction contract — metrics-block parsing, the `not available`
fallback for missing blocks/fields (Recommendation 3), and the
procedure-integrity checklist shape — is regression-guarded by
`scripts/tests/test_health_benchmark_adapter.py`, so the adapter cannot silently
rot between refreshes.
