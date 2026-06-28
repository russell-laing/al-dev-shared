# Ticket Context Output Format

The context file follows this structure:

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
```

**File path:** `.dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md`
