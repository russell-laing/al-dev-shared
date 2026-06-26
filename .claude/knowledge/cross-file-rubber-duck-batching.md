# Cross-File Rubber-Duck Batching Strategy

When dispatching verify-health-finding agents, group findings by their subject file path. Batch findings that share the same subject file into a single agent call to reduce parallelism overhead while preserving focused context.

## Batching Rule

**K ≈ 5 findings per agent call** — group up to 5 findings with the same `subject_path` into one agent dispatch. This balances:

- **Parallelism benefit:** Running 4 parallel agents (5 findings each) is faster than 20 sequential agents (1 finding each)
- **Token cost:** One agent reads the 5-finding context once; N agents would read it N times
- **Context clarity:** 5 findings per file provide enough context to reason about coupling without overwhelming the agent

## Example

**Input:** 20 findings across 6 distinct subject files

- File A (8 findings) → 2 agent calls (5+3)
- File B (5 findings) → 1 agent call
- File C (3 findings) → 1 agent call
- Files D, E, F (1 finding each) → 1 agent call (batch singleton findings across multiple files)

**Output:** ~5 parallel agents instead of 20 sequential

## Implementation

When calling `superpowers:dispatching-parallel-agents`:

1. Group findings by `subject_path` (file)
2. Within each group, partition into K≤5-finding batches
3. Dispatch one agent per batch
4. Include `subject_path: [file1, file2, ...]` (list of paths in batch) in each agent's context

## Token Tradeoff

| Approach | Agent calls | Parallelism | Token cost/call | Total tokens |
|----------|------------|-------------|-----------------|--------------|
| No batching (1 finding/agent) | N | high | low | high (many calls) |
| K≈5 batching | N/5 | medium | medium | low (fewer calls, shared reads) |
| One-file batching | # files | low | high | medium (many calls, file re-reads) |

Choose K≈5 as the sweet spot: reasonable parallelism, bounded token growth.
