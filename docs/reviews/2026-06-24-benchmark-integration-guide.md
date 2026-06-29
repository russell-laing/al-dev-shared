# Benchmark Report Integration Guide

**Purpose:** How to use the `generate-benchmark-report` skill and its output
artifacts to drive concrete improvements to the Claude Code self-healing loop.
This is a process guide, not a report — it maps benchmark findings to workflow
actions.

**Status as of 2026-06-29:**
Baseline report exists at
`docs/reviews/2026-06-20-claude-self-healing-benchmark-baseline.md`.
Recommendations 1–5 are still implemented; Recommendation 6 is still deferred.
The adapter survived the later health-package refactor: the public CLI remains
`scripts/health_benchmark_adapter.py`, while implementation lives in
`scripts/al_dev_tools/health/health_benchmark_adapter.py`. The updated
`generate-benchmark-report` skill now runs both the adapter and
`scripts/validate_health_loop_state.py` before preserving clean loop-quality
claims.

---

## 1. The Core Feedback Loop

The benchmark report is a **meta-level scorecard that measures the health loop
itself**, not just the plugin/tooling surfaces it audits. To be useful it needs
to close its own loop:

```text
Health sweep → Benchmark report → Integration actions → Next health sweep
                     ↑                                          |
                     └──────────── delta benchmark ←───────────┘
```

The health loop itself is currently closed (`.dev/health-loop-state.md` reports
`next_command: none`), but the benchmark integration loop is still open:
Recommendation 6 is deferred, no delta report measures whether scores improved,
and no automatic cadence triggers a refresh.

---

## 2. Integration Patterns by Finding Type

### 2.1 False-Positive Class Findings

**What the baseline shows:** 29 of 74 raw findings were dropped as unverified
across the June 19 runs. The June 18 friction-mapping pass produced 6 findings
all dropped because files were mapped from `profile-claude-al-dev/` to
structurally different `profile-al-dev-shared/` files.

**How to route this:**

- Track recurring false-positive classes in a dedicated table (see §5 below)
  so patterns are visible across sweeps rather than buried in prose.
- Once a class recurs across two independent sweeps, promote it to `Suppress`
  and pass it as explicit context to `verify-health-finding` dispatch so the
  agent knows to apply the suppression rule (see §5 for the mechanism).
- Verify in the next benchmark that retained findings no longer include any
  examples from a suppressed class. Success means zero retained findings from
  that class, not a change in the suppression count.

**Immediate action (Recommendation 6, currently deferred):**

Create `docs/health/false_positive_classes.md` with the starter table from §5.
Start with the two classes the baseline names: `friction-surface-mismatch` and
`subjective-clarity-name-fit`. Both are currently `Candidate` (seen once each).
Add a row each time a class is first seen; promote through `Candidate → Monitor
→ Suppress` as it recurs. This is a lightweight precursor to synthetic fixture
coverage.

### 2.2 Evidence-Gate Fixture Findings

**What the baseline shows:** Recall is scored 2/5 with low confidence because
there are no controlled fixtures and no fresh adversarial sweep. The loop cannot
prove false-negative rates from historical artifacts alone.

**Important distinction — what fixtures at this injection point actually test:**

Fixtures injected into the findings file between `discover-plugin-health` and
`report-plugin-health` test whether the **evidence-verification gate correctly
retains valid findings** — this is precision-gate behavior. It answers: "does
`verify-health-finding` avoid false negatives on findings already surfaced by
lenses?" This is not the same as recall.

True recall — whether the lenses surface real problems in the first place —
requires injecting known problems upstream into the source files the lenses
scan. That is a larger effort and requires lens-level fixture design.

**What to build first:**

Build precision-gate fixtures. They are more tractable, directly test the most
consequential gate in the loop, and give a rerunnable test harness without
requiring changes to lens agents:

- Design 3–5 synthetic findings that describe genuine structural issues in real
  files with real line ranges.
- Inject them into a copy of a recent findings file.
- Run `report-plugin-health` against the copy.
- Verify each synthetic finding is retained in the output dossier (not dropped
  as unverified).
- Record them in `scripts/tests/fixtures/benchmark/`.

Once precision-gate fixtures pass reliably, design a separate upstream recall
fixture effort that places known problems into source files before lens dispatch.

### 2.3 Procedure-Integrity Findings

**What the baseline shows:** The loop produces a clean final ledger state, but
the benchmark notes that a clean ledger is not sufficient proof that all
required phase-proof steps were actually taken.

**How to route this:**

- The adapter already emits a `procedure_integrity` checklist retrospectively
  from artifacts. The gap is that this checklist is generated after the fact
  rather than written during the run. The current benchmark skill now treats any
  ❌ checklist item or failed `validate_health_loop_state.py` run as scoring
  evidence, so retrospective failures should no longer be hidden by a clean
  prose summary.
- Adding a prospective procedure log requires appending a record at the end of
  each skill phase — across 6+ skills with multiple phases each. That is a
  significant cross-cutting change and should not be treated as a simple fix.
- **Narrow starting point:** Add the procedure log only to
  `implement-plugin-health` first, since corrupt success (closing the ledger
  without sufficient phase proof) is most dangerous at the implement phase.
  Verify the adapter reads it before extending to upstream phases.
- A procedure log is only checkable if the "expected phase list" is defined
  somewhere the adapter can compare against. Define this list in a companion
  file (e.g., `docs/health/expected_phases.md`) before writing the log.

### 2.4 Token Efficiency Findings

**What the baseline shows:** Token efficiency is entirely unavailable — no
prompt-token counts, completion-token counts, or context-window utilization data
exist in the June 18-20 artifact window. The only defensible inference is that
strong evidence filtering likely reduced downstream token spend.

**How to capture this in future runs:**

- Emit a `<!-- token-usage -->` comment block in each dossier (similar to the
  existing `<!-- benchmark-metrics -->` block). Populate it with per-phase token
  counts if the harness exposes them, or with a `not available` literal if not.
- Add `token_data_available: true|false` to the adapter's output schema so the
  benchmark can report coverage without claiming false precision.
- The token signal most worth capturing first is not raw counts but **context
  compaction events** — when the harness compresses prior context during a
  health run. Each compaction event is evidence the run was long enough to
  matter, and recording them gives a proxy for run complexity. Note: compaction
  events are not currently exposed in a way that skill agents can detect; this
  may require harness-level instrumentation rather than a skill change.

---

## 3. Score Improvement Targets

Current scores from the baseline:

| Dimension | Score | Confidence | Key blocker |
| --- | ---: | --- | --- |
| Best-practice alignment | 4/5 | Medium | Reliability stress testing unmeasured |
| Precision | 4/5 | Medium | False-positive classes untracked; June 18 denominators unavailable |
| Loop quality | 4/5 | High | Procedure-integrity retrospective gap |
| Recall signal | 2/5 | Low | No fixtures, no adversarial sweep |

**Realistic next targets (one benchmark cycle):**

| Dimension | Realistic next score | Required action |
| --- | ---: | --- |
| Precision | 4/5 → 4/5 stable | Add false-positive class tracker; bring June 18 denominator coverage online |
| Loop quality | 4/5 → 5/5 | Add prospective procedure log to `implement-plugin-health`; verify adapter reads it |
| Recall signal | 2/5 → 3/5 | Add precision-gate fixtures; note this does not yet measure true recall |
| Token efficiency | not scored → instrumented | Emit `<!-- token-usage -->` blocks even if `not available`; a score requires actual data, not just coverage |
| Best-practice alignment | 4/5 → 4/5 stable | No new action needed; maintain existing gates |

**Do not try to move all scores in one cycle.** Precision-gate fixtures and the
false-positive class tracker are the highest-value first steps because they
address the two most tractable deferred items without requiring upstream
instrumentation changes.

---

## 4. Delta Benchmark Pattern

The current baseline is a one-shot scorecard. To make it durable, introduce a
**delta benchmark** that runs after each completed health cycle:

1. Run the validator and adapter: `python3 scripts/validate_health_loop_state.py` and `python3 scripts/health_benchmark_adapter.py --surface tooling --limit 1 --format markdown`
2. Re-read the baseline scores.
3. For each dimension, ask: did the score change? If so, which action caused it?
4. Write a two-section append to the baseline (`## Delta — YYYY-MM-DD`) rather
   than a full regeneration.

This keeps the baseline as a stable anchor and the delta as a growing changelog.
The delta format should use the same rubric table but add a `Previous` and
`Change` column.

A delta report is warranted only when at least one of the following is true:

- A new health cycle has completed (at least one full discover → report →
  implement pass).
- A deferred recommendation has been implemented.
- A score-relevant script or gate has changed.

Do not generate a delta report just because the date changed.

---

## 5. Deferred Item: False-Positive Class Tracker

Recommendation 6 from the baseline is the only unimplemented recommendation.
Its lightweight implementation:

**File:** `docs/health/false_positive_classes.md`

```markdown
# False-Positive Classes

| ID | Description | First seen | Last seen | Status |
| --- | --- | --- | --- | --- |
| friction-surface-mismatch | Friction-ingest findings mapped to structurally different target files | 2026-06-18 | 2026-06-18 | Candidate |
| subjective-clarity-name-fit | Clarity and name-fit lens findings with no objective criterion | 2026-06-19 | 2026-06-19 | Candidate |
```

**Status progression:**

- `Candidate` — seen in one sweep only; watch for recurrence. Both starter
  classes are at this status because each has been observed once.
- `Monitor` — recurred across two independent sweeps; include in benchmark
  precision notes as a known noise source.
- `Suppress` — approved for active suppression; update the `discover-plugin-health`
  dispatch prompt (or its knowledge context) to include the class ID and
  description as a known false-positive pattern. The `verify-health-finding`
  agent will encounter this context when evaluating matching findings and can
  apply the suppression rule. Suppression requires a deliberate prompt update —
  a table status change alone has no runtime effect.

**Success metric for a suppressed class:** Zero retained findings from that
class in the next two sweeps after suppression is applied. A suppressed class
that continues to appear in retained findings means the prompt context is
insufficient and needs a stronger suppression instruction.

---

## 6. Harness Automation Path

The benchmark currently uses human scoring after adapter extraction. The path
toward evidence-based scoring (not replacing human review, but anchoring it):

**Stage 1 (now):** The health-loop validator must pass, the adapter extracts
fields, and human review assigns 1-5 scores based on adapter output. The June
29, 2026 updated-skill run produced one clean post-refactor sample: all
`procedure_integrity` checks passed, `list-open accepted: 0`, and
`health-loop-state: PASS`.

**Stage 2 (after 3 clean adapter runs):** Define evidence-based score thresholds
per dimension. For example:

- Precision (gate vs. lens): if `dropped_unverified_count / raw_count > 0.4`,
  the lenses are noisy but the evidence-verification gate is filtering
  aggressively. This reflects gate precision (low false-acceptance rate), not
  lens precision. Score these separately: high gate precision + high lens noise
  is a different signal than both being low. A combined precision score of at
  least 3/5 is supportable only if the gate is clean (`failed_lens_count == 0`)
  and lens noise is trending down across sweeps.
- Loop quality: if `validate_health_loop_state.py` passes, `procedure_integrity`
  checklist is all ✅, and `jsonl_open_accepted_count == 0`, loop quality is at
  least 4/5.

The adapter emits the raw values; a thin scoring function maps them to suggested
scores. Human confirms or overrides.

**Stage 3 (after fixture coverage):** Run precision-gate fixtures as part of the
benchmark. Fixture-retention rate feeds into the precision score for the
evidence-verification gate. Recall scoring remains manual until upstream lens
fixtures exist.

Do not skip Stage 2. Running Stage 3 fixtures before the adapter has a stable
extraction contract means fixture results cannot be trusted.

---

## 7. Benchmark Cadence

There is no defined trigger for when to regenerate the benchmark. Proposed
cadence:

| Trigger | Action | Executor |
| --- | --- | --- |
| Health cycle completed (implement → closed) | Run validator and adapter; write delta benchmark if any score-relevant change occurred | Codex (handover from Claude Code) |
| Deferred recommendation implemented | Write delta benchmark section for that dimension only | Codex (manually triggered session) |
| Score-relevant script changed (adapter, gates, staleness checker) | Run adapter smoke test; write delta benchmark only if scores shift | Codex (manually triggered session) |
| Time-based (quarterly backstop) | Run full benchmark refresh if no handover-triggered refresh has occurred that quarter | Codex (manually triggered session) |

The quarterly backstop fires only if no handover-triggered refresh has already
run that quarter. It does not replace the handover pattern. In a healthy loop
with regular health cycles, Codex handover-triggered benchmarks should occur
more frequently than quarterly.

---

## 8. Resolved Decisions

These were open questions; answers are recorded here so future benchmark
refreshes do not re-litigate them.

### 8.1 Surface Separation

**Decision:** Benchmark the tooling surface first. The plugin surface is deferred.

**Rationale:** The tooling surface health loop is self-contained and measurable
with the existing machinery. The plugin surface health is harder — its real
performance signal comes from AL development and documentation quality
(code review outcomes, plan accuracy, commit hygiene), not from the health loop
machinery. Plugin surface metrics need a separate design effort before they can
be scored.

The interim plugin surface signal is ad-hoc friction reports, which feed the
health audit discovery phase via `ingest-plugin-friction`. These are not
benchmark inputs — they feed the health audit, not the benchmark scorecard.
Do not use friction report counts as plugin-surface benchmark evidence until a
separate benchmark design exists for that surface.

**Next step:** When designing plugin-surface metrics, start from observable
AL-development outcomes (e.g., fix-rate on plan tasks, re-work rate on developed
code, accuracy of generated release notes) rather than trying to reuse the
tooling-surface precision/recall frame.

### 8.2 Fixture Scope

**Decision:** Scope the first fixture pass to the `audit-plugin-health` skill
and its direct callees (`discover-plugin-health`, `report-plugin-health`,
`verify-health-finding`). These are **precision-gate fixtures**, not recall
fixtures.

**What this tests vs. what it does not:**

- **Tests:** Whether `verify-health-finding` correctly retains valid findings
  that enter `report-plugin-health` from the findings file. This is the
  evidence-verification gate's precision behavior — it confirms the gate does
  not drop real findings.
- **Does not test:** Whether the lenses in `discover-plugin-health` surface real
  problems that exist in source files. That is recall — detecting what lenses
  missed — and requires upstream fixture injection into source files the lenses
  scan. That is a separate, larger effort.

**Injection point in practice:**

1. Write a synthetic finding block into a copy of a recent findings file.
2. Run `report-plugin-health` against the copy.
3. Verify the synthetic finding appears retained in the output dossier. The
   dispatch to `verify-health-finding` is internal to `report-plugin-health`;
   the observable signal is the output dossier, not the internal agent call.
4. Record the fixture and retained output in `scripts/tests/fixtures/benchmark/`.

### 8.3 Benchmark Ownership

**Decision:** Codex owns the benchmark. A deliberate handover pause is the
integration pattern.

**Rationale:** The benchmark needs to be independent of the Claude Code tooling
that produced the artifacts being scored. Codex is already the host of the
`generate-benchmark-report` skill (`.codex/skills/generate-benchmark-report/`),
making it the natural owner. A handover pause means: after a Claude Code health
cycle completes, the loop explicitly pauses and hands off to Codex to run the
benchmark. Codex returns findings; Claude Code resumes if implementation is
needed.

**Handover pattern:**

1. Claude Code health cycle reaches `stage_completed: implement-plugin-health`.
2. The health-loop breadcrumb records `next_command: none`; do not write
   `run-benchmark` there. `scripts/validate_health_loop_state.py` only accepts
   known health-loop slash commands or `none`, and the benchmark is a Codex-owned
   review step outside that state machine.
3. The user opens a Codex session, points it at the closed breadcrumb and the
   latest health artifacts, and asks it to run `generate-benchmark-report` or a
   delta refresh.
4. Codex writes the delta or refresh to `docs/reviews/`. It should not modify
   `.dev/health-loop-state.md` unless a separate, validator-backed benchmark
   handoff state is introduced.
5. Claude Code reads the new benchmark output on the next session start.

**Current limitation:** This is a manual convention, not an automatic trigger.
The current `.dev/health-loop-state.md` contract is deliberately scoped to the
Claude health loop. If benchmark due-state needs to be machine-readable later,
add a separate benchmark handoff artifact or extend the validator and lifecycle
contract first; do not overload `next_command` with an unrecognized token.

This also means the benchmark cadence is primarily driven by health-cycle
completion and user-initiated Codex sessions, not by a Claude Code cron or
autonomous trigger.

---

## 9. Additional Benchmark Metrics from Self-Healing Literature

The current rubric scores precision, recall, loop quality, and best-practice
alignment. The self-healing pipeline literature names three further metrics that
this loop can compute from artifacts it already produces. Add them as
adapter-extracted signals, not as new human-scored dimensions, until each has a
stable extraction contract (same discipline as §6 Stage 2).

### 9.1 Recovery-Ledger Hit Rate (Disposition Reuse)

**Source concept:** the dev.to pipeline guide lists *recovery-ledger hit rate* —
how often a failure matches a previously-recorded recovery — as a core metric.

**Loop analog:** the JSONL disposition store is this loop's recovery ledger. The
deterministic disposition matcher in `plan-plugin-findings` Phase 1 already
classifies each new finding against prior `accepted` / `declined` /
`grandfathered` / `fixed` events.

**What to compute:** of the findings entering a sweep, the fraction that match an
existing disposition event. Emit it from `scripts/health_disposition_store.py`
alongside the existing counts.

**How to read it:** a finding matching a prior `declined` or `grandfathered`
disposition *should* be suppressed — so a rising hit rate against those states is
evidence the loop is re-surfacing already-decided noise and the §5 suppression
path is not keeping up. A hit against `fixed` events is a regression signal.
**Do not** treat a high hit rate as unambiguously good or bad; always split it by
the matched disposition state, because the states mean opposite things.

### 9.2 Mean Time to Disposition (MTTR Analog)

**Source concept:** mean time to recovery is the headline self-healing metric in
the dev.to guide.

**Loop analog:** the JSONL event store carries timestamps. The interval from a
finding first appearing in a dossier to its closing `fixed` (or `declined`)
event is this loop's time-to-recovery.

**What to compute:** median interval per disposition state, derived from event
timestamps. This needs no new instrumentation — only a reduction over existing
JSONL events.

**Caveat:** this measures human-gated turnaround, not autonomous recovery speed.
A long interval is not necessarily a defect — it can mean a finding is correctly
waiting on a deliberate decision. Report it as a workflow-throughput signal, not
a health score. **Do not** target a low MTTR by auto-closing; the read-only,
user-gated design (see §11) is intentional.

### 9.3 Cascade-Prevention Rate (Evidence Gate)

**Source concept:** the dev.to guide lists *cascade prevention rate* — stopping
one failure from spawning downstream failures.

**Loop analog:** the evidence-verification gate in `report-plugin-health` drops
unverified findings before they reach disposition, planning, and implementation.
Every dropped false finding is a prevented cascade of wasted downstream work.

**What to compute:** `dropped_unverified_count / raw_count` — already surfaced in
§6 as a precision signal. Reframing it as cascade-prevention makes its *value*
legible: it is not just "the lenses were noisy," it is "N downstream plan/implement
cycles were averted." Pair it with §9.1 so a high drop rate that is really the
same recurring false-positive class shows up as a tracking gap, not a win.

---

## 10. Anti-Patterns the Benchmark Must Surface

The dev.to guide names three self-healing anti-patterns. Each maps onto a gap
this guide already tracks; naming them as anti-patterns sharpens why the gap
matters and gives the benchmark something explicit to check for.

- **Healing without observability.** Closing the ledger (the loop's "heal") while
  emitting no token data (§2.4) and only a retrospective procedure check (§2.3)
  is this anti-pattern. It is the concrete reason best-practice alignment is
  capped below 5/5: the loop heals but cannot fully show its work. The benchmark
  should flag any dossier that records a `fixed` close-back with no procedure log
  and no token block.

- **Suppressing without changing constraints.** The literature's "retrying
  hallucinations without changing constraints" maps to promoting a false-positive
  class to `Suppress` (§5) without updating the `discover-plugin-health` dispatch
  prompt. The guide already warns a table status change "has no runtime effect" —
  the benchmark should verify a suppressed class's success metric (zero retained
  findings over two sweeps), not just its table status, so a no-op suppression
  cannot read as resolved.

- **Clean ledger treated as proof.** "Silent error swallowing" maps to §2.3: a
  clean final ledger is not proof every phase-proof step ran. Surfacing the
  `blocked` state from the `implement-plugin-health` checkpoint in the benchmark
  output keeps a corrupt-success run visible instead of swallowed.

---

## 11. External Best-Practice Alignment

Three of the four reviewed sources independently endorse the loop's core
safety design; one names lifecycle gaps it does not yet track. This grounds the
**best-practice alignment** dimension (§3), which otherwise reads as "no new
action needed" with no external criterion.

| External principle | Source | Loop element | Status |
| --- | --- | --- | --- |
| Prompt/source changes never auto-applied; surfaced for human approval | Medium (Evolve) | Loop never auto-edits source; all outputs are read-only observations | Validated |
| Match autonomy to blast radius | Zenity | Read-only audit + user-gated dispositions and plan execution (high blast radius = source edits) | Validated |
| Feed failures back as structured context; failed runs become inspectable artifacts | Union.ai | `blocked` state recorded in the `implement-plugin-health` checkpoint | Validated; motivates the prospective procedure log (§2.3) |
| Persistent memory builds on findings across sessions | Medium (Evolve) | JSONL disposition store exists; cross-sweep false-positive class tracker is deferred | Partial — close by implementing §5 |
| Measure whether controls actually work | Zenity | Suppressed-class success metric (§5); the benchmark itself | Partial — needs §9 metrics + fixtures (§2.2) |
| Monitor sequences, not isolated events | Zenity | Track false-positive *classes* across sweeps, not single findings (§5) | Partial — depends on §5 tracker |
| Plan for retirement / decommissioning | Zenity | Archived skills and agents are not represented in benchmark coverage | Gap — benchmark does not yet account for decommissioned surfaces |

**Note on human-in-the-loop.** Union.ai positions human escalation as a *last
resort* for autonomous infra recovery; this loop is deliberately human-gated at
*every* disposition. That is not a contradiction: Union.ai's domain is
infrastructure failures (cheap, reversible, high-volume), whereas this loop's
"recovery" is editing the plugin's own source (high blast radius, hard to
reverse). Per Zenity's autonomy-to-blast-radius principle, full human gating is
the correct posture here. Record this as a resolved decision, not a gap, so a
future benchmark does not penalise the loop for low auto-recovery.

---

## Sources

This guide incorporates findings from four self-healing / agentic-AI references
(summaries under `docs/`):

- `dev-to-self-healing-ai-agent-pipeline-summary.md` — failure taxonomy,
  metrics-that-matter, and anti-patterns (§9, §10).
- `medium-evolve-self-healing-ai-agents-summary.md` — human-gated diffs and
  cross-session memory (§11).
- `union-ai-self-healing-agents-summary.md` — failures as inspectable context;
  blast-radius framing for human-in-the-loop (§2.3, §11).
- `zenity-agentic-ai-best-practices-summary.md` — autonomy-to-blast-radius,
  control measurement, and lifecycle/retirement (§11).
