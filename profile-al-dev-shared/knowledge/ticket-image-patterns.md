# Ticket Image Detection Patterns

Reference patterns for ticket-context-writer image attachment detection.

## Detection Patterns

| Pattern | Matches | Example |
|---------|---------|---------|
| `src="https?://` | External image URL | `src="https://cdn.freshdesk.com/img.jpg"` |
| `src="cid:` | Inline CID reference | `src="cid:attachment_123abc"` |
| `src="data:image/` | Base64 data URI | `src="data:image/png;base64,..."` |

## Handling Rules

- **External URLs** (`https://`): download and attach if accessible.
- **CID references** (`cid:`): note as inline attachment by reference.
- **Base64 data URIs** (`data:image/`): note as "inline base64 image (not downloaded)".
  Do not attempt to download or decode base64 content.

## Integration Notes

This file documents the extraction patterns used in Step 1.5 of the ticket agent fetch phase. The inline image detection step scans HTML from ticket descriptions and conversations for `<img src="..."` tags matching these patterns and compiles a distinct list of inline images separate from the file attachments array in the API response.
