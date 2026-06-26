# Commit Intent Preflight

Before dispatching commit agents, staging files, unstaging files, or committing, verify the intent matches the user's request.

## Default Intent

The default intent for commit-related skills is `COMMIT`.

## Mismatch Detection

If the request is review-only, edit-only, assessment-only, or asks for a commit plan without committing, **stop immediately** and apply the intent-mismatch prompt:

> "I'm about to [describe the action]. Did you want me to [action], or were you asking for something else?"

Examples of mismatches:

- "review these staged changes" → user wants analysis, not a commit
- "draft messages for my commits" → user wants a plan, not execution
- "what changes will this commit?" → user wants assessment, not staging/dispatch

## Recovery

If the user clarifies intent:

- **Intent mismatch confirmed** (e.g., "no, just review") — stop and do not proceed with commit dispatch
- **Intent confirmed** (e.g., "yes, go ahead") — proceed with the original skill

If the user wants to re-intent the request (e.g., "actually, do commit after review"), close the current skill and have them re-invoke with a commit-explicit request.
