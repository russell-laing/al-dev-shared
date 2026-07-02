---
name: validate-health-loop-second-opinion
description: Use when asked for a second opinion, external validator, or trust check on one Claude-produced plugin-health artifact before acting on it.
---

# Validate Health Loop Second Opinion

Perform a bounded, report-only trust assessment of one Claude-produced
plugin-health artifact.

Use this skill when the user asks for:

- a second opinion on a plugin-health artifact
- an external validator for a Claude health-loop output
- a trust check before acting on a findings report, dossier, plan, or
  loop-state-adjacent health report
- a review that decides whether a plugin-health artifact is trustworthy enough
  to use now

Do not use this for:

- generic code review
- broad repository health audits
- producing new plugin-health dossiers, plans, or disposition close-back events
- automatically editing `profile-al-dev-shared`, generated projections, or
  Claude health-loop artifacts

## Required Input

Exactly one source artifact:

- a concrete readable path, or
- pasted artifact content from the conversation

Supported first-wave artifact family:

- plugin-health findings report
- health dossier or assessment report
- plugin-health implementation plan
- loop-state-adjacent report whose purpose is to justify a next action in the
  plugin-health flow

If no source is supplied, ask for one concrete artifact. If the source is
outside this family, stop and say it is out of scope for this validator.

## Role Boundary

Claude health-loop skills own discovery, dossier production, planning,
implementation, close-back artifacts, and disposition updates.

This Codex skill owns only:

- independent trust assessment of the supplied artifact
- targeted live verification of consequential claims
- one durable review report under `.dev/`

Default failure behavior is a report. Do not auto-fix, regenerate, close
dispositions, or edit shared plugin content unless the user makes a separate
explicit patch request after reading the review.

## Workflow

### 1. Classify the source

Read the full source artifact. Identify one artifact class:

- `findings report`
- `health dossier`
- `implementation plan`
- `loop-state-adjacent report`

Before deep checking, state the artifact class, bounded validation scope, and
whether targeted live verification appears necessary.

If the artifact cannot be read, report the read failure and stop.

### 2. Run artifact-first validation

Check the artifact itself for:

- missing required sections, tables, handoff fields, or success evidence
- internal count drift, contradictory totals, or inconsistent status language
- severity, ranking, or recommendation strength that exceeds cited evidence
- unsupported claims using words such as `fixed`, `updated`, `validated`,
  `clean`, `ready`, or `closed`
- stale references detectable from the artifact alone

Use these minimum checks for the classified source:

- `findings report`: findings list, severity or priority signal, evidence for
  each consequential claim, and a next-action or recommendation section
- `health dossier`: findings summary, ranked recommendations or decision
  framing, supporting evidence, and any stated readiness or completion claims
- `implementation plan`: stated goal, scoped tasks or steps, validation
  commands or evidence expectations, and explicit non-goals or scope limits
- `loop-state-adjacent report`: current state claim, source of that claim,
  next-action basis, and any freshness cue such as timestamps, current-run
  evidence, or referenced live artifacts

This phase is text-only and deterministic. Do not start a fresh repo audit.

### 3. Promote only consequential claims to live verification

Verify live state only when the claim changes whether the maintainer should
trust or act on the artifact.

Use narrow checks such as:

```bash
test -e <referenced-path>
rg -n "<claim-specific-pattern>" <referenced-file-or-directory>
python3 scripts/health_disposition_store.py list-open
python3 scripts/check_ledger_staleness.py
python3 scripts/validate_health_loop_state.py
git status --short -- <referenced-path>
```

Examples of claims worth verifying:

- a recommendation depends on a file, skill, agent, or script path existing
- the artifact says a finding is already fixed, validated, clean, ready, or
  closed
- the next action depends on `.dev/health-loop-state.md`,
  `docs/health/dispositions_open.md`, `docs/health/dispositions_current.md`,
  `docs/health/dispositions_index.json`, or JSONL events under
  `docs/health/dispositions_events/`
- a priority ranking depends on live repo conditions rather than only on
  artifact-internal evidence

Do not verify claims that are merely background context and do not affect the
trust recommendation.

If the requested review would require a broad repo audit, stop and report that
the source cannot be validated within this skill's bounded scope.

### 4. Write the review report

Write one report to:

```text
.dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
```

Use the source basename without its extension for `<source-slug>`. If the
source came from pasted conversation content, use `conversation`.

Use this exact structure:

```markdown
# Health Loop Second Opinion: <Source Title>

Date: YYYY-MM-DD
Source: <path or conversation-supplied content>
Artifact class: <findings report | health dossier | implementation plan | loop-state-adjacent report>
Validation scope: <one paragraph describing what was checked>

## Trust Recommendation

<trust | trust with caveats | rework before use>

## Findings

### 1. <Finding title>

Classification: <valid blocker | valid but lower priority | stale | unsupported | overstated>
Evidence: <artifact quote or live repo check summary>
Impact: <why this changes trust in the source artifact>
Required action: <what the maintainer should do before relying on the source>

## Verified Areas

- <artifact sections, paths, commands, or live checks actually verified>

## Unverified Areas

- <areas intentionally not checked and why>

## Notes

- <confidence limits, blocked checks, or scope boundaries>
```

Each finding must use exactly one classification:

- `valid blocker`
- `valid but lower priority`
- `stale`
- `unsupported`
- `overstated`

The final trust recommendation must be exactly one of:

- `trust`
- `trust with caveats`
- `rework before use`

If live verification is blocked, downgrade confidence explicitly in the
recommendation and explain which check was blocked.

## Output Style

Present findings first in the chat response after writing the report. Include
the report path, the final trust recommendation, and the strongest evidence.

Do not paraphrase the entire source artifact. Do not claim the source is fixed,
validated, clean, ready, or closed unless the current run produced and read the
evidence needed for that claim.

## Validation Before Completion

Before saying the review is complete, run:

```bash
test -s .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
rg -n "^Date: [0-9]{4}-[0-9]{2}-[0-9]{2}$" .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
rg -n "^Source: .+" .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
rg -n "^Artifact class: (findings report|health dossier|implementation plan|loop-state-adjacent report)$" .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
rg -n "^Validation scope: .+" .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
rg -n "^## (Trust Recommendation|Findings|Verified Areas|Unverified Areas|Notes)$" .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
rg -n "^Classification: (valid blocker|valid but lower priority|stale|unsupported|overstated)$" .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
rg -n "^Evidence: .+" .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
rg -n "^Impact: .+" .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
rg -n "^Required action: .+" .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
rg -n "^(trust|trust with caveats|rework before use)$" .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
git diff --check -- .dev/YYYY-MM-DD-health-loop-second-opinion-<source-slug>.md
```

If any command fails, fix the report before presenting it.
