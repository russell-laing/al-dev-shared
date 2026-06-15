---
name: verify-commits
description: Verify recent commits match planned commit groups; split only when approved groups were combined into one local commit
---

# Verify Commits

## Quick Check

Verify that recent commits match the plan's approved commit groups. Treat
"combined" as two or more approved commit groups collapsed into a single local
git commit.

## Steps

1. Read the approved plan or commit-group artifact and count the expected
   commit groups. If no artifact names the approved groups, stop and report
   that verification cannot proceed from memory or commit count alone.
2. Set `<N>` to the number of approved commit groups unless the user supplied
   an explicit override such as `-N 10`.
3. Run `git log --oneline -n <N>` to inspect the recent local commits.
4. Compare the recent commits against the approved groups. Check both:
   - commit count
   - whether each approved group still has its own commit subject and file set
5. If approved groups were combined into one local commit, stop and confirm the
   rewrite is safe before suggesting any reset:
   - only local, unpublished commits are in scope (unpublished = not yet pushed to a remote; check with `git log origin/<branch>..<branch>` if a remote is configured)
   - the affected commits are the recent commits just inspected
   - the user wants history rewritten
   If the user does not confirm (declines the rewrite), stop. Inform them:
   "Leaving the combined commit as-is. To split manually later:
   `git reset --soft HEAD~<N>` then re-commit each approved group separately."
6. If that safety check passes, use `git reset --soft HEAD~<N>` to unstage and
   re-commit each approved group as a separate atomic commit.
7. Re-run `git log --oneline -n <N>` and confirm the final commits match the
   approved groups by count and subject, not count alone.

## Example

Plan specifies 3 commits: "add feature", "update docs", "fix tests"
Actual log shows 2 commits: "add feature + update docs", "fix tests"

Fix: Reset last 2 commits, re-apply atomically:

- `git reset --soft HEAD~2`
- Commit "add feature"
- Commit "update docs"
- Commit "fix tests"
- Verify: `git log --oneline -n 3`
