# Design: Harness Engineering Demo — Three Maintainer Improvements (Wave 2)

**Date:** 2026-05-29
**Goal:** Adapt three remaining patterns from `coleam00/harness-engineering-demo` to strengthen `profile-al-dev-shared` solution plan quality and maintainer feedback loops
**Scope:** Per-task planning fields in solution plan template; two Claude Code maintainer hooks
**Effort:** ~75 minutes total
**Source:** https://github.com/coleam00/harness-engineering-demo

---

## Background

Wave 1 (2026-05-28) adapted pattern references, constrained acceptance criteria, pre-commit compile
gate, investigation tightening, and intent-preflight completion from the same demo. Three patterns
were not addressed in Wave 1:

1. The demo's plan format requires each task to include `Gotcha:` and `Validate:` fields — the architect
   identifies project-specific pitfalls and exact validation commands per task, not just for the feature overall.
2. The demo's `post_tool_use_lint.py` runs validators after every file edit (advisory, exits 0).
3. The demo's `stop_validate.py` blocks turn completion until quality gates pass.

Previous spec: `docs/superpowers/specs/2026-05-28-harness-demo-three-improvements-design.md`

---

## Existing Coverage Reviewed

- `knowledge/solution-plan-template.md` — has Pattern reference per object and constrained
  Acceptance Criteria per feature. No implementation tasks section with per-task `Gotcha:` or
  `Validate:` fields.
- `.claude/settings.json` — `hooks: {}` (empty). No PostToolUse or Stop hooks in the project.
- `~/.claude/settings.json` — has a pyright PostToolUse hook for `.py` files only. No shared-surface
  validators.
- `profile-al-dev-shared/generated/agents/` — projection regeneration is a manual step
  (`python3 scripts/generate-agent-projections.py`). CLAUDE.md documents it but no automated
  enforcement exists.

---

## Change 1: Per-task `Gotcha:` and `Validate:` in the Solution Plan

### Problem

The solution plan template produces object-level Pattern references and a feature-level Acceptance
Criteria section. It has no implementation task structure. When `al-dev-developer` works from a
solution plan, it has no per-task guidance for common AL pitfalls or per-task validation checkpoints.
Regressions and anti-patterns are only caught at the end (compile gate, code review) rather than at
each task boundary.

The demo's plan format addresses this directly: each task has a `Gotcha:` (project-specific trap)
and `Validate:` (exact shell command). The architect is best placed to supply both — it has already
researched the codebase and knows the risk surface for each task.

### Addition to `knowledge/solution-plan-template.md`

Add a new `### Implementation Tasks` section at the same `###` level as `### Implementation Notes`,
placed between `### Implementation Notes` and `### Acceptance Criteria`:

```markdown
### Implementation Tasks

**Task 1: [name]**
Files: [files to create or modify]
Gotcha: [one project-specific pitfall — e.g., "object names must be ≤30 chars; verify before
  creating" or "var parameters from AL MCP must be verified before use in subscribers"]
Validate: [exact shell command confirming this task is done — e.g.,
  `grep -rn "procedure ValidatePostingDate" src/` or
  `grep -c "error AL" .dev/compile-errors.log | grep -q "^0$"`]

**Task 2: [name]**
Files: ...
Gotcha: ...
Validate: ...
```

When no shell command is possible:

```markdown
Validate: [manual] — [what to check visually]
```

Rules:
- `Gotcha:` is required. Write `Gotcha: none — no project-specific pitfall identified` rather than
  omitting it.
- `Validate:` is required. Write `Validate: [manual] — [description]` rather than omitting it.
- Tasks here are the architect's logical implementation units. They inform (but do not replace) the
  detailed sub-task checklist produced by `writing-plans`.

### Addition to `agents/al-dev-solution-architect.md`

In the `## Output Format` section, extend the existing bullet list that describes what the solution
plan must include. After the current `**Acceptance Criteria section:**` bullet, add:

```markdown
- **Implementation Tasks section:** Add a `### Implementation Tasks` section listing each
  logical implementation unit. For each task include:
  - `Files:` — files to create or modify
  - `Gotcha:` — the most likely project-specific pitfall for this task. Consult
    `knowledge/al-developer-patterns.md` for known AL/BC traps (object name length,
    var parameter verification, bash regex line-collapse). Write one concrete warning;
    write `none — [rationale]` if no pitfall applies.
  - `Validate:` — an exact shell command the developer runs after completing this task
    to confirm it is done. Prefer `grep`, `wc -l`, or `al-compile` checks. Write
    `[manual] — [description]` if no shell command suffices.
```

### Files Changed

- `profile-al-dev-shared/knowledge/solution-plan-template.md`
- `profile-al-dev-shared/agents/al-dev-solution-architect.md`

---

## Change 2: PostToolUse Auto-Validation Hook

### Problem

Harness-specific tokens and agent structure errors in shared surface files are caught at commit time
via `validate_harness_neutrality.py` and `validate-lens-agents.py`. The demo's `post_tool_use_lint.py`
demonstrates that running validators after every edit gives immediate feedback and keeps the
correction loop tight. No hooks exist in this project's `.claude/settings.json`.

This change is advisory only. The hook must fail open on malformed payloads or command errors and
must not block editing.

### Hook Behavior

**File:** `.claude/hooks/post_edit_validate.py`

The hook reads the tool event from stdin as JSON and extracts the changed file path from the active
harness's edit payload. If the payload does not expose a usable file path, the hook exits 0 without
side effects.

```python
import sys, json, subprocess, os

try:
    event = json.load(sys.stdin)
    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if not file_path:
        sys.exit(0)

    project_root = os.environ.get("CLAUDE_PROJECT_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    shared_prefix = os.path.join(project_root, "profile-al-dev-shared")
    generated_prefix = os.path.join(shared_prefix, "generated")
    agents_prefix = os.path.join(shared_prefix, "agents")

    abs_path = os.path.abspath(file_path)

    if abs_path.startswith(shared_prefix) and not abs_path.startswith(generated_prefix):
        result = subprocess.run(
            ["python3", os.path.join(project_root, "scripts", "validate_harness_neutrality.py"), shared_prefix],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("[post-edit] harness-neutrality: OK")
        else:
            print("[post-edit] harness-neutrality: issues found — fix before committing")
            print(result.stdout[:500])

    if abs_path.startswith(agents_prefix) and abs_path.endswith(".md"):
        result = subprocess.run(
            ["python3", os.path.join(project_root, "scripts", "validate-lens-agents.py"),
             "--path", agents_prefix],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("[post-edit] agent-structure: OK")
        else:
            print("[post-edit] agent-structure: issues found")
            print(result.stdout[:500])

except Exception:
    pass  # Fail open — never block on hook error

sys.exit(0)
```

Advisory only — always exits 0. Skips generated artifacts (projections are not validated this way).

### Hook Registration

**File:** `.claude/settings.json`

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /Users/russelllaing/al-dev-shared/.claude/hooks/post_edit_validate.py"
          }
        ]
      }
    ]
  }
}
```

### Files Changed

- `.claude/hooks/post_edit_validate.py` (new file)
- `.claude/settings.json`

---

## Change 3: Stop Hook for Stale Projections

### Problem

When agent source files in `profile-al-dev-shared/agents/` are modified, `generate-agent-projections.py`
must be re-run before committing. CLAUDE.md documents this requirement but it is easy to forget
during multi-file editing sessions. The demo's `stop_validate.py` demonstrates a pattern for
blocking turn completion when session-end quality requirements are not met.

This change is also advisory only with one narrow exception: it may block turn completion when
agent sources changed and projections are stale, but it must fail open on any ambiguous state that
cannot be verified locally.

### Hook Behavior

**File:** `.claude/hooks/stop_projection_check.py`

```python
import sys, json, subprocess, os

try:
    event = json.load(sys.stdin)

    # Prevent infinite blocking: if hook already fired once this stop, pass through
    if event.get("stop_hook_active"):
        sys.exit(0)

    project_root = os.environ.get("CLAUDE_PROJECT_DIR",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    tracked = subprocess.run(
        ["git", "-C", project_root, "diff", "--name-only", "HEAD"],
        capture_output=True, text=True
    )
    staged = subprocess.run(
        ["git", "-C", project_root, "diff", "--cached", "--name-only"],
        capture_output=True, text=True
    )
    untracked = subprocess.run(
        ["git", "-C", project_root, "ls-files", "--others", "--exclude-standard"],
        capture_output=True, text=True
    )
    changed = (tracked.stdout + staged.stdout + untracked.stdout).splitlines()

    agent_changes = [f for f in changed if "profile-al-dev-shared/agents/" in f and f.endswith(".md")]
    generated_changes = [f for f in changed if "profile-al-dev-shared/generated/agents/" in f]

    if agent_changes and not generated_changes:
        reason = (
            "Agent source files modified but projections not regenerated.\n"
            "Run: python3 scripts/generate-agent-projections.py\n"
            f"Modified agents: {', '.join(agent_changes)}"
        )
        print(f"[stop-hook] warning: {reason}", file=sys.stderr)
        print(json.dumps({"decision": "block", "reason": reason}))
        sys.exit(0)

except Exception:
    pass  # Fail open

sys.exit(0)
```

The `stop_hook_active` guard (from the demo) prevents infinite blocking: if Claude attempts to stop
a second time after already being blocked, the hook passes through. This handles the case where
`generate-agent-projections.py` fails and Claude cannot resolve the block.

When the hook blocks, Claude is re-prompted and should run `python3 scripts/generate-agent-projections.py`
before attempting to stop again.

### Hook Registration

**File:** `.claude/settings.json` — extend alongside the PostToolUse hook:

```json
{
  "hooks": {
    "PostToolUse": [...],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /Users/russelllaing/al-dev-shared/.claude/hooks/stop_projection_check.py"
          }
        ]
      }
    ]
  }
}
```

### Files Changed

- `.claude/hooks/stop_projection_check.py` (new file)
- `.claude/settings.json`

---

## Combined Scope Summary

| Change | Files | Risk |
|--------|-------|------|
| 1 — Gotcha + Validate in solution plan | `solution-plan-template.md`, `al-dev-solution-architect.md` | Low — additive planning guidance |
| 2 — PostToolUse validation hook | `.claude/hooks/post_edit_validate.py`, `settings.json` | Medium — advisory, fails open, payload schema must be verified during implementation |
| 3 — Stop hook for stale projections | `.claude/hooks/stop_projection_check.py`, `settings.json` | Medium — block-with-remedy, `stop_hook_active` guard, includes untracked-file check, fails open on ambiguity |

**New files:** 2 hook scripts  
**Modified files:** `solution-plan-template.md`, `al-dev-solution-architect.md`, `settings.json`

---

## Acceptance Criteria

1. `knowledge/solution-plan-template.md` contains a `### Implementation Tasks` section with
   `Gotcha:` and `Validate:` fields shown per task, and rules making both fields required.
2. `agents/al-dev-solution-architect.md` `## Output Format` section requires the architect to
   populate `Gotcha:` and `Validate:` per task, referencing `knowledge/al-developer-patterns.md`.
3. `.claude/hooks/post_edit_validate.py` exists; runs harness-neutrality validator on any
   shared surface edit, additionally runs agent-structure validator on agent file edits; always
   exits 0.
4. `.claude/hooks/stop_projection_check.py` exists; emits `{"decision": "block", ...}` when
   agent sources are modified or newly added and projections are not; includes
   `stop_hook_active` guard; always exits 0 when agents are not modified or on any exception.
5. Both hooks are registered in `.claude/settings.json` under their respective hook types.
6. `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared` exits 0 after all
   shared-surface changes.
7. No forbidden tokens (`TBD`, `TODO`, `[date]`, `YYYY-MM-DD` as literal, `claude:`, `copilot:`)
   in any changed file.
