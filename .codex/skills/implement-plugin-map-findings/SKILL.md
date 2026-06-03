---
name: implement-plugin-map-findings
description: Use when implementing a corrected plugin-map or tooling-surface findings plan in al-dev-shared, especially when tasks mix repo-local `.claude/` maintainer tooling with `profile-al-dev-shared/` shared surfaces and may contain conditional or overlapping edits.
---

# Implement Plugin Map Findings

Execute corrected plugin-map and tooling-surface findings plans with the session traps already handled.

## When to Use

Use this after the plan has already been pressure-tested against live repo state.

Do not use this for plan review only. Use `findings-plan-rubber-duck` first when the plan still needs correction.

Use `repeat-plan-execution` for the generic isolated-plan workflow. This skill adds the plugin-map-specific traps that generic execution misses.

## Workflow

1. Read the full plan and collapse conditional or superseded tasks before editing.
   Task overlap is common here. If one task says "only if Task N is deferred" or another task replaces the same block, treat that as one implementation path, not two.
2. Start in a project-local `.worktrees/<topic>` worktree and note unrelated dirty files in the main checkout.
   If the plan file is absent inside the worktree, pass its full text to implementer/reviewer agents or copy it into scope before relying on path-based reads.
3. Verify the live target files and validators behind each finding before editing.
   For this plan family, check real field names, timeout argument names, checkpoint status vocabulary, workflow script return shape, and whether warnings are advisory or state-changing.
4. Execute task-owned edits sequentially with task-sized commits and review gates.
   Run spec compliance review before code-quality review. If a reviewer finds a real mismatch, fix the task and re-run the same review instead of papering over it.
5. Treat validator-driven wording or command changes as explicit deviations that need justification.
   If a repo validator requires wording that differs slightly from the plan text, keep the change minimal, note why it was necessary, and make the reviewer confirm it is acceptable.
6. Keep subagent orchestration tidy.
   Close completed agents before spawning more if you are near the thread limit. Do not let old review agents linger until they block later tasks.
7. Re-run the repo validators on the worktree, then verify whether generator warnings produce actual diffs before expanding scope.
   For advisory doc-map freshness warnings, run the generator and inspect `git status --short`. If there is no diff, do not widen the task just to silence the warning.
8. Merge back only after a clean worktree verification pass, then validate again from `master`.
   If git metadata writes fail with `Operation not permitted` or `index.lock`, retry the same narrow git operation with the needed permission instead of changing the workflow.

## Mandatory Checks

Start with:

```bash
git status --short --branch
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
```

Add as needed for this findings-plan family:

```bash
python3 scripts/generate-map-doc-sections.py
python3 scripts/tests/test_generate_agent_projections.py
python3 scripts/tests/test_generate_plugin_graph.py
git diff --check <base-sha>..HEAD
```

## Friction Traps

| Trap | What to Do |
|---|---|
| Conditional task overlap | Collapse the tasks up front so you do not edit the same block twice. |
| Plan file missing in worktree | Provide full plan text to agents or bring the file into scope before using worktree-local reads. |
| Reviewer catches live-script drift | Trust the live file over the plan, patch the task, and re-run the same review gate. |
| Subagent thread limit | Close completed agents before starting the next review or implementation worker. |
| Git metadata permission failures | Retry the exact `git` operation with the needed permission; do not broaden the command. |
| Advisory generator warning | Run the generator and inspect for real diffs before changing extra files. |
| Dirty main checkout during merge | Compare intended branch paths against `git status --short` in the main checkout before merge-back. |

## Common Mistakes

- Treating Task 1 and Task 4 style overlaps as independent edits.
- Assuming a Workflow script returns fields like `failed_lenses` without reading the actual script.
- Letting doc or validator warnings pull generated or unrelated files into the commit.
- Trusting the worktree to contain untracked plan artifacts from the main checkout.
- Finishing task reviews but forgetting to retire the agents, then hitting the thread ceiling later.
