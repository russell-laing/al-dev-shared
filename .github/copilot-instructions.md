# Copilot Instructions for al-dev-shared

## Repository Overview

`al-dev-shared` is a **shared plugin** for AL/BC development — a library of skills, agents, and knowledge documents consumed by AI harness profiles (Claude Code, Copilot CLI, Codex, etc.). This is **not** an AL project itself; it contains no `.al` source files.

### What This Repo Does

- **Skills** (`profile-al-dev-shared/skills/<name>/SKILL.md`) — Reusable workflows invoked by users (e.g., `/al-dev-plan`, `/al-dev-develop`)
- **Agents** (`profile-al-dev-shared/agents/<name>.md`) — Spawned by skills to execute specific tasks with system prompts and tool definitions
- **Knowledge** (`profile-al-dev-shared/knowledge/*.md`) — Shared documentation referenced by skills and agents
- **BC Code Intelligence Knowledge** (`profile-al-dev-shared/bc-code-intel-knowledge/`) — Specialist knowledge base for BC development

## Repository Structure

```
profile-al-dev-shared/
  skills/                    # 19 shared AL dev skills
    <skill-name>/
      SKILL.md              # Skill definition with YAML frontmatter
      <companion-files>     # Optional: validators, examples, templates
  agents/                    # Agent system prompts spawned by skills
  knowledge/                 # Workflow, pattern, and strategy knowledge
  bc-code-intel-knowledge/   # BC Code Intelligence specialist knowledge
  markdown/                  # Markdown and Mermaid style guides
.claude/                     # Claude Code profile (skills, agents, settings)
.claude-plugin/              # Marketplace registration metadata
docs/                        # Architecture maps and audit reports
scripts/                     # Validation and maintenance scripts
```

## Shared Surface Boundaries

Treat `profile-al-dev-shared/` as three distinct maintainer surfaces:

- **Shared authored content** — `skills/`, `agents/`, most `knowledge/`, `markdown/`, and `bc-code-intel-knowledge/`. This is the source of truth and must remain harness agnostic.
- **Intentional harness-mapping docs** — files such as `knowledge/harness-concepts.md` and `knowledge/agent-tool-projection-policy.md`. These may name harnesses and tool mappings explicitly because that is their purpose.
- **Generated projection artifacts** — `generated/agents/**`. These are derived harness-native outputs and must not be hand-edited.

Before committing changes to shared authored content, run `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`.

## File Format Conventions

### Skill Files

All skills are markdown files with YAML frontmatter:

```markdown
---
name: skill-name
description: >-
  Trigger description (used by AI to decide when to invoke).
argument-hint: "[optional args]"
---
# Skill instructions...
```

**Key patterns:**

- Reference knowledge via relative paths: `../../knowledge/workflow-routing.md`
- Spawn agents by name: `al-dev-shared:al-dev-developer`
- Multi-phase skills checkpoint to `.dev/progress.md` and check Phase 0 for resume capability
- All artifacts written to `.dev/` directory (not repo root)

### Agent Files

Each agent is a markdown file with YAML frontmatter:

```markdown
---
name: agent-name
description: Brief role summary
model: claude-opus-4-7  # or sonnet-4-6 / haiku-4-5
tools:
  - Tool1
  - Tool2
---
# System prompt (full agent instructions)
```

### Knowledge Files

Documentation files that explain patterns, workflows, and best practices. Referenced by skills via relative paths.

## Validation & Quality Checks

Run these Python validators **before committing**:

### Validate Agent Structure & Tools

```bash
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
```

Checks:

- All expected lens agents exist
- Skills reference only declared tools (no forbidden tools)
- Agent frontmatter is complete

### Validate Knowledge Quality

```bash
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge
```

Checks:

- Files reference examples or have clear structure
- Code keywords are followed by code blocks
- No stub sections or incomplete patterns

### Validate Shared-Surface Harness Neutrality

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Checks:

- Shared authored files do not contain harness-branded instructions or tool tokens
- Harness-aware mapping docs are excluded by allowlist
- Generated projections are excluded because they are derived artifacts

### Plugin Health Sweep

```bash
# Suggestions-only sweep — writes per-surface dossiers, never auto-edits
/audit-plugin-health --surface both
```

Dispatches design, quality, and naming lenses. Review the dossiers in `docs/health/` and use `/verify-map-suggestions` to act on accepted items.

## Commit Conventions

- **Gitmoji prefix** — Check `git log` for current style (e.g., `🐛 fix(agents):`, `✨ feat(skills):`, `📚 docs:`)
- **Ticket references** — Include `#FD<number>` for Freshdesk tickets in commit body
- **No `Co-Authored-By`** — Don't include AI attribution trailers
- **Git flags** — Use `git -C <path>` instead of `cd <path> && git` when operating on subdirectories

Example:

```
✨ feat(skills): add phase checkpoints to al-dev-plan

- Implement resume/restart logic via .dev/progress.md
- Phase 0 checks for existing progress and offers options
- Fixes #FD12345
```

## Key Architectural Patterns

### Complexity Routing

All skills classify tasks using `knowledge/workflow-routing.md`:

- **TRIVIAL** — Direct single-agent fix
- **SIMPLE** — Single-phase skill
- **MEDIUM** — Multi-phase skill with competitive analysis
- **COMPLEX** — Full multi-agent pipeline (planning, specialized reviewers, integration)

### Workflow Resilience

Multi-phase skills use checkpointing:

1. Phase 0 checks `.dev/progress.md` for resume capability
2. After each phase: checkpoint to `.dev/progress.md`
3. User can resume or restart

See `knowledge/workflow-resilience.md` for details.

### Artifact Naming Convention

All skill outputs go to `.dev/` directory:

```
.dev/
  progress.md                                  # Multi-phase checkpoints
  YYYY-MM-DD-al-dev-plan-solution-plan.md     # Solution plans
  YYYY-MM-DD-al-dev-develop-code-review.md    # Code reviews
  YYYY-MM-DD-al-dev-lint-lint-report.md       # Lint reports
  YYYY-MM-DD-al-dev-ticket-ticket-context.md  # Ticket contexts
```

Validator scripts find outputs via `find $AL_DEV_SHARED_PLUGIN_ROOT -name "validate-*.py"`.

## Harness Mapping

Generic skill/agent concepts map to concrete harness implementations. Keep the authored shared surface neutral; put named harness mappings here or in the dedicated knowledge mapping docs instead of back into shared operational content.

| Concept | Copilot CLI | Claude Code | Codex |
|---------|-------------|-------------|-------|
| **Instructions file** | `AGENTS.md` | `CLAUDE.md` | `AGENTS.md` |
| **Settings file** | `~/.copilot/settings.json` | `~/.claude/settings.json` | harness-local configuration |
| **Plugin root variable** | `AL_DEV_SHARED_PLUGIN_ROOT` | (filesystem path) | (filesystem path) |
| **Ask user** | `ask_user` tool | `AskUser` tool | `request_user_input` tool |
| **Explore agent** | `agent_type: "explore"` in task tool | `explore` agent in task tool | subagent or parallel developer-tool workflow |
| **MCP: AL** | `al-mcp-server-*` | `al-mcp-server-*` | `al-mcp-server-*` |
| **MCP: BC Code Intel** | `bc-code-intelligence-mcp-*` | `bc-code-intelligence-mcp-*` | `bc-code-intelligence-mcp-*` |

See `AGENTS.md` (Copilot CLI), `CLAUDE.md` (Claude Code), and the generated projections for harness-specific guidance.

## Documentation

- `docs/al-dev-plugin-map.md` — Skill inventory, Layer 1 lifecycle diagram, skill relationships
- `docs/agent-map.md` — Agent inventory, tool assignments, agent relationships
- `profile-al-dev-shared/markdown/md-mermaid-helper.md` — Mermaid diagram style guide

## Code Review & Planning

### Before Committing

1. **Run validators** — Ensure structure and quality checks pass
2. **Verify no forbidden patterns**:
   - `[date]` — unrendered template
   - `YYYY-MM-DD` (literal) — unrendered placeholder
   - `TODO` / `TBD` — incomplete work
   - `claude:` or `copilot:` prefixes — harness-specific debug tokens
3. **Self-review for token audit** — If your plan prohibits certain tokens, scan all code examples for violations

### Plan Execution

- Multi-phase changes should include a planning step using competitive architect review
- Integrate feedback from rubber-duck agent before implementing architectural changes
- Mid-point integration reviews for tasks spanning 7+ phases

## Known Issues

### Python 3.13 / libexpat Conflict (macOS)

`pytest` may fail with a libexpat dynamic-library conflict. Workaround:

```bash
python3.13 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('mod', 'path/to/test.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.test_function() == expected_value, 'Test failed'
print('PASS')
"
```

## Quick Reference

- **Sync docs with code**: Use `/review-skill-map` and `/review-agent-map` skills (Claude Code) to update maps
- **Audit design**: Use `/analyze-skill-design` and `/analyze-agent-design` (Claude Code) for architecture improvement suggestions
- **Check quality**: Use `/audit-skill-quality` and `/audit-agent-quality` (Claude Code) for structural issues
- **Run health sweep**: invoke `/audit-plugin-health` (suggestions-only; writes per-surface dossiers, no auto-fixes)
