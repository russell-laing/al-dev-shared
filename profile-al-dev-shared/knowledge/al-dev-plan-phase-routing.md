# al-dev-plan Preflight Complexity Routing

This document defines the complexity-routing decisions made in
`al-dev-plan-preflight` during context assembly before `al-dev-plan`
Phase 2 architect dispatch. Preflight classifies the request up front,
selects an architect model, and records the debate configuration in
`PREFLIGHT_CONTEXT`. The routing logic is canonical here; the planning
skills reference this file and keep only lightweight summaries inline.

## Complexity Classification

Score the request against these signals:

| Signal | SIMPLE | MEDIUM / COMPLEX |
| --- | --- | --- |
| Estimated file count | ≤ 3 | 4+ or unclear |
| Pattern in codebase (if known) | Yes | No / unclear |
| New architecture needed | No | Yes |
| Requirements ambiguous | No | Yes |

Tier mapping to `knowledge/workflow-routing.md`:

- **SIMPLE** maps to TRIVIAL or SIMPLE in `workflow-routing.md`.
- **MEDIUM / COMPLEX** maps to MEDIUM or COMPLEX.

## Model Assignment

The classification sets `architect_model` in `PREFLIGHT_CONTEXT` for
`al-dev-plan` Phase 2:

- **SIMPLE** → `sonnet` — simpler problem, shorter debate, lower cost.
- **MEDIUM / COMPLEX** → `opus` — larger scope, novelty, and ambiguity
  justify the stronger model.

Guidance: when in doubt, default to `opus`. Over-provisioning is safer
than under-provisioning for architecture work, where wrong-approach
rework is far more expensive than the extra tokens. Do not surface this
decision to the user.

## Phase 0.5 Routing Logic

1. **Extract signals** from the user request: estimated file count,
   whether the pattern already exists in the codebase, whether new
   architecture is needed, and whether requirements are ambiguous.
2. **Score complexity** against the classification table. If any
   MEDIUM / COMPLEX signal is present (or signals are unclear), treat the
   request as MEDIUM / COMPLEX.
3. **Record the decision** for Phase 1 and Phase 2: note the tier and the
   resulting `architect_model` so the architect dispatch can apply it.

## Architect Debate Configuration

Configure the architect debate that begins at `al-dev-plan` Phase 2 by
tier:

- **SIMPLE:** 2 architects, shorter debate, a single evaluator pass.
  Abbreviate the cross-architect challenge rounds.
- **MEDIUM / COMPLEX:** 2-3 architects, full competitive debate with
  multiple challenge rounds; the synthesis may itself need an evaluation
  pass before the plan is written.

## Glossary

- **Competitive design debate** — the Phase 2/3 pattern in which 2-3
  architect agents each design a distinct approach, then critique and
  falsify one another's designs so the orchestrator can select or
  synthesize the strongest solution.
- **Abbreviate** — for the SIMPLE tier, run fewer architects and shorter
  challenge rounds rather than the full multi-round debate, trading
  adversarial depth for speed when the problem is small and well-patterned.
- **Synthesis** — the orchestrator's own final design, combining the
  best elements of the architect proposals; never a copy of any single
  architect's output.
