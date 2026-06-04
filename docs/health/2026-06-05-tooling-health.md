# Tooling Health — 2026-06-05

Source findings: `docs/health/2026-06-05-tooling-findings.md` (21 lenses, none failed;
`design-skill-lens-surface-placement` excluded per discover §3.1b).

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 1      | 5       | 0      | 6     |
| Medium   | 4      | 15      | 0      | 19    |
| Low      | 2      | 9       | 0      | 11    |
| **Total**| **7**  | **29**  | **0**  | **36**|

New this sweep: 28 · Recurring from prior sweeps: 8 (annotated inline) ·
Stale/invalid (dropped): 4 · No-action lens observations (excluded): 26

Top 5 ranked actions:

1. **plugin-health-report** — Atomise: split parse/gating (Phases 0–1d) from
   rank/write (Phases 2–4) so dossiers can be re-ranked without re-gating
   (verified against live file 2026-06-05).
2. **sync-documentation-maps-agent-audit** — define the failure path when
   `scripts/derive-agent-callers.py` errors or returns empty; today the agent
   has no instruction and could silently fall back to ad-hoc derivation
   (verified against live file 2026-06-05).
3. **plugin-health-discover** — cadence guard has no explicit
   confirmation/rejection branch; add "on confirmation proceed to Phase 1; on
   rejection stop" (verified against live file 2026-06-05).
4. **plugin-health-report** — define "monitor-only" operatively in Phase 1 so
   the verdict=None exclusion rule is self-explanatory (verified against live
   file 2026-06-05).
5. **plugin-health-discover** — restructure Phase 3 (nested 3.1/3.1b/3.2/3.3)
   into top-level phases (open since 2026-06-04; verified still nested
   2026-06-05).

Failed lenses: none.

## Design suggestions

### High

- **plugin-health-report** (Atomise, verdict=Atomise) | 8 phases carrying two
  separable concerns: (A) locate/parse findings + recurrence/staleness/
  disposition gates (Phases 0–1d); (B) rank + write dossier + present
  (Phases 2–4). Every invocation carries both. | Split into a parse/gate step
  that emits a validated findings structure and a dossier step that ranks and
  writes; re-ranking then skips re-gating. *(verified against live file
  2026-06-05)*

### Medium

- **naming-convention-lens ⇄ plugin-health-discover** (Align) | Agent's Inputs
  table requires `convention_doc`, but the discover skill's Phase 2 aggregation
  never documents building it — every other required context field has an
  explicit construction step. The dispatch works only if the operator infers
  the field from `lens-invocation-patterns.md`. *(open since 2026-06-04)* |
  Add `convention_doc` construction to discover Phase 2 (path to
  `docs/al-dev-naming-convention.md`) and show it in the §3.2 prompt list.
- **sync-documentation-maps + sync-documentation-maps-collect** (Connect) |
  Both skills duplicate the same background-dispatch handoff (dispatch prompt
  frame, artifact schema, checkpoint merge), each pointing at skill-local
  pattern files. The canonical doc `knowledge/background-agent-dispatch.md`
  **already exists** (2026-06-03) but neither skill references it — drift risk
  unresolved. *(open since 2026-06-04; action corrected: reference the
  existing doc, do not create a new one)* | Update both skills to cite the
  canonical doc and trim skill-local duplication.
- **align-harness-repos** (Atomise, verdict=Atomise) | Two separable concerns:
  validation (Steps 1–3, useful standalone in CI/pre-commit) and user-gated
  fixing (Steps 4–6). | Extract a validation-only entry point; keep the
  current skill as the gate-then-fix wrapper. *(adjacent to the 2026-06-05
  grandfathered naming row — that row settles the name, not the structure)*
- **verify-map-suggestions → execution** (Extend) | The discover → report →
  verify chain ends at a written plan; no skill consumes the plan to dispatch
  implementation. *(open since 2026-06-04)* | Add an execution step or
  document the post-plan handoff expectation in verify-map-suggestions.

### Low

- **plugin-health-discover** (Connect) | Workflow-based lens dispatch is
  intentionally different from background-agent dispatch; the distinction is
  undocumented. *(open since 2026-06-04)* | Add a "what this pattern is not"
  note to `knowledge/background-agent-dispatch.md`.
- **analyze-architectural-design** (Extend) | `docs/al-dev-plugin-synthesis.md`
  is consumed by no downstream skill. | Either feed it into
  verify-map-suggestions or document it as a human-review artifact.

Monitor-only / no-action lens observations (excluded from counts): the
usage-patterns lens emitted 26 Low "findings" stating that agents meet only
2 of its 3 inline criteria — i.e., that they are *not* inline candidates —
with self-contradictory fixes ("document Inputs/Outputs" on agents that
already have them). Lens-quality signal, not surface findings; consider
tightening the lens to emit only when all criteria are met.

## Quality findings

### High

- **sync-documentation-maps-agent-audit** (clarity) | The instruction forbids
  grep fallback for caller derivation but defines no behaviour when
  `scripts/derive-agent-callers.py` fails or returns empty
  (`.claude/agents/sync-documentation-maps-agent-audit.md:77`). | Add: on
  script failure or empty output, stop and report the error; never fall back
  to grep. *(verified against live file 2026-06-05)*
- **plugin-health-discover** (clarity) | Cadence guard: "Proceed only on
  explicit confirmation" defines no explicit action for confirmation vs
  rejection. | Add explicit branches: confirm → Phase 1; reject → stop.
  *(verified against live file 2026-06-05)*
- **plugin-health-report** (clarity) | "Monitor-only" (Phase 1 verdict=None
  rule) has no operative definition. | Define: observations requiring
  tracking but no implementation action; excluded because they are expected
  behaviour, not open work. *(verified against live file 2026-06-05)*
- **plugin-health-discover** (bloat) | Phase 3 still carries nested
  3.1/3.1b/3.2/3.3 sub-steps (~48-line §3.2 mixing prompt construction,
  invocation, and result processing). *(open since 2026-06-04)* | Promote the
  sub-steps to top-level phases. *(verified still nested 2026-06-05)*
- **review-documentation-map** (bloat) | Phase 4 spans ~71 lines covering
  compare, style-guard, and report operations as nested 4a–4c. **⚠ possibly
  stale** — this nesting was the deliberate result of the 2026-06-04 fixes
  (`40f1ad8`, `8a5a5fa`) for the prior sweep's bloat finding; the lens may be
  re-litigating a settled restructure. Excluded from top-5; verify intent
  before acting. *(open since 2026-06-04)*

### Medium

- **design-agent-lens-caller-alignment** (clarity) | Double-negative dispatch
  rule ("no passed context block is not evidence…"). | Rephrase positively.
- **design-skill-lens-handoff-gaps** (clarity) | "Zero matches = orphaned"
  doesn't state whether the originating file is excluded from the grep
  scope. | Define: zero matches across all *other* SKILL.md files.
- **quality-skill-lens-structure** (clarity) | Argument-hint detection
  patterns underspecified (exact match? flags?). | Enumerate the operative
  patterns.
- **sync-documentation-maps-skill-audit** (clarity) | Date-normalisation regex
  edge cases unstated (nested parentheses in paths). | Document the
  assumption or anchor the pattern.
- **plugin-health-discover** (bloat) | Resume detection and dispatch flow
  repeat the same "check files, build sets, filter" block. | Extract a named
  decision block.
- **plugin-health-discover** (clarity) | `already_inline_candidates` filter
  criteria undefined — this sweep had to guess an empty list when building
  context. | Define the qualifying criteria beyond single-use.
- **plugin-health-report** (clarity) | Placement of the "Monitor-only
  (excluded from counts)" note ambiguous (inline vs summary block). | Specify
  a single-line note after Design suggestions.
- **review-documentation-map** (clarity) | "Ordering dependencies" threshold
  in Phase 2a undefined. | Define as audit-output dependency between files.
- **review-documentation-map** (description) | Description says "a plugin
  documentation map" (singular) though the skill handles two surfaces via
  `--surface`. | Reword to name both.
- **sync-documentation-maps-collect** (clarity) | Resume/restart conditional
  still incomplete: the "status unset or 'audit'" clause lacks an explicit
  action. *(open since 2026-06-04; was High on 2026-06-04)* | Add the explicit
  default action.
- **sync-documentation-maps-collect** (bloat) | Phases 2 and 3 reconstruct
  artifact state twice with overlapping parse/validate logic. | Merge into a
  single read-and-prepare phase.
- **sync-documentation-maps-apply** (description) | Description omits the
  count-consistency gate (catalog rows vs disk) added in `5138844`, a
  substantive validation that can skip a surface. | Mention it.
- **verify-map-suggestions** (bloat) | Phases 1/1b/2 repeat the
  read-subject + staleness-check pattern. *(open since 2026-06-04)* |
  Extract a shared sub-block.
- **verify-map-suggestions** (clarity) | Valid finding-type arguments are
  exemplified, never enumerated. | List the full set.
- **verify-map-suggestions** (name-fit) | Name says "verify" but the skill is
  a rubber-duck-to-plan pipeline that writes implementation plans; trigger
  phrases emphasise planning. | Rename (e.g. plan-oriented) or widen the
  description to cover the full pipeline.

### Low

- **design-skill-lens-surface-placement** (structure) | Empty-findings example
  uses asterisk emphasis instead of the family's underscore form (line 61). |
  Align the example.
- **sync-documentation-maps** (clarity) | Progress-file append shown as a
  heredoc; repo conventions warn against heredocs for file edits. | Show the
  literal text to append instead.
- **plugin-health-discover** (clarity) | The workflow dispatch reference doc
  is cited without a fallback if absent. | Name the inline examples as the
  fallback.
- **sync-documentation-maps-apply** (clarity) | `argument-hint` says
  "[RUN_ID from checkpoint]" but the body requires `--team-ids <id>[,<id>]`
  (line 8 vs 38/42). | Correct the hint. *(verified against live file
  2026-06-05)*
- **align-harness-repos** (structure) | Uses "Step N" headings where the
  surface convention is "Phase N". | Align heading style.
- **plugin-health-report** (structure) | Sub-phases 1b/1c/1d use letter
  suffixes against the dotted-notation majority. | Standardise.
- **review-documentation-map** (structure) | Mixed sub-step notation
  (2a/2b, 4a/4b/4c). | Standardise.
- **sync-documentation-maps-collect** (structure) | Letter-suffix sub-steps
  (2a/3a) inconsistent with the family. | Standardise.
- **verify-map-suggestions** (structure) | Letter-suffix sub-steps (1b/2b). |
  Standardise.

## Naming violations

*No issues found.* (The four 2026-06-05 grandfathered names were respected by
the lens and are not re-litigated here.)

## Stale (dropped)

- **design-skill-lens-complexity** (clarity, was High) | Claimed no handling
  for 8+ phase skills without separable concerns — the live file covers this
  explicitly ("however many phases it has — takes verdict `None` and severity
  Low", fixed by `3f0de0d` on 2026-06-05). Claim does not hold.
- **design-skill-lens-preplanning** (clarity, was High) | Claimed exact-match
  vs prefix-match contradiction — the two rules govern different operations
  (skill selection vs diagram node-label matching). Claim does not hold.
- **sync-documentation-maps** (clarity, was High) | Flagged dispatch-mechanism
  tokens in the skill body as needing harness-neutral wording — repo policy
  explicitly scopes the neutrality rule to outputs and the shared surface;
  repo-local maintainer tooling is harness-specific by design. Claim invalid.
- **sync-documentation-maps** (clarity, was Medium) | Claimed
  `AUTO_UPDATE=false` is improper assignment syntax — it is valid shell
  assignment. Claim does not hold.

## Dispositioned (suppressed)

- align-harness-repos — name retained (grandfathered 2026-06-05).
- analyze-architectural-design / plugin-health-discover / plugin-health-report
  — workflow-phase family names (grandfathered 2026-06-05).

## Notes

- Prior-sweep findings not re-raised by this sweep and still undispositioned:
  model upgrades for the two map-update agents (model-fit, 2026-06-04), the
  missing tooling-surface lifecycle diagram (preplanning, 2026-06-04), and the
  align-harness-repos durable validation report (handoff-gaps, 2026-06-04).
  Record dispositions for these or expect churn in future sweeps.
- Lens-quality signal this sweep: 26 no-action observations (usage-patterns)
  and 4 dropped findings (2 clarity FPs against lens agents, 1 policy
  mismatch, 1 shell-syntax FP). Tightening usage-patterns emission criteria
  would remove most of the noise.
