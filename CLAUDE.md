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

## Diagram Guidance

When writing Mermaid diagrams, read
`profile-al-dev-shared/markdown/md-mermaid-helper.md` before generating
any diagram blocks.

---

## Plan Task Verification Standard

Every plan task must end with a verification step before its commit:

1. **File persistence check:** `git status` shows expected file changes (not empty, no unexpected extras)
2. **Forbidden pattern scan:** No forbidden patterns in changed files:
   - `[date]` (e.g., `[2026-05-15]`) — indicates unrendered template
   - `YYYY-MM-DD` (literal string, not date value) — unrendered date placeholder
   - `TODO` or `TBD` — incomplete work
   - `Co-Authored-By` — AI attribution in code comments (not git trailers)
   - `claude:` or `copilot:` prefixed comments — harness-specific debugging left in
3. **Acceptance criteria verification:** Each acceptance criterion stated in the task spec is met in actual file content
4. **Failure recovery:** On verification failure:
   - Re-execute the task with the specific failures embedded in context
   - Cap at 3 total retries per task
   - After 3 failures, escalate to user with a summary of what failed and why

When dispatching subagents to execute plan tasks (both Claude Code and Copilot CLI),
pass the above checklist in the dispatch prompt so subagents self-verify before returning.

## Planning Routing

For tasks that need a design decision:

**SMALL/TRIVIAL** (single file, clear requirements, no alternatives):
- Use `superpowers:writing-plans` directly if requirements are unambiguous
- Skip the architect debate phase; the extra tokens and time aren't justified

**MEDIUM** (4+ files, novel architecture, OR ambiguous requirements):
- **Prefer** `/al-dev-plan` to run the competitive architect debate
- This adds ~90–120 seconds and 20–40% token overhead vs `writing-plans` alone
- Then use `superpowers:writing-plans` to convert the winning design into a task plan
- **Why:** Adversarial review catches wrong-approach risks early; rework later is 3× more expensive

**LARGE/COMPLEX** (multiple subsystems, major refactor, strategic decision):
- **Always** use `/al-dev-plan` with mandatory architect debate
- Do NOT use `writing-plans` alone for large scope
- Consider escalating to user for requirements review before planning

**Anti-pattern to avoid:**
- Using `writing-plans` alone for MEDIUM+ work skips adversarial review and increases wrong-approach risk
- If you're unsure whether a task is SMALL or MEDIUM, default to MEDIUM and use `al-dev-plan`

Shared parity reference: `profile-al-dev-shared/knowledge/verification-and-planning.md`.

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
