# Architect Invocation Patterns

`solution-architect` is used through two structurally different
invocation styles: competitive planning in `/plan` and a bounded
single-architect diagnostic pass in `/fix`. The domain-specific prompt
content (what to analyse, what to produce) stays local to each skill; only the
structural mechanics are documented here.

## Pattern 1: Competitive Debate (×2-3 parallel)

Used by /plan.

Spawn 2-3 `solution-architect` agents in parallel, each assigned a
**meaningfully different starting approach** to prevent convergence. The goal
is genuine diversity of design, not minor variations on the same idea.

Before spawning, derive 2-3 distinct approaches from the requirement itself
(data-centric: table extension vs. separate table; process: event-driven vs.
direct integration; reporting: query object vs. API page, etc.).

After agents complete:

1. Collect all outputs (proposal, critique, falsification from each).
2. Facilitate cross-architect debate — challenge weak points, ask architects
   to respond to each other's critiques.
3. Synthesise the winner or create a hybrid from the best elements.

Spawn count guidance: 2 for SIMPLE; 2-3 for MEDIUM / COMPLEX, matching
`knowledge/plan-phase-routing.md`.

### Pattern 1 dispatch block

```text
Agent: al-dev-shared:solution-architect
Prompt:
  You are Architect {N} of {TOTAL}. Your assigned approach: {APPROACH_NAME}.

  **Task Complexity Tier:** {COMPLEXITY_TIER}

  Feature request:
  {REQUIREMENT_DESCRIPTION}

  Project context:
  - Object ID range: {OBJECT_ID_RANGE}
  - Naming prefix: {NAMING_PREFIX}
  - Key patterns: {KEY_PATTERNS}

  Starting approach:
  {APPROACH_DESCRIPTION}

  Design considerations:
  1. BC base app integration (tables/events to extend)
  2. Complete object design (tables, pages, codeunits, APIs)
  3. Data model and validation rules
  4. Testability (dependency injection, interfaces)
  5. Performance implications
  6. Upgrade considerations
  7. SaaS environment — If designing for BC SaaS, exclude SQL-based queries, direct database access, and stored procedures. Require AL-based SetFilter, Query objects, and AL logic for all data operations. See `solution-plan-template.md` for enforcement patterns.

  Produce three sections in exactly this order:
  1. Design proposal — existing objects to modify, new objects required, data flow
  2. Self-critique — the weakest point of your own design
  3. Falsification — one scenario that would prove your approach wrong
```

`{COMPLEXITY_TIER}` is resolved by the calling skill (e.g. plan maps it
from the architect model tier).

Include in prompt: the finalized `.dev/preflight-context.md` inputs consumed by
`/plan` Phase 2 (`requirements`, `scope`, `user_context`, and
`external_findings_status` when present), any AL symbol or analogue evidence
gathered during preflight, and the approach assignment derived from the
requirement.

## Pattern 2: Quick Analysis (×1 serial)

Used by `/fix` only for its bounded single-architect diagnostic path.

Spawn **one** `solution-architect` with a time-bounded prompt (5 min
max) to diagnose a bounded fix issue, not to produce a full architecture plan.
Ask for:

1. Root cause hypothesis (2-3 sentences)
2. Recommended fix approach (bullet points)
3. Files that need changes
4. Risks/side effects to watch for

After the agent returns, review the analysis yourself:

- Does the root cause make sense?
- Is the fix approach sound?
- Are there risks?

If the approach needs refinement, engage the architect directly (one
revision pass). After confirming, spawn a developer with the approved
approach.

### Pattern 2 dispatch block

```text
Agent: al-dev-shared:solution-architect
Prompt:
  Analyse this issue and return a concise fix plan. Time budget: 5 minutes.

  Issue:
  {ISSUE_DESCRIPTION}

  Files likely involved:
  {FILE_LIST}

  Return four sections in exactly this order:
  1. Root cause hypothesis (2–3 sentences)
  2. Recommended fix approach (bullet points)
  3. Files that need changes (paths only)
  4. Risks and side effects to watch for
```

Include in prompt: the reported symptom, likely file list, relevant file
contents, and compile or lint output if available. Keep the request scoped to
root-cause analysis and a minimal fix approach.

## Adding a New Caller

Add the new calling skill here with its pattern type, then document any
structural variation (e.g. different model tier, different output format).
