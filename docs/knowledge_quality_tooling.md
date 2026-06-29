# Knowledge File Quality Report — Tooling Surface

Generated: 2026-06-26 10:10 UTC
Surface: `.claude/knowledge/`
Issues: HIGH: 0 | MEDIUM: 0 | LOW: 13 (all false positives or validator limitations)

---

## Summary

All 13 findings are false positives produced by a validator limitation: the
`validate_knowledge_quality.py` script checks dead-refs by resolving paths
relative to `.claude/knowledge/`, but cannot follow cross-surface references to
`profile-al-dev-shared/knowledge/`. Every referenced file exists in the repo.
No agent guidance is impaired.

There are two root causes:

- **Category A (12 findings):** Tooling knowledge files explicitly reference
  plugin-surface files using full-prefix paths (`profile-al-dev-shared/knowledge/…`)
  or relative paths (`../../profile-al-dev-shared/knowledge/…`). All referenced
  files exist; the validator simply cannot resolve across surfaces.
- **Category B (1 finding):** `knowledge-audit-analysis.md` contains the phrase
  `"Reference knowledge/X.md for examples"` in a schema description. This is
  illustrative text, not a live reference.

---

## HIGH Severity (Blocks Agent Guidance)

_None._

---

## MEDIUM Severity (Incomplete Guidance)

_None._

---

## LOW Severity (Minor/False Positives)

### Category A — Cross-surface references (validator limitation)

**File:** `.claude/knowledge/delegated-scope-pack.md`

- **References:** `profile-al-dev-shared/knowledge/scope-expansion-gate.md` (×2),
  `profile-al-dev-shared/knowledge/background-agent-dispatch.md` (×1)
- **Referencing skills:** `.claude/skills/sync-map-documentation-collect/SKILL.md`
- **Issue:** DEAD-REF — validator cannot resolve plugin-surface paths from
  `.claude/knowledge/`
- **Assessment:** All three referenced files exist at the named paths. References
  appear in a prose intro (line 3–5) and a "Related contracts" footer section —
  informational only, not operational directives. Agent guidance is unimpaired.
- **Fix:** No action needed. Validator limitation acknowledged.

---

**File:** `.claude/knowledge/dispatch-fallback-contract.md`

- **References:** `profile-al-dev-shared/knowledge/workflow-resilience.md` (×1),
  `profile-al-dev-shared/knowledge/background-agent-dispatch.md` (×1)
- **Referencing skills:** `audit-knowledge-quality`, `discover-plugin-health`,
  `fix-knowledge-quality`, `ingest-plugin-friction`, `plan-plugin-findings`,
  `report-plugin-health`, `sync-map-documentation`
- **Issue:** DEAD-REF — validator cannot resolve plugin-surface paths
- **Assessment:** Both files exist. The `workflow-resilience.md` reference appears
  in a "Related contracts" footer (line 47). All operational text in this file is
  self-contained; no agent is instructed to "read that file to continue". Guidance
  is unimpaired.
- **Fix:** No action needed.

---

**File:** `.claude/knowledge/health-discover-aggregation.md`

- **References:** `profile-al-dev-shared/knowledge/lens-invocation-patterns.md` (×2)
- **Referencing skills:** `discover-plugin-health`
- **Issue:** DEAD-REF — validator cannot resolve plugin-surface paths
- **Assessment:** `lens-invocation-patterns.md` exists in the plugin surface. Both
  refs cite it as the authority for per-lens context fields and quality-lens
  dimension rules (lines 47, 65). An agent reading `health-discover-aggregation.md`
  could follow those references using the stated full path. Guidance is intact.
- **Fix:** No action needed.

---

**File:** `.claude/knowledge/health-plan-context-template.md`

- **References:** `profile-al-dev-shared/knowledge/commit-conventions.md` (×1)
- **Referencing skills:** `plan-plugin-findings`
- **Issue:** DEAD-REF — validator cannot resolve plugin-surface paths
- **Assessment:** `commit-conventions.md` exists in the plugin surface. The reference
  (line 45) names the commit-message format spec. The file includes an inline example
  that satisfies the agent's immediate guidance need, so the cross-reference is
  supplemental only.
- **Fix:** No action needed.

---

**File:** `.claude/knowledge/phase-proof-contract.md`

- **References:** `profile-al-dev-shared/knowledge/artifact-contracts.md` (×1),
  `profile-al-dev-shared/knowledge/workflow-resilience.md` (×1)
- **Referencing skills:** `audit-knowledge-quality`, `discover-plugin-health`,
  `fix-knowledge-quality`, `ingest-plugin-friction`, `plan-plugin-findings`,
  `report-plugin-health`, `sync-map-documentation`
- **Issue:** DEAD-REF — validator cannot resolve plugin-surface paths
- **Assessment:** Both files exist. The `artifact-contracts.md` reference (line 9)
  draws a distinction between end-of-run and per-phase proof rules — informational.
  The `workflow-resilience.md` reference (line 47) is in a "Related contracts" footer.
  All operative instructions are self-contained in this file.
- **Fix:** No action needed.

---

**File:** `.claude/knowledge/report-input-gates.md`

- **References:** `profile-al-dev-shared/knowledge/lens-invocation-patterns.md` (×2)
- **Referencing skills:** `report-plugin-health`
- **Issue:** DEAD-REF — validator cannot resolve plugin-surface paths
- **Assessment:** Both references (lines 79–80) name `lens-invocation-patterns.md`
  as the authority for the finding-evidence contract and for quality-lens context
  structures. These are inline operational citations. The cited file exists at
  the stated full path. An agent following `report-input-gates.md` can navigate
  to it correctly.
- **Fix:** No action needed.

---

**File:** `.claude/knowledge/rubber-duck-orchestration.md`

- **Reference:** `../../profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`
- **Referencing skills:** `plan-plugin-findings`
- **Issue:** DEAD-REF — validator does not follow `../../` relative paths across
  surfaces
- **Assessment:** The relative path from `.claude/knowledge/` resolves correctly
  to `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md`, which
  exists. Validator limitation only.
- **Fix:** No action needed.

---

### Category B — Template/example text (false positive)

**File:** `.claude/knowledge/knowledge-audit-analysis.md`

- **Reference:** `knowledge/X.md` (line 68)
- **Issue:** DEAD-REF — validator treats illustrative text as a live path
- **Assessment:** The phrase `"Reference knowledge/X.md for examples"` (line 68)
  is an example within the HIGH severity criteria description. It is not a
  cross-reference; it is illustrating what a severity-HIGH agent message looks
  like. No navigation is implied.
- **Fix:** No action needed. Validator false positive by design.

---

## Fix Recommendations

### High Priority

_No HIGH-severity issues found. No immediate fixes required._

### Medium Priority

_No MEDIUM-severity issues found._

### Low Priority — Validator Enhancement (optional)

The `validate_knowledge_quality.py` dead-ref checker could be taught to
recognise cross-surface references (paths starting with
`profile-al-dev-shared/knowledge/` or resolving to that directory via `../../`)
as valid, preventing the 13 recurring false-positive warnings in future audits.
This is a cosmetic improvement — the current warnings are correctly classified
LOW and do not block any agent guidance.

Similarly, the validator could be taught to skip references embedded in schema
examples (lines containing `"Reference knowledge/`-style quoted paths within
bullet descriptions).

---

## High-Priority Fix Tasks

<!-- auto-generated by /audit-knowledge-quality — consumed by /fix-knowledge-quality -->

```yaml
tasks: []
```

_No HIGH-severity findings — no fix tasks generated._
