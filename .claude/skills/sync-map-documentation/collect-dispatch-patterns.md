# Collect Dispatch & Checkpoint-Merge Patterns

Shared procedure for the `sync-map-documentation-collect` phase that dispatches
the two background update agents and merges their IDs into the checkpoint. The
collect skill keeps its user-gate and collect-specific decisions inline and
references this doc for the mechanical dispatch + merge steps, mirroring the
companion docs `sync-agent-patterns.md` and `checkpoint-patterns.md`.

---

## Update-Agent Dispatch Skeleton

Once a `UPDATE_CHOICE` of `skills`, `agents`, or `both` has been resolved,
dispatch the selected update agents **in the background, in parallel** — issue
both calls in one message and do not wait for one before starting the other.
They target different artifact files. Use the `Agent` tool with
`run_in_background: true`, per the canonical Background-Agent Dispatch Pattern in
`.claude/skills/sync-map-documentation/checkpoint-patterns.md`.

- **Skills update** (when `UPDATE_CHOICE` is `skills` or `both`): dispatch
  `subagent_type: sync-map-documentation-skill-update` with a prompt that
  includes `RUN_ID` and `RUN_DIR`. Capture the returned background agent ID as
  `SKILL_UPDATE_TEAM_ID`.
- **Agents update** (when `UPDATE_CHOICE` is `agents` or `both`): dispatch
  `subagent_type: sync-map-documentation-agent-update` with a prompt that
  includes `RUN_ID` and `RUN_DIR`. Capture the returned background agent ID as
  `AGENT_UPDATE_TEAM_ID`.

For any surface not selected, set the corresponding ID variable to `null`.

---

## Checkpoint-Merge Procedure

Merge the new update-team IDs into both the root checkpoint and
`${RUN_DIR}/manifest.json` using the preserve-existing-fields merge pattern in
`.claude/skills/sync-map-documentation/checkpoint-patterns.md`. Update only
these fields; preserve all others:

| Field | Value |
|---|---|
| `phase` | `"update"` |
| `status` | `"dispatched"` |
| `update_choice` | `UPDATE_CHOICE` |
| `skill_update_team_id` | `SKILL_UPDATE_TEAM_ID` or `null` |
| `agent_update_team_id` | `AGENT_UPDATE_TEAM_ID` or `null` |

After merging, verify both files were written to disk:

```bash
ls -la /Users/russelllaing/al-dev-shared/.dev/sync-map-documentation-checkpoint.json
ls -la "${RUN_DIR}/manifest.json"
```

If either file is absent, stop and report the failure — do not report dispatch
success for a checkpoint that was not persisted.

---

## Return Summary

Print a summary and exit without waiting for update-team completion. Build the
next-step command using only the non-null update-team IDs:

```text
Update teams dispatched.

  Run ID:              RUN_ID
  Skills update ID:    SKILL_UPDATE_TEAM_ID   (or "not selected")
  Agents update ID:    AGENT_UPDATE_TEAM_ID   (or "not selected")
  Run directory:       RUN_DIR

Next step (when teams complete):
  /sync-map-documentation-apply --team-ids <non-null-ids>
```
