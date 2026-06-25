---
name: al-dev-ticket
description: >-
  Fetch and contextualise a Freshdesk ticket, optionally research
  and draft a support reply. Use --mode=context-only to load ticket
  context only (default behavior), or --mode=full to include
  research and reply drafting; Phase 5 branches on the selected mode.
argument-hint: "[ticket-id or search-term] [--mode=context-only|full]"
---

# Freshdesk Ticket Context Loader

Thin orchestrator. Resolves the ticket number, verifies
credentials, then dispatches `al-dev-ticket-context-writer` to do the
API work and file writing. Can optionally extend to research
and reply drafting via `--mode=full`.

## Artifact Contract

This skill is governed by `knowledge/artifact-contracts.md`.

Do not claim the work is complete or ready for handoff until the success evidence named in `knowledge/artifact-contracts.md` for this skill has been produced and read in the current run.

## Usage

```text
/al-dev-ticket 1234           — load ticket #1234
/al-dev-ticket                — auto-detect from branch name or prompt
/al-dev-ticket search terms   — search tickets by subject/description
```

## Branch Naming Convention

Include `FD<number>` in your branch name for auto-detection:

```text
feature/#CU86d0dnfx2-FD1234-description
```

---

## Phase 0.5: Resolve Mode

Parse the `--mode` argument:

- `--mode=context-only` (default) → Run Steps 1–4 only (fetch and contextualize ticket)
- `--mode=full` → Run all steps including research + reply drafting

If `--mode=` is not specified, default to `context-only`.

Extract the mode flag from $ARGUMENTS using:

```bash
MODE="context-only"
if [[ "$ARGUMENTS" =~ --mode=([^ ]+) ]]; then
  MODE="${BASH_REMATCH[1]}"
  # Remove flag from ARGUMENTS (handles any position, not just with leading space)
  ARGUMENTS="${ARGUMENTS//--mode=[^ ]*/}"
fi

# Validate mode value
if [[ ! "$MODE" =~ ^(context-only|full)$ ]]; then
  echo "ERROR: Invalid mode '$MODE'. Allowed: context-only, full"
  exit 1
fi
```

The validation is case-sensitive: only `context-only` and `full` (lowercase) are accepted. Passing `--mode=Full` or `--mode=FULL` will fail validation and emit the error message.

**Test cases — trailing-argument boundary:**

| Input `$ARGUMENTS` | Expected `$MODE` |
|---|---|
| `--mode=full` | `full` (last and only token) |
| `1234 --mode=full` | `full` (last arg; `[^ ]+` captures to end-of-string) |
| `--mode=full --other-flag` | `full` (`[^ ]+` captures until next space) |
| (empty) | `context-only` (default) |

The `[^ ]+` capture group matches one or more non-space characters, so `--mode=full` at the end of `$ARGUMENTS` is captured correctly without a trailing space.

---

## Phase 0 — Load Interview Requirements (Optional)

If a prior interview was conducted, load structured requirements to inform the reply context:

1. **Check for interview requirements:**

   ```bash
   ls .dev/*-al-dev-interview-requirements.md 2>/dev/null | sort | tail -1
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

Check the arguments provided (text after `/al-dev-ticket`):

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

## Phase 3 — Dispatch al-dev-ticket-context-writer (fetch phase)

```text
DATE=$(date +%Y-%m-%d)

Agent tool:
  agent: al-dev-shared:al-dev-ticket-context-writer
  description: "Fetch Freshdesk ticket #[TICKET_ID]"

Prompt:
  "Fetch Freshdesk ticket and write
  .dev/$DATE-al-dev-ticket-ticket-context.md.

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
   FILE: .dev/$DATE-al-dev-ticket-ticket-context.md"
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
.dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md

[TITLE]
[STATUS] | [PRIORITY]

[SUMMARY]

Context is ready — run /al-dev-interview or /al-dev-plan to continue.
```

If `ATTACHMENTS` is not `NONE`, ask:

```text
ATTACHMENTS ([count]):
  [list from agent output]

Download to .dev/attachments/? [y/n]
```

**Download decision logic:**

**If yes (user opts to download):**
Dispatch `al-dev-ticket-context-writer` again (download phase):

```text
Agent tool:
  agent: al-dev-shared:al-dev-ticket-context-writer
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
  .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md
  
  Note: /al-dev-support-reply (research and reply drafting) may have
  incomplete context if critical information was only in attachments.
  You can return here later with /al-dev-ticket <id> --download to
  retrieve them.
  ```

- Proceed to Phase 5, which branches on `MODE`.

---

## Phase 5: Mode Branching

Branch on `MODE` as parsed in Phase 0.5:

```text
mode ∈ {context-only, full}

if mode == "context-only":
  └─ Ticket context already written by Phase 3 to
     .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md
  └─ Exit workflow (no further phases)

if mode == "full":
  └─ Dispatch /al-dev-support-reply with the ticket context file
  └─ Read the returned REPLY block
  └─ Write the REPLY block to .dev/$(date +%Y-%m-%d)-al-dev-ticket-reply.md
  └─ Output REPLY to caller
```
