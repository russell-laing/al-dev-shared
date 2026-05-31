# Modern CLI Tooling Adoption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize `rg` for text search and `jq` for JSON work across repo-facing tooling guidance and shared plugin guidance, while keeping the projection layer harness-neutral.

**Architecture:** This change has three coordinated surfaces. First, repo-maintainer docs will describe `rg` and `jq` as the preferred local CLI tools for search and structured file handling. Second, shared plugin docs and skills will recommend those tools inside Bash-based workflows without turning them into projection capabilities. Third, the `al-dev-script-engineer` agent will gain the same guidance and its generated projections will be refreshed so the distributed agent set stays synchronized.

**Tech Stack:** Markdown docs, generated agent projections, `rg`, `jq`, Python validation scripts, git

---

### Task 1: Standardize `rg` and `jq` in repo-facing tooling guidance

**Files:**
- Modify: `profile-al-dev-shared/knowledge/script-engineer-conventions.md`
- Modify: `profile-al-dev-shared/knowledge/compile-lint-procedure.md`
- Modify: `profile-al-dev-shared/knowledge/solution-plan-template.md`

- [ ] **Step 1: Read the current search and JSON-handling sections**

Run:

```bash
sed -n '1,240p' profile-al-dev-shared/knowledge/script-engineer-conventions.md
sed -n '1,240p' profile-al-dev-shared/knowledge/compile-lint-procedure.md
sed -n '1,140p' profile-al-dev-shared/knowledge/solution-plan-template.md
```

Expected: confirm where the current `grep`, `sed`, `find`, and `head` examples live so the edits stay targeted.

- [ ] **Step 2: Add a preferred-CLI section to `script-engineer-conventions.md`**

Insert this section after `### Protocol-Based Integration`:

```markdown
### Preferred CLI Tools

Use `rg` first for text search, file discovery, and log inspection.
Use `jq` first for JSON inspection and JSON field updates.
Use `grep`, `find`, `sed`, or Python only when they are a better fit or when `rg`/`jq` are unavailable.

Examples:

- `rg -n "pattern" profile-al-dev-shared`
- `jq '.version' .claude/settings.json`
```

- [ ] **Step 3: Replace the compile-log search examples in `compile-lint-procedure.md`**

Update the log-inspection examples to use `rg` instead of `grep` for text search and counts:

```bash
diff .dev/compile-baseline.log .dev/compile-errors.log | rg '^[<>]'

rg -n -e "error|warning" .dev/compile-errors.log | rg '\.(Page|PageExt)\.al'

rg -c '^Error' .dev/compile-errors.log
rg -c '^Warning' .dev/compile-errors.log

rg '^Error' .dev/compile-errors.log | sed 's/.*\[\(.*\)\]/\1/' | sort -u
```

Keep the `find`-based freshness check, because that check is about file timestamps rather than text search.

- [ ] **Step 4: Update the `Validate:` examples in `solution-plan-template.md`**

Replace the current `grep`-based example with a `rg` and `jq` pair that matches the new guidance:

```markdown
Validate: [exact shell command confirming this task is done — e.g., `rg -rn "procedure ValidatePostingDate" src/` or `jq -r '.version' .dev/output.json`]
```

This keeps the template aligned with the plan's preferred local tooling.

- [ ] **Step 5: Verify the repo-facing guidance now names the modern tools**

Run:

```bash
rg -n "Preferred CLI Tools|rg first|jq first" profile-al-dev-shared/knowledge/script-engineer-conventions.md
rg -n "rg -c '\\^Error'|rg -c '\\^Warning'|rg -n -e \"error\\|warning\"" profile-al-dev-shared/knowledge/compile-lint-procedure.md
rg -n "rg -rn \"procedure ValidatePostingDate\"|jq -r '.version'" profile-al-dev-shared/knowledge/solution-plan-template.md
```

Expected: each file shows the updated guidance and the old `grep`-only search examples no longer appear in the replaced sections.

---

### Task 2: Update shared plugin guidance to recommend `rg` and `jq`

**Files:**
- Modify: `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`
- Modify: `profile-al-dev-shared/bc-code-intel-knowledge/README.md`
- Modify: `profile-al-dev-shared/bc-code-intel-knowledge/specialists/sam-coder.md`
- Modify: `profile-al-dev-shared/bc-code-intel-knowledge/specialists/roger-reviewer.md`
- Modify: `profile-al-dev-shared/bc-code-intel-knowledge/specialists/terry-test.md`
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-lint/SKILL.md`

- [ ] **Step 1: Add the boundary note to `agent-tool-projection-policy.md`**

Insert a short note near the canonical vocabulary or maintainer boundary section:

```markdown
- `rg` and `jq` are local CLI conventions, not shared capabilities and not projection targets.
- Shared skills and knowledge may recommend them inside Bash-based workflows.
- If `rg` or `jq` is unavailable, fall back to `grep` or Python in the workflow body rather than changing the projection contract.
```

This keeps the projection model generic while still documenting the preferred local tools.

- [ ] **Step 2: Add a quick-reference tooling section to `bc-code-intel-knowledge/README.md`**

Add this under the quick reference area:

```markdown
### Preferred CLI Tools

- Use `rg` for evidence gathering, search, and scoped pattern checks.
- Use `jq` for JSON inspection and structured updates.
- Prefer these before `grep` or manual parsing when the environment supports them.
```

This gives BC-code-intel users a concise rule they can apply in agent prompts and specialist workflows.

- [ ] **Step 3: Add the same tooling preference to the specialist docs**

Add a short paragraph to each specialist file after the role or communication-style section:

```markdown
When shell inspection is needed, prefer `rg` for text search and `jq` for JSON artifacts.
```

Apply that sentence to:

```text
profile-al-dev-shared/bc-code-intel-knowledge/specialists/sam-coder.md
profile-al-dev-shared/bc-code-intel-knowledge/specialists/roger-reviewer.md
profile-al-dev-shared/bc-code-intel-knowledge/specialists/terry-test.md
```

This keeps the recommendation visible where maintainers actually read the specialist guidance.

- [ ] **Step 4: Add the tooling preference to the shared skill docs**

Insert a short note near the workflow or conventions section in each file:

```markdown
When shell search or structured-file inspection is required, prefer `rg` and `jq` before falling back to broader shell text processing.
```

Apply that note to:

```text
profile-al-dev-shared/skills/al-dev-plan/SKILL.md
profile-al-dev-shared/skills/al-dev-develop/SKILL.md
profile-al-dev-shared/skills/al-dev-fix/SKILL.md
profile-al-dev-shared/skills/al-dev-lint/SKILL.md
```

In `al-dev-develop`, also replace the Phase 4.5 log-inspection commands with `rg` equivalents from Task 1 so the guidance is consistent across the repo.

- [ ] **Step 5: Verify the shared plugin guidance mentions both tools**

Run:

```bash
rg -n "rg|jq" profile-al-dev-shared/knowledge/agent-tool-projection-policy.md
rg -n "rg|jq" profile-al-dev-shared/bc-code-intel-knowledge/README.md
rg -n "rg|jq" profile-al-dev-shared/bc-code-intel-knowledge/specialists/sam-coder.md
rg -n "rg|jq" profile-al-dev-shared/bc-code-intel-knowledge/specialists/roger-reviewer.md
rg -n "rg|jq" profile-al-dev-shared/bc-code-intel-knowledge/specialists/terry-test.md
rg -n "rg|jq" profile-al-dev-shared/skills/al-dev-plan/SKILL.md
rg -n "rg|jq" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
rg -n "rg|jq" profile-al-dev-shared/skills/al-dev-fix/SKILL.md
rg -n "rg|jq" profile-al-dev-shared/skills/al-dev-lint/SKILL.md
```

Expected: each file contains the new tooling guidance, and the projection policy still only describes generic capabilities.

---

### Task 3: Update `al-dev-script-engineer` and regenerate projections

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-script-engineer.md`
- Modify: `profile-al-dev-shared/generated/agents/claude/al-dev-script-engineer.md`
- Modify: `profile-al-dev-shared/generated/agents/copilot/al-dev-script-engineer.md`
- Modify: `profile-al-dev-shared/generated/agents/codex/al-dev-script-engineer.toml`

- [ ] **Step 1: Add a preferred-CLI section to the agent**

Insert this block into `profile-al-dev-shared/agents/al-dev-script-engineer.md` under the existing `Conventions` section:

```markdown
### Preferred CLI Tools

- Use `rg` for text search, repo scanning, and log inspection.
- Use `jq` for JSON inspection and updates.
- Prefer these before `grep` or manual parsing when the environment supports them.
```

This is the place where the repo's scripting agent should state the tool preference most explicitly.

- [ ] **Step 2: Regenerate the harness projections**

Run:

```bash
python3 scripts/generate-agent-projections.py
```

Expected: the three generated `al-dev-script-engineer` projection files are rewritten in place.

- [ ] **Step 3: Confirm the generated projections carry the new guidance**

Run:

```bash
rg -n "Preferred CLI Tools|rg|jq" profile-al-dev-shared/generated/agents/claude/al-dev-script-engineer.md
rg -n "Preferred CLI Tools|rg|jq" profile-al-dev-shared/generated/agents/copilot/al-dev-script-engineer.md
rg -n "Preferred CLI Tools|rg|jq" profile-al-dev-shared/generated/agents/codex/al-dev-script-engineer.toml
```

Expected: all three generated files mention the preferred CLI tools and remain valid harness-native projections.

- [ ] **Step 4: Stage the regenerated agent tree together**

Run:

```bash
git add profile-al-dev-shared/agents/al-dev-script-engineer.md \
  profile-al-dev-shared/generated/agents/claude/al-dev-script-engineer.md \
  profile-al-dev-shared/generated/agents/copilot/al-dev-script-engineer.md \
  profile-al-dev-shared/generated/agents/codex/al-dev-script-engineer.toml
```

Expected: the source agent and all three generated outputs are staged as one unit.

---

### Task 4: Validate the adoption pass and commit the change set

**Files:**
- All files modified in Tasks 1-3

- [ ] **Step 1: Run the repo's shared validation gates**

Run:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
python3 scripts/tests/test_generate_agent_projections.py
```

Expected: all three commands pass. The neutrality validator must still report no harness-specific leakage, and the projection test must pass after regenerating `al-dev-script-engineer`.

- [ ] **Step 2: Spot-check the final content with targeted searches**

Run:

```bash
rg -n "Preferred CLI Tools|rg first|jq first" profile-al-dev-shared/knowledge profile-al-dev-shared/bc-code-intel-knowledge profile-al-dev-shared/skills profile-al-dev-shared/agents
rg -n "projection targets|local CLI conventions|not shared capabilities" profile-al-dev-shared/knowledge/agent-tool-projection-policy.md
git status --short
```

Expected: the new guidance is present in the intended files, and `git status` shows only the plan file plus the expected documentation and generated projection edits.

- [ ] **Step 3: Commit the implementation set**

Run:

```bash
git add docs/superpowers/plans/2026-05-31-modern-cli-tooling-adoption.md \
  profile-al-dev-shared/knowledge/script-engineer-conventions.md \
  profile-al-dev-shared/knowledge/compile-lint-procedure.md \
  profile-al-dev-shared/knowledge/solution-plan-template.md \
  profile-al-dev-shared/knowledge/agent-tool-projection-policy.md \
  profile-al-dev-shared/bc-code-intel-knowledge/README.md \
  profile-al-dev-shared/bc-code-intel-knowledge/specialists/sam-coder.md \
  profile-al-dev-shared/bc-code-intel-knowledge/specialists/roger-reviewer.md \
  profile-al-dev-shared/bc-code-intel-knowledge/specialists/terry-test.md \
  profile-al-dev-shared/skills/al-dev-plan/SKILL.md \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/skills/al-dev-fix/SKILL.md \
  profile-al-dev-shared/skills/al-dev-lint/SKILL.md \
  profile-al-dev-shared/agents/al-dev-script-engineer.md \
  profile-al-dev-shared/generated/agents/claude/al-dev-script-engineer.md \
  profile-al-dev-shared/generated/agents/copilot/al-dev-script-engineer.md \
  profile-al-dev-shared/generated/agents/codex/al-dev-script-engineer.toml

git commit -m "docs: standardize rg and jq guidance across tooling and plugin surfaces"
```

Expected: the commit succeeds with the repo's pre-commit checks passing, and the change set remains limited to the modern CLI tooling adoption work.

---

### Acceptance Criteria

1. `profile-al-dev-shared/knowledge/script-engineer-conventions.md` contains a `Preferred CLI Tools` section that explicitly names `rg` and `jq`.
2. `profile-al-dev-shared/knowledge/compile-lint-procedure.md` uses `rg` in the compile-log inspection examples instead of `grep` for the updated search/count patterns.
3. `profile-al-dev-shared/knowledge/solution-plan-template.md` uses `rg` and `jq` in its `Validate:` examples.
4. `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md` explicitly says `rg` and `jq` are local CLI conventions, not projection targets.
5. `profile-al-dev-shared/agents/al-dev-script-engineer.md` contains a `Preferred CLI Tools` section, and all three generated projections for that agent mention `rg` and `jq`.
6. `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared` passes after the edits.
7. `python3 scripts/tests/test_generate_agent_projections.py` passes after regenerating the `al-dev-script-engineer` projections.
