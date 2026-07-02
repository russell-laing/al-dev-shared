---
name: audit-disposition-ledger
description: >-
  Use when you suspect the health disposition ledger is corrupted, forked, or
  mis-read; after any rename or path change under docs/health/ or paths.py;
  when disposition counts look implausibly low or high; or when a skill/knowledge
  file may reference a renamed or deleted ledger artifact. Read-only integrity
  audit of the JSONL event store, its generated views, and the file references
  that point at them.
workflow:
  stage: derive
  invoked-by: user
  repeatable: true
  inputs:
    - docs/health/dispositions_events/
    - .claude/
    - profile-al-dev-shared/
  outputs: []   # console-only audit; prints findings, writes no artifact
  next: []
---

# Skill: /audit-disposition-ledger

Read-only integrity audit of the disposition ledger. It never writes, edits, or
regenerates the ledger — it only runs deterministic checks and reports findings.
Fixing anything it surfaces is left to the user's normal flow.

Background on why this class of bug matters:
`.claude/knowledge/health-disposition-storage-contract.md` and the fork incident
recorded in the store's own history.

## When to use

- After any rename, move, or `paths.py` edit touching `docs/health/dispositions*`.
- Disposition counts look implausibly low/high, or the ledger "went quiet".
- A skill, knowledge, or agent file may point at a renamed/deleted ledger file.
- Routine spot-check before trusting `/plan-plugin-findings --backlog`.

**When NOT to use:** to *change* the ledger (append/close/regenerate) — that is
`/record-plugin-dispositions` and `scripts/health_disposition_store.py`.

## Phases

Run each phase in order. Every phase is a single deterministic command; report
its output verbatim and classify severity before moving on.

### Phase 0 — Path-drift gate (highest value)

```bash
python3 scripts/check_ledger_path_drift.py
```

Asserts every canonical path in `paths.py` resolves on disk. A failure here is
the fork signature (paths.py resolving to a location the real data left). Exit 1
= **CRITICAL** — stop and report; downstream phases may read the wrong tree.

### Phase 1 — Event-store data integrity

```bash
python3 scripts/check_disposition_store_consistency.py
```

Verifies every `closes_event_ids` resolves and no event is unparseable. Exit 1 =
**HIGH** (dangling close-back reference or corrupt event line).

### Phase 2 — Store-vs-view drift

```bash
python3 scripts/check_view_drift.py
```

Re-derives the four generated views (`dispositions_open.md`,
`dispositions_current.md`, `dispositions.md`, `dispositions_index.json`) in
memory from the JSONL event store and compares them to the on-disk files. Exit 1
= **HIGH** — a view no longer matches the store. This is the only phase that
catches a view that was hand-edited or a commit that appended/closed events
without running `regenerate` (e.g. a finding "closed" by deleting its
`dispositions_open.md` row while the store still holds it as open-accepted).
Phases 0 and 1 pass on that state because the JSONL store stays internally
consistent — the drift is store-vs-view, which only this phase compares. The fix
is always `python3 scripts/health_disposition_store.py regenerate` (a store
mutation — out of this read-only skill's scope; hand off to the user's commit
flow).

### Phase 3 — Broken ledger references

Scan the surfaces for references to renamed/deleted ledger artifacts. The
`--match dispositions` filter scopes output to the ledger class (the broader
documentation-reference backlog is out of scope for this skill):

```bash
for d in .claude/knowledge .claude/skills .claude/agents profile-al-dev-shared; do
  python3 scripts/validate_reference_integrity.py --path "$d" --match dispositions
done
```

`reference-legacy-alias` on a ledger path (e.g. a resurfaced
`dispositions-open.md`) or `reference-dead-path` to a `docs/health/dispositions*`
file = **CRITICAL** — a silent-failing Read that disables whatever gate the
reference feeds.

To sweep every reference on a surface (not just ledger ones), drop `--match` —
expect unrelated pre-existing findings that are out of scope here.

### Phase 4 — Report

Summarize findings severity-ranked (CRITICAL → HIGH → MEDIUM), each with its
file/path and the exact command that surfaced it. If everything passes, say so
plainly and note the verified event count from Phase 1.

## Quick reference

| Check | Command | Fail severity |
|---|---|---|
| Path drift (fork) | `check_ledger_path_drift.py` | CRITICAL |
| Store consistency | `check_disposition_store_consistency.py` | HIGH |
| Store-vs-view drift | `check_view_drift.py` | HIGH |
| Broken references | `validate_reference_integrity.py --path <dir>` | CRITICAL / MEDIUM |

Phase 0 and the Phase 3 reference scan on staged surface markdown also run
automatically in `.githooks/pre-commit` (drift blocking; reference scan as a
WARN), so routine drift is caught at commit time — this skill is the on-demand
deep audit. `check_view_drift.py` is a candidate for the same hook: it exits 1 on
any store-vs-view mismatch, so wiring it into the commit gate would block a
stale-view commit (the `regenerate`-was-skipped case) before it lands.

## Common mistakes

- **Treating a low count as data loss.** Suspect a path/store fork first (Phase 0),
  not deletion — the events are usually intact under a differently-named tree.
- **Editing the ledger from here.** This skill is read-only; route fixes through
  `/record-plugin-dispositions` or a deliberate `paths.py`/reference correction.
- **Skipping Phase 0 when Phase 1 passes.** Consistency can pass on a *forked*
  store that is internally coherent but detached from the canonical path.
- **Trusting a green Phase 1 as "views are correct".** Store consistency (Phase 1)
  only checks the JSONL store's internal integrity. A view can silently disagree
  with a consistent store — e.g. a row deleted from `dispositions_open.md` to
  "close" a finding without a `fixed` event, or a commit that skipped
  `regenerate`. Phase 2 is what catches that; run it before trusting any open
  count or `/plan-plugin-findings --backlog`.
