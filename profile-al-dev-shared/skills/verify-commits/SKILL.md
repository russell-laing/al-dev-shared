---
name: verify-commits
description: Verify recent commits match planned commit groups; auto-split if combined
argument-hint: "[optional: -N 10]"
---

# Verify Commits

## Quick Check

Verify that recent commits match the plan's approved commit groups. If groups were mistakenly combined, split them.

## Steps

1. Count expected commits from the plan
2. Run `git log --oneline -n <N>` to inspect recent commits
3. Compare against plan — if any approved commit group is missing:
   - Use `git reset --soft HEAD~<N>` to unstage
   - Re-commit each group as a separate atomic commit
4. Verify final commit count matches plan with `git log --oneline -n <N>`

## Example

Plan specifies 3 commits: "add feature", "update docs", "fix tests"
Actual log shows 2 commits: "add feature + update docs", "fix tests"

Fix: Reset last 2 commits, re-apply atomically:
- `git reset --soft HEAD~2`
- Commit "add feature"
- Commit "update docs"  
- Commit "fix tests"
- Verify: `git log --oneline -n 3`
