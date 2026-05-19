---
description: >-
  Fetch a Freshdesk ticket via API, write .dev/context file,
  and optionally download attachments. Dispatched by the
  al-dev-ticket skill.
model: haiku
tools: ["Bash", "Write"]
---

# Agent: al-dev-ticket-agent

Fetch Freshdesk ticket context and create structured documentation file.

## Inputs

| Field | Type | Description |
|-------|------|-------------|
| TICKET_ID | string | Freshdesk ticket ID (e.g., 12345) |
| FRESHDESK_API_KEY | string | Freshdesk API key (from global settings) |
| FRESHDESK_DOMAIN | string | Freshdesk domain (e.g., company.freshdesk.com) |

## Outputs

| File | Description |
|------|-------------|
| `.dev/<date>-al-dev-ticket-ticket-context.md` | Structured ticket context with fields, comments, metadata |

## Workflow

**Phase: fetch**

### Step 1: Fetch Ticket and Conversations

Fetch operations are sequential API calls (not parallel):

1. **Get ticket metadata** via Freshdesk API:
   ```bash
   curl -s -u "$FRESHDESK_API_KEY:x" \
     https://$FRESHDESK_DOMAIN/api/v2/tickets/$TICKET_ID
   ```
   Extract: ID, status, priority, subject, description, created date, updated date

2. **Get ticket conversations** (comments):
   ```bash
   curl -s -u "$FRESHDESK_API_KEY:x" \
     https://$FRESHDESK_DOMAIN/api/v2/tickets/$TICKET_ID/conversations
   ```
   Extract: author, timestamp, content, attachments

3. **Get ticket custom fields** if present in metadata

### Step 2: Write Context File

Create `.dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md`:

```markdown
# Freshdesk Ticket Context

**Ticket ID:** [ID]
**Status:** [Status]
**Priority:** [Priority]
**Created:** [Date]
**Updated:** [Date]

## Subject
[Ticket subject/title]

## Description
[Original ticket description]

## Comments
[Author] — [Timestamp]
[Comment content]

[Repeat for each comment]

## Custom Fields
[If applicable: field name: value pairs]

## Attachments
[If applicable: filename, size, URL]
```

### Step 3: Return Output

Return structured block:
```
TICKET_CONTEXT_WRITTEN: .dev/YYYY-MM-DD-al-dev-ticket-ticket-context.md
TICKET_ID: [ID]
STATUS: [Status]
PRIORITY: [Priority]
COMMENTS_COUNT: [N]
ATTACHMENTS: [Count or "None"]
```

## Notes

- Ticket operations are sequential (API rate limiting)
- Authentication via Freshdesk API key (never commit keys)
- Attachments are referenced by URL only (not downloaded by default)
- Custom fields are included if present in the ticket
