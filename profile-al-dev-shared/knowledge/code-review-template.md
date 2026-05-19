# Code Review Template

## Standard Structure

```markdown
## Code Review: [Feature Name]

### Implementation Summary
[What was built: objects, key functionality]

### Review Process
3 specialized reviewers (security, AL expert, performance)
completed parallel review.

### Critical Issues (All Resolved)
- Issue: [description]
  Fix: [what was changed]
  Verified by: [which reviewer re-checked]

### Issues for User Decision

**High Priority:**
1. [Issue description]
   - Severity: High
   - Impact: [what happens if not fixed]
   - Recommendation: [suggested fix]

**Minor Issues:**
1. [Issue description]
   - Recommendation: [optional improvement]

### Review Consensus
[Overall quality assessment]

### Recommendation
Code is ready for [testing/deployment] with [N]
high-priority issues to address.
```

## Autonomous Mode Addition

Append this section when `--autonomous` is active:

```markdown
### Autonomous Verification Results

#### Signature Verification
| Procedure | Status | Source |
| --- | --- | --- |
| ObjectName.ProcedureName | ✅ Verified | al_search_object_members |
| ObjectName.OtherProc | ⚠️ Not verified | Not found in MCP |

Unverified risks: [describe any NOT VERIFIED entries]

#### Static Validation
| Check | Result |
| --- | --- |
| Object names (≤30 chars) | ✅ All valid / ❌ N fixed |
| Compile guards (#if logic) | ✅ All correct / ❌ N fixed |
| Label consistency | ✅ Matches plan / ⚠️ N flagged |

#### Compile-Verify Loop
- Attempts required: N of 5
- Final status: ✅ Clean / ⚠️ N warnings remain
```
