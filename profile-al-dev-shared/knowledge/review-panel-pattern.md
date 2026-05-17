# Review Panel Pattern

The three-reviewer panel is the standard parallel review composition
used by /al-dev-develop and /al-dev-autonomous. Spawn all three
reviewers in a single batch (one message, three Agent tool calls).

## Composition

**al-dev-security-reviewer:**
Review all implemented code for permission issues, data exposure
risks, authentication gaps.

**al-dev-expert-reviewer:**
Review for AL naming conventions, BC best practices
(SetLoadFields, FieldCaption), code organization, event patterns.

**al-dev-performance-reviewer:**
Review for query efficiency, N+1 patterns, SetLoadFields usage,
loop efficiency, record variable scoping.

Each reviewer reads ALL implemented AL files.

## Spawn Instructions

Spawn all three as a single batch:
- Agent type: `al-dev-security-reviewer`, `al-dev-expert-reviewer`,
  `al-dev-performance-reviewer`
- Prompt each reviewer with: paths to ALL implemented AL files
- Pattern: ×3 parallel (one message, three Agent calls)

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
