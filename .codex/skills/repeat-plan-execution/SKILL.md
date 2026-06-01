---
name: repeat-plan-execution
description: Use when executing an al-dev-shared implementation plan from docs/superpowers/plans, or when the user asks to repeat the regular isolated plan-to-merge routine.
---

# Repeat Plan Execution

Use this for recurring `al-dev-shared` implementation-plan runs where the goal is a clean branch, task-sized commits, validation, merge, and worktree cleanup.

## Trigger

Use when the user points at a plan file such as:

```text
docs/superpowers/plans/YYYY-MM-DD-topic.md
```

Also use when the user says to repeat "this process", "the regular process", "the worktree process", or similar after a successful plan execution.

## Workflow

1. Read the plan once and extract the task list.
2. Verify repo state:
   - `git status --short`
   - `git branch --show-current`
   - note unrelated dirty files and do not stage or revert them.
3. Create or use an isolated worktree:
   - prefer `.worktrees/<topic-branch>`
   - verify `.worktrees/` is ignored before creating it.
4. Run baseline checks that match the repo and plan.
5. Execute tasks sequentially:
   - change only the task-owned files
   - run the task's specified checks
   - commit the task before moving on
   - review for spec compliance, then code quality
   - if subagents are unavailable, do the same checks locally and say so.
6. Before final completion, run the full validation block from the plan.
7. Merge only after validation passes and the user chooses merge.
8. After merge, validate again from `master`, then remove the owned worktree and delete the merged branch.

## Validation Defaults

For `al-dev-shared`, start with:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
python3 -m unittest scripts.tests.test_validate_harness_neutrality scripts.tests.test_validate_knowledge_quality -v
git status --short
```

Add plan-specific tests and validators. If a baseline command fails before implementation, capture the exact failure and re-check it at the end.

## Merge Guard

Before merging into `master`:

1. Check dirty files in the main checkout.
2. Compare them with the branch diff.
3. If paths overlap or the merge would overwrite user work, stop and report the blocker.
4. Prefer fast-forward merge when the branch split cleanly:

```bash
git merge --ff-only <topic-branch>
```

## Common Mistakes

- Starting on `master` when a worktree is practical.
- Letting task commits stage unrelated dirty files.
- Treating generated plans/specs as current guidance after a durable summary exists.
- Skipping post-merge validation.
- Removing a worktree before the merge succeeds.
