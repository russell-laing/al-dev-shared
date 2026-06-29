# Expected Health Phases

This benchmark contract lists prospective procedure-log phases that the adapter
can compare against retrospective procedure-integrity checks. Start with
`implement-plugin-health`; extending this file to upstream health skills
requires updating the adapter tests and the relevant skill prompts in the same
change.

## implement-plugin-health

| Phase | Required proof |
| --- | --- |
| 0 | plan_located |
| 1 | tasks_executing |
| 2 | per_task_verified |
| 3 | ledger_closed |
| 4 | artifacts_finalized |
| 5 | loop_closed |
