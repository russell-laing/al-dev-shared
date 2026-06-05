# Health Finding Dispositions

The closure ledger for health-audit findings. One row per dispositioned
finding. Produced by `/record-health-dispositions` (or direct edits).
Consumed by `/plugin-health-report` (suppresses `declined` and
`grandfathered` findings from counts and ranking; treats re-flagged `fixed`
findings as suspect lens output) and by `/plan-health-findings` (plans
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
| al-dev-ticket | Clarity: "first token decides" precedence under-specified (re-flag) | fixed | 2026-06-05 | `966d81b` — explicit `^(FD-?)?[0-9]+$` regex + IF/THEN already live; 2026-06-05 plugin sweep re-flagged fixed text. Verified against live file. |
| al-dev-commit | Bloat: repetitive dispatch blocks across phases (re-flag) | fixed | 2026-06-05 | `e0ea5eb` — dispatch frame extracted; live file cites `knowledge/commit-dispatch-template.md` once per phase. Verified against live file. |
| al-dev-plan-swarm-validate | Description: 6-critic dispatch not shown in body (re-flag) | fixed | 2026-06-05 | `76b0c5b` — live body enumerates all 6 parallel Agent dispatches + Dispatch Pattern section. Verified against live file. |
| al-dev-develop | Clarity: undefined `<src-file>` placeholder and unexplained `-nt` operator | fixed | 2026-06-05 | Not reproduced against the live file (no such pseudo-code); finding retired during rubber-duck |
| al-dev-fix | Clarity: ambiguous `IF complexity == 'medium' or 'complex'` branch | fixed | 2026-06-05 | `b522c6a` — explicit MEDIUM/COMPLEX branches |
| al-dev-interview | Clarity: INTERVIEW COMPLETE gate has no else clause | fixed | 2026-06-05 | `4a81c4b` — mandatory categories + recovery decision |
| al-dev-lint | Clarity: no fallback when neither `al-compile` nor `al compile` available | fixed | 2026-06-05 | `83e8cb3` — stop-and-report fallback added |
| al-dev-plan-preflight | Clarity: "substantive answer" undefined | fixed | 2026-06-05 | `05e4dc3` — substantive-answer criteria defined inline |
| al-dev-developer-tdd, al-dev-developer-traditional | Bloat: AL coding standards duplicated near-verbatim | fixed | 2026-06-05 | `804b0e1` — deduped to existing `knowledge/al-developer-patterns.md` |
| al-dev-developer-tdd, al-dev-developer-traditional | Shared-backbone: identical dispatch pattern across /al-dev-develop and /al-dev-fix | fixed | 2026-06-05 | Already canonical in `knowledge/developer-invocation-patterns.md`; rubber-duck verdict: no change needed |
| al-dev-solution-architect | Bloat: 130-line workflow, repeated MCP guidance | fixed | 2026-06-05 | `5fff2c7` — moved to `knowledge/solution-architect-research-patterns.md` |
| al-dev-interview | Bloat: 90-line interview-process section with nested categories | fixed | 2026-06-05 | Already delegated to `knowledge/interview-question-bank.md`; rubber-duck verdict: no change needed |
| al-dev-commit-hook-fixer | Bloat: 74-line procedure with nested Steps 1–5 | fixed | 2026-06-05 | `0200d9e` — tables moved to `knowledge/commit-hook-recovery-patterns.md` |
| al-dev-commit-lint-fixer, al-dev-release-notes-writer, al-dev-commit-analyzer, al-dev-script-engineer, al-dev-support-researcher, al-dev-diagnostics-fixer | Bloat: oversized/overlapping sections | fixed | 2026-06-05 | `99c4d95`, `72387a4`, `e910dab`; analyzer bloat folded into `9e441d9` |
| al-dev-solution-architect | Clarity: analogue yes/no examples; TESTABILITY_COMPLETE criteria | fixed | 2026-06-05 | `630d91f` — verdict examples + explicit testability gate |
| al-dev-commit-lint-fixer, al-dev-developer-tdd, al-dev-developer-traditional, al-dev-explore, al-dev-support-reply-drafter, al-dev-commit-recover-fixer | Clarity: vague qualifiers / undefined terms | fixed | 2026-06-05 | `99c4d95`, `b990285`, `f5d1166`, `4b9ba04`; support-reply-drafter link marker already documented (skip) |
| al-dev-code-review | Name-fit: too generic vs specialist reviewers | fixed | 2026-06-05 | `750068d` — renamed to `al-dev-general-code-reviewer` |
| al-dev-ticket-agent | Name-fit: "agent" classifier not verb | fixed | 2026-06-05 | `b941a28` — renamed to `al-dev-ticket-context-writer` |
| al-dev-commit-agent-analysis, al-dev-commit-agent-execute | Name-fit (Low): awkward suffixes | fixed | 2026-06-05 | `1da22e6`, `319e4c7` — renamed to `al-dev-commit-analyzer` / `al-dev-commit-executor` |
| al-dev-explore, al-dev-commit-analyzer, al-dev-release-notes-writer | Structure (Low): code-fence / step-numbering | fixed | 2026-06-05 | `f5d1166`, `9e441d9`, `72387a4` |
| al-dev-consolidate, al-dev-document, al-dev-help, al-dev-perf, al-dev-plan, al-dev-release-notes, al-dev-review-develop, al-dev-ticket, commit-recover | Clarity: vague qualifiers / undefined terms | fixed | 2026-06-05 | `d1fd1ff` (perf/ticket/commit-recover); consolidate/document/help/plan/release-notes/review-develop verified already-explicit (rubber-duck skip) |
| al-dev-consolidate, al-dev-develop, al-dev-explore, al-dev-plan-final-review, al-dev-support-reply | Description drift | fixed | 2026-06-05 | `e9622f2` (explore/plan-final-review/support-reply); consolidate/develop verified already-accurate (skip) |
| al-dev-support-reply | Structure: argument-hint contradicts two usage modes | fixed | 2026-06-05 | `8469b90` |
| al-dev-lint, al-dev-perf, al-dev-plan-swarm-validate, al-dev-review-develop-preflight, al-dev-ticket, commit-recover, verify-commits | Structure (Low): missing `bash` language tags | fixed | 2026-06-05 | Already satisfied — MD040 clean (rubber-duck verified opening fences already tagged) |
| al-dev-commit-agent-analysis | Caller-alignment: REPO documented required but dispatch never passes it | fixed | 2026-06-05 | `9e441d9` — REPO documented as inferred from working dir |
| al-dev-developer-tdd, al-dev-developer-traditional | Caller-alignment (Low): inputs under-specify inline context fields | fixed | 2026-06-05 | `b990285` — Context-Fields reference added |
| al-dev-consolidate | Surface-placement: no agents; references internal repo paths | fixed | 2026-06-05 | `6131b7b` — BREAKING: moved to `.claude/skills/` (removed from distribution) |
| al-dev-commit (chain) | Handoff-gap: no post-commit orchestration consumer | declined | 2026-06-05 | Net-new skill design; deferred to a dedicated /al-dev-plan design pass. Revisit there, not via re-sweep |
| al-dev-fix, al-dev-consolidate | Handoff-gap (Low): test-plan.md / sessions-index.md unconsumed | declined | 2026-06-05 | test-plan.md already consumed by al-dev-fix/al-dev-develop (moot); sessions-index consumer deferred to the same design pass |
| al-dev-support-reply-drafter | Scope-isolation: Split internal-findings vs customer-reply into separate agents | declined | 2026-06-05 | Creates a new agent for a marginal separation; heavier than a cleanup and not selected in the 2026-06-05 accept pass. Revisit only by editing this row. |
| al-dev-commit-lint-fixer | Clarity: `.git/.commit-baselines` written unconditionally; documented `.dev/` fallback never implemented | accepted | 2026-06-05 | Compute `BASELINE_FILE` conditionally before the write loop — awaiting implementation |
| al-dev-plan-swarm-validate | Name-fit: name says "validate"; behavior drafts a plan then red-teams it | accepted | 2026-06-05 | Rename (e.g. `al-dev-plan-critic-review`) or re-scope — awaiting implementation |
| al-dev-commit | Bloat: 18 top-level Step/Phase headers; structural consolidation (header/verbosity aspect) | accepted | 2026-06-05 | Consolidate into ~5 phase groups; dispatch-frame aspect already fixed (`e0ea5eb`) — awaiting implementation |
| al-dev-plan-preflight | Bloat: Resume Modes A/B/C repeat near-identical file-loading | accepted | 2026-06-05 | One decision tree + shared loading step — awaiting implementation |
| al-dev-commit-executor | Description: internal heading still reads `al-dev-commit-agent (Execute Phase)` after rename | accepted | 2026-06-05 | One-line heading fix at agent file line 14 (rename was `319e4c7`) — awaiting implementation |
| al-dev-commit-executor | Description: internal heading still read `al-dev-commit-agent` after rename | fixed | 2026-06-05 | `bf9d289` — heading corrected; projections regenerated |
| al-dev-commit-lint-fixer | Clarity: `.dev/commit-baselines` fallback implemented as conditional `BASELINE_FILE` | fixed | 2026-06-05 | `c8f2f8b` |
| al-dev-commit | Bloat: subsection consolidation (re-scoped — top level already ~5 phase groups; merged 0.3+0.4, 0.5+0.6, folded 4.2; fixed stale Step 9.5a/b agent refs) | fixed | 2026-06-05 | `4f51722`, `ed05940` — externally-referenced numbering preserved |
| al-dev-plan-preflight | Bloat: resume modes folded into decision tree + shared load step; doubled 1.5/1.6 intros and substantive-answer criteria deduped (re-scoped) | fixed | 2026-06-05 | `58527e7` — Mode A/B/C labels and phase numbering preserved |
| al-dev-plan-swarm-validate | Name-fit: renamed to `al-dev-plan-critic-review` | fixed | 2026-06-05 | `d7c3e72` — no live callers; maps regenerated |
