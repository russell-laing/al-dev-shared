# Companion-Context Ownership

Several shared skills route users to `/al-dev-init-context` and read a
`.dev/project-context.md` document (object ID ranges, naming conventions,
architectural patterns, integration points). The shared plugin surface does
not own that bootstrap capability: `al-dev-init-context` is provided by
companion repositories layered on top of this shared surface. This document
records that ownership boundary and the fallback behavior when the companion
capability is unavailable.

## Ownership Boundary

- The shared surface (`profile-al-dev-shared/`) consumes
  `.dev/project-context.md` as optional input and may suggest creating it, but
  does not define the skill that produces it.
- Companion repositories own the `al-dev-init-context` skill that produces
  `.dev/project-context.md`. (Such companion layers are typically per-harness
  configuration repositories; the shared surface names them only as examples of
  where the capability lives, never as a required dependency of any single
  harness.)

## Fallback Behavior — Degrade to Inferred Context

`.dev/project-context.md` is optional. When it is absent:

1. Do not hard-stop. Note that no project-context document was found.
2. Suggest `/al-dev-init-context` (provided by a companion layer) as the way to
   create a durable one.
3. Proceed with a minimal inferred context gathered from the current request
   and repository: the object-naming prefix, object ID ranges, and patterns
   observed in nearby files.
4. Mark any field that was inferred rather than read from a durable
   project-context document, so downstream steps know it is provisional.

A routed skill must never block solely because the companion
`al-dev-init-context` capability is not installed.

## Consumers

`workflow-routing.md`, `al-dev-explore`, `al-dev-plan-preflight`,
`al-dev-develop-orchestrate`, and `al-dev-commit-preflight` all read or suggest
`.dev/project-context.md`, or route to `al-dev-init-context`. Each applies the
degrade-to-inferred fallback above. `al-dev-commit-preflight` is a special case:
its guard is on the project *instructions* file rather than the optional
`.dev/project-context.md`, but it must still degrade — never hard-stop — when the
companion `al-dev-init-context` capability is unavailable.
