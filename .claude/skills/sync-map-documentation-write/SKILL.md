---
name: sync-map-documentation-write
description: >-
  Regenerate derived diagrams and projections from canonical source files,
  then commit all generated artifacts. Final step after map updates (apply skill)
  completes; regenerates and commits the generated product, not the maps.
workflow:
  stage: map-sync
  invoked-by: user
  repeatable: false
  inputs:
    - .dev/sync-map-documentation-checkpoint.json
    - docs/skills-map.md
    - docs/agent-map.md
  outputs:
    - docs/workflow-diagrams.md
    - docs/plugin-graph.md
    - docs/maintainer-tooling.md
    - docs/maintainer-tooling/
    - profile-al-dev-shared/generated/agents/
  next: [audit-plugin-health]
---

# Sync Map Documentation — Write (Regenerate and Commit)

Final regeneration step after `/sync-map-documentation-apply`; fourth step of
the async sync flow. Regenerates Mermaid diagrams, harness-native agent
projections, the plugin dependency graph, and the maintainer guide pages from the
updated maps, then commits all changes.

**Four-skill workflow:**

1. `/sync-map-documentation` — dispatch audit teams (~5 min, then exit)
2. `/sync-map-documentation-collect --team-ids <ids>` — collect results, spawn updates
3. `/sync-map-documentation-apply --team-ids <ids>` — validate artifacts, write maps
4. `/sync-map-documentation-write` — regenerate diagrams, projections, and commit (this skill)

**Working directory assumption:** All relative paths are resolved from
`/Users/russelllaing/al-dev-shared`. Use absolute paths in Bash commands.

---

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md` — emit a phase-proof block at each phase boundary before reporting completion or updating `.dev/health-loop-state.md`.

## Phase 0 — Verify Maps Are Written

Read `.dev/sync-map-documentation-checkpoint.json`. Confirm `status` **is**
`"awaiting-write"` (the state `/sync-map-documentation-apply` leaves on success).
If it is anything else, the maps are not yet written — stop and instruct the user
to run `/sync-map-documentation-apply` first.

```bash
cat /Users/russelllaing/al-dev-shared/.dev/sync-map-documentation-checkpoint.json
```

Extract `run_id` → `RUN_ID`, `result_dir` → `RUN_DIR`, and `skip_commit` →
`SKIP_COMMIT`.

If `status` is not `"awaiting-write"`, stop with:

```text
Maps not yet written. Run /sync-map-documentation-apply first to validate
artifacts and write the maps to docs/, then re-run this step.
```

Confirm the docs/ maps exist and are non-empty:

```bash
ls -la /Users/russelllaing/al-dev-shared/docs/skills-map.md
ls -la /Users/russelllaing/al-dev-shared/docs/agent-map.md
```

---

## Phase 1 — Regenerate Diagrams, Agent Projections, Dependency Graph, and Maintainer Guide

When documentation maps are updated, agent definitions and relationships may have changed.
Regenerate Mermaid diagrams, harness-native projections, and the plugin dependency graph to
keep all derived artifacts in sync.

First, regenerate all Mermaid diagrams (Layer 1 lifecycle, Layer 2 drilldowns, agent catalog):

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate_map_doc_sections.py
```

Capture the exit code. If non-zero, report:

```text
Mermaid diagram regeneration failed (exit <code>).
```

**Count-consistency gate:** Before committing, run the three-way count check in
`.claude/knowledge/map-count-consistency-gate.md` (active files on disk vs generated
Coverage count vs generated catalog rows). On mismatch, stop here (do not commit)
and read the bounded-recovery steps in that doc before retrying.

Once the count check passes, run the three remaining regenerations in sequence. Each follows the same pattern — execute the
script and capture its exit code; on a non-zero code, report the labelled error
(substituting the actual exit code), record the non-zero result, and continue to the next regeneration script — do not skip the remaining generators:

| Artifact | Script | Error label on non-zero exit |
| --- | --- | --- |
| Agent projections | `generate_agent_projections.py` | `Agent projection regeneration failed (exit <code>).` |
| Dependency graph | `generate_plugin_graph.py` | `Dependency graph refresh failed (exit <code>).` |
| Maintainer guide | `generate_maintainer_guide.py` | `Maintainer guide regeneration failed (exit <code>).` |

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate_agent_projections.py
python3 /Users/russelllaing/al-dev-shared/scripts/generate_plugin_graph.py
python3 /Users/russelllaing/al-dev-shared/scripts/generate_maintainer_guide.py
```

Run them one at a time so the failure label can be matched to the failing script.
If all FOUR operations (the Mermaid step above plus these three) succeed, continue
to Phase 2.

If any fail, report:

```text
One or more artifact updates failed. Maps have been written; derived artifacts
may be stale. Check the errors above and re-run /sync-map-documentation
to regenerate missing artifacts.
```

After all regeneration scripts have run, report the accumulated failures (if any) using the block above, then continue to Phase 2 regardless of exit code. **Failure behavior:** regeneration failures do not block Phase 2 (summary) or Phase 3 (commit). Map changes are committed even when derived artifacts are stale. Each failed artifact is labeled in the Phase 2 summary template as "regeneration failed — see above".

---

## Phase 2 — Present Summary

Print a summary of all work completed:

```text
Sync finalized.

  Run ID: RUN_ID

  Updated files:
    docs/skills-map.md       — <N> lines  (or "skipped")
    docs/agent-map.md        — <N> lines  (or "skipped")

  Derived artifacts:
    Mermaid diagrams: regenerated   (or "regeneration failed — see above")
    Agent projections: regenerated  (or "regeneration failed — see above")
    Dependency graph: refreshed     (or "refresh failed — see above")
    Maintainer guide: regenerated   (or "regeneration failed — see above")

  Next: run /audit-plugin-health to find improvements against the updated maps.
```

---

## Phase 3 — Commit

If `SKIP_COMMIT=true`, print a dry-run message and stop:

```text
--skip-commit set. Skipping commit. Files written to docs/ are ready for
manual review and commit.
```

Otherwise, stage and commit:

```bash
git -C /Users/russelllaing/al-dev-shared status
git -C /Users/russelllaing/al-dev-shared add \
    docs/skills-map.md \
    docs/agent-map.md \
    docs/maintainer-tooling.md \
    docs/maintainer-tooling/ \
    docs/workflow-diagrams.md \
    docs/plugin-graph.md
git -C /Users/russelllaing/al-dev-shared add \
    profile-al-dev-shared/generated/ 2>/dev/null || true
git -C /Users/russelllaing/al-dev-shared diff --cached --stat
git -C /Users/russelllaing/al-dev-shared commit \
    -m "docs: sync documentation maps with current codebase"
git -C /Users/russelllaing/al-dev-shared log --oneline -n 1
```

If the commit exits non-zero, report the error and advise the user to inspect
`git status` and commit manually.

---

## Phase 4 — Update Checkpoint

Set `phase` to `"complete"` and `status` to `"done"` in both checkpoint files.
These are two distinct fields, not duplicates: `phase` records the furthest
workflow position reached, while `status` records the run's lifecycle state that
downstream skills (the `/sync-map-documentation` Phase 0 cadence guard,
`-collect`, and `-apply`) read. Do not collapse them into one field.

```bash
# Update .dev/sync-map-documentation-checkpoint.json
# Update ${RUN_DIR}/manifest.json
```

Use the merge pattern in
`.claude/skills/sync-map-documentation/checkpoint-patterns.md`. Update only the
two fields; preserve all pre-existing fields:

```bash
CHECKPOINT_FILE="/Users/russelllaing/al-dev-shared/.dev/sync-map-documentation-checkpoint.json"
jq '.phase = "complete" | .status = "done"' \
    "$CHECKPOINT_FILE" \
    > /tmp/sdm-checkpoint-tmp.json && \
    mv /tmp/sdm-checkpoint-tmp.json "$CHECKPOINT_FILE"

jq '.phase = "complete" | .status = "done"' \
    "${RUN_DIR}/manifest.json" \
    > /tmp/sdm-manifest-tmp.json && \
    mv /tmp/sdm-manifest-tmp.json "${RUN_DIR}/manifest.json"
```

Append a completion record to `.dev/progress.md`:

```text
[<current-date>] sync-map-documentation-write complete — RUN_ID maps written
and committed.
```

(Use the actual current date and RUN_ID value.)

Print a final confirmation:

```text
sync-map-documentation workflow complete. Run ID: RUN_ID
```

## Phase 5 — Preserve the health-loop breadcrumb

Check whether `.dev/health-loop-state.md` exists:

```bash
ls .dev/health-loop-state.md 2>/dev/null
```

Do not overwrite `.dev/health-loop-state.md`. Map sync is a preparation stage,
not a lifecycle stage accepted by `scripts/validate_health_loop_state.py`.

- If the file is absent, finish normally and recommend `/audit-plugin-health`.
- If the file exists, report its current `next_command` and leave it unchanged.
  The maintainer can intentionally restart from `/audit-plugin-health` after the
  map-sync commit, but map sync must not replace an in-flight durable handoff.
