# Commit Agent Dispatch Template

> **Documentation only.** The PROJECT_CONTEXT preamble is inlined directly at each
> dispatch site in `al-dev-commit-preflight` (Phases 1.1, 1.3). The dispatch frame
> is self-documented in each phase block. This file is kept as reference for the
> frame format and preamble structure; it is no longer read at runtime.

All `/al-dev-commit` phase dispatches share the same dispatch frame. Each phase
supplies only its own parameters (agent, model, description, phase label, prompt
body, return format). The six-agent commit contract in
`knowledge/commit-workflow-orchestration.md` is authoritative for phase
order and gate logic.

## Dispatch frame

```text
Agent tool:
  agent: <AGENT>
  model: <MODEL>          # include this line only when a phase sets a model
  description: "<DESCRIPTION>"

Prompt:
  "<PHASE-LABEL>

   <PROMPT-BODY>

   Return output in exactly the format specified (<RETURN-FORMAT>)."
```

Preserve the `Return output in exactly the format specified (...)` line and its
tokens verbatim per phase — downstream phases parse those exact tokens, so any
change to a return-format token silently breaks the workflow.

## Shared project-context preamble

Phases that need project context paste this exact 6-line preamble into the
prompt body:

```text
PROJECT_CONTEXT:
- Valid scopes: [list from Phase 0.2]
- Object ID prefix: [from Phase 0.2]
- AL naming pattern: [from Phase 0.2]
- Gitmoji style: [from Phase 0.4]

FD_TICKET: [ticket number from Phase 0.2, or empty]
```
