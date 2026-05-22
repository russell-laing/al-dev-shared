# Ticket Agent Invocation Pattern

Canonical pattern for dispatching `al-dev-ticket-agent` from skills that interact with Freshdesk.

## Pattern Summary

Both `/al-dev-ticket` and `/al-dev-support` dispatch `al-dev-ticket-agent` with identical environment variables and phase parameters. This document captures the canonical pattern to prevent drift.

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
TICKET_LOADED
FILE: .dev/YYYY-MM-DD-al-dev-ticket-ticket-context.md
TITLE: [ticket title]
STATUS: [ticket status]
SUMMARY: [one-line summary]
ATTACHMENTS: [count]
```

## Using This Pattern

When a new skill needs to fetch Freshdesk tickets, it should:

1. Reference this file in the skill documentation
2. Copy the dispatch block template above
3. Substitute `[TICKET_ID]` with the user's ticket ID
4. Ensure `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` are available in the environment
5. Parse the return block to extract the output file path

## Related Files

- Agent definition: `profile-al-dev-shared/agents/al-dev-ticket-agent.md`
- Skills using this pattern:
  - `/al-dev-ticket` — Fetch ticket context (Phase 3)
  - `/al-dev-support` → redirects to `/al-dev-ticket --mode=full` (Phase 2)

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

When the ticket skill spawns the ticket agent, it passes context in this structure:

```json
{
  "ticket_id": "JIRA-1234",
  "ticket_type": "bug|feature|perf|data-migration|integration|docs|compliance",
  "title": "user-provided ticket title",
  "description": "user-provided full description",
  "priority": "p1|p2|p3",
  "severity": "critical|high|medium|low",
  "affected_systems": ["Customer", "Sales Order", "Reports"],
  "context_files": ["path/to/al/file.al", "docs/knowledge/related-doc.md"]
}
```

**Example invocation for bug ticket:**

```json
{
  "ticket_id": "BUG-567",
  "ticket_type": "bug",
  "title": "Sales Order total calculation incorrect when multiple discounts applied",
  "description": "When a sales order has both header discount and line discounts...",
  "severity": "high",
  "affected_systems": ["Sales Order", "Calculation Engine"],
  "context_files": ["SalesOrder.Codeunit.al", "DiscountCalculation.Codeunit.al"]
}
```

The ticket agent uses this to route analysis to the correct files and assessment framework (bug analysis vs. feature feasibility).
