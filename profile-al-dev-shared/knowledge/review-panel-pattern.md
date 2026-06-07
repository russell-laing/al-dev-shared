# Review Panel Pattern

The three-reviewer panel is the standard parallel review composition used by
`/al-dev-review-develop` after `/al-dev-develop` produces its implementation
handoff. Dispatch all three reviewers simultaneously through the active
harness's parallel agent capability.

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

Each reviewer receives the same preflight `CHANGED_FILES` list and the
implementation context from the `/al-dev-develop` handoff.

## Spawn Instructions

Dispatch all three simultaneously as one parallel batch. Use the active
harness's native agent-dispatch mechanism:

```text
Dispatch agent: al-dev-shared:al-dev-security-reviewer
  description: "Security review of implemented code"
  prompt: "Review these AL files for security issues: [CHANGED_FILES]. Use the supplied implementation context. Check permissions, data exposure, auth gaps."

Dispatch agent: al-dev-shared:al-dev-al-pattern-reviewer
  description: "AL patterns and BC best practices review"
  prompt: "Review these AL files for naming, patterns, and BC conventions: [CHANGED_FILES]. Use the supplied implementation context. Check SetLoadFields, naming consistency, event patterns."

Dispatch agent: al-dev-shared:al-dev-performance-reviewer
  description: "Performance analysis of implemented code"
  prompt: "Review these AL files for query efficiency and performance: [CHANGED_FILES]. Use the supplied implementation context. Check N+1 patterns, SetLoadFields, loop scoping."
```

Require each reviewer to use the canonical output format and severity taxonomy
from `reviewer-findings-template.md`.

- All reviewers receive **the same preflight file list and implementation context**
- Each reviewer focuses on their domain (security / patterns / performance)
- Responses arrive in any order; synthesis happens after all complete

## Synthesis (after all three complete)

1. Read all three review outputs.
2. Cross-reference and deduplicate overlapping findings. Agreement from
   multiple reviewers increases confidence in a finding but does not, by
   itself, change its severity.
3. Where reviewers contradict each other (e.g. AL Expert recommends
   a pattern that Performance flags as slow), apply judgement to
   resolve using the canonical severity scale in
   `reviewer-findings-template.md`.
4. Consolidate into a single categorised list before assigning fixes.

## Adding a Fourth Reviewer

Add the new reviewer type here with its role description, then update
the spawn batch in each calling skill's review phase.
