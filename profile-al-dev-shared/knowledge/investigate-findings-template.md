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

### Example A: Recently discovered regression (Recently working = yes)

**Timeline:**
- Feature working on **2026-05-15** (confirmed in v2.4.1 QA)
- Feature broken on **2026-06-02** (first reported by customer)
- **Recently working?** yes
- **Investigation focus:** Changes between 2026-05-15 and 2026-06-02 — use blame-driven hypothesis prioritization. Git log and changelogs in that window will reveal commits, config changes, or dependency updates likely responsible. Start with "what changed?" before considering design flaws.

### Example B: Long-standing defect (Recently working = no)

**Timeline:**
- Last known good: unknown (feature may never have worked reliably)
- First reported failure: 2026-03-10 (initial discovery date)
- **Recently working?** no
- **Investigation focus:** Feature design review and stress-test hypotheses. No recent change to blame; the issue is likely a pre-existing design limitation, corner case, or environmental constraint that was only uncovered under specific load or edge-case input. Prioritize hypothesis families around architectural assumptions, boundary conditions, and integration contracts.

### Decision Gate

This section is a critical gate for hypothesis prioritization — not decorative metadata. The value of "Recently working?" determines which hypothesis families to investigate first:

- **Recently working = yes** → Blame-driven hypotheses dominate. Investigate what changed (code commits, config updates, dependency upgrades) in the timeline window. See `/al-dev-investigate` skill, Step 2 (lines 100–131) for how timeline gates hypothesis prioritization logic.
- **Recently working = no** → Design and pre-existing-defect hypotheses dominate. Investigate architectural assumptions, boundary conditions, and integration contracts that may have always been problematic but were only exposed under specific conditions.

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
