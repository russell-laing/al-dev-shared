# Commit Hook Recovery Patterns

Reference for `al-dev-commit-hook-fixer`. Classification of pre-commit hook
failures and the approved scripted fixes per class.

## Failure Classification

| Failure class | Examples | `action` | Recovery |
|---------------|----------|----------|----------|
| **Fixable** | AL lint (`AA0xxx`), markdownlint, trailing whitespace, Python `ruff` | `retry` | Apply a scripted Bash fix, re-stage, signal retry |
| **Non-fixable** | Harness-neutrality / policy violations, forbidden tokens, projection-stale, secrets detected | `manual-review` | Report root cause; user must resolve |
| **Transient** | Network timeout, lock contention, temporary tool unavailability | `retry` | No code change needed; signal retry |

## Approved Fixes

- Trailing whitespace: `sed -E -i '' 's/[[:blank:]]+$//' <file>`
- Python lint: `ruff check --fix <file>`
- Markdown: `markdownlint --fix <file>` (or the project's configured fixer)
