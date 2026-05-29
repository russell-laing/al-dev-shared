# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## What This Repo Is

`al-dev-shared` is a **shared AI development plugin** — a unified library of AL/BC development skills, agents, and knowledge documents consumed by three AI coding harnesses:

- **Claude Code** (claude.ai/code) — Desktop app, CLI, and IDE extensions
- **Copilot CLI** — Autonomous command-line agent (see `AGENTS.md`)
- **Codex** — Autonomous development system (see `CODEX.md`)

It maintains one canonical authored surface (`profile-al-dev-shared/`) and generates harness-native projection artifacts for each consumer. This document covers Claude Code registration and usage; refer to `AGENTS.md` (Copilot CLI) and `CODEX.md` (Codex) for harness-specific guidance.

This repository is not itself an AL project; it contains no `.al` source files.

### Claude Code Registration

`al-dev-shared` is registered in `~/.claude/settings.json` as:

```json
"al-dev-shared": {
  "source": { "source": "directory", "path": "/Users/russelllaing/al-dev-shared" }
}
```

Claude Code consumes:
- **Shared skills** from `profile-al-dev-shared/skills/`
- **Generated agent projections** from `profile-al-dev-shared/generated/agents/claude/`
- **Shared knowledge** from `profile-al-dev-shared/knowledge/` and `bc-code-intel-knowledge/`

## Shared Plugin Surface (All Harnesses)

All three harnesses consume the same authored source:

```text
profile-al-dev-shared/          # Canonical authored plugin surface
  skills/<name>/SKILL.md        # Skill definitions (invoked as /name)
  agents/<name>.md              # Agent definitions (harness-neutral)
  knowledge/                    # Generic workflow knowledge
  bc-code-intel-knowledge/      # BC Code Intelligence specialist knowledge
  markdown/                     # Markdown and Mermaid style guides
.claude-plugin/marketplace.json # Marketplace registration (Claude Code only)
```

## Generated Projection Artifacts (Per-Harness Native Formats)

For harness-native tool execution, the projection layer generates harness-specific artifacts:

```text
profile-al-dev-shared/generated/agents/
  claude/                       # Claude Code-native agent projections (Markdown)
  copilot/                      # Copilot CLI-native agent projections (Markdown)
  codex/                        # Codex-native agent projections (TOML)
```

Each projection applies the mappings from `knowledge/agent-tool-projection-policy.md` to translate generic capability names (e.g., `USER_GATE`, `Read`, `Bash`) into harness-native tool names (e.g., `AskUserQuestion`, `read`, `execute`).

**Key rule:** Shared source is canonical; generated artifacts are derived output and must never be hand-edited.

## Repo-Local Maintainer Tooling

`profile-al-dev-shared/` is the shared authored plugin surface distributed to all three harnesses.

`.claude/agents/` and `.claude/skills/` contain Claude Code-specific maintainer tooling used to review, audit, and improve the shared plugin surface. This tooling is currently Claude-specific; future harnesses may have parallel tooling (`.agents/`, `.codex/`, etc.).

**Output boundary rule:** While the maintainer tooling is harness-specific, its **outputs must be harness-agnostic**:
- Any documents written to the shared surface or `.dev/` directory must not contain harness-specific tokens
- Changes made to shared files must use generic vocabulary (from `knowledge/harness-concepts.md`)
- Generated artifacts remain the output of the projection layer, never hand-edited by maintainer tooling

Repo-local tooling may *inspect* shared source and generated projection outputs for analysis, but its modifications or documents must maintain neutrality across all three harnesses.

## Skill File Format

Each skill is a markdown file in `profile-al-dev-shared/skills/<name>/SKILL.md` with YAML frontmatter:

```markdown
---
name: skill-name
description: >-
  Trigger description (auto-invoked when user request matches).
  Used by Claude to decide whether to invoke this skill.
argument-hint: "[optional args]"
---
# Skill instructions...
```

**Key patterns:**

- Skills reference knowledge via relative paths (e.g., `../../knowledge/workflow-routing.md`)
- Agents are spawned by name (e.g., `al-dev-shared:al-dev-developer`)
- Phase 0 of multi-phase skills checks `.dev/progress.md` for resume capability
- All artifacts written to `.dev/` directory (not the project root)

## Agent File Format

Each agent is a markdown file in `profile-al-dev-shared/agents/<name>.md` with YAML frontmatter:

```markdown
---
name: agent-name
description: Brief summary of agent role
model: claude-opus-4-7  # or sonnet-4-6 / haiku-4-5
tools:

  - Tool1
  - Tool2

---
# System prompt (the full agent instructions)
```

**Agent naming:** Agents referenced by skills use `al-dev-shared:<agent-name>` format.

## Key Architectural Patterns

**Complexity routing** (`knowledge/workflow-routing.md`): All skills classify tasks as TRIVIAL / SIMPLE / MEDIUM / COMPLEX and route accordingly. TRIVIAL → direct fix; COMPLEX → full multi-agent pipeline.

**Workflow resilience** (`knowledge/workflow-resilience.md`): Multi-phase skills checkpoint to `.dev/progress.md` after each phase. Phase 0 of every multi-phase skill checks this file and offers resume/restart.

**`.dev/` directory convention**: All skill artifacts are written here — progress checkpoints, solution plans (`YYYY-MM-DD-al-dev-plan-solution-plan.md`), code reviews (`YYYY-MM-DD-al-dev-develop-code-review.md`), lint reports (`YYYY-MM-DD-al-dev-lint-lint-report.md`), ticket contexts, requirements files. See `knowledge/artifact-contracts.md` for the per-skill contract governing which of these files are required, in what read-order, and what completion they evidence.

**Artifact contracts** (`knowledge/artifact-contracts.md`): Defines the durable handoff artifacts, resume read-order, and success-evidence requirements for each core skill. The key rule: a skill may not claim completion (ready, clean, validated) until it has read its named success-evidence file in the current run. Skills that implement this: `al-dev-plan`, `al-dev-develop`, `al-dev-review-develop`, `al-dev-fix`, `al-dev-commit`, `al-dev-lint`. Each implementing skill has an **Artifact Contract** section in its SKILL.md that cross-references this file.

**Validator scripts**: Some skills have companion Python validators (e.g., `skills/al-dev-plan/validate-plan.py`) that are run after output files are written. Skills look for these via `find ~/.claude/plugins -name "validate-*.py"`.

**Skill test scenarios** (`skills/<name>/tests/scenarios.yaml`): Regression corpora protecting behavioral invariants for individual skills. Each scenario defines a user request, expected trigger/no-trigger outcome, and a rationale. Add scenarios when a misfire (false trigger) or miss (failure to trigger) is fixed to prevent regression. These coexist with validator scripts but test trigger behavior rather than output correctness. See `knowledge/skill-test-format.md` for the full YAML schema.

## Compile/Lint

Skills that run AL compilation use:

```bash
al-compile --output .dev/compile-errors.log
```

This command applies to AL projects *using* this plugin, not to this repo itself. The full procedure is in `knowledge/compile-lint-procedure.md`.

## Commit Conventions

project-type: tool
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md

## Development Commands

Common commands for maintaining the shared plugin surface:

### Validation (All Harnesses)

```bash
# Validate that shared source has no harness-specific leakage
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared

# Validate agent structure (frontmatter, tools, model assignment)
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents

# Validate knowledge file quality
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge

# Validate that skills honour the artifact-contract matrix
python3 scripts/validate_artifact_contracts.py
```

### Projection (Harness-Native Artifacts)

```bash
# Regenerate all harness projections after shared agent/policy changes
python3 scripts/generate-agent-projections.py

# Verify generated artifacts match shared source across all three harnesses
# (run after any projection policy or agent updates)
```

### Plugin Health and Documentation

```bash
# Run the suggestions-only health sweep (writes per-surface dossiers; never auto-edits)
/plugin-health --surface both
```

### Updating Documentation Maps

When skills or agents change, synchronize the documentation:

```bash
# Within Claude Code, use these skills in sequence:
/review-skill-map        # Update profile-al-dev-shared skills vs. docs/al-dev-plugin-map.md
/review-agent-map        # Update profile-al-dev-shared agents vs. docs/al-dev-agent-map.md
/analyze-skill-design    # Generate architecture improvement suggestions
/analyze-agent-design    # Generate agent design improvement suggestions
```

These skills write findings to:

- `docs/al-dev-plugin-map.md` — Skill inventory and relationships
- `docs/al-dev-agent-map.md` — Agent inventory and tool assignments
- `docs/al-dev-skill-quality.md` — Skill clarity and structural issues
- `docs/al-dev-agent-quality.md` — Agent quality audit results

## Plugin Architecture Quick Reference

**Start here:** `docs/al-dev-plugin-map.md` (Layer 1 lifecycle diagram shows the three entry points and how skills connect)

**Active skills:** 19 distributed skills covering three main flows:

1. **Ticket/Support flow** (`al-dev-ticket` → `al-dev-support-reply-drafter`)
2. **Development flow** (`al-dev-investigate` → `al-dev-plan` → `al-dev-develop` → `al-dev-commit`)
3. **Direct fix flow** (`al-dev-fix` for trivial changes)

**Pre-planning tributaries (optional):** `al-dev-explore`, `al-dev-interview`, `al-dev-perf`

**Post-commit outputs:** `al-dev-release-notes`, `al-dev-handoff`, `al-dev-document`, `commit-recover`

## Diagram Guidance

When writing Mermaid diagrams, read
`profile-al-dev-shared/markdown/md-mermaid-helper.md` before generating
any diagram blocks.

## Verification Before Commit

Before committing changes:

1. **File persistence check**

   ```bash
   git status              # Shows expected file changes
   wc -l <file>           # Verify line counts unchanged for automated edits
   ```

2. **Forbidden patterns scan** — Check for unfinished work:
   - `[date]` like `[2026-05-15]` — unrendered template
   - `YYYY-MM-DD` as literal string — unrendered date placeholder
   - `TODO` or `TBD` — incomplete work
   - `Co-Authored-By` in code comments — AI attribution (OK in git trailers)
   - `claude:` or `copilot:` prefixed comments — harness debug tokens left in

3. **Content acceptance criteria** — File content matches spec in commit message

4. **Skill/agent validation** — If editing skills or agents:

   ```bash
   python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
   ```

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
