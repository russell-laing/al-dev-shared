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
  over ad-hoc planning.
argument-hint: "[feature description]"
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

## Phase 0: Check for Existing Progress

Per the Phase 0 Read Protocol in
`knowledge/workflow-resilience.md`.

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

1. **Input Validation Gate** (mandatory) — ensure requirements are present and understood (see the gate above; do not proceed without a substantive feature description).
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

**Phase 1.6 (Optional — Pre-Research Base App):** If Phase 1's pre-research via AL LSP or MCP returns results, consolidate findings. If no results, skip to Phase 2. If results are incomplete and a required symbol remains unverified, note it for architect input in Phase 2.

Before acting on any findings file or context document:

1. **Identify targets:**
   - Findings reference: Extract the target name/path from the document
   - Your request: Extract target from user message (skill, repo, file, or project)
   - Output path: Absolute path where work will land
2. **Validate match:**
   ```
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

## Phase 2: Spawn Architect Team (2-3 agents)

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
```

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
```

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
```

USER_GATE — ask the user with options:
- Approve - Proceed to development
- Refine - Adjust plan (what needs changing?)
- Review Alternatives - Show me other architect approaches
- Stop - Cancel planning

If user selects "Refine", spawn architects again with the
user's feedback.
