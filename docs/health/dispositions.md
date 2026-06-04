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
| al-dev-ticket | Clarity: "first token decides" precedence under-specified (re-flag) | fixed | 2026-06-05 | `966d81b` — explicit `^(FD-?)?[0-9]+$` regex + IF/THEN already live; 2026-06-05 plugin sweep re-flagged fixed text. Verified against live file. |
| al-dev-commit | Bloat: repetitive dispatch blocks across phases (re-flag) | fixed | 2026-06-05 | `e0ea5eb` — dispatch frame extracted; live file cites `knowledge/commit-dispatch-template.md` once per phase. Verified against live file. |
| al-dev-plan-swarm-validate | Description: 6-critic dispatch not shown in body (re-flag) | fixed | 2026-06-05 | `76b0c5b` — live body enumerates all 6 parallel Agent dispatches + Dispatch Pattern section. Verified against live file. |
| al-dev-develop | Clarity: undefined `<src-file>` placeholder and unexplained `-nt` operator | accepted | 2026-06-05 | 2026-06-05 plugin sweep; replace placeholder with concrete loop, explain `-nt` — awaiting implementation |
| al-dev-fix | Clarity: ambiguous `IF complexity == 'medium' or 'complex'` branch | accepted | 2026-06-05 | Split into explicit MEDIUM / COMPLEX branches — awaiting implementation |
| al-dev-interview | Clarity: INTERVIEW COMPLETE gate has no else clause (open since 2026-06-04) | accepted | 2026-06-05 | Add recovery path: proceed with partial findings, documenting skipped categories — awaiting implementation |
| al-dev-lint | Clarity: no fallback when neither `al-compile` nor `al compile` available | accepted | 2026-06-05 | Add stop-and-report fallback — awaiting implementation |
| al-dev-plan-preflight | Clarity: "substantive answer" undefined (open since 2026-06-04) | accepted | 2026-06-05 | Add substantive criteria (business goal + BC object + concrete user action) — awaiting implementation |
| al-dev-developer-tdd, al-dev-developer-traditional | Bloat: AL coding standards duplicated near-verbatim | accepted | 2026-06-05 | Extract shared standards to `knowledge/al-developer-patterns.md`, reference from both — awaiting implementation |
| al-dev-developer-tdd, al-dev-developer-traditional | Shared-backbone: identical dispatch pattern across /al-dev-develop and /al-dev-fix (open since 2026-06-04) | accepted | 2026-06-05 | Canonicalize the developer dispatch template in `knowledge/` (new `developer-test-plan-dispatch-pattern.md` or expand `developer-invocation-patterns.md`) — awaiting implementation |
| al-dev-solution-architect | Bloat: 130-line workflow, repeated MCP guidance | accepted | 2026-06-05 | Move MCP guidance + pattern-evidence hierarchy to a knowledge reference; reduce sections (reverses 2026-06-04 "no issues") — awaiting implementation |
| al-dev-interview | Bloat: 90-line interview-process section with nested categories | accepted | 2026-06-05 | Extract question categories to `knowledge/interview-question-bank.md` — awaiting implementation |
| al-dev-commit-hook-fixer | Bloat: 74-line procedure with nested Steps 1–5 | accepted | 2026-06-05 | Move Failure Classification table + Approved Fixes to `knowledge/commit-hook-recovery-patterns.md` — awaiting implementation |
| al-dev-commit-lint-fixer, al-dev-release-notes-writer, al-dev-commit-agent-analysis, al-dev-script-engineer, al-dev-support-researcher, al-dev-diagnostics-fixer | Bloat: oversized/overlapping sections | accepted | 2026-06-05 | Consolidate sections / extract templates to knowledge per findings file; release-notes-writer also has an unclosed code fence to fix — awaiting implementation |
| al-dev-solution-architect | Clarity: "best existing analogue" needs yes/no examples; TESTABILITY_COMPLETE criteria undefined | accepted | 2026-06-05 | Rubric partially objectified by `6de8bfd`; residual = concrete verdict examples + explicit testability completion gate — awaiting implementation |
| al-dev-commit-lint-fixer, al-dev-developer-tdd, al-dev-developer-traditional, al-dev-explore, al-dev-support-reply-drafter, al-dev-commit-recover-fixer | Clarity: vague qualifiers / undefined terms | accepted | 2026-06-05 | Per findings file: sed-warning placement, "latest" glob tie-break, "largest file count", link-marker format, fallback-strategy definitions — awaiting implementation |
| al-dev-code-review | Name-fit: too generic vs specialist reviewers | accepted | 2026-06-05 | Rename to `al-dev-general-code-reviewer` (or `-code-quality-reviewer`); update caller refs — awaiting implementation |
| al-dev-ticket-agent | Name-fit: "agent" classifier not verb; scope is Freshdesk fetch + context write | accepted | 2026-06-05 | Rename to `al-dev-ticket-context-writer`; update `/al-dev-ticket` refs — awaiting implementation |
| al-dev-commit-agent-analysis, al-dev-commit-agent-execute | Name-fit (Low): awkward "agent-analysis/execute" suffixes | accepted | 2026-06-05 | Rename to `al-dev-commit-analyzer` / `al-dev-commit-executor`; update `/al-dev-commit` refs — awaiting implementation |
| al-dev-explore, al-dev-commit-agent-analysis, al-dev-release-notes-writer | Structure (Low): code-fence / step-numbering issues | accepted | 2026-06-05 | Close/format fences; standardize step headings — awaiting implementation |
| al-dev-consolidate, al-dev-document, al-dev-help, al-dev-perf, al-dev-plan, al-dev-release-notes, al-dev-review-develop, al-dev-ticket, commit-recover | Clarity: vague qualifiers / undefined terms (several open since 2026-06-04) | accepted | 2026-06-05 | Per findings file: glob definition, `[AUDIENCE]` substitution, trigger examples, loop-body scope, "meaningfully different" criteria, version auto-fill, severity-field spec, URL-encode example, "verified" definition — awaiting implementation |
| al-dev-consolidate, al-dev-develop, al-dev-explore, al-dev-plan-final-review, al-dev-support-reply | Description drift (open since 2026-06-04) | accepted | 2026-06-05 | Per findings file: context-window note, Phase 4 handoff content, "delegates" wording, validator-fail path, REPLY-block vs `.dev/ticket-reply.md` — awaiting implementation |
| al-dev-support-reply | Structure: argument-hint contradicts two usage modes | accepted | 2026-06-05 | Update argument-hint to cover filepath + auto-detect — awaiting implementation |
| al-dev-lint, al-dev-perf, al-dev-plan-swarm-validate, al-dev-review-develop-preflight, al-dev-ticket, commit-recover, verify-commits | Structure (Low): missing `bash` language tags (open since 2026-06-04) | accepted | 2026-06-05 | Add language tags to code fences — awaiting implementation |
| al-dev-commit-agent-analysis | Caller-alignment: REPO documented required but dispatch template never passes it | accepted | 2026-06-05 | Document REPO as inferred from working dir (or add to dispatch preamble) — awaiting implementation |
| al-dev-developer-tdd, al-dev-developer-traditional | Caller-alignment (Low): inputs under-specify inline context fields (open since 2026-06-04) | accepted | 2026-06-05 | Add "Context Fields" row referencing `knowledge/al-dev-develop-spawn-prompt.md` — awaiting implementation |
| al-dev-consolidate | Surface-placement: no agents; references internal repo paths (`.dev/sessions/`, `profile-al-dev-shared/`) | accepted | 2026-06-05 | Move to `.claude/skills/` — awaiting implementation |
| al-dev-commit (chain) | Handoff-gap: no post-commit orchestration consumer for `commits.json`/`hook-failures.json` (open since 2026-06-04) | accepted | 2026-06-05 | Consider `al-dev-deploy`/release-readiness skill consuming commit outputs — awaiting implementation |
| al-dev-fix, al-dev-consolidate | Handoff-gap (Low): `.dev/test-plan.md` / `sessions-index.md` unconsumed | accepted | 2026-06-05 | Optional downstream consumers — awaiting implementation |
| al-dev-support-reply-drafter | Scope-isolation: Split internal-findings vs customer-reply into separate agents | declined | 2026-06-05 | Creates a new agent for a marginal separation; heavier than a cleanup and not selected in the 2026-06-05 accept pass. Revisit only by editing this row. |
