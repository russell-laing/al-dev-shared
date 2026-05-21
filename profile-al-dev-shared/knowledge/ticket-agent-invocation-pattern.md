# Ticket Agent Invocation Pattern

Canonical pattern for dispatching `al-dev-ticket-agent` from skills that interact with Freshdesk.

## Pattern Summary

Both `/al-dev-ticket` and `/al-dev-support` dispatch `al-dev-ticket-agent` with identical environment variables and phase parameters. This document captures the canonical pattern to prevent drift.

## Dispatch Block Template

```bash
Agent tool:
  agent: al-dev-shared:al-dev-ticket-agent
  description: "Fetch Freshdesk ticket #[TICKET_ID]"

Prompt: |
  Fetch Freshdesk ticket and write
  .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md.

  Phase: fetch
  Ticket ID: [TICKET_ID]

  FRESHDESK_API_KEY and FRESHDESK_DOMAIN are set in the
  environment — use them directly in curl commands.
```

## Environment Variables

The following environment variables **must be set** by the harness before dispatching the agent:

| Variable | Description | Source |
|----------|-------------|--------|
| `FRESHDESK_API_KEY` | Freshdesk API authentication key | User's global settings (harness settings file) |
| `FRESHDESK_DOMAIN` | Freshdesk subdomain (e.g., `company.freshdesk.com`) | User's global settings |

These are resolved from the harness environment, not passed in the dispatch prompt.

## Phases

### Phase: fetch

Fetch Freshdesk ticket metadata, conversations, and attachments. Output structured ticket context.

**Agent behavior:**
1. Use `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` from environment
2. Make sequential API calls (not parallel) to avoid rate-limiting
3. Extract inline images from conversation HTML (regex scan for `src=` attributes)
4. Write structured `.dev/` output file with metadata, conversations, and attachments
5. Return structured block with file path and summary

**Output file:** `.dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md`

**Return block format:**

```text
TICKET_LOADED
FILE: .dev/YYYY-MM-DD-al-dev-ticket-ticket-context.md
TITLE: [ticket title]
STATUS: [ticket status]
SUMMARY: [one-line summary]
ATTACHMENTS: [count]
```

## Using This Pattern

When a new skill needs to fetch Freshdesk tickets, it should:

1. Reference this file in the skill documentation
2. Copy the dispatch block template above
3. Substitute `[TICKET_ID]` with the user's ticket ID
4. Ensure `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` are available in the environment
5. Parse the return block to extract the output file path

## Related Files

- Agent definition: `profile-al-dev-shared/agents/al-dev-ticket-agent.md`
- Skills using this pattern:
  - `/al-dev-ticket` — Fetch ticket context (Phase 3)
  - `/al-dev-support` → redirects to `/al-dev-ticket --mode=full` (Phase 2)
