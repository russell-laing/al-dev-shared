# Performance Report Template

```markdown
# Performance Analysis — [scope] — [date]

## Summary

| Severity | Count |
| --- | --- |
| 🔴 CRITICAL | N |
| 🟠 HIGH | N |
| 🟡 MEDIUM | N |
| 🟢 LOW | N |

**Total findings:** N across X files

## Findings

### 🔴 CreateJobV6.Codeunit.al — ⚡ Entry Point

#### 🔴 P1 — N+1 Query — line 123

~~~al
// Current (BAD):
if V6QuoteItem.FindSet() then repeat
    Item.Get(V6QuoteItem."Item No.");  // N DB calls
until V6QuoteItem.Next() = 0;
~~~

**Fix:**

~~~al
// Pre-load all Items with SetLoadFields before the loop,
// or cache in a temporary record keyed on Item No.
~~~

**Estimated impact:** CRITICAL (escalated from HIGH) — Entry Point called by Job Queue; P1 hit on every quote item in batch processing

[Repeat per codeunit; within each codeunit, repeat per finding ordered by CRITICAL → LOW]

### 🟢 StringHelper.Codeunit.al — 🗃 Utility

#### 🟢 P6 — SetRange + FindFirst — line 44

[finding details...]

**Estimated impact:** LOW — Utility procedure; low call frequency

## Recommended Fix Order

1. [CRITICAL findings — fix immediately]
2. [HIGH findings — fix before next release]
3. [MEDIUM findings — fix when touching the file]
4. [LOW findings — optional, low risk]

## Next Steps

[If CRITICAL or HIGH findings:]
Design fixes with: `/al-dev-plan fix performance issues in [scope]`

[If only LOW findings:]
No critical issues. Low findings documented for reference.
```
