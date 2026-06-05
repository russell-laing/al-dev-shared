# Reviewer Findings Template

Canonical output format and severity taxonomy shared by the four code-review
specialist agents: al-dev-al-pattern-reviewer, al-dev-security-reviewer,
al-dev-performance-reviewer, and al-dev-general-code-reviewer.

## Findings Entry Format

Each finding must include all five fields:

- **File + Line:** `path/to/File.al:42`
- **Severity:** `Critical` / `High` / `Medium` / `Low`
- **Issue:** One sentence — what is wrong
- **Impact:** Why this matters (risk, performance, correctness, security)
- **Fix:** Concrete corrective action

## Severity Scale

| Level    | Definition |
|----------|-----------|
| Critical | Compile failure, data loss, or security breach requiring immediate action |
| High     | Logic error, incorrect behaviour, or significant performance/security risk |
| Medium   | Code smell, maintainability concern, or non-idiomatic AL pattern |
| Low      | Style, minor readability, or optional improvement |

## Output Section Format

Present findings organized by severity level:

```markdown
## CRITICAL

[List critical issues with file:line, issue, impact, fix]

## HIGH

[List high-severity issues]

## MEDIUM

[List medium-severity issues]

## LOW

[List low-severity issues]
```

## Panel Review Header

When reviewing as part of a parallel panel (dispatched alongside other specialists),
prefix your section with your role, e.g. `## Security Review Findings` or
`## AL Pattern Review Findings`.

Do not duplicate findings already listed in other reviewers' sections.
The lead agent synthesizes across the panel.
