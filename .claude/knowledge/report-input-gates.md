# Report Input Gates

Operative procedures for the `/plugin-health-report` Phase 1b–1d filter stages.
These rules are canonical; the SKILL.md sub-sections point here.

---

## 1b — Recurrence annotation

Locate the previous findings file for the same surface:

```bash
python3 scripts/select_health_artifacts.py \
  --directory docs/health \
  --kind findings \
  --surface <surface> \
  --offset 1
```

If none exists, skip (every finding is new). Otherwise, for each parsed finding,
check whether the same object with substantially the same issue appears in the
previous findings file (match on substance, not wording).

For each repeat:

- Annotate the finding line in the dossier with `(open since YYYY-MM-DD)`.
  Carry the **earliest** known date forward — if the prior dossier already
  dated the finding, reuse that date rather than resetting it.
- If the severity differs from the prior sweep with no change to the subject
  file, append `(was <severity> on <date>)` — severity churn is signal about
  the lens, not about progress.

Recurring findings stay in the dossier and in the severity counts (they are
still open work), but the Summary must split the totals: new vs recurring.

---

## 1c — Staleness spot-check

Apply the **staleness spot-check protocol** from
`../../knowledge/health-audit-preconditions.md` (lines 120–136) to every High
finding and every top-5 candidate before ranking.

Resolve the subject to its file path (skill →
`profile-al-dev-shared/skills/<name>/SKILL.md` or `.claude/skills/<name>/SKILL.md`;
agent → the matching `agents/<name>.md`), then run the protocol's `git log --since`
check, supplying `FINDINGS_DATE` (from the findings-file name) in place of the
protocol's generic `DOSSIER_DATE` boundary — and, for recurring findings, again
with `PRIOR_DATE` from Phase 1b, since a repeat whose subject changed between
sweeps may be a lens re-issuing a complaint against already-fixed text.
Label any whose subject changed `⚠ possibly stale`.

A labelled finding may enter the top 5 only after reading the live subject file
and confirming the claim still holds; record the spot-check
("verified against live file <date>") next to the action. If the claim no longer
holds, drop the finding from counts and list it under a "Stale (dropped)" note
instead.

---

## 1d — Disposition suppression

Read `docs/health/dispositions.md` (skip if absent). Match each parsed finding
against ledger rows by object + issue essence, then apply the
**disposition suppression rules** from
`../../knowledge/health-audit-preconditions.md`:

- **`declined` / `grandfathered`** → suppress (exclude from severity counts,
  dimension grouping, and top-5); list one line each under a
  "Dispositioned (suppressed)" note at the foot of the dossier.
- **`fixed`** → treat a re-flagged finding as suspect and verify it against the
  live subject file (Phase 1c spot-check); drop it under "Stale (dropped)" if
  the claim no longer holds, or keep it with a "regressed — previously fixed in
  [commit]" note if it genuinely regressed.
- **`accepted`** → keep, annotated "(accepted YYYY-MM-DD — awaiting
  implementation)".
