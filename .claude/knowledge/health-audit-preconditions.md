# Health Audit Preconditions

> Storage contract: see `.claude/knowledge/health-disposition-storage-contract.md` for the canonical artifact roles, source-of-truth event store, and generated read views.

Shared precondition and filtering rules for the health-audit loop. Referenced by
`/discover-plugin-health` (cadence + stale-open guards) and
`/report-plugin-health` (staleness spot-check + disposition suppression).
Canonical filter vocabulary lives in `health-filter-contract.md`.

## Disposition coverage criterion (cadence guard)

A prior dossier counts as **dispositioned** when every *actionable* finding in it
has a disposition event in the JSONL store (`docs/health/dispositions-events/`) —
that is, an event whose disposition is `accepted`, `declined`, `grandfathered`,
or `fixed`. Read `docs/health/dispositions-index.json` for a quick count check,
then `docs/health/dispositions-open.md` for the open accepted list. Non-actionable
lens lines (fix field states no action required) do not need an event.

- If coverage exists for the prior dossier, proceed.
- If actionable findings from the prior dossier have no ledger row, they are
  undispositioned: stop and route the user to `/record-plugin-dispositions`.

## Stale-open accepted rows

An accepted row is **stale-open** when its subject file changed in git *after*
the row date — the fix may already be implemented but the row was never flipped
to `fixed`. Detect with `scripts/check_ledger_staleness.py` (the pre-commit gate
runs it in `--staged` mode). Verify against the live file before trusting any
stale-open finding; flip resolved rows to `fixed`.

## Staleness spot-check protocol

For a finding whose subject file changed *after* the dossier date, re-verify
before ranking or planning:

```bash
# DOSSIER_DATE from the dossier filename (YYYY-MM-DD-<surface>-health.md)
git log --since="$DOSSIER_DATE 00:00" --oneline -- "$SUBJECT_PATH"
```

The `00:00` boundary means any commit on or after midnight of the dossier date
counts as "after" (e.g. for a `2026-06-10` dossier, a commit at
`2026-06-10 08:29` is in scope). Non-empty output → read the subject file from
start to finish and re-check the claim; expect it may already be implemented.

## Phase 0 orchestration contract (for `/discover-plugin-health`)

This section defines the complete pre-run orchestration that `/discover-plugin-health`
executes in Phase 0 before dispatching any lenses.

**Inputs:** `--surface` (plugin | tooling | both), `--dimension`, `--resume` flag.

**`--resume` exemption:** Skip all Phase 0 checks when `--resume` is present.
Resuming an interrupted sweep is not a new sweep — the cadence guard and
stale-open check do not apply.

**Dossier selection:** For each requested surface, locate the most recent dossier:

```bash
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind health \
  --surface <surface>
```

**Disposition-coverage test:** If a dossier exists, check whether its actionable
findings have disposition coverage in the JSONL event store per the
*Disposition coverage criterion* section above. Read
`docs/health/dispositions-index.json` for a quick count check. A single recent
event is not enough — every actionable finding needs its own event.

**Warning branch (undispositioned dossier):** If the ledger is absent or coverage
is incomplete, print this warning as plain assistant text and ask the binary
confirmation inline — do **not** invoke a structured question tool (e.g.
`AskUserQuestion`) for this single yes/no; a malformed structured call (missing
`questions`) has stalled this gate before. End the message with the literal
prompt `Proceed with the sweep anyway? (yes / no)` and wait for the reply:

```text
The latest <surface> dossier (<date>) has no recorded dispositions.
A new sweep will largely re-discover its open findings. Record
accept/decline/fixed rows via /record-plugin-dispositions first, or
confirm to sweep anyway.

Proceed with the sweep anyway? (yes / no)
```

**User override and stop path:**

- Disposition coverage exists and is dated on or after the dossier date → proceed
  to the stale-open check.
- User replies `yes` (override) → proceed to Phase 1.
- User declines, or gives no clear confirmation → stop. Report "Sweep not
  dispatched — record dispositions via `/record-plugin-dispositions` and re-run."
  Do not dispatch any lens.

**Stale-open reporting:** After passing (or skipping) the disposition-coverage test,
run the staleness check:

```bash
python3 scripts/check_ledger_staleness.py
```

For each `STALE-OPEN` row, report before dispatch: "Row `<object>` accepted
`<row-date>` — object changed since (`<commit>`); possibly already implemented.
Verify and flip the ledger row before sweeping, or the sweep may re-rank a fixed
item." This check warns only; it never blocks the sweep on its own.

## Disposition suppression rules

When filtering a findings set against the ledger (match on object + issue
essence, rephrase-tolerant):

- **`accepted`** → keep (primary planning/ranking input).
- **`declined` / `grandfathered`** → drop entirely; closed decisions, not
  re-litigated. Revisiting one requires editing the ledger row first.
- **`fixed`** → if the lens has re-flagged the same issue, treat it as suspect:
  verify against the live subject file. If the claim no longer holds, drop it
  under "Stale (dropped)"; if it has genuinely regressed, keep it and note
  "regressed — previously fixed in `<commit>`". This suspect rule applies only
  to `fixed` rows; other dispositions follow their own rule above.
