# Dispatch-Fallback Contract

Repo-local rule for maintainer skills that delegate work to agents. It
closes the "dispatch fragility" gap: wasted cycles from a preferred
delegation mechanism failing (schema-invalid tool, missing permission,
empty output) before a manual pivot.

Every dispatch lane must make four things explicit.

## 1. Preferred path

Name the delegation mechanism this lane uses first. For audit/health/sync
fan-out in this repo, the preferred mechanism is the `Agent` tool.

## 2. Preflight

Before dispatching, confirm the mechanism is usable: the tool is available
in this session, and the arguments match the receiving skill/agent contract
(surface vs. dimension values, required file paths exist). A failed preflight
skips straight to the fallback — it does not attempt the dispatch.

## 3. Fallback path

State what happens when the preferred path fails, by failure class:

- Schema/validation failure (e.g. `RemoteTrigger` does not validate in this
  repo's workflows): do not retry the same mechanism; switch to the `Agent`
  tool or inline execution.
- Permission failure: report the blocked action and the exact permission
  needed; do not silently work around it.
- Empty/short output: re-dispatch once with the failure embedded, then fall
  back to inline (per shared `workflow-resilience.md`).

## 4. Log line

Emit one line recording `preferred → outcome → fallback → reason` so the
execution state is auditable rather than inferred.

## Skills in scope

The authoritative list is the `DISPATCHING_SKILLS` set in
`scripts/validate_maintainer_contracts.py` — skills whose body spawns one or
more agents.

## Related contracts

- `profile-al-dev-shared/knowledge/workflow-resilience.md` (shared): empty
  output and usage-limit fallback after dispatch starts.
- `profile-al-dev-shared/knowledge/background-agent-dispatch.md` (shared):
  exact inputs, fixed artifact paths, artifact-based completion gates.
- The project `CLAUDE.md` "Tool Usage" and "Skill Invocation" sections state
  the `RemoteTrigger`-avoidance and surface/dimension argument rules this
  contract operationalizes.
