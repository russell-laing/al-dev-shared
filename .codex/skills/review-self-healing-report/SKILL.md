---
name: review-self-healing-report
description: Use when a recommendation-heavy report, tooling-health doc, architectural analysis, plan, or spec in al-dev-shared may have stale rankings, unsupported counts, or overstated fixes and must be checked against live repo state.
---

# Review Self-Healing Report

Review the artifact against live repo truth before trusting any recommendation.

Use this when the user says `rubber duck`, `review for technical accuracy`,
`second pass`, `patch again`, or `final sweep` on a report-like artifact.

## Use Cases

- `.dev/*.md` or `docs/health/*.md` reports with ranked actions
- plan/spec/report docs whose counts, severities, or updated-file claims may be stale
- repeated tightening passes on the same artifact

Do not use for generic code review.

## Required Input

One source artifact:

- a concrete path, or
- pasted report content

If missing, ask for it.

## Workflow

1. Read the full artifact. Extract scope, rankings, severity buckets, counts,
   and claimed updated files.
2. Verify live repo state before judging recommendations:

   ```bash
   git status --short
   rg -n "intent-preflight|artifact-contract|Phase 4 handoff|INTERVIEW COMPLETE|SYMBOL_PREFLIGHT_GATE|generate-map-doc-sections|generate-agent-projections" profile-al-dev-shared .claude .codex docs .dev
   ```

3. Read the exact live files behind the claims. Re-count inventories from disk;
   do not trust report metadata.
4. Use validators when relevant:

   ```bash
   python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
   python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
   python3 scripts/validate_artifact_contracts.py
   ```

5. Classify each finding as one of:
   - `valid blocker`
   - `valid but lower priority`
   - `overstated`
   - `stale`
   - `unsupported`
6. Re-rank by urgency:
   - runtime/contract failures
   - projection or generated-doc mismatches
   - artifact/handoff gaps
   - real but non-blocking clarity issues
   - hygiene
7. If the user asked to patch, edit the source artifact itself. Preserve the
   structure and add narrow corrections such as `Technical accuracy update`,
   `Corrected recommendation`, `Implementation context:`, or a short correction
   summary.
8. On repeat passes, re-open the same artifact, scan for leftover stale
   headings, duplicated findings, count drift, and contradictory recommendations,
   then patch again with the smallest safe edit.

## Output

- Review-only: findings first, ordered by severity/importance, with live repo
  evidence and corrected priority.
- Patch request: update the source artifact in place and report what changed.

## Guardrails

- Do not paraphrase the artifact back as the main answer.
- Do not trust same-day docs, generated maps, or report counts without live checks.
- Do not treat report recommendations as accepted requirements.
- Do not create a separate handoff note when the user asked to update the source.
- Do not broaden into a repo-wide audit unless asked.
- In a dirty worktree, validate touched/staged paths separately from unrelated changes.
- If original totals/tables are preserved, mark them as original or unrecomputed.

## Validation

Before claiming the artifact is ready:

```bash
git status --short
rg -n "Technical accuracy update|Corrected recommendation|Implementation context|correction summary" [report-path]
```

Confirm the remaining top-ranked actions still match live repo evidence.
