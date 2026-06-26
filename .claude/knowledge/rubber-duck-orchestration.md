# Rubber-Duck Orchestration

How to orchestrate the rubber-duck verification pass across many findings.
Referenced by `/plan-plugin-findings` Phase 2. The per-check registry (Universal
U1–U3 and type-specific checks) lives in
`../../profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`; this doc
owns the run flow only.

## Progress tracking

Before rubber-ducking any suggestion, create one progress todo per suggestion
named `[Type] [Subject]`. Mark each in-progress when rubber-ducking begins and
complete when its rubber-duck record is written.

## Read-only dispatch (default)

Rubber-ducking and evidence verification are **read-only** — they never modify
subject files. Because they are read-only, parallel dispatch to isolated
subagents is safe by default and eliminates the per-finding inline-read cost
that causes context growth.

**Default model:** dispatch one `verify-health-finding` agent per finding (batch
findings that share one subject file into a single agent). Use
`superpowers:dispatching-parallel-agents`. Each agent reads subject files in
its own context and returns only a compact rubber-duck record — no file dumps,
no source echoes. The parent collects records and never reads subject files
itself during Phase 2.

Sequential inline rubber-ducking is the fallback **only** when
`superpowers:dispatching-parallel-agents` is genuinely unavailable.

## Evidence Mode

The `evidence` mode is dispatched by `/report-plugin-health` Phase 2 to verify
that each finding's cited `file:line` snippet still exists at the named
location. The canonical dispatch fields, batching rules, and `verified |
dropped: <reason>` handling live in
`.claude/knowledge/report-input-gates.md` §1c. This document adds only the mode
distinction: evidence mode is a read-only verification pass and is not the same
as rubber-duck verdicting for planning.

## Independence and modify sets

Independence analysis applies only when the accepted worklist contains a
**modify** set — findings where the proposed change to one subject file would
affect whether another finding's claim holds. For read-only verification, every
finding is independent by definition; no topological ordering is required.

If Phase 2 yields `modify` verdicts whose adjusted scopes share file-set
dependencies, build a directed edge A→B when B's scope depends on A's
adjustment; process in topological order, parallelising any layer with no
incoming edges.

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
