# Collect Phase — Artifact Polling and Read

Canonical poll-then-read state machine for `/sync-documentation-maps-collect`
Phase 2. The audit agents run as background agents and write their results to
`${RUN_DIR}/audit/`. This doc owns the branching so the skill body stays short.
Background-agent IDs are **not** pollable with `TaskGet`; the artifact files are
the authoritative completion signal (see `checkpoint-patterns.md`).

## Inputs

- `WAIT_MODE` — `true` if `--wait` was passed, else `false`.
- `RUN_DIR` — run directory extracted from the checkpoint.

## Poll (only when `WAIT_MODE=true`)

Poll on **artifact presence** — `ls "${RUN_DIR}/audit/skill-audit.json"` and
`ls "${RUN_DIR}/audit/agent-audit.json"` — until both files exist or the timeout
is reached. Log
which files are present after each check. Do not wait more than 30 minutes
total; if the timeout is reached, advise the user to retry later and stop.

When `WAIT_MODE=false`, skip polling — the harness notifies when the background
agents finish, and the read step below handles any artifact still absent.

## Read audit artifacts

Verify presence of both audit results:

```bash
ls -la "${RUN_DIR}/audit/skill-audit.json" 2>/dev/null
ls -la "${RUN_DIR}/audit/agent-audit.json" 2>/dev/null
```

For each present file, read and parse the JSON. Extract `surface`,
`discrepancies` (array), and `summary` (string).

## Absence handling

- **One file absent, `WAIT_MODE=false`** → record that surface as `pending`,
  report that the harness will notify on completion, and do **not** block. The
  user re-runs collect (or runs `--wait`) once notified.
- **Same surface still `pending` on a later collect re-run for the same
  `RUN_ID`** → treat it as stalled, not "still pending". Report the missing
  artifact path, note that the current run did not complete its audit write, and
  tell the user to restart from `/sync-documentation-maps` instead of looping on
  collect.
- **Both files absent** → stop with:

  ```text
  Audit results not yet available. Re-run with --wait to block until complete,
  or wait for the teams to finish and then re-run this collect step.
  ```
