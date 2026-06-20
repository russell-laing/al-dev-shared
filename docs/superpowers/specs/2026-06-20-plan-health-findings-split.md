# plan-health-findings Split: Intermediate Artifact Contract

**Date:** 2026-06-20
**Status:** Draft — pending implementation
**Accepted finding:** disp_20260620_000092 (Atomise, tooling/design, 2026-06-20)

## Background

`plan-health-findings` (`.claude/skills/plan-health-findings/SKILL.md`, 459 lines)
runs five sequential phases:

- **Phases 0–3** (pre-planning verification): read loop state → extract findings
  → staleness gate → rubber-duck all findings
- **Phases 4–5** (plan-writing): invoke `superpowers:writing-plans` → hand off to
  `/implement-health-plan`

The two concern clusters are real, but the current skill carries Phase 3
rubber-duck records and Phase 1 `closes_event_ids` maps only in-context.
No intermediate file exists. A split into `verify-findings` (Phases 0–3) and
`write-plan` (Phases 4–5) requires this intermediate artifact contract to be
defined and implemented first.

## Proposed Intermediate Artifact

### Location

`.dev/health-verify-worklist.json` — written by `verify-findings` at Phase 3
completion, consumed by `write-plan` at startup.

### Schema

```json
{
  "generated_at": "ISO-8601 timestamp",
  "source_dossiers": ["docs/health/<date>-<surface>-health.md"],
  "health_filters": {
    "surfaces": ["tooling"],
    "dimensions": ["design"]
  },
  "findings": [
    {
      "event_id": "disp_20260620_000094",
      "surface": "tooling",
      "dimension": "design",
      "object": "design-skill-lens-near-duplicates",
      "finding": "Remodel: ...",
      "subject_path": ".claude/agents/design-skill-lens-near-duplicates.md",
      "rubber_duck_verdict": "proceed",
      "rubber_duck_evidence": "model: haiku confirmed; body requires multi-file synthesis",
      "rubber_duck_modified_scope": null
    }
  ],
  "skipped": [
    {
      "event_id": "disp_20260620_000093",
      "reason": "skip [refuted]: SKIP_COMMIT=true flag already covers dry-run use case"
    }
  ]
}
```

`rubber_duck_modified_scope` is `null` for `proceed` verdicts and a string
describing the adjusted scope for `modify` verdicts. This intermediate artifact
field is consumed by `write-plan` Phase 0 when adjusting task scope.

### Invariants

1. All `findings` entries have `rubber_duck_verdict` of `proceed` or `modify`.
   `skip` verdicts go to `skipped`.
2. Every `findings[].event_id` must appear in `docs/health/dispositions-open.md`
   at the time `verify-findings` writes the file.
3. `write-plan` reads `.dev/health-verify-worklist.json` in Phase 0 and fails
   fast if the file is absent or its `generated_at` is more than 24 hours old
   (guard against stale worklists).

## Proposed Skill Split

### verify-findings skill (Phases 0–3)

- **Input:** Dossier path(s) or `--backlog` flag; `--surface`, `--dimension`, etc.
- **Phases:** Read loop state → extract findings → staleness gate → rubber-duck all
  findings (parallel agent dispatch)
- **Output:** `.dev/health-verify-worklist.json` (schema above) + a human-readable
  summary printed to console
- **Writes loop state:** `next_command: /write-plan` with `next_inputs:
  .dev/health-verify-worklist.json`

### write-plan skill (Phases 4–5)

- **Input:** `.dev/health-verify-worklist.json` (reads it in Phase 0)
- **Phases:** Invoke `superpowers:writing-plans` with the worklist as context →
  verify `closes_event_ids:` coverage → hand off to `/implement-health-plan`
- **Output:** `docs/superpowers/plans/<date>-plugin-map-<label>.md`
- **Writes loop state:** `next_command: /implement-health-plan`

## closes_event_ids Handoff Chain

Currently `plan-health-findings` Phase 1 extracts `event_id` values from
`dispositions-open.md` and carries them in-context to Phase 4, where
`writing-plans` embeds them in plan task verification blocks.

After the split, the chain becomes:

1. `verify-findings` Phase 1 extracts `event_id` → stores in `findings[].event_id`
   in `.dev/health-verify-worklist.json`
2. `write-plan` Phase 0 reads the worklist and reconstructs the event-ID map
3. `write-plan` passes event IDs to `writing-plans` the same way `plan-health-findings`
   Phase 4 does today

No change to how `implement-health-plan` or the ledger consume `closes_event_ids`.

## Files and Callers Needing Updates After Split Implementation

| File | Change needed |
|------|---------------|
| `.claude/skills/plan-health-findings/SKILL.md` | Split into two new skills; archive this file |
| `.claude/knowledge/health-loop-state-contract.md` | Add `next_command: /verify-findings` and `/write-plan` as valid stage values |
| `.claude/knowledge/health-plan-context-template.md` | Update caller reference from `plan-health-findings Phase 4` to `write-plan` |
| `.claude/skills/implement-health-plan/SKILL.md` | Update reference from `plan-health-findings` to `write-plan` in Phase 0 breadcrumb |
| `.claude/skills/revise-health-plan/SKILL.md` | Update cross-reference to `plan-health-findings` phase structure |
| `docs/maintainer-tooling.md` (generated) | Regenerate after new skill workflow: contracts are added |
| `docs/al-dev-skills-map.md` | No change expected (distributed surface only) |

## Why Deferred

The split cannot be implemented before this contract is reviewed because:

1. **No intermediate artifact format exists.** The JSON schema above is proposed but not
   yet validated against a real rubber-duck run.
2. **Stale-worklist guard threshold is not yet settled** (24 hours is a first
   guess; sessions can span restarts).
3. **Two new skills need naming** (`verify-findings` / `write-plan` are working
   names only — check against docs/al-dev-naming-convention.md before creating files).
4. **Workflow contract** pages (docs/maintainer-tooling/) must be updated
   atomically with the skill creation.

## Next Steps

1. Review this spec. Adjust the JSON schema and invariants if needed.
2. Create a new plan: `plan-health-findings` split implementation using this contract.
3. That plan closes `disp_20260620_000092` (carried here via this prerequisite task).
