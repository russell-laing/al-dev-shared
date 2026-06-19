# Health Backlog Drain — Change Summary

## Problem

The health-audit loop silently accumulated accepted-but-unimplemented findings.
95 rows in `docs/health/dispositions.md` carried `accepted` status with no
corresponding `fixed` row, spanning 2026-06-05 → 2026-06-19.

The root cause: `plan-health-findings` Phase 1 sourced its worklist **only from
the single latest dossier**. It consulted the ledger only to *classify* dossier
findings — never to *discover* open accepted rows. Any accepted finding a lens
didn't happen to re-emit in a later sweep was simply absent from the new dossier,
and therefore never planned.

**Correction to earlier diagnosis:** the report phase does *not* actively
suppress accepted findings — `health_disposition_store.py` maps `accepted` →
`keep`. The leak was upstream, in how the planning skill sourced its worklist.

---

## Changes

### 1. `scripts/health_disposition_store.py` — new `list-open` subcommand

Adds `list_open()` (reusing `materialize_current_view()`) and a `list-open` CLI
subcommand. An `accepted` row in the current view has no later `fixed`/`declined`
superseding it, so this output *is* the genuinely-open backlog.

```bash
python3 scripts/health_disposition_store.py list-open              # → 95 rows
python3 scripts/health_disposition_store.py list-open \
  --surface tooling --dimension design                             # → 6 rows (incl. #932)
```

### 2. `scripts/tests/test_health_disposition_store.py` — `ListOpenTest` class

Four new tests: accepted-only filtering, last-writer-wins exclusion of a
fixed-superseded row, surface/dimension filters, and alternate `--status`.
**11/11 tests pass.**

### 3. `.claude/skills/plan-health-findings/SKILL.md` — `--backlog` mode

Adds an explicit path to plan the open accepted backlog without touching the
default dossier-sourced behaviour:

- `--backlog` Argument Routing entry
- Phase 1 branch: skip dossier location + matcher; run `list-open`; each row's
  `#NNN` id is the Phase 4 close-back ID directly
- Phase 2: per-row staleness baseline (each row's own `date`, not a dossier date)
- Phase 3: rubber-duck edge for backlog rows (no `file:line` citation expected;
  missing-object → skip → surface to user)
- Argument-hint updated

**Default behaviour unchanged.**

### 4. `.claude/skills/record-health-dispositions/SKILL.md` — backlog guard

After collecting disposition decisions, runs `list-open --status accepted`. If
the count is ≥ 10, emits:

> ⚠ N open `accepted` rows (oldest `<date>`) — including rows from earlier
> sweeps the dossier no longer surfaces. Run `/plan-health-findings --backlog`
> to drain the full backlog.

When the guard fires, the loop-state breadcrumb `note` also carries the
`--backlog` recommendation so it survives session boundaries.

### 5. `.claude/skills/plugin-health-discover/SKILL.md` — backlog guard

Identical guard at the discover stage (before a new sweep begins). Appended to
the "Return to caller" step. Informational only; does not block the sweep.

---

## Verification

| Check | Result |
|---|---|
| `list-open` (accepted) | 95 |
| `list-open --status fixed` | 594 |
| `list-open --surface tooling --dimension design` | 6 (incl. #932) |
| Open accepted date span | 2026-06-05 → 2026-06-19 |
| All 11 store tests | pass |
| Forbidden-pattern scan | clean |

5 files modified, uncommitted. No other files touched.
