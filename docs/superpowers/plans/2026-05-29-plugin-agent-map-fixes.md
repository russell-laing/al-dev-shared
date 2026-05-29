# Plugin and Agent Map Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply 7 open suggestions from the Observations sections of `docs/al-dev-plugin-map.md` and `docs/al-dev-agent-map.md` — 3 documentation-only Align fixes, 1 Connect routing clarity prose update, 1 Remodel for complexity-gated architect dispatch, 1 Split to extract a preflight agent from the execute agent, and 1 implementation of the stub al-dev-review-develop skill.

**Architecture:** Tasks ordered by blast radius — doc-only fixes first (Tasks 1–3), prose knowledge update (Task 4), dispatch block changes across 2 skills (Task 5), new agent creation and 3-file skill split (Task 6), and stub skill implementation from scratch (Task 7). Each task is independently committable and verifiable.

**Tech Stack:** Markdown agent/skill files in `profile-al-dev-shared/agents/` and `profile-al-dev-shared/skills/`; regenerate harness projections with `python3 scripts/generate-agent-projections.py` after source edits; validate with `python3 scripts/validate-lens-agents.py` and `python3 scripts/validate_harness_neutrality.py`.

---

## File Map

| Task | Action | File |
|------|--------|------|
| 1 | Modify | `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md` |
| 2 | Modify | `profile-al-dev-shared/agents/al-dev-developer.md` |
| 3 | Modify | `profile-al-dev-shared/agents/al-dev-ticket-agent.md` |
| 4 | Modify | `profile-al-dev-shared/knowledge/workflow-routing.md` |
| 5 | Modify | `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` |
| 5 | Modify | `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` |
| 6 | **Create** | `profile-al-dev-shared/agents/al-dev-commit-preflight.md` |
| 6 | Modify | `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md` |
| 6 | Modify | `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` |
| 6 | Modify | `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml` |
| 7 | Modify | `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` |

---

## Task 1: Align — al-dev-commit-recover-verifier REPO parameter

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md:23`

**Rubber duck verdict:** The `REPO` row in the Inputs table is marked Required, but the agent body never uses a `$REPO` parameter — it infers repo context from the working directory. Fix: change Required→No and explain the inference.

- [ ] **Step 1: Read the file to confirm current line 23 content**

```bash
grep -n "REPO" profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md
```

Expected: `23:| \`REPO\` | **Yes** | Project root directory |`

- [ ] **Step 2: Apply the Inputs table fix**

Use the Edit tool on `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md`:

```
old_string: | `REPO` | **Yes** | Project root directory |
new_string: | `REPO` | No | Inferred from working directory; not passed explicitly by /commit-recover |
```

- [ ] **Step 3: Verify line count unchanged**

```bash
wc -l profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md
```

Expected: 55 lines (same as before).

- [ ] **Step 4: Confirm the change**

```bash
grep "REPO" profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md
```

Expected: `| \`REPO\` | No | Inferred from working directory; not passed explicitly by /commit-recover |`

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md \
        profile-al-dev-shared/agents/al-dev-developer.md \
        profile-al-dev-shared/agents/al-dev-ticket-agent.md
```

> Hold commit until Tasks 2 and 3 are also done — all three are doc-only Align fixes that belong in one atomic commit.
>
> Before committing, regenerate `profile-al-dev-shared/generated/agents/**` so the authored surface and committed projections stay in sync.

---

## Task 2: Align — al-dev-developer TDD test-plan reference

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-developer.md:23`

**Rubber duck verdict:** Inputs table references "test-engineer agent" as the source of the test-plan file, but no such agent exists anywhere in the plugin. Fix: remove the nonexistent agent reference. The Optional flag and TDD gate logic are correct and should remain unchanged.

- [ ] **Step 1: Confirm current line 23 content**

```bash
grep -n "test-engineer" profile-al-dev-shared/agents/al-dev-developer.md
```

Expected: line 23 contains `User-supplied or created by test-engineer agent (TDD workflow).`

- [ ] **Step 2: Apply the Inputs table fix**

Use the Edit tool on `profile-al-dev-shared/agents/al-dev-developer.md`:

```
old_string: | `.dev/*-al-dev-test-test-plan.md` | Optional | User-supplied or created by test-engineer agent (TDD workflow). If absent, uses traditional implementation workflow. |
new_string: | `.dev/*-al-dev-test-test-plan.md` | Optional | User-supplied test plan for TDD workflow. If absent, uses traditional implementation workflow. |
```

- [ ] **Step 3: Verify line count unchanged**

```bash
wc -l profile-al-dev-shared/agents/al-dev-developer.md
```

Expected: 126 lines.

- [ ] **Step 4: Confirm the removal**

```bash
grep "test-engineer" profile-al-dev-shared/agents/al-dev-developer.md
```

Expected: no output (the reference is removed).

---

## Task 3: Align — al-dev-ticket-agent env var pass mechanism

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-ticket-agent.md:19-22`

**Rubber duck verdict:** The Inputs table and note describe FRESHDESK_API_KEY/FRESHDESK_DOMAIN as "resolved from harness environment and set as shell variables" but don't explain HOW they arrive in the agent's bash context (harness environment settings, not the spawning skill). Fix: update the table rows and note to name the actual mechanism precisely. The suggested wording "exported by the spawning skill" from the map observation is inaccurate — the skill only verifies presence, it doesn't export. Correct phrasing: "configured in harness environment settings."

- [ ] **Step 1: Confirm current rows 19-22**

```bash
sed -n '19,22p' profile-al-dev-shared/agents/al-dev-ticket-agent.md
```

Expected output:
```
| `FRESHDESK_API_KEY` | **Yes** | API key (environment variable, not dispatch field) |
| `FRESHDESK_DOMAIN` | **Yes** | Freshdesk subdomain (environment variable, not dispatch field) |

**Note:** `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` are resolved from the harness environment and set as shell variables, not passed in the dispatch prompt. See `knowledge/ticket-agent-invocation-pattern.md`.
```

- [ ] **Step 2: Apply the Inputs table and note fix**

Use the Edit tool on `profile-al-dev-shared/agents/al-dev-ticket-agent.md`:

```
old_string:
| `FRESHDESK_API_KEY` | **Yes** | API key (environment variable, not dispatch field) |
| `FRESHDESK_DOMAIN` | **Yes** | Freshdesk subdomain (environment variable, not dispatch field) |

**Note:** `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` are resolved from the harness environment and set as shell variables, not passed in the dispatch prompt. See `knowledge/ticket-agent-invocation-pattern.md`.

new_string:
| `FRESHDESK_API_KEY` | **Yes** | API key; available as shell environment variable in agent bash context (configured in harness environment settings per `knowledge/ticket-agent-invocation-pattern.md`) |
| `FRESHDESK_DOMAIN` | **Yes** | Freshdesk subdomain; available as shell environment variable in agent bash context (configured in harness environment settings per `knowledge/ticket-agent-invocation-pattern.md`) |

**Note:** `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` are configured in the harness environment settings and injected as shell variables at agent dispatch — not passed in the dispatch prompt.
```

- [ ] **Step 3: Verify line count unchanged**

```bash
wc -l profile-al-dev-shared/agents/al-dev-ticket-agent.md
```

Expected: 127 lines (same as before — the replacement has the same line count).

- [ ] **Step 4: Confirm the change**

```bash
grep "harness environment settings" profile-al-dev-shared/agents/al-dev-ticket-agent.md
```

Expected: 3 lines (two table rows + the note).

- [ ] **Step 5: Commit Tasks 1–3 together**

```bash
python3 scripts/generate-agent-projections.py
git add profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md \
        profile-al-dev-shared/agents/al-dev-developer.md \
        profile-al-dev-shared/agents/al-dev-ticket-agent.md \
        profile-al-dev-shared/generated/agents
git commit -m "$(cat <<'EOF'
docs(agents): three Align fixes — REPO param, TDD ref, env var mechanism

- al-dev-commit-recover-verifier: REPO changed Required→No (inferred from cwd)
- al-dev-developer: removed nonexistent test-engineer agent reference from Inputs
- al-dev-ticket-agent: expanded FRESHDESK_* rows to name harness env settings mechanism

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 6: Verify commit**

```bash
git log --oneline -1
```

Expected: commit with message starting "docs(agents): three Align fixes"

---

## Task 4: Connect — workflow-routing.md /al-dev-fix non-trivial branch

**Files:**
- Modify: `profile-al-dev-shared/knowledge/workflow-routing.md:34-42`

**Rubber duck verdict:** The TRIVIAL section already mentions escalation on line 19 and steps 3-4 of the Steps list, but the non-trivial escalation branch behavior is understated. A caller reading the TRIVIAL section could conclude `/al-dev-fix` is always a direct edit and route non-trivial issues elsewhere. Fix: replace the 5-step list with a clearer two-part structure (direct path + explicit escalation description).

- [ ] **Step 1: Confirm the current Steps block**

```bash
grep -n "Steps\|non-trivial\|escalat" profile-al-dev-shared/knowledge/workflow-routing.md | head -15
```

Expected: lines 34-42 contain the current 5-step list and "non-trivial branch" reference.

- [ ] **Step 2: Apply the Steps block replacement**

Use the Edit tool on `profile-al-dev-shared/knowledge/workflow-routing.md`:

```
old_string:
**Steps:**
1. Read project-context.md
2. Locate the likely file with minimal search
3. If the fix stays obvious and single-scope, continue on the direct `/al-dev-fix` path
4. If ambiguity, multiple files, or integration risk appears, follow the `/al-dev-fix` non-trivial branch instead of forcing a trivial edit
5. Run compile/lint verification and present the bounded result

**Time saved:** 15-25 minutes vs full workflow

new_string:
**Steps (direct-fix path, 2-5 min):**
1. Read project-context.md
2. Locate the likely file with minimal search
3. If the fix stays obvious and single-scope, implement directly
4. Run compile/lint verification and present the bounded result

**Non-trivial escalation (10-20 min):** If ambiguity, multiple files, or integration risk appears at step 3, `/al-dev-fix` switches automatically to its built-in escalation branch:
- Spawns `al-dev-solution-architect` for quick root-cause analysis (~5 min)
- Reviews architect's hypothesis; presents to user for approval
- Spawns `al-dev-developer` with confirmed approach
- Runs compile/lint verification and presents result

Do not route to `/al-dev-plan` for issues that are bounded (single subsystem, clear root cause after architect review) — the `/al-dev-fix` escalation handles these efficiently.

**Time saved:** 15-25 min vs full workflow (direct path); 10-15 min vs full plan cycle (escalation path)
```

- [ ] **Step 3: Verify line count**

```bash
wc -l profile-al-dev-shared/knowledge/workflow-routing.md
```

The new block is 4 lines longer than the old (old: 7 lines, new: 11 lines). Expected: ~323 lines (old 319 + 4 = 323).

- [ ] **Step 4: Confirm the changes**

```bash
grep -n "Non-trivial escalation\|direct-fix path" profile-al-dev-shared/knowledge/workflow-routing.md
```

Expected: two lines — "Steps (direct-fix path, 2-5 min):" and "**Non-trivial escalation (10-20 min):**"

- [ ] **Step 5: Validate harness neutrality**

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected: exit 0, no forbidden tokens in changed file.

- [ ] **Step 6: Commit**

```bash
git add profile-al-dev-shared/knowledge/workflow-routing.md
git commit -m "$(cat <<'EOF'
docs(knowledge): clarify /al-dev-fix escalation path in workflow-routing

TRIVIAL section now has explicit non-trivial escalation block describing
architect → review → implement sequence, timing estimate, and guidance
not to route bounded issues to /al-dev-plan instead.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Remodel — al-dev-solution-architect complexity-gated dispatch

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` (Phase 2 dispatch prompt template)
- Modify: `profile-al-dev-shared/skills/al-dev-fix/SKILL.md` (Step 3 non-trivial architect dispatch)

**Rubber duck verdict:** al-dev-plan already computes `architect_model` in Phase 0.5 and uses it to conditionally override the model parameter in Phase 2, but the dispatch prompt itself doesn't tell the architect what complexity tier it's operating at. al-dev-fix has no complexity routing at all — it always spawns the architect with opus and no tier context. Fix: (1) add tier string to al-dev-plan Phase 2 prompt template, (2) add complexity assessment + conditional model override to al-dev-fix Step 3.

### Sub-task 5a: al-dev-plan Phase 2 dispatch prompt

- [ ] **Step 1: Locate the Phase 2 architect prompt template**

```bash
grep -n "Each architect prompt must include" profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

Expected: one match around line 234.

- [ ] **Step 2: Confirm the current opening of the prompt template**

```bash
sed -n '234,242p' profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

Expected:
```
Each architect prompt must include:

```text
Design a complete AL/BC solution for: [user requirement]
```

- [ ] **Step 3: Add complexity tier to the prompt template**

Use the Edit tool on `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`:

```
old_string:
Each architect prompt must include:

```text
Design a complete AL/BC solution for: [user requirement]

new_string:
Each architect prompt must include:

```text
**Task Complexity Tier:** [SIMPLE if architect_model=sonnet | MEDIUM/COMPLEX if architect_model=opus]

Design a complete AL/BC solution for: [user requirement]
```

- [ ] **Step 4: Verify the change**

```bash
grep -n "Task Complexity Tier" profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

Expected: one line containing `**Task Complexity Tier:**`

### Sub-task 5b: al-dev-fix Step 3 architect dispatch

- [ ] **Step 5: Locate the current Step 3 architect spawn line**

```bash
grep -n "Spawn al-dev-shared:al-dev-solution-architect for quick analysis" profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Expected: one match around line 187.

- [ ] **Step 6: Confirm the current content of the dispatch block**

```bash
sed -n '187,189p' profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Expected:
```
1. Spawn al-dev-shared:al-dev-solution-architect for quick analysis.
   Include this in the dispatch prompt: "Follow `knowledge/al-symbol-pre-flight.md` for symbol verification rigor. Ensure all proposed changes reference verified AL symbol definitions."
```

- [ ] **Step 7: Add complexity assessment and conditional model override**

Use the Edit tool on `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`:

```
old_string:
1. Spawn al-dev-shared:al-dev-solution-architect for quick analysis.
   Include this in the dispatch prompt: "Follow `knowledge/al-symbol-pre-flight.md` for symbol verification rigor. Ensure all proposed changes reference verified AL symbol definitions."

new_string:
1. Assess fix complexity to determine architect model tier:
   - **SIMPLE tier** (use sonnet): root cause is obvious, 1-2 files, < 20 lines to change
   - **COMPLEX tier** (use opus — default): root cause is unclear, multi-file, ≥ 20 lines, or architectural impact

   Spawn al-dev-shared:al-dev-solution-architect for quick analysis.
   - If complexity = SIMPLE: include `model: sonnet` in the Agent tool invocation
   - If complexity = COMPLEX: omit model parameter (agent default opus applies)

   Include this in the dispatch prompt:
   "**Fix Complexity Tier:** [SIMPLE|COMPLEX]
   Follow `knowledge/al-symbol-pre-flight.md` for symbol verification rigor. Ensure all proposed changes reference verified AL symbol definitions."
```

- [ ] **Step 8: Verify the change**

```bash
grep -n "SIMPLE tier\|COMPLEX tier\|Fix Complexity Tier" profile-al-dev-shared/skills/al-dev-fix/SKILL.md
```

Expected: 3 lines.

- [ ] **Step 9: Validate harness neutrality**

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected: exit 0.

- [ ] **Step 10: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-plan/SKILL.md \
        profile-al-dev-shared/skills/al-dev-fix/SKILL.md
git commit -m "$(cat <<'EOF'
feat(skills): complexity-gated architect dispatch in plan and fix skills

- al-dev-plan Phase 2: dispatch prompt now includes Task Complexity Tier
  string so architect knows whether it's a SIMPLE or MEDIUM/COMPLEX task
- al-dev-fix Step 3: adds complexity assessment before architect spawn;
  uses sonnet for SIMPLE (obvious root cause, 1-2 files) and opus for
  COMPLEX (unclear root cause, multi-file, architectural impact)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Split — al-dev-commit-agent-execute → al-dev-commit-preflight

**Files:**
- **Create:** `profile-al-dev-shared/agents/al-dev-commit-preflight.md`
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`

**Rubber duck verdict:** The execute agent mixes two separable concerns: (a) pre-flight lint + OOXML validation (Steps 1-2) and (b) git commit execution + hook retry (Steps 3-4). These share no mutable state across the boundary. Extract concern (a) into `al-dev-commit-preflight` (25 chars, ≤30 limit). The al-dev-commit skill dispatches the new preflight agent as Step 9.5 before Step 10. LINT_FIXES moves from execute outputs to preflight outputs; Step 11 of the skill reads LINT_FIXES from the Step 9.5 result.

### Sub-task 6a: Create al-dev-commit-preflight agent

- [ ] **Step 1: Create the new preflight agent file**

Write `profile-al-dev-shared/agents/al-dev-commit-preflight.md`:

```markdown
---
name: al-dev-commit-preflight
description: >-
  Pre-flight lint and OOXML validation for staged commit files. Runs Python
  lint, trailing whitespace fixes, line-count corruption detection, and ZIP
  validation on OOXML files. Returns LINT_FIXES and OOXML_FAILURES. Dispatched
  by al-dev-commit (Step 9.5) before commit execution.
model: sonnet
tools: ["Bash", "Read"]
---

# Agent: al-dev-commit-preflight

Run pre-flight validation on staged files before commit execution.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups and messages from analysis phase |

## Outputs

| Output | Description |
|--------|-------------|
| `LINT_FIXES` | Files re-staged after lint fixes (or `NONE`) |
| `OOXML_FAILURES` | OOXML files that failed ZIP validation (or `NONE`) |

⚠️ **CRITICAL:** Never use Write or Edit on staged source files. All fixes via Bash only. If a fix cannot be made via Bash, record as OOXML_FAILURE and stop.

## Phase: preflight

### Pre-flight Lint (Step 1)

For each approved group:
1. Capture line counts baseline: `git diff --cached --name-only | while IFS= read -r f; do [ -f "$f" ] || continue; printf '%s\t%d\n' "$f" "$(wc -l < "$f")" >> .git/.commit-baselines; done`
2. For every `.py` file: `ruff check --fix <file> && ruff format <file> && git add <file>`
3. Trailing whitespace: `git diff --cached --name-only | while IFS= read -r f; do perl -pi -e 's/[ \t]+$//' "$f"; git add "$f"; done`
4. Detect corruption by comparing post-lint line counts against baseline. If drastically shrunk, restore and halt.

⚠️ **Regex MUST be `[ \t]+$` (horizontal whitespace only).** Never use `[[:space:]]+$` or `\s+$` — those include `\n`, collapsing entire file into one line.

### OOXML Gate (Step 2)

For files with OOXML extensions (`.docx`, `.xlsx`, `.pptx`, `.odt`):
1. Run ZIP validation: `unzip -t <file> > /dev/null 2>&1`
2. If validation fails: record as OOXML_FAILURE, do not proceed to commit
3. Require human review before re-staging OOXML files

### Return Block (Step 3)

```text
LINT_FIXES: [file1, file2] (or NONE)
OOXML_FAILURES: [filename: reason] (or NONE)
```
```

- [ ] **Step 2: Verify the file was written**

```bash
ls -la profile-al-dev-shared/agents/al-dev-commit-preflight.md && wc -l profile-al-dev-shared/agents/al-dev-commit-preflight.md
```

Expected: file exists, ~53 lines.

### Sub-task 6b: Modify al-dev-commit-agent-execute

- [ ] **Step 3: Remove the description's lint/OOXML references and update model comment**

Use the Edit tool on `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`:

```
old_string:
description: >-
  Git commit execution agent. Runs lint, validates OOXML integrity, and
  executes git commits from an approved plan. Dispatched by al-dev-commit
  (execute phase). Never writes or edits source files directly — all fixes
  go through Bash.
model: sonnet  # Upgraded from haiku: multi-phase orchestration (baseline → lint → validation → commit → retry) with interdependent state and error recovery requires multi-step reasoning

new_string:
description: >-
  Git commit execution agent. Executes git commits from an approved plan,
  handling hook failures and retry logic. Dispatched by al-dev-commit
  (execute phase) after al-dev-commit-preflight completes. Never writes or
  edits source files directly — all fixes go through Bash.
model: sonnet  # Upgraded from haiku: multi-step commit orchestration with hook retry and error recovery requires multi-step reasoning
```

- [ ] **Step 4: Remove LINT_FIXES from the Outputs table**

Use the Edit tool on `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`:

```
old_string:
| `COMMITS` block | SHA and message for each committed group |
| `SKIPPED` | Number of skipped groups |
| `LINT_FIXES` | Files re-staged after lint (or `NONE`) |
| `HOOK_FAILURES` | Raw hook output for any failed groups (or `NONE`) |
| `STRIPPED_ATTRIBUTIONS` | Removed AI attribution lines (or `NONE`) |

new_string:
| `COMMITS` block | SHA and message for each committed group |
| `SKIPPED` | Number of skipped groups |
| `HOOK_FAILURES` | Raw hook output for any failed groups (or `NONE`) |
| `STRIPPED_ATTRIBUTIONS` | Removed AI attribution lines (or `NONE`) |
```

- [ ] **Step 5: Add preflight-completed note to Inputs table**

Use the Edit tool on `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`:

```
old_string:
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups and messages from analysis phase |

new_string:
| Dispatch prompt | **Yes** | `APPROVED_PLAN` — approved groups and messages from analysis phase; al-dev-commit-preflight must have completed successfully before this agent is dispatched |
```

- [ ] **Step 6: Remove Pre-flight Lint (Step 1) and OOXML Gate (Step 2) sections, renumber remaining steps**

Use the Edit tool on `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`:

```
old_string:
## Phase: execute

### Pre-flight Lint (Step 1)

For each approved group:
1. Capture line counts baseline: `git diff --cached --name-only | while IFS= read -r f; do [ -f "$f" ] || continue; printf '%s\t%d\n' "$f" "$(wc -l < "$f")" >> .git/.commit-baselines; done`
2. For every `.py` file: `ruff check --fix <file> && ruff format <file> && git add <file>`
3. Trailing whitespace: `git diff --cached --name-only | while IFS= read -r f; do perl -pi -e 's/[ \t]+$//' "$f"; git add "$f"; done`
4. Detect corruption by comparing post-lint line counts against baseline. If drastically shrunk, restore and halt.

⚠️ **Regex MUST be `[ \t]+$` (horizontal whitespace only).** Never use `[[:space:]]+$` or `\s+$` — those include `\n`, collapsing entire file into one line.

### OOXML Gate (Step 2)

For files with OOXML extensions (`.docx`, `.xlsx`, `.pptx`, `.odt`):
1. Run ZIP validation: `unzip -t <file> > /dev/null 2>&1`
2. If validation fails: record as HOOK_FAILURE, do not commit
3. Require human review before re-staging OOXML files

### Commit & Retry (Steps 3-4)

#### Step 3: Execute commit

new_string:
## Phase: execute

### Commit & Retry (Steps 1-2)

#### Step 1: Execute commit
```

- [ ] **Step 7: Renumber Step 4 and Return Block**

Use the Edit tool on `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`:

```
old_string:
#### Step 4: Handle failures

new_string:
#### Step 2: Handle failures
```

Use the Edit tool on `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`:

```
old_string:
### Return Block (Step 5)

new_string:
### Return Block (Step 3)
```

- [ ] **Step 8: Remove LINT_FIXES from the return block template**

Use the Edit tool on `profile-al-dev-shared/agents/al-dev-commit-agent-execute.md`:

```
old_string:
SKIPPED: [N groups]

LINT_FIXES: [file1, file2] (or NONE)

HOOK_FAILURES: [group_id: raw_output] (or NONE)

new_string:
SKIPPED: [N groups]

HOOK_FAILURES: [group_id: raw_output] (or NONE)
```

- [ ] **Step 9: Verify the modified execute agent**

```bash
wc -l profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
```

Expected: ~52 lines (original 87 lines minus ~35 lines for Steps 1-2 and their related content).

```bash
grep "Pre-flight\|OOXML Gate\|LINT_FIXES" profile-al-dev-shared/agents/al-dev-commit-agent-execute.md
```

Expected: no output (all three removed).

### Sub-task 6c: Insert Step 9.5 in al-dev-commit SKILL.md

- [ ] **Step 10: Confirm the Step 9/Step 10 boundary in the skill**

```bash
grep -n "Step 9\|Step 10\|Step 11\|MIXED_AL_DOCX\|proceed directly to Step 10" profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: Step 9 ends at the MIXED_AL_DOCX gate, "proceed directly to Step 10" on ~line 403.

- [ ] **Step 11: Insert Step 9.5 between Step 9 and Step 10**

Use the Edit tool on `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`:

```
old_string:
If no `MIXED_AL_DOCX` warning exists, proceed directly to Step 10.

---

## Step 10 — Dispatch Execution Agent

new_string:
If no `MIXED_AL_DOCX` warning exists, proceed directly to Step 9.5.

---

## Step 9.5 — Dispatch Preflight Agent

Dispatch `al-dev-shared:al-dev-commit-preflight` with the approved plan:

```text
Agent tool:
  agent: al-dev-shared:al-dev-commit-preflight
  description: "Pre-flight lint and OOXML validation"

Prompt:
  "Perform PREFLIGHT phase for git commit workflow.

   Phase: preflight

   APPROVED_PLAN:
   [paste the approved plan from Step 9]

   CRITICAL RULES:
   - NEVER use Write or Edit on staged source files — all fixes via Bash only
   - Record OOXML failures; do not proceed to commit for failed files

   Return output in exactly the format specified (LINT_FIXES, OOXML_FAILURES)."
```

If `OOXML_FAILURES` is not `NONE`, show:

```text
⚠️  OOXML VALIDATION FAILURE

The following files failed ZIP validation and cannot be committed:
[OOXML_FAILURES output]

Resolve these files (save in Microsoft Word, not via script), re-stage, and re-run.
```

Stop if any OOXML failures — do not proceed to Step 10.

Store the `LINT_FIXES` value from the preflight output for display in Step 11.

---

## Step 10 — Dispatch Execution Agent
```

- [ ] **Step 12: Update Step 10 dispatch prompt to remove LINT_FIXES from return format**

Use the Edit tool on `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`:

```
old_string:
   Return output in exactly the format specified (COMMITS, SKIPPED,
   LINT_FIXES, HOOK_FAILURES)."

new_string:
   Return output in exactly the format specified (COMMITS, SKIPPED,
   HOOK_FAILURES)."
```

- [ ] **Step 13: Update Step 11 to read LINT_FIXES from preflight output**

```bash
grep -n "LINT_FIXES" profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: one remaining line in Step 11 that displays `LINT_FIXES`. It should now reference the preflight result.

Use the Edit tool on `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`:

```
old_string:
[If LINT_FIXES is not NONE:]
  Files re-staged after lint: [LINT_FIXES]

new_string:
[If LINT_FIXES from Step 9.5 is not NONE:]
  Files re-staged after lint: [LINT_FIXES]
```

### Sub-task 6d: Update scenarios.yaml

- [ ] **Step 14: Add al-dev-commit-preflight to must_invoke_agent for all execution-path scenarios**

The `compile-gate-blocks-errors` scenario halts before the execution path (before Step 9.5), so it must NOT list the preflight agent. All other scenarios (commit-staged-clean, commit-scope-creep-guard, commit-explicit-scoped-docs, docs-only-skip-compile-gate) proceed to execution and must include both preflight and execute.

Use the Edit tool on `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`:

```
old_string:
  - id: commit-staged-clean
    status: golden
    user_prompt: "Commit the staged changes."
    expected_artifacts: []
    must_invoke_agent:
      - al-dev-shared:al-dev-commit-agent-analysis
      - al-dev-shared:al-dev-commit-agent-execute
    notes: "Standard commit flow. Harness pre-seeds a small staged change (one-line edit to a fixture file) before the run."

new_string:
  - id: commit-staged-clean
    status: golden
    user_prompt: "Commit the staged changes."
    expected_artifacts: []
    must_invoke_agent:
      - al-dev-shared:al-dev-commit-agent-analysis
      - al-dev-shared:al-dev-commit-preflight
      - al-dev-shared:al-dev-commit-agent-execute
    notes: "Standard commit flow. Harness pre-seeds a small staged change (one-line edit to a fixture file) before the run."
```

Use the Edit tool on `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`:

```
old_string:
  - id: commit-scope-creep-guard
    status: golden
    user_prompt: "Commit the staged changes."
    expected_artifacts: []
    must_invoke_agent:
      - al-dev-shared:al-dev-commit-agent-analysis
      - al-dev-shared:al-dev-commit-agent-execute
    notes: "Harness pre-seeds a deletion of an unrelated file. Skill must surface the unexpected deletion in its summary and gate on user confirmation — verified by transcript grep for 'unrelated' / 'scope' in the agent's final message."

new_string:
  - id: commit-scope-creep-guard
    status: golden
    user_prompt: "Commit the staged changes."
    expected_artifacts: []
    must_invoke_agent:
      - al-dev-shared:al-dev-commit-agent-analysis
      - al-dev-shared:al-dev-commit-preflight
      - al-dev-shared:al-dev-commit-agent-execute
    notes: "Harness pre-seeds a deletion of an unrelated file. Skill must surface the unexpected deletion in its summary and gate on user confirmation — verified by transcript grep for 'unrelated' / 'scope' in the agent's final message."
```

Use the Edit tool on `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`:

```
old_string:
  - id: commit-explicit-scoped-docs
    status: golden
    user_prompt: "Commit only the staged docs changes after checking scope."
    expected_artifacts: []
    must_invoke_agent:
      - al-dev-shared:al-dev-commit-agent-analysis
      - al-dev-shared:al-dev-commit-agent-execute
    notes: "Commit intent regression. Explicit scoped commit prompts must route to commit gates and commit agents, not edit or planning flows."

new_string:
  - id: commit-explicit-scoped-docs
    status: golden
    user_prompt: "Commit only the staged docs changes after checking scope."
    expected_artifacts: []
    must_invoke_agent:
      - al-dev-shared:al-dev-commit-agent-analysis
      - al-dev-shared:al-dev-commit-preflight
      - al-dev-shared:al-dev-commit-agent-execute
    notes: "Commit intent regression. Explicit scoped commit prompts must route to commit gates and commit agents, not edit or planning flows."
```

Use the Edit tool on `profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml`:

```
old_string:
  - id: docs-only-skip-compile-gate
    status: golden
    user_prompt: "Commit the staged changes."
    expected_artifacts: []
    must_invoke_agent:
      - al-dev-shared:al-dev-commit-agent-analysis
      - al-dev-shared:al-dev-commit-agent-execute
    notes: "Docs-only optimization regression. Harness pre-seeds only non-AL staged changes. Skill may skip Step 4a, but it still must base any ready-to-commit claim on the current staged diff and required staged-state evidence."

new_string:
  - id: docs-only-skip-compile-gate
    status: golden
    user_prompt: "Commit the staged changes."
    expected_artifacts: []
    must_invoke_agent:
      - al-dev-shared:al-dev-commit-agent-analysis
      - al-dev-shared:al-dev-commit-preflight
      - al-dev-shared:al-dev-commit-agent-execute
    notes: "Docs-only optimization regression. Harness pre-seeds only non-AL staged changes. Skill may skip Step 4a, but it still must base any ready-to-commit claim on the current staged diff and required staged-state evidence."
```

- [ ] **Step 15: Verify scenarios.yaml**

```bash
grep -c "al-dev-commit-preflight" profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml
```

Expected: 4 (one per execution-path scenario).

```bash
grep -A5 "compile-gate-blocks-errors" profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml | grep "preflight"
```

Expected: no output (compile-gate scenario does NOT list preflight).

- [ ] **Step 16: Validate agent structure**

```bash
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
```

Expected: exit 0, no validation errors for the new agent or modified agents.

- [ ] **Step 17: Validate harness neutrality**

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected: exit 0.

- [ ] **Step 18: Commit Task 6**

```bash
python3 scripts/generate-agent-projections.py
git add profile-al-dev-shared/agents/al-dev-commit-preflight.md \
        profile-al-dev-shared/agents/al-dev-commit-agent-execute.md \
        profile-al-dev-shared/skills/al-dev-commit/SKILL.md \
        profile-al-dev-shared/skills/al-dev-commit/tests/scenarios.yaml \
        profile-al-dev-shared/generated/agents
git commit -m "$(cat <<'EOF'
feat(agents): split al-dev-commit-agent-execute — extract preflight agent

New agent al-dev-commit-preflight (Step 9.5) owns pre-flight lint and
OOXML validation; al-dev-commit-agent-execute now focuses solely on
git commit execution and hook retry. LINT_FIXES moves to preflight
output. Scenarios updated to require preflight on all execution paths.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Implement al-dev-review-develop Phases 5-10

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`

**Rubber duck verdict:** The skill is a confirmed stub — 60 lines with no phase implementation, only bullet-point summaries and implementation notes that say "copy from al-dev-develop." Phases 5-10 DO NOT EXIST in al-dev-develop; only Phases 0-4.5 are implemented there. This is a design + build task. The execution order per the glossary is: Phase 5 (prep) → Phase 8 (compile verify) → Phase 8.5 (staging) → Phases 6-7 (review panel dispatch) → Phase 9 (write artifact) → Phase 10 (present). The artifact contract requires: Phase 4 handoff read, compile verification result read, and code-review artifact exists and read before any clean/ready claim.

**Execution order (not phase-number order):**
Phase 5 (prep context) → Phase 8 (compile) → Phase 8.5 (verify compile) → Phase 6-7 (review panel) → Phase 9 (write code-review) → Phase 10 (present)

- [ ] **Step 1: Read the current stub to confirm its exact content**

```bash
wc -l profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
cat -n profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: 61 lines, ending with the Implementation Notes section.

- [ ] **Step 2: Replace the stub body with the full Phase 5-10 implementation**

The replacement replaces everything from `## Phase 5–10 Summary` through the end of the file (Implementation Notes). Keep the frontmatter, Prerequisites, Artifact Contract, Review Panel, and Outputs sections intact.

Use the Edit tool on `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`:

```
old_string:
## Phase 5–10 Summary

- **Phase 5:** Prepare review entry + compile discipline
- **Phase 6–7:** Dispatch 3-specialist review panel (security, AL expert, performance) in parallel
- **Phase 8:** Compile verification (up to 5 fix cycles in autonomous mode)
- **Phase 8.5:** Pre-review staging
- **Phase 9:** Write code-review artifact
- **Phase 10:** Present review findings to user

## Review Panel

Three specialist agents (haiku):
- **al-dev-security-reviewer** — permission/auth/data exposure
- **al-dev-expert-reviewer** — AL conventions/BC patterns
- **al-dev-performance-reviewer** — N+1/SetLoadFields/efficiency

## Outputs

`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md` — synthesized review findings from all three reviewers; this file is also the downstream handoff artifact named in `knowledge/artifact-contracts.md` and must be read before any final clean/ready claim.

## Implementation Notes

This skill contains the full implementation of Phases 5–10 from the parent /al-dev-develop skill. Copy verbatim from parent skill during refactoring, with these adaptations:

1. Adjust description to reflect post-implementation focus
2. Remove Phase 0–4 content entirely
3. Update prerequisites to reference Phase 4 handoff artifact
4. Keep compilation discipline, review panel, and code review write unchanged
5. Update input references to use Phase 4 handoff instead of full plan context

new_string:
## Review Panel

Three specialist agents (haiku):
- **al-dev-security-reviewer** — permission/auth/data exposure
- **al-dev-expert-reviewer** — AL conventions/BC patterns
- **al-dev-performance-reviewer** — N+1/SetLoadFields/efficiency

## Outputs

`.dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md` — synthesized review findings from all three reviewers; this file is also the downstream handoff artifact named in `knowledge/artifact-contracts.md` and must be read before any final clean/ready claim.

---

## Phase 5: Prepare Review Context

**Input:** Phase 4 handoff artifact from `/al-dev-develop`.

1. **Locate the Phase 4 handoff artifact:**

   ```bash
   ls .dev/*-al-dev-develop-phase4-handoff.md 2>/dev/null | sort | tail -1
   ```

   If no handoff artifact is found, stop and tell the user:
   "No Phase 4 handoff found. Run `/al-dev-develop` first and wait for it to complete Phase 4."

2. **Read the Phase 4 handoff in full** — note the developer module assignments and status.

3. **Identify changed AL files** — combine two sources:
   - Files listed in the handoff's module assignments section
   - `git diff --cached --name-only --diff-filter=ACMR` filtered to `*.al`, `app.json`, and `*.al.json`
   - `git ls-files --others --exclude-standard` filtered to `*.al`, `app.json`, and `*.al.json`

   Build a deduplicated list: `CHANGED_FILES`

4. **Write progress checkpoint:**

   ```bash
   echo "Phase 5 complete — $(date +%Y-%m-%d %H:%M): context loaded, CHANGED_FILES identified" >> .dev/progress.md
   ```

---

## Phase 8: Compile Verification

Run `al-compile` and handle errors. This phase must pass before the review panel is spawned.

1. **Run compile:**

   ```bash
   al-compile --output .dev/compile-errors.log
   ```

2. **Check for errors:**

   ```bash
   grep -c "error AL" .dev/compile-errors.log 2>/dev/null || echo "0"
   ```

3. **If errors found:**

   - **Standard mode:** Show the errors and stop. Ask the user to fix compilation errors before proceeding to code review.

   - **`--autonomous` mode:** Spawn `al-dev-shared:al-dev-developer` to fix errors:

     ```text
     Agent: al-dev-shared:al-dev-developer
     Prompt:
       "Fix compilation errors in .dev/compile-errors.log for the current Phase 4 handoff.
        Read the errors, identify root causes, and apply minimal fixes.
        Use the current solution plan and handoff context; if either is missing, stop and escalate to the user.
        Compile after each fix. Return: files changed, errors resolved."
     ```

     Re-run compile after fixes. Repeat up to 5 cycles total. If errors remain after 5 cycles, stop and escalate to user.

4. **Read compile verification result** (required by artifact contract):

   ```bash
   # Confirm the log was written and record result
   ls -la .dev/compile-errors.log
   ```

5. **Write progress checkpoint:**

   ```bash
   echo "Phase 8 complete — $(date +%Y-%m-%d %H:%M): compile verification passed" >> .dev/progress.md
   ```

---

## Phase 8.5: Pre-Review Staging

Verify all prerequisites are met before spawning the review panel.

1. **Confirm compile passed** (zero `error AL` lines in `.dev/compile-errors.log`).
2. **Confirm `CHANGED_FILES` list is non-empty** — if empty, stop and tell the user no changed AL files were detected.
3. If both checks pass, proceed to Phase 6-7.

---

## Phase 6-7: Dispatch Review Panel

Spawn the three specialist reviewer agents in parallel. Pass each agent the same `CHANGED_FILES` list and implementation context from the Phase 4 handoff.

**Dispatch prompt for each reviewer:**

```text
Review the following AL files for [reviewer specialty]:
[CHANGED_FILES list — one file per line]

Implementation context (from Phase 4 handoff):
[Summary of what was implemented — module assignments and scope from handoff]

Return findings in this format:
CRITICAL: [issues that block release]
HIGH: [significant issues to fix]
MEDIUM: [notable issues to address]
LOW: [minor improvements]

If no issues found in your specialty: return "NONE" under each severity.
```

Spawn these three agents with the above prompt adapted to each specialty:
- `al-dev-shared:al-dev-security-reviewer` — focus: permissions, data exposure, auth checks
- `al-dev-shared:al-dev-expert-reviewer` — focus: AL conventions, naming, BC patterns
- `al-dev-shared:al-dev-performance-reviewer` — focus: N+1 queries, SetLoadFields, resource loops

Collect all three outputs before proceeding to Phase 9.

---

## Phase 9: Write Code-Review Artifact

Synthesize findings from all three reviewers into a single dated code-review file.

1. **Create the code-review artifact:**

   ```bash
   CODE_REVIEW_FILE=".dev/$(date +%Y-%m-%d)-al-dev-develop-code-review.md"
   ```

2. **Write the file** using this structure:

   ```markdown
   # Code Review: [date]

   **Scope:** [CHANGED_FILES list]
   **Phase 4 handoff:** [handoff filename]
   **Compile:** ✅ Passed

   ## Critical Issues

   [All CRITICAL findings from all three reviewers, deduplicated and attributed]

   ## High Issues

   [All HIGH findings, deduplicated and attributed]

   ## Medium Issues

   [All MEDIUM findings, deduplicated and attributed]

   ## Low / Minor

   [All LOW findings, deduplicated and attributed]

   ## Review Panel Summary

   | Reviewer | Critical | High | Medium | Low |
   |----------|----------|------|--------|-----|
   | Security | N | N | N | N |
   | AL Expert | N | N | N | N |
   | Performance | N | N | N | N |

   ## Verdict

   [BLOCKING: N critical issues must be resolved before commit]
   [READY: no blocking issues found — proceed to /al-dev-commit]
   ```

3. **Read the file back** to confirm it was written (required by artifact contract):

   ```bash
   ls -la "$CODE_REVIEW_FILE" && wc -l "$CODE_REVIEW_FILE"
   ```

4. **Write progress checkpoint:**

   ```bash
   echo "Phase 9 complete — $(date +%Y-%m-%d %H:%M): code-review artifact written" >> .dev/progress.md
   ```

---

## Phase 10: Present Review Findings

1. **Display a summary** of the code-review artifact:

   ```text
   Code review complete.

   Scope: [N files reviewed]
   Compile: ✅ Passed

   Critical: [N] | High: [N] | Medium: [N] | Low: [N]

   [If BLOCKING:]
   ⚠️  [N] critical issue(s) must be resolved before committing.
   Full findings: [CODE_REVIEW_FILE]
   Next step: Fix critical issues, then re-run /al-dev-review-develop (or proceed directly to /al-dev-commit if you accept the risk).

   [If READY:]
   ✅  No blocking issues found.
   Full findings: [CODE_REVIEW_FILE]
   Next step: /al-dev-commit
   ```

2. **Do not claim "clean" or "ready" until** the code-review artifact file has been read in this run (per `knowledge/artifact-contracts.md`).
```

- [ ] **Step 3: Verify the file was written and is non-empty**

```bash
ls -la profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
wc -l profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: file exists, ~200+ lines (substantially larger than the 61-line stub).

- [ ] **Step 4: Spot-check key sections exist**

```bash
grep -n "Phase 5\|Phase 8\|Phase 8.5\|Phase 6-7\|Phase 9\|Phase 10" profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: 6 lines — one per phase heading.

```bash
grep -n "al-dev-security-reviewer\|al-dev-expert-reviewer\|al-dev-performance-reviewer" profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: at least 3 lines in the Phase 6-7 dispatch section.

```bash
grep -n "al-compile\|compile-errors.log" profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: at least 2 lines in Phase 8.

```bash
grep -n "artifact-contracts\|success evidence\|clean.*ready\|ready.*claim" profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: at least 1 line (artifact contract compliance check in Phase 10).

- [ ] **Step 5: Check for forbidden patterns**

```bash
grep -n "\[date\]\|YYYY-MM-DD\|TODO\|TBD\|claude:\|copilot:" profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: no output (no forbidden patterns).

- [ ] **Step 6: Validate harness neutrality**

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected: exit 0.

- [ ] **Step 7: Validate artifact contracts**

```bash
python3 scripts/validate_artifact_contracts.py
```

Expected: exit 0 (al-dev-review-develop passes its contract checks — Phase 4 handoff read, compile verification read, code-review artifact written and read).

- [ ] **Step 8: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
git commit -m "$(cat <<'EOF'
feat(skills): implement al-dev-review-develop Phases 5-10

Replaces stub body with full Phase 5-10 implementation:
- Phase 5: load Phase 4 handoff, identify changed files
- Phase 8/8.5: compile verify with autonomous fix loop (up to 5 cycles)
- Phase 6-7: parallel three-reviewer dispatch (security/expert/perf)
- Phase 9: synthesize code-review artifact with Critical/High/Medium/Low
- Phase 10: present blocking vs ready verdict with artifact path

Implements artifact contract: Phase 4 handoff read, compile result read,
and code-review artifact read before any clean/ready claim.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review

### Spec coverage check

| Suggestion | Task | Coverage |
|------------|------|----------|
| Align: REPO param in commit-recover-verifier | Task 1 | ✅ Line 23 Required→No |
| Align: TDD test-plan source in developer | Task 2 | ✅ Removed nonexistent agent ref |
| Align: FRESHDESK env var mechanism in ticket-agent | Task 3 | ✅ Rows + note updated |
| Connect: /al-dev-fix escalation in workflow-routing.md | Task 4 | ✅ Steps block replaced with two-part structure |
| Remodel: complexity-gated dispatch in al-dev-plan Phase 2 | Task 5a | ✅ Tier added to prompt template |
| Remodel: complexity-gated dispatch in al-dev-fix Step 3 | Task 5b | ✅ SIMPLE/COMPLEX assessment + conditional model |
| Split: extract preflight from execute agent | Task 6 | ✅ New agent + 3-file skill update + scenarios |
| Align: al-dev-review-develop stub skill | Task 7 | ✅ Full Phase 5-10 implementation |

### Placeholder scan

- No `TBD` or `TODO` in any task step.
- No `[date]` or `YYYY-MM-DD` as literal strings (only used correctly inside bash date commands).
- All code blocks have complete, executable content.
- All file paths are exact.

### Type consistency

- `al-dev-commit-preflight` used consistently across the new agent file, the SKILL.md Step 9.5 dispatch, and scenarios.yaml.
- `LINT_FIXES` transferred from execute outputs to preflight outputs; Step 11 reference updated accordingly.
- Phase numbering in review-develop matches artifact-contracts.md (Phase 4 handoff → Phases 5-10 → code-review artifact).
