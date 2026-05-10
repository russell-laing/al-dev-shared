# Feedback Resolution Protocol

Reference document for structured disposition of review findings across all review agents (plan-reviewer, code-reviewer).

## Severity Levels

| Severity | Definition | Examples |
|----------|-----------|----------|
| **CRITICAL** | Blocks progress. Must be fixed before proceeding. | Security vulnerability, data corruption risk, fundamental design flaw, compliance failure |
| **SERIOUS** | Significant risk if ignored. Should be fixed. | Performance issue, DRY violation, missing error handling, BC anti-pattern, missing edge case |
| **MINOR** | Improvement suggestion. Acceptable to defer. | Documentation gap, naming inconsistency, style preference, future enhancement |

## Dispositions

Each finding must receive one of these dispositions:

| Disposition | Meaning | When to Use |
|-------------|---------|-------------|
| **ACCEPT-FIX** | Will fix now | Issue is valid and will be addressed in this iteration |
| **ACCEPT-DEFER** | Valid but fix later | Issue is real but not blocking; tracked for future work |
| **ACKNOWLEDGE** | Noted, accepted as-is | Understood the trade-off, proceeding intentionally |
| **DISMISS** | Not applicable | Finding is incorrect or not relevant; requires reasoning |

## Rules

1. **CRITICAL findings MUST be ACCEPT-FIX** — no exceptions
2. **DISMISS requires written reasoning** — explain why the finding doesn't apply
3. **ACCEPT-DEFER requires a tracking note** — where/when will it be addressed
4. **All findings must be dispositioned** — none can be left unaddressed

## Exit Condition

A review loop exits when ALL of the following are true:
- Every finding has a disposition
- No ACCEPT-FIX items remain (all have been implemented)
- Reviewer confirms: **"APPROVED: Proceed to [next step]"**

## Disposition Reporting Format

After receiving review findings, the fixing agent (solution-planner or al-developer) reports dispositions:

```markdown
## Feedback Dispositions

| # | Finding | Severity | Disposition | Action/Reasoning |
|---|---------|----------|-------------|-----------------|
| 1 | Missing error handling in Get() | CRITICAL | ACCEPT-FIX | Added null check with Error() |
| 2 | DRY violation in 3 files | SERIOUS | ACCEPT-FIX | Centralized in CreditLimitMgt |
| 3 | Missing XML docs | MINOR | ACCEPT-DEFER | Will add in documentation phase |
| 4 | Use enum instead of boolean | MINOR | DISMISS | Boolean is sufficient for binary state |
```

## Iteration Flow

```
Reviewer produces findings with severity
    ↓
Fixing agent dispositions each finding
    ↓
Fixing agent implements all ACCEPT-FIX items
    ↓
Reviewer re-reviews
    ├─ All resolved → "APPROVED: Proceed to [next step]"
    └─ Issues remain → Another iteration
```

## Stall Prevention

If the same finding appears 3+ times across iterations with no progress, escalate to user. See Loop Governance in CLAUDE.md.
