# Ledger Closure Protocol

> See `.claude/knowledge/health-disposition-storage-contract.md` for the
> authoritative storage layout. `docs/health/dispositions-history/` is the
> append-only source of truth; `docs/health/dispositions.md` is the generated
> current-state view. Never append rows directly to `docs/health/dispositions.md`.

Use this protocol when a fix session resolves an `accepted` health finding.

## Why closure matters

`docs/health/dispositions.md` is the source of truth for whether an accepted
finding is still open. A code change without same-session ledger closure leaves
the row falsely open and causes later sweeps to re-rank fixed work.

## Closure rules

1. If the accepted row is still local and uncommitted, update that row in place:
   set the disposition to `fixed` and replace the note with the resolving
   commit hash plus a short summary. **Change only the `Disposition`, `Date`,
   and `Evidence / note` columns — leave the `Finding` text byte-identical.**
2. If the accepted row is already committed, append a new `fixed` row that
   reuses the **same `ID`** and keeps the **`Finding` text byte-identical** to
   the accepted row (change only `Disposition`, `Date`, and `Evidence / note`).
   This is what makes the supersession deterministic: identical
   `(surface, dimension, object, finding)` keys collapse cleanly in the
   materialized current view (last-writer-wins → `fixed`), so the closure never
   depends on the fragile object-order positional fallback.
3. **`closes #ID` is mandatory** on every `fixed`/`declined`/`grandfathered`
   row that supersedes an accepted row. Reuse the accepted row's ID. It keeps
   the linkage machine-readable in the append-only history shards even when a
   rephrase is unavoidable, and it is the only signal that lets
   `check_ledger_staleness.py` attribute a closure without guessing by row
   order.
4. Cite the ledger ID in the resolving commit message so the closure is
   auditable from git history.

### Why the `Finding` text must not be edited on a flip

The disposition matching key is
`(surface, dimension, object, finding)`. Editing the `Finding` text while
flipping the disposition forks the key: the old `accepted` row and the new
`fixed`/`declined` row no longer collapse, so **both** survive in the current
view sharing one `ID`. That is the duplicate-ID / ambiguous-closure class
flagged by `integrity_warnings()` in `check_ledger_staleness.py`. Record what
changed in the `Evidence / note` column, never by rewording the `Finding`.

## Verification

Run `python3 scripts/check_ledger_staleness.py` after the source change. Then:

- Any remaining `STALE-OPEN` row for the resolved object means the closure
  write-back did not happen correctly.
- Any `data-integrity warning` naming the resolved row (duplicate ID, or a
  positional/object-order closure) means the write-back forked the key or
  omitted `closes #ID` — fix it so the closure is deterministic.
