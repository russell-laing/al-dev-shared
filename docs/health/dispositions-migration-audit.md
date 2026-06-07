# Health Dispositions Migration Audit

Source ledger: `docs/health/dispositions.md`

- Migrated rows: 247
- Rows requiring manual provenance cleanup: 242

## Unresolved Rows

| Row | Surface | Dimension | Object | Finding | Date | Reason |
|-----|---------|-----------|--------|---------|------|--------|
| 1 | unknown | unknown | al-dev-solution-architect | `TESTABILITY_COMPLETE: no` had no caller halt procedure | 2026-06-04 | no live provenance match |
| 2 | unknown | unknown | al-dev-investigate | Step 5 inline 98-line findings template (bloat) | 2026-06-04 | no live provenance match |
| 3 | unknown | unknown | al-dev-perf | Inline classification + 60-line report template (bloat) | 2026-06-04 | no live provenance match |
| 4 | unknown | unknown | al-dev-commit | Repeated dispatch patterns across phases (bloat, partial) | 2026-06-04 | no live provenance match |
| 5 | unknown | unknown | al-dev-ticket | Mixed-input precedence rule ambiguous | 2026-06-04 | no live provenance match |
| 6 | unknown | unknown | al-dev-plan-swarm-validate | Description promised critics/synthesis the body lacked | 2026-06-04 | no live provenance match |
| 7 | unknown | unknown | sync-documentation-maps-write | Phase 0 status guard inverted | 2026-06-04 | no live provenance match |
| 8 | unknown | unknown | al-dev-diagram-generator | Phase 3 lacked one-vs-two diagram routing | 2026-06-04 | no live provenance match |
| 9 | unknown | unknown | projection-sync | Phase 0 Resume/Restart had no non-response default | 2026-06-04 | no live provenance match |
| 10 | unknown | unknown | align-harness-repos | Step 5 permitted discretionary replacement path | 2026-06-04 | no live provenance match |
| 11 | unknown | unknown | verify-map-suggestions | Phase 3 verification commands unmapped to finding verbs | 2026-06-04 | no live provenance match |
| 12 | unknown | unknown | sync-documentation-maps-agent-audit | Step 3 grep union/dedup unsequenced (open since 2026-06-03) | 2026-06-05 | no live provenance match |
| 13 | unknown | unknown | docs/al-dev-agent-map.md | Header count stale (22 vs 23 on disk) | 2026-06-05 | no live provenance match |
| 14 | unknown | unknown | align-harness-repos | Name implies alignment; behavior is validation-only | 2026-06-05 | no live provenance match |
| 15 | unknown | unknown | al-dev-support-reply-drafter | Model fit: downgrade sonnet → haiku | 2026-06-05 | no live provenance match |
| 16 | unknown | unknown | analyze-architectural-design, plugin-health-discover, plugin-health-report | Naming: not verb-first `{verb}-{object}-{aspect}` | 2026-06-05 | no live provenance match |
| 17 | unknown | unknown | sync-documentation-maps-agent-update, sync-documentation-maps-skill-update | Model fit: upgrade haiku → sonnet for map synthesis | 2026-06-05 | no live provenance match |
| 18 | unknown | unknown | maintainer surface | No tooling lifecycle diagram (Layer 1 scoped to distributed skills) | 2026-06-05 | no live provenance match |
| 19 | unknown | unknown | align-harness-repos | No durable pass/fail validation artifact for downstream gating | 2026-06-05 | no live provenance match |
| 20 | unknown | unknown | verify-map-suggestions | Name says "verify" but the skill is a rubber-duck-to-plan pipeline (name-fit, 2026-06-05 sweep) | 2026-06-05 | no live provenance match |
| 21 | unknown | unknown | plan-health-findings | Skill name (lineage: plan-map-changes → al-dev-map-suggestions-verify → verify-map-suggestions → plan-health-findings) | 2026-06-05 | no live provenance match |
| 22 | unknown | unknown | al-dev-ticket | Clarity: "first token decides" precedence under-specified (re-flag) | 2026-06-05 | no live provenance match |
| 23 | unknown | unknown | al-dev-commit | Bloat: repetitive dispatch blocks across phases (re-flag) | 2026-06-05 | no live provenance match |
| 24 | unknown | unknown | al-dev-plan-swarm-validate | Description: 6-critic dispatch not shown in body (re-flag) | 2026-06-05 | no live provenance match |
| 25 | unknown | unknown | al-dev-develop | Clarity: undefined `<src-file>` placeholder and unexplained `-nt` operator | 2026-06-05 | no live provenance match |
| 26 | unknown | unknown | al-dev-fix | Clarity: ambiguous `IF complexity == 'medium' or 'complex'` branch | 2026-06-05 | no live provenance match |
| 27 | unknown | unknown | al-dev-interview | Clarity: INTERVIEW COMPLETE gate has no else clause | 2026-06-05 | no live provenance match |
| 28 | unknown | unknown | al-dev-lint | Clarity: no fallback when neither `al-compile` nor `al compile` available | 2026-06-05 | no live provenance match |
| 29 | unknown | unknown | al-dev-plan-preflight | Clarity: "substantive answer" undefined | 2026-06-05 | no live provenance match |
| 30 | unknown | unknown | al-dev-developer-tdd, al-dev-developer-traditional | Bloat: AL coding standards duplicated near-verbatim | 2026-06-05 | no live provenance match |
| 31 | unknown | unknown | al-dev-developer-tdd, al-dev-developer-traditional | Shared-backbone: identical dispatch pattern across /al-dev-develop and /al-dev-fix | 2026-06-05 | no live provenance match |
| 32 | unknown | unknown | al-dev-solution-architect | Bloat: 130-line workflow, repeated MCP guidance | 2026-06-05 | no live provenance match |
| 33 | unknown | unknown | al-dev-interview | Bloat: 90-line interview-process section with nested categories | 2026-06-05 | no live provenance match |
| 34 | unknown | unknown | al-dev-commit-hook-fixer | Bloat: 74-line procedure with nested Steps 1–5 | 2026-06-05 | no live provenance match |
| 35 | unknown | unknown | al-dev-commit-lint-fixer, al-dev-release-notes-writer, al-dev-commit-analyzer, al-dev-script-engineer, al-dev-support-researcher, al-dev-diagnostics-fixer | Bloat: oversized/overlapping sections | 2026-06-05 | no live provenance match |
| 36 | unknown | unknown | al-dev-solution-architect | Clarity: analogue yes/no examples; TESTABILITY_COMPLETE criteria | 2026-06-05 | no live provenance match |
| 37 | unknown | unknown | al-dev-commit-lint-fixer, al-dev-developer-tdd, al-dev-developer-traditional, al-dev-explore, al-dev-support-reply-drafter, al-dev-commit-recover-fixer | Clarity: vague qualifiers / undefined terms | 2026-06-05 | no live provenance match |
| 38 | unknown | unknown | al-dev-code-review | Name-fit: too generic vs specialist reviewers | 2026-06-05 | no live provenance match |
| 39 | unknown | unknown | al-dev-ticket-agent | Name-fit: "agent" classifier not verb | 2026-06-05 | no live provenance match |
| 40 | unknown | unknown | al-dev-commit-agent-analysis, al-dev-commit-agent-execute | Name-fit (Low): awkward suffixes | 2026-06-05 | no live provenance match |
| 41 | unknown | unknown | al-dev-explore, al-dev-commit-analyzer, al-dev-release-notes-writer | Structure (Low): code-fence / step-numbering | 2026-06-05 | no live provenance match |
| 42 | unknown | unknown | al-dev-consolidate, al-dev-document, al-dev-help, al-dev-perf, al-dev-plan, al-dev-release-notes, al-dev-review-develop, al-dev-ticket, commit-recover | Clarity: vague qualifiers / undefined terms | 2026-06-05 | no live provenance match |
| 43 | unknown | unknown | al-dev-consolidate, al-dev-develop, al-dev-explore, al-dev-plan-final-review, al-dev-support-reply | Description drift | 2026-06-05 | no live provenance match |
| 44 | unknown | unknown | al-dev-support-reply | Structure: argument-hint contradicts two usage modes | 2026-06-05 | no live provenance match |
| 45 | unknown | unknown | al-dev-lint, al-dev-perf, al-dev-plan-swarm-validate, al-dev-review-develop-preflight, al-dev-ticket, commit-recover, verify-commits | Structure (Low): missing `bash` language tags | 2026-06-05 | no live provenance match |
| 46 | unknown | unknown | al-dev-commit-agent-analysis | Caller-alignment: REPO documented required but dispatch never passes it | 2026-06-05 | no live provenance match |
| 47 | unknown | unknown | al-dev-developer-tdd, al-dev-developer-traditional | Caller-alignment (Low): inputs under-specify inline context fields | 2026-06-05 | no live provenance match |
| 48 | unknown | unknown | al-dev-consolidate | Surface-placement: no agents; references internal repo paths | 2026-06-05 | no live provenance match |
| 49 | unknown | unknown | al-dev-commit (chain) | Handoff-gap: no post-commit orchestration consumer | 2026-06-05 | no live provenance match |
| 50 | unknown | unknown | al-dev-fix, al-dev-consolidate | Handoff-gap (Low): test-plan.md / sessions-index.md unconsumed | 2026-06-05 | no live provenance match |
| 51 | unknown | unknown | al-dev-support-reply-drafter | Scope-isolation: Split internal-findings vs customer-reply into separate agents | 2026-06-05 | no live provenance match |
| 52 | unknown | unknown | al-dev-commit-lint-fixer | Clarity: `.git/.commit-baselines` written unconditionally; documented `.dev/` fallback never implemented | 2026-06-05 | no live provenance match |
| 53 | unknown | unknown | al-dev-plan-swarm-validate | Name-fit: name says "validate"; behavior drafts a plan then red-teams it | 2026-06-05 | no live provenance match |
| 54 | unknown | unknown | al-dev-commit | Bloat: 18 top-level Step/Phase headers; structural consolidation (header/verbosity aspect) | 2026-06-05 | no live provenance match |
| 55 | unknown | unknown | al-dev-plan-preflight | Bloat: Resume Modes A/B/C repeat near-identical file-loading | 2026-06-05 | no live provenance match |
| 56 | unknown | unknown | al-dev-commit-executor | Description: internal heading still reads `al-dev-commit-agent (Execute Phase)` after rename | 2026-06-05 | no live provenance match |
| 57 | unknown | unknown | al-dev-commit-executor | Description: internal heading still read `al-dev-commit-agent` after rename | 2026-06-05 | no live provenance match |
| 58 | unknown | unknown | al-dev-commit-lint-fixer | Clarity: `.dev/commit-baselines` fallback implemented as conditional `BASELINE_FILE` | 2026-06-05 | no live provenance match |
| 59 | unknown | unknown | al-dev-commit | Bloat: subsection consolidation (re-scoped — top level already ~5 phase groups; merged 0.3+0.4, 0.5+0.6, folded 4.2; fixed stale Step 9.5a/b agent refs) | 2026-06-05 | no live provenance match |
| 60 | unknown | unknown | al-dev-plan-preflight | Bloat: resume modes folded into decision tree + shared load step; doubled 1.5/1.6 intros and substantive-answer criteria deduped (re-scoped) | 2026-06-05 | no live provenance match |
| 61 | unknown | unknown | al-dev-plan-swarm-validate | Name-fit: renamed to `al-dev-plan-critic-review` | 2026-06-05 | no live provenance match |
| 62 | unknown | unknown | sync-documentation-maps family | Description: workflow-count frame inconsistent — sync/-collect say "Three-skill", -apply/-write say "Four-skill" + "two-step finalization" | 2026-06-05 | no live provenance match |
| 63 | unknown | unknown | plugin-health-discover | Description: documented `workflow_utils.py` dispatch path returns mock findings; §3.2 invocation cannot work as written | 2026-06-05 | no live provenance match |
| 64 | unknown | unknown | sync-documentation-maps-* agents (×4) | Structure: `model:` pinned to `claude-haiku-4-5-20251001` vs the `haiku` alias used by every other agent | 2026-06-05 | no live provenance match |
| 65 | unknown | unknown | plugin-health-discover | Bloat: 9 top-level sections; Phase 3 nested 3.1/3.1b/3.2/3.3 | 2026-06-05 | no live provenance match |
| 66 | unknown | unknown | al-dev-consolidate | Bloat: Phase 2 ~73 lines duplicate patterns now canonical in `consolidate-extraction-patterns.md` | 2026-06-05 | no live provenance match |
| 67 | unknown | unknown | al-dev-develop | Bloat: 9 top-level phases; Phase 4 Output section redundant with Phase 4 completion | 2026-06-05 | no live provenance match |
| 68 | unknown | unknown | al-dev-fix | Bloat: Decision Tree section duplicates Implementation Steps routing | 2026-06-05 | no live provenance match |
| 69 | unknown | unknown | al-dev-plan | Bloat: Phases 2–4 restate the architect contract + evidence rules | 2026-06-05 | no live provenance match |
| 70 | unknown | unknown | al-dev-ticket | Bloat: Steps 1/1.5 both resolve ticket input; Phase 5 repeats Phase 0.5 mode branching | 2026-06-05 | no live provenance match |
| 71 | unknown | unknown | sync-documentation-maps | Bloat: Phase 3 ~42 lines, nested 3.1/3.1b/3.2/3.3 | 2026-06-05 | no live provenance match |
| 72 | unknown | unknown | sync-documentation-maps-collect | Bloat: Phase 4 defers all dispatch logic to `collect-dispatch-patterns.md` (forward reference) | 2026-06-05 | no live provenance match |
| 73 | unknown | unknown | maintainer surface | No tooling lifecycle diagram (closes the accepted row dated 2026-06-05 above) | 2026-06-05 | no live provenance match |
| 74 | unknown | unknown | review-docs | Bloat: Phase 2 ~94 lines (2a Technical Accuracy + 2b Readability) | 2026-06-06 | no live provenance match |
| 75 | unknown | unknown | review-documentation-map | Bloat: Phase 4 ~70 lines across 4a/4b/4c | 2026-06-06 | no live provenance match |
| 76 | unknown | unknown | sync-documentation-maps-agent-audit | Bloat: Instructions (Steps 1–6) >30 lines | 2026-06-06 | no live provenance match |
| 77 | unknown | unknown | sync-documentation-maps-agent-update | Bloat: Instructions ~43 lines | 2026-06-06 | no live provenance match |
| 78 | unknown | unknown | sync-documentation-maps-skill-audit | Bloat: Instructions ~52 lines | 2026-06-06 | no live provenance match |
| 79 | unknown | unknown | sync-documentation-maps-skill-update | Bloat: Instructions ~43 lines | 2026-06-06 | no live provenance match |
| 80 | unknown | unknown | sync-documentation-maps-apply | Bloat: Phase 3 repeats file-validation 3× | 2026-06-06 | no live provenance match |
| 81 | unknown | unknown | sync-documentation-maps-collect | Bloat: Phase 4 parallels /sync Phase 4 | 2026-06-06 | no live provenance match |
| 82 | unknown | unknown | sync-documentation-maps | Bloat: checkpoint JSON field tables enumerated twice | 2026-06-06 | no live provenance match |
| 83 | unknown | unknown | sync-documentation-maps-write | Bloat: four near-identical regeneration blocks | 2026-06-06 | no live provenance match |
| 84 | unknown | unknown | plan-health-findings | Bloat: 7 top-level sections; Phase 2b ~35 lines | 2026-06-06 | no live provenance match |
| 85 | unknown | unknown | design-agent-lens-caller-alignment | Clarity: "dispatch line and context block" co-occurrence ambiguous | 2026-06-06 | no live provenance match |
| 86 | unknown | unknown | naming-convention-lens | Clarity: pipe set-notation for the plugin/tooling argument | 2026-06-06 | no live provenance match |
| 87 | unknown | unknown | quality-agent-lens-clarity | Clarity: own placeholder meta-notation risks self-flagging | 2026-06-06 | no live provenance match |
| 88 | unknown | unknown | quality-skill-lens-clarity | Clarity: own placeholder meta-notation risks self-flagging | 2026-06-06 | no live provenance match |
| 89 | unknown | unknown | sync-documentation-maps-agent-audit | Clarity: (none) literal normalization, type-mismatch risk | 2026-06-06 | no live provenance match |
| 90 | unknown | unknown | sync-documentation-maps-skill-audit | Clarity: sed pipe-before-filename command order | 2026-06-06 | no live provenance match |
| 91 | unknown | unknown | al-dev-consolidate | Clarity: inconsistent dir-name backticks + undefined "same session date" matching | 2026-06-06 | no live provenance match |
| 92 | unknown | unknown | audit-knowledge-quality | Clarity: "Explore subagent" not a named agent type here | 2026-06-06 | no live provenance match |
| 93 | unknown | unknown | plugin-health-discover | Clarity: single_use_agents zero-use inclusion + "right of an edge" Mermaid ambiguity | 2026-06-06 | no live provenance match |
| 94 | unknown | unknown | plugin-health-report | Clarity: "repeats" vs "match on substance" terminology | 2026-06-06 | no live provenance match |
| 95 | unknown | unknown | record-health-dispositions | Clarity: ← implemented / ← completed markers undefined | 2026-06-06 | no live provenance match |
| 96 | unknown | unknown | review-documentation-map | Clarity: node-ID grep doesn't state quoted IDs unsupported | 2026-06-06 | no live provenance match |
| 97 | unknown | unknown | sync-documentation-maps-apply | Clarity: "Exit 1 or other: runtime error" undefined | 2026-06-06 | no live provenance match |
| 98 | unknown | unknown | sync-documentation-maps | Clarity: "Abandoned runs" cites history without a defined rule | 2026-06-06 | no live provenance match |
| 99 | unknown | unknown | audit-knowledge-quality | Description: "targeted fixes" scope unclear | 2026-06-06 | no live provenance match |
| 100 | unknown | unknown | fix-knowledge-quality | Description: "converts findings into a task list" — task block originates in audit | 2026-06-06 | no live provenance match |
| 101 | unknown | unknown | plan-health-findings | Description: omits --skills/--agents routing | 2026-06-06 | no live provenance match |
| 102 | unknown | unknown | plugin-health-discover | Description: does not say it writes RAW findings, not the dossier | 2026-06-06 | no live provenance match |
| 103 | unknown | unknown | review-docs | Description: "archived path references" check absent from description | 2026-06-06 | no live provenance match |
| 104 | unknown | unknown | sync-documentation-maps-collect | Description: omits Resume/Restart + --wait | 2026-06-06 | no live provenance match |
| 105 | unknown | unknown | sync-documentation-maps | Description: omits Phase 0 cadence guard + --force | 2026-06-06 | no live provenance match |
| 106 | unknown | unknown | analyze-architectural-design | Bloat (Low): inline synthesis protocol overlaps /plan-health-findings rubber-duck | 2026-06-06 | no live provenance match |
| 107 | unknown | unknown | design-agent-lens-caller-alignment | Clarity (Low): "potential High" — drop "potential" | 2026-06-06 | no live provenance match |
| 108 | unknown | unknown | design-skill-lens-preplanning | Clarity (Low): substring-match else clause | 2026-06-06 | no live provenance match |
| 109 | unknown | unknown | sync-documentation-maps-agent-audit | Clarity (Low): "not a failure" double negative + relative ls path | 2026-06-06 | no live provenance match |
| 110 | unknown | unknown | al-dev-diagram-generator | Clarity (Low): "partial edge" undefined | 2026-06-06 | no live provenance match |
| 111 | unknown | unknown | design-agent-lens-caller-alignment | Description (Low): omits skills-dir grep | 2026-06-06 | no live provenance match |
| 112 | unknown | unknown | sync-documentation-maps-agent-update, -skill-update | Description (Low): says writes docs/al-dev-*-map.md; body writes to updates staging dir | 2026-06-06 | no live provenance match |
| 113 | unknown | unknown | sync-documentation-maps-write | Description (Low): omits "maintainer guide" from regenerated list | 2026-06-06 | no live provenance match |
| 114 | unknown | unknown | sync-documentation-maps-apply | Description (Low): "applies" omits Phase 3 validation | 2026-06-06 | no live provenance match |
| 115 | unknown | unknown | sync-documentation-maps | Name-fit (Low): name implies single sync; it dispatches audit agents + writes checkpoint | 2026-06-06 | no live provenance match |
| 116 | unknown | unknown | review-maps | Name-fit (Low): name suggests inspection; it is a mode-selection router | 2026-06-06 | no live provenance match |
| 117 | unknown | unknown | design-skill-lens-surface-placement, sync-documentation-maps-agent-audit/-agent-update/-skill-audit | Structure (Low): missing MD040 code-block language tags (agent files) | 2026-06-06 | no live provenance match |
| 118 | unknown | unknown | ~19 skill files | Structure (Low): pervasive MD040 missing code-block language tags | 2026-06-06 | no live provenance match |
| 119 | unknown | unknown | al-dev-diagram-generator | Structure (Low): Phase/Sub-step numbering inconsistency | 2026-06-06 | no live provenance match |
| 120 | unknown | unknown | align-harness-repos | Structure (Low): uses "Step N" instead of "Phase N" | 2026-06-06 | no live provenance match |
| 121 | unknown | unknown | sync-documentation-maps-agent-update | Bloat: Instructions ~43 lines | 2026-06-06 | no live provenance match |
| 122 | unknown | unknown | sync-documentation-maps-skill-update | Bloat: Instructions ~43 lines | 2026-06-06 | no live provenance match |
| 123 | unknown | unknown | sync-documentation-maps-collect | Description: omits Resume/Restart + --wait | 2026-06-07 | no live provenance match |
| 124 | unknown | unknown | sync-documentation-maps | Description: omits Phase 0 cadence guard + --force | 2026-06-07 | no live provenance match |
| 125 | unknown | unknown | sync-documentation-maps-write | Description (Low): omits "maintainer guide" from regenerated list | 2026-06-07 | no live provenance match |
| 126 | unknown | unknown | plugin-health-discover | Description: does not say it writes RAW findings, not the dossier | 2026-06-07 | no live provenance match |
| 127 | unknown | unknown | plan-health-findings | Description: omits --skills/--agents routing | 2026-06-07 | no live provenance match |
| 128 | unknown | unknown | review-docs | Description: "archived path references" check absent from description | 2026-06-07 | no live provenance match |
| 129 | unknown | unknown | audit-knowledge-quality | Description: "targeted fixes" scope unclear | 2026-06-07 | no live provenance match |
| 130 | unknown | unknown | fix-knowledge-quality | Description: "converts findings into a task list" — task block originates in audit | 2026-06-07 | no live provenance match |
| 131 | unknown | unknown | sync-documentation-maps-agent-update, -skill-update | Description (Low): says writes docs/al-dev-*-map.md; body writes to updates staging dir | 2026-06-07 | no live provenance match |
| 132 | unknown | unknown | sync-documentation-maps | Clarity: "Abandoned runs" cites history without a defined rule | 2026-06-07 | no live provenance match |
| 133 | unknown | unknown | sync-documentation-maps-skill-audit | Clarity: sed pipe-before-filename command order | 2026-06-07 | no live provenance match |
| 134 | unknown | unknown | sync-documentation-maps-agent-audit | Clarity (Low): "not a failure" double negative + relative ls path | 2026-06-07 | no live provenance match |
| 135 | unknown | unknown | record-health-dispositions | Clarity: ← implemented / ← completed markers undefined | 2026-06-07 | no live provenance match |
| 136 | unknown | unknown | review-documentation-map | Clarity: node-ID grep doesn't state quoted IDs unsupported | 2026-06-07 | no live provenance match |
| 137 | unknown | unknown | design-agent-lens-caller-alignment | Clarity: "dispatch line and context block" co-occurrence ambiguous | 2026-06-07 | no live provenance match |
| 138 | unknown | unknown | design-agent-lens-caller-alignment | Clarity (Low): "potential High" — drop "potential" | 2026-06-07 | no live provenance match |
| 139 | unknown | unknown | naming-convention-lens | Clarity: pipe set-notation for the plugin/tooling argument | 2026-06-07 | no live provenance match |
| 140 | unknown | unknown | design-skill-lens-preplanning | Clarity (Low): substring-match else clause | 2026-06-07 | no live provenance match |
| 141 | unknown | unknown | align-harness-repos | Structure (Low): uses "Step N" instead of "Phase N" | 2026-06-07 | no live provenance match |
| 142 | unknown | unknown | al-dev-diagram-generator | Clarity (Low): "partial edge" undefined | 2026-06-07 | no live provenance match |
| 143 | unknown | unknown | al-dev-diagram-generator | Structure (Low): Phase/Sub-step numbering inconsistency | 2026-06-07 | no live provenance match |
| 144 | unknown | unknown | plugin-health-report | Complexity → Atomise: 8 phases, two independently-runnable concerns (0–1d processing vs 2–4 generation+presentation) | 2026-06-07 | no live provenance match |
| 145 | unknown | unknown | design-skill-lens-near-duplicates | Model fit: multi-file comparative synthesis on haiku | 2026-06-07 | no live provenance match |
| 146 | unknown | unknown | design-skill-lens-preplanning | Model fit: multi-file cross-reference on haiku | 2026-06-07 | no live provenance match |
| 147 | unknown | unknown | design-skill-lens-shared-backbone | Model fit: multi-file pattern synthesis on haiku | 2026-06-07 | no live provenance match |
| 148 | unknown | unknown | sync-documentation-maps-agent-audit | Model fit: bash + Python + multi-file JSON aggregation on haiku | 2026-06-07 | no live provenance match |
| 149 | unknown | unknown | sync-documentation-maps-skill-audit | Model fit: same task profile as agent-audit, on haiku | 2026-06-07 | no live provenance match |
| 150 | unknown | unknown | docs/al-dev-plugin-synthesis.md | Handoff gap: produced by analyze-architectural-design; no downstream consumer | 2026-06-07 | no live provenance match |
| 151 | unknown | unknown | docs/superpowers/plans/<date>-<topic>.md | Handoff gap: plan→implement chain incomplete | 2026-06-07 | no live provenance match |
| 152 | unknown | unknown | sync-documentation-maps audit/update agents | Shared backbone: background-dispatch pattern not canonicalized in one doc | 2026-06-07 | no live provenance match |
| 153 | unknown | unknown | naming-convention-lens | Tool hygiene: Glob declared in frontmatter, unused in body | 2026-06-07 | no live provenance match |
| 154 | unknown | unknown | profile-al-dev-shared/generated/agents/ | Handoff gap: no downstream projection-vs-source validation skill | 2026-06-07 | no live provenance match |
| 155 | unknown | unknown | docs/al-dev-workflow-diagrams.md | Handoff gap: produced by diagram-generator/sync-write; no downstream consumer | 2026-06-07 | no live provenance match |
| 156 | unknown | unknown | plan-health-findings | Bloat: 7 top-level sections; Phase 2b ~35 lines | 2026-06-07 | no live provenance match |
| 157 | unknown | unknown | sync-documentation-maps-write | Bloat: four near-identical regeneration blocks | 2026-06-07 | no live provenance match |
| 158 | unknown | unknown | naming-convention-lens | Tool hygiene: Glob declared in frontmatter, unused in body | 2026-06-07 | no live provenance match |
| 159 | unknown | unknown | sync-documentation-maps-agent-audit | Model fit: bash + Python + multi-file JSON aggregation on haiku | 2026-06-07 | no live provenance match |
| 160 | unknown | unknown | sync-documentation-maps-skill-audit | Model fit: same task profile as agent-audit, on haiku | 2026-06-07 | no live provenance match |
| 161 | unknown | unknown | review-documentation-map | Bloat: Phase 4 ~70 lines across 4a/4b/4c | 2026-06-07 | no live provenance match |
| 162 | unknown | unknown | plugin-health-report | Complexity → Atomise: 8 phases, two independently-runnable concerns | 2026-06-07 | no live provenance match |
| 163 | unknown | unknown | review-docs | Bloat: Phase 2 ~94 lines (2a Technical Accuracy + 2b Readability) | 2026-06-07 | no live provenance match |
| 164 | unknown | unknown | review-docs | Bloat: repeated script/skill/path verification blocks in Technical Accuracy not templated | 2026-06-07 | no live provenance match |
| 165 | unknown | unknown | align-harness-repos | Bloat: Phase 5 token-replacement block >30 lines inline | 2026-06-07 | no live provenance match |
| 166 | unknown | unknown | review-documentation-map | Bloat: Phase 2 (~76 lines) profile extraction + caller sets inline | 2026-06-07 | no live provenance match |
| 167 | unknown | unknown | record-health-dispositions | Clarity: no rule for contradictory batch input | 2026-06-07 | no live provenance match |
| 168 | unknown | unknown | plugin-health-discover | Clarity: Phase 1 cadence guard missing else branch (happy path implicit) | 2026-06-07 | no live provenance match |
| 169 | unknown | unknown | plan-health-findings | Clarity: --skills/--agents and FILTER_TYPE interaction order not stated | 2026-06-07 | no live provenance match |
| 170 | unknown | unknown | design-agent-lens-caller-alignment | Clarity: "passed context with no dispatch line" severity label missing | 2026-06-07 | no live provenance match |
| 171 | unknown | unknown | design-skill-lens-near-duplicates | Clarity: "within 2 of each other" phase count comparison ambiguous | 2026-06-07 | no live provenance match |
| 172 | unknown | unknown | audit-knowledge-quality | Bloat: Phase 2a and 2b near-identical decision trees differing only by file-count threshold | 2026-06-07 | no live provenance match |
| 173 | unknown | unknown | align-harness-repos | Clarity: Phase 5 fenced-code-block trigger condition for manual-review flag is vague | 2026-06-07 | no live provenance match |
| 174 | unknown | unknown | audit-knowledge-quality | Clarity: Phase 2a step 2 no else branch for orphaned knowledge file | 2026-06-07 | no live provenance match |
| 175 | unknown | unknown | plan-health-findings | Clarity: "rubber-duck it by reading the live subject file in full first" — "in full" imprecise | 2026-06-07 | no live provenance match |
| 176 | unknown | unknown | plugin-health-discover | Clarity: Phase 3.1b "false" Move findings undefined operationally | 2026-06-07 | no live provenance match |
| 177 | unknown | unknown | review-documentation-map | Clarity: Phase 6 no else branch for "not accurate AND NO_UPDATE=false" | 2026-06-07 | no live provenance match |
| 178 | unknown | unknown | sync-documentation-maps-collect | Clarity: Phase 2 no guard against infinite retry | 2026-06-07 | no live provenance match |
| 179 | unknown | unknown | sync-documentation-maps-collect | Clarity: Phase 3 sort order and dedup winner unspecified | 2026-06-07 | no live provenance match |
| 180 | unknown | unknown | sync-documentation-maps-write | Clarity: "If the three values differ, stop" has no recovery action | 2026-06-07 | no live provenance match |
| 181 | unknown | unknown | plugin-health-audit | Description: implies single-unit dispatch; body delegates to two sub-skills | 2026-06-07 | no live provenance match |
| 182 | unknown | unknown | sync-documentation-maps-apply | Name Fit: "apply" implies writing; validation gate invisible to callers | 2026-06-07 | no live provenance match |
| 183 | unknown | unknown | sync-documentation-maps-apply | Structure: argument-hint references RUN_ID; body describes --team-ids parameter | 2026-06-07 | no live provenance match |
| 184 | unknown | unknown | sync-documentation-maps | Bloat: "Abandoned runs spawn audit agents whose results are never read" explanatory sentence in Phase 0 | 2026-06-07 | no live provenance match |
| 185 | unknown | unknown | record-health-dispositions | Bloat: Closure write-back rule dated procedural tone | 2026-06-07 | no live provenance match |
| 186 | unknown | unknown | align-harness-repos | Clarity: Phase 5 <placeholder> meta-notation undefined | 2026-06-07 | no live provenance match |
| 188 | unknown | unknown | record-health-dispositions | Naming: "record" verb and "health-dispositions" object outside documented sets | 2026-06-07 | no live provenance match |
| 189 | unknown | unknown | review-documentation-map | Naming: compound "documentation-map" object outside simple singular pattern | 2026-06-07 | no live provenance match |
| 190 | unknown | unknown | review-maps | Naming: plural "maps" object | 2026-06-07 | no live provenance match |
| 191 | unknown | unknown | design-agent-lens-caller-alignment | Structure: code blocks lack language tags | 2026-06-07 | no live provenance match |
| 194 | unknown | unknown | align-harness-repos | Structure: code blocks in Phase 2-4 lack language tags | 2026-06-07 | no live provenance match |
| 195 | unknown | unknown | analyze-architectural-design | Structure: code block lacks bash tag | 2026-06-07 | no live provenance match |
| 196 | unknown | unknown | audit-knowledge-quality | Structure: phase headers mix "Phase N" and "Step N" | 2026-06-07 | no live provenance match |
| 197 | unknown | unknown | fix-knowledge-quality | Structure: code blocks lack language tags | 2026-06-07 | no live provenance match |
| 198 | unknown | unknown | plugin-health-discover | Structure: code blocks lack bash tags | 2026-06-07 | no live provenance match |
| 199 | unknown | unknown | plugin-health-report | Structure: code blocks lack language tags; phase header punctuation inconsistent | 2026-06-07 | no live provenance match |
| 200 | unknown | unknown | projection-sync | Structure: code blocks lack bash tags | 2026-06-07 | no live provenance match |
| 201 | unknown | unknown | record-health-dispositions | Structure: code blocks lack bash tags | 2026-06-07 | no live provenance match |
| 202 | unknown | unknown | review-documentation-map | Structure: nested "### Phase 2b" under "## Phase 2" breaks header hierarchy | 2026-06-07 | no live provenance match |
| 203 | unknown | unknown | review-maps | Structure: code block lacks bash tag | 2026-06-07 | no live provenance match |
| 204 | unknown | unknown | sync-documentation-maps-apply | Structure: code blocks lack language tags | 2026-06-07 | no live provenance match |
| 205 | unknown | unknown | sync-documentation-maps-collect | Structure: code blocks lack language tags | 2026-06-07 | no live provenance match |
| 206 | unknown | unknown | review-docs | Bloat: repeated script/skill/path verification blocks in Technical Accuracy not templated | 2026-06-07 | no live provenance match |
| 207 | unknown | unknown | analyze-architectural-design | Structure: code block lacks bash tag | 2026-06-07 | no live provenance match |
| 208 | unknown | unknown | docs/al-dev-plugin-synthesis.md | Handoff gap: produced by analyze-architectural-design; no downstream consumer | 2026-06-07 | no live provenance match |
| 209 | unknown | unknown | align-harness-repos | Bloat: Phase 5 token-replacement block >30 lines inline | 2026-06-07 | no live provenance match |
| 210 | unknown | unknown | review-documentation-map | Bloat: Phase 2 (~76 lines) profile extraction + caller sets inline | 2026-06-07 | no live provenance match |
| 211 | unknown | unknown | record-health-dispositions | Clarity: no rule for contradictory batch input | 2026-06-07 | no live provenance match |
| 212 | unknown | unknown | plan-health-findings | Clarity: --skills/--agents and FILTER_TYPE interaction order not stated | 2026-06-07 | no live provenance match |
| 213 | unknown | unknown | design-agent-lens-caller-alignment | Clarity: "passed context with no dispatch line" severity label missing | 2026-06-07 | no live provenance match |
| 214 | unknown | unknown | design-skill-lens-near-duplicates | Clarity: "within 2 of each other" phase count comparison ambiguous | 2026-06-07 | no live provenance match |
| 215 | unknown | unknown | audit-knowledge-quality | Bloat: Phase 2a and 2b near-identical decision trees differing only by file-count threshold | 2026-06-07 | no live provenance match |
| 216 | unknown | unknown | align-harness-repos | Clarity: Phase 5 fenced-code-block trigger condition for manual-review flag is vague | 2026-06-07 | no live provenance match |
| 217 | unknown | unknown | audit-knowledge-quality | Clarity: Phase 2a step 2 no else branch for orphaned knowledge file | 2026-06-07 | no live provenance match |
| 218 | unknown | unknown | plan-health-findings | Clarity: "rubber-duck it by reading the live subject file in full first" — "in full" imprecise | 2026-06-07 | no live provenance match |
| 219 | unknown | unknown | plugin-health-discover | Clarity: Phase 3.1b "false" Move findings undefined operationally | 2026-06-07 | no live provenance match |
| 220 | unknown | unknown | review-documentation-map | Clarity: Phase 6 no else branch for "not accurate AND NO_UPDATE=false" | 2026-06-07 | no live provenance match |
| 221 | unknown | unknown | sync-documentation-maps-collect | Clarity: Phase 2 no guard against infinite retry | 2026-06-07 | no live provenance match |
| 222 | unknown | unknown | sync-documentation-maps-collect | Clarity: Phase 3 sort order and dedup winner unspecified | 2026-06-07 | no live provenance match |
| 223 | unknown | unknown | sync-documentation-maps-write | Clarity: "If the three values differ, stop" has no recovery action | 2026-06-07 | no live provenance match |
| 224 | unknown | unknown | plugin-health-audit | Description: implies single-unit dispatch; body delegates to two sub-skills | 2026-06-07 | no live provenance match |
| 225 | unknown | unknown | sync-documentation-maps-apply | Name Fit: "apply" implies writing; validation gate invisible to callers | 2026-06-07 | no live provenance match |
| 226 | unknown | unknown | sync-documentation-maps-apply | Structure: argument-hint references RUN_ID; body describes --team-ids parameter | 2026-06-07 | no live provenance match |
| 227 | unknown | unknown | record-health-dispositions | Bloat: Closure write-back rule dated procedural tone | 2026-06-07 | no live provenance match |
| 228 | unknown | unknown | align-harness-repos | Clarity: Phase 5 <placeholder> meta-notation undefined | 2026-06-07 | no live provenance match |
| 229 | unknown | unknown | design-agent-lens-caller-alignment | Structure: code blocks lack language tags | 2026-06-07 | no live provenance match |
| 232 | unknown | unknown | align-harness-repos | Structure: code blocks in Phase 2-4 lack language tags | 2026-06-07 | no live provenance match |
| 233 | unknown | unknown | audit-knowledge-quality | Structure: phase headers mix "Phase N" and "Step N" | 2026-06-07 | no live provenance match |
| 234 | unknown | unknown | fix-knowledge-quality | Structure: code blocks lack language tags | 2026-06-07 | no live provenance match |
| 235 | unknown | unknown | plugin-health-discover | Structure: code blocks lack bash tags | 2026-06-07 | no live provenance match |
| 236 | unknown | unknown | plugin-health-report | Structure: code blocks lack language tags; phase header punctuation inconsistent | 2026-06-07 | no live provenance match |
| 237 | unknown | unknown | projection-sync | Structure: code blocks lack bash tags | 2026-06-07 | no live provenance match |
| 238 | unknown | unknown | record-health-dispositions | Structure: code blocks lack bash tags | 2026-06-07 | no live provenance match |
| 239 | unknown | unknown | review-documentation-map | Structure: nested "### Phase 2b" under "## Phase 2" breaks header hierarchy | 2026-06-07 | no live provenance match |
| 240 | unknown | unknown | review-maps | Structure: code block lacks bash tag | 2026-06-07 | no live provenance match |
| 241 | unknown | unknown | sync-documentation-maps-apply | Structure: code blocks lack language tags | 2026-06-07 | no live provenance match |
| 242 | unknown | unknown | sync-documentation-maps-collect | Structure: code blocks lack language tags | 2026-06-07 | no live provenance match |
| 243 | unknown | unknown | plugin-health-discover | Bloat: 9 top-level sections; Phase 3 nested 3.1/3.1b/3.2/3.3 | 2026-06-07 | no live provenance match |
| 244 | unknown | unknown | sync-documentation-maps-agent-update | Bloat: Instructions ~43 lines | 2026-06-07 | no live provenance match |
| 245 | unknown | unknown | sync-documentation-maps-skill-update | Bloat: Instructions ~43 lines | 2026-06-07 | no live provenance match |
| 246 | unknown | unknown | plugin-health-discover | Clarity: Phase 1 cadence guard missing else branch (happy path implicit) | 2026-06-07 | no live provenance match |
| 247 | unknown | unknown | sync-documentation-maps | Bloat: "Abandoned runs spawn audit agents whose results are never read" explanatory sentence in Phase 0 | 2026-06-07 | no live provenance match |
