# Health Finding Dispositions

The closure ledger for health-audit findings. One row per dispositioned
finding. Consumed by `/plugin-health-report` (suppresses `declined` and
`grandfathered` findings from counts and ranking; treats re-flagged `fixed`
findings as suspect lens output) and by `/verify-map-suggestions` (plans
only `accepted` findings).

Rules:

- Match rows by **object + issue essence**, not exact wording — lenses
  rephrase between sweeps.
- `fixed` rows cite the resolving commit. If a later sweep re-flags a
  `fixed` item, verify against the live file before trusting the finding —
  the lens may be re-issuing a stale complaint.
- `declined` and `grandfathered` rows record settled decisions. A sweep may
  not re-litigate them; revisiting one requires editing this file first.
- Append new rows at the bottom of the table; never rewrite history.

| Object | Issue | Disposition | Date | Evidence / note |
|--------|-------|-------------|------|-----------------|
| al-dev-solution-architect | `TESTABILITY_COMPLETE: no` had no caller halt procedure | fixed | 2026-06-04 | `2d83dab` — plan halts until testability resolved |
| al-dev-investigate | Step 5 inline 98-line findings template (bloat) | fixed | 2026-06-04 | `86576bf` — extracted to `knowledge/investigate-findings-template.md` |
| al-dev-perf | Inline classification + 60-line report template (bloat) | fixed | 2026-06-04 | `b02b332` — extracted to `knowledge/perf-report-template.md` |
| al-dev-commit | Repeated dispatch patterns across phases (bloat, partial) | fixed | 2026-06-04 | `e0ea5eb` — dispatch frame extracted; Phase 0 gate still open as a separate finding |
| al-dev-ticket | Mixed-input precedence rule ambiguous | fixed | 2026-06-04 | `966d81b` — explicit IF/THEN/ELSE; 19:43 sweep re-flagged the fixed text (lens misjudgment) |
| al-dev-plan-swarm-validate | Description promised critics/synthesis the body lacked | fixed | 2026-06-04 | `76b0c5b` — description reconciled; body depth tracked separately |
| sync-documentation-maps-write | Phase 0 status guard inverted | fixed | 2026-06-04 | `d8146e0` — guard corrected; was the one live bug of the 06-04 tooling sweep |
| al-dev-diagram-generator | Phase 3 lacked one-vs-two diagram routing | fixed | 2026-06-04 | `45f7480` |
| projection-sync | Phase 0 Resume/Restart had no non-response default | fixed | 2026-06-04 | `7cebb69` — defaults to Restart |
| align-harness-repos | Step 5 permitted discretionary replacement path | fixed | 2026-06-04 | `d8067cc` — pinned to canonical `~/.harness-config` |
| verify-map-suggestions | Phase 3 verification commands unmapped to finding verbs | fixed | 2026-06-04 | `7835800` — verb → command table |
| sync-documentation-maps-agent-audit | Step 3 grep union/dedup unsequenced (open since 2026-06-03) | fixed | 2026-06-05 | `a365db9` — grep deleted; callers from `scripts/derive-agent-callers.py` |
| docs/al-dev-agent-map.md | Header count stale (22 vs 23 on disk) | fixed | 2026-06-05 | `3da3c72` — counts generator-owned in Coverage markers |
| align-harness-repos | Name implies alignment; behavior is validation-only | grandfathered | 2026-06-05 | Deliberate: name retained when the skill was repointed at `validate_harness_neutrality.py` (al-dev-align archived). Do not re-flag; revisit only by editing this row. |
| al-dev-support-reply-drafter | Model fit: downgrade sonnet → haiku | declined | 2026-06-05 | sonnet was a deliberate 2026-06-01 assignment (`3bed965`); reply quality outranks the token saving |
| analyze-architectural-design, plugin-health-discover, plugin-health-report | Naming: not verb-first `{verb}-{object}-{aspect}` | grandfathered | 2026-06-05 | Workflow-phase family names are intentional; all three predate the convention |
| sync-documentation-maps-agent-update, sync-documentation-maps-skill-update | Model fit: upgrade haiku → sonnet for map synthesis | declined | 2026-06-05 | haiku retained: `3da3c72` moved the hardest synthesis (count derivation) to the generator, and `a365db9` made callers script-derived. Revisit only if update artifacts regress. |
| maintainer surface | No tooling lifecycle diagram (Layer 1 scoped to distributed skills) | accepted | 2026-06-05 | Genuine doc gap, flagged 2026-06-04 and implicitly since; add `docs/al-dev-tooling-skills-map.md` or document the exclusion in CLAUDE.md — awaiting implementation |
| align-harness-repos | No durable pass/fail validation artifact for downstream gating | declined | 2026-06-05 | No downstream consumer exists; writing the artifact now would create exactly the orphaned-artifact class the audits flag. Revisit when projection-sync or sync-write actually gates on it. |
| verify-map-suggestions | Name says "verify" but the skill is a rubber-duck-to-plan pipeline (name-fit, 2026-06-05 sweep) | fixed | 2026-06-05 | `6f131a1` — renamed to `plan-health-findings`; description widened to cover the verify-then-plan pipeline |
| plan-health-findings | Skill name (lineage: plan-map-changes → al-dev-map-suggestions-verify → verify-map-suggestions → plan-health-findings) | grandfathered | 2026-06-05 | Name settled after three renames. Future name-fit findings on this skill are suppressed; a fourth rename requires editing this row first. |
