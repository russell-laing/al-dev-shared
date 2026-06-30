---
name: investigate
description: >-
  Structured root cause investigation for bugs and unexpected
  behaviour. Spawns parallel investigation agents to test
  competing hypotheses, then synthesises confirmed/rejected
  findings to findings file. Use before /plan when the
  root cause is unclear. Triggers on: "investigate why", "find
  root cause", "what is causing", "bug not fixed",
  "recurring issue".
argument-hint: "[symptom or bug description]"
---

# Skill: /investigate

Root cause investigation — answers "why is this happening?" before
`/plan` answers "how do we fix it?".

This skill itself is the shared-profile root-cause framework.
Do not create an ad-hoc implementation hypothesis and jump straight to fixes.
Use the regression timeline, competing-hypothesis, and evidence gates below before recommending any implementation path.

## Artifact Contract

This skill is governed by `knowledge/artifact-contracts.md`.

Do not claim the investigation is complete or ready for handoff until the success evidence named in `knowledge/artifact-contracts.md` for this skill has been produced and read in the current run.

---

## When to Use

| Situation | Use |
| --- | --- |
| Root cause of a bug is unclear | ✅ |
| A previously deployed fix has stopped working | ✅ |
| Multiple competing hypotheses exist | ✅ |
| `/plan` was run to find reasons, not solutions | ✅ |
| You need a clear solution to design | ❌ Use `/plan` |
| General codebase questions | ❌ Use `/explore` |

---

## Implementation

### Step 0 — Target Confirmation

Before acting on any findings file or context document, apply **Target
Confirmation (Step 0)** from
`knowledge/verification-and-planning.md`.

For `/investigate`, use:

- **Findings reference** — the target described in the prior findings or
  ticket context
- **User request** — the symptom or subsystem named in the user's
  request
- **Output path** — the investigation findings artifact that will be
  written for this run

If the findings reference and user request disagree, stop and ask the
user whether to restart with clarified requirements or proceed with the
current scope despite the mismatch.

### Step 1 — Load Context

Read in this order:

1. Latest ticket context (glob):
   `$(ls .dev/*-ticket-ticket-context.md 2>/dev/null | sort | tail -1)`
   (if it exists) — symptom, affected data
2. `.dev/project-context.md` (if it exists) — relevant objects,
   established patterns
3. Latest explore findings (glob):
   `$(ls .dev/*-explore-findings.md 2>/dev/null | sort | tail -1)`
   (if it exists) — prior exploration

If a ticket is referenced but no `.dev/*-ticket-ticket-context.md`
file exists, suggest `/ticket <id>` first.

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

- **Last known good:** date/version when the behavior was last confirmed
  working as intended by the user or in production
  (or "unknown" if this was never confirmed working)
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

Before spawning agents, list 2–4 initial hypotheses inline in your response to the user.

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
```

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
```

**Agent 1:** H1 and H2 with their test targets.
**Agent 2:** H3 and H4 with their test targets.

Both agents run in parallel (single message, two Agent tool calls).

---

Do not present a fix path until the findings file contains at least one confirmed or best-supported hypothesis and the rejected alternatives are named.

> best-supported = the hypothesis with the most corroborating code-line evidence
> and the fewest contradictions.

### Step 5 — Synthesise Findings

Read both agents' results and write
`.dev/$(date +%Y-%m-%d)-investigate-findings.md`. Include the
regression timeline values captured in Step 2 when populating
the findings template.

> **Write guard:** if a findings file already exists at this path from a prior
> run, Read it before overwriting (an unread existing file fails the write); a
> brand-new file needs no prior Read. After writing, confirm with `ls -la` and
> `wc -l`. See `knowledge/workflow-resilience.md` Write Protocol.
>
> **Reconciliation Gate (required if Root Cause is labelled
> "pre-existing" or "environmental"):**
>
> Before writing a "pre-existing" or "environmental" Root Cause,
> apply the timeline prioritisation rules from Step 2 (Recently working
> = yes / no / unknown) to verify the label is consistent with the
> captured timeline values. If the timeline contradicts the label,
> either revise the Root Cause or document how you reconciled the
> contradiction before proceeding.
>
> Write the reconciliation as a paragraph immediately under Root
> Cause, prefixed `**Reconciliation:**`.

Produce the findings using the structure in
`knowledge/investigate-findings-template.md` (read it before writing).

---

### Step 6 — Present to User

```text
Investigation complete → .dev/YYYY-MM-DD-investigate-findings.md

Root cause: [1–2 sentences]

Hypotheses tested: 4
  ✅ Confirmed: H1 — [brief label]
  ❌ Rejected: H2, H4
  ⚠️ Inconclusive: H3 — [what is needed]

Fix required in: [repo name]

Next:
  Trivial, single-file fix → /fix [fix description] (loads these findings)
  Fix is in this repo → /plan [fix description]
  Fix is in another repo → /handoff [path to target repo]
  More data needed → [specific check]
```

---

## Notes

- Creates date-prefixed `.dev/YYYY-MM-DD-investigate-findings.md`
  each run (one file per investigation date)
- If all hypotheses are rejected, formulate 2 new hypotheses and
  repeat from Step 3 — do not give up after one round
- For bugs spanning 2 repos, identify which repo owns the fix and
  suggest `/handoff` to migrate context
- When ticket context exists, always read it before formulating
  hypotheses — it often contains the key data point
