---
name: sync-documentation-maps-write
description: >-
  Second step of two-step sync finalization. Regenerates diagrams, projections,
  and the plugin graph from updated maps, then commits. Run after
  /sync-documentation-maps-apply has written the maps to docs/.
argument-hint: "[RUN_ID from checkpoint]"
workflow:
  stage: map-sync
  invoked-by: user
  repeatable: false
  inputs:
    - .dev/sync-documentation-maps-checkpoint.json
    - docs/al-dev-skills-map.md
    - docs/al-dev-agent-map.md
  outputs:
    - docs/al-dev-workflow-diagrams.md
    - docs/al-dev-plugin-graph.md
    - docs/maintainer-tooling.md
    - profile-al-dev-shared/generated/agents/
  next: [plugin-health-audit]
---

# Sync Documentation Maps — Write (Regenerate and Commit)

Second step of two-step sync finalization. Regenerates Mermaid diagrams,
harness-native agent projections, and the plugin dependency graph from the
updated maps, then commits all changes.

**Four-skill workflow:**

1. `/sync-documentation-maps` — dispatch audit teams (~5 min, then exit)
2. `/sync-documentation-maps-collect --team-ids <ids>` — collect results, spawn updates
3. `/sync-documentation-maps-apply --team-ids <ids>` — validate artifacts, write maps
4. `/sync-documentation-maps-write` — regenerate diagrams, projections, and commit (this skill)

**Working directory assumption:** All relative paths are resolved from
`/Users/russelllaing/al-dev-shared`. Use absolute paths in Bash commands.

---

## Phase 0 — Verify Maps Are Written

Read `.dev/sync-documentation-maps-checkpoint.json`. Confirm `status` **is**
`"awaiting-write"` (the state `/sync-documentation-maps-apply` leaves on success).
If it is anything else, the maps are not yet written — stop and instruct the user
to run `/sync-documentation-maps-apply` first.

```bash
cat /Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json
```

Extract `run_id` → `RUN_ID`, `result_dir` → `RUN_DIR`, and `skip_commit` →
`SKIP_COMMIT`.

If `status` is not `"awaiting-write"`, stop with:

```text
Maps not yet written. Run /sync-documentation-maps-apply first to validate
artifacts and write the maps to docs/, then re-run this step.
```

Confirm the docs/ maps exist and are non-empty:

```bash
ls -la /Users/russelllaing/al-dev-shared/docs/al-dev-skills-map.md
ls -la /Users/russelllaing/al-dev-shared/docs/al-dev-agent-map.md
```

---

## Phase 1 — Regenerate Diagrams, Agent Projections, and Refresh Dependency Graph

When documentation maps are updated, agent definitions and relationships may have changed.
Regenerate Mermaid diagrams, harness-native projections, and the plugin dependency graph to
keep all derived artifacts in sync.

First, regenerate all Mermaid diagrams (Layer 1 lifecycle, Layer 2 drilldowns, agent catalog):

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate-map-doc-sections.py
```

Capture the exit code. If non-zero, report:

```text
Mermaid diagram regeneration failed (exit <code>).
```

After a successful regeneration, run the count-consistency gate. The
generator owns the `Coverage` line and the catalog table; all three numbers
below must agree before anything is committed:

```bash
DISK_AGENTS=$(ls /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/*.md | wc -l | tr -d ' ')
COVERAGE_COUNT=$(grep -o '[0-9][0-9]* active agents' /Users/russelllaing/al-dev-shared/docs/al-dev-agent-map.md | grep -o '[0-9]*')
CATALOG_ROWS=$(awk '/BEGIN GENERATED: agent-catalog-table/,/END GENERATED: agent-catalog-table/' \
  /Users/russelllaing/al-dev-shared/docs/al-dev-agent-map.md | grep -c '^| al-dev')
echo "disk=${DISK_AGENTS} coverage=${COVERAGE_COUNT} catalog=${CATALOG_ROWS}"
```

If the three values differ, **stop before Phase 3 (commit)** and report:

```text
Agent count mismatch after regeneration (disk=X coverage=Y catalog=Z).
The maps would commit stale counts. Investigate before committing.
```

Then regenerate agent projections:

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate-agent-projections.py
```

Capture the exit code. If non-zero, report:

```text
Agent projection regeneration failed (exit <code>).
```

Then refresh the dependency graph:

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/generate-plugin-graph.py
```

Capture the exit code. If non-zero, report:

```text
Dependency graph refresh failed (exit <code>).
```

If all THREE operations succeed, continue to Phase 2.

If any fail, report:

```text
One or more artifact updates failed. Maps have been written; derived artifacts
may be stale. Check the errors above and re-run /sync-documentation-maps
to regenerate missing artifacts.
```

Continue to Phase 2 regardless of exit code.

---

## Phase 2 — Present Summary

Print a summary of all work completed:

```text
Sync finalized.

  Run ID: RUN_ID

  Updated files:
    docs/al-dev-skills-map.md       — <N> lines  (or "skipped")
    docs/al-dev-agent-map.md        — <N> lines  (or "skipped")

  Derived artifacts:
    Mermaid diagrams: regenerated   (or "regeneration failed — see above")
    Agent projections: regenerated  (or "regeneration failed — see above")
    Dependency graph: refreshed     (or "refresh failed — see above")

  Next: run /plugin-health-audit to find improvements against the updated maps.
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
    docs/al-dev-skills-map.md \
    docs/al-dev-agent-map.md
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

Set `phase` to `"complete"` and `status` to `"done"` in both checkpoint files:

```bash
# Update .dev/sync-documentation-maps-checkpoint.json
# Update ${RUN_DIR}/manifest.json
```

Use the merge pattern in
`.claude/skills/sync-documentation-maps/checkpoint-patterns.md`. Update only the
two fields; preserve all pre-existing fields:

```bash
CHECKPOINT_FILE="/Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-checkpoint.json"
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
[<current-date>] sync-documentation-maps-write complete — RUN_ID maps written
and committed.
```

(Use the actual current date and RUN_ID value.)

Print a final confirmation:

```text
sync-documentation-maps workflow complete. Run ID: RUN_ID
```
