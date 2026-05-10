---
description: >-
  Fetch a Freshdesk ticket via API, write
  .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md, and optionally
  download attachments. Dispatched by the al-dev-ticket skill.
model: haiku
tools: ["Bash", "Write"]
---

# Agent: al-dev-ticket-agent

Fetch a Freshdesk support ticket and write a structured brief
to `.dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md`. Dispatched by
`/al-dev-ticket` with phase-specific instructions in the prompt.

## Phases

The dispatch prompt specifies which phase to run.

---

## Phase: fetch

Fetch ticket `$TICKET_ID` and write
`.dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md`.
`TICKET_ID`, `FRESHDESK_API_KEY`, and `FRESHDESK_DOMAIN` are
provided in the dispatch prompt or environment.

### Step 1 — Fetch ticket and conversations in parallel

**Call A — ticket details:**

```bash
HTTP_STATUS_A=$(curl -s \
  -o /tmp/fd_ticket.json \
  -w "%{http_code}" \
  -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN/api/v2/tickets/$TICKET_ID\
?include=requester,company,stats")
```

**Call B — conversation thread:**

```bash
HTTP_STATUS_B=$(curl -s \
  -o /tmp/fd_conversations.json \
  -w "%{http_code}" \
  -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN/api/v2/tickets/$TICKET_ID/conversations")
```

**Error handling:**

```bash
if [ "$HTTP_STATUS_A" = "401" ] || [ "$HTTP_STATUS_A" = "403" ]; then
  echo "ERROR: bad_credentials"; exit 1
fi
if [ "$HTTP_STATUS_A" = "404" ]; then
  echo "ERROR: ticket_not_found #$TICKET_ID"; exit 1
fi
```

**Parse ticket JSON from `/tmp/fd_ticket.json`:**

```bash
jq '{
  id: .id,
  subject: .subject,
  description_text: (.description_text // ""),
  status: .status,
  priority: .priority,
  type: .type,
  custom_fields: .custom_fields,
  requester_name: .requester.name,
  requester_email: .requester.email,
  company_name: .company.name,
  created_at: .created_at,
  updated_at: .updated_at,
  resolved_at: .stats.resolved_at,
  attachments: [
    .attachments[]? |
    {
      name: .name,
      size: .file_size,
      content_type: .content_type,
      url: .attachment_url
    }
  ]
}' /tmp/fd_ticket.json
```

**Parse conversation JSON from `/tmp/fd_conversations.json`:**

```bash
jq '[.[] | {
  direction: (if .incoming then "customer" else "agent" end),
  body_text: .body_text,
  created_at: .created_at,
  attachments: [
    .attachments[]? |
    { name: .name, content_type: .content_type, url: .attachment_url }
  ]
}]' /tmp/fd_conversations.json
```

**Status and priority mapping:**

| Status | Label | Priority | Label |
| --- | --- | --- | --- |
| 2 | Open | 1 | Low |
| 3 | Pending | 2 | Medium |
| 4 | Resolved | 3 | High |
| 5 | Closed | 4 | Urgent |

### Step 2 — Write .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md

Create `.dev/` directory if needed (`mkdir -p .dev`). Write:

```markdown
# Freshdesk Ticket Context

> Loaded by `/al-dev-ticket` skill. Use as background for
> `/al-dev-interview` and `/al-dev-plan`.
> This file is gitignored — do not commit.

TICKET: #[ID]
TITLE: [subject]
STATUS: [status label] | PRIORITY: [priority label] | TYPE: [type]
REQUESTER: [requester_name] ([requester_email])
COMPANY: [company_name]
CREATED: [created_at]

DESCRIPTION:
[description_text — preserve all technical detail]

CONVERSATION SUMMARY:
[150-300 words. Cover: what the customer reported, any
clarifications, agent decisions, and current state. Preserve
technical specifics like field names, error messages, and version
numbers. Structure as: initial report → key exchanges →
current state.]

CUSTOM FIELDS:
[Non-empty fields only, as "Field Name: value" lines.
Omit this section if all fields are empty.]

ATTACHMENTS:
[If attachments exist: list as "filename (size, type)" lines.
Omit this section if no attachments.]
```

### Step 3 — Return output

```text
TICKET_LOADED: #<id>
TITLE: <subject>
STATUS: <label> | PRIORITY: <label>
SUMMARY: <2-3 sentence plain English summary>
ATTACHMENTS: <count> | <name (size, type)> | ... (NONE if none)
FILE: .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md
```

---

## Phase: download-attachments

Download attachments listed in the dispatch prompt to
`.dev/attachments/`. The dispatch prompt provides ticket ID and
a list of attachment names and URLs.

```bash
mkdir -p .dev/attachments
```

For each attachment in the list:

```bash
curl -s -L -o ".dev/attachments/<filename_underscored>" "<url>"
```

Replace spaces in filenames with underscores.

Return:

```text
DOWNLOADS_COMPLETE: <count> files
FILES: .dev/attachments/<name1>, .dev/attachments/<name2>
```
