# Investigate Findings Template

```markdown
# Investigation: [Symptom] — [Date]

**Ticket:** [FDxxxxx if applicable]
**Repos involved:** [repos where relevant code was found]

## Verdict

| Hypothesis | Status | Confidence |
| --- | --- | --- |
| H1: [text] | ✅ CONFIRMED | High |
| H2: [text] | ❌ REJECTED | High |
| H3: [text] | ⚠️ INCONCLUSIVE | — |
| H4: [text] | ❌ REJECTED | Medium |

## Regression Timeline

- **Last known good:** YYYY-MM-DD / version / "unknown"
- **First reported failure:** YYYY-MM-DD / event
- **Recently working?** yes | no | unknown
- **Implications for hypothesis prioritisation:** [1 sentence]

## Root Cause

[1–3 sentences. State which confirmed hypothesis is the actual
cause. If inconclusive, state what data is needed to resolve it.]

**Reconciliation:** [Required if Root Cause is pre-existing or environmental — see reconciliation gate above]

## Evidence

### H1 — CONFIRMED

**File:** `src/codeunit/Cod50741.al:336`

~~~al
if Item."ACAKAU01 Nominal Weight" = 0 then
    exit;  // exits without recalculating Total Kg
~~~

**Why this matters:** [explanation]

### H2 — REJECTED

**Evidence:** `EventSubscribers.codeunit.al:172` only fires on
`OnAfterCopySalesLine`, not during posting. Posting path confirmed
in `Cod50741.al:471`.

## Gaps

- [Anything not verifiable from local code]
- [BC base app behaviour requiring external reference]

## Affected Repositories

| Repo | Role | Fix needed? |
| --- | --- | --- |
| MM_Kembla_Core | Root cause lives here | ✅ Yes |
| MM_Kembla_Price_App | Symptom visible here | ❌ No code change |

## Next Steps

[Exactly one of:]

- Root cause confirmed in this repo →
  `/al-dev-plan [fix description]`
- Fix needed in another repo →
  `/al-dev-handoff [path to target repo]`
- Inconclusive — specific data needed →
  [exact query or check to run]

```
