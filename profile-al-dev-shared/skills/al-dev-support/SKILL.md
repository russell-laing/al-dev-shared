---
name: al-dev-support
description: >-
  DEPRECATED ALIAS: Use /al-dev-ticket --mode=full instead.
  
  Fetch a Freshdesk ticket, research a BC support query, and draft
  a customer-facing reply. This is now a mode of /al-dev-ticket.
argument-hint: "[ticket-id or search-term] --mode=full"
---

# Support Reply Skill (Deprecated)

This skill has been consolidated with `/al-dev-ticket` for clarity.
Use `/al-dev-ticket --mode=full` instead.

The consolidated skill provides:
- `--mode=context-only` (default) — fetch ticket context only
- `--mode=full` — fetch + research + reply draft

Example:

```bash
/al-dev-ticket 12345 --mode=full
```

This is equivalent to the former `/al-dev-support 12345`.

**Note:** When using `--mode=full`, the skill internally dispatches `al-dev-ticket-agent` using the pattern documented in `../../knowledge/ticket-agent-invocation-pattern.md`.
