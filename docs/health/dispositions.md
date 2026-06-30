# Health Finding Dispositions

<!-- generated from docs/health/dispositions_events/; do not edit directly -->

| ID | Surface | Dimension | Object | Finding | Disposition | Date | Note |
|----|---------|-----------|--------|---------|-------------|------|------|
| disp_20260701_000005 | plugin | design | commit-preflight-staged-diff-crosscheck | Phase 2.1 presents PROPOSED_GROUPS with no cross-check against git diff --cached --name-only | fixed | 2026-07-01 | d12e85af — Add staged-file cross-check in Phase 2.1; verified live; closes disp_20260701_000001 |
| disp_20260701_000006 | plugin | quality | compile-lint-procedure | Documented plain-text diagnostic format contradicts actual SARIF/JSON output | fixed | 2026-07-01 | c1003861 — Update diagnostic format to SARIF JSON; verified live; closes disp_20260701_000002 |
| disp_20260701_000007 | plugin | design | commit-preflight-manifest-grep-permissionset | Inline manifest grep doesn't cover permission-set lines | fixed | 2026-07-01 | 7678dd02 — Extend manifest grep to permission-set lines; verified live; closes disp_20260701_000003 |
| disp_20260701_000008 | plugin | design | commit-compile-gate-fixed-cost | Compile gate always triggers full-project compile regardless of diff size | fixed | 2026-07-01 | a68e0130 — Document scoped compile future enhancement; verified live; closes disp_20260701_000004 |
| disp_20260701_000009 | plugin | quality | interview | 7 top-level sections exceed threshold of 6; creates cognitive load | accepted | 2026-07-01 | Structural Conventions — dossier 2026-07-01 |
| disp_20260701_000010 | plugin | quality | commit-group-drafter | Empty tools array is non-canonical | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000011 | plugin | quality | develop-orchestrate | Phase 1.2 (Signature Verification) oversized with 3 options + decision tree | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000012 | plugin | quality | plan-preflight | Phase 1.5 has 8 nested steps over 60+ lines; optional but heavyweight | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000013 | plugin | quality | plan | Phase 2 Retry Protocol (lines 172-195) is lengthy | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000014 | plugin | quality | lint | Step 2 lacks inline dispatch examples; Step 1 fallback unclear | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000015 | plugin | quality | interview | Phase 2 completion failure recovery is 11-line nested procedure | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000016 | plugin | quality | commit-execute | Phase 4.3 (Dispatch Hook-Failure Recovery) has complex 3-path branching | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000017 | plugin | quality | document | Formatting-Sweep Variant (lines 330-432) is 103 lines with 4 sub-steps | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000018 | plugin | quality | commit-preflight | Phase 1.1 has 16-line bash grep logic for manifest extraction | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000019 | plugin | quality | commit-analyzer | 200 changed lines gate is ambiguous—scope undefined | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000020 | plugin | quality | developer-tdd | Vague language: 'try to follow' and 'should compile' lack imperative force | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000021 | plugin | quality | developer-traditional | Vague language: 'should compile' lacks imperative force | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000022 | plugin | quality | general-code-reviewer | Incomplete fallback path (Step 1 lines 58-60 vague) | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000023 | plugin | quality | support-reply-drafter | Nested conditionals in Step 1.5 hard to parse | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000024 | plugin | quality | plan-preflight | Sufficient context requirement is underspecified; needs concrete template | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000025 | plugin | quality | investigate | Testable criterion is vague in hypothesis formulation | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000026 | plugin | quality | develop-orchestrate | Evidence precedence rule doesn't specify when to stop | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000027 | plugin | quality | lint | Case sensitivity and regex anchoring rules undefined | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000028 | plugin | quality | perf | Heuristic 'Run' suffix false-positives on many codeunit names | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000029 | plugin | quality | interview | Completion gate uses conditional proceed/re-run, not hard stop | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000030 | plugin | quality | commit-recover | Step 2 uses non-executable pseudo-code syntax | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000031 | plugin | quality | release-notes | Placeholders [start_hash] and [end_hash] lack executed example | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000032 | plugin | quality | commit-hook-fixer | Description mentions reversibility but body lacks verification step | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000033 | plugin | quality | diagnostics-resolver | Says escalates but body says delegate (internal, not escalation) | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000034 | plugin | quality | docs-writer | Promises maintain structure but only ensures folders exist | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000035 | plugin | quality | release-notes-writer | AL symbol research order vague; lookup conditional in Step 2 | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000036 | plugin | quality | commit-recover | Missing output contract for .dev/learnings.md and log format | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000037 | plugin | quality | help | Says recommend workflows but no .dev/ file or direct dispatch | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000038 | plugin | quality | research | Curated-first evidence undefined; which sources checked first | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000039 | plugin | quality | handoff | Description says migration but body is context packaging | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000040 | plugin | quality | plan-with-critics | Says six critics but doesn't clarify writing-plans is called first | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000041 | plugin | quality | perf | Escalation severity escalation vaguely defined | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000042 | plugin | quality | document | Says orchestrate/review but spawns single agent | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000043 | plugin | quality | commit-group-drafter | Weak verb 'drafter' undersells synthesis work | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000044 | plugin | quality | support-reply-drafter | Weak verb 'drafter' undersells synthesis work | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000045 | plugin | quality | commit-recover | Scope is narrow (corruption only), not recovery in general | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000046 | plugin | quality | plan-final-review | Validation + approval gate, not code review | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000047 | plugin | quality | support-reply | Doesn't send reply; drafts and gates on confirmation | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000048 | plugin | quality | plan-preflight | Name acceptable; preflight vs proceed could clarify | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000049 | plugin | quality | review-develop | Dispatcher role not signaled in name | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
| disp_20260701_000050 | plugin | quality | release-notes | Primary verb is generate via dispatcher | accepted | 2026-07-01 | Quality dossier 2026-07-01 |
