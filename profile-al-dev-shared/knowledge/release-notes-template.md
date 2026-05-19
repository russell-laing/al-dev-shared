# Release Notes Template

Referenced by: `al-dev-release-notes-writer` agent

## Release Notes Structure

Use this template when generating release notes:

```markdown
# Release Notes — v[VERSION]

**Release Date:** [YYYY-MM-DD]

## Summary
[One-paragraph overview of major changes, new features, and impact]

## New Features

- **Feature Name:** [Description with business impact]
  - Subfeature or related capability
- **Another Feature:** [Description]

## Bug Fixes

- **Bug Title:** [Description of what was broken and how it's fixed]
- **Another Bug:** [Description]

## Improvements

- **Performance:** [Describe optimization]
- **Usability:** [Describe UX improvement]

## Breaking Changes

- **Change Name:** [Description with migration guidance]
  - Migration path: [How to adapt existing code]

## Performance Improvements

- **[Area Name]:** [Metric improvement] — e.g., "API Response Time: 40% faster"
- **Database Query:** [Specific optimization]

## Known Issues

- **Issue:** [Description of known limitation]
  - Workaround: [If applicable]

## Deprecated Features

- **[Feature Name]:** Deprecated in this release, will be removed in v[X.Y]
  - Migration path: Use [alternative] instead

## Contributors

[If applicable: list contributors, credits]

## Installation & Upgrade

[Link to installation guide or upgrade instructions]
```

## Writing Guidelines

1. **Summary:** One paragraph capturing the essence — who should care and why
2. **Features:** User-facing benefits, not technical implementation
3. **Bug Fixes:** Describe the problem and the resolution, not just "fixed X"
4. **Breaking Changes:** ALWAYS include migration guidance
5. **Performance:** Include metrics if available (% improvement, before/after numbers)
6. **Metrics:** Be specific: "40% faster" not just "faster"

## Example

```markdown
# Release Notes — v2.5.0

**Release Date:** 2026-05-19

## Summary
This release focuses on performance improvements and API stability. We've optimized database queries for 40% faster response times and added comprehensive error handling. Three new reporting endpoints are now available for analytics integration.

## New Features

- **Analytics Reporting API:** Export transaction data, user activity, and custom reports via REST endpoints
- **Scheduled Exports:** Automate daily/weekly report generation
- **Performance Dashboard:** Real-time visibility into system health

## Bug Fixes

- **Issue:** Memory leak in background job processor — now properly cleans up after job completion
- **Issue:** API timeouts on large dataset exports — now batches results automatically

## Breaking Changes

- **Legacy Auth Endpoint (`/auth/legacy`):** Removed. Migrate to OAuth 2.0 — see [Migration Guide](docs/migration-v2.5.md)
```
