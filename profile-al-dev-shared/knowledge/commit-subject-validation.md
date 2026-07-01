# Commit Subject Validation

## Overview

Commit subjects (the first line of a commit message) must not exceed 72 characters per `commit-conventions.md`. When generating commit messages in plan tasks, validation must occur before finalizing the message.

## Validation Rule

For each generated commit message:

1. Extract the subject line (everything before the first blank line or `\n\n`)
2. Count characters (not bytes)
3. If the count exceeds 72 characters:
   - **Option A:** Reject and ask the user to shorten the message
   - **Option B:** Truncate at 70 characters and append "…" to signal truncation

## Bash Validation Pattern

```bash
subject="<generated-subject>"
if [ $(printf '%s' "$subject" | wc -m) -gt 72 ]; then
  echo "⚠️  Subject exceeds 72 characters: $subject"
  exit 1
fi
```

## Integration Points

This validation should be applied by any skill that generates commit messages:

- `superpowers:writing-plans` — when outputting implementation plan commit subjects
- `solution-architect` — when including commit subjects in design proposals
- Plan-generation skills — when drafting task commits

## Friction Context

Observed in sessions: 20 of 20 generated commit subjects exceeded 72 characters when this validation was absent. This pattern was logged as friction and flagged for all plan-generation workflows.

See `solution-plan-template.md` for example commit subject structure in plan tasks.
