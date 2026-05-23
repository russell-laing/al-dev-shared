# AGENTS.md

> **Note:** This file contains Copilot CLI–specific guidance and review discipline.
> For general repository information applicable to all harnesses (architecture, validation, build commands, file format conventions), see `.github/copilot-instructions.md`.

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

## Repo-Local Maintainer Tooling

`profile-al-dev-shared/` is the shared authored plugin surface.

Maintain a strict boundary inside that tree:

- Shared authored content in `skills/`, `agents/`, most `knowledge/`, `markdown/`, and `bc-code-intel-knowledge/` must remain harness agnostic.
- Harness-mapping documentation such as `knowledge/harness-concepts.md` and `knowledge/agent-tool-projection-policy.md` may name Copilot CLI, Claude Code, and Codex explicitly.
- `profile-al-dev-shared/generated/agents/` contains generated harness-native projection artifacts and must not be edited by hand.

Before committing shared-content changes, run `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`.

`profile-al-dev-shared/generated/agents/` contains generated projection
artifacts for harness-native consumption. These files are derived outputs and
must not be edited by hand.

`.claude/agents/` and `.claude/skills/` are repo-local Claude maintainer
tooling. They may inspect shared source and generated projection artifacts
locally, but they are never part of the distributed plugin or projection
contract.

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

## Maintainer Validation

Run the shared-surface neutrality validator where you would normally run repo validators:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Checks:
- Shared authored files do not contain harness-branded instructions or tool tokens
- Harness-aware mapping docs are excluded by allowlist
- Generated projections are excluded because they are derived artifacts

## Diagram Guidance

When writing Mermaid diagrams, read
`profile-al-dev-shared/markdown/md-mermaid-helper.md` before generating
any diagram blocks.

---

## Harness Mapping

This table maps generic concept names (used in shared skills and agents) to their
concrete Copilot CLI equivalents. Maintained here so `align-harness-repos` can verify coverage.

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

## Plan Self-Review Requirement

Before submitting any plan for execution, the plan author MUST perform a
self-consistency pass:

1. **Token audit:** If the plan prohibits harness-specific tokens in output
   files, scan all *plan-specified file content* for those same tokens. Any
   occurrence in a code block example counts as a violation of the plan's own
   rule and must be resolved (genericise the example or add an explicit
   exception with reasoning) before execution begins.

2. **Constraint propagation check:** For every "must not contain X" rule in
   a spec, verify that no task step directs an agent to write content that
   contains X.

Unresolved contradictions at plan-review time cost 3× more to fix during
execution than at authoring time.

## Tiered Code Review Protocol

Per-task reviews check task-scope correctness. A **mid-point integration
review** must be scheduled at the halfway task (e.g. after Task 4 of 7) to
review the whole module assembled so far — not just the latest additions.

Integration review checklist additions (beyond per-task scope) — adapt to project type:
- [ ] All patterns/rules tested against the full input set, not just inputs
      introduced in the current task
- [ ] Deduplication / membership logic verified end-to-end across all
      functions added to date
- [ ] Interface names (flags, field names, API parameters) consistent across
      all definitions added so far

Shared parity reference: `profile-al-dev-shared/knowledge/verification-and-planning.md`.
Use it to keep Claude Code and Copilot CLI verification/planning behavior aligned.

## Known Environment Issues

### Python 3.13 / libexpat conflict (macOS)

`pytest` may fail with a libexpat dynamic-library conflict under Python 3.13
on macOS. Workaround: run tests inline:

```bash
python3.13 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('mod', 'path/to/script.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.some_function() == <expected_value>, 'Test failed'
print('PASS')
"
```

If `pytest` fails with a libexpat conflict, use this pattern as a fallback
for Python test verification in al-dev-shared sessions.
