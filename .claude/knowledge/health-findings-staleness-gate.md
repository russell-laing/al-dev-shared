# Health Findings Staleness Gate

This document defines the staleness-gate logic applied in Phase 1b of
`plan-health-findings`. A dossier is a point-in-time snapshot; findings are
routinely implemented piecemeal between the audit and the planning step, so any
finding whose subject file changed *after* the dossier was generated is likely
already addressed (or has drifted out from under the finding text).

## Procedure

For each dossier, take its date from the filename (`YYYY-MM-DD-<surface>-health.md`).
For each collected finding, resolve its subject to a file path:

- skill → `profile-al-dev-shared/skills/<name>/SKILL.md` or `.claude/skills/<name>/SKILL.md`
- agent → `profile-al-dev-shared/agents/<name>.md` or `.claude/agents/<name>.md`

Then check whether that file changed since the dossier date:

```bash
# DOSSIER_DATE from the dossier filename; SUBJECT_PATH per finding
git log --since="$DOSSIER_DATE 00:00" --oneline -- "$SUBJECT_PATH"
```

The `--since="$DOSSIER_DATE 00:00"` boundary means any commit on or after 00:00 on the
dossier date is "after" (e.g. for a `2026-06-10` dossier, a commit at `2026-06-10 08:29`
is in scope).

- **Non-empty output** → label the finding **`⚠ possibly stale`** and record the
  commit(s). In Phase 2, rubber-duck it by reading the entire subject file from
  start to finish before checking the claim; expect the claim may no longer
  match (verdict `skip [already implemented]` is common here).
- **Empty output** → the subject is unchanged since the audit; rubber-duck
  normally.

If a finding's subject cannot be resolved to a single file (e.g. a cross-surface
or handoff finding), skip the gate for it and rubber-duck normally.

## Stale-tier handling

After labelling, count the stale ratio and handle by tier. The **stale ratio**
denominator is the count of findings dispatched to Phase 3 rubber-ducking this
run — i.e. the findings remaining after Phase 1 disposition filtering, excluding
any `suppress`/`verify`/skipped findings:

| Stale ratio | Action |
|---|---|
| 100% (all findings) | Advise re-running `/plugin-health-audit`; do not proceed |
| ≥80% | Report ratio; offer (a) re-run audit or (b) proceed with heightened scrutiny; only proceed if user chooses (b) |
| <80% | Proceed; mark stale findings `⚠ possibly stale` in the worklist |
