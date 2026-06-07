# Ledger Closure Protocol

Use this protocol when a fix session resolves an `accepted` health finding.

## Why closure matters

`docs/health/dispositions.md` is the source of truth for whether an accepted
finding is still open. A code change without same-session ledger closure leaves
the row falsely open and causes later sweeps to re-rank fixed work.

## Closure rules

1. If the accepted row is still local and uncommitted, update that row in place:
   set the disposition to `fixed` and replace the note with the resolving
   commit hash plus a short summary.
2. If the accepted row is already committed, append a new `fixed` row for the
   same object and issue essence. Include the resolving commit hash and
   `closes row N` so the supersession is machine-readable.
3. Cite the ledger row in the resolving commit message when practical so the
   closure is auditable from git history.

## Verification

Run `python3 scripts/check_ledger_staleness.py` after the source change. Any
remaining `STALE-OPEN` row for the resolved object means the closure write-back
did not happen correctly.
