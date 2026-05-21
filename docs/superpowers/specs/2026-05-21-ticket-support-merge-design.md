# Design Spec: Merge /al-dev-ticket + /al-dev-support

**Status:** Draft — run /plan-map-changes after approving this design to generate the implementation plan
**Date:** 2026-05-21
**Source:** docs/al-dev-plugin-map.md — Architectural suggestions > Merge

---

## Problem Statement

/al-dev-support is a superset of /al-dev-ticket for the ticket-fetch use case — it already
dispatches al-dev-ticket-agent internally. The plugin map suggests consolidating into one skill.
However, input type (ticket# vs file vs freetext) is orthogonal to action level (context-only vs
research+reply). A unified design must handle both dimensions.

## What Each Skill Does Today

### /al-dev-ticket (steps summarised)

/al-dev-ticket is a thin orchestrator that resolves a Freshdesk ticket number and fetches its context.

**Step 1** resolves input: numeric ticket IDs (e.g., 1234 or FD-1234) proceed directly to fetch; non-numeric text triggers a keyword search path; no argument branches to auto-detect from the git branch name (pattern: FD\d+) with fallback prompt.

**Step 1.5** (unique to /al-dev-ticket) implements keyword search. It URL-encodes search terms and queries the Freshdesk search endpoint with a query targeting subject and description fields. Results (up to 10 tickets) are presented to the user with ID, status, and subject, allowing the user to pick one to load. If the user does not pick a ticket, the skill exits without dispatching the agent.

**Step 2** verifies that FRESHDESK_API_KEY and FRESHDESK_DOMAIN environment variables are set. If either is missing, the skill stops and instructs the user to add credentials to their harness settings file.

**Step 3** dispatches al-dev-ticket-agent with phase: fetch and the resolved ticket ID. The agent fetches the Freshdesk API and writes the ticket context to `.dev/<date>-al-dev-ticket-ticket-context.md`, returning a structured summary (ticket ID, title, status, priority, brief summary, attachment count and names).

**Step 4** presents the ticket to the user and optionally handles attachment downloads. If the agent returns an error (bad_credentials or ticket_not_found), the skill stops with an appropriate error message. If attachments are present, the skill asks the user whether to download them; if yes, al-dev-ticket-agent is dispatched again with phase: download-attachments and the attachment list, writing files to .dev/attachments/.

### /al-dev-support (steps summarised)

/al-dev-support is a thin orchestrator that resolves a support query source (ticket, file, or freetext), assembles a prompt envelope, and dispatches al-dev-support-researcher and al-dev-support-reply-drafter to research findings and draft a customer reply.

**Step 1** resolves input type by pattern matching: numeric IDs or FD-NNNN format trigger the Freshdesk ticket path; file-like patterns (start with /, ./, ~/ or known file extensions) trigger the file-read path; no argument triggers branch auto-detect; any other text is treated as a free-text query.

**Step 1.5** (branch auto-detect) runs `git branch --show-current` and extracts a Freshdesk ticket number matching FD(\d+). If found, the user is confirmed; if not found, the skill prompts the user to enter a ticket number, customer question, or file path.

**Step 2** (ticket path only) verifies Freshdesk credentials (FRESHDESK_API_KEY and FRESHDESK_DOMAIN); if missing, it stops with the credential setup message. If credentials are present, it dispatches al-dev-ticket-agent with phase: fetch to load the ticket context file, capturing the SUMMARY for downstream use. Errors (bad_credentials or ticket_not_found) cause the skill to stop. On success, QUERY_TYPE is set to "ticket", QUERY_CONTEXT is set to the ticket summary, and TICKET_FILE is set to the .dev path.

**Step 3** (file and freetext paths) reads the file or uses the argument text as-is. For files, a missing file causes the skill to stop with an error message. For both paths, QUERY_CONTEXT is set to the file content or argument text, QUERY_TYPE is set to "file" or "freetext", and TICKET_FILE is set to NONE.

**Step 4** (research phase) dispatches al-dev-support-researcher with an assembled prompt envelope containing QUERY_TYPE, QUERY_CONTEXT, and TICKET_FILE.

**Step 4b** (reply phase) dispatches al-dev-support-reply-drafter with the original query context, QUERY_TYPE, TICKET_FILE, and the full structured RESEARCHER_FINDINGS output.

**Step 5** presents the result to the user by parsing the drafter's summary (FILE, QUERY_TYPE, BC_VERSION_SCOPE, SOURCES, SUMMARY) and confirms that findings and draft reply are written for the user to review and copy into Freshdesk.

## Key Observation: Two Orthogonal Dimensions

1. **Input type** (what you provide): ticket#, keyword search, file path, free text, or nothing (branch auto-detect)
2. **Action level** (what you want): context-only (load ticket) vs full research + reply

The mode flag controls action level. Input type is determined by argument shape.

## Proposed Unified Interface

```
/al-dev-support [input]           # full research + reply (default)
/al-dev-support [input] --fetch   # context-only (ticket fetch)
```

Where `[input]` follows the same routing as today:
| Input pattern | Treatment |
|---------------|-----------|
| Numeric / FD-NNNN | Freshdesk ticket |
| `search <terms>` | Keyword search → user picks ticket |
| File path | Read file as query body |
| No argument | Branch auto-detect → ticket or prompt |
| Other text | Free-text query |

The keyword search capability (currently in /al-dev-ticket Step 1.5) is preserved in the unified skill.

## Action Routing

| Flag | Action |
|------|--------|
| (none) | Full research + reply via al-dev-support-researcher + al-dev-support-reply-drafter |
| `--fetch` | Context-only via al-dev-ticket-agent; write ticket-context.md; stop |

## Alias Recommendation

Keep `/al-dev-ticket` as a one-line redirecting alias:

```
/al-dev-ticket redirects to /al-dev-support --fetch [args]
```

This preserves muscle memory without maintaining duplicate logic.

## Files to Change (when this design is approved)

- Modify `profile-al-dev-shared/skills/al-dev-support/SKILL.md` — add --fetch routing + keyword search from /al-dev-ticket Step 1.5
- Keep `profile-al-dev-shared/skills/al-dev-ticket/SKILL.md` — replace body with redirect notice
- No agent changes needed (al-dev-ticket-agent and the split researcher/drafter agents are unchanged)
- Update `docs/al-dev-plugin-map.md` — note /al-dev-ticket as alias

## Open Questions

1. Should `--fetch` be `--fetch-only` or `--context-only`? Recommendation: `--fetch` — short, matches
   the agent's "phase: fetch" wording, unambiguous.
2. Should /al-dev-ticket be deleted entirely or kept as an alias? Recommendation: keep as alias for
   one release cycle, then remove.
