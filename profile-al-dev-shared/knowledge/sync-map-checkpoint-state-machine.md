# Sync-Map-Documentation Checkpoint State Machine

The `sync-map-documentation` workflow is a 4-skill async choreography. Checkpoint state must be passed through all stages with clear transition rules and recovery paths.

## Checkpoint Structure

```yaml
stage: string  # dispatcher | collect | apply | write
completed_at: ISO date
artifact_paths:
  plugin_metadata: path/to/plugin-artifact.json
  tooling_metadata: path/to/tooling-artifact.json
  plugin_audit: path/to/plugin-audit.json
  tooling_audit: path/to/tooling-audit.json
  plugin_update: path/to/plugin-update.md
  tooling_update: path/to/tooling-update.md
surface_count: int  # 1 (plugin only) or 2 (both)
version: int  # Schema version for evolution (start at 1)
last_error: (optional) string describing why a stage failed
```

## Valid State Transitions

```
dispatcher → collect:  All audit artifacts present
collect → apply:       All compare artifacts present + user decision recorded
apply → write:         All update artifacts present + validation passed
write → complete:      Generated diagrams and commits successful
```

## Recovery Paths

| Failure Point | Last Checkpoint | Recovery |
|---|---|---|
| Audit phase (dispatcher) | None exists | Re-run `/sync-map-documentation audit` |
| Collect phase (compare) | dispatcher checkpoint | Re-run `/sync-map-documentation collect --resume` (reuses audit artifacts) |
| Apply phase (write maps) | collect checkpoint | Re-run `/sync-map-documentation apply` (idempotent) |
| Write phase (regen + commit) | apply checkpoint | Re-run `/sync-map-documentation write` (detects partial state, retries) |

## Version Field

Increment `version` when the checkpoint schema changes:

- v1 (current): artifact_paths with plugin/tooling keys
- v2 (future): per-artifact metadata, timestamp tracking
- Consumers must validate version before assuming field structure

## Implementation Guidance

Each skill phase should:

1. **Read** current checkpoint (if resuming)
2. **Validate** it matches expected stage
3. **Execute** its phase
4. **Write** new checkpoint with updated `completed_at`, new `stage`, and persisted `artifact_paths`
5. **Clear** `last_error` on success; set it on failure
