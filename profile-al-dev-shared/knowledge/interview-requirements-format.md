# Interview Requirements Output Format

## Requirements Entry Format

```markdown
REQ:REQ-001|FUNCTIONAL|HIGH|DEFINED|Validate customer credit limit before posting sales orders exceeding limit

ACC:ACC-001|REQ-001|Given: Customer with $10,000 credit limit | When: Posting $12,000 order | Then: Posting is blocked with error message

ACC:ACC-002|REQ-001|Given: Customer with $10,000 credit limit | When: Posting $8,000 order | Then: Posting succeeds
```

## Session Log Entry Format

```markdown
## [HH:MM:SS] al-dev-interview

- Interview duration: ~30 minutes
- Requirements gathered: X features
- Edge cases identified: Y
- Open questions: Z (for stakeholder resolution)
- Output: .dev/YYYY-MM-DD-al-dev-interview-requirements.md
- Status: ✓ Complete
```

**File path:** `.dev/$(date +%Y-%m-%d)-al-dev-interview-requirements.md`
