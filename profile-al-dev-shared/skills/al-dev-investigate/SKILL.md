---
name: al-dev-investigate
description: >-
  Structured root cause investigation for bugs and unexpected
  behaviour. Spawns parallel investigation agents to test
  competing hypotheses, then synthesises confirmed/rejected
  findings to findings file. Use before /al-dev-plan when the
  root cause is unclear. Triggers on: "investigate why", "find
  root cause", "what is causing", "bug not fixed",
  "recurring issue".
argument-hint: "[symptom or bug description]"
---

# Skill: /al-dev-investigate

Root cause investigation — answers "why is this happening?" before
`/al-dev-plan` answers "how do we fix it?".

This skill itself is the shared-profile root-cause framework.
Do not create an ad-hoc implementation hypothesis and jump straight to fixes.
Use the regression timeline, competing-hypothesis, and evidence gates below before recommending any implementation path.

---

## When to Use

| Situation | Use |
| --- | --- |
| Root cause of a bug is unclear | ✅ |
| A previously deployed fix has stopped working | ✅ |
| Multiple competing hypotheses exist | ✅ |
| `/al-dev-plan` was run to find reasons, not solutions | ✅ |
| You need a clear solution to design | ❌ Use `/al-dev-plan` |
| General codebase questions | ❌ Use `/al-dev-explore` |

---

## Implementation

### Step 0 — Target Confirmation

Before acting on any findings file or context document:

1. **Identify targets:**
   - Findings reference: target name/path from findings
   - Your request: target from user request
   - Output path: where investigation output will be written
2. **Validate match:**
   ```
   > **Target check:**
   > - Findings reference: [extracted from findings]
   > - Your request: [extracted from your message]
   > - Output path: [absolute path where work will land]
   >
   > Do these match?
   >
   > **If all align:** Continue to Step 1.
   >
   > **If findings and request disagree:** STOP. Ask the user to confirm whether to:
   > 1. Restart the investigation with clarified requirements, or
   > 2. Proceed with the current scope despite the mismatch
   ```

### Step 1 — Load Context

Read in this order:

1. Latest ticket context (glob):
   `$(ls .dev/*-al-dev-ticket-ticket-context.md 2>/dev/null | sort | tail -1)`
   (if it exists) — symptom, affected data
2. `.dev/project-context.md` (if it exists) — relevant objects,
   established patterns
3. Latest explore findings (glob):
   `$(ls .dev/*-al-dev-explore-findings.md 2>/dev/null | sort | tail -1)`
   (if it exists) — prior exploration

If a ticket is referenced but `ticket-context.md` is missing,
suggest `/al-dev-ticket <id>` first.

Extract from the user's args or ticket:

- **Symptom**: What is the user observing?
  (wrong field value, error, missing data)
- **Conditions**: Under what circumstances?
  (after posting, on Copy Document, for certain items only)
- **Affected data**: Specific records if mentioned
  (order number, item, reference)

**Tool output framing:** If ticket context or findings include output from external tools
(codeburn, lint analyzers, third-party plugins):

- Treat each tool-output claim as a **hypothesis**, not an established finding
- Add each claim to the hypothesis list to test during investigation steps
- Confirm claim vs actual codebase before including it in final findings report
- If tool output contradicts code, flag contradiction and resolve which source is current

---

### Step 2 — Regression Timeline

Before formulating hypotheses, capture the regression timeline.
This is metadata for the investigation and a gate against
"pre-existing" misdiagnosis.

Extract or ask the user for:

- **Last known good:** date/version when this last worked correctly
  (or "unknown" if never confirmed working)
- **First reported failure:** date/event of the first failure report
- **Recently working?** yes / no / unknown

If the user did not provide these and they are not in the ticket
context, ASK before proceeding to Step 2. One combined question is
fine ("When did this last work, and when did it first fail?").

Carry these three captured values forward. They become required
fields in the findings file (Step 5) — alongside one derived field
("Implications for hypothesis prioritisation", which you fill in
during Step 5 synthesis based on the captured timeline). They also
influence hypothesis prioritisation during Step 3:

- If **Recently working = yes**, prioritise change-timeline
  hypotheses (recent deployments, platform updates, IP/cert
  changes, dependency upgrades) over pre-existing-defect hypotheses
- If **Recently working = no**: treat as a never-worked scenario.
  De-prioritise change-timeline hypotheses; focus on design
  defects, configuration gaps, or missing setup.
- If **Recently working = unknown**, treat both hypothesis families
  as equally likely

---

### Step 3 — Formulate Hypotheses

Before spawning agents, list 2–4 initial hypotheses inline.

Each hypothesis must be:

- **Specific**: not "event subscriber issue" but "subscriber exits
  early when Item Nominal Weight = 0"
- **Testable**: a code path or data state must be able to confirm
  or reject it
- **Bounded**: points to a specific codeunit, table, or event

Example hypothesis set for a "Total Kg overstated" bug:

```text
H1: Nominal Weight = 0 on the affected item — subscriber exits
    early without recalculating Total Kg
H2: Copy Document copies stale Total Kg — EventSubscribers fires
    on copy but not on posting
H3: Upgrade tag already applied but data fix not re-run —
    one-time correction did not cover this scenario
H4: Missing Outstanding Quantity filter in GetUninvoiceKg —
    fully-invoiced lines included in aggregation
```text

---

### Step 4 — Spawn Parallel Investigation Agents

> Pattern: `knowledge/explore-subagent-pattern.md` — Steps A–D.
> Hypothesis-testing prompt structure is below; spawn ×2 in parallel.

Route by hypothesis count:
- **1–2 hypotheses:** spawn 1 agent with all hypotheses.
- **3–4 hypotheses:** spawn 2 agents in parallel (H1+H2 → agent 1; H3+H4 → agent 2).
- **5+ hypotheses:** spawn 3 agents, distributing hypotheses evenly.

```text
Spawn an explore agent:
  purpose: Investigate H1 and H2: [brief label]
  prompt: [hypothesis investigation prompt]
  output: confirmed/rejected findings with evidence

Prompt:
  "You are investigating a bug in an AL/Business Central extension.
   Confirm or reject these two hypotheses by reading the code.
   For each hypothesis, find the exact code path that supports or
   contradicts it. Do not propose solutions — only investigate.

   Bug symptom: [SYMPTOM]
   Conditions: [CONDITIONS]

   Project context:
   [paste relevant sections from project-context.md if available]

   HYPOTHESIS H1: [full text]
   Test by reading: [specific files / objects to check]

   HYPOTHESIS H2: [full text]
   Test by reading: [specific files / objects to check]

   For EACH hypothesis report:

   **Output handling:** If your investigation requires running compile,
   build, or test commands, redirect all output to `.dev/investigate-errors.log`
   (use `2>>.dev/investigate-errors.log`). Extract only relevant error summaries
   or findings to report back — do not let verbose compiler output flow to the
   session. If a compilation error is significant to the investigation, include
   the error message but not the full compiler trace.

   VERDICT: CONFIRMED | REJECTED | INCONCLUSIVE
   EVIDENCE: [file path, line number, code snippet]
   REASONING: [1-2 sentences]
   GAPS: [what cannot be verified from local code alone]"
```yaml

**Agent 1:** H1 and H2 with their test targets.
**Agent 2:** H3 and H4 with their test targets.

Both agents run in parallel (single message, two Agent tool calls).

---

Do not present a fix path until the findings file contains at least one confirmed or best-supported hypothesis and the rejected alternatives are named.

### Step 5 — Synthesise Findings

Read both agents' results and write
`.dev/$(date +%Y-%m-%d)-al-dev-investigate-findings.md`. Include the
regression timeline values captured in Step 2 when populating
the findings template.

> **Reconciliation Gate (required if Root Cause is labelled
> "pre-existing" or "environmental"):**
>
> If you are about to write Root Cause as a pre-existing defect or
> environmental cause, you MUST first reconcile with the Regression
> Timeline above:
>
> - If **Recently working = yes**: a pre-existing label is a
>   contradiction. Either (a) the defect was latent and a recent
>   change triggered it — identify the trigger, OR (b) the Recently
>   Working assessment was wrong — explain how. Do NOT submit
>   "pre-existing" without one of these reconciliations.
> - If **Recently working = no**: state the evidence that rules out
>   a recent trigger before accepting pre-existing.
> - If **Recently working = unknown**: state the evidence that rules
>   out a recent trigger before accepting pre-existing.
>
> Write the reconciliation as a paragraph immediately under Root
> Cause, prefixed `**Reconciliation:**`.

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

---

### Step 6 — Present to User

```text
Investigation complete → .dev/YYYY-MM-DD-al-dev-investigate-findings.md

Root cause: [1–2 sentences]

Hypotheses tested: 4
  ✅ Confirmed: H1 — [brief label]
  ❌ Rejected: H2, H4
  ⚠️ Inconclusive: H3 — [what is needed]

Fix required in: [repo name]

Next:
  Fix is in this repo → /al-dev-plan [fix description]
  Fix is in another repo → /al-dev-handoff [path to target repo]
  More data needed → [specific check]
```text

---

## Notes

- Creates date-prefixed `.dev/YYYY-MM-DD-al-dev-investigate-findings.md`
  each run (one file per investigation date)
- If all hypotheses are rejected, formulate 2 new hypotheses and
  repeat from Step 3 — do not give up after one round
- For bugs spanning 2 repos, identify which repo owns the fix and
  suggest `/al-dev-handoff` to migrate context
- When ticket context exists, always read it before formulating
  hypotheses — it often contains the key data point
