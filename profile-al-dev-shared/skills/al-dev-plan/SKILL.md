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

## Phase Numbering Rationale

The skill uses fractional phase numbers (Phase 0, Phase 0.5, Phase 1–7) to reflect semantic workflow layers rather than strict sequential numbering. Each fractional phase represents a distinct decision point or checkpoint within the broader workflow. This allows precise specification of where handoff points occur without forcing artificially sequential numbering.

## Phase 0: Check for Existing Progress

Per the Phase 0 Read Protocol in
`knowledge/workflow-resilience.md`.

---

## Phase 0.5: Complexity Triage

Classify the request before gathering full context.
Use these signals from `knowledge/workflow-routing.md`:

| Signal | SIMPLE | MEDIUM / COMPLEX |
| --- | --- | --- |
| Estimated file count | ≤ 3 | 4+ or unclear |
| Pattern in codebase (if known) | Yes | No / unclear |
| New architecture needed | No | Yes |
| Requirements ambiguous | No | Yes |

"SIMPLE" here maps to TRIVIAL or SIMPLE in `knowledge/workflow-routing.md`;
MEDIUM / COMPLEX maps to MEDIUM or COMPLEX.

Note `architect_model` for use in Phase 2:

- **SIMPLE** → `sonnet`
- **MEDIUM / COMPLEX** → `opus`

When in doubt, default to `opus` — over-provisioning is safer
than under-provisioning for architecture work.
Do not surface this decision to the user.

---

## Phase 1: Gather Context

**Input Validation Gate (run before any other step):**
Check whether $ARGUMENTS contains a meaningful feature description.
- If $ARGUMENTS is empty, missing, or only a vague word (e.g. "plan", "help", "this") with no feature context — **STOP immediately**. Ask the user exactly one question:
  > "What AL feature or fix should I plan? Please describe the requirement or paste a spec."
- Do **not** proceed to steps 1–4 below, read any files, or spawn any agents until a substantive answer is provided.
- Once a description is given, resume from step 1 with it as the effective $ARGUMENTS.

1. Read user's request from $ARGUMENTS
2. Check for dated requirements file (from /interview)
   - Use: `$(ls .dev/*-al-dev-interview-requirements.md 2>/dev/null
     | sort | tail -1)`
   - If requirements are unclear/complex, suggest /interview
   - Simple requests can proceed without formal requirements
3. Check for `.dev/project-context.md`
   - If exists, read it for object ID ranges, naming
     conventions, architectural patterns, base app
     integration points
   - If not exists, suggest `/al-dev-init-context` and
     continue without it
4. Pre-research base app integration points using the AL
   Symbols MCP (`al-mcp-server`) before spawning architects:
   - `al_search_objects` — find relevant base app tables,
     pages, or codeunits the feature will extend or interact
     with (e.g. "Sales Header", "Customer", "Item")
   - `al_get_object_definition` — inspect the fields,
     triggers, and events on key base objects
   - `al_search_object_members` — locate existing events or
     procedures the solution can subscribe to

   Include these findings in every architect prompt so
   architects start from real object knowledge, not
   assumptions.

   If the MCP server is unavailable or returns no results
   (e.g., no BC workspace is active), proceed directly to
   Phase 2 using general AL knowledge. Do not stop.

5. Load performance constraints if available:
   ```bash
   PERF=$(ls .dev/*-al-dev-perf-perf-analysis.md 2>/dev/null | sort | tail -1)
   ```
   If a file is found, read the CRITICAL and HIGH severity findings.
   Include them as **"Performance constraints from prior analysis:"** in every
   architect prompt in Phase 2. If no file exists, skip silently.

## Phase 1.5: Verify External Claims

If the request references a findings file, codeburn output, lint report,
or any third-party analysis, verify the claims before forwarding to architects:

1. **File path verification:** For each file path mentioned in findings:
   - Confirm the file exists at that exact path with `test -f <path>`
   - Spot-check content: open the file and verify the described issue/content is present
   - If path doesn't exist → mark as **unverified**, note the missing path
   - If content differs from description → mark as **partially verified**, note the discrepancy
2. **Symbol/API verification:** For each function, procedure, field, or table mentioned:
   - Use the AL MCP server (`al_search_objects` or `al_find_references`) to confirm the symbol exists
   - Cross-harness fallback: `grep -r "symbol_name" src/ --include="*.al"`
   - If not found → mark as **unverified**
   - If found but context differs → mark as **partially verified**
3. **Build evidence summary** as Markdown table:

   | Claim | Type | Status | Evidence |
   | --- | --- | --- | --- |
   | "File X has problem Y" | file+issue | ✅ Verified | File exists, issue confirmed at line Z |
   | "Function Q is slow" | performance | ⚠️ Unverified | Function exists but no profiling data provided |
   | "Table R has no indexes" | schema | ✅ Verified | Grep confirms table R, no index definitions found |

4. **Communicate findings to architects** under `**External findings status:**`
   - ✅ Verified — treat as design input
   - ⚠️ Unverified — treat as hypothesis to test, not requirement
   - ⚠️ Partially verified — details differ; assume claims are approximate
5. **Decision threshold:**
   - ≥75% verified → proceed
   - 50–74% verified → proceed with explicit caveat in prompt
   - <50% verified → gate with USER_GATE decision (proceed as hypotheses / re-run investigation / proceed anyway)

## Phase 1.6: Target Confirmation

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

Default fallback if nothing more specific fits: table
extension approach / separate table approach /
event-driven approach.

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
4. Verify architects use MCP tools:
   - BC Code Intelligence for architecture patterns
   - MS Docs for BC API documentation
   - AL Symbols MCP (`al-mcp-server`) for base app object
     exploration (`al_search_objects`, `al_get_object_definition`,
     `al_find_references`)

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

