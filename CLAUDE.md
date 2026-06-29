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

Claude Code consumes:

- **Shared skills** from `profile-al-dev-shared/skills/`
- **Generated agent projections** from `profile-al-dev-shared/generated/agents/claude/`
- **Shared knowledge** from `profile-al-dev-shared/knowledge/` and `profile-al-dev-shared/bc-code-intel-knowledge/`

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

**Maintainer skill workflow contracts:** `.claude/skills/` files may also contain a
`workflow:` block — a repo-local frontmatter extension consumed by
`scripts/generate_maintainer_guide.py` to auto-generate the
`docs/maintainer-tooling.md` summary and `docs/maintainer-tooling/` stage pages.
This block is invisible to Claude Code and all distributed harnesses. See
`.claude/knowledge/skill-workflow-contract.md` for the schema. Skills without a
`workflow:` block appear in the generator's "Missing contract" gap table; skills that
should stay out of the health audit loop must remain uncontracted.

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
model: opus  # or sonnet / haiku
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

**`.dev/` directory convention**: All skill artifacts are written here — progress checkpoints, solution plans, code reviews, lint reports, ticket contexts, requirements files. See `knowledge/artifact-contracts.md` for the per-skill contract governing which of these files are required, in what read-order, and what completion they evidence.

**Artifact contracts** (`knowledge/artifact-contracts.md`): Defines the durable handoff artifacts, resume read-order, and success-evidence requirements for each core skill. The key rule: a skill may not claim completion (ready, clean, validated) until it has read its named success-evidence file in the current run. Skills that implement this: `al-dev-plan`, `al-dev-develop`, `al-dev-review-develop`, `al-dev-fix`, `al-dev-commit`, `al-dev-lint`. Each implementing skill has an **Artifact Contract** section in its SKILL.md that cross-references this file.

**Validator scripts**: Some skills have companion Python validators (e.g., `skills/al-dev-plan/validate-plan.py`) that are run after output files are written. Skills look for these via `find ~/.claude/plugins -name "validate-*.py"`.

**Skill test scenarios** (`skills/<name>/tests/scenarios.yaml`): Regression corpora protecting behavioral invariants for individual skills. Each scenario defines a user request, expected trigger/no-trigger outcome, and a rationale. Add scenarios when a misfire (false trigger) or miss (failure to trigger) is fixed to prevent regression. These coexist with validator scripts but test trigger behavior rather than output correctness. See `knowledge/skill-test-format.md` for the full YAML schema.

## Commit Conventions

project-type: tool
Full spec: profile-al-dev-shared/knowledge/commit-conventions.md

## Development Commands

See `docs/development-commands.md` for the full command reference (validation, pre-commit gate, projections, documentation map regeneration).

## Plugin Architecture Quick Reference

**Start here:** `docs/al-dev-skills-map.md` (Layer 1 lifecycle diagram shows the three entry points and how skills connect)

**Maintainer surface:** `docs/maintainer-tooling.md` (five-stage summary with detailed pages under `docs/maintainer-tooling/` for the repo-local `.claude/` tooling, which the Layer 1 distributed-skills diagram intentionally excludes — see `docs/al-dev-skills-map.md` scope note)

**Active skills:** 24 distributed skills covering three main flows:

1. **Ticket/Support flow** (`al-dev-ticket` → `al-dev-support-reply`)
2. **Development flow** (`al-dev-investigate` → `al-dev-plan` → `al-dev-develop` → `al-dev-commit`)
3. **Direct fix flow** (`al-dev-fix` for trivial changes)

**Pre-planning tributaries (optional):** `al-dev-explore`, `al-dev-interview`, `al-dev-perf`

**Post-commit outputs:** `al-dev-release-notes`, `al-dev-handoff`, `al-dev-document`, `commit-recover`

**Sub-skills & utilities:** `al-dev-plan-preflight`, `al-dev-plan-with-critics`, `al-dev-plan-final-review`, `al-dev-commit-preflight`, `al-dev-commit-execute`, `al-dev-review-develop-preflight`, `al-dev-help`, `verify-commits`

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
   - date placeholder like `2026-05-15` — unrendered template
   - literal ISO date text — unrendered date placeholder
   - incomplete-work markers — incomplete work
   - `Co-Authored-By` in code comments — AI attribution (OK in git trailers)
   - `claude:` or `copilot:` prefixed comments — harness debug tokens left in

3. **Content acceptance criteria** — File content matches spec in commit message

4. **Skill/agent validation** — If editing skills or agents:

   ```bash
   python3 scripts/validate_lens_agents.py --path profile-al-dev-shared/agents
   ```

5. **No unprompted destructive git actions** — Do not perform branch deletion,
   `git reset --hard`, `git push --force`, or any other destructive version-control
   operation unless the user has explicitly requested it in the current turn.

---

## Plan Task Verification Standard

Every plan task must end with a verification step before its commit:

1. **File persistence check:** `git status` shows expected file changes (not empty, no unexpected extras)
2. **Forbidden pattern scan:** No forbidden patterns in changed files (same list as Verification Before Commit §2)
3. **Acceptance criteria verification:** Each acceptance criterion stated in the task spec is met in actual file content
4. **Failure recovery:** On verification failure:
   - Re-execute the task with the specific failures embedded in context
   - Cap at 3 total retries per task
   - After 3 failures, escalate to user with a summary of what failed and why

When dispatching subagents to execute plan tasks (both Claude Code and Copilot CLI),
pass the above checklist in the dispatch prompt so subagents self-verify before returning.

## Artifact Lifecycle and Cleanup

Skills that write output to `.dev/` or `docs/superpowers/` must follow these
lifecycle rules:

**Temporary Artifacts** (removed at task completion):

- Dated research files: `.dev/YYYY-MM-DD-*.md` — one-off investigation outputs
- Working checkpoints: `.dev/*-progress.md`, `.dev/*-checkpoint.json`
- Intermediate findings: `.dev/discover-*-findings.md` (before report phase)
- Unused review docs: `.dev/review-*.md` that didn't become part of main output

**Persistent Artifacts** (committed to git):

- Core tracking files: `.dev/progress.md` (resume pointer for multi-phase skills)
- Disposition ledger: `docs/health/dispositions*.md`, `docs/health/dispositions-events/`,
  `docs/health/dispositions-history/`
- Generated documentation: `docs/al-dev-*.md`, `.claude/knowledge/`, etc.
- Durable planning provenance: `docs/superpowers/history.md` and
  `docs/superpowers/README.md`
- Legacy tracked raw plan/spec files may remain as readonly historical references
  until they are retired deliberately; do not add to that set during normal work

**Cleanup Expectations by Skill Type**:

- **Investigation skills** (`discover-*`, `research-*`): Remove `.dev/YYYY-MM-DD-*.md`
  files after rolling findings into structured output (`.dev/findings.md` or
  `docs/health/` entries). Checkpoints are auto-removed after success.

- **Planning skills** (`writing-plans`, `plan-*-findings`): Temporary specs go in
  `docs/superpowers/specs/` (gitignored). Remove dated spec files after plan is
  written to `docs/superpowers/plans/`. Raw plan files under
  `docs/superpowers/plans/` are working artifacts, not durable outputs; record
  durable provenance in `docs/superpowers/history.md` instead of force-adding
  new plan/spec markdown files.

- **Audit/Review skills** (`audit-*`, `report-*`): Remove intermediate working
  files (e.g. `.dev/audit-work-*.json`, `.dev/review-draft.md`). Keep only final
  dossiers and reports.

**Cleanup Checklist** (every multi-phase skill MUST perform before returning):

- [ ] All `.dev/YYYY-MM-DD-*.md` research/investigation files removed
- [ ] All `.dev/*-work*.json` or `.dev/*-draft*` files removed
- [ ] Progress checkpoints cleaned up (only `.dev/progress.md` remains if needed)
- [ ] No new raw markdown files are staged from `docs/superpowers/plans/`,
  `docs/superpowers/plans/archived/`, or `docs/superpowers/specs/`
- [ ] Final outputs (plans, reports, dossiers) are in their persistent locations
- [ ] If `git status` shows any `.dev/` or raw `docs/superpowers/` artifact files
  staged for commit, verify they are intentional (usually they shouldn't be)

**Prevention:** The pre-commit hook (`.githooks/pre-commit`) runs
`scripts/validate-artifact-leaks.py` to catch dated scratch files, named
progress files, and raw Superpowers plan/spec markdown before commit. If caught,
abort commit and clean up before re-attempting.

## Subagent-Driven Development Best Practices

When dispatching subagents via `superpowers:subagent-driven-development`:

**Permission Pre-Flight:** Before dispatching, verify required tool permissions are
pre-authorized:

- File creation/modification → `Write`, `Edit`
- Testing → `Bash` with test runner allowed

Check `.claude/settings.json` for the `allowedTools` list. If required tools are
missing, prompt the user to grant permissions before dispatch to avoid permission
blocks forcing fallback to serial execution.

**Output Verification:** After subagents complete, independently verify all files:

1. Check file existence: `ls -la <claimed-file-path>`
2. Verify content matches claims (function signatures present, no truncation)
3. If a file is missing or empty, re-dispatch the subagent with error context

This prevents silent subagent failures from being discovered downstream.

## Planning Routing

For tasks that need a design decision:

**SMALL/TRIVIAL** (single file, clear requirements, no alternatives):

- Use `superpowers:writing-plans` directly if requirements are unambiguous
- Skip the architect debate phase; the extra tokens and time aren't justified

**MEDIUM** (4+ files, novel architecture, OR ambiguous requirements):

- **Prefer** `/al-dev-plan` to run the competitive architect debate
- This adds ~90–120 seconds and 20–40% token overhead vs `writing-plans` alone
- Then use `superpowers:writing-plans` to convert the winning design into a task plan

**LARGE/COMPLEX** (multiple subsystems, major refactor, strategic decision):

- **Always** use `/al-dev-plan` with mandatory architect debate
- Do NOT use `writing-plans` alone for large scope
- Consider escalating to user for requirements review before planning

**Anti-pattern to avoid:**

- Using `writing-plans` alone for MEDIUM+ work skips adversarial review and increases wrong-approach risk
- If you're unsure whether a task is SMALL or MEDIUM, default to MEDIUM and use `al-dev-plan`

Shared parity reference: `profile-al-dev-shared/knowledge/verification-and-planning.md`.

## Plan & Spec Writing

- **File persistence verification:** When writing implementation plans or
  specification files, immediately verify the file was written to disk and
  confirm its path before reporting completion. Do not claim the plan is
  complete until `ls -la <path>` confirms the file exists.

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

## Documentation & Markdown Quality

- **Markdownlint compliance:** All generated or modified markdown files must pass
  `markdownlint` (unique headings, blank lines around headings/lists, language
  specifiers on code blocks). Run verification before committing markdown changes.
- **Count verification:** When reporting a count of skills, agents, or other
  enumerable plugin surfaces, verify it by running
  `find <dir> -name "SKILL.md" | wc -l` (skills) or
  `find <dir> -name "*.md" | wc -l` (agents) and cross-checking against any
  manually-enumerated list. Avoid `ls | wc -l` — it overcounts if non-target
  files or subdirectories exist. Never state a count without cross-checking
  against the filesystem.

## Plan Self-Review Requirement

Before submitting any plan for execution, the plan author MUST perform a
self-consistency pass:

1. **Token audit:** If the plan prohibits harness-specific tokens in output files, scan all *plan-specified file content* for those same tokens. Any occurrence in a code block example counts as a violation and must be resolved (genericise the example or add an explicit exception) before execution begins.

2. **Constraint propagation check:** For every "must not contain X" rule in a spec, verify that no task step directs an agent to write content that contains X.

## File & Reference Verification

Before referencing scripts, files, or validators in skills, specs, or plans,
verify they still exist in the repo (not archived, renamed, or moved). Use `find`
or `git ls-files` to confirm before writing them into tasks.

## Tiered Code Review Protocol

Per-task reviews check task-scope correctness. A **mid-point integration
review** must be scheduled at the halfway task (e.g. after Task 4 of 7) to
review the whole module assembled so far — not just the latest additions.

Integration review checklist additions (beyond per-task scope) — adapt to project type:

- [ ] All patterns/rules tested against the full input set, not just inputs introduced in the current task
- [ ] Deduplication / membership logic verified end-to-end across all functions added to date
- [ ] Interface names (flags, field names, API parameters) consistent across all definitions added so far

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

## Tool Usage

Use the Agent tool to dispatch audit and health teams. Do not use RemoteTrigger —
it fails schema validation in this repo's workflows.

## Skill Invocation

Before invoking any health or plan skill, confirm argument names match the
skill's contract. `tooling` and `plugin` are surface values; `design`, `quality`,
`naming`, and `all` are dimension values. Passing a surface as `--dimension`
stalls the run silently.

## Plugin Health / Disposition Workflow

When parsing findings for disposition (in `/record-plugin-dispositions` or any
skill that calls `health_disposition_store.py filter_findings`), verify that the
parsed finding count matches the total findings count in the source file before
proceeding. Bullet-format and table-format findings must both be counted. If the
counts diverge, stop and report the discrepancy rather than silently continuing
with a partial list.

## Health Ledger

After appending any `fixed` ledger events, sync them to the correct month shard
under `docs/health/dispositions-history/` using `sync_shard --since`:

```bash
python3 scripts/health_disposition_store.py sync_shard --since <today's ISO date>
```

(The `/implement-plugin-health` Phase 3 "Sync the history shard" step does exactly
this.) Do not declare the loop closed until shard presence is verified
(`grep <fixed-event-id> docs/health/dispositions-history/<year>/<month>.md`).
