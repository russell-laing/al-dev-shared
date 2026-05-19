# Tighten Investigation / Fix Loop — Design Spec

**Date:** 2026-05-18
**Status:** Approved (design); pending implementation plan
**Repo:** `al-dev-shared`

## Background

Usage data from the 2026-05-18 insights report (315 sessions, 2026-04-17 to 2026-05-18) surfaced three recurring friction patterns that originate inside three skills owned by this repo:

1. **Confident "pre-existing" conclusions during investigations.** Most prominent case: a GoSweetSpot 400 error was diagnosed as pre-existing when the affected orders had been working — re-investigation found a BC outbound-IP regression. The user had to push back to force the redirect. The current `al-dev-investigate` skill does not require a regression timeline, so "pre-existing" can be claimed without reconciliation.
2. **Scope creep during fixes.** A BC 28 compile-fix session expanded into hook script patching, AL0432 deprecation sweeps, and ruleset modifications — none of which were in the original plan. The current `al-dev-fix` and `al-dev-develop` skills do not require any scope-vs-plan diff before edits or commits.
3. **Write tool calls that silently fail to persist.** A cross-repo handoff session had Claude claim files were created via Write when they did not actually exist on disk. The user noticed and Claude recreated them via Bash. No project-wide rule currently requires post-Write verification.

This spec addresses all three with surgical edits to four files in `al-dev-shared` plus one project-root rule. Medium weight — every change produces an inspectable written artefact or a structured checkpoint, not just a prompt nudge. No new skills, no new agents, no new validator scripts, no harness coupling.

Out of scope:

- Test-driven investigation loop (deferred to a separate spec)
- Commit-count guard in `al-dev-commit` (small isolated change to do separately)
- BC version / terminology rules from the insights report (those belong in user app projects, not this plugin marketplace)
- Hooks or harness-level changes

---

## Architecture

Five file edits across one repo. All changes additive (insert new sections / bullets) — no section rewrites.

| File | Change | Suggestion |
|---|---|---|
| `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md` | New Step 1.5 (Regression Timeline) + new findings-template section in Step 4 + conditional reconciliation gate when Root Cause is labelled "pre-existing" / "environmental" | A |
| `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` | New pre-commit scope diff checkpoint immediately before the commit step | B |
| `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` | New mid-flight Scope Expansion Gate behavioural rule, also propagated into dispatched developer agent prompts | B |
| `CLAUDE.md` | New "Write-Persistence Verification" subsection under existing "File Editing Safety" section | C |
| `profile-al-dev-shared/knowledge/verification-and-planning.md` | One-line cross-reference to the Write-Persistence rule in `CLAUDE.md` | C |

Files NOT touched: agent prompts (agents inherit through dispatch prompts), `marketplace.json` (no new skills), other knowledge files.

---

## Suggestion A — `al-dev-investigate` regression-timeline gate

### Problem

The skill currently jumps from context loading (Step 1) into hypothesis formulation (Step 2) with no timeline grounding. "Pre-existing" or "environmental" verdicts can be reached in Step 4 without ever checking whether the symptom is in fact a regression.

### Solution

Three coordinated additions to the existing skill.

#### A1 — New Step 1.5: Regression Timeline

Inserted between Step 1 (Load Context) and Step 2 (Formulate Hypotheses):

```markdown
### Step 1.5 — Regression Timeline

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
fields in the findings file (Step 4) — alongside one derived field
("Implications for hypothesis prioritisation", which you fill in
during Step 4 synthesis based on the captured timeline). They also
influence hypothesis prioritisation during Step 2:

- If **Recently working = yes**, prioritise change-timeline
  hypotheses (recent deployments, platform updates, IP/cert
  changes, dependency upgrades) over pre-existing-defect hypotheses
- If **Recently working = unknown**, treat both hypothesis families
  as equally likely
```

#### A2 — Required `## Regression Timeline` section in the Step 4 findings template

Inserted between the existing `## Verdict` and `## Root Cause` blocks of the findings file template:

```markdown
## Regression Timeline

- **Last known good:** YYYY-MM-DD / version / "unknown"
- **First reported failure:** YYYY-MM-DD / event
- **Recently working?** yes | no | unknown
- **Implications for hypothesis prioritisation:** [1 sentence]
```

#### A3 — Conditional reconciliation gate in Step 4 — Root Cause block

Added as a required sub-step when the Root Cause statement contains the words "pre-existing", "always", "never worked", "environmental", or "unrelated change":

```markdown
**Pre-existing claim reconciliation (required if Root Cause is
labelled "pre-existing" or "environmental"):**

If you are about to write Root Cause as a pre-existing defect or
environmental cause, you MUST first reconcile with the Regression
Timeline above:

- If **Recently working = yes**: a pre-existing label is a
  contradiction. Either (a) the defect was latent and a recent
  change triggered it — identify the trigger, OR (b) the Recently
  Working assessment was wrong — explain how. Do NOT submit
  "pre-existing" without one of these reconciliations.
- If **Recently working = no/unknown**: state the evidence that
  rules out a recent trigger before accepting pre-existing.

Write the reconciliation as a paragraph immediately under Root
Cause, prefixed `**Reconciliation:**`.
```

### Why the three changes form one unit

- A1 captures the data (cheap, helps every investigation regardless of conclusion shape)
- A2 forces the data into the inspectable artefact (medium-weight written gate)
- A3 fires the actual reconciliation guard only when the failure pattern matches (low friction for unrelated investigations)

---

## Suggestion B — Scope-lock in `al-dev-fix` and `al-dev-develop`

### Problem

Two different scope-creep failure modes:

- `al-dev-fix` (lightweight, fast-iteration) bundles unrelated fixes into the final commit because there is no final-diff inspection.
- `al-dev-develop` (multi-task, multi-agent) silently expands edits mid-flight because dispatched developer agents are not constrained against out-of-plan changes.

Two different gates, matched to each skill's design intent.

### Solution B1 — `al-dev-fix` pre-commit scope diff checkpoint

Added as a new step immediately before the existing commit step. Single inspection point — preserves the skill's no-mid-flight-friction identity.

```markdown
### Step N — Pre-commit Scope Check

Before committing the fix, list every file in `git status` and
classify each against the original symptom:

~~~text
**Scope diff:**

In scope (directly fixes the reported symptom):
- path/to/file1.al — [one-line reason]
- path/to/file2.al — [one-line reason]

Out of scope (encountered while fixing, not in original request):
- path/to/extra.al — [what was changed and why]
- path/to/ruleset.json — [what was changed and why]
~~~

**Decision rule:**

- If "Out of scope" is empty → commit.
- If "Out of scope" has entries → STOP. Present the list to the
  user and ask: "These are outside the original fix. Keep, revert,
  or split into a separate commit?" Wait for per-item decisions
  before committing.

Rationale: this is the smallest possible gate that catches the
"AL0432 sweep bundled in" failure mode without slowing down the
common case (clean, focused fix).
```

### Solution B2 — `al-dev-develop` mid-flight Scope Expansion Gate

Added as a behavioural rule near the top of the skill, then referenced again wherever the skill dispatches developer agents. Trigger-style — fires only when Claude is about to act outside the approved plan.

```markdown
### Scope Expansion Gate

While executing this skill, BEFORE you (or any dispatched
developer agent) edit a file or change a line that is not
explicitly named in the approved plan, you MUST:

1. Pause the in-flight edit.
2. List the proposed out-of-scope change(s) as numbered items:

   ~~~text
   **Proposed out-of-scope changes:**
   1. [file:line] — [what would change and why]
   2. [file:line] — [what would change and why]
   ~~~

3. Present to the user with this exact prompt:
   "These changes are outside the approved plan. Approve, reject,
   or defer each. Reply with item numbers (e.g., '1 approve, 2
   defer')."
4. Wait for per-item decision before resuming.

**What counts as "out of scope":**

- New file not listed in the plan
- Edit to a file listed in the plan but to a line/function the
  plan does not name
- Fixing an "encountered" issue (lint warning, deprecated API,
  unrelated bug) that the plan did not call out

**What does NOT count as "out of scope":**

- Cosmetic adjustments inside an in-scope edit (whitespace,
  formatter output)
- Importing a dependency required to implement an in-scope change

Pass this gate verbatim into every dispatched developer agent's
prompt so the rule propagates to subagents.
```

### Why the two designs are different on purpose

- `al-dev-fix` users do one-shot bug fixes — value is catching extra files in the final diff. One check, near-zero overhead.
- `al-dev-develop` users run multi-task plans with dispatched agents — value is preventing wasted work mid-flight so the user does not review code that should never have been written. Catches the expansion at the source.

---

## Suggestion C — Write-Persistence Verification

### Problem

The Write tool can silently fail to persist a file (cross-repo handoffs, missing parent directories, harness-level drops). Currently no rule requires post-Write verification. Documented failure: cross-repo handoff session where Claude claimed files were created but they were not on disk.

### Solution

Single rule defined globally in `CLAUDE.md` (it is a Write-tool hygiene rule, not a skill-specific concern), cross-referenced once in the knowledge layer so skills that load `verification-and-planning.md` surface it at skill time.

#### C1 — New subsection in `CLAUDE.md` under existing "File Editing Safety"

```markdown
### Write-Persistence Verification

The Write tool can silently fail to persist a file (e.g., on
cross-repo handoffs, when path parents are missing, or when the
harness drops the result). Treat a Write tool call as a *claim*
of success — verify before acting on it.

Rules:

- After every Write tool call that creates a NEW file path,
  immediately run `ls -la <path>` (or read the file) to confirm
  the file exists on disk before reporting the work complete or
  moving to the next step.
- If the file is large or its content matters for downstream
  steps, also confirm content (e.g., `wc -l <path>`, or Read the
  first N lines).
- If verification fails, do NOT silently retry with Write — switch
  to Bash (`mkdir -p` parent, then `cat <<EOF > path`) and re-verify.
- Never tell the user "I've written X" without having verified
  X exists on disk.

Edit-tool calls do not need this check (Edit errors loudly on
mismatch), but a Write to a path the harness has not yet seen
does.
```

#### C2 — One-line cross-reference in `knowledge/verification-and-planning.md`

```markdown
### Write-Persistence

See `CLAUDE.md` → "File Editing Safety" → "Write-Persistence
Verification" for the project-wide rule. Skills that produce new
artefact files (findings, plans, reports, contexts) MUST verify
file existence after Write before reporting the artefact complete.
```

### Why this placement (not per-skill duplication)

- The failure mode (Write silently dropping) is tool behaviour, not skill design — it can happen during any Write call, including ad-hoc work outside a skill.
- `CLAUDE.md` is loaded for every conversation in this repo, so the rule is always in scope.
- Canonical text in `CLAUDE.md` plus a pointer in `verification-and-planning.md` gives one source of truth and surfaces the rule at skill time.
- Avoids the "6 places to maintain" cost of the targeted-per-skill approach.

---

## Verification & success criteria

### Per-change verification (grep-based)

| Change | Verification |
|---|---|
| A1 — Step 1.5 added | `grep -n "Regression Timeline" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md` returns the new step header between Step 1 and Step 2 |
| A2 — Findings template field | Same file: `## Regression Timeline` block present in Step 4 between `## Verdict` and `## Root Cause` |
| A3 — Reconciliation gate | Same file: "Pre-existing claim reconciliation" sub-block present in Step 4 Root Cause section |
| B1 — `al-dev-fix` pre-commit check | `grep -n "Pre-commit Scope Check" profile-al-dev-shared/skills/al-dev-fix/SKILL.md` returns the new step |
| B2 — `al-dev-develop` mid-flight gate | `grep -n "Scope Expansion Gate" profile-al-dev-shared/skills/al-dev-develop/SKILL.md` returns the new section AND every developer-dispatch prompt template includes pass-through wording |
| C1 — `CLAUDE.md` rule | `grep -n "Write-Persistence Verification" CLAUDE.md` returns under "File Editing Safety" |
| C2 — Knowledge cross-reference | `grep -n "Write-Persistence" profile-al-dev-shared/knowledge/verification-and-planning.md` returns the pointer line |

### Smoke-test plan (manual, one-time after merge)

Run on real work the next time it arises, looking for the new behaviours:

1. `/al-dev-investigate` on a real ticket — confirm Claude asks the regression-timeline question (if not in context), the findings file contains `## Regression Timeline`, and any "pre-existing" verdict produces a `**Reconciliation:**` paragraph.
2. `/al-dev-fix` on a small bug — intentionally let Claude touch one out-of-scope file (e.g., an obvious adjacent lint warning) and confirm the pre-commit checkpoint surfaces it for approval rather than committing silently.
3. `/al-dev-develop` on a planned task — observe whether dispatched developer agents pause and list out-of-scope candidates instead of silently expanding.
4. Write-Persistence — exercised implicitly during any of the above; confirm `ls -la` follows any new artefact file Write.

### Done criteria

- All seven `grep` checks pass on `HEAD` after the implementation plan completes.
- One smoke-test pass per skill, captured as a short note in the next session log (no formal acceptance doc needed — plugin-internal tooling, not user-facing product).

### Rollback

Each change is a self-contained markdown edit. If any one of A/B/C causes friction in real use, the single-skill (or single-rule) edit can be reverted independently without breaking the others. No coupling across the three.

---

## Sources

- Insights report: `file:///Users/russelllaing/.claude/usage-data/report-2026-05-18-142417.html` (315 sessions, 2026-04-17 to 2026-05-18)
- Friction patterns referenced: "pre-existing" misdiagnosis (GoSweetSpot 400 / outbound IP), scope creep (BC 28 compile fix expanding into AL0432 + ruleset), Write-tool persistence (cross-repo handoff missing files)
- Related prior spec: `2026-05-15-plugin-reliability-quality-improvements-design.md` (verification standard pattern reused here)
