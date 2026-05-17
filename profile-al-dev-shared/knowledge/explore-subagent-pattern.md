# Explore Subagent Pattern

Skills that delegate codebase investigation to a focused read-only
agent follow this three-step structure. The domain-specific prompt
content (what to look for, what to report) stays local to each
skill; only the structural mechanics are documented here.

## When to Use an Explore Subagent

Use an Explore subagent when:
- The investigation covers multiple files or directories
- Results must be written to `.dev/` for persistence
- The question is bounded (one analytical lens)

Do NOT use an Explore subagent for:
- Simple single-file reads (use Read directly)
- Tasks that require editing (Explore agents are read-only)

## Step A — Load Context

Before spawning, check for and read:

1. `.dev/project-context.md` (if it exists) — key objects,
   architectural patterns, directory layout
2. Latest ticket context (glob):
   `$(ls .dev/*-al-dev-ticket-ticket-context.md 2>/dev/null | sort | tail -1)`
3. Latest explore findings (glob):
   `$(ls .dev/*-al-dev-explore-findings.md 2>/dev/null | sort | tail -1)`

Pass relevant excerpts (not the full files) into the agent prompt
to narrow scope and avoid redundant discovery.

## Step B — Spawn Invocation Format

The canonical Agent tool invocation for an Explore subagent:

```text
Spawn an explore agent:
  purpose: [Domain] scan: [scope description]
  prompt: [domain-specific investigation prompt — defined locally
           in each skill, not here]
  output: structured findings with file paths and line numbers
```

Agent type: `Explore` (the fast read-only search agent).

Spawn count guidance:
- ×1 for a single analytical lens (explore, perf, single-topic investigate)
- ×2 in parallel for hypothesis testing (investigate splits hypotheses
  evenly across two agents)

## Step C — Output File Convention

Write findings to `.dev/` immediately after the agent returns.
Do NOT accumulate results in memory and write at the end of the skill.

Naming: `$(date +%Y-%m-%d)-<skill-name>-<artifact-name>.md`

Examples:
- `2026-05-18-al-dev-explore-findings.md`
- `2026-05-18-al-dev-perf-perf-analysis.md`
- `2026-05-18-al-dev-explore-findings.md` (investigate also uses this name)

Files are date-prefixed to preserve history. Do not overwrite previous runs.

## Step D — Present to User

After writing the file, show a short inline summary and reference the file:

```text
[Domain] analysis complete → .dev/[filename].md

[2–5 sentence summary of findings]

[Suggest next command if findings warrant one]
```
