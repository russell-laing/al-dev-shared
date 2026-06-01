---
description: "Fetch a Freshdesk ticket via API, write .dev/context file, and optionally download attachments. Dispatched by the al-dev-ticket skill."
tools: ["Bash", "Write"]
---


# Agent: al-dev-ticket-agent

Fetch Freshdesk ticket context and create structured documentation file.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `TICKET_ID` | **Yes** | Freshdesk ticket ID (passed in dispatch prompt, e.g., 12345) |
| `FRESHDESK_API_KEY` | **Yes** | API key; available as shell environment variable in agent bash context (configured in harness environment settings per `knowledge/ticket-agent-invocation-pattern.md`) |
| `FRESHDESK_DOMAIN` | **Yes** | Freshdesk subdomain; available as shell environment variable in agent bash context (configured in harness environment settings per `knowledge/ticket-agent-invocation-pattern.md`) |

**Note:** `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` are configured in the harness environment settings and injected as shell variables at agent dispatch — not passed in the dispatch prompt.

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

### Step 1.5: Detect Inline Image Attachments

After extracting conversation HTML from the API response, scan for inline embedded images:

1. **Regex scan for `src=` attributes:** Extract all image URLs from `<img src="..."` tags in description and conversation HTML
2. **Regex scan for `cid:` references:** Extract content-ID references (Freshdesk inline attachment pattern) from `src="cid:..."` tags
3. **Compile inline-image list:** Create a distinct list of inline images found — these are separate from the file attachments array in the API response

Example patterns to match:
```text
src="https://cdn.freshdesk.com/...jpg"     → extract URL
src="cid:attachment_123abc"                 → extract cid:attachment_123abc
<img src="data:image/png;base64,..."      → note as "inline base64 image"
```text

If inline images are found, include them in the return block as `INLINE_IMAGES_COUNT: [N]`.

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

**File Attachments:** (from API attachments array)
[If applicable: filename, size, URL]

**Inline Embeds:** (extracted from HTML src= and cid: references)
[If applicable: image URL or cid:reference, extracted from description and comments]
```text

### Step 3: Return Output

Return structured block:
```text
TICKET_CONTEXT_WRITTEN: .dev/YYYY-MM-DD-al-dev-ticket-ticket-context.md
TICKET_ID: [ID]
STATUS: [Status]
PRIORITY: [Priority]
COMMENTS_COUNT: [N]
ATTACHMENTS: [Count or "None"]
INLINE_IMAGES_COUNT: [N or "None"]
```text

## Download Phase (Conditional)

If the dispatcher asks to download attachments (separate invocation with `Phase: download-attachments`):

1. **Parse attachment list** from the dispatch prompt
2. **Create target directory:** `.dev/attachments/` if it does not exist
3. **Download each file:**
   ```bash
   curl -s -u "$FRESHDESK_API_KEY:x" \
     -o ".dev/attachments/[filename]" \
     "[attachment_url_from_api]"
   ```
4. **Return summary:**
   ```text
   DOWNLOADS_COMPLETE: [N] files
   FILES: [comma-separated list of downloaded filenames]
   ```

**Decision logic for attachment downloads:**
- If dispatcher asks to download → fetch all attachments and write to disk
- If dispatcher declines or does not ask → do NOT download; rely on URL references in context file
- Missing or inaccessible attachments → record in output with count and reason (e.g., "expired URL", "access denied")

## Notes

- Ticket operations are sequential (API rate limiting)
- Authentication via Freshdesk API key (never commit keys)
- Attachments are referenced by URL only in context file (not downloaded by default)
- Downloads are triggered by separate dispatcher call, not automatic
- Custom fields are included if present in the ticket
