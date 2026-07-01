---
name: ticket
description: >-
  Fetch and contextualise a Freshdesk ticket, optionally research
  and draft a support reply. Use without flag to load ticket context only
  (default), or --research-reply to include research and reply drafting.
argument-hint: "[ticket#|--research-reply|search-term|none]"
---

# Freshdesk Ticket Context Loader

Thin orchestrator. Resolves the ticket number, verifies
credentials, then dispatches `ticket-context-writer` to do the
API work and file writing. Can optionally extend to research
and reply drafting via `--mode=full`.

## Artifact Contract

This skill is governed by `knowledge/artifact-contracts.md`.

Do not claim the work is complete or ready for handoff until the success evidence named in `knowledge/artifact-contracts.md` for this skill has been produced and read in the current run.

## Usage

```text
/ticket 1234           — load ticket #1234
/ticket                — auto-detect from branch name or prompt
/ticket search terms   — search tickets by subject/description
```

## Branch Naming Convention

Include `FD<number>` in your branch name for auto-detection:

```text
feature/#CU86d0dnfx2-FD1234-description
```

---

## Phase 0.5: Mode Gate (research-reply delegation)

Determine ticket mode:

- **Research mode:** If ticket requires supportive research (customer documentation,
  troubleshooting guide, FAQ), delegate to `/support-reply` skill

- **Support-reply flow:** If ticket is support-request or documentation-pull,
  invoke `/support-reply` and stop here

- **Context-loading mode:** If ticket is internal task or development request,
  continue to Phases 1-4 (context gathering + response)

**Decision criterion:** Does this ticket need external research (docs, community knowledge)?
If YES → delegate to `/support-reply`. If NO → continue with context-loading.

---

## Phase 0 — Load Interview Requirements (Optional)

If a prior interview was conducted, load structured requirements to inform the reply context:

1. **Check for interview requirements:**

   ```bash
   ls .dev/*-interview-requirements.md 2>/dev/null | sort | tail -1
   ```

2. **If found, read the requirements:**

   Load the requirements document and note:
   - Structured requirements (REQ blocks)
   - Risk assessments
   - Scope boundaries

   Present to user: "Structured requirements available from prior interview. Reference these when composing your reply."

3. **If not found, continue:** Proceed with ticket context alone.

This is optional; missing interview requirements do not block reply composition.

---

## Phase 1 — Resolve the Ticket Number or Search Intent

Check the arguments provided (text after `/ticket`):

**Precedence rule (mixed input):** when the input contains both a ticket
ID and other text (e.g. `1234 posting error`), the first token decides —
if the first token matches `^(FD-?)?[0-9]+$`, treat the input as a ticket
ID and ignore the remaining text; otherwise treat the entire input as
search terms.

- **Numeric argument** (e.g. `1234` or `FD-1234`): extract the
  number and proceed to Phase 2.
- **`search <terms>` or non-numeric text**: this is a keyword
  search — skip to **Phase 1.5 — Search Tickets** (the section immediately following this one).
- **No argument**: run `git branch --show-current`, extract from
  pattern `FD([0-9]+)`. If found, confirm:
  _"Found FD ticket #XXXX from branch — loading."_
  If not found, ask: _"What is the Freshdesk ticket number (or
  enter keywords to search)?"_

---

## Phase 1.5 — Search Tickets (Keyword Search)

URL-encode the search terms and query the search endpoint:

```bash
SEARCH_TERMS="[USER_TERMS]"
ENCODED=$(python3 -c \
  "import urllib.parse,sys; \
   q='(subject:\\'%s\\' OR description:\\'%s\\')' % (sys.argv[1],sys.argv[1]); \
   print(urllib.parse.quote(q))" \
  "$SEARCH_TERMS")
curl -s -f -u "$FRESHDESK_API_KEY:X" \
  "https://$FRESHDESK_DOMAIN/api/v2/search/tickets?query=\"$ENCODED\""
```

Example: `subject:'posting error'` → `subject%3A%27posting%20error%27` after encoding.

Extract and display up to 10 results:

```text
SEARCH RESULTS: "[query]"

#[ID] | [status label] | [subject]
#[ID] | [status label] | [subject]
...
```

Ask the user which ticket to load. If they choose one, proceed
from Phase 2 with that ticket ID. Otherwise exit — do not
dispatch the agent.

---

## Phase 2 — Verify Environment Variables

```bash
echo "API_KEY=${FRESHDESK_API_KEY:+set}" && \
echo "DOMAIN=${FRESHDESK_DOMAIN:+set}"
```

If either shows blank (not `set`), stop and tell the user:

```text
Missing Freshdesk credentials.

Add to your harness settings file (global user settings, never committed):

  "env": {
    "FRESHDESK_API_KEY": "your-api-key",
    "FRESHDESK_DOMAIN": "yoursubdomain.freshdesk.com"
  }

Restart your AI coding agent session after saving.
See your harness profile's Freshdesk setup guide for details.
```

---

## Phase 3 — Dispatch ticket-context-writer (fetch phase)

```text
DATE=$(date +%Y-%m-%d)

Agent tool:
  agent: al-dev-shared:ticket-context-writer
  description: "Fetch Freshdesk ticket #[TICKET_ID]"

Prompt:
  "Fetch Freshdesk ticket and write
  .dev/$DATE-ticket-ticket-context.md.

   Phase: fetch
   Ticket ID: [TICKET_ID]

   Environment: Credentials have been verified in Phase 2.
   Use FRESHDESK_API_KEY and FRESHDESK_DOMAIN directly in
   curl commands.

   Return your output in exactly this format:
   TICKET_LOADED: #<id>
   TITLE: <subject>
   STATUS: <label> | PRIORITY: <label>
   SUMMARY: <2-3 sentence plain English summary>
   ATTACHMENTS: <count> | <name (size, type)> | ... (NONE if none)
   FILE: .dev/$DATE-ticket-ticket-context.md"
```

**See:** `../../knowledge/ticket-agent-invocation-pattern.md` for canonical dispatch pattern.

---

## Phase 4 — Present Result and Handle Attachments

Parse the agent output. If it starts with `ERROR:`:

- `bad_credentials`: repeat the Phase 2 credential error message.
- `ticket_not_found`: tell the user _"Ticket #[ID] not found."_
  and stop.

Otherwise present to user:

```text
Freshdesk #[ID] loaded →
.dev/$(date +%Y-%m-%d)-ticket-ticket-context.md

[TITLE]
[STATUS] | [PRIORITY]

[SUMMARY]

Context is ready — run /interview or /plan to continue.
```

If `ATTACHMENTS` is not `NONE`, ask:

```text
ATTACHMENTS ([count]):
  [list from agent output]

Download to .dev/attachments/? [y/n]
```

**Download decision logic:**

**If yes (user opts to download):**
Dispatch `ticket-context-writer` again (download phase):

```text
Agent tool:
  agent: al-dev-shared:ticket-context-writer
  description: "Download attachments for Freshdesk #[TICKET_ID]"

Prompt:
  "Download attachments for Freshdesk ticket #[TICKET_ID].

   Phase: download-attachments
   Ticket ID: [TICKET_ID]
   Attachments:
   [paste the attachment list lines from Phase 3 output]

   Environment: Credentials verified in Phase 2. Use
   FRESHDESK_API_KEY and FRESHDESK_DOMAIN directly in curl.

   Return:
   DOWNLOADS_COMPLETE: <count> files
   FILES: <comma-separated list>"
```

Append to the user summary:

```text
Attachments saved to .dev/attachments/ ([count] files).
```

**If no (user declines to download):**

- Proceed directly to Phase 5 without downloading attachments
- Append note to user summary:

  ```text
  Attachments not downloaded. References available in ticket context file:
  .dev/$(date +%Y-%m-%d)-ticket-ticket-context.md
  
  Note: /support-reply (research and reply drafting) may have
  incomplete context if critical information was only in attachments.
  You can return here later with /ticket <id> --download to
  retrieve them.
  ```

- Proceed to Phase 5, which branches on `MODE`.

---

## Phase 5: Deliver result

Present the context or research-reply output to the user based on the mode selected in Phase 0.5. If research-reply was delegated, `/support-reply` has already completed that flow.
