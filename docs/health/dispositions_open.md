# Open Health Dispositions

<!-- generated from docs/health/dispositions_events/; do not edit directly -->

| Event ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence | Closes |
|----------|---------|-----------|--------|---------|-------------|------|----------|--------|
| disp_20260702_000016 | tooling | quality | design-skill-lens-preplanning | High/Structural: Regressed to 7 top-level sections; reduce section count or extract concern | accepted | 2026-07-02 | Regressed from 6 sections (declined 2026-06-27, was accurate then) to 7 after commit e7115f68; re-verified live 2026-07-02 — genuine regression, not measurement error |  |
| disp_20260702_000094 | plugin | quality | commit-analyzer.md | Bash code blocks mix procedural description with executable commands | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000095 | plugin | quality | interview.md | Description claims direct user interaction but body reveals orchestrator role | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000096 | plugin | quality | question-gatherer.md | Named 'question-gatherer' but produces answers, not questions | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000097 | plugin | quality | solution-architect.md | 'Rogue File Guard' section verbose and could be condensed | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000098 | plugin | quality | developer-tdd.md | Inputs table repeats 'auto-located by glob' in 4 rows | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000099 | plugin | quality | diagnostics-resolver.md | 'Judgment-Required Rules Reference' table belongs in knowledge file | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000100 | plugin | quality | developer-traditional.md | Dispatch context repeats language from developer-tdd.md | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000101 | plugin | quality | diagnostics-classifier.md | 'Assess fixability' undefined; 'mechanical pattern match' not operationally defined | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000102 | plugin | quality | spec-writer.md | Outputs section lists categories with no format specification | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000103 | plugin | quality | explore.md | Tool list shows no Bash but 'Tool: Bash Output Capture' section discusses Bash | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000104 | plugin | quality | support-reply-drafter.md | 'Critical reading' section uses vague language without specifying tools | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000105 | plugin | quality | ticket-context-writer.md | Inline image detection refers to knowledge file without fallback | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000106 | plugin | quality | change-analyzer.md | Outputs section unclear if structure is actual format or template | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000107 | plugin | quality | solution-architect.md | Description says agent creates plans but outputs show /plan Phase 5 creates them | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000108 | plugin | quality | findings-synthesizer.md | Description says '3 independent MCP sources' but only 1 is MCP | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000109 | plugin | quality | evidence-gatherer.md | Description says 'Search 3 MCP sources' but input-tool mapping not specified | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000110 | plugin | quality | commit-hook-fixer.md | Description assumes pre-classified input; doesn't cover non-fixable failures | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000111 | plugin | quality | docs-writer.md | Description lists both 'docs/' and 'wiki/' but doesn't clarify preference | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000112 | plugin | quality | release-notes-writer.md | Description says agent 'extracts' changes but body shows it invokes sub-agent | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000113 | plugin | quality | findings-synthesizer.md | Generic name; 'evidence-synthesizer' more accurate | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000114 | plugin | quality | explore.md | Generic name; 'codebase-explorer' clarifies scope | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000115 | plugin | quality | support-researcher.md | Generic name; 'bc-support-researcher' clarifies domain | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000116 | plugin | quality | diagnostics-classifier.md | Boundary with diagnostics-fixability-decision unclear from name | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000117 | plugin | quality | document.md | Formatting-Sweep Variant is 102-line alternate workflow bundled as secondary mode | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000118 | plugin | quality | plan-final-review.md | Validator fix patterns could use extracted knowledge file or bullet list | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000119 | plugin | quality | review-develop.md | Phase numbering jumps from Phase 0 to Phase 4 (Phases 1–3 absent) | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000120 | plugin | quality | commit-execute.md | Line 264 malformed git command: trailing -- requires path argument | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000121 | plugin | quality | commit-preflight.md | Verdict categories introduced via conditionals, should be enumerated upfront | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000122 | plugin | quality | document.md | 'Context-continuation check' described in prose without concrete verification steps | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000123 | plugin | quality | fix.md | Complexity classification uses subjective terms; boundaries ambiguous for edge cases | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000124 | plugin | quality | generic-preflight.md | 'Context gathering' (Phases 1–2) undefined in skeletal skill | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000125 | plugin | quality | help.md | 'Quick reference' intentionally concise but omits edge cases | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000126 | plugin | quality | investigate.md | Template reference lacks structure; unclear what fields required | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000127 | plugin | quality | perf.md | Classification heuristic rule not stated, only assumed | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000128 | plugin | quality | plan.md | Resume modes labeled A/B/C internally, schema refers only as conditions | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000129 | plugin | quality | plan-with-critics.md | Step 1 doesn't show complete prompt or success criteria | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000130 | plugin | quality | research.md | Phases very brief; 'shallow' stopping rule subjective, sparse on procedure | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000131 | plugin | quality | commit-execute.md | Description doesn't mention dispatched agent 'commit-executor' | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000132 | plugin | quality | commit-recover.md | Description says file 'always present' but Step 1 says 'may be absent' | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000133 | plugin | quality | develop-orchestrate.md | Emphasizes 'dispatch' but downplays 'Handoff to /review-develop' integration | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000134 | plugin | quality | document.md | Description over-promises Mode 2 as secondary when actually parallel | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000135 | plugin | quality | generic-preflight.md | Description over-promises 'state checkpointing' not shown in body | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000136 | plugin | quality | perf.md | Primary verb is 'Analyze for performance' not 'classifies codeunit type' | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000137 | plugin | quality | research.md | Generic description without naming four available modes | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000138 | plugin | quality | document.md | Generic name; two modes not distinguished by name | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
| disp_20260702_000139 | plugin | quality | research.md | Generic name; BC/AL specialization not indicated | accepted | 2026-07-02 | User decision: disposition batch, quality dimension |  |
