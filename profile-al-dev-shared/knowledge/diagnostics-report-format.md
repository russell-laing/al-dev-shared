# AL Diagnostics Report Format

The diagnostic report follows this structure:

```markdown
# AL Diagnostics Report

## Summary

- Total issues: X
- Fixed: Y
- Unresolved: Z
- Duration: ~Xm

## Fixed Issues

- AA0073 (5 occurrences): Temporary variable naming → Fixed
- AA0218 (12 occurrences): Field DataClassification → Fixed

## Unresolved Issues

- AS0016 (3 occurrences): DataClassification requires explicit choice
  - File: src/Tables/Price.al (lines: 10, 25, 42)
  - Action: Review and apply appropriate classification

## Compilation Status
✓ All fixes applied; compilation passing (0 errors, X warnings)
```

**File path:** `.dev/$(date +%Y-%m-%d)-al-dev-diagnostics-report.md`
