# Support Reply Output Format

The combined findings and reply file follows this structure:

```markdown
# Internal Findings

## Root Cause
[From researcher findings]

## Evidence

- AL Symbol: [from researcher]
- MS Docs: [from researcher]
- BC History: [from researcher]

## Workarounds
[From researcher findings]

---

# Draft Customer Reply

## Issue Summary
[Restate customer's problem in clear terms]

## Root Cause
[Non-technical explanation]

## Solution
[Step-by-step fix or workaround]

## If Issue Persists
[Escalation path, support contacts, debug steps]
```

**File path:** `.dev/$(date +%Y-%m-%d)-plugin-support-reply-<slug>.md`

Where `<slug>` is:

- Ticket ID if a ticket context file was provided (e.g., `T-12345`)
- Query-type slug for freetext queries (e.g., `connection-error`, `perf-issue`)
