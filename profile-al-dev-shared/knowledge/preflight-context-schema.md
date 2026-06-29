# PREFLIGHT_CONTEXT Schema

Canonical schema for `.dev/preflight-context.md`, the context block written
by `/plan-preflight` and consumed by `/plan` (Phase 2 architect
debate) and any other workflow that chains preflight.

Writer: `/plan-preflight` (end of Phase 1.6). Overwrite any existing
context file — latest state wins.

## Schema

```json
{
  "phase": 2,
  "requirements": "user feature requirement and preliminary scope",
  "scope": "estimated file count, affected BC objects, patterns",
  "architect_model": "opus",
  "user_context": "object ID range, naming prefix, key patterns, perf/explore findings",
  "external_findings_status": "summary of verified/unverified claims, or null",
  "timestamp": "2026-06-01T00:00:00Z",
  "no_crit_swarm": false
}
```

## Field Semantics

| Field | Meaning |
|---|---|
| `phase` | Always `2` — the next phase the consumer should enter |
| `requirements` | The user requirement plus preliminary scope statement |
| `scope` | Estimated file count, affected BC objects, patterns |
| `architect_model` | Model assignment from complexity triage (`sonnet` or `opus`) — consumers must not re-triage |
| `user_context` | Object ID range, naming prefix, key patterns, plus any perf/explore findings |
| `external_findings_status` | The **External findings status:** block forwarded to architects, or `null` if claim verification was skipped |
| `timestamp` | ISO 8601 write time |
| `no_crit_swarm` | When `true`, consumers skip the critic-swarm validation step |

If a required field is missing when consuming the block, re-run the specific
preflight step that produces it (or re-dispatch `/plan-preflight`)
rather than proceeding with empty state.
