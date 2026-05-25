# Codex State Fixture Notes

This skill does not commit a SQLite fixture because the local Codex `threads`
schema may evolve. Manual validation should be run against the operator's real
`~/.codex/state_5.sqlite` file after confirming the `threads` table contains at
least these columns:

- `source`
- `model_provider`
- `cwd`
- `archived`

If the schema changes in a future Codex release, update
`scripts/summarize_codex_usage.py` and these notes together.
