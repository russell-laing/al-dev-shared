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
- A `fixed` row that supersedes a committed `accepted` row should include
  `closes row N` in its note (N = the superseded row's data-row number,
  counting table rows from 1). Without the token, supersession is inferred
  by object order — ambiguous when one object has several open rows.
- `python3 scripts/check_ledger_staleness.py` reports the effective-open
  accepted rows and flags any whose object changed in git after the row
  date (likely implemented but never flipped). The pre-commit gate runs it
  in `--staged` mode.

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
| sync-documentation-maps family | Description: workflow-count frame inconsistent — sync/-collect say "Three-skill", -apply/-write say "Four-skill" + "two-step finalization" | fixed | 2026-06-05 | `6dc9efb` — four-skill frame adopted in sync/collect; family descriptions now aligned |
| plugin-health-discover | Description: documented `workflow_utils.py` dispatch path returns mock findings; §3.2 invocation cannot work as written | fixed | 2026-06-05 | `a9ef0b3` — workflow_utils stub subsystem removed (−279 lines); in-session lens dispatch documented as canonical |
| sync-documentation-maps-* agents (×4) | Structure: `model:` pinned to `claude-haiku-4-5-20251001` vs the `haiku` alias used by every other agent | fixed | 2026-06-05 | `4e31dda` — model normalized to `haiku` alias (stays haiku; distinct from the declined sonnet upgrade, row 39) |
| plugin-health-discover | Bloat: 9 top-level sections; Phase 3 nested 3.1/3.1b/3.2/3.3 | accepted | 2026-06-05 | Fold cadence guard into Phase 0; merge resume+dispatch (count-based — re-verify before executing) — awaiting implementation |
| al-dev-consolidate | Bloat: Phase 2 ~73 lines duplicate patterns now canonical in `consolidate-extraction-patterns.md` | fixed | 2026-06-05 | Not reproduced against live file — Phase 2 already cross-references the patterns by name (`6cf7e81` only repathed the existing ref); remaining inline bash is group-specific by design. Verified 2026-06-05. |
| al-dev-develop | Bloat: 9 top-level phases; Phase 4 Output section redundant with Phase 4 completion | fixed | 2026-06-05 | `32a5ff3` — Phase 4 Output demoted into Phase 4 subsection; external Phase 4 label and handoff filename preserved |
| al-dev-fix | Bloat: Decision Tree section duplicates Implementation Steps routing | fixed | 2026-06-05 | `b1e5916` — Decision Tree folded into Implementation Steps |
| al-dev-plan | Bloat: Phases 2–4 restate the architect contract + evidence rules | fixed | 2026-06-05 | `d36e113` — architect contract absorbed via `architect-invocation-patterns.md` Pattern 1 reference; dangling H2 folded into Phase 2 |
| al-dev-ticket | Bloat: Steps 1/1.5 both resolve ticket input; Phase 5 repeats Phase 0.5 mode branching | fixed | 2026-06-05 | `476a068` — Phase 0.5 made the single parse point, Phase 5 the single branch point; stale Phase 5 refs fixed |
| sync-documentation-maps | Bloat: Phase 3 ~42 lines, nested 3.1/3.1b/3.2/3.3 | fixed | 2026-06-05 | `47cdf12` — Phase 3 dispatch bullets collapsed into one template |
| sync-documentation-maps-collect | Bloat: Phase 4 defers all dispatch logic to `collect-dispatch-patterns.md` (forward reference) | fixed | 2026-06-05 | `81a7f4c` — minimal dispatch summary inlined in Phase 4 |
| maintainer surface | No tooling lifecycle diagram (closes the accepted row dated 2026-06-05 above) | fixed | 2026-06-05 | `46d3a5a` — CLAUDE.md points to `docs/maintainer-tooling.md`; `7fcd53c` — Visual Workflow lifecycle diagram landed in that doc |
| review-docs | Bloat: Phase 2 ~94 lines (2a Technical Accuracy + 2b Readability) | accepted | 2026-06-06 | Elevate 2a/2b to top-level phases; template the script/skill/path verification blocks — awaiting implementation |
| review-documentation-map | Bloat: Phase 4 ~70 lines across 4a/4b/4c | accepted | 2026-06-06 | Elevate the sub-phases; converges with the audit/apply split — awaiting implementation |
| sync-documentation-maps-agent-audit | Bloat: Instructions (Steps 1–6) >30 lines | declined | 2026-06-06 | rubber-duck 2026-06-06: Instructions are surface-specific; no viable shared extraction beyond existing `sync-agent-patterns.md` |
| sync-documentation-maps-agent-update | Bloat: Instructions ~43 lines | accepted | 2026-06-06 | Extract the shared procedure to one knowledge doc (count-based — re-verify) — awaiting implementation |
| sync-documentation-maps-skill-audit | Bloat: Instructions ~52 lines | declined | 2026-06-06 | rubber-duck 2026-06-06: Instructions are surface-specific; no viable shared extraction beyond existing `sync-agent-patterns.md` |
| sync-documentation-maps-skill-update | Bloat: Instructions ~43 lines | accepted | 2026-06-06 | Extract the shared procedure to one knowledge doc (count-based — re-verify) — awaiting implementation |
| sync-documentation-maps-apply | Bloat: Phase 3 repeats file-validation 3× | declined | 2026-06-06 | rubber-duck 2026-06-06: claim does not hold against live file — Phase 3 has one shared artifact check block, one agent-only count check, and one rules table |
| sync-documentation-maps-collect | Bloat: Phase 4 parallels /sync Phase 4 | declined | 2026-06-06 | rubber-duck 2026-06-06: already addressed / marginal — shared dispatch logic already lives in `collect-dispatch-patterns.md` |
| sync-documentation-maps | Bloat: checkpoint JSON field tables enumerated twice | declined | 2026-06-06 | rubber-duck 2026-06-06: claim does not hold against live file — only one checkpoint field table remains in `/sync` |
| sync-documentation-maps-write | Bloat: four near-identical regeneration blocks | accepted | 2026-06-06 | Template/consolidate the regeneration blocks — awaiting implementation |
| plan-health-findings | Bloat: 7 top-level sections; Phase 2b ~35 lines | accepted | 2026-06-06 | Extract Phase 2b — awaiting implementation |
| design-agent-lens-caller-alignment | Clarity: "dispatch line and context block" co-occurrence ambiguous | accepted | 2026-06-06 | Clarify the AND/OR logic — awaiting implementation |
| naming-convention-lens | Clarity: pipe set-notation for the plugin/tooling argument | accepted | 2026-06-06 | Rewrite the set-notation as a prose list — awaiting implementation |
| quality-agent-lens-clarity | Clarity: own placeholder meta-notation risks self-flagging | declined | 2026-06-06 | rubber-duck 2026-06-06: already addressed / marginal — the rule already exempts meta-notation in these instructions |
| quality-skill-lens-clarity | Clarity: own placeholder meta-notation risks self-flagging | declined | 2026-06-06 | rubber-duck 2026-06-06: already addressed / marginal — the rule already exempts meta-notation in these instructions |
| sync-documentation-maps-agent-audit | Clarity: (none) literal normalization, type-mismatch risk | declined | 2026-06-06 | rubber-duck 2026-06-06: claim does not hold against live file — `(none)` and `(none found)` are already handled as distinct empty cases |
| sync-documentation-maps-skill-audit | Clarity: sed pipe-before-filename command order | accepted | 2026-06-06 | Fix the sed/grep command order — awaiting implementation |
| al-dev-consolidate | Clarity: inconsistent dir-name backticks + undefined "same session date" matching | declined | 2026-06-06 | rubber-duck 2026-06-06: already satisfied / canonical against live file — session-date rule is explicit and cited dir names are already backticked |
| audit-knowledge-quality | Clarity: "Explore subagent" not a named agent type here | declined | 2026-06-06 | rubber-duck 2026-06-06: already satisfied / canonical against live file — `Explore subagent` is canonical terminology per `harness-concepts.md` |
| plugin-health-discover | Clarity: single_use_agents zero-use inclusion + "right of an edge" Mermaid ambiguity | declined | 2026-06-06 | rubber-duck 2026-06-06: claim does not hold against live file — `single_use_agents` is defined as `agent_usage_counts == 1` and the Mermaid wording is absent |
| plugin-health-report | Clarity: "repeats" vs "match on substance" terminology | declined | 2026-06-06 | rubber-duck 2026-06-06: already satisfied / canonical against live file — `repeat` is the recurrence state and `match on substance` is the comparison method |
| record-health-dispositions | Clarity: ← implemented / ← completed markers undefined | accepted | 2026-06-06 | Define the marker syntax — awaiting implementation |
| review-documentation-map | Clarity: node-ID grep doesn't state quoted IDs unsupported | accepted | 2026-06-06 | Note that quoted IDs are unsupported — awaiting implementation |
| sync-documentation-maps-apply | Clarity: "Exit 1 or other: runtime error" undefined | fixed | 2026-06-06 | verified against live file 2026-06-06 — already satisfied; not reproduced |
| sync-documentation-maps | Clarity: "Abandoned runs" cites history without a defined rule | accepted | 2026-06-06 | Define the abandoned-run rule — awaiting implementation |
| audit-knowledge-quality | Description: "targeted fixes" scope unclear | accepted | 2026-06-06 | Clarify the targeted-fix scope — awaiting implementation |
| fix-knowledge-quality | Description: "converts findings into a task list" — task block originates in audit | accepted | 2026-06-06 | Correct the description — awaiting implementation |
| plan-health-findings | Description: omits --skills/--agents routing | accepted | 2026-06-06 | Add the routing flags to the description — awaiting implementation |
| plugin-health-discover | Description: does not say it writes RAW findings, not the dossier | accepted | 2026-06-06 | Clarify that it writes findings, not the dossier — awaiting implementation |
| review-docs | Description: "archived path references" check absent from description | accepted | 2026-06-06 | Add the archived-path check to the description — awaiting implementation |
| sync-documentation-maps-collect | Description: omits Resume/Restart + --wait | accepted | 2026-06-06 | Add Resume/Restart + --wait to the description — awaiting implementation |
| sync-documentation-maps | Description: omits Phase 0 cadence guard + --force | accepted | 2026-06-06 | Add the cadence guard + --force to the description — awaiting implementation |
| analyze-architectural-design | Bloat (Low): inline synthesis protocol overlaps /plan-health-findings rubber-duck | declined | 2026-06-06 | rubber-duck 2026-06-06: claim does not hold against live file — the remaining synthesis guidance is conceptual-only and writes a different output |
| design-agent-lens-caller-alignment | Clarity (Low): "potential High" — drop "potential" | accepted | 2026-06-06 | Drop the hedge word — awaiting implementation |
| design-skill-lens-preplanning | Clarity (Low): substring-match else clause | accepted | 2026-06-06 | Define the else clause — awaiting implementation |
| sync-documentation-maps-agent-audit | Clarity (Low): "not a failure" double negative + relative ls path | accepted | 2026-06-06 | Fix the double negative; use an absolute path — awaiting implementation |
| al-dev-diagram-generator | Clarity (Low): "partial edge" undefined | accepted | 2026-06-06 | Define "partial edge" — awaiting implementation |
| design-agent-lens-caller-alignment | Description (Low): omits skills-dir grep | declined | 2026-06-06 | rubber-duck 2026-06-06: already addressed / marginal — adding the grep detail to the description would leak mechanism, unlike sibling lens descriptions |
| sync-documentation-maps-agent-update, -skill-update | Description (Low): says writes docs/al-dev-*-map.md; body writes to updates staging dir | accepted | 2026-06-06 | Correct the description to name the staging dir — awaiting implementation |
| sync-documentation-maps-write | Description (Low): omits "maintainer guide" from regenerated list | accepted | 2026-06-06 | Add the maintainer guide to the description — awaiting implementation |
| sync-documentation-maps-apply | Description (Low): "applies" omits Phase 3 validation | fixed | 2026-06-06 | verified against live file 2026-06-06 — already satisfied; not reproduced |
| sync-documentation-maps | Name-fit (Low): name implies single sync; it dispatches audit agents + writes checkpoint | fixed | 2026-06-06 | verified against live file 2026-06-06 — already satisfied; not reproduced |
| review-maps | Name-fit (Low): name suggests inspection; it is a mode-selection router | declined | 2026-06-06 | rubber-duck 2026-06-06: already satisfied / canonical against live file — the description already states the router role and names both delegated paths |
| design-skill-lens-surface-placement, sync-documentation-maps-agent-audit/-agent-update/-skill-audit | Structure (Low): missing MD040 code-block language tags (agent files) | declined | 2026-06-06 | rubber-duck 2026-06-06: claim does not hold against live file — surface-placement has no fences and the sync-agent fences are already tagged or absent |
| ~19 skill files | Structure (Low): pervasive MD040 missing code-block language tags | declined | 2026-06-06 | rubber-duck 2026-06-06: claim does not hold against live file — active skills are MD040 clean; remaining hits are archived-only |
| al-dev-diagram-generator | Structure (Low): Phase/Sub-step numbering inconsistency | accepted | 2026-06-06 | Normalize the numbering — awaiting implementation |
| align-harness-repos | Structure (Low): uses "Step N" instead of "Phase N" | accepted | 2026-06-06 | Normalize to "Phase N" — awaiting implementation |
| sync-documentation-maps-agent-update | Bloat: Instructions ~43 lines | fixed | 2026-06-06 | `e8efc32` — extracted shared update procedure to `.claude/knowledge/sync-map-update-shared.md`; closes row 107 |
| sync-documentation-maps-skill-update | Bloat: Instructions ~43 lines | fixed | 2026-06-06 | `e8efc32` — extracted shared update procedure to `.claude/knowledge/sync-map-update-shared.md`; closes row 109 |
| sync-documentation-maps-collect | Description: omits Resume/Restart + --wait | fixed | 2026-06-07 | `052cbb0` — description now documents Resume/Restart and `--wait` artifact polling; closes row 104 |
| sync-documentation-maps | Description: omits Phase 0 cadence guard + --force | fixed | 2026-06-07 | `0de2bf8` — description and Arguments now document the Phase 0 cadence guard and `--force`; closes row 105 |
| sync-documentation-maps-write | Description (Low): omits "maintainer guide" from regenerated list | fixed | 2026-06-07 | `3047459` — description now names the maintainer guide and corrects regenerated-artifact provenance; closes row 113 |
| plugin-health-discover | Description: does not say it writes RAW findings, not the dossier | fixed | 2026-06-07 | `c08c54f` — description now distinguishes RAW findings from the ranked dossier; closes row 102 |
| plan-health-findings | Description: omits --skills/--agents routing | fixed | 2026-06-07 | `2396672` — description now documents `--skills` and `--agents` object-type routing; closes row 101 |
| review-docs | Description: "archived path references" check absent from description | fixed | 2026-06-07 | `b4c706c` — description now includes archived path references in the checklist; closes row 103 |
| audit-knowledge-quality | Description: "targeted fixes" scope unclear | fixed | 2026-06-07 | `d3faeac` — description and body now scope post-report help to user-gated HIGH-severity fix guidance; closes row 99 |
| fix-knowledge-quality | Description: "converts findings into a task list" — task block originates in audit | fixed | 2026-06-07 | `b8170a7` — description now says the skill reads the fix-task block produced by `/audit-knowledge-quality`; closes row 100 |
| sync-documentation-maps-agent-update, -skill-update | Description (Low): says writes docs/al-dev-*-map.md; body writes to updates staging dir | fixed | 2026-06-07 | `d999e38` — both descriptions now lead with the `<result_dir>/updates/` staging targets; closes row 112 |
| sync-documentation-maps | Clarity: "Abandoned runs" cites history without a defined rule | fixed | 2026-06-07 | `bda1383` — removed the unsourced historical statistic while keeping the cadence-guard rule unchanged; closes row 128 |
| sync-documentation-maps-skill-audit | Clarity: sed pipe-before-filename command order | fixed | 2026-06-07 | `a77819c` — the runnable snippet now defines `skill_file` explicitly and uses `"$skill_file"`; closes row 90 |
| sync-documentation-maps-agent-audit | Clarity (Low): "not a failure" double negative + relative ls path | fixed | 2026-06-07 | `84f8662` — rewrote the empty-list note with positive phrasing and kept the file's relative-path convention; closes row 109 |
| record-health-dispositions | Clarity: ← implemented / ← completed markers undefined | fixed | 2026-06-07 | `b2fc35d` — the parser now defines the marker set as legacy inline dossier annotations and includes `← already implemented`; closes row 95 |
| review-documentation-map | Clarity: node-ID grep doesn't state quoted IDs unsupported | fixed | 2026-06-07 | `73d0684` — non-canonical Mermaid node IDs are now flagged as style violations rather than documented as manual-check cases; closes row 96 |
| design-agent-lens-caller-alignment | Clarity: "dispatch line and context block" co-occurrence ambiguous | fixed | 2026-06-07 | `abe7cf6` — the lens now checks dispatch and context as independent signals and uses the qualified `al-dev-shared:<agent-name>` search token; closes row 85 |
| design-agent-lens-caller-alignment | Clarity (Low): "potential High" — drop "potential" | fixed | 2026-06-07 | `abe7cf6` — missing context is now stated definitively as High in the severity rules; closes row 107 |
| naming-convention-lens | Clarity: pipe set-notation for the plugin/tooling argument | fixed | 2026-06-07 | `6457818` — the lens and convention doc now use explicit set/prose notation instead of pipe shorthand; closes row 86 |
| design-skill-lens-preplanning | Clarity (Low): substring-match else clause | fixed | 2026-06-07 | `f97702b` — fixed the Inputs map path and enumerated exact, substring-only, main-spine-only, and absent occurrence states; closes row 108 |
| align-harness-repos | Structure (Low): uses "Step N" instead of "Phase N" | fixed | 2026-06-07 | `93f1370` — all workflow headers now use `Phase N` consistently; closes row 120 |
| al-dev-diagram-generator | Clarity (Low): "partial edge" undefined | fixed | 2026-06-07 | `8a4610e` — archived the orphaned maintainer skill instead of polishing a dead surface; closes row 140 |
| al-dev-diagram-generator | Structure (Low): Phase/Sub-step numbering inconsistency | fixed | 2026-06-07 | `8a4610e` — archived the orphaned maintainer skill instead of normalizing headings on a dead surface; closes row 149 |
| plugin-health-report | Complexity → Atomise: 8 phases, two independently-runnable concerns (0–1d processing vs 2–4 generation+presentation) | accepted | 2026-06-07 | Split into a process step + finalize step, or extract Phase 3 graph-refresh as a post-write utility — awaiting implementation |
| design-skill-lens-near-duplicates | Model fit: multi-file comparative synthesis on haiku | declined | 2026-06-07 | Prior sweeps judged this lens clean for model-fit; severity churn — revisit only if artifact quality regresses |
| design-skill-lens-preplanning | Model fit: multi-file cross-reference on haiku | declined | 2026-06-07 | Prior sweeps judged this lens clean for model-fit; severity churn — revisit only if artifact quality regresses |
| design-skill-lens-shared-backbone | Model fit: multi-file pattern synthesis on haiku | declined | 2026-06-07 | Prior sweeps judged this lens clean for model-fit; severity churn — revisit only if artifact quality regresses |
| sync-documentation-maps-agent-audit | Model fit: bash + Python + multi-file JSON aggregation on haiku | accepted | 2026-06-07 | Consider haiku → sonnet; not covered by declined row 47 (which named only the update pair) — awaiting implementation |
| sync-documentation-maps-skill-audit | Model fit: same task profile as agent-audit, on haiku | accepted | 2026-06-07 | Consider haiku → sonnet; parallel to agent-audit finding — awaiting implementation |
| docs/al-dev-plugin-synthesis.md | Handoff gap: produced by analyze-architectural-design; no downstream consumer | grandfathered | 2026-06-07 | Deliberate terminal artifact; human-read by design. Revisit only by editing this row. |
| docs/superpowers/plans/<date>-<topic>.md | Handoff gap: plan→implement chain incomplete | declined | 2026-06-07 | Overlaps declined rows 79–80; post-plan orchestration deferred to a dedicated design pass |
| sync-documentation-maps audit/update agents | Shared backbone: background-dispatch pattern not canonicalized in one doc | declined | 2026-06-07 | collect-dispatch-patterns.md already covers the shared dispatch pattern |
| naming-convention-lens | Tool hygiene: Glob declared in frontmatter, unused in body | accepted | 2026-06-07 | Trim Glob from tools list (open since 2026-06-04) — awaiting implementation |
| profile-al-dev-shared/generated/agents/ | Handoff gap: no downstream projection-vs-source validation skill | declined | 2026-06-07 | Net-new skill for a rare failure mode; not worth the weight now |
| docs/al-dev-workflow-diagrams.md | Handoff gap: produced by diagram-generator/sync-write; no downstream consumer | grandfathered | 2026-06-07 | Diagram docs are human-read terminals by convention. Revisit only by editing this row. |
| plan-health-findings | Bloat: 7 top-level sections; Phase 2b ~35 lines | fixed | 2026-06-07 | `c9a34b3` — folded Phase 2b into Phase 2; phase headings 5 → 4; record format kept inline; closes row 84 |
| sync-documentation-maps-write | Bloat: four near-identical regeneration blocks | fixed | 2026-06-07 | `c1d55ca` — regen blocks 2-4 table-driven with one runnable bash block; closes row 83 |
| naming-convention-lens | Tool hygiene: Glob declared in frontmatter, unused in body | fixed | 2026-06-07 | `11f4653` — trimmed Glob from tools list; closes row 153 |
| sync-documentation-maps-agent-audit | Model fit: bash + Python + multi-file JSON aggregation on haiku | fixed | 2026-06-07 | `3cf8d5f` — model haiku → sonnet; closes row 148 |
| sync-documentation-maps-skill-audit | Model fit: same task profile as agent-audit, on haiku | fixed | 2026-06-07 | `b3ac86f` — model haiku → sonnet; closes row 149 |
| review-documentation-map | Bloat: Phase 4 ~70 lines across 4a/4b/4c | fixed | 2026-06-07 | `95b173a` — elevated 4a/4b/4c to Phase 4/5/6, stale refs retargeted to Phase 7; no split; closes row 75 |
| plugin-health-report | Complexity → Atomise: 8 phases, two independently-runnable concerns | fixed | 2026-06-07 | `2d9d82f` — removed duplicate Phase 3 graph refresh (post-write-utility branch), reconciled caller contracts; closes row 144 |
| review-docs | Bloat: Phase 2 ~94 lines (2a Technical Accuracy + 2b Readability) | fixed | 2026-06-07 | `87850bb` — PARTIAL: elevated 2a/2b to Phase 3/4 with Phase 2 as loop owner; templating the repeated verification blocks remains open (see new accepted row); closes row 74 |
| review-docs | Bloat: repeated script/skill/path verification blocks in Technical Accuracy not templated | accepted | 2026-06-07 | Remaining half of the elevated review-docs finding — template the repeated grep→test verification idiom — awaiting implementation |
| align-harness-repos | Bloat: Phase 5 token-replacement block >30 lines inline | accepted | 2026-06-07 | Extract token-mapping to reference doc; reduce Phase 5 to ~5-line shell-out — awaiting implementation |
| review-documentation-map | Bloat: Phase 2 (~76 lines) profile extraction + caller sets inline | accepted | 2026-06-07 | Extract to knowledge/documentation-map-profile-schema.md + documentation-map-comparison-rules.md — awaiting implementation |
| record-health-dispositions | Clarity: no rule for contradictory batch input | accepted | 2026-06-07 | Add: if any decision in a batch contradicts an earlier one, ask for clarification before recording — awaiting implementation |
| plugin-health-discover | Clarity: Phase 1 cadence guard missing else branch (happy path implicit) | accepted | 2026-06-07 | Add explicit "If dispositioned rows exist dated on/after the dossier date, proceed" branch — awaiting implementation |
| plan-health-findings | Clarity: --skills/--agents and FILTER_TYPE interaction order not stated | accepted | 2026-06-07 | Verified live 2026-06-07 — still present; add explicit ordering rule with example — awaiting implementation |
| design-agent-lens-caller-alignment | Clarity: "passed context with no dispatch line" severity label missing | accepted | 2026-06-07 | Re-verified post-abe7cf6 — still unspecified; add severity label (e.g. Medium) — awaiting implementation |
| design-skill-lens-near-duplicates | Clarity: "within 2 of each other" phase count comparison ambiguous | accepted | 2026-06-07 | Define operationally: "phase counts differ by at most 2" — awaiting implementation |
| audit-knowledge-quality | Bloat: Phase 2a and 2b near-identical decision trees differing only by file-count threshold | accepted | 2026-06-07 | Unify into one decision section with threshold condition — awaiting implementation |
| align-harness-repos | Clarity: Phase 5 fenced-code-block trigger condition for manual-review flag is vague | accepted | 2026-06-07 | Rewrite: "If token appears inside a fenced code block, flag for manual review only" — awaiting implementation |
| audit-knowledge-quality | Clarity: Phase 2a step 2 no else branch for orphaned knowledge file | accepted | 2026-06-07 | Add: "If no referencing agent or skill found, note as orphaned, severity LOW" — awaiting implementation |
| plan-health-findings | Clarity: "rubber-duck it by reading the live subject file in full first" — "in full" imprecise | accepted | 2026-06-07 | Verified live 2026-06-07 — still present; rewrite: "Read entire subject file from start to finish" — awaiting implementation |
| plugin-health-discover | Clarity: Phase 3.1b "false" Move findings undefined operationally | accepted | 2026-06-07 | Replace: "Any 'Move' suggestion against a tooling-surface file is a non-actionable false positive" — awaiting implementation |
| review-documentation-map | Clarity: Phase 6 no else branch for "not accurate AND NO_UPDATE=false" | accepted | 2026-06-07 | Verified live 2026-06-07 — still present; add "Otherwise, proceed to Phase 7" — awaiting implementation |
| sync-documentation-maps-collect | Clarity: Phase 2 no guard against infinite retry | accepted | 2026-06-07 | Add: "If same surface still pending on re-run, check for agent failures and stop" — awaiting implementation |
| sync-documentation-maps-collect | Clarity: Phase 3 sort order and dedup winner unspecified | accepted | 2026-06-07 | Clarify: sort alphabetically; keep first (object, type) duplicate occurrence — awaiting implementation |
| sync-documentation-maps-write | Clarity: "If the three values differ, stop" has no recovery action | accepted | 2026-06-07 | Add recovery: re-run /sync-documentation-maps or manually verify — awaiting implementation |
| plugin-health-audit | Description: implies single-unit dispatch; body delegates to two sub-skills | accepted | 2026-06-07 | Revise to name the two-phase internal workflow (discover → report) — awaiting implementation |
| sync-documentation-maps-apply | Name Fit: "apply" implies writing; validation gate invisible to callers | accepted | 2026-06-07 | Consider rename or add validation note to trigger phrases — awaiting implementation |
| sync-documentation-maps-apply | Structure: argument-hint references RUN_ID; body describes --team-ids parameter | accepted | 2026-06-07 | Update argument-hint to match parameters actually in body — awaiting implementation |
| sync-documentation-maps | Bloat: "Abandoned runs spawn audit agents whose results are never read" explanatory sentence in Phase 0 | accepted | 2026-06-07 | Verified live 2026-06-07 — still present; remove explanatory sentence, keep operative rule only — awaiting implementation |
| record-health-dispositions | Bloat: Closure write-back rule dated procedural tone | accepted | 2026-06-07 | Condense to 3-item checklist; move narrative to knowledge/ledger-closure-protocol.md — awaiting implementation |
| align-harness-repos | Clarity: Phase 5 <placeholder> meta-notation undefined | accepted | 2026-06-07 | Add note: "<placeholder> indicates a substitution point — replace with actual token" — awaiting implementation |
| plugin-health-audit | Naming: structure inverted (object-verb-aspect vs verb-object-aspect) | grandfathered | 2026-06-07 | plugin-health-* prefix family is intentional workflow-phase naming; consistent with the 2026-06-05 grandfathered cluster |
| record-health-dispositions | Naming: "record" verb and "health-dispositions" object outside documented sets | grandfathered | 2026-06-07 | Name is intentional and established; do not rename |
| review-documentation-map | Naming: compound "documentation-map" object outside simple singular pattern | grandfathered | 2026-06-07 | Name is intentional; renaming to review-map would conflict with the review-maps router |
| review-maps | Naming: plural "maps" object | grandfathered | 2026-06-07 | Name is intentional for the multi-surface router role; do not rename |
| design-agent-lens-caller-alignment | Structure: code blocks lack language tags | accepted | 2026-06-07 | Add bash/regex/text tags as appropriate — awaiting implementation |
| quality-agent-lens-clarity | Structure: pseudo-code block lacks language tag | accepted | 2026-06-07 | Add text tag — awaiting implementation |
| quality-skill-lens-clarity | Structure: pseudo-code block lacks language tag | accepted | 2026-06-07 | Add text tag — awaiting implementation |
| align-harness-repos | Structure: code blocks in Phase 2-4 lack language tags | accepted | 2026-06-07 | Add bash for command blocks, text for output-only blocks — awaiting implementation |
| analyze-architectural-design | Structure: code block lacks bash tag | accepted | 2026-06-07 | Add bash tag — awaiting implementation |
| audit-knowledge-quality | Structure: phase headers mix "Phase N" and "Step N" | accepted | 2026-06-07 | Standardize to "Phase N" throughout — awaiting implementation |
| fix-knowledge-quality | Structure: code blocks lack language tags | accepted | 2026-06-07 | Add bash and text tags — awaiting implementation |
| plugin-health-discover | Structure: code blocks lack bash tags | accepted | 2026-06-07 | Add bash tags — awaiting implementation |
| plugin-health-report | Structure: code blocks lack language tags; phase header punctuation inconsistent | accepted | 2026-06-07 | Add bash tags; standardize headers to "## Phase N —" — awaiting implementation |
| projection-sync | Structure: code blocks lack bash tags | accepted | 2026-06-07 | Add bash tags — awaiting implementation |
| record-health-dispositions | Structure: code blocks lack bash tags | accepted | 2026-06-07 | Add bash tags — awaiting implementation |
| review-documentation-map | Structure: nested "### Phase 2b" under "## Phase 2" breaks header hierarchy | accepted | 2026-06-07 | Restructure as flat "## Phase 2b" or fold into Phase 2 narrative — awaiting implementation |
| review-maps | Structure: code block lacks bash tag | accepted | 2026-06-07 | Add bash tag — awaiting implementation |
| sync-documentation-maps-apply | Structure: code blocks lack language tags | accepted | 2026-06-07 | Add bash tags — awaiting implementation |
| sync-documentation-maps-collect | Structure: code blocks lack language tags | accepted | 2026-06-07 | Add bash tags — awaiting implementation |
