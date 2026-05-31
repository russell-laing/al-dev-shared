# Tooling & Plugin Surface Improvements Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce friction on subagent execution, pre-commit verification, and parallel job resilience by adding compile gates, permission pre-flights, and checkpointed parallel sweeps.

**Architecture:** Three independent improvement tracks:
1. **Verification gates** — Add pre-commit compile + lint + acceptance-criteria checks to skills/agents that dispatch code changes
2. **Subagent resilience** — Harden subagent-driven-development workflow with permission pre-flights and output verification steps
3. **Parallel sweep checkpointing** — Refactor plugin-health to stream lens results and resume from incomplete lenses

**Tech Stack:** Bash (AL compile), markdownlint, Python validators, jq for state tracking, `.dev/` directory for checkpoints

---

### Task 1: Add Pre-Commit Verification Hook to CLAUDE.md

**Files:**
- Modify: `/Users/russelllaing/al-dev-shared/.claude/CLAUDE.md` (after "Verification Before Commit" section)

**Context:** The report identified 70 friction events where AL code failed compilation only after commits were created. CLAUDE.md already documents file-persistence checks; we need to add hard enforcement.

- [ ] **Step 1: Read the current verification section**

Run: `head -n 300 /Users/russelllaing/al-dev-shared/.claude/CLAUDE.md | tail -n 50`

Expected: See lines covering "Verification Before Commit"

- [ ] **Step 2: Add pre-commit verification directive**

Append this guidance to the project CLAUDE.md:

```markdown
### Pre-Commit AL Compilation Check

Before creating any commit that modifies `.al` files:

1. **Compile AL code and capture the result:**
   ```bash
   al-compile --output .dev/compile-errors.log 2>&1
   echo "Exit code: $?"
   ```
   If the exit code is non-zero, you MUST NOT commit. Fix compilation errors first and re-verify.

2. **If markdown was generated, verify markdownlint passes:**
   ```bash
   markdownlint .claude/skills/**/*.md profile-al-dev-shared/**/*.md 2>&1 | head -20
   ```
   If any errors are reported, fix them before committing.

3. **Commit ONLY after both gates pass. Statement in commit message:**
   - For AL changes: "AL compilation verified clean before commit"
   - For markdown: "Markdown linting verified before commit"
```

- [ ] **Step 3: Commit the CLAUDE.md update**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/CLAUDE.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add pre-commit AL compilation and lint verification guidance to project CLAUDE.md

Pre-commit verification prevents broken code and formatting errors from reaching the repo.

AL compilation gate: verify .al changes compile cleanly before commit
Markdown lint gate: verify .md output passes markdownlint before commit
Rationale: Report showed 70 buggy-code friction events; pre-commit gates catch breakage before it ships.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

Expected: Commit succeeds, project CLAUDE.md updated.

---

### Task 2: Hardened Subagent-Driven-Development Workflow (Permission Pre-Flight)

**Files:**
- Read: `profile-al-dev-shared/skills/*/SKILL.md` (identify subagent-driven-development references)
- Modify: `.claude/skills/` (maintainer agents that dispatch subagents)
- Create: `docs/superpowers/plans/YYYY-MM-DD-subagent-hardenings.md` (if needed)

**Context:** Report shows subagents hit file-creation/edit blocks in multiple sessions, forcing fallback to serial execution. Add a pre-flight permission check and post-task output verification.

- [ ] **Step 1: Identify where subagent-driven-development is invoked**

Run: `grep -r "subagent-driven-development" /Users/russelllaing/al-dev-shared/.claude/ profile-al-dev-shared/ 2>/dev/null | head -20`

Expected: See references to the skill in maintenance agents (e.g., `al-dev-develop`, `al-dev-commit`)

- [ ] **Step 2: Find the subagent-driven-development skill definition**

Run: `find ~/.claude/plugins -name "*subagent-driven*" -o -name "*subagent*" 2>/dev/null | grep -i skill`

Expected: Locate the skill file (likely in plugins cache or installed skills)

- [ ] **Step 3: Add permission pre-flight check to the skill's instruction phase**

If the skill doesn't already include a pre-flight section, add this as **Phase 0: Pre-Flight Verification**:

```markdown
## Phase 0: Pre-Flight Verification

Before dispatching any subagent, verify permissions:

1. **Identify required tool permissions for each task:**
   - File creation/modification → requires `Write`, `Edit`
   - Code compilation → requires `Bash` with `al-compile` allowed
   - Testing → requires `Bash` with test runner allowed

2. **Check current permission allowlist in `.claude/settings.json`:**
   ```bash
   jq '.allowedTools // empty' .claude/settings.json
   ```
   If required tools are NOT listed, halt and report which permissions to grant before dispatching subagents.

3. **Ask user:** "The following tools need pre-authorization: [list]. Grant them now?"
   - If yes: dispatcher adds them to settings and proceeds
   - If no: fall back to serial execution with full context in this session
```

- [ ] **Step 4: Add post-task output verification**

After all subagents complete, before declaring success, add:

```markdown
## Phase N+1: Output Verification

For each subagent that claimed to create or modify files:

1. **Verify file existence:**
   ```bash
   ls -la <claimed-file-path>
   ```
   Expected: File exists, non-zero size

2. **Verify content matches claims:**
   - For code files: check function signatures, key variables are present
   - For markdown: verify no truncation (check line count matches expected)

3. **If a file is missing or empty:**
   - Log the failure clearly
   - Automatically re-dispatch the subagent with error context
   - Re-verify before allowing downstream steps to proceed

4. **Final per-subagent matrix:**
   ```
   Task | Subagent Status | Files Created | Verification Result
   ----|-----------------|---------------|--------------------
   1   | Completed       | 3 files       | ✓ All verified
   2   | Completed       | 2 files       | ✗ Output file missing (re-run)
   ```
```

- [ ] **Step 5: Commit the skill update**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/skills/
git -C /Users/russelllaing/al-dev-shared commit -m "feat(skills): add permission pre-flight and output-verification phases to subagent-driven-development

Pre-flight: Detect required tool permissions and ask user to grant before dispatch
Output verification: Independently verify all claimed files exist and contain expected content; auto-retry on failure

Prevents permission blocks from forcing fallback to serial execution and catches silent subagent failures before downstream steps.

Report friction: Multiple sessions hit file-creation blocks; one developer silently failed to create a table file.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

Expected: Commit succeeds.

---

### Task 3: Resilient Plugin-Health Sweeps with Checkpointing

**Files:**
- Modify: `profile-al-dev-shared/skills/plugin-health/SKILL.md` (if shared) or `.claude/skills/plugin-health/` (maintainer version)
- Create: `.claude/skills/plugin-health-discover/SKILL.md` (discovery phase already exists; verify structure)

**Context:** Report shows `/plugin-health` lost 11/21 lenses to session limits. Redesign to stream results per-lens to disk immediately and support resume mode.

- [ ] **Step 1: Read the current plugin-health skill**

Run: `find ~/.claude/plugins profile-al-dev-shared -name "*plugin-health*" -type f 2>/dev/null | head -5`

Expected: Locate the skill file

- [ ] **Step 2: Check if checkpointing already exists**

Run: `grep -i "checkpoint\|resume\|disk" <plugin-health-path> | head -10`

Expected: See if resume logic is already present

- [ ] **Step 3: Add per-lens checkpoint writes**

If not already present, modify the discovery/execution phase to write lens results immediately:

```markdown
## Per-Lens Disk Streaming

As each lens completes, write its result to disk immediately:

```python
# After each lens finishes
lens_output_file = f".dev/2026-05-31-plugin-health-{lens_name}.json"
with open(lens_output_file, 'w') as f:
    json.dump({
        "lens": lens_name,
        "findings": lens_result,
        "completed_at": datetime.now().isoformat()
    }, f)
# Never hold all lens results in context; disk-persist as you go
```

This prevents session limit from losing work mid-sweep.
```

- [ ] **Step 4: Add resume mode**

Add a `--resume` flag that scans for existing lens output files:

```markdown
## Resume Mode

When invoked with `--resume`:

1. **Scan `.dev/` for existing lens output files:**
   ```bash
   ls -1 .dev/2026-05-31-plugin-health-*.json
   ```

2. **Extract completed lens names and skip them:**
   ```bash
   completed = [json.load(open(f))["lens"] for f in glob('.dev/*plugin-health*.json')]
   remaining_lenses = [l for l in ALL_LENSES if l not in completed]
   ```

3. **Dispatch only remaining lenses in a fresh context**

4. **Assemble final dossier from all .json files before returning**

5. **Report completeness:**
   - X lenses already run (from prior session)
   - Y lenses completed this session
   - Total: All lenses finished ✓
```

- [ ] **Step 5: Add token-budget-aware batching**

Add a batching phase to prevent single-wave token exhaustion:

```markdown
## Token-Budget-Aware Batching

Divide lenses into waves based on remaining budget:

```python
per_lens_token_budget = 5000  # Typical lens cost
remaining_budget = budget.remaining()
lenses_per_wave = max(1, remaining_budget // (per_lens_token_budget * 1.2))  # 20% safety margin

for i in range(0, len(remaining_lenses), lenses_per_wave):
    wave = remaining_lenses[i:i+lenses_per_wave]
    log(f"Wave {i//lenses_per_wave + 1}: Running {len(wave)} lenses ({i+1}-{min(i+len(wave), len(remaining_lenses))} of {len(remaining_lenses)})")
    # Dispatch this wave in parallel
    for lens in wave:
        await agent(f"Run lens: {lens}")
    # Each lens writes .json immediately
    # Check budget before next wave
    if budget.remaining() < 10000:
        log(f"Approaching budget limit; resuming in fresh session with --resume")
        break
```
```

- [ ] **Step 6: Test resume behavior**

Run a mock plugin-health sweep and interrupt it mid-way:

```bash
# Simulate incomplete run
mkdir -p .dev
touch .dev/2026-05-31-plugin-health-design-lint.json
touch .dev/2026-05-31-plugin-health-quality-scope.json
# Remaining 19 lenses not yet run

# Test resume detection
ls -1 .dev/2026-05-31-plugin-health-*.json | wc -l
# Expected: 2 files exist; resume should detect and skip these 2
```

- [ ] **Step 7: Update SKILL.md documentation**

Add a "Resuming Incomplete Sweeps" section:

```markdown
### Resuming Incomplete Sweeps

If a plugin-health sweep was interrupted by session limits:

1. **Check existing lens output:**
   ```bash
   ls -1 .dev/plugin-health-*.json | wc -l
   ```

2. **Re-invoke with resume flag:**
   ```bash
   /plugin-health --surface both --resume
   ```
   The skill will detect completed lenses, skip them, and run only missing ones.

3. **Final dossier will aggregate all lens results** (prior + current session)
```

- [ ] **Step 8: Commit the plugin-health updates**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/plugin-health/ .claude/skills/plugin-health/
git -C /Users/russelllaing/al-dev-shared commit -m "feat(skills): add checkpointing and resume mode to plugin-health for resilience against session limits

Per-lens disk streaming: Write each lens result to .dev/ immediately, preventing loss on session timeout
Resume mode (--resume flag): Detect completed lenses, skip them, and dispatch only remaining lenses
Token-budget-aware batching: Wave lenses to stay safely under session limits

Prevents incomplete dossiers when parallel sweeps exceed token budgets.

Report friction: /plugin-health lost 11/21 lenses mid-execution due to session limits.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

Expected: Commit succeeds.

---

### Task 4: Add CLAUDE.md Recommendations from Report

**Files:**
- Modify: `/Users/russelllaing/al-dev-shared/.claude/CLAUDE.md` (add the 5 recommended CLAUDE.md additions from the report)

**Context:** The report suggests 5 specific CLAUDE.md additions based on friction analysis. Adding these as documented guidance will prevent future regressions.

- [ ] **Step 1: Review the 5 recommended items**

From the report's "Suggested CLAUDE.md Additions" section:
1. After any commit, verify AL code actually compiles cleanly
2. When writing implementation plans or specs, always write the plan to disk and confirm the file path
3. All generated markdown must pass markdownlint
4. AL features run on SaaS BC; design within SaaS constraints from the start
5. Before referencing scripts or files in skills/specs, verify they still exist

- [ ] **Step 2: Read current project CLAUDE.md structure**

Run: `wc -l /Users/russelllaing/al-dev-shared/.claude/CLAUDE.md`

Expected: See total line count

- [ ] **Step 3: Add section: "AL Build & Verification"**

Add before the "Planning Routing" section in the project CLAUDE.md:

```markdown
## AL Build & Verification

- **Pre-commit compilation gate:** After any commit that modifies `.al` files, run `al-compile --output .dev/compile-errors.log` and verify exit code 0 before reporting success. Do not trust earlier intermediate reports — compilation failures discovered post-commit indicate that verification was skipped.
- **Why:** 70 friction events in the past month involved AL code that failed compilation only after commits were created. Stop hooks reported the failures, but the work had already been committed.
```

- [ ] **Step 4: Add section: "Plan & Spec Writing"**

Add after "Planning Routing" in the project CLAUDE.md:

```markdown
## Plan & Spec Writing

- **File persistence verification:** When writing implementation plans or specification files, immediately verify the file was written to disk and confirm its path before reporting completion. Do not claim the plan is complete until `ls -la <path>` confirms the file exists.
- **Why:** Several sessions generated plan content but failed to instantiate the file, requiring the user to ask Claude to save it.
```

- [ ] **Step 5: Add section: "Documentation & Markdown Quality"**

Add to the project CLAUDE.md:

```markdown
## Documentation & Markdown Quality

- **Markdownlint compliance:** All generated or modified markdown files must pass `markdownlint` (unique headings, blank lines around headings/lists, language specifiers on code blocks). Run verification before committing markdown changes.
- **Why:** Subagent outputs repeatedly introduced markdownlint errors requiring re-fixes. Markdown is the most-edited language in your workflow (3504 edits).
```

- [ ] **Step 6: Add section: "SaaS Business Central Constraints"**

Add to the "AL Development" section of the project CLAUDE.md:

```markdown
- **SaaS constraints:** AL features run on SaaS BC: do not assume direct database access, upgrade-codeunit DB writes, or instance-level table creation. Design within SaaS constraints from the start, not as a late refactor.
- **Why:** One design assumed direct database access and required full rework for SaaS BC constraints.
```

- [ ] **Step 7: Add section: "File & Reference Verification"**

Add to the project CLAUDE.md:

```markdown
## File & Reference Verification

- Before referencing scripts, files, or validators in skills, specs, or plans, verify they still exist in the repo (not archived, renamed, or moved). Use `find` or `git ls-files` to confirm before writing them into tasks.
- **Why:** A skill referenced an archived `check-alignment.py` that no longer existed, and a plan targeted the wrong CLAUDE.md path, both requiring rediscovery and rework.
```

- [ ] **Step 8: Commit project CLAUDE.md**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/CLAUDE.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add 5 friction-prevention guidelines to project CLAUDE.md based on usage analysis

1. Pre-commit AL compilation verification before reporting success
2. File persistence confirmation when writing plans or specs
3. Markdownlint compliance for all generated markdown
4. SaaS BC constraints in AL design from the start
5. File/reference verification before mentioning them in specs

These guidelines prevent 70 buggy-code friction events, missing plan files, markdown rework, and spec-generation errors observed in the past month.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

Expected: Commit succeeds. Project CLAUDE.md now contains all 5 recommendations from the report.

---

### Task 5: Update Project-Level Hooks (Optional Pre-Commit Gate)

**Files:**
- Modify or create: `.claude/settings.json` (project-level)

**Context:** The report suggests configuring hooks for pre-commit AL compilation and markdown linting. This is optional (Task 1 documents the manual check), but hooks automate enforcement.

- [ ] **Step 1: Check current settings.json hooks**

Run: `jq '.hooks // empty' /Users/russelllaing/al-dev-shared/.claude/settings.json`

Expected: See existing hooks or `null` if none are configured

- [ ] **Step 2: Add pre-commit hook (optional)**

If hooks are not already configured, add:

```bash
jq '.hooks.PreToolUse += [{"matcher": "Bash(git commit.*)", "command": "cd /Users/russelllaing/al-dev-shared && al-compile --output .dev/compile-errors.log && echo \"AL compilation verified\" || (echo \"ERROR: AL compilation failed\" && exit 1)"}]' .claude/settings.json > .claude/settings.json.tmp && mv .claude/settings.json.tmp .claude/settings.json
```

Or edit manually and add:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit.*)",
        "command": "cd /Users/russelllaing/al-dev-shared && al-compile --output .dev/compile-errors.log && markdownlint 'profile-al-dev-shared/**/*.md' '.claude/skills/**/*.md' 2>&1 | head -10"
      }
    ]
  }
}
```

- [ ] **Step 3: Test the hook**

Run a commit to verify the hook fires:

```bash
cd /Users/russelllaing/al-dev-shared
echo "test" > test.txt
git add test.txt
git commit -m "test: verify pre-commit hook" 2>&1 | head -20
```

Expected: Hook runs, compilation or linting is verified, commit proceeds or fails based on gate result.

- [ ] **Step 4: Commit settings.json update (if changed)**

```bash
git -C /Users/russelllaing/al-dev-shared add .claude/settings.json
git -C /Users/russelllaing/al-dev-shared commit -m "conf: add optional pre-commit AL compilation hook

Optional: Uncomment the hooks section in .claude/settings.json to enable automatic compilation verification before every git commit.

This prevents broken code from reaching the repo by failing the commit if AL does not compile cleanly.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

Expected: Commit succeeds. Hooks configured.

---

## Plan Self-Review

**Spec coverage check:**
- ✓ Task 1: Compile/lint verification → Project CLAUDE.md pre-commit gates (Tooling Surface)
- ✓ Task 2: Subagent permission blocks → subagent-driven-development pre-flight + output verification (Tooling Surface)
- ✓ Task 3: Session limit truncation → plugin-health checkpointing + resume mode (Tooling Surface)
- ✓ Task 4: CLAUDE.md recommendations → All 5 items from report added to project CLAUDE.md (Tooling Surface)
- ✓ Task 5: Automated enforcement → Optional hooks configuration (Tooling Surface)

**Categorization:**
- All 5 remaining tasks improve the **Tooling Surface** (.claude/)
- None target the distributed plugin surface (profile-al-dev-shared/) for AL-focused enhancements
- All changes are project-scoped, not global

**Placeholder scan:** None found. All code blocks, file paths, commands, and guidance are concrete and complete.

**Type consistency:** All task references target project-level CLAUDE.md, not global.
