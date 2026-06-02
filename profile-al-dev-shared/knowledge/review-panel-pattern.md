# Review Panel Pattern

The three-reviewer panel is the standard parallel review composition
used by /al-dev-develop (with or without `--autonomous`). Spawn all three
reviewers in a single batch (one message, three agent dispatches).

## Composition

**al-dev-security-reviewer:**
Review all implemented code for permission issues, data exposure
risks, authentication gaps.

**al-dev-al-pattern-reviewer:**
Review for AL naming conventions, BC best practices
(SetLoadFields, FieldCaption), code organization, event patterns.

**al-dev-performance-reviewer:**
Review for query efficiency, N+1 patterns, SetLoadFields usage,
loop efficiency, record variable scoping.

Each reviewer reads ALL implemented AL files.

## Spawn Instructions

Dispatch all three as a single batch in a single message with three
independent agent dispatch blocks:

```text
Dispatch agent: al-dev-shared:al-dev-security-reviewer
  description: "Security review of implemented code"
  prompt: "Review these AL files for security issues: [file list]. Check permissions, data exposure, auth gaps."

Dispatch agent: al-dev-shared:al-dev-al-pattern-reviewer
  description: "AL patterns and BC best practices review"
  prompt: "Review these AL files for naming, patterns, BC conventions: [file list]. Check SetLoadFields, naming consistency, event patterns."

Dispatch agent: al-dev-shared:al-dev-performance-reviewer
  description: "Performance analysis of implemented code"
  prompt: "Review these AL files for query efficiency and performance: [file list]. Check N+1 patterns, SetLoadFields, loop scoping."
```

**Pattern:** All three dispatches in ONE message (x3 parallel) — execution time = max(all three), not sum.

- All reviewers read **the same file list** (complete implementation set)
- Each reviewer focuses on their domain (security / patterns / performance)
- Responses arrive in any order; synthesis happens after all complete

## Synthesis (after all three complete)

1. Read all three review outputs.
2. Cross-reference overlapping findings — issues raised by multiple
   reviewers are higher priority than single-reviewer findings.
3. Where reviewers contradict each other (e.g. AL Expert recommends
   a pattern that Performance flags as slow), apply judgement to
   resolve using the severity categories in the calling skill.
4. Consolidate into a single categorised list before assigning fixes.

## Adding a Fourth Reviewer

Add the new reviewer type here with its role description, then update
the spawn batch in each calling skill's review phase.
