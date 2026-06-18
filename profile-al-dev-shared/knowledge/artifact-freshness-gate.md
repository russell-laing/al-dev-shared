# Artifact Freshness Gate

Reusable `.dev/` context artifacts (ticket context, exploration findings,
investigation findings, handoff packs, lint reports) persist across sessions.
A consuming workflow must never trust such an artifact as current evidence
without first confirming it is fresh relative to the code or inputs it
describes. This gate generalises the compile-log freshness check in
`compile-lint-procedure.md` (Step 0) to every reusable context artifact.

## Why This Exists

A stale artifact reused as if current produces wrong downstream routing,
plans built on outdated exploration, and false "ready" claims. See the
stale-artifact gaps documented in `handoff-chain-map.md` (Explore Findings
Staleness, Lint Report Accumulation).

## Covered Artifacts

| Artifact pattern | Producing skill | Stale when |
|---|---|---|
| `.dev/*-al-dev-ticket-ticket-context.md` | `al-dev-ticket` | the ticket was updated after the file was written |
| `.dev/*-al-dev-explore-findings.md` | `al-dev-explore` | source files it references changed after it was written |
| `.dev/*-al-dev-investigate-findings.md` | `al-dev-investigate` | source files in its evidence changed after it was written |
| `.dev/*-al-dev-handoff-handoff-prompt.md` | `al-dev-handoff` | the underlying findings were regenerated after the prompt |
| `.dev/*-al-dev-lint-lint-report.md` | `al-dev-lint` | any source file changed after the report |

## Gate Procedure

Before reading a reusable artifact as current evidence:

1. Resolve the latest matching artifact (glob, newest by modification time).
2. Determine its freshness against the inputs it describes. Prefer the paths the
   artifact itself names over a blanket single-language glob:

   - **Context artifacts (explore, investigate, ticket, handoff):** extract the
     concrete file paths the artifact references and compare each against the
     artifact's own modification time; treat it as possibly stale if any
     referenced path is newer. A glob limited to `.al` would miss real drift —
     this shared surface and many consuming projects carry Markdown, YAML,
     Python, and generated knowledge as primary source.
   - **Compile-log artifacts only:** the `.al` source glob is the correct check,
     mirroring `compile-lint-procedure.md`, because the artifact is a compile log:

     ```bash
     ART="$(ls .dev/<pattern> 2>/dev/null | sort | tail -1)"
     if [ -n "$ART" ]; then
       NEWER="$(find . -name '*.al' -newer "$ART" 2>/dev/null | head -1)"
       if [ -n "$NEWER" ]; then
         echo "Artifact may be stale - source files changed since it was written: $ART"
       fi
     fi
     ```

   - **Externally-derived artifacts (ticket- or handoff-derived):** compare
     against the upstream artifact or external input's last-known update
     timestamp rather than local source files.

3. If the artifact may be stale, do one of:
   - regenerate it by re-running the producing skill, or
   - explicitly confirm with the user that the stale artifact is still valid
     before using it.

Never present a completion, "ready", or routing decision that depends on an
artifact you have not confirmed is fresh in the current run.

## Relationship to Artifact Contracts

`artifact-contracts.md` governs which artifacts a skill may claim as durable
output and what success evidence a completion claim requires. This gate adds
the freshness dimension: success evidence must be both present and current.
