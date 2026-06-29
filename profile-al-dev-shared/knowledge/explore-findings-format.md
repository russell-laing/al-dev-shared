# Exploration Findings Output Format

When writing persistent findings, follow this structure:

```markdown
# Codebase Exploration Results

**Question:** [Original exploration question]
**Date:** [Today's date]
**Scope:** [Scope explored]

## Findings

### [Category 1]
- **File:** path/to/file.al (lines X-Y)
- **Finding:** What was discovered

### [Category 2]
[Repeat]

## Summary
[Concise explanation of code organization relevant to question]

## Recommendations
[Next steps or related areas to explore]
```

**File path:** `.dev/$(date +%Y-%m-%d)-explore-findings.md`
