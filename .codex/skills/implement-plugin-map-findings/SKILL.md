---
name: implement-plugin-map-findings
description: Use when implementing a corrected plugin-map or tooling-surface findings plan in al-dev-shared, especially when tasks mix repo-local `.claude/` maintainer tooling with `profile-al-dev-shared/` shared surfaces and may contain conditional or overlapping edits.
---

# Implement Plugin Map Findings

Execute plugin-map and tooling-surface implementation plans only after the live
health-loop, ledger, and generated-artifact contracts prove the plan is still
the right execution target.

## When to Use

Use this when the user asks to implement a corrected plugin-map, plugin-health,
or tooling-surface findings plan in `al-dev-shared`.

Do not use this for review-only commentary. Use
`write-superpowers-plan-commentary` for plan review, and use
`revise-plugin-plan` when commentary or review findings must be reconciled into
an existing health-loop plan before implementation.

Use `repeat-plan-execution` for generic isolated-plan work that does not close
health disposition events. This skill adds the plugin-map and health-loop traps
that generic execution misses.

## Phase 0: Live Routing Gate

Before editing anything, read the current loop and storage contracts:

- `.dev/health-loop-state.md`
- `.claude/knowledge/health-loop-state-contract.md`
- `.claude/knowledge/health-disposition-storage-contract.md`
- `.claude/knowledge/ledger-closure-protocol.md`
- `.claude/skills/implement-plugin-health/SKILL.md`

Route from live state, not from memory or an old plan:

| Live state | Action |
| --- | --- |
| `next_command: /plan-plugin-findings` | Stop implementation. Plan accepted rows first. |
| `next_command: /revise-plugin-plan` or review commentary exists for the target plan | Reconcile the plan and ledger before implementation. |
| `next_command: /implement-plugin-health --plan <path>` | Use that plan path unless the user explicitly overrides it. |
| `next_command: none` or no breadcrumb | Fresh entry. Require an explicit plan path or locate a current, non-archived plan with `closes_event_ids:`. |
| Pointer names a different skill | Tell the user what the pointer expects and ask before overriding it. |

If the user says "the codebase has changed since this was last used," treat
that as a hard stale-plan signal: re-check the breadcrumb, the target plan, the
open accepted events, and all validators before implementation.

## Workflow

1. Read the full plan and collapse conditional or superseded tasks before editing.
   Task overlap is common here. If one task says "only if Task N is deferred" or another task replaces the same block, treat that as one implementation path, not two.
2. Verify the plan is execution-ready:
   - it is not under `docs/superpowers/plans/archived/`
   - it contains `closes_event_ids:` for every ledger-closing task
   - those IDs still appear as open accepted events in `docs/health/dispositions-open.md`
   - skipped, declined, or grandfathered items are handled by ledger events, not by pretending a source edit fixed them.
3. Start in a project-local `.worktrees/<topic>` worktree only after checking the current branch, unrelated dirty files, and whether `.worktrees/` is ignored.
   If the plan file is absent inside the worktree, copy the full plan text into scope before relying on path-based reads.
4. Verify the live target files and validators behind each finding before editing.
   For this plan family, check real field names, timeout argument names, checkpoint status vocabulary, workflow script return shape, and whether warnings are advisory or state-changing.
5. Execute task-owned edits sequentially.
   For health-loop plans, follow the current `/implement-plugin-health` model: inline, one task at a time, commit before the next task, and use `.dev/implement-plugin-health-progress.md` as the checkpoint. Only dispatch subagents when the plan explicitly requires independent work that is worth the coordination overhead.
6. Respect authored/generated boundaries.
   Edit `profile-al-dev-shared/skills`, `agents`, `knowledge`, or generator scripts. Do not hand-edit `profile-al-dev-shared/generated/`, generated map sections, or generated disposition views; regenerate them from the supported command.
7. Treat validator-driven wording or command changes as explicit deviations that need justification.
   If a repo validator requires wording that differs slightly from the plan text, keep the change minimal, note why it was necessary, and make the reviewer confirm it is acceptable.
8. Close ledger events through the JSONL store only.
   Append `fixed`, `declined`, or `grandfathered` events with fresh IDs and `closes_event_ids` through `scripts/health_disposition_store.py append_event`, then run `regenerate`; use `sync_shard` only when the plan or current workflow explicitly requires Markdown history shard sync. Never append rows directly to `docs/health/dispositions.md`.
9. Re-run the repo validators on the worktree, then verify whether generator warnings produce actual diffs before expanding scope.
   For advisory doc-map freshness warnings, run the generator and inspect `git status --short`. If there is no diff, do not widen the task just to silence the warning.
10. Merge back only after a clean worktree verification pass and user approval, then validate again from the target branch.
   If git metadata writes fail with `Operation not permitted` or `index.lock`, retry the same narrow git operation with the needed permission instead of changing the workflow.

## Mandatory Checks

Start with:

```bash
git status --short --branch
python3 scripts/validate_health_loop_state.py
python3 scripts/check_ledger_staleness.py
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge
python3 scripts/validate_artifact_contracts.py
python3 scripts/validate_maintainer_contracts.py
```

Add path-sensitive checks:

```bash
python3 scripts/generate-map-doc-sections.py
python3 scripts/generate-maintainer-guide.py
python3 scripts/generate-agent-projections.py
python3 scripts/tests/test_generate_agent_projections.py
python3 scripts/tests/test_generate_plugin_graph.py
python3 -m unittest scripts.tests.test_health_disposition_jsonl_store scripts.tests.test_validate_health_loop_state -v
git diff --check <base-sha>..HEAD
```

## Friction Traps

| Trap | What to Do |
| --- | --- |
| Conditional task overlap | Collapse the tasks up front so you do not edit the same block twice. |
| Loop pointer expects planning | Stop and run the pointed next command; do not execute an old plan. |
| Plan file missing in worktree | Provide full plan text to agents or bring the file into scope before using worktree-local reads. |
| Plan has commentary or review-only findings | Use `revise-plugin-plan`; do not silently apply every finding as a source edit. |
| Reviewer catches live-script drift | Trust the live file over the plan, patch the task, and re-run the same review gate. |
| Generated artifact target | Redirect to authored source or generator, then regenerate. |
| Ledger close-back skipped | Block completion until the JSONL event store has deterministic `closes_event_ids` closure. |
| Subagent thread limit | Prefer inline sequential execution; close completed agents before starting any required worker. |
| Git metadata permission failures | Retry the exact `git` operation with the needed permission; do not broaden the command. |
| Advisory generator warning | Run the generator and inspect for real diffs before changing extra files. |
| Dirty main checkout during merge | Compare intended branch paths against `git status --short` in the main checkout before merge-back. |

## Common Mistakes

- Treating Task 1 and Task 4 style overlaps as independent edits.
- Assuming a Workflow script returns fields like `failed_lenses` without reading the actual script.
- Letting doc or validator warnings pull generated or unrelated files into the commit.
- Trusting the worktree to contain untracked plan artifacts from the main checkout.
- Running implementation when `.dev/health-loop-state.md` still points to `/plan-plugin-findings`.
- Closing accepted findings by editing generated disposition views instead of appending JSONL events.
- Finishing task reviews but forgetting to retire any required agents, then hitting the thread ceiling later.
