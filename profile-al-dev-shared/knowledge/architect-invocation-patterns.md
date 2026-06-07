# Architect Invocation Patterns

`al-dev-solution-architect` is used through two structurally different
invocation styles: competitive planning in `/al-dev-plan` and a bounded
single-architect diagnostic pass in `/al-dev-fix`. The domain-specific prompt
content (what to analyse, what to produce) stays local to each skill; only the
structural mechanics are documented here.

## Pattern 1: Competitive Debate (×2-3 parallel)

Used by /al-dev-plan.

Spawn 2-3 `al-dev-solution-architect` agents in parallel, each assigned a
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
`knowledge/al-dev-plan-phase-routing.md`.

### Pattern 1 dispatch block

```text
Agent: al-dev-shared:al-dev-solution-architect
Prompt:
  You are Architect {N} of {TOTAL}. Your assigned approach: {APPROACH_NAME}.

  Feature request:
  {REQUIREMENT_DESCRIPTION}

  Starting approach:
  {APPROACH_DESCRIPTION}

  Produce three sections in exactly this order:
  1. Design proposal — existing objects to modify, new objects required, data flow
  2. Self-critique — the weakest point of your own design
  3. Falsification — one scenario that would prove your approach wrong
```

Include in prompt: the finalized `.dev/preflight-context.md` inputs consumed by
`/al-dev-plan` Phase 2 (`requirements`, `scope`, `user_context`, and
`external_findings_status` when present), any AL symbol or analogue evidence
gathered during preflight, and the approach assignment derived from the
requirement.

## Pattern 2: Quick Analysis (×1 serial)

Used by `/al-dev-fix` only for its bounded single-architect diagnostic path.

Spawn **one** `al-dev-solution-architect` with a time-bounded prompt (5 min
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
Agent: al-dev-shared:al-dev-solution-architect
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
