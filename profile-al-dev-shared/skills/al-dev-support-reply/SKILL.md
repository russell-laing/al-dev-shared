---
name: al-dev-support-reply
description: >-
  Research and draft customer replies for Freshdesk support tickets. Executes phases 6–8 of
  Freshdesk ticket workflow: multi-source research (AL symbols, MS Docs, BC history),
  synthesis of findings, and customer-facing reply drafting. Input: ticket context
  from al-dev-ticket Phase 5 (CONTEXT block, or auto-detected latest). Output: a REPLY
  metadata block plus the full customer reply written to `.dev/YYYY-MM-DD-al-dev-ticket-reply.md`.
argument-hint: "[context-file-path | blank to auto-detect latest]"
---

# Support Reply Researcher and Drafter

Takes a loaded ticket context, runs multi-source BC research, then
drafts a customer-facing reply. Consumes the CONTEXT block produced
by `al-dev-ticket` Phase 5 and emits a REPLY block written to
`.dev/YYYY-MM-DD-al-dev-ticket-reply.md`.

## Usage

```text
/al-dev-support-reply .dev/2026-06-01-al-dev-ticket-ticket-context.md
/al-dev-support-reply                 — auto-detect latest ticket context
```

This skill is normally chained from `/al-dev-ticket --mode=full`, but
can be invoked standalone for research-only consumption on complex
tickets after context has already been loaded.

---

## Phase 0 — Resolve the CONTEXT Input

Accept the ticket context (CONTEXT block) produced by
`al-dev-ticket` Phase 5.

1. **If a context file path was passed as an argument**, read it
   directly.

2. **If no argument was passed**, auto-detect the latest context file:

   ```bash
   ls .dev/*-al-dev-ticket-ticket-context.md 2>/dev/null | sort | tail -1
   ```

   If none is found, stop and tell the user:

   ```text
   No ticket context found. Run /al-dev-ticket <id> first to load a
   ticket, then re-run /al-dev-support-reply.
   ```

3. From the CONTEXT block / context file, extract:
   - `TICKET_FILE` — path to the ticket context file
   - `SUMMARY` — 2-3 sentence plain English summary
   - The ticket ID (from the filename or block header)

---

## Phase 1 — Dispatch al-dev-support-researcher (research phase)

Assemble the research prompt using the ticket context from Phase 0:

```text
QUERY_TYPE: ticket
QUERY_CONTEXT: <SUMMARY from CONTEXT block>
TICKET_FILE: <TICKET_FILE from CONTEXT block>
```

Dispatch:

```text
Agent tool:
  agent: al-dev-shared:al-dev-support-researcher
  description: "BC support research: <60-char query summary>"

Prompt: <assembled prompt above>
```

---

## Phase 2 — Dispatch al-dev-support-reply-drafter (reply phase)

Assemble the reply prompt using the researcher's output:

```text
QUERY_TYPE: ticket
QUERY_CONTEXT: <SUMMARY from CONTEXT block>
TICKET_FILE: <TICKET_FILE from CONTEXT block>
RESEARCHER_FINDINGS: <full structured output block from al-dev-support-researcher>
```

Dispatch:

```text
Agent tool:
  agent: al-dev-shared:al-dev-support-reply-drafter
  model: claude-sonnet-4-6   # intentional pin: takes precedence over the drafter agent's frontmatter model
  description: "Draft customer reply: <60-char query summary>"

Prompt: <assembled prompt above>
```

---

## Phase 3 — Emit REPLY Block

Parse the drafter agent's returned summary and write the REPLY block
to `.dev/$(date +%Y-%m-%d)-al-dev-ticket-reply.md`:

```text
REPLY
FILE: .dev/YYYY-MM-DD-al-dev-ticket-reply.md
QUERY_TYPE: <class>
BC_VERSION_SCOPE: <scope or "not version-specific">
SOURCES: MS Docs (<n> pages) | BC History (<n> commits or NONE)
         | AL Symbols (<n> objects)
SUMMARY: <1-2 sentence plain English summary of findings>
```

Present to user:

```text
Support research complete →
.dev/YYYY-MM-DD-al-dev-ticket-reply.md

<SUMMARY value>
<QUERY_TYPE> | <BC_VERSION_SCOPE>

Findings and draft reply written. Review and copy-paste
the Draft Customer Reply section into Freshdesk.
```

---

## Phase 4 — Gated Post-Back to the Ticket

Phase 3 leaves the drafted reply in `.dev/$(date +%Y-%m-%d)-al-dev-ticket-reply.md`
with no downstream consumer. Phase 4 closes that loop. Posting a reply publishes
content to the customer, so this phase never auto-posts — it always gates on the
user.

1. **Read the reply artifact** written in Phase 3
   (`.dev/$(date +%Y-%m-%d)-al-dev-ticket-reply.md`) and locate its
   `Draft Customer Reply` section.

2. **USER_GATE — confirm before posting.** Ask the user to confirm posting the
   `Draft Customer Reply` back to the ticket. Do not take any external action
   before an explicit confirmation.

3. **On confirmation**, post the reply:
   - The default path is manual copy-paste of the `Draft Customer Reply` section
     into Freshdesk.
   - If a ticket API is configured, its credentials come from the user's global
     settings — never from project settings (see global development standards).

4. **On a non-success response or user decline**, report the failure or decline,
   do NOT mark the reply as posted, and leave the artifact in place so it can be
   retried.
