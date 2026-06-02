# Checkpoint Patterns for Multi-Phase Workflows

## JSON Checkpoint Read-Validate-Write Pattern

Multi-phase async workflows (e.g., audit + update + finalize) use a shared checkpoint file to track state across phases. This document defines the canonical pattern to prevent drift.

### Checkpoint File Location

`.dev/<workflow>-checkpoint.json` (e.g., `.dev/sync-documentation-maps-checkpoint.json`)

### Checkpoint Structure

```json
{
  "operation": "sync-documentation-maps",
  "run_id": "timestamp-id",
  "spawned_at": "iso-timestamp",
  "skill_audit_team_id": "team-id",
  "agent_audit_team_id": "team-id",
  "phase": "audit|update|complete",
  "status": "dispatched|skipped|complete|done",
  "result_dir": "/absolute/path",
  "auto_update": false,
  "skip_commit": false,
  "manifest_path": "/absolute/path/to/manifest.json",
  "update_choice": null,
  "skill_update_team_id": null,
  "agent_update_team_id": null
}
```

`sync-documentation-maps` writes the initial fields. `sync-documentation-maps-collect`
adds update fields. `sync-documentation-maps-finalize` marks completion. Preserve
unknown fields when updating either checkpoint file.

### Read Pattern (Phase 1 of each skill)

```bash
# Read checkpoint
checkpoint_file="/Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json"
checkpoint=$(cat "$checkpoint_file" 2>/dev/null || echo '{}')

# Extract fields
run_id=$(echo "$checkpoint" | jq -r '.run_id // empty')
phase=$(echo "$checkpoint" | jq -r '.phase // "unknown"')
status=$(echo "$checkpoint" | jq -r '.status // "pending"')

# Validate required fields
if [ -z "$run_id" ]; then
    echo "Error: checkpoint missing run_id"
    exit 1
fi
```

### Merge Pattern (Write in each Phase)

Use jq to merge updates while preserving pre-existing fields:

```bash
# Merge updates into existing checkpoint
new_data='{"phase":"update","status":"dispatched"}'
merged=$(jq -s '.[0] * .[1]' <(cat "$checkpoint_file") <(echo "$new_data"))

# Write atomically (temp + move)
temp_file="${checkpoint_file}.tmp.$$"
echo "$merged" | jq . > "$temp_file"
mv "$temp_file" "$checkpoint_file"

# Verify write
ls -la "$checkpoint_file" >/dev/null || exit 1
```

### Phase Progression

- **Dispatch**: `phase="audit"`, `status="dispatched"`
- **Collect updates selected**: `phase="update"`, `status="dispatched"`
- **Collect no updates needed**: `status="complete"` or `status="skipped"` depending on outcome
- **Finalize**: `phase="complete"`, `status="done"`

### Side Effects

This contract is currently specific to the three-skill `sync-documentation-maps`
workflow:

- `sync-documentation-maps`
- `sync-documentation-maps-collect`
- `sync-documentation-maps-finalize`

The workflow writes and updates these repo-local state files:

- `.dev/sync-documentation-maps-checkpoint.json` - root checkpoint read by each
  phase.
- `${RUN_DIR}/manifest.json` - run-local copy of the same checkpoint state.
- `.dev/progress.md` - dispatch and completion records appended by
  `sync-documentation-maps` and `sync-documentation-maps-finalize`.

The run directory is
`.dev/sync-documentation-maps-runs/${RUN_ID}`. The dispatcher creates
`${RUN_DIR}/audit` and `${RUN_DIR}/updates`; audit teams write
`${RUN_DIR}/audit/skill-audit.json` and `${RUN_DIR}/audit/agent-audit.json`,
and update teams write `${RUN_DIR}/updates/skills-map.md` and
`${RUN_DIR}/updates/agent-map.md` before finalize copies valid update artifacts
to their canonical documentation paths.

Future async workflows may reuse the read-preserve-update pattern, but should
document their own schemas instead of sharing this exact field set by default.
