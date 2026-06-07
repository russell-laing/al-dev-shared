# Background-Agent Dispatch Pattern

Canonical pattern for running several independent agents in parallel **in the
current session** and collecting their results through files. Use this when a
skill fans work out to multiple worker agents whose outputs are handed back
through per-unit artifacts (for example, one agent per suggestion or parallel
audit/update agents that each write their own result file).

This is the harness-neutral contract. Each harness maps the dispatch instruction
to its own background-execution mechanism (see
[`harness-concepts.md`](harness-concepts.md)); the file-handoff and completion
rules below are identical across harnesses.

## When to use

- 2+ independent units of work that touch **different** output files.
- Each unit is self-contained: it reads its inputs, does its work, and writes one
  result artifact. No shared mutable state between units.

If the units would write to the same file, run them sequentially (inline)
instead — parallel writers to one artifact corrupt each other.

## The pattern

1. **Prepare a run directory.** Create a single timestamped directory that holds
   every artifact for this run (inputs, per-unit results, manifest). Pass its
   absolute path to each agent as `result_dir`.

2. **Dispatch agents in the background, in parallel.** For each unit, issue the
   harness-native background-dispatch instruction for the target agent:

   ```text
   Agent: al-dev-shared:<agent-name>
   Inputs: [only the unit-specific inputs, plus run_id and result_dir]
   Output artifact: [exact file path under result_dir]
   ```

   in background mode, issuing all dispatches together so they run concurrently.
   Give each agent only the inputs it needs plus `run_id` and `result_dir`, and
   tell it the exact artifact path it must write.

3. **Record the returned agent handles** (one per dispatch) in the run manifest or
   checkpoint artifact for traceability. If the caller does not keep a dedicated
   run manifest, record them in the phase checkpoint the workflow already writes.
   These handles are **informational only** — do not treat them as pollable task
   IDs.

4. **Hand off through artifacts.** Each agent writes its result to a fixed path
   under `result_dir`. The artifact file — not the agent handle — is the contract
   between the dispatching skill and the collecting skill.

5. **Gate on artifact presence.** The harness signals when a background agent
   finishes. The consuming phase confirms completion by checking that each expected
   artifact exists and is valid (non-empty, expected header/schema). Treat a
   missing or malformed artifact as "that unit is not done", regardless of any
   reported agent status. If artifacts are still absent, either wait and re-check,
   or report the units as pending.

   Example validity checks:
   - markdown result has the required top-level heading for that unit
   - structured output includes the expected keys or sections
   - error artifacts use the documented error record shape instead of partial prose

## What this pattern is not

This is **in-session** background execution: artifacts land on the local
filesystem the dispatching session can read. It is distinct from **scheduled cloud
routines**, which execute server-side in a managed environment and therefore cannot
write to the local run directory. Do not use a scheduled-routine mechanism to
implement this pattern — its results never reach the local `result_dir` the
collecting phase reads.

## Failure handling

- **Dispatch unavailable:** if the session cannot spawn background agents, stop and
  ask the user to rerun in a supported session, or fall back to running the units
  inline (sequentially) for small batches while preserving the same per-unit
  artifact paths and validation checks.
- **Partial completion:** if some artifacts are present after a reasonable wait and
  others are not, surface the pending units via a `USER_GATE` and let the user
  choose to wait, proceed with the completed subset, or abort.
- **Failed unit:** if an agent writes an error record instead of a result, include
  it in the aggregation as a failure rather than silently dropping it.
