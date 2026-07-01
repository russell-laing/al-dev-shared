# Design: Multi-Phase Skill Structure

## Phase Isolation Principle

Multi-phase skills (discover → report → plan → implement) must have sequential, non-coupled phases. Each phase completes to a durable checkpoint before the next phase begins, enabling recovery from failure midway through the loop.

## Why Sequential, Not Coupled

- **Recoverability:** A failed phase can be re-run without re-running prior phases.
- **Context freshness:** Each phase starts with a clean read of its inputs, preventing stale-data bugs from propagated intermediate state.
- **Parallel-friendliness:** Future phases can dispatch multiple subagents in parallel knowing the prior phase's outputs are durable.

## Checkpoint Contracts

Each phase must write its outputs to a durable checkpoint file before reporting completion. See `./health-loop-state-contract.md` for the exact schema.

## Related Skills

- `/discover-plugin-health` — discovers findings, writes to `docs/health/YYYY-MM-DD-*-findings.md`
- `/report-plugin-health` — reads findings, writes to `docs/health/YYYY-MM-DD-*-health.md`
- `/plan-plugin-findings` — reads verified checkpoint, writes to `docs/superpowers/plans/`
- `/implement-plugin-health` — executes plan, writes `fixed` ledger events

Phases are always sequential; the health loop forces fresh sessions at phase boundaries.
