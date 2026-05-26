# AI Harness Neutral Usage Report

## Source

- Source artifact: `~/.claude/usage-data/report.html`
- Reporting window: `2026-04-22` to `2026-05-23`
- Scope: 2,433 messages across 378 sessions, 688 files touched, net line movement of `+102,100/-4,589`

## Executive Summary

The source report describes a month of highly structured, plan-driven AI-assisted development. The dominant pattern is deliberate: specs become detailed plans, plans become subagent-assisted execution, and execution is gated by review and commit hygiene. The strongest results come from parallel analysis, especially when competing designs are pressure-tested before implementation.

The main failure modes are also clear. AL code generation still produces compile-time errors often enough to trigger repeated edit/retry cycles, and a smaller but recurring class of issues comes from scope creep, stale context, or non-productive command usage.

## Activity Snapshot

- 378 sessions over 30 days
- 2,433 messages, or 81.1 messages per day
- 227 fully achieved outcomes, 47 mostly achieved, 13 partially achieved, 3 not achieved, and 5 unclear
- The report’s strongest work areas are AL/Business Central development, plan creation and subagent-driven execution, skill and agent architecture design, knowledge-base quality work, and plugin configuration/context setup

## Observed Working Style

The working style is methodical and review-oriented. The source report emphasizes plan-first execution, parallel lens-based analysis, and rubber-duck refinement before code is accepted. It also shows a preference for many multi-file changes and for using agents to explore alternatives before choosing an implementation path.

The report’s own counts reinforce that pattern: multi-file changes are the leading helpful capability, and task completion is usually high once work is organized into explicit plans with review gates.

## What Is Working Well

- Plan-first, subagent-driven execution is the clearest strength.
- Parallel analysis catches real design errors before they become code.
- Iterative review improves the quality of plans and documentation before implementation starts.
- The source report credits 227 fully achieved sessions, which is a strong signal that the overall workflow is effective when scope is well bounded.
- The most helpful capabilities in the report are multi-file changes, good explanations, correct code edits, and good debugging.

## Friction and Failure Modes

- AL compilation failures are the dominant technical friction. The report repeatedly mentions non-existent field references, wrong object types, and incorrect object IDs.
- Scope creep appears in both commits and edits, especially when unrelated files are swept into a change or a review task turns into an implementation task.
- Stale logs, false positives, and non-interactive command noise waste time and obscure the actual problem.
- The report treats some compile-hook failures as warnings, but the narrative says that is not always safe and can leave work only partially complete.

## Neutral Recommendations

- Validate object IDs, field references, and type declarations against base app symbols before writing AL code.
- Treat compile-hook failures as hard gates instead of assuming they are pre-existing warnings.
- Keep review commands read-only unless an edit is explicitly requested.
- Stage explicit file paths instead of broad commit operations.
- Confirm the freshness and scope of logs before debugging them deeply.

## Codex Observations

These observations are derived from local Codex history/state data rather than a built-in Codex Insights report.

- History sessions seen: `25`
- History messages seen: `128`
- Active thread rows seen: `65`
- First history timestamp seen: `2026-05-15 09:08:17Z`
- Last history timestamp seen: `2026-05-23 12:09:52Z`

### Pattern Hints

- Top thread sources: `cli` dominates; a small number of subagent-spawn records also appear in the thread table.
- Top model providers: `openai (65)`
- Top working directories: `/Users/russelllaing/al-dev-shared (36)`, `/Users/russelllaing/codex-configs (29)`

### Interpretation Limits

- This section is inferential and based only on locally readable Codex history/state artifacts.
- It does not include a built-in Codex sentiment, friction, or recommendation engine.

## Caveats

- The source report is Claude-branded, so the numeric and qualitative findings reflect that harness’ activity stream.
- The Codex section is derived from local history/state data, not a built-in Insights report.
- The report uses inference for some behavioral conclusions; those are not direct measurements.

## Bottom Line

This is a high-discipline workflow with strong results when work is planned, split, and reviewed explicitly. The main gains come from keeping AL validation tight, reducing scope drift, and treating stale or noisy context as a first-class risk.
