---
name: review-scripts
description: >-
  Use when reviewing the Python under scripts/ for correctness, data-integrity,
  idempotency, and fail-open-validator bugs. Dispatches parallel per-cluster
  review agents seeded with the repo's recurring bug classes, ranks findings by
  severity, and writes a report to docs/scripts_quality.md. Triggers on: "review
  the scripts", "python quality review", "audit scripts", "check the scripts",
  "scripts quality review", "review scripts/".
argument-hint: "[--cluster <name>] [--fix]"
---

# Review Scripts

## Purpose

`scripts/` is this repo's maintainer tooling: the health disposition ledger,
documentation-map generators, and pre-commit validators. Its bugs are
data-integrity and fail-open bugs, not feature bugs. This skill reproduces a
rigorous parallel quality review on demand and surfaces findings before they
corrupt the ledger or let a broken commit through.

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md` — emit a phase-proof
block at each phase boundary before reporting completion.

## When NOT to Use

- **A diff review of pending changes** — use `/code-review`; this skill audits the
  whole `scripts/` surface, not the working tree.
- **Documentation-map accuracy** — use `/sync-map-documentation`.
- **Knowledge-file quality** — use `/audit-knowledge-quality`.

## Phase 0: Parse Arguments

Read `$ARGUMENTS`:

- `--cluster <name>` → restrict to one cluster (see Phase 2); default is all.
- `--fix` → after reporting, offer gated edits for confirmed findings.

## Phase 1: Load the watch list

Read `../../knowledge/scripts-review-watchlist.md` in full. Every dispatched
agent's prompt MUST embed these six recurring bug classes as an explicit
checklist. Findings that match a watch-list class are ranked one severity tier
higher because they are known-recurring.

## Phase 2: Build the cluster file list

Top-level scripts that are compat shims delegate into `al_dev_tools/`; exclude
them from review (they carry no logic):

```bash
# Shims to EXCLUDE
grep -l "Compatibility wrapper" scripts/*.py 2>/dev/null | sort
```

Group the remaining real-logic files into clusters (skip empty clusters; honor
`--cluster`):

- **ledger-core** — `scripts/al_dev_tools/health/{disposition_*,ledger_*,health_disposition_store,health_benchmark_adapter}.py`
- **health-checks** — `scripts/al_dev_tools/health/{check_*,migrate_*,validate_health_loop_state,select_health_artifacts,split_multilens_findings,assemble_health_findings,precision_gate_fixture,paths}.py`
- **docs-render** — `scripts/al_dev_tools/docs/*.py`
- **shared-utils** — `scripts/al_dev_tools/{io_utils,markdown_frontmatter,reference_contracts,runtime_artifacts,shared_surface_names,companion_surface_contract}.py` + `scripts/_compat_entrypoint.py`
- **validators** — `scripts/validate_*.py`
- **generators** — `scripts/{generate_*,derive_*,health_static_lenses,summarize_superpowers_history,check_health_loop_handoffs}.py`

Print: `Reviewing N files across M clusters (skipping K compat shims)`.

## Phase 3: Dispatch parallel review agents

Dispatch one `general-purpose` agent per non-empty cluster, **concurrently**
(all Agent tool-uses in a single message). Each agent prompt MUST:

1. List its cluster's exact file paths and instruct it to read each in full.
2. Embed the six watch-list bug classes from Phase 1 as a priority checklist.
3. Require every finding to be VERIFIED by tracing the actual code path — no
   speculation — and ranked Critical / High / Medium / Low with `file:line`, a
   one-sentence defect, and a concrete failure scenario (inputs → wrong result).
4. Instruct the agent to return findings only (its final message is the
   deliverable) and to say so briefly when a file is clean.

## Phase 4: Synthesize and write the report

Merge the per-cluster findings, de-duplicate, and rank across the whole surface
(most-severe first). Write `docs/scripts_quality.md`:

```markdown
# Scripts Quality Review

Generated: <today's date>
Files reviewed: N | Clusters: M | Skipped (compat shims): K

## Summary

- Critical: N | High: N | Medium: N | Low: N
- Watch-list matches: N

## Findings (ranked)

### <severity> — <one-line summary>

- **File:** `path:line`
- **Defect:** ...
- **Failure scenario:** ...
- **Watch-list class:** <#N or "—">
```

Verify the report was written:

```bash
ls -la docs/scripts_quality.md
```

## Phase 5: Report and offer fixes

Print a brief severity summary and list the Critical/High findings by file.

If `--fix` (or the user asks), propose one Edit per confirmed finding, most-
severe first, one at a time. Do NOT auto-apply — confirm each. For any fix that
touches a distributed surface, run the neutrality validator before committing.

## Success Criteria

✅ Compat shims excluded; real-logic clusters reviewed
✅ Every finding verified against code with `file:line` + failure scenario
✅ Watch-list classes checked and flagged
✅ Report written to `docs/scripts_quality.md` and verified on disk
✅ Fixes are user-gated, never auto-applied
