# Harness Demo Wave 2: Three Maintainer Improvements — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add per-task `Gotcha:` and `Validate:` fields to the solution plan template, create PostToolUse auto-validation hook, and create Stop hook to block on stale projections.

**Architecture:** Three independent changes — a template update, a PostToolUse advisory hook, and a Stop guard hook. Each can be implemented and tested independently. Hooks fail open and never block editing; the Stop hook includes a `stop_hook_active` guard to prevent infinite blocking.

**Tech Stack:** Python 3 (hooks), JSON (settings), Markdown (templates), bash (validation commands)

---

## Task 1: Update Solution Plan Template with Implementation Tasks Section

**Files:**
- Modify: `profile-al-dev-shared/knowledge/solution-plan-template.md` (add `### Implementation Tasks` section)

- [ ] **Step 1: Read the current solution plan template**

```bash
head -100 profile-al-dev-shared/knowledge/solution-plan-template.md
```

This gives context for where to place the Implementation Tasks section (between Implementation Notes and Acceptance Criteria).

- [ ] **Step 2: Add the Implementation Tasks section to the template**

After `### Implementation Notes` section, insert the following new section before `### Acceptance Criteria`:

```markdown
### Implementation Tasks

**Task 1: [name]**
Files: [files to create or modify]
Gotcha: [one project-specific pitfall — e.g., "object names must be ≤30 chars; verify before creating" or "var parameters from AL MCP must be verified before use in subscribers"]
Validate: [exact shell command confirming this task is done — e.g., `grep -rn "procedure ValidatePostingDate" src/` or `grep -c "error AL" .dev/compile-errors.log | grep -q "^0$"`]

**Task 2: [name]**
Files: ...
Gotcha: ...
Validate: ...

**Task N: [name]**
Files: ...
Gotcha: ...
Validate: ...

---

#### Gotcha and Validate Rules

- `Gotcha:` is required. Write `Gotcha: none — [rationale]` rather than omitting it.
- `Validate:` is required. Write `Validate: [manual] — [description]` rather than omitting it.
- Tasks here are the architect's logical implementation units. They inform (but do not replace) the detailed sub-task checklist produced by `writing-plans`.

```

Gotcha: When editing Markdown templates, verify the section hierarchy is correct (`###` must align with existing sections).
Validate: `grep -c "^### Implementation Tasks" profile-al-dev-shared/knowledge/solution-plan-template.md` should return `1`, and `grep -A 5 "^### Implementation Tasks" profile-al-dev-shared/knowledge/solution-plan-template.md` should show the full template.

- [ ] **Step 3: Verify the insertion preserved the file structure**

```bash
wc -l profile-al-dev-shared/knowledge/solution-plan-template.md
grep -n "^### Implementation Tasks" profile-al-dev-shared/knowledge/solution-plan-template.md
grep -n "^### Acceptance Criteria" profile-al-dev-shared/knowledge/solution-plan-template.md
```

Expected: Implementation Tasks should appear before Acceptance Criteria (lower line number), and line count should increase by ~20 lines.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/solution-plan-template.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(solution-plan): add per-task Gotcha and Validate fields

Tasks now include explicit gotchas (project-specific pitfalls) and validate
commands per implementation unit, as adopted from coleam00/harness-engineering-demo.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Update Solution Architect Agent Output Format

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-solution-architect.md` (extend `## Output Format` section)

- [ ] **Step 1: Read the current Output Format section**

```bash
grep -A 30 "^## Output Format" profile-al-dev-shared/agents/al-dev-solution-architect.md
```

This shows the existing bullets that describe what the solution plan must include.

- [ ] **Step 2: Find the Acceptance Criteria bullet**

```bash
grep -n "Acceptance Criteria section:" profile-al-dev-shared/agents/al-dev-solution-architect.md
```

This gives the line number where you'll add the new bullet after it.

- [ ] **Step 3: Add the Implementation Tasks bullet after Acceptance Criteria**

After the `**Acceptance Criteria section:**` bullet, add:

```markdown
- **Implementation Tasks section:** Add a `### Implementation Tasks` section listing each logical implementation unit. For each task include:
  - `Files:` — files to create or modify
  - `Gotcha:` — the most likely project-specific pitfall for this task. Consult `knowledge/al-developer-patterns.md` for known AL/BC traps (object name length, var parameter verification, bash regex line-collapse). Write one concrete warning; write `none — [rationale]` if no pitfall applies.
  - `Validate:` — an exact shell command the developer runs after completing this task to confirm it is done. Prefer `grep`, `wc -l`, or `al-compile` checks. Write `[manual] — [description]` if no shell command suffices.
```

Gotcha: When editing Markdown agent files, verify you do not introduce harness-specific tokens (claude:, copilot:, etc.) in comments.
Validate: `grep -E "(claude:|copilot:)" profile-al-dev-shared/agents/al-dev-solution-architect.md` should return no matches (exit 0).

- [ ] **Step 4: Verify the bullet was inserted in the correct location**

```bash
grep -A 50 "^## Output Format" profile-al-dev-shared/agents/al-dev-solution-architect.md | grep -A 8 "Implementation Tasks section"
```

Expected: The new bullet should appear after "Acceptance Criteria section:" and before any closing section.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-solution-architect.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(al-dev-solution-architect): require Implementation Tasks in output

Architect now documents Gotcha and Validate requirements per task,
guiding developers toward per-task validation and pitfall awareness.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Create PostToolUse Validation Hook

**Files:**
- Create: `.claude/hooks/post_edit_validate.py`

- [ ] **Step 1: Create the .claude/hooks directory if it doesn't exist**

```bash
mkdir -p /Users/russelllaing/al-dev-shared/.claude/hooks
ls -la /Users/russelllaing/al-dev-shared/.claude/hooks/
```

Expected: Directory exists and is empty or only contains files from previous work.

- [ ] **Step 2: Write the post_edit_validate.py hook**

Create `/Users/russelllaing/al-dev-shared/.claude/hooks/post_edit_validate.py` with:

```python
#!/usr/bin/env python3
import sys
import json
import subprocess
import os

try:
    event = json.load(sys.stdin)
    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if not file_path:
        sys.exit(0)

    project_root = os.environ.get(
        "CLAUDE_PROJECT_DIR",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    shared_prefix = os.path.join(project_root, "profile-al-dev-shared")
    generated_prefix = os.path.join(shared_prefix, "generated")
    agents_prefix = os.path.join(shared_prefix, "agents")

    abs_path = os.path.abspath(file_path)

    # Check harness neutrality for shared surface files (excluding generated)
    if abs_path.startswith(shared_prefix) and not abs_path.startswith(generated_prefix):
        result = subprocess.run(
            ["python3", os.path.join(project_root, "scripts", "validate_harness_neutrality.py"), shared_prefix],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[post-edit] harness-neutrality: OK")
        else:
            print("[post-edit] harness-neutrality: issues found — fix before committing")
            print(result.stdout[:500])

    # Check agent structure for agent files
    if abs_path.startswith(agents_prefix) and abs_path.endswith(".md"):
        result = subprocess.run(
            ["python3", os.path.join(project_root, "scripts", "validate-lens-agents.py"),
             "--path", agents_prefix],
            capture_output=True,
            text=True
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

Gotcha: The hook must fail open (always exit 0) and never block file editing. The try-except ensures any JSON parse or subprocess error does not propagate.
Validate: `python3 -m py_compile /Users/russelllaing/al-dev-shared/.claude/hooks/post_edit_validate.py` should exit 0, and `grep "sys.exit(0)" /Users/russelllaing/al-dev-shared/.claude/hooks/post_edit_validate.py | wc -l` should return 2 (one in except, one at end).

- [ ] **Step 3: Make the hook executable**

```bash
chmod +x /Users/russelllaing/al-dev-shared/.claude/hooks/post_edit_validate.py
ls -la /Users/russelllaing/al-dev-shared/.claude/hooks/post_edit_validate.py
```

Expected: `-rwxr-xr-x` permission bit set.

- [ ] **Step 4: Test the hook syntax**

```bash
python3 -m py_compile /Users/russelllaing/al-dev-shared/.claude/hooks/post_edit_validate.py
echo $?
```

Expected: Exit code 0 (no syntax errors).

- [ ] **Step 5: Commit the hook**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/hooks/post_edit_validate.py
git -C /Users/russelllaing/al-dev-shared commit -m "feat(.claude/hooks): add PostToolUse validation hook

Runs harness-neutrality and agent-structure validators after every edit
to shared surface files. Advisory only (always exits 0, never blocks editing).
Skips generated artifacts.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Create Stop Projection Check Hook

**Files:**
- Create: `.claude/hooks/stop_projection_check.py`

- [ ] **Step 1: Write the stop_projection_check.py hook**

Create `/Users/russelllaing/al-dev-shared/.claude/hooks/stop_projection_check.py` with:

```python
#!/usr/bin/env python3
import sys
import json
import subprocess
import os

try:
    event = json.load(sys.stdin)

    # Prevent infinite blocking: if hook already fired once this stop, pass through
    if event.get("stop_hook_active"):
        sys.exit(0)

    project_root = os.environ.get(
        "CLAUDE_PROJECT_DIR",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    # Get all changed files (tracked, staged, untracked)
    tracked = subprocess.run(
        ["git", "-C", project_root, "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True
    )
    staged = subprocess.run(
        ["git", "-C", project_root, "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    untracked = subprocess.run(
        ["git", "-C", project_root, "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True
    )
    changed = (tracked.stdout + staged.stdout + untracked.stdout).splitlines()

    # Detect agent source changes and projection staleness
    agent_changes = [f for f in changed if "profile-al-dev-shared/agents/" in f and f.endswith(".md")]
    generated_changes = [f for f in changed if "profile-al-dev-shared/generated/agents/" in f]

    # Block if agents changed but projections were not regenerated
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

Gotcha: The hook must check for `stop_hook_active` in the event payload to prevent infinite blocking. If Claude attempts to stop again after being blocked, the hook should pass through. The guard lets the user manually run `generate-agent-projections.py` and retry.
Validate: `python3 -m py_compile /Users/russelllaing/al-dev-shared/.claude/hooks/stop_projection_check.py` should exit 0, and `grep "stop_hook_active" /Users/russelllaing/al-dev-shared/.claude/hooks/stop_projection_check.py` should return exactly 1 match.

- [ ] **Step 2: Make the hook executable**

```bash
chmod +x /Users/russelllaing/al-dev-shared/.claude/hooks/stop_projection_check.py
ls -la /Users/russelllaing/al-dev-shared/.claude/hooks/stop_projection_check.py
```

Expected: `-rwxr-xr-x` permission bit set.

- [ ] **Step 3: Test the hook syntax**

```bash
python3 -m py_compile /Users/russelllaing/al-dev-shared/.claude/hooks/stop_projection_check.py
echo $?
```

Expected: Exit code 0 (no syntax errors).

- [ ] **Step 4: Test the hook guard logic**

Create a test JSON payload with `stop_hook_active: true`:

```bash
echo '{"stop_hook_active": true}' | python3 /Users/russelllaing/al-dev-shared/.claude/hooks/stop_projection_check.py
echo "Exit code: $?"
```

Expected: Exit code 0 (hook passes through when guard is set).

- [ ] **Step 5: Commit the hook**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/hooks/stop_projection_check.py
git -C /Users/russelllaing/al-dev-shared commit -m "feat(.claude/hooks): add Stop hook for stale projection detection

Blocks turn completion when agent sources are modified and projections not
regenerated. Includes stop_hook_active guard to prevent infinite blocking.
Fails open on ambiguous state or exceptions.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Register Hooks in .claude/settings.json

**Files:**
- Modify: `.claude/settings.json`

- [ ] **Step 1: Read the current .claude/settings.json**

```bash
cat /Users/russelllaing/al-dev-shared/.claude/settings.json
```

This shows the current structure and hook configuration state.

- [ ] **Step 2: Verify hooks section exists**

```bash
grep -A 2 '"hooks"' /Users/russelllaing/al-dev-shared/.claude/settings.json
```

If `hooks: {}` (empty) or `"hooks"` is missing, you'll need to add or extend it.

- [ ] **Step 3: Add or update the hooks section with PostToolUse and Stop hooks**

The final hooks section should look like:

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
    ],
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

If the file already has other top-level keys (like `"workspace"`, `"permissions"`, etc.), preserve them and add the hooks alongside.

Gotcha: JSON syntax is strict — all commas, quotes, and braces must be correct. Use `python3 -m json.tool` to validate.
Validate: `python3 -m json.tool /Users/russelllaing/al-dev-shared/.claude/settings.json > /dev/null && echo "OK"` should print "OK" and exit 0.

- [ ] **Step 4: Validate the JSON syntax**

```bash
python3 -m json.tool /Users/russelllaing/al-dev-shared/.claude/settings.json > /dev/null
echo "JSON validation exit code: $?"
```

Expected: Exit code 0 (valid JSON).

- [ ] **Step 5: Verify the hook commands are correctly registered**

```bash
grep -A 5 '"PostToolUse"' /Users/russelllaing/al-dev-shared/.claude/settings.json | grep "post_edit_validate.py"
grep -A 5 '"Stop"' /Users/russelllaing/al-dev-shared/.claude/settings.json | grep "stop_projection_check.py"
```

Expected: Both grep commands should return the hook paths.

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/settings.json
git -C /Users/russelllaing/al-dev-shared commit -m "config(.claude/settings.json): register PostToolUse and Stop hooks

Hooks run validators after every edit and check for stale projections
on turn completion. Both fail open and never block editing flow.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Final Validation — Harness Neutrality and Forbidden Patterns

**Files:**
- All changed files (validate their content)

- [ ] **Step 1: Run harness neutrality validator on shared surface**

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/validate_harness_neutrality.py /Users/russelllaing/al-dev-shared/profile-al-dev-shared
echo "Validation exit code: $?"
```

Expected: Exit code 0 (all harness-neutral).

- [ ] **Step 2: Scan for forbidden patterns in all changed files**

```bash
for file in \
  profile-al-dev-shared/knowledge/solution-plan-template.md \
  profile-al-dev-shared/agents/al-dev-solution-architect.md \
  .claude/settings.json \
  .claude/hooks/post_edit_validate.py \
  .claude/hooks/stop_projection_check.py; do
  echo "=== Checking $file ==="
  grep -E "(\[date\]|YYYY-MM-DD|TODO|TBD|claude:|copilot:)" "$file" || echo "  No forbidden patterns"
done
```

Expected: No matches for `[date]`, `YYYY-MM-DD` (literal), `TODO`, `TBD`, `claude:`, or `copilot:` in any file.

- [ ] **Step 3: Verify line counts are reasonable**

```bash
wc -l profile-al-dev-shared/knowledge/solution-plan-template.md \
   profile-al-dev-shared/agents/al-dev-solution-architect.md \
   .claude/hooks/post_edit_validate.py \
   .claude/hooks/stop_projection_check.py \
   .claude/settings.json
```

Expected: All files exist and have content (non-zero line counts).

- [ ] **Step 4: Review git log to confirm all commits were created**

```bash
git -C /Users/russelllaing/al-dev-shared log --oneline -n 6
```

Expected: 6 commits (one per task), all with "Co-Authored-By: Claude Haiku 4.5".

- [ ] **Step 5: Confirm git status is clean**

```bash
git -C /Users/russelllaing/al-dev-shared status
```

Expected: "nothing to commit, working tree clean" (or only untracked files from other work).

- [ ] **Step 6: Summary**

All three changes are now implemented and committed:
1. ✅ Solution plan template has `### Implementation Tasks` section with Gotcha and Validate fields
2. ✅ Solution architect agent documents Implementation Tasks requirement
3. ✅ PostToolUse hook validates shared surface and agent files after every edit
4. ✅ Stop hook blocks on stale projections with remedy guidance and `stop_hook_active` guard
5. ✅ Both hooks registered in `.claude/settings.json`
6. ✅ All validations pass, no forbidden patterns, 6 atomic commits

Gotcha: none — validation is complete and comprehensive.
Validate: `git -C /Users/russelllaing/al-dev-shared log --oneline -n 6 | wc -l` should return 6.

---

## Summary of Changes

| Change | Files | Status |
|--------|-------|--------|
| Implementation Tasks in plan template | `solution-plan-template.md`, `al-dev-solution-architect.md` | ✅ |
| PostToolUse validation hook | `.claude/hooks/post_edit_validate.py`, `.claude/settings.json` | ✅ |
| Stop projection check hook | `.claude/hooks/stop_projection_check.py`, `.claude/settings.json` | ✅ |

**Total commits:** 6 atomic commits, one per task, all verified and harness-neutral.
