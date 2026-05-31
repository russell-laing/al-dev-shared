# Agent Teams Reference

> Best practices and technical specifications for using Claude Code Agent Teams.

**Last updated:** 2026-05-31

---

## 1. Architectural Overview & Configuration

Agent Teams are designed for **complex, parallel tasks** — not sequential sub-agents. Use them only when multiple independent areas of a codebase need simultaneous work with peer-to-peer dependencies.

**Enabling the feature:** Agent Teams are experimental and must be opted in via `settings.local.json`:

```json
{
  "agentTeams": { "enabled": true }
}
```

**Plan Approval Mode:** Teammates submit plans for approval by the main agent (or the user) before execution begins. The main agent reviews each teammate's plan and either approves it or sends it back with corrections. No teammate begins implementation until its plan is approved.

---

## 2. Prompting Standards

- **Structure:** Open with a single high-level goal sentence, then define a team of 3–5 agents. For each agent, specify role name and model (default: Sonnet).
- **Territories:** Assign each agent explicit file ownership. Name the exact directories or files each agent controls. Agents must not write to another agent's territory without explicit handoff.
- **Named recipients:** Always address messages to a named teammate (`@researcher`, `@implementer`). Never send unaddressed broadcasts.
- **Dependencies:** Declare all inter-agent dependencies in the initial prompt. If Agent B needs Agent A's output, state it upfront so the team can self-sequence without asking.

Example team definition structure:

```
Goal: Refactor the reporting pipeline.

Team:
- @schema-agent (Sonnet): owns /src/schema/. Redesigns the schema layer.
- @query-agent (Sonnet): owns /src/queries/. Updates queries to match new schema. Depends on @schema-agent finishing first.
- @test-agent (Sonnet): owns /tests/reporting/. Writes integration tests. Depends on both above agents.
```

---

## 3. Operational Rules

### Communication

Teammates can message each other directly to resolve dependencies — they do not need to route through the main agent. Encourage this; it reduces bottlenecks.

### Permissions

Agents inherit **all** permissions from the main session, including bash commands, MCP servers, and file write access. There is no per-agent permission scoping.

### Efficiency

Agent Teams are expensive and slow. Use them only for complex, multi-area projects where genuine parallelism exists. For sequential tasks (A then B then C), use sub-agents instead — they are cheaper and simpler to reason about.

### Lifecycle Management

Before ending the session, perform a **clean shutdown**: ask each agent to confirm it has saved and committed its work. Do not close the session until all agents report completion. Uncommitted work is lost when the session ends.

---

## 4. Troubleshooting / Don'ts

| Issue | Resolution |
|-------|------------|
| Team exceeds 5 agents | Split the project into independent sub-projects; run separate teams sequentially |
| Vague deliverables | Rewrite agent goals with specific file paths and measurable output criteria before dispatching |
| Permission loop (agents repeatedly asking for approval) | Pre-approve the required tools in `.claude/settings.json` `allowedTools` before starting the team |
| Agent appears idle | Explicitly re-assign its task or unblock its dependency in the prompt: name the agent and state the new instruction directly |
| Two agents overwriting each other | Review territory assignments; territory boundaries must be non-overlapping directories or named files |
