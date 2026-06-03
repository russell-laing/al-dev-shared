# Ticket Agent Invocation Pattern

Canonical pattern for dispatching `al-dev-ticket-agent` from skills that interact with Freshdesk.

## Pattern Summary

The `/al-dev-ticket` skill dispatches `al-dev-ticket-agent` for the fetch phase in both modes. When `--mode=full` is selected, `/al-dev-ticket` then chains to `/al-dev-support-reply` for research and reply drafting. This document captures the canonical fetch-phase pattern to prevent drift.

## Dispatch Block Template

```bash
Agent tool:
  agent: al-dev-shared:al-dev-ticket-agent
  description: "Fetch Freshdesk ticket #[TICKET_ID]"

Prompt: |
  Fetch Freshdesk ticket and write
  .dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md.

  Phase: fetch
  Ticket ID: [TICKET_ID]

  FRESHDESK_API_KEY and FRESHDESK_DOMAIN are set in the
  environment — use them directly in curl commands.
```

## Environment Variables

The following environment variables **must be set** by the harness before dispatching the agent:

| Variable | Description | Source |
|----------|-------------|--------|
| `FRESHDESK_API_KEY` | Freshdesk API authentication key | User's global settings (harness settings file) |
| `FRESHDESK_DOMAIN` | Freshdesk subdomain (e.g., `company.freshdesk.com`) | User's global settings |

These are resolved from the harness environment, not passed in the dispatch prompt.

## Phases

### Phase: fetch

Fetch Freshdesk ticket metadata, conversations, and attachments. Output structured ticket context.

**Agent behavior:**
1. Use `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` from environment
2. Make sequential API calls (not parallel) to avoid rate-limiting
3. Extract inline images from conversation HTML (regex scan for `src=` attributes)
4. Write structured `.dev/` output file with metadata, conversations, and attachments
5. Return structured block with file path and summary

**Output file:** `.dev/$(date +%Y-%m-%d)-al-dev-ticket-ticket-context.md`

**Return block format:**

```text
TICKET_CONTEXT_WRITTEN: .dev/YYYY-MM-DD-al-dev-ticket-ticket-context.md
TICKET_ID: [ID]
STATUS: [Status]
PRIORITY: [Priority]
COMMENTS_COUNT: [N]
ATTACHMENTS: [Count or "None"]
INLINE_IMAGES_COUNT: [N or "None"]
```

## Using This Pattern

When a new skill needs to fetch Freshdesk tickets, it should:

1. Reference this file in the skill documentation
2. Copy the dispatch block template above
3. Substitute `[TICKET_ID]` with the user's ticket ID
4. Ensure `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` are available in the environment
5. Parse the return block to extract the output file path

## Related Files

```text
profile-al-dev-shared/agents/al-dev-ticket-agent.md
profile-al-dev-shared/skills/al-dev-ticket/SKILL.md
```

- Agent definition: `profile-al-dev-shared/agents/al-dev-ticket-agent.md`
- Skills using this pattern:
  - `/al-dev-ticket` — Fetch and contextualize the ticket (with `--mode=context-only` or `--mode=full`)
  - `/al-dev-support-reply` — Follow-on research and reply drafting after ticket context is loaded

### Ticket Type → Affected Files Mapping

| Ticket Type | Primary Files | Agent Spawn Context |
|-------------|--------------|-------------------|
| **Bug Report** | Codeunit, Table, Page (where bug occurs) | `ticket_type: "bug"`, `severity: "high|medium|low"` |
| **Feature Request** | New Codeunit/Table, Existing Page (UI integration point), Test coverage plan | `ticket_type: "feature"`, `priority: "p1|p2|p3"` |
| **Performance Issue** | Codeunit (query loops, batching), Table (indexing), Report (rendering) | `ticket_type: "perf"`, `metric: "response_time|memory|throughput"` |
| **Data Migration** | New Codeunit (migration logic), Source/Target Tables | `ticket_type: "data-migration"`, `cutover_date: "YYYY-MM-DD"` |
| **Integration** | New Codeunit (API/webhook handler), Existing Codeunit (caller), External API definition | `ticket_type: "integration"`, `system: "Salesforce|SAP|Custom"` |
| **Documentation** | Knowledge files, Help context strings, project instructions file | `ticket_type: "docs"`, `audience: "admin|developer|end-user"` |
| **Compliance/Security** | Codeunit (access control), Table (audit fields), Permission Set | `ticket_type: "compliance"`, `standard: "GDPR|SOC2|HIPAA"` |

### When Ticket Analysis Routes to Multiple Files

If a ticket requires changes to 3+ files, the ticket agent should:

1. **Prioritize by logical dependency:** Core table changes before UI changes, data structures before business logic
2. **Document affected file groups:** Group related changes (e.g., "Data Layer: [tables]", "Business Logic: [codeunits]")
3. **Flag integration points:** Where one file's changes affect another (e.g., table field rename requires codeunit update)

**Example:** Feature ticket requesting "Add customer credit limit field and enforce it on sales orders"

Affected file mapping:
```
TABLES:
- Customer table (add Credit Limit field, validation)
- Sales Order Header (add Check Credit Before Release field)
- Sales Order Line (reference customer credit limit)

CODEUNITS:
- Sales-Post codeunit (add pre-post validation checking credit limit)
- Customer-Management codeunit (add credit limit recalculation on receipt)

PAGES:
- Customer Card (add Credit Limit field to FactBox)
- Sales Order (add warning if approaching credit limit)

TESTS:
- Add test_CustomerCreditLimitEnforcement.al
- Add test_SalesOrderCreditCheck.al
```

### Invocation Pattern: Agent Spawn Parameters

For the canonical fetch phase, the live dispatch contract is intentionally small:

- `TICKET_ID` in the dispatch prompt
- `FRESHDESK_API_KEY` in the environment
- `FRESHDESK_DOMAIN` in the environment

Do not assume richer typed routing metadata is available unless the calling workflow explicitly adds it as a separate downstream context block.
