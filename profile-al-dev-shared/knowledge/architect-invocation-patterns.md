# Architect Invocation Patterns

`al-dev-solution-architect` is spawned by two skills using structurally
different patterns. The domain-specific prompt content (what to analyse,
what to produce) stays local to each skill; only the structural mechanics
are documented here.

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

Spawn count guidance: 2 for SIMPLE/MEDIUM; 3 for COMPLEX. Omit if
TRIVIAL — route directly to a developer.

## Pattern 2: Quick Analysis (×1 serial)

Used by /al-dev-fix (non-trivial path).

Spawn **one** `al-dev-solution-architect` with a time-bounded prompt (5 min
max). Ask for:
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

## Adding a New Caller

Add the new calling skill here with its pattern type, then document any
structural variation (e.g. different model tier, different output format).
