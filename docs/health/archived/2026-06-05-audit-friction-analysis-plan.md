# Audit Friction Analysis Plan — 2026-06-05

## Context

The 2026-06-04 plugin-health audit and its follow-on sessions produced two
dossiers (`2026-06-04-plugin-health.md`, `2026-06-04-tooling-health.md`)
containing 168 combined findings — but a material fraction are false
positives or restatements of stale data, and several High findings have now
recurred across three consecutive sweeps without resolution. Sweeps are
running roughly every 1.5 days (11 health commits since May 31) while the
closure rate stays near zero. This plan defines the analysis needed to
quantify that noise, root-cause each friction class, and produce a
prioritized remediation backlog.

This is an analysis plan: its output is a diagnosis report and backlog, not
source edits. Remediation is planned and executed separately (via
`/verify-map-suggestions` → plan → execute).

## Evidence base (verified 2026-06-05)

### F1 — Lens false positives

| Instance | Mechanism | Evidence |
| --- | --- | --- |
| 9× "Move to `.claude/skills/`" for files already there | Surface-placement lens has a hardcoded recommendation (`design-skill-lens-surface-placement.md:48`) and receives no surface parameter — the dispatch context in `lens-invocation-patterns.md` contains no `surface` field, so the lens cannot tell current location from target | `2026-06-04-tooling-health.md:87-89` flags all nine as false positives |
| 2× High complexity findings whose own verdict is "Not an Atomise candidate" | Severity is assigned from phase count alone (`design-skill-lens-complexity.md:39-45`); the verdict lives only in narrative text and is never cross-checked against severity | `2026-06-04-tooling-health.md:27-29` |
| Severity tallies count known noise | `plugin-health-report` Phase 2 counts every finding by severity with no verdict filter, dedup, or suppression step | Tooling summary table reports 62 total; ~11 are lens-calibration noise the dossier itself disclaims |
| Precedent: this is fixable | `quality-agent-lens-structure` emitted 26 false positives on 2026-06-03; after a fix it returned zero on 2026-06-04 | `2026-06-04-tooling-health.md:31-33` |

### F2 — Stale map data

| Instance | Mechanism | Evidence |
| --- | --- | --- |
| Header says "22 agents", 23 exist | Header count is hardcoded prose; the update agent (`sync-documentation-maps-agent-update.md:57`) only replaces the date, never re-derives the count from the audit's `total_files: 23` | `docs/al-dev-agent-map.md:3` (verified live 2026-06-05) |
| "Spawned by: (none found)" while callers exist | Caller list is grep-derived at audit time but stored as static text; drift accumulates between full pipeline runs | 2026-06-04 run fixed 3 caller mismatches, yet the dossier's Graph deltas section still reports catalog-vs-profile drift |
| No count validation gate | `sync-documentation-maps-apply` validates line counts and headers only; `generate-map-doc-sections.py` regenerates marked sections but never the header metadata | Full pipeline completed and committed (`2ab2811`) with the wrong count intact |
| Audits consume stale inputs | The recurrence claim "lens-invocation-patterns.md missing" persisted into 2026-06-04 analysis even though the file was created 2026-06-04 19:03 | `profile-al-dev-shared/knowledge/lens-invocation-patterns.md` exists on disk |

### F3 — No closure loop (recurrence)

- Sync-doc audit-agent grep/dedup ambiguity: High, explicitly "repeat from
  2026-06-03, still open" (`2026-06-04-tooling-health.md:39`).
- `naming-convention-lens` unused `Glob`: identical finding, identical
  severity, two sweeps running.
- Shared-backbone dispatch duplication across the sync skill family: flagged
  every sweep since 2026-06-03, never extracted.
- Every dossier ends "run `/verify-map-suggestions` next" — no
  verify-map-suggestions artifact exists in `.dev/` from any sweep. Findings
  are re-discovered instead of tracked.

### F4 — Process churn

- 11 health commits in 16 days; multiple same-day re-sweeps ("supersedes the
  earlier 2026-06-04 sweep run").
- `.dev/progress.md` shows 10+ sync-documentation-maps dispatches May 31 –
  Jun 4, several without evidence of reaching collect/apply/write.
- Severity churn without closure (sync audit model-fit: High on 06-03 → Low
  on 06-04, issue unchanged) makes diffs between sweeps unreliable as a
  progress signal.

## Analysis tasks

### Phase 1 — Quantify the noise floor

1. **Classify every 2026-06-04 finding** (106 plugin + 62 tooling) into:
   `actionable` / `false-positive` / `monitor-only` / `stale-input` /
   `duplicate-of-prior-sweep`. Source: the two findings files plus the
   2026-06-03 pair for duplicate detection.
2. **Compute per-lens precision**: actionable ÷ total per lens. This ranks
   which of the 22 lenses generate noise (surface-placement and complexity
   are known offenders; the analysis should confirm no others).
3. **Build a cross-sweep recurrence matrix** (2026-06-01 → 06-04): finding ×
   sweep, with severity per cell. Flags both never-closed items and
   severity churn.

Output: noise-floor table + per-lens precision + recurrence matrix.

### Phase 2 — Root-cause the false-positive classes

For each FP class confirmed in Phase 1, document the mechanism chain
(dispatch context → lens rule → aggregation) with file:line references.
The three known chains to verify and complete:

1. Surface-placement: missing surface parameter end-to-end
   (`plugin-health-discover` Phase 1/3.2 → lens line 48).
2. Complexity: severity/verdict decoupling (lens lines 39-45 →
   `plugin-health-report` counting).
3. Aggregation: absence of any suppression/dedup/verdict-filter stage
   between lens output and dossier summary table.

### Phase 3 — Root-cause the stale-data classes

1. Trace the header-count provenance: who writes it, who could recompute it
   (update agent vs `generate-map-doc-sections.py`), and why the apply gate
   misses it.
2. Inventory all statically-stored-but-dynamically-derived fields in both
   maps (counts, "Spawned by", model/tool columns) and classify each as
   script-generatable vs agent-maintained.
3. Determine why audits consumed stale inputs (the lens-invocation-patterns
   case): is there a freshness check on context documents before dispatch?

### Phase 4 — Closure-loop and cadence analysis

1. Measure closure rate: of all High/Medium findings since 2026-06-01, how
   many were resolved before the next sweep ran?
2. Identify why `/verify-map-suggestions` is never reached (the documented
   next step after every dossier).
3. Assess sweep cadence: is re-sweeping before executing the prior dossier
   producing any new signal, or only re-discovering known findings at
   growing token cost (findings file grew 24KB → 52KB in one day)?

### Phase 5 — Synthesize remediation backlog

Write the diagnosis report with a prioritized backlog. Expected candidates
(to be confirmed/refined by Phases 1–4):

1. Pass a `surface` parameter to the surface-placement lens (or scope it to
   the distributed surface only) — kills 9 FPs per sweep.
2. Gate complexity-lens severity on its own verdict — kills 2 High FPs.
3. Add a verdict/suppression filter to `plugin-health-report` so summary
   counts exclude self-disclaimed noise.
4. Derive map header counts from table rows (script or update-agent rule) +
   add a count-consistency gate to `sync-documentation-maps-apply`.
5. Add a recurrence ledger: dossiers annotate repeats as "open since
   YYYY-MM-DD" instead of re-ranking them as new.
6. Cadence policy: no new sweep until the prior dossier's accepted items
   have been verified (`/verify-map-suggestions`) or explicitly declined.

## Deliverable

`docs/health/2026-06-05-audit-friction-analysis.md` containing: noise-floor
metrics, per-lens precision, recurrence matrix, root-cause chains
(file:line), closure-rate measurement, and the prioritized backlog.

## Verification

- Every classification in Phase 1 must cite the finding's line in its
  source findings file; spot-check 10 random classifications against the
  live codebase.
- Every root-cause chain must reproduce: reading the cited lines must show
  the claimed mechanism (e.g., line 48 hardcoded recommendation; absent
  surface field in the dispatch context table).
- Backlog items must each name the FP/staleness instances they eliminate so
  the next sweep can confirm the fix empirically (precedent: the
  structure-lens fix verified by its 26 → 0 drop).
