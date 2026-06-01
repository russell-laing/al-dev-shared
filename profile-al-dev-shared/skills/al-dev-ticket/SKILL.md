---
name: al-dev-ticket
description: >-
  Fetch and contextualise a Freshdesk ticket, optionally research
  and draft a support reply. Use --mode=context-only to load ticket
  context only (default behavior), or --mode=full to include
  research and reply drafting.
argument-hint: "[ticket-id or search-term] [--mode=context-only|full]"
---

# Freshdesk Ticket Context Loader

Thin orchestrator. Resolves the ticket number, verifies
credentials, then dispatches `al-dev-ticket-agent` to do the
API work and file writing. Can optionally extend to research
and reply drafting via `--mode=full`.

## Usage

```text
/al-dev-ticket 1234           — load ticket #1234
/al-dev-ticket                — auto-detect from branch name or prompt
/al-dev-ticket search terms   — search tickets by subject/description
```markdown

## Branch Naming Convention

Include `FD<number>` in your branch name for auto-detection:

```text
feature/#CU86d0dnfx2-FD1234-description
```text

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
```text

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

## Step 1 — Resolve the Ticket Number or Search Intent

Check the arguments provided (text after `/al-dev-ticket`):

- **Numeric argument** (e.g. `1234` or `FD-1234`): extract the
  number and proceed to Step 2.
- **`search <terms>` or non-numeric text**: this is a keyword
  search — skip to **Step 1.5 — Search Tickets** (the section immediately following this one).
- **No argument**: run `git branch --show-current`, extract from
  pattern `FD([0-9]+)`. If found, confirm:
  _"Found FD ticket #XXXX from branch — loading."_
  If not found, ask: _"What is the Freshdesk ticket number (or
  enter keywords to search)?"_

---

## Step 1.5 — Search Tickets (Keyword Search)

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
```yaml

Extract and display up to 10 results:

```text
SEARCH RESULTS: "[query]"

#[ID] | [status label] | [subject]
#[ID] | [status label] | [subject]
...
```text

Ask the user which ticket to load. If they choose one, proceed
from Step 2 with that ticket ID. Otherwise exit — do not
dispatch the agent.

---

## Step 2 — Verify Environment Variables

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
```text

---

## Step 3 — Dispatch al-dev-ticket-agent (fetch phase)

```text
DATE=$(date +%Y-%m-%d)

Agent tool:
  agent: al-dev-shared:al-dev-ticket-agent
  description: "Fetch Freshdesk ticket #[TICKET_ID]"

Prompt:
  "Fetch Freshdesk ticket and write
  .dev/$DATE-al-dev-ticket-ticket-context.md.

   Phase: fetch
   Ticket ID: [TICKET_ID]

   Environment: Credentials have been verified in Step 2.
   Use FRESHDESK_API_KEY and FRESHDESK_DOMAIN directly in
   curl commands.

   Return your output in exactly this format:
   TICKET_LOADED: #<id>
   TITLE: <subject>
   STATUS: <label> | PRIORITY: <label>
   SUMMARY: <2-3 sentence plain English summary>
   ATTACHMENTS: <count> | <name (size, type)> | ... (NONE if none)
   FILE: .dev/$DATE-al-dev-ticket-ticket-context.md"
```yaml

**See:** `../../knowledge/ticket-agent-invocation-pattern.md` for canonical dispatch pattern.

---

## Step 4 — Present Result and Handle Attachments

Parse the agent output. If it starts with `ERROR:`:

- `bad_credentials`: repeat the Step 2 credential error message.
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
```yaml

If `ATTACHMENTS` is not `NONE`, ask:

```text
ATTACHMENTS ([count]):
  [list from agent output]

Download to .dev/attachments/? [y/n]
```yaml

**Download decision logic:**

**If yes (user opts to download):**
Dispatch `al-dev-ticket-agent` again (download phase):

```text
Agent tool:
  agent: al-dev-shared:al-dev-ticket-agent
  description: "Download attachments for Freshdesk #[TICKET_ID]"

Prompt:
  "Download attachments for Freshdesk ticket #[TICKET_ID].

   Phase: download-attachments
   Ticket ID: [TICKET_ID]
   Attachments:
   [paste the attachment list lines from Step 3 output]

   Environment: Credentials verified in Step 2. Use
   FRESHDESK_API_KEY and FRESHDESK_DOMAIN directly in curl.

   Return:
   DOWNLOADS_COMPLETE: <count> files
   FILES: <comma-separated list>"
```yaml

Append to the user summary:

```text
Attachments saved to .dev/attachments/ ([count] files).
```yaml

**If no (user declines to download):**
- Proceed directly to Phase 5 without downloading attachments
- Append note to user summary:
  ```text
  Attachments not downloaded. References available in ticket context file:
  .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md
  
  Note: Steps 5-7 (research and reply drafting) may have incomplete context
  if critical information was only in attachments. You can return here later
  with /al-dev-ticket <id> --download to retrieve them.
  ```
- If MODE is `context-only`: Exit after this note
- If MODE is `full`: Continue to Phase 6 with available context only

---

## Phase 5: Branch on Mode

**Note:** This phase controls execution flow. If mode is context-only, the skill 
exits here. Otherwise, it continues to Phases 6 and 7 below.

If MODE is `context-only`:
- Skip Phases 6 and 7
- Output ticket context only
- Exit

If MODE is `full`:
- Continue to Phase 6 (research)

---

## Phase 6: Dispatch al-dev-support-researcher (research phase)

Assemble the research prompt using the ticket context loaded in Step 3:

```text
QUERY_TYPE: ticket
QUERY_CONTEXT: <SUMMARY from agent output in Step 3>
TICKET_FILE: <FILE from agent output in Step 3>
```yaml

Dispatch:

```text
Agent tool:
  agent: al-dev-shared:al-dev-support-researcher
  description: "BC support research: <60-char query summary>"

Prompt: <assembled prompt above>
```text

---

## Phase 7: Dispatch al-dev-support-reply-drafter (reply phase)

Assemble the reply prompt using the researcher's output:

```text
QUERY_TYPE: ticket
QUERY_CONTEXT: <SUMMARY from ticket loaded in Step 3>
TICKET_FILE: <FILE from ticket loaded in Step 3>
RESEARCHER_FINDINGS: <full structured output block from al-dev-support-researcher>
```yaml

Dispatch:

```text
Agent tool:
  agent: al-dev-shared:al-dev-support-reply-drafter
  model: claude-sonnet-4-6
  description: "Draft customer reply: <60-char query summary>"

Prompt: <assembled prompt above>
```text

---

## Phase 8: Present Result

Parse the agent's returned summary:

```text
FILE: .dev/YYYY-MM-DD-support-<slug>.md
QUERY_TYPE: <class>
BC_VERSION_SCOPE: <scope or "not version-specific">
SOURCES: MS Docs (<n> pages) | BC History (<n> commits or NONE)
         | AL Symbols (<n> objects)
SUMMARY: <1-2 sentence plain English summary of findings>
```yaml

Present to user:

```text
Support research complete →
<FILE value>

<SUMMARY value>
<QUERY_TYPE> | <BC_VERSION_SCOPE>

Findings and draft reply written. Review and copy-paste
the Draft Customer Reply section into Freshdesk.
```text
