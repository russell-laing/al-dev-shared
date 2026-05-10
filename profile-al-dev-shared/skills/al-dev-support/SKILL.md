---
name: al-dev-support
description: Research BC support queries and draft customer replies.
argument-hint: "[ticket# | question | file path]"
---

# Skill: /al-dev-support

Thin orchestrator. Resolves the support query source, assembles
a prompt envelope, and dispatches `al-dev-support-agent` to
research and draft the customer reply.

## Usage

```text
/al-dev-support 1234           — Freshdesk ticket #1234
/al-dev-support FD-1234        — same, FD prefix form
/al-dev-support "Users can't post invoices after upgrade"
                               — free-text query
/al-dev-support ./notes/error.txt
                               — read file as query body
/al-dev-support                — auto-detect from branch
```

---

## Step 1 — Resolve Input

Check the argument after `/al-dev-support`:

| Pattern | Treatment |
| --- | --- |
| Numeric or `FD-NNNN` | Freshdesk ticket — go to Step 2 |
| Path (`/`, `./`, `~/`, or known extension) | File — go to Step 3 (file) |
| No argument | Check branch — go to Step 1A |
| Any other text | Free-text query — go to Step 3 (freetext) |

### Step 1A — Branch Auto-Detect

```bash
git branch --show-current
```

If the branch matches `FD(\d+)` (case-insensitive), extract the
number and confirm:
_"Found FD ticket #XXXX from branch — loading."_
Proceed to Step 2 with that ticket ID.

If no match, ask: _"What is the support query? (Enter a ticket
number, paste the customer question, or provide a file path.)"_

---

## Step 2 — Verify Freshdesk Credentials (ticket path only)

```bash
echo "API_KEY=${FRESHDESK_API_KEY:+set}" && \
echo "DOMAIN=${FRESHDESK_DOMAIN:+set}"
```

If either shows blank (not `set`), stop and tell the user:

```text
Missing Freshdesk credentials.

Add to your harness settings file (never committed):

  "env": {
    "FRESHDESK_API_KEY": "your-api-key",
    "FRESHDESK_DOMAIN": "yoursubdomain.freshdesk.com"
  }

Restart your AI coding agent session after saving.
```

If credentials are present, dispatch `al-dev-ticket-agent`:

```text
Agent tool:
  agent: al-dev-shared:al-dev-ticket-agent
  description: "Fetch Freshdesk ticket #[TICKET_ID]"

Prompt:
  "Fetch Freshdesk ticket and write
  .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md.

   Phase: fetch
   Ticket ID: [TICKET_ID]

   FRESHDESK_API_KEY and FRESHDESK_DOMAIN are set in the
   environment — use them directly in curl commands.

   Return your output in exactly this format:
   TICKET_LOADED: #<id>
   TITLE: <subject>
   STATUS: <label> | PRIORITY: <label>
   SUMMARY: <2-3 sentence plain English summary>
   ATTACHMENTS: <count> | <name (size, type)> | ... (NONE)
   FILE: .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md"
```

If the agent returns `ERROR: bad_credentials`, repeat the
credential error message above and stop.

If the agent returns `ERROR: ticket_not_found`, tell the user:
_"Ticket #[ID] not found."_ and stop.

After a successful load, set:

- `QUERY_TYPE: ticket`
- `QUERY_CONTEXT: <SUMMARY from agent output>`
- `TICKET_FILE: <FILE from agent output>`

Proceed to Step 4.

---

## Step 3 — Prepare Free-Text or File Context

**File input:** Read the file:

```bash
cat "[FILE_PATH]"
```

If the command fails (file not found), tell the user:
_"File not found: [FILE_PATH]"_ and stop.

Set `QUERY_CONTEXT` to the file content.
Set `QUERY_TYPE: file`. Set `TICKET_FILE: NONE`.

**Free-text input:**
Set `QUERY_CONTEXT` to the argument text.
Set `QUERY_TYPE: freetext`. Set `TICKET_FILE: NONE`.

---

## Step 4 — Dispatch al-dev-support-agent

Assemble the prompt envelope:

```text
QUERY_TYPE: [ticket | file | freetext]
QUERY_CONTEXT: <customer question, ticket summary, or file content>
TICKET_FILE: <.dev path if loaded, else NONE>
```

Dispatch:

```text
Agent tool:
  agent: al-dev-shared:al-dev-support-agent
  description: "BC support research: <60-char query summary>"

Prompt: <assembled prompt envelope above>
```

---

## Step 5 — Present Result

Parse the agent's returned summary:

```text
FILE: .dev/YYYY-MM-DD-support-<slug>.md
QUERY_TYPE: <class>
BC_VERSION_SCOPE: <scope or "not version-specific">
SOURCES: MS Docs (<n> pages) | BC History (<n> commits or NONE)
         | AL Symbols (<n> objects)
SUMMARY: <1-2 sentence plain English summary of findings>
```

Present to user:

```text
Support research complete →
<FILE value>

<SUMMARY value>
<QUERY_TYPE> | <BC_VERSION_SCOPE>

Findings and draft reply written. Review and copy-paste
the Draft Customer Reply section into Freshdesk.
```
