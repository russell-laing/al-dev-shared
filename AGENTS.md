# AGENTS.md

This file provides guidance to Copilot CLI when working with code in this repository.

## What This Repo Is

`al-dev-shared` is a **shared plugin** — a library of AL/BC development skills, agents, and knowledge documents consumed by AI coding harness profiles. It is not an AL project itself; it contains no `.al` source files.

It is registered as an installed plugin. The plugin root is available via `AL_DEV_SHARED_PLUGIN_ROOT`.

## Structure

```
profile-al-dev-shared/          # The plugin content consumed by harness profiles
  skills/<name>/SKILL.md        # Skill definitions (invoked as /name)
  agents/<name>.md              # Agent definitions (spawned by skills)
  knowledge/                    # Workflow knowledge referenced by skills
  bc-code-intel-knowledge/      # BC Code Intelligence specialist knowledge
  markdown/                     # Markdown and Mermaid style guides
.claude-plugin/marketplace.json # Marketplace registration schema
```

## Skill File Format

Each skill is a markdown file with YAML frontmatter:

```markdown
---
name: skill-name
description: >-
  Trigger description used by the AI to auto-invoke.
argument-hint: "[optional args]"
---
# Skill instructions...
```

Skills reference knowledge files using relative paths (e.g., `knowledge/workflow-routing.md`). Agents are referenced by their type name (e.g., `al-dev-shared:al-dev-developer`).

## Agent File Format

Each agent is a markdown file with YAML frontmatter specifying `name`, `description`, `model`, and `tools`. The body is the system prompt passed to the spawned agent.

## Key Architectural Patterns

**Complexity routing** (`knowledge/workflow-routing.md`): All skills classify tasks as TRIVIAL / SIMPLE / MEDIUM / COMPLEX and route accordingly. TRIVIAL → direct fix; COMPLEX → full multi-agent pipeline.

**Workflow resilience** (`knowledge/workflow-resilience.md`): Multi-phase skills checkpoint to `.dev/progress.md` after each phase. Phase 0 of every multi-phase skill checks this file and offers resume/restart.

**`.dev/` directory convention**: All skill artifacts are written here — progress checkpoints, solution plans (`YYYY-MM-DD-al-dev-plan-solution-plan.md`), code reviews (`YYYY-MM-DD-al-dev-develop-code-review.md`), lint reports (`YYYY-MM-DD-al-dev-lint-lint-report.md`), ticket contexts, requirements files.

**Validator scripts**: Some skills have companion Python validators (e.g., `skills/al-dev-plan/validate-plan.py`) that are run after output files are written. Skills look for these via `find $AL_DEV_SHARED_PLUGIN_ROOT -name "validate-*.py"`.

## Compile/Lint

Skills that run AL compilation use:
```bash
al-compile --output .dev/compile-errors.log
```
This command applies to AL projects *using* this plugin, not to this repo itself. The full procedure is in `knowledge/compile-lint-procedure.md`.

## Commit Conventions

- Gitmoji prefix on every commit (check `git log` for current style)
- Freshdesk tickets as `#FD<number>` in the message body
- No `Co-Authored-By` trailers
- Use `git -C <path>` instead of `cd <path> && git`

---

## Harness Mapping

This table maps generic concept names (used in shared skills and agents) to their
concrete Copilot CLI equivalents. Maintained here so `al-dev-align` can verify coverage.

| Concept | Copilot CLI Value |
|---|---|
| **project instructions file** | `AGENTS.md` |
| **harness settings file** | `~/.copilot/settings.json` |
| **AL_DEV_SHARED_PLUGIN_ROOT** | `~/.copilot/installed-plugins/<plugin-id>/profile-al-dev-shared` |
| **USER_GATE** | `ask_user` tool |
| **explore agent** | `agent_type: "explore"` in task tool |
| **restart the agent** | start a new Copilot CLI session |
| **MCP: al-mcp-server** | `al-mcp-server-<tool>` |
| **MCP: bc-code-intelligence** | `bc-code-intelligence-mcp-<tool>` |
| **MCP: microsoft-docs** | `microsoft_docs_mcp-<tool>` |

---

## Quality Review Conventions

**Iterative task reviews (per-task scope):**
When a quality reviewer finds a bug class in one task, it MUST add that class
to an explicit "watch list" carried into every subsequent task review in the
same session. Append to the review prompt:

> "Previously found in this session: [list bug classes]. Check all new bash
> command blocks for stdout capture; check all new JSON output paths for
> completeness."

This prevents the same class of bug being found twice across two sequential
review cycles.
