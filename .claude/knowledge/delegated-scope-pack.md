# Delegated Scope Pack

Repo-local enforcement shape for the shared
`profile-al-dev-shared/knowledge/scope-expansion-gate.md`. The shared gate
states the *policy* (agents must not expand scope); this contract defines how
maintainer execution lanes *package and check* that policy when they delegate
a task.

## The scope pack

Every delegated maintainer task ships a scope pack in its dispatch prompt:

- **Allowed paths:** the exact files/globs the task may create or modify.
- **Do-not-touch list:** surfaces the task must never write outside Allowed
  paths; manual ledger edits are never allowed. Disposition store artifacts
  (`docs/health/dispositions_events/`, `docs/health/dispositions_open.md`,
  `docs/health/dispositions_current.md`,
  `docs/health/dispositions_index.json`, and the generated compatibility view
  `docs/health/dispositions.md`) are protected surfaces and may only be
  modified when they are explicitly included in Allowed paths for a close-back
  flow. Validator scripts remain out of scope unless explicitly listed.
- **Expected outputs:** the artifact path(s) the dispatcher will verify on
  return.

## Post-task diff sanity check

After the agent returns, before accepting its result, the dispatcher runs a
diff sanity check and rejects out-of-scope changes:

```bash
REPO=$(git rev-parse --show-toplevel)
git -C "$REPO" status --short
```

Any path not in Allowed paths — extra ledger rows, validator edits, partial
renames, unrelated touches — is a scope violation: discard or revert the
out-of-scope change and re-dispatch with the violation named, per the shared
gate's retry rule.

## Skills in scope

The authoritative list is the `DELEGATING_EXECUTION_SKILLS` set in
`scripts/validate_maintainer_contracts.py` — lanes that delegate *mutating*
work (not read-only audits).

## Related contracts

- `profile-al-dev-shared/knowledge/scope-expansion-gate.md` (shared): policy.
- `profile-al-dev-shared/knowledge/background-agent-dispatch.md` (shared):
  delegated artifact contract this pack extends.
- `dispatch-fallback-contract.md`: the lane that carries the scope pack.
