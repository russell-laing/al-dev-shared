# Phase-Proof Contract

Repo-local rule for multi-phase maintainer skills under `.claude/skills/`.
It closes the "phantom execution" gap: a skill may not report a phase
complete, advance to the next phase, or write its phase result to the
health-loop breadcrumb until it has emitted a **phase-proof block**.

This is distinct from the shared end-of-run success-evidence rule in
`profile-al-dev-shared/knowledge/artifact-contracts.md`: that governs the
final deliverable; this governs every intermediate phase boundary.

## What a phase-proof block is

A fenced command plus its real output that demonstrates the phase's
deliverable exists or its action ran. Use the cheapest proof that actually
binds to the deliverable:

- File produced this phase: `ls -la <path>` (exists) and, when content
  matters downstream, `wc -l <path>` (non-empty).
- Command/dispatch ran: the command's own exit status or a one-line summary
  of its captured stdout.
- Aggregation/parse step: a count assertion (e.g. number of findings parsed).

A restated intention ("Phase 2 complete") is NOT proof. The block must show
observed output, not a claim.

## When it is required

Before any of: printing a "phase N complete" line, advancing to phase N+1,
or writing the phase outcome to `.dev/health-loop-state.md`.

## Skills in scope

The authoritative list is the `MULTI_PHASE_SKILLS` set in
`scripts/validate_maintainer_contracts.py`. A skill enters scope when it has
two or more numbered phases that report progress between them. Single-phase
utilities and pure read-only reporters are out of scope.

## Related contracts

- `report-input-gates.md` and `health-audit-preconditions.md` already gate
  specific inputs; this contract generalizes the per-phase proof requirement.
- `health-loop-state-contract.md` defines the breadcrumb that a proven phase
  is allowed to update.
- `profile-al-dev-shared/knowledge/workflow-resilience.md` (shared) covers
  checkpoint/resume; phase-proof is the proof that a checkpoint is real.
