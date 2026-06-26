# Subagent Dispatch Batching

## Cold-Start Overhead

Each subagent dispatch carries a fixed cold-start token cost (~24k tokens per
invocation) regardless of the task size. This includes context loading, tool
registration, and first-response overhead.

For a fan-out that dispatches N independent agents in parallel:

- Token overhead = N × ~24k (cold-start) + actual task tokens
- At N=11 dispatches, fixed overhead is ~264k tokens before any work is done

## Decision Rule

Choose between per-unit and batched dispatch based on the primary constraint:

| Primary Constraint | Strategy | Use Case |
| --- | --- | --- |
| Latency | Per-unit dispatch | User waiting; independent units; cost acceptable |
| Token usage | Batched dispatch | Tight window; shared context possible; latency secondary |

## Reference Threshold

**N ≥ 8 units** is the practical inflection point where batching becomes worth
the coordination complexity. Below N=8, per-unit dispatch is usually simpler and
latency savings outweigh the token cost.

The ~24k cold-start floor is an empirical estimate as of 2026-06 for the skills
in this plugin. Calibrate against measured usage data when the pattern is
performance-critical.

## Related Docs

- `background-agent-dispatch.md` — mechanical fan-out pattern (how to dispatch,
  artifact hand-off, failure modes)
- `explore-subagent-pattern.md` — when to spawn a subagent (capability vs. cost)
