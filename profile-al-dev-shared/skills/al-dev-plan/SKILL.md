---
name: al-dev-plan
description: >-
  Design a complete AL/BC solution using competitive solution
  design (2-3 architect agents debate approaches, you pick the
  winner). Use this skill whenever the user wants to plan,
  design, or architect a Business Central feature — including
  when they describe a requirement, ask "how should I build
  this", or say "plan this" or "design this". Runs the architect
  debate (phases 2–7); context gathering (phases 0–1.6) is
  handled by /al-dev-plan-preflight, which this skill dispatches
  automatically. Produces
  .dev/$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md. Prefer this
  over ad-hoc planning. Supports resuming directly to Phase 2
  (architect debate) if you already have finalized preflight
  context: `--resume-from=phase2`.
argument-hint: "[feature description] [--resume-from=phase2]"
---

# Plan Skill

Design a complete AL/BC solution by facilitating competitive
debate between 2-3 solution architect agents, then synthesizing
the winning approach. You do NOT design the solution yourself.

This skill runs the architect-debate phases (2–7). Context
gathering and verification (phases 0–1.6 — resume check,
complexity triage, context loading, claims verification, target
confirmation) live in the reusable `/al-dev-plan-preflight`
skill. Phase 0 below dispatches preflight automatically (or reads
its `PREFLIGHT_CONTEXT` output when resuming), so direct
invocation of `/al-dev-plan` still performs the full flow
end-to-end.

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

## Phase 0: Obtain Preflight Context

The architect debate (phases 2–7) consumes only the
`PREFLIGHT_CONTEXT` state produced by `/al-dev-plan-preflight`. That
state — requirements, scope, `architect_model`, project context, and
the **External findings status:** block — is written to
`.dev/preflight-context.md`. Phase 0 obtains that context, then jumps
to Phase 2.

### Resume modes

**Mode A — `--resume-from=phase2` passed in $ARGUMENTS:**
The caller is asserting preflight context is already finalized and
wants to skip context gathering and go straight to architect debate.

1. Read `.dev/preflight-context.md`.
2. If the file is **missing or unreadable**, STOP and report:
   *"No preflight context to resume from. Run /al-dev-plan without
   --resume-from to perform preflight (phases 0–1.6) first."*
   Do not fabricate context state.
3. If present, load the context fields (see schema below) into the
   working state used by Phase 2 and jump to **Phase 2**. Honour
   `no_crit_swarm` if set.

**Mode B — no `--resume-from`, but `.dev/preflight-context.md`
exists:**
Offer resume via USER_GATE:

> A prior preflight context exists (saved [timestamp]) for:
> [one-line requirements summary].
>
> - **Resume** — skip preflight and go to architect debate (Phase 2)
> - **Restart** — discard the context and gather it fresh

- **Resume** → load context, jump to Phase 2 (same as Mode A).
- **Restart** → delete `.dev/preflight-context.md`, then dispatch
  preflight fresh (Mode C).

> **Tip:** on a fresh invocation you can skip straight to the architect debate
> with `/al-dev-plan --resume-from=phase2` (Mode A), provided
> `.dev/preflight-context.md` is current.

**Mode C — no `--resume-from` and no context file:**
Dispatch `/al-dev-plan-preflight` with the same $ARGUMENTS. That
skill runs the full context-gathering flow (resume check, complexity
triage, context loading, claims verification, target confirmation),
writes `.dev/preflight-context.md`, and emits the `PREFLIGHT_CONTEXT`
block. When it returns, load that block into the working state used by
Phase 2 and continue. If preflight stops at its input-validation gate
(no substantive requirement), it has already asked the user — do not
proceed to Phase 2 until preflight completes and emits context.

### PREFLIGHT_CONTEXT schema

`/al-dev-plan-preflight` writes `.dev/preflight-context.md`. The
canonical schema and field semantics are defined in
`../../knowledge/preflight-context-schema.md` — read that file before
loading the context block.

Treat these fields as the authoritative inputs to Phase 2:

- `requirements` + `scope` → the user requirement and scope for the
  architect prompts.
- `architect_model` → the model assignment from preflight (do not
  re-triage).
- `user_context` → the project-context inputs (object ID range,
  naming prefix, key patterns) and any perf/explore findings.
- `external_findings_status` → the **External findings status:**
  block forwarded to architects; skip if null.

If a required field is missing from the context, re-dispatch
`/al-dev-plan-preflight` rather than proceeding with empty state.

## Phase 2: Spawn Architect Team (2-3 agents)

**State source:** Phase 2 draws on exactly the `PREFLIGHT_CONTEXT`
fields obtained in Phase 0 — requirement (`requirements`),
scope/objects (`scope`), `architect_model`, project context
(`user_context`), and the **External findings status:** block
(`external_findings_status`). Phase 2 must not read any intermediate
preflight working state beyond these fields, so a resumed run is
equivalent to a fresh one.

Follow the **Competitive Debate** pattern in
`knowledge/architect-invocation-patterns.md` (Pattern 1) for deriving 2-3
meaningfully different starting approaches and the spawn-count guidance.

Default fallback if nothing more specific fits — use these debate angles in
order: (1) table extension (conservative, builds on base app); (2) separate
table (isolated scope, decoupled from base); (3) event-driven (flexible,
extensible, minimal coupling). If none of these three angles fits the actual
problem domain, derive three domain-appropriate contrasting angles from the
requirements directly (e.g. scope isolation, coupling strategy, data-ownership model).

**Spawn count:** Default 2 architects. Use 1 if the scope is clearly
defined (fits one page, all BC objects named, no architectural
trade-offs) and only one viable approach exists. Use 3 if the scope is
highly complex, contested, or spans multiple architectural concerns.

Spawn 2–3 **al-dev-solution-architect** agents with DIFFERENT
starting approaches to prevent convergence. Assign each
a distinct approach derived above.

**Progress signal (required):** immediately after dispatching the architect
agents and before waiting on their results, emit a one-line status message so
the parallel wait does not read as a stall, e.g.:

```text
Architects running: <N> agents spawned (<approach labels>) — waiting for results...
```

Emit the equivalent signal again when the Phase 3 debate round is dispatched.

If `architect_model = sonnet` (set during preflight), include
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

### Architect Output Contract

Each architect must return the three sections defined in the **Pattern 1
dispatch block** of `knowledge/architect-invocation-patterns.md`
(Proposal, Self-critique, Falsification), in that order.

Skill-specific quality bar: critiques must name concrete failure modes and
identify an observable condition or code-level breakage; falsifications must
state one realistic condition where the approach fails. Architects missing
any of the three sections are excluded from Phase 3 synthesis.

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

**Phase 3 ends when any of these conditions is met:**

- (a) All spawned architects have submitted their three required sections
  (Proposal, Self-critique, Falsification).
- (b) A clear trade-off comparison is visible across all dimensions reviewed
  in this phase.
- (c) The user explicitly requests a decision without further debate.

Proceed to Phase 4 when any condition is met.

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

**Testability gate:** If the architect's return block contains
`TESTABILITY_COMPLETE: no`, the architect could not design a testable
solution and did not write a plan. Do not treat planning as complete and do
not proceed to development. Surface the unresolved testability concern to the
user verbatim and stop until it is resolved (re-run the architect with the
clarified constraints, or escalate).

## Phase 5: Write .dev/$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md

YOU write the final synthesis yourself. Do not copy architect
output. Use the structure defined in
`knowledge/solution-plan-template.md`.

Write `.dev/progress.md` per `knowledge/workflow-resilience.md`.

After writing the solution plan, invoke **/al-dev-plan-final-review** to run
validation and gate user approval before implementation begins.
