# Collect Resume Patterns

Reference for the Resume / Restart / Cancel decision gate in
`/sync-documentation-maps-collect` Phase 1.

## Status-Keyed Decision Gate

The checkpoint file at
`.dev/sync-documentation-maps-checkpoint.json` contains a `status` field that
controls whether the collect step runs fresh or enters the resume gate.

| Checkpoint `status` | Action |
| --- | --- |
| unset or `"audit"` | Proceed normally with fresh Phase 1 |
| `"dispatched"` / `"complete"` / `"skipped"` | USER\_GATE: Resume / Restart / Cancel (see below) |
| file absent | Stop — advise running `/sync-documentation-maps` first |

There is no `phase: collect` field. The gate keys solely on `status`.

## USER\_GATE Prompt

```text
A previous collect run reached status "<status>". How would you like to proceed?

[1] Resume — re-read artifacts and continue from where it left off
[2] Restart — re-run the full collect step from a clean state
[3] Cancel — stop without changes
```

## Branch Semantics

### Resume

Re-read the existing artifacts and continue with the `update_choice` and team
IDs already stored in the checkpoint. Valid after any of `"dispatched"` /
`"complete"` / `"skipped"`.

### Restart

Discard the prior update fields and re-run this collect step from a clean
state. **Do not clear `run_id` or `result_dir` from the checkpoint** — removing
those fields would break the downstream `-apply` and `-write` steps which need
them to locate artifacts. Restart does **not** re-dispatch the audit agents;
re-running the audits is `/sync-documentation-maps`'s job, not this skill's.

### Cancel

Stop with no changes.
