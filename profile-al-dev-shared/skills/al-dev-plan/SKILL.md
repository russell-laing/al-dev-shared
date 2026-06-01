---
name: al-dev-plan
description: >-
  Design a complete AL/BC solution using competitive solution
  design (2-3 architect agents debate approaches, you pick the
  winner). Use this skill whenever the user wants to plan,
  design, or architect a Business Central feature — including
  when they describe a requirement, ask "how should I build
  this", or say "plan this" or "design this". Produces
  .dev/$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md. Prefer this
  over ad-hoc planning. Supports resuming directly to Phase 2
  (architect debate) if you already have a finalized spec:
  `--resume-from=phase2`.
argument-hint: "[feature description] [--resume-from=phase2]"
---

# Plan Skill

Design a complete AL/BC solution by facilitating competitive
debate between 2-3 solution architect agents, then synthesizing
the winning approach. You do NOT design the solution yourself.

## Intent Preflight

Before dispatching architect agents or writing a plan artifact, apply
`knowledge/intent-preflight.md`.

Default intent for this skill is `REVIEW` when the user asks for design,
planning, or architecture output. Writing the requested `.dev/` plan artifact is
allowed as part of that planning request.

Stop before architect dispatch if the request is only an audit, validation
review, code review, or report assessment that does not ask for a design or
implementation plan. Ask the intent-mismatch prompt from
`knowledge/intent-preflight.md` before continuing.

## Artifact Contract

This skill is governed by `knowledge/artifact-contracts.md`.

Do not claim the work is complete or ready for implementation until the success evidence named in `knowledge/artifact-contracts.md` for this skill has been produced and read in the current run.

When shell search or structured-file inspection is required, prefer `rg` and
`jq` before falling back to broader shell text processing.

## Phase 0: Check for Existing Progress

This skill has two preflight groups:

- **Preflight phases (0–1.6):** requirements gathering, complexity
  triage, context loading, external-claim verification, and target
  confirmation. These produce the state needed to begin architect
  debate.
- **Architect-debate phases (2–7):** competitive design, debate
  facilitation, evaluation, synthesis, validation, and approval.
  These phases consume only the checkpoint state listed below — they
  do not read intermediate state from the preflight phases directly.

### Resume modes

**Mode A — `--resume-from=phase2` passed in $ARGUMENTS:**
The caller is asserting the spec is already finalized and wants to
skip preflight and go straight to architect debate.

1. Read `.dev/al-dev-plan-checkpoint.json`.
2. If the file is **missing or unreadable**, STOP and report:
   *"No checkpoint to resume from. Run /al-dev-plan without
   --resume-from to perform preflight (phases 0–1.6) first."*
   Do not fabricate checkpoint state.
3. If present, load the checkpoint fields (see schema below) into the
   working state used by Phase 2, skip phases 0.5–1.6 entirely, and
   jump to **Phase 2**. Honour `no_crit_swarm` if set.

**Mode B — no `--resume-from`, but `.dev/al-dev-plan-checkpoint.json`
exists:**
Offer resume via USER_GATE:

> A prior planning checkpoint exists (saved [timestamp]) for:
> [one-line requirements summary].
>
> - **Resume** — skip preflight and go to architect debate (Phase 2)
> - **Restart** — discard the checkpoint and gather context fresh

- **Resume** → load checkpoint, skip to Phase 2 (same as Mode A).
- **Restart** → delete `.dev/al-dev-plan-checkpoint.json`, then also
  apply the standard `.dev/progress.md` Read Protocol below before
  Phase 0.5.

**Mode C — no `--resume-from` and no checkpoint:**
Apply the standard Phase 0 Read Protocol in
`knowledge/workflow-resilience.md` (handles `.dev/progress.md`
mid-run resume), then proceed to Phase 0.5.

### Checkpoint schema

The preflight phases write `.dev/al-dev-plan-checkpoint.json` once
context gathering and any optional verification phases complete (see
the **end of Phase 1.6** write step). It captures every input Phase 2
needs so the debate phases never depend on skipped-phase state:

```json
{
  "phase": 2,
  "requirements": "user feature requirement and preliminary scope",
  "scope": "estimated file count, affected BC objects, patterns",
  "architect_model": "opus",
  "user_context": "object ID range, naming prefix, key patterns, perf/explore findings",
  "external_findings_status": "summary of verified/unverified claims, or null",
  "timestamp": "2026-06-01T00:00:00Z",
  "no_crit_swarm": false
}
```

When resuming (Mode A or Mode B → Resume), treat these fields as the
authoritative substitute for the corresponding preflight outputs:

- `requirements` + `scope` → the user requirement and scope for the
  architect prompts.
- `architect_model` → the model assignment from Phase 0.5 (do not
  re-triage).
- `user_context` → the project-context inputs (object ID range,
  naming prefix, key patterns) and any perf/explore findings.
- `external_findings_status` → the **External findings status:**
  block forwarded to architects (Phase 1.5 output); skip if null.

If a required field is missing from the checkpoint, fall back to
re-running the specific preflight step that produces it rather than
proceeding with empty state.

---

## Phase 0.5: Complexity Triage

Classify the request before gathering full context.
See `knowledge/al-dev-plan-phase-routing.md` for full complexity classification rules and model assignment logic.

Quick reference:

| Signal | SIMPLE | MEDIUM / COMPLEX |
| --- | --- | --- |
| Estimated file count | ≤ 3 | 4+ or unclear |
| Pattern in codebase (if known) | Yes | No / unclear |
| New architecture needed | No | Yes |
| Requirements ambiguous | No | Yes |

When in doubt, default to `opus` (MEDIUM / COMPLEX tier).

Note `architect_model` for use in Phase 2:

- **SIMPLE** → `sonnet`
- **MEDIUM / COMPLEX** → `opus`

Do not surface this decision to the user.

---

## Phase 1: Gather Context

**Input Validation Gate (run before any other step):**
Check whether $ARGUMENTS contains a meaningful feature description.

- If $ARGUMENTS is empty, missing, or only a vague word (e.g. "plan", "help", "this") with no feature context — **STOP immediately**. Sufficient context requires: (1) a feature name or description, AND (2) at least one functional requirement. Example: "Add a credit limit check during posting." Ask the user exactly one question:
  > "What AL feature or fix should I plan? Please describe the requirement or paste a spec."
- Do **not** proceed to steps 1–4 below, read any files, or spawn any agents until a substantive answer is provided.
- Once a description is given, resume from step 1 with it as the effective $ARGUMENTS.

**Clarification retry logic:**

- **First vague response:** Ask for clarification once. Expected context: (1) business goal, (2) key workflows, (3) affected BC objects.
- **Second vague response:** Ask for clarification a second time with specific prompt: "Please provide: (1) the business goal (what problem does this solve?), (2) the key user workflows (who does what?), and (3) the BC objects affected (which tables/pages/events?)."
- **Third vague response:** Stop and escalate to user with message: "I've asked twice for clarification. To proceed, I need these three pieces of information: (1) business goal — what problem this solves, (2) key workflows — who does what and when, (3) affected BC objects — which tables/pages/events. Please provide all three, or consider running /interview first for guided discovery."
- Do NOT proceed to architect spawn if after 2 clarification attempts the description remains too vague (e.g., "make it better", "improve the system").

1. **Read input from $ARGUMENTS** — Extract the user's feature request and preliminary scope. If missing, gate requires clarification.
2. **Load requirements and context files** — read `.dev/project-context.md` (object ID ranges, naming conventions, architectural patterns, base app integration points) and any prior interview requirements (`$(ls .dev/*-al-dev-interview-requirements.md 2>/dev/null | sort | tail -1)`). If project context is missing, suggest `/al-dev-init-context` and continue without it. If requirements are unclear/complex, suggest `/interview`.
3. **Gather symbol evidence** — use the strongest available AL symbol evidence before spawning architects: prefer `AL LSP` semantic navigation (go-to-definition, find-references, document symbols, hover/type) when the active harness exposes it; otherwise AL MCP via `al-mcp-server` (`al_search_objects`, `al_get_object_definition`, `al_search_object_members`); otherwise tightly scoped `rg` labeled as `text search`. Include findings and evidence source (`AL LSP`, `AL MCP`, `text search`, or `unverified`) in every architect prompt. If no provider/result is available, proceed to Phase 2 using general AL knowledge unless a required symbol is `unverified`.
4. **Load performance and exploration findings** — if available, integrate findings from `/al-dev-explore` or `/al-dev-perf` pre-planning phases:

   ```bash
   PERF=$(ls .dev/*-al-dev-perf-perf-analysis.md 2>/dev/null | sort | tail -1)
   EXPLORE=$(ls .dev/*-al-dev-explore-findings.md 2>/dev/null | sort | tail -1)
   ```

   If a perf file is found, read CRITICAL/HIGH findings and include them as **"Performance constraints from prior analysis:"** in every architect prompt in Phase 2. If an explore file is found, read the findings and synthesized recommendations and include them as **"Codebase exploration findings from prior investigation:"** in every architect prompt. If neither exists, skip silently.

## Phase 1.5: Verify External Claims

**Phase 1.5 (Optional — External Claims Verification):** If the user request references a findings file, codeburn output, lint report, or third-party analysis, execute this phase to verify claims before forwarding to architects. Otherwise, skip to Phase 2.

If the request references a findings file, codeburn output, lint report,
or any third-party analysis, verify the claims before forwarding to architects:

1. **File path verification:** For each file path mentioned in findings:
   - Confirm the file exists at that exact path with `test -f <path>`
   - Spot-check content: open the file and verify the described issue/content is present
   - If path doesn't exist → mark as **unverified**, note the missing path
   - If content differs from description → mark as **partially verified**, note the discrepancy
2. **Symbol/API verification:** For each function, procedure, field, or table mentioned:
   - Prefer `AL semantic navigation` (`AL LSP`) when the active
     harness exposes it: go-to-definition, find-references,
     document symbols, and hover/type information.
   - If unavailable, use AL MCP (`al_search_objects`,
     `al_search_object_members`, `al_get_object_definition`, or
     `al_find_references`).
   - If no semantic provider is available, use scoped text search:
     `rg -n "symbol_name" src/ --glob "*.al"`.
   - Record evidence source as `AL LSP`, `AL MCP`, `text search`,
     or `unverified`.
   - If not found → mark as **unverified**.
   - If found but context differs → mark as **partially verified**.
3. **Build evidence summary** as Markdown table:

   | Claim | Type | Status | Evidence Source | Evidence |
   | --- | --- | --- | --- | --- |
   | "Field X exists on table Y" | symbol | Verified | text search | `src/TableY.al:42` contains field declaration; semantic provider unavailable |
   | "Procedure Q exists" | procedure | Unverified | unverified | No `AL LSP`, `AL MCP`, or scoped `rg` result found |
   | "Event R has parameter S" | event signature | Verified | AL MCP | `al_search_object_members` found publisher signature with parameter S |

4. **Communicate findings to architects** under `**External findings status:**`
   - ✅ Verified — treat as design input
   - ⚠️ Unverified — treat as hypothesis to test, not requirement
   - ⚠️ Partially verified — details differ; assume claims are approximate
5. **Decision threshold:**
   - ≥75% verified → proceed
   - 50–74% verified → proceed with explicit caveat in prompt
   - <50% verified → gate with USER_GATE decision (proceed as hypotheses / re-run investigation / proceed anyway)

## Phase 1.6: Target Confirmation

**Phase 1.6 (Optional — Target Confirmation):** If Phase 1 discovers a target ambiguity or a specific resource constraint (e.g., a .dev/findings-file.md or external lint output that references a particular subsystem), cross-check the target interpretation before architect dispatch. Otherwise, skip to Phase 2.

Before acting on any findings file or context document:

1. **Identify targets:**
   - Findings reference: Extract the target name/path from the document
   - Your request: Extract target from user message (skill, repo, file, or project)
   - Output path: Absolute path where work will land
2. **Validate match:**

   ```text
   > **Target check:**
   > - Findings reference: [extracted from findings]
   > - Your request: [extracted from your message]
   > - Output path: [absolute path where work will land]
   >
   > Do these match? If findings and request disagree, stop and confirm before proceeding.
   ```

3. **Decision:**
   - If all align → continue
   - If findings/request disagree → flag mismatch and wait
   - If mismatch is fundamental → stop and escalate to user

### Preflight checkpoint write

Once preflight (phases 0.5–1.6) is complete and before spawning
architects, write `.dev/al-dev-plan-checkpoint.json` using the schema
in Phase 0. This captures the full state Phase 2 needs so a later run
can resume with `--resume-from=phase2`:

```bash
mkdir -p .dev
```

Populate `requirements`, `scope`, `architect_model`, `user_context`,
`external_findings_status` (or `null` if Phase 1.5 was skipped),
`timestamp` (ISO 8601), and `no_crit_swarm`. Set `phase` to `2`.
Overwrite any existing checkpoint — latest state wins.

## Phase 2: Spawn Architect Team (2-3 agents)

**State source:** Use the checkpoint state when this run resumed via
`--resume-from=phase2` (or Mode B → Resume); otherwise use the
preflight outputs from phases 0.5–1.6. Either way, Phase 2 draws on
exactly these inputs — requirement (`requirements`), scope/objects
(`scope`), `architect_model`, project context (`user_context`), and
the **External findings status:** block (`external_findings_status`).
Phase 2 must not read intermediate preflight working state beyond
these fields, so a resumed run is equivalent to a fresh one.

Follow the **Competitive Debate** pattern in
`knowledge/architect-invocation-patterns.md`.

Before spawning, derive 2-3 meaningfully different starting
approaches from the requirement itself. The goal is to prevent
convergence — each architect should have a genuinely distinct
angle, not minor variations on the same idea.

Examples of how to choose approaches (adapt to the specific
requirement):

- Data-centric feature: table extension vs. separate table
  vs. virtual table
- Business process: event-driven vs. direct integration
  vs. workflow codeunit
- External integration: REST API vs. OData vs. message
  queue
- Reporting: query object vs. API page vs. report extension

Default fallback if nothing more specific fits — use these debate angles in order:
(1) table extension (conservative, builds on base app);
(2) separate table (isolated scope, decoupled from base);
(3) event-driven (flexible, extensible, minimal coupling).

Spawn 2-3 **al-dev-solution-architect** agents with DIFFERENT
starting approaches to prevent convergence. Assign each
a distinct approach derived above.

If `architect_model = sonnet` (set in Phase 0.5), include
`model: sonnet` as a parameter in each Agent tool invocation.
If `architect_model = opus`, omit the model parameter — the
agent frontmatter default (`opus`, see
`agents/al-dev-solution-architect.md`) applies.

Each architect prompt must include:

```text
**Task Complexity Tier:** [SIMPLE if architect_model=sonnet | MEDIUM/COMPLEX if architect_model=opus]

Design a complete AL/BC solution for: [user requirement]

Project context:
- Object ID range: [from project-context.md or ask user]
- Naming prefix: [from project-context.md or ask user]
- Key patterns: [from project-context.md]

Design considerations:
1. BC base app integration (tables/events to extend)
2. Complete object design (tables, pages, codeunits, APIs)
3. Data model and validation rules
4. Testability (dependency injection, interfaces)
5. Performance implications
6. Upgrade considerations

Your assigned approach: [specific approach for this architect]
```markdown

## Architect Output Requirements

Each architect must produce THREE outputs (not one):

1. **Proposal** — complete solution design (recommended approach)
2. **Critique** — specific critique of ONE other approach from briefing
   - Must name concrete failure modes
   - Must identify observable condition or code-level breakage
3. **Falsification** — one realistic condition where YOUR approach fails
   - State design limits honestly

Architects without all three outputs are excluded from Phase 3 synthesis.
Quality bar: critiques/falsifications must be substantive enough to force re-evaluation of a design.

## Phase 3: Facilitate Debate

1. Let architects work independently first (2-5 min)
2. Facilitate cross-architect debate:
   - "Architect A, explain why your approach is better for
     maintainability"
   - "Architect B, what's your response to A's upgrade
     complexity concerns?"
   - "Architect C, compare event-driven overhead vs direct
     integration"
3. Challenge weak points yourself:
   - "Your plan doesn't address [scenario X]. How would
     your approach handle it?"
   - "What happens when [edge case Y] occurs?"
4. Verify architects use available semantic evidence:
   - AL semantic navigation (`AL LSP`) when exposed for definition
     lookup, references, document symbols, hover/type information,
     and rename/refactor impact checks
   - AL Symbols MCP (`al-mcp-server`) for base app object
     exploration (`al_search_objects`, `al_get_object_definition`,
     `al_find_references`)
   - BC Code Intelligence for architecture patterns
   - MS Docs for BC API documentation
   - Scoped text search only as a weaker fallback labeled
     `text search`

Push architects to think deeper. Do not accept superficial
solutions.

Write `.dev/progress.md` per `knowledge/workflow-resilience.md`.

## Phase 4: Evaluate and Select

Review all architect outputs on these criteria:

1. **Completeness** - All requirements addressed? Object
   design complete? BC integration points identified?
2. **Technical Quality** - AL best practices? Dependency
   injection for testability? Edge cases handled?
3. **BC Integration** - Right base objects extended?
   Appropriate events? Upgrade-compatible?
4. **Maintainability** - Clear object responsibilities?
   Extensible design? Follows project patterns?
5. **Trade-offs** - Costs acknowledged? Weak scenarios
   identified? Complexity justified?

Then decide (this is YOUR tactical decision, not the user's):

- **Pick one approach** with clear rationale
- **Create hybrid** combining best elements from multiple
- **Send back** for refinement if all approaches are weak

## Phase 5: Write .dev/$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md

YOU write the final synthesis yourself. Do not copy architect
output. Use the structure defined in
`knowledge/solution-plan-template.md`.

Write `.dev/progress.md` per `knowledge/workflow-resilience.md`.

## Phase 6: Validate the Plan

After writing the solution plan file, run the validator:

```bash
VALIDATOR="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-plan/validate-plan.py"
REQ=$(ls .dev/*-al-dev-interview-requirements.md 2>/dev/null \
  | sort | tail -1)
PLAN=$(ls .dev/*-al-dev-plan-solution-plan.md 2>/dev/null \
  | sort | tail -1)
[ -f "$VALIDATOR" ] && [ -n "$REQ" ] && [ -n "$PLAN" ] && \
  python3 "$VALIDATOR" "$PLAN" "$REQ" \
  || echo "Validator not found or files missing — skipping"
```text

The script auto-detects files in the same directory.

Fix any issues the validator reports before presenting to the
user. Common issues:
- Missing required sections (add them)
- Duplicate object IDs (reconcile from architect merge)
- Untraced requirements (add REQ-NNN references to plan)

## Phase 7: Present to User for Approval

Present your synthesized plan:

```text
Solution plan complete -> .dev/$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md

Key decisions:
- [Major design decisions with rationale]
- [Key objects: 3-5 most important ones]
- [BC integration approach]

Evaluated [N] competing approaches:
- Approach A: [1 sentence pro/con]
- Approach B: [1 sentence pro/con] <- Selected
- Approach C: [1 sentence pro/con]

Selected Approach [X] because [key rationale].

Ready to proceed to development?
```yaml

USER_GATE — ask the user with options:
- Approve - Proceed to development
- Refine - Adjust plan (what needs changing?)
- Review Alternatives - Show me other architect approaches
- Stop - Cancel planning

If user selects "Refine", spawn architects again with the
user's feedback.
