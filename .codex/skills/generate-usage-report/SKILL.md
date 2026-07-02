---
name: generate-usage-report
description: Convert harness-specific usage/session artifacts into an AI-harness-neutral markdown report, optionally augmenting the output with Codex-derived session observations from local Codex history/state data. Use when asked to review Claude Code Insights HTML, create a neutral cross-harness usage report, or include Codex-side usage observations in the same report.
---

# Generate Usage Report

Create a neutral markdown report from one or more AI harness usage artifacts.

## When to Use

Use this skill when the user asks to:

- review a Claude Code Insights HTML report
- convert a harness-specific usage report into neutral markdown
- include Codex-derived observations in a report
- write the final report into this repository's `.dev/` artifact area

## Output Convention

Write the final artifact to:

- `.dev/2026-07-02-ai-harness-neutral-usage-report.md`

If that filename already exists for the current day, append a short suffix that reflects the scope, for example:

- `.dev/2026-07-02-ai-harness-neutral-usage-report-claude-only.md`
- `.dev/2026-07-02-ai-harness-neutral-usage-report-cross-harness.md`

## Supported Inputs

### 1. Existing harness reports

Examples:

- `~/.claude/usage-data/report.html`
- any similar local HTML or markdown usage summary supplied by the user

For existing reports:

1. Read the source artifact directly.
2. Extract the core findings, metrics, strengths, friction points, and recommendations.
3. Rewrite them in harness-neutral language.
4. Keep product-specific terminology only when needed to identify a source artifact or tool capability.

### 2. Codex local session/history data

When the user asks to include Codex-side observations, inspect local Codex artifacts if available:

- `~/.codex/history.jsonl`
- `~/.codex/state_5.sqlite`

Use the helper script:

```bash
python3 .codex/skills/generate-usage-report/scripts/summarize_codex_usage.py \
  --history ~/.codex/history.jsonl \
  --state ~/.codex/state_5.sqlite
```

The script emits a markdown fragment that can be incorporated into the final report.

## Workflow

### Phase 1: Classify the request

Determine which of these applies:

- normalize an existing harness report only
- normalize an existing harness report and add Codex observations
- create a Codex-only usage summary

State the chosen scope briefly in the response before doing substantial work.

### Phase 2: Read source artifacts

For report files:

- read the source artifact directly
- extract:
  - reporting window
  - activity counts
  - dominant work patterns
  - strengths
  - friction/failure modes
  - recommendations
  - caveats or missing sections

For Codex data:

- run the helper script
- review the emitted markdown fragment before using it
- if the fragment is sparse or obviously misleading, say so and keep the Codex section minimal

### Phase 3: Write the neutral report

The report should usually use this structure:

1. `# AI Harness Neutral Usage Report`
2. `## Source`
3. `## Executive Summary`
4. `## Activity Snapshot`
5. `## Observed Working Style`
6. `## What Is Working Well`
7. `## Friction and Failure Modes`
8. `## Neutral Recommendations`
9. `## Codex Observations` (only when Codex data is included)
10. `## Caveats`
11. `## Bottom Line`

Keep the final wording:

- harness-neutral
- direct
- evidence-based
- explicit about missing data or inference

## Guardrails

- Do not describe the result as cross-harness unless Codex observations were actually included.
- Do not imply Codex has a built-in Insights HTML artifact unless one was explicitly provided.
- If the Codex data is limited to local history/session stores, state that clearly.
- Preserve useful exact counts from the source artifact when available.
- Do not silently drop notable caveats from the source artifact.

## Validation

Before reporting success:

1. Confirm the target markdown file exists in `.dev/`.
2. Re-open the file and scan for:
   - placeholder text
   - harness-specific wording that should have been generalized
   - claims about Codex unsupported by the local data actually read
3. If Codex observations were included, confirm the helper script ran successfully or explain why it could not.
