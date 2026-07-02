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

## Phase 0: Set Up Isolated Worktree

**REQUIRED SUB-SKILL:** Use superpowers:using-git-worktrees before any other
phase. Every artifact this skill produces — the report written in Phase 5
(`docs/scripts_quality.md`) and any `--fix` edits applied in Phase 6 — happens
inside that isolated worktree, never directly against whatever the caller
already has checked out. `scripts/` has no build step, so Step 2/3 of that
skill (dependency install, baseline tests) can report "N/A — no package
manifest" and proceed straight to Phase 1.

## Phase 1: Parse Arguments

Read `$ARGUMENTS`:

- `--cluster <name>` → restrict to one cluster (see Phase 3); default is all.
- `--fix` → after reporting, offer gated edits for confirmed findings.

## Phase 2: Load the watch list

Read `../../knowledge/scripts-review-watchlist.md` in full. Every dispatched
agent's prompt MUST embed these six recurring bug classes as an explicit
checklist. Findings that match a watch-list class are ranked one severity tier
higher because they are known-recurring.

## Phase 3: Build the cluster file list

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
- **shared-utils** — `scripts/al_dev_tools/{io_utils,markdown_frontmatter,reference_contracts,runtime_artifacts,shared_surface_names,companion_surface_contract,git_utils}.py`, `scripts/{_compat_entrypoint,_entrypoint_bootstrap}.py`, and every package `__init__.py` (`scripts/__init__.py`, `scripts/al_dev_tools/__init__.py`, `scripts/al_dev_tools/health/__init__.py`, `scripts/al_dev_tools/docs/__init__.py`) — the last two carry real lazy-import `__all__` lists, not boilerplate
- **validators** — `scripts/validate_*.py`
- **generators** — `scripts/{generate_*,derive_*,health_static_lenses,summarize_superpowers_history,check_health_loop_handoffs}.py`
- **tests** — `scripts/tests/*.py` + `scripts/test_validator_false_positives.py`

**Completeness check (required):** a file that matches no cluster and isn't a
shim silently skips review every time this skill runs — the exact fail-open
failure mode this skill exists to catch elsewhere. Verify the six-cluster set
above plus the shim exclusion covers every file before dispatching:

```bash
covered=$(mktemp)
{
  grep -l "Compatibility wrapper" scripts/*.py 2>/dev/null
  find scripts/al_dev_tools/health -maxdepth 1 \( -name "disposition_*.py" -o -name "ledger_*.py" -o -name "health_disposition_store.py" -o -name "health_benchmark_adapter.py" \)
  find scripts/al_dev_tools/health -maxdepth 1 \( -name "check_*.py" -o -name "migrate_*.py" -o -name "validate_health_loop_state.py" -o -name "select_health_artifacts.py" -o -name "split_multilens_findings.py" -o -name "assemble_health_findings.py" -o -name "precision_gate_fixture.py" -o -name "paths.py" \)
  find scripts/al_dev_tools/docs -maxdepth 1 -name "*.py"
  find scripts/al_dev_tools -maxdepth 1 \( -name "io_utils.py" -o -name "markdown_frontmatter.py" -o -name "reference_contracts.py" -o -name "runtime_artifacts.py" -o -name "shared_surface_names.py" -o -name "companion_surface_contract.py" -o -name "git_utils.py" -o -name "__init__.py" \)
  find scripts -maxdepth 1 \( -name "_compat_entrypoint.py" -o -name "_entrypoint_bootstrap.py" -o -name "__init__.py" \)
  find scripts/al_dev_tools/health -maxdepth 1 -name "__init__.py"
  find scripts -maxdepth 1 -name "validate_*.py"
  find scripts -maxdepth 1 \( -name "generate_*.py" -o -name "derive_*.py" -o -name "health_static_lenses.py" -o -name "summarize_superpowers_history.py" -o -name "check_health_loop_handoffs.py" \)
  find scripts/tests -maxdepth 1 -name "*.py"
  find scripts -maxdepth 1 -name "test_validator_false_positives.py"
} | sort -u > "$covered"
comm -23 <(find scripts -name "*.py" | sort -u) "$covered"
rm -f "$covered"
```

Do NOT pipe the comparison through nested process substitutions on both sides
of `comm` — it produced spurious non-empty output in testing. Write the
covered set to a file first, as above. Any line printed is an uncategorized
file; add it to the nearest cluster by directory before dispatching — do not
proceed with a known gap.

Print: `Reviewing N files across M clusters (skipping K compat shims)`.

## Phase 4: Dispatch parallel review agents

Dispatch one `general-purpose` agent per non-empty cluster, **concurrently**
(all Agent tool-uses in a single message). Each agent prompt MUST:

1. List its cluster's exact file paths and instruct it to read each in full.
2. Embed the six watch-list bug classes from Phase 2 as a priority checklist.
3. Require every finding to be VERIFIED by tracing the actual code path — no
   speculation — and ranked Critical / High / Medium / Low with `file:line`, a
   one-sentence defect, and a concrete failure scenario (inputs → wrong result).
4. Instruct the agent to return findings only (its final message is the
   deliverable) and to say so briefly when a file is clean.

## Phase 5: Synthesize and write the report

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

## Phase 6: Report and offer fixes

Print a brief severity summary and list the Critical/High findings by file.

If `--fix` (or the user asks), propose one Edit per confirmed finding, most-
severe first, one at a time. Do NOT auto-apply — confirm each. If a fix
touches a generator or validator that writes into `profile-al-dev-shared/`
(e.g. `generate_agent_projections.py`, `validate_harness_neutrality.py`
itself), run `python3 scripts/validate_harness_neutrality.py
profile-al-dev-shared` before committing — the fix could change generated
output in a way that reintroduces a harness-specific token.

## Phase 7: Integrate worktree changes

**REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch to
decide how the worktree's changes reach the caller's branch — merge, PR, or
discard. Do this even when `--fix` was not passed: the Phase 5 report is
itself a real file change and must not be stranded in an orphaned worktree.

## Success Criteria

✅ Work performed in an isolated worktree (Phase 0), integrated at the end (Phase 7)
✅ Compat shims excluded; real-logic clusters reviewed
✅ Cluster completeness verified — no file silently skipped review
✅ Every finding verified against code with `file:line` + failure scenario
✅ Watch-list classes checked and flagged
✅ Report written to `docs/scripts_quality.md` and verified on disk
✅ Fixes are user-gated, never auto-applied
