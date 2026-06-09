# Rubber-Duck Orchestration

How to orchestrate the rubber-duck verification pass across many findings.
Referenced by `/plan-health-findings` Phase 2. The per-check registry (Universal
U1–U3 and type-specific checks) lives in
`../../profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`; this doc
owns the run flow only.

## Progress tracking

Before rubber-ducking any suggestion, create one progress todo per suggestion
named `[Type] [Subject]`. Mark each in-progress when rubber-ducking begins and
complete when its rubber-duck record is written.

## Independence and parallel exploration

Two suggestions are **independent** iff (a) the file sets they would modify are
disjoint, AND (b) neither suggestion's subject file is read during the other's
checks. Build a directed edge A→B when B's checks must read a file A produces or
modifies; process in topological order, parallelising any layer with no incoming
edges.

When a topological layer contains 3+ independent suggestions, dispatch that layer
to parallel exploration agents before starting rubber-ducking (in Claude Code,
invoke `superpowers:dispatching-parallel-agents`); if parallel dispatch is
unavailable, rubber-duck the layer sequentially. Dispatch one exploration agent
per suggestion (or per subject file when several findings share one file). Each
agent reads the affected file(s) in full, runs the U2 artifact checks and the
type-specific checks, and returns a structured rubber-duck record. Collect all
records before writing any plan content. When every layer contains ≤2
suggestions, the sequential inline path is fine.

## Cross-layer verification (conditional)

When the accepted worklist contains both skill and agent findings, verify the two
layers together before writing any verdicts:

1. Trace each affected skill-to-agent handoff through the live skill callers and
   agent "Spawned by" references. A *live skill caller* is a skill file that
   spawns the agent — search active skill bodies for the agent's
   `al-dev-shared:<agent-name>` invocation. Record missing, stale, or
   contradictory caller relationships in the relevant rubber-duck records.
2. Compare skill complexity with agent model assignments using the current maps,
   then confirm disputed values against the live skill and agent source. Do not
   rely on dossier-era assignments when the source has changed.
3. Identify skill and agent changes that must land together to preserve a
   handoff, model fit, or shared pattern. Record each coupled pair as one plan
   task or as explicit task dependencies.

This verification creates no standalone artifact; its evidence stays in the
rubber-duck records and the resulting plan.
