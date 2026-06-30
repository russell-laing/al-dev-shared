# Exploration Findings Output Format

When writing persistent findings, use this ANSWER/FILES structure:

```markdown
# Codebase Exploration Results

**Question:** [Original exploration question]
**Date:** [Today's date]
**Scope:** [Scope explored]

## ANSWER
[Direct answer to the question]

## FILES
- **File:** path/to/file.al (lines X-Y)
  - **Finding:** What was discovered

## PATTERNS
[Optional supporting patterns or recurring observations]

## RISKS
[Optional risks, gaps, or follow-up items]
```

**File path:** `.dev/$(date +%Y-%m-%d)-explore-findings.md`
