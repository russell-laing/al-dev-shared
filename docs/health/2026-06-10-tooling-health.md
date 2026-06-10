# Tooling Health — 2026-06-10

surface: tooling
dimensions:

- quality

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | —      | 14      | —      | 14    |
| Medium   | —      | 28      | —      | 28    |
| Low      | —      | ~73     | —      | ~73   |

New this sweep: 0 confirmed actionable · Recurring / already dispositioned: the
remainder (annotated inline) · Stale (dropped): 28 (26 false-positive structure +
2 stale bloat)

**Headline:** This sweep re-discovered findings already dispositioned earlier
today. `docs/health/dispositions.md` holds **106 tooling/quality rows, ~90 dated
2026-06-10** — covering essentially every object in this sweep (most `fixed`, the
rest `accepted` awaiting implementation, a few `declined`). Every one of the 14
High findings targets a file modified in git today, so all are `⚠ possibly stale`
under the staleness gate; spot-checks confirm the claims no longer hold or are
already settled. **Net genuinely-new actionable work after suppression,
staleness verification, and candidate spot-checks: 0.**

Top actions — status after this session's work:

1. **✅ DONE — Flipped 20 stale-open `accepted` ledger rows to `fixed`.** Each was
   verified against its live file (the fix is present) and closed citing the
   implementing commit (`fc765db`, `d11ce71`, `12b1a69`, `14b8315`, `442494a`,
   `6851778`, `d7fc629`, `7e0b0e7`, `9735c2f`). `check_ledger_staleness.py` now
   reports **0 stale-open** rows (was 20). The 5 remaining effective-open accepted
   rows (339, 341, 342, 344, 348) have no commits since their row date — genuine
   pending work for `/plan-health-findings`.
2. **✅ DONE (no edit) — Dropped the agent "missing `## Outputs` header" class (26
   files).** Confirmed false positive: every live agent file has a `## Outputs`
   header (`quality-agent-lens-bloat.md:14`, `design-agent-lens-caller-alignment.md:17`,
   `sync-documentation-maps-agent-audit.md:22`). The lens **definition is correct**
   (`quality-agent-lens-structure.md:47` checks Inputs/Outputs presence at Medium) —
   this was a one-off `haiku` subagent misread, not a lens-text defect. **No lens
   edit made** (would fix a non-bug).
3. **✅ VERIFIED NOT A FINDING — `design-skill-lens-complexity` Atomise-vs-Absorb.**
   False premise: Atomise targets 6+-phase skills (`:26-32`); Absorb targets exactly
   2-phase zero-agent skills (`:34-37`). The populations are mutually exclusive, so
   "both could apply" cannot occur. Clarity-lens subagent over-read; no action.
4. **✅ VERIFIED NOT A FINDING — `sync-documentation-maps-agent-audit` failure path.**
   Live text (`:87-93`) is consistent: "stop caller cross-referencing" and "skip
   `caller_mismatch` detection for this run" are the same action at two granularities,
   and "state in the report's `summary`" makes clear the audit continues to Step 4.
   At most an optional one-clause polish; not the High issue the lens labeled it.
5. **No further new work.** The remaining bloat / clarity / description / name-fit /
   structure findings map to existing `accepted`, `fixed`, or `declined` ledger rows
   dated 2026-06-06…2026-06-10 (see Quality findings + suppressed/stale lists below).

Failed lenses: none — all 10 quality lenses returned.

## Design suggestions

_Not requested in this run._

## Quality findings

Raw lens output is preserved in `docs/health/2026-06-10-tooling-findings.md`.
Below, each class is annotated with its disposition reality.

### Bloat

- **Agent — sync-documentation-maps-agent-audit / -skill-audit** | High | "Instructions
  section >30 lines" — **suppressed: `declined` 2026-06-06** ("Bloat: Instructions
  (Steps 1–6) >30 lines" / "~52 lines"). Settled decision; not re-litigated.
- **Skill — plan-health-findings / plugin-health-discover** | High | "9–10 top-level
  sections" — **stale (dropped):** ledger marks both `fixed` 2026-06-10 (`1b6f33e`,
  `c3ff35d`); live files now have **6** and **5** `##` sections respectively, contradicting
  the lens's 9/10 claim.
- **Skill — plugin-health-report / record-health-dispositions / sync-documentation-maps /
  sync-documentation-maps-write / sync-documentation-maps-collect / sync-documentation-maps-apply /
  audit-knowledge-quality / projection-sync** | High/Medium | "too many sections / nested
  phases" — **mostly already dispositioned 2026-06-10:** `record-health-dispositions`
  bloat is `declined`; `sync-documentation-maps`, `-collect`, `-apply`,
  `audit-knowledge-quality` bloat/clarity rows are `fixed`; `sync-documentation-maps-collect`
  Phase-1 nesting is `accepted` (awaiting implementation). `plugin-health-report` Phase 1
  remains nested (1b/1c/1d) on the live file despite a `fixed` row — **possible regression;
  verify before any action.**
- **Skill — align-harness-repos, fix-knowledge-quality, plugin-health-audit, review-maps**
  | Medium/Low | bloat/redundancy — map to `accepted` 2026-06-10 rows
  (`align-harness-repos` historical note; `fix-knowledge-quality` Phase 3 dispatch
  boilerplate; `plugin-health-audit` resume paths) **awaiting implementation.**

### Clarity

- **Agent — design-skill-lens-complexity** | High | Atomise-vs-Absorb precedence undefined —
  **candidate new** (see Top action 3); ⚠ subject changed today.
- **Agent — sync-documentation-maps-agent-audit** | High | "stop caller cross-referencing"
  vs "skip caller_mismatch" — **candidate new** (see Top action 4); ⚠ subject changed today.
- **Agent — sync-documentation-maps-agent-audit (Step 4 `(none)` normalization)** | Medium |
  **`accepted` 2026-06-10** ("Step 4 normalization target unstated") — awaiting implementation.
- **Agent — sync-documentation-maps-skill-audit ("same clause")** | Medium | **`fixed`
  2026-06-10** ("write verbs lack operative definition") — suspect re-flag; verify, likely stale.
- **Agent — caller-alignment / handoff-gaps / shared-backbone / surface-placement /
  naming-convention-lens** | Medium/Low | vague-qualifier findings — map to `accepted`/`fixed`
  2026-06-10 rows for the same objects (working-contract, "independently runnable",
  "small delta", etc.).
- **Skill — plan-health-findings ("rubber-duck normally"), sync-documentation-maps-collect
  (placeholders), sync-documentation-maps-write (grep pattern / recovery branch)** | High |
  subjects all `fixed`/`accepted` 2026-06-10; ⚠ changed today — verify before trusting.
- **Skill — audit-knowledge-quality, fix-knowledge-quality, plugin-health-discover,
  plugin-health-report, projection-sync, record-health-dispositions, sync-documentation-maps,
  sync-documentation-maps-apply** | Medium/Low | each maps to an `accepted` or `fixed`
  2026-06-10 ledger row of the same essence.

### Structure

- **Agent — "missing `## Outputs` section header" (all 26 agents)** | Low |
  **STALE (DROPPED) — confirmed false positive.** Live agent files all carry a `## Outputs`
  header. `quality-agent-lens-structure` mis-reported; treat as a lens bug (Top action 2),
  not 26 findings.
- **Agent — code-block language tags (agent-audit, skill-audit, surface-placement, agent-update)**
  | Low | **`declined` 2026-06-06** (MD040 on agent files) — suppressed.
- __Skill — missing code-block language tags (align-harness-repos, audit-knowledge-quality,
  fix-knowledge-quality, plan-health-findings, plugin-health-report, projection-sync,
  record-health-dispositions, review-maps, sync-documentation-maps_, etc.)_* | Low/Medium |
  several map to `accepted` 2026-06-10 rows; the rest are minor MD040 polish. Low priority.
- **Skill — plugin-health-audit / plugin-health-discover argument-hint documentation** |
  Medium | `argument-hint` lists `--surface/--dimension/--resume` but body under-documents
  per-argument behavior — minor; `plugin-health-audit` description row is `accepted` 2026-06-10.

### Name-fit

- **Skill — fix-knowledge-quality, review-maps** | Medium | name vs primary verb
  (skills dispatch/coordinate rather than fix/review). `review-maps` and
  `fix-knowledge-quality` both have `accepted` 2026-06-10 rows; name-rename essence
  is adjacent but not identical — low-value cosmetic, defer.
- **Skill — align-harness-repos, projection-sync, plugin-health-report, others** | Low |
  optional rename suggestions — non-actionable polish.
- **Agent — all 26** | Low | `_No issues found._` — names follow the established
  `<dimension>-<object>-lens-<aspect>` convention.

### Description

- **Skill — audit-knowledge-quality, review-maps** | Medium | description overstates
  scope (defers fixes / is a dispatcher). `review-maps` description row is `accepted`
  2026-06-10; `audit-knowledge-quality` is a candidate refinement but low value.
- __Agent — design-agent-lens-_ "X suggestions" vs "Findings" header wording_* | Low |
  cosmetic description/header wording drift; `caller-alignment` and `model-fit` already
  `accepted` 2026-06-10. Defer as a batch.

## Naming violations

_Not requested in this run._

## Graph deltas

_Not requested in this run (tooling surface — section omitted by contract)._

## Dispositioned (suppressed)

- `sync-documentation-maps-agent-audit` — Bloat: Instructions >30 lines — **declined** 2026-06-06
- `sync-documentation-maps-skill-audit` — Bloat: Instructions ~52 lines — **declined** 2026-06-06
- `record-health-dispositions` — Bloat: Phase 2 guard patterns / Phases 3–4 repeat — **declined** 2026-06-10
- Agent code-block language tags (agent-audit/skill-audit/surface-placement/agent-update) — **declined** 2026-06-06
- (Plus ~70 `fixed` and ~25 `accepted` 2026-06-10 rows whose essences match findings above —
  annotated inline rather than re-listed.)

## Stale (dropped)

- Agent "missing `## Outputs` header" (26 files) — false positive; live files have the header.
- `plan-health-findings` Bloat (9 sections) — `fixed` `1b6f33e`; live has 6 sections.
- `plugin-health-discover` Bloat (10 sections) — `fixed` `c3ff35d`; live has 5 sections.
