# Critic Dispatch Template

This template documents the parallel critic/reviewer agent dispatch pattern
used by `/plan-with-critics` (6-critic panel) and `/review-develop` 
(3-reviewer panel). Both skills use identical structure: dispatch agents in
parallel, aggregate findings, dedupe by severity, synthesize into unified report.

## Pattern Overview

1. **Dispatch Phase:** Launch N independent agents in parallel (each critic/reviewer 
   operates independently, no shared state). Each agent reads the same context 
   (spec/code) and generates a findings list with severity ratings.

2. **Aggregation Phase:** Collect all agent outputs into a single list.

3. **Deduplication Phase:** Dedupe findings by (file, line, class) tuple — if 
   two agents report the same issue, keep highest severity, discard duplicates.

4. **Synthesis Phase:** Rank deduplicated findings by severity (HIGH → MEDIUM → LOW) 
   and synthesize into a single report document with a unified severity distribution.

## Implementation Variants

### 6-Critic Variant (plan-with-critics)
- **Agents:** 6 independent critic agents (approach-A, approach-B, etc.)
- **Dispatch:** Parallel invocation, all in same skill phase
- **Dedup strategy:** Severity-based (keep highest severity per issue)
- **Output:** Unified findings report with 6-critic consensus

### 3-Reviewer Variant (review-develop)
- **Agents:** 3 independent reviewer agents (correctness, testing, architecture)
- **Dispatch:** Parallel invocation, all in same skill phase
- **Dedup strategy:** Severity-based (keep highest severity per issue)
- **Output:** Unified review report with 3-reviewer consensus

## When to Use

Use this template when:
- A skill needs independent parallel agent evaluation (no inter-agent communication)
- Multiple agents assess the same context and produce independent findings
- Findings must be deduplicated and re-ranked before synthesis
- Output should be a single unified report combining all perspectives

## Common Implementation Gotchas

- **Shared state:** Ensure agents have NO shared mutable state; each must 
  independently assess the input
- **Dedup correctness:** When two agents find the same issue at the same location 
  but with different severity, keep the higher severity rating
- **Synthesis order:** Re-sort by severity AFTER dedup, not before (else lower-severity 
  duplicates may be sorted ahead of higher-severity unique findings)
