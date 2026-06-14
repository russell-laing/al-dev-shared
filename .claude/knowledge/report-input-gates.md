# Report Input Gates

> See `.claude/knowledge/health-disposition-storage-contract.md` for the
> authoritative storage layout. `docs/health/dispositions-history/` is the
> append-only source of truth; `docs/health/dispositions.md` is the generated
> current-state view. Never append rows directly to `docs/health/dispositions.md`.

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
`../../knowledge/health-audit-preconditions.md` (see its
"## Staleness spot-check protocol" section) to every High
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

### Evidence verification (every finding)

The `git log` staleness check above is time-boundary heuristics — it only
catches subjects edited *since* the sweep. It does not catch a finding that was
wrong the moment it was written. Because the discovery stage now requires every
finding to carry a `file:line` + quoted snippet (the **Finding evidence
contract** in `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`),
verify that evidence directly — this is the primary false-positive filter:

For **every** parsed finding, before it enters the dossier:

1. Open the cited `file:line` in the live source.
2. Confirm the quoted snippet still exists at (or near) that location **and**
   that the claimed problem actually holds against the current text.
3. If the quoted evidence is absent, or the claimed condition does not hold,
   drop the finding from all counts and the top-5, and list it under a
   **"Dropped (unverified)"** note at the foot of the dossier (parallel to
   "Stale (dropped)"), with one line per finding: `<object> — <why it did not
   verify>`.

This reads each finding's subject file once. If per-run cost is a concern,
verify High and Medium findings in full (snippet + claim) and verify Low
findings at snippet-existence level only. Record the count of dropped findings
so the filter is auditable, not silent.

---

## 1d — Disposition suppression

**Run the deterministic matcher first.** Before judging matches by hand, run:

```bash
python3 scripts/health_disposition_store.py match \
  --findings docs/health/YYYY-MM-DD-<surface>-findings.md
```

It classifies each finding against the current-view ledger as `suppress`
(matches a declined/grandfathered row), `verify` (matches a fixed row), or
`keep` (no decided match), matching on surface + dimension + object membership +
finding-type with rephrase-tolerant text overlap. The output is a
**high-precision candidate shortlist, not an auto-decision**: confirm each
`suppress`/`verify` candidate against the cited ledger row before acting, and
still scan the `keep` set by hand for matches the script missed (it favours
precision over recall, so heavily-rephrased matches can fall through). Then
apply the rules below to the confirmed set.

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
