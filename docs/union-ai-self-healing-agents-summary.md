# How to Build Self-Healing Agents - Summary

Source: https://www.union.ai/blog-post/how-to-build-self-healing-agents

## Main idea

The article argues that agent failures in production are often not semantic failures from the model itself, but infrastructure failures: memory exhaustion, preempted instances, network timeouts, and process crashes. The key proposal is to treat infrastructure failures as part of the agent's context so the agent can recover instead of restarting from scratch.

## Core message

- Roughly half of workflow failures are infrastructure-related, so semantic evals alone are not enough.
- Agents become more durable when failure details are surfaced as structured context instead of opaque termination events.
- Recovery should be cheap and fast, not perfect.

## Three building blocks

1. Replay logs
   - Record per-run state at each step.
   - Let a run resume from the exact failed step instead of starting over.

2. Global caching
   - Reuse deterministic tool outputs across runs.
   - Cache research or data-fetching steps, but avoid caching creative synthesis steps when reuse would reduce quality.

3. Intermediate state persistence
   - Automatically store LLM calls, tool outputs, and intermediate results.
   - Preserves lineage, survives infra failures, and turns failed runs into inspectable artifacts.

## Six design principles

- Use plain Python or another language the LLM handles well.
- Add durability through wrappers or decorators rather than burying it in business logic.
- Make failures cheap by checkpointing, persisting state, and caching deterministic work.
- Feed infrastructure failures back into the agent loop as structured context.
- Provide sandboxed code execution paths for problems the normal toolset cannot handle.
- Use human-in-the-loop escalation only as the final fallback when the task cannot be recovered autonomously.

## Case study

The article describes a deep-research system that used checkpointing, layered orchestration, and caching to support very large agent runs. In that setup, spot-instance preemptions became short interruptions instead of lost work, duplicated research was reduced, and recovery time dropped significantly.

## Practical takeaway

Agents should be designed like durable workflows, not just clever prompts. If the infrastructure can checkpoint, persist, cache, and surface failures back into the loop, the agent can self-heal in many cases where a traditional implementation would fail outright.
