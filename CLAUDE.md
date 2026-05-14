# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

`al-dev-shared` is a **Claude Code plugin marketplace** — a shared library of AL/BC development skills, agents, and knowledge documents consumed by Claude Code profiles. It is not an AL project itself; it contains no `.al` source files.

It is registered in `~/.claude/settings.json` as:
```json
"al-dev-shared": {
  "source": { "source": "directory", "path": "/Users/russelllaing/al-dev-shared" }
}
```

## Structure

```
profile-al-dev-shared/          # The plugin consumed by Claude Code
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
  Trigger description used by Claude to auto-invoke.
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

**Validator scripts**: Some skills have companion Python validators (e.g., `skills/al-dev-plan/validate-plan.py`) that are run after output files are written. Skills look for these via `find ~/.claude/plugins -name "validate-*.py"`.

## Compile/Lint

Skills that run AL compilation use:
```bash
al-compile --output .dev/compile-errors.log
```
This command applies to AL projects *using* this plugin, not to this repo itself. The full procedure is in `knowledge/compile-lint-procedure.md`.

## Commit Conventions

project-type: tool
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md

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
