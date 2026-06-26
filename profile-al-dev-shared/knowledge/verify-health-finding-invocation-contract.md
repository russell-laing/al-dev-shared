# Verify Health Finding — Invocation Contract

Two distinct operational modes dispatch this agent: **rubber-duck** (pre-plan verification of findings against live code) and **evidence** (post-discover verification of cited claims).

## Mode: rubber-duck

**Purpose:** Verify each finding's claim before including it in an implementation plan. Agent confirms the problem is real, the proposed scope is sound, and there are no blocking dependencies or side effects.

**Inputs:**

- `mode: rubber-duck`
- `findings`: Markdown list of findings as `Type — Subject — proposed change`
- `subject_path`: Absolute path(s) to subject file(s) (skill/agent/knowledge doc being changed)
- `findings_date`: `YYYY-MM-DD` from the dossier filename (staleness baseline)

**Return (compact rubber-duck record):**

```yaml
verdict: proceed | skip | modify
reason: one-line justification
scope_delta: (if modify) specific adjustment to finding scope
```

**Verdict semantics:**

- `proceed`: Claim is substantiated; proposed fix is architecturally sound; no blocking dependencies
- `skip`: Claim is refuted, inaccurate, or already-covered; finding should not enter the plan
- `modify`: Claim is partially substantiated; adjust scope, constraints, or deliverables before planning

---

## Mode: evidence

**Purpose:** Post-discover verification of findings that cite specific file:line evidence. Agent confirms the cited code patterns still exist, the severity claim is accurate, and the finding is not already suppressed or fixed.

**Inputs:**

- `mode: evidence`
- `findings`: Markdown findings with file:line citations (from health dossier)
- `subject_path`: Path(s) to cited file(s)
- `findings_date`: Dossier date for recurrence baseline

**Return (evidence-verification record):**

```yaml
verdict: proceed | skip | verify
citation_status: claim matches live code | code has changed | citation invalid
reason: one-line observation
```

**Verdict semantics:**

- `proceed`: Citation is valid; live code matches claim
- `skip`: Code has been changed or claim was already addressed
- `verify`: Evidence is ambiguous or secondary; requires human judgment

---

## Cross-Mode Responsibility Boundaries

- **Agent responsibility:** Read subject files, verify code patterns, return compact verdict records
- **Caller responsibility (plan-plugin-findings, report-plugin-health):** Interpret verdicts, route findings to tasks or ledger, handle refuted findings
- **Agent contract:** Never echo file contents in return; use verdict + reason. Return one record per dispatch.
