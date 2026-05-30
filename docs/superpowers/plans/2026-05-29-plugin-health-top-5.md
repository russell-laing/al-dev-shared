# Plugin Health Fixes — Top 5 Actions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address the top 5 harness-agnostic findings from the 2026-05-29 plugin health sweep: agent model downgrades, reviewer template consolidation, tool/frontmatter canonicality, operational clarity gaps, and stale documentation maps.

**Architecture:** Five independent fix categories executed in order: (1) Knowledge extraction for reviewer template, (2) Agent file edits (frontmatter, model IDs, tool names, clarity fixes), (3) Documentation map updates. All changes maintain harness-agnostic vocabulary. Each commit is atomic.

**Tech Stack:** AL development plugin system (profile-al-dev-shared/), Markdown skill/agent definitions, knowledge files, plugin map documentation.

---

## Task Breakdown

### Task 1: Create Knowledge File — Review Panel Invocation Pattern

**Files:**
- Create: `profile-al-dev-shared/knowledge/review-panel-invocation-pattern.md`

**Rationale:** Both `/al-dev-develop` and `/al-dev-review-develop` currently inline the three-reviewer dispatch template. Extract to a canonical reference to reduce duplication and enable consistent updates.

- [ ] **Step 1: Read the current dispatch template from al-dev-review-develop**

Run:
```bash
sed -n '145,166p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected output: Phase 6-7 dispatch prompt section (lines 145-166).

- [ ] **Step 2: Create the new knowledge file with reviewer dispatch pattern**

Write to `profile-al-dev-shared/knowledge/review-panel-invocation-pattern.md`:

```markdown
# Review Panel Dispatch Pattern

The three-specialist review panel is the standard parallel reviewer composition spawned by:
- `/al-dev-develop` (Phase 6–7, after developers complete and compilation passes)
- `/al-dev-review-develop` (Phase 6–7, specialized review dispatch)

## Standard Dispatch Template

Spawn all three reviewers simultaneously (same message, three independent agent dispatch blocks). Each reviewer reads the same CHANGED_FILES list and implementation context.

**Dispatch prompt structure (adapt specialty per reviewer):**

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

## Reviewer Specialties

**al-dev-shared:al-dev-security-reviewer**
- Focus: permissions, data exposure, authentication checks
- Pattern: parallel, reads all files, security-domain findings

**al-dev-shared:al-dev-expert-reviewer**
- Focus: AL conventions, naming consistency, BC design patterns
- Pattern: parallel, reads all files, pattern-domain findings

**al-dev-shared:al-dev-performance-reviewer**
- Focus: N+1 queries, SetLoadFields usage, resource loops
- Pattern: parallel, reads all files, efficiency-domain findings

## Synthesis (after all three complete)

1. Read all three review outputs
2. Cross-reference overlapping findings — issues raised by multiple reviewers are higher priority
3. Where reviewers contradict (e.g., pattern rec vs. performance concern), apply skill judgment using severity categories
4. Consolidate into single categorised list before assigning fixes

## Handoff from Implementation

The calling skill passes:
- `CHANGED_FILES` — file list from Phase 4 handoff (all AL files modified)
- Implementation context — summary of modules, scope, key design decisions
- Reviewer specialty (implicit via agent selection)

Each reviewer is independent; no coordination needed between them.
```

- [ ] **Step 3: Verify file was written**

Run:
```bash
ls -la profile-al-dev-shared/knowledge/review-panel-invocation-pattern.md && wc -l profile-al-dev-shared/knowledge/review-panel-invocation-pattern.md
```

Expected: File exists, non-empty (60+ lines).

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/review-panel-invocation-pattern.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
docs(knowledge): add review-panel-invocation-pattern knowledge file

Extract three-reviewer dispatch template from al-dev-review-develop into
canonical knowledge reference. Both develop and review-develop skills will
reference this instead of inlining. Reduces duplication and ensures
consistent reviewer dispatch across workflow.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds with 1 file changed.

---

### Task 2: Update al-dev-review-develop to Reference Knowledge File

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md` (lines 141-167)

**Rationale:** Replace the inlined Phase 6-7 dispatch template with a reference to the new knowledge file. Update the dispatch prompt to use variable substitution for reviewer specialty.

- [ ] **Step 1: Read current Phase 6-7 section**

Run:
```bash
sed -n '141,167p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected output: Full Phase 6-7 dispatch section (currently ~27 lines inlined).

- [ ] **Step 2: Replace inlined template with knowledge reference**

Edit `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`, lines 141-167.

Old section (lines 141-167):
```markdown
## Phase 6-7: Dispatch Review Panel

Spawn all three specialist reviewer agents simultaneously — do not wait for one agent to return before spawning the next. Pass each agent the same `CHANGED_FILES` list and implementation context from the Phase 4 handoff.

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
```

Replace with:
```markdown
## Phase 6-7: Dispatch Review Panel

Spawn all three specialist reviewer agents simultaneously — do not wait for one agent to return before spawning the next. Pass each agent the same `CHANGED_FILES` list and implementation context from the Phase 4 handoff.

**See `knowledge/review-panel-invocation-pattern.md` for the standard dispatch template and reviewer specialties.**

Dispatch structure:
- Each reviewer receives the dispatch prompt adapted to their specialty (see knowledge file)
- `CHANGED_FILES` — list of all modified AL files (one per line)
- Implementation context — summary from Phase 4 handoff (modules, scope, key decisions)

Spawn order (simultaneous, all in one message):
1. `al-dev-shared:al-dev-security-reviewer` — permissions, data exposure, auth checks
2. `al-dev-shared:al-dev-expert-reviewer` — AL conventions, naming, BC patterns
3. `al-dev-shared:al-dev-performance-reviewer` — N+1 queries, SetLoadFields, resource loops

Collect all three outputs before proceeding to Phase 9.
```

- [ ] **Step 3: Verify changes**

Run:
```bash
sed -n '141,158p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
```

Expected: Inlined template is gone; reference to knowledge file is present; line count is significantly reduced (~18 lines vs ~27).

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
refactor(skills): de-inline reviewer dispatch template in review-develop

Replace 27-line inlined Phase 6-7 dispatch template with reference to
knowledge/review-panel-invocation-pattern.md. Single source of truth for
reviewer spawn pattern; both al-dev-develop and al-dev-review-develop
now reference instead of duplicating.

Reduces bloat in review-develop skill by ~27 lines.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 1 file changed, ~20 lines deleted.

---

### Task 3: Remove Spurious `name:` Fields from 4 Agents

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-preflight.md` (line 2)
- Modify: `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md` (line 2)
- Modify: `profile-al-dev-shared/agents/al-dev-support-reply-drafter.md` (line 2)
- Modify: `profile-al-dev-shared/agents/al-dev-support-researcher.md` (line 2)

**Rationale:** Agents use filename for identity; `name:` is a skill-only frontmatter field. Remove from all four agents.

- [ ] **Step 1: Verify which agents have the spurious field**

Run:
```bash
grep -n "^name:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/*.md
```

Expected: 4 hits (commit-preflight, commit-recover-verifier, support-reply-drafter, support-researcher).

- [ ] **Step 2: Remove `name:` from al-dev-commit-preflight.md**

Edit line 2 of `profile-al-dev-shared/agents/al-dev-commit-preflight.md`.

Old:
```yaml
name: al-dev-commit-preflight
description: >-
```

New:
```yaml
description: >-
```

- [ ] **Step 3: Remove `name:` from al-dev-commit-recover-verifier.md**

Edit line 2 of `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md`.

Old:
```yaml
name: al-dev-commit-recover-verifier
description: >-
```

New:
```yaml
description: >-
```

- [ ] **Step 4: Remove `name:` from al-dev-support-reply-drafter.md**

Edit line 2 of `profile-al-dev-shared/agents/al-dev-support-reply-drafter.md`.

Old:
```yaml
name: al-dev-support-reply-drafter
description: >-
```

New:
```yaml
description: >-
```

- [ ] **Step 5: Remove `name:` from al-dev-support-researcher.md**

Edit line 2 of `profile-al-dev-shared/agents/al-dev-support-researcher.md`.

Old:
```yaml
name: al-dev-support-researcher
description: >-
```

New:
```yaml
description: >-
```

- [ ] **Step 6: Verify all changes**

Run:
```bash
grep -n "^name:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/*.md
```

Expected: No output (no matches).

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/agents/al-dev-commit-preflight.md \
  profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md \
  profile-al-dev-shared/agents/al-dev-support-reply-drafter.md \
  profile-al-dev-shared/agents/al-dev-support-researcher.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(agents): remove spurious name: field from 4 agent frontmatters

Agents use filename for identity. The 'name:' field is a skill-only
frontmatter field and must not appear in agent definitions.

Removed from:
- al-dev-commit-preflight
- al-dev-commit-recover-verifier
- al-dev-support-reply-drafter
- al-dev-support-researcher

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 4 files changed, 4 lines deleted (one per file).

---

### Task 4: Normalize All Agent Model IDs to Canonical Form

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md` (line 7)
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent-analysis.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-commit-message-drafter.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-commit-preflight.md` (line 8)
- Modify: `profile-al-dev-shared/agents/al-dev-docs-writer.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-expert-reviewer.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-explore.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-interview.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-performance-reviewer.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-release-notes-writer.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-script-engineer.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-security-reviewer.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-solution-architect.md` (line 5)
- Modify: `profile-al-dev-shared/agents/al-dev-support-reply-drafter.md` (line 6)
- Modify: `profile-al-dev-shared/agents/al-dev-ticket-agent.md` (line 6)

**Rationale:** Non-canonical aliases (`haiku`, `sonnet`, `opus`) must be normalized to full canonical IDs for harness projection consistency:
- `haiku` → `claude-haiku-4-5-20251001`
- `sonnet` → `claude-sonnet-4-6`
- `opus` → `claude-opus-4-8`

- [ ] **Step 1: List all current non-canonical model aliases**

Run:
```bash
grep "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/*.md | grep -v "claude-"
```

Expected: ~13 hits with `model: haiku`, `model: sonnet`, `model: opus`, or `model: sonnet  # comment`.

- [ ] **Step 2: Bulk replace haiku aliases**

Run:
```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" -exec sed -i '' 's/^model: haiku$/model: claude-haiku-4-5-20251001/g' {} +
```

- [ ] **Step 3: Bulk replace sonnet aliases**

Run:
```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" -exec sed -i '' 's/^model: sonnet$/model: claude-sonnet-4-6/g' {} +
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" -exec sed -i '' 's/^model: sonnet  # /model: claude-sonnet-4-6  # /g' {} +
```

- [ ] **Step 4: Bulk replace opus aliases**

Run:
```bash
find /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents -name "*.md" -exec sed -i '' 's/^model: opus$/model: claude-opus-4-8/g' {} +
```

- [ ] **Step 5: Verify all aliases replaced**

Run:
```bash
grep "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/*.md | grep -v "claude-"
```

Expected: No output (all normalized).

- [ ] **Step 6: Spot-check canonical form in a few files**

Run:
```bash
sed -n '6,8p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-code-review.md
sed -n '5,7p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md
```

Expected: `model: claude-sonnet-4-6` and `model: claude-opus-4-8` visible.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/*.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(agents): normalize all model IDs to canonical form

Replace non-canonical aliases with full model IDs for harness projection
consistency:
- haiku → claude-haiku-4-5-20251001
- sonnet → claude-sonnet-4-6
- opus → claude-opus-4-8

Affects 16 agents. Ensures all three harnesses (Claude Code, Copilot CLI,
Codex) receive consistent model assignments.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; many files changed, lines updated.

---

### Task 5: Fix Non-Canonical Tool Names (USER_GATE, MCP Prefix)

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-interview.md`
- Modify: `profile-al-dev-shared/agents/al-dev-release-notes-writer.md`
- Modify: `profile-al-dev-shared/agents/al-dev-solution-architect.md`
- Modify: `profile-al-dev-shared/agents/al-dev-support-researcher.md`

**Rationale:** Normalize non-canonical tool names:
- `USER_GATE` → `AskUserQuestion`
- `MCP: ...` → `mcp__...` (double underscore, lowercase prefix)

- [ ] **Step 1: Verify non-canonical tool names**

Run:
```bash
grep -n "USER_GATE\|MCP:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/*.md
```

Expected: `al-dev-interview` has USER_GATE; release-notes-writer, solution-architect, support-researcher have MCP: prefixes.

- [ ] **Step 2: Fix al-dev-interview.md — Replace USER_GATE with AskUserQuestion**

Edit `profile-al-dev-shared/agents/al-dev-interview.md`:

Find and replace `USER_GATE` → `AskUserQuestion` (2 occurrences: tools list + body reference).

Old (tools line):
```yaml
tools: ["Read", "Write", "USER_GATE"]
```

New:
```yaml
tools: ["Read", "Write", "AskUserQuestion"]
```

Also update any references in the body (search for "USER_GATE" in the file).

- [ ] **Step 3: Fix al-dev-release-notes-writer.md — Replace MCP: with mcp__**

Edit `profile-al-dev-shared/agents/al-dev-release-notes-writer.md`:

Old (tools lines 7-11):
```yaml
tools: [
  "Bash", "Write", "Read",
  "MCP: al-mcp-server",
  "MCP: bc-code-intelligence"
]
```

New:
```yaml
tools: [
  "Bash", "Write", "Read",
  "mcp__al-mcp-server",
  "mcp__bc-code-intelligence"
]
```

- [ ] **Step 4: Fix al-dev-solution-architect.md — Replace MCP: with mcp__**

Edit `profile-al-dev-shared/agents/al-dev-solution-architect.md`:

Old (tools lines 6-11):
```yaml
tools: [
  "Read", "Write", "Glob", "Grep",
  "MCP: bc-code-intelligence",
  "MCP: microsoft-docs",
  "MCP: al-mcp-server"
]
```

New:
```yaml
tools: [
  "Read", "Write", "Glob", "Grep",
  "mcp__bc-code-intelligence",
  "mcp__microsoft-docs",
  "mcp__al-mcp-server"
]
```

- [ ] **Step 5: Fix al-dev-support-researcher.md — Replace MCP: with mcp__**

Edit `profile-al-dev-shared/agents/al-dev-support-researcher.md`:

Old (tools lines 8-12):
```yaml
tools: [
  "Read",
  "MCP: al-mcp-server",
  "MCP: microsoft-docs",
  "MCP: bc-code-intelligence"
]
```

New:
```yaml
tools: [
  "Read",
  "mcp__al-mcp-server",
  "mcp__microsoft-docs",
  "mcp__bc-code-intelligence"
]
```

- [ ] **Step 6: Verify all tool names are canonical**

Run:
```bash
grep -n "USER_GATE\|MCP:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/*.md
```

Expected: No output (all normalized).

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/agents/al-dev-interview.md \
  profile-al-dev-shared/agents/al-dev-release-notes-writer.md \
  profile-al-dev-shared/agents/al-dev-solution-architect.md \
  profile-al-dev-shared/agents/al-dev-support-researcher.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(agents): normalize tool names to canonical form

Standardize non-canonical tool names:
- al-dev-interview: USER_GATE → AskUserQuestion
- 3 agents: MCP: prefix → mcp__ (double underscore)

Affects:
- al-dev-interview
- al-dev-release-notes-writer
- al-dev-solution-architect
- al-dev-support-researcher

Ensures harness projection layer receives canonical names.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 4 files changed, 5+ lines updated.

---

### Task 6: Fix Operational Clarity Gaps in al-dev-commit-preflight

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-preflight.md` (lines 31–55)

**Rationale:** Three operational issues: (1) incomplete baseline-capture code block, (2) undeclared perl dependency, (3) regex safety note in wrong position. All fixes improve clarity without changing logic.

- [ ] **Step 1: Read current Step 1 (baseline-capture and lint)**

Run:
```bash
sed -n '31,55p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-preflight.md
```

Expected: Current Phase preflight section with issues.

- [ ] **Step 2: Fix regex safety note position and perl issue**

Edit lines 31–55. Replace the entire section with:

```markdown
## Phase: preflight

### Pre-flight Lint (Step 1)

⚠️ **Regex MUST be `[ \t]+$` (horizontal whitespace only).** Never use `[[:space:]]+$` or `\s+$` — those include `\n`, collapsing entire file into one line.

For each approved group:
1. Capture line counts baseline: `git diff --cached --name-only | while IFS= read -r f; do [ -f "$f" ] || continue; printf '%s\t%d\n' "$f" "$(wc -l < "$f")" >> .git/.commit-baselines; done`
2. For every `.py` file: `ruff check --fix <file> && ruff format <file> && git add <file>`
3. Trailing whitespace: **use `sed` for portability:**
   ```bash
   git diff --cached --name-only | while IFS= read -r f; do sed -i '' 's/[ \t]*$//' "$f"; git add "$f"; done
   ```
4. Detect corruption by comparing post-lint line counts against baseline. If drastically shrunk, restore and halt.

⚠️ **CRITICAL:** Never use Write or Edit on staged source files. All fixes via Bash only. If a fix cannot be made via Bash, record as OOXML_FAILURE and stop.

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

- [ ] **Step 3: Verify changes**

Run:
```bash
sed -n '31,60p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-preflight.md
```

Expected: Regex caution visible before code blocks; `sed` visible instead of `perl`; CRITICAL note visible.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-commit-preflight.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(agents): clarify operational issues in al-dev-commit-preflight

Three clarity fixes:

1. Move regex safety constraint to BEFORE the code block that uses it
   (was appearing after, causing confusion)

2. Replace perl with sed for trailing-whitespace fixing
   (perl not declared as dependency; sed is portable)

3. Restructure Step 1 to clarify that all fixes must use Bash only
   (no Write/Edit on staged source files)

Code logic unchanged; clarity improved.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 1 file changed, several lines modified.

---

### Task 7: Fix Operational Clarity Gaps in al-dev-solution-architect

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-solution-architect.md`

**Rationale:** Three operational issues: (1) `$AL_DEV_SHARED_PLUGIN_ROOT` undefined at agent runtime, (2) SIMPLE-tier gate has no active verification, (3) "Pattern reference" term used without definition.

- [ ] **Step 1: Read the current Workflow section**

Run:
```bash
sed -n '38,100p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md
```

Expected: Current Workflow and complexity classification.

- [ ] **Step 2: Check for bash blocks with undefined variable**

Run:
```bash
grep -n "AL_DEV_SHARED_PLUGIN_ROOT" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md
```

If found, replace with dynamic lookup. If not found, this issue is already resolved.

- [ ] **Step 3: Add SIMPLE-tier gate logic and Pattern reference definition**

Find the Workflow section (around line 38). Add these sections before the "Workflow" header:

```markdown
## Complexity Classification

**SIMPLE features:**
Before skipping research, confirm complexity is actually SIMPLE:
- Verify: Requirement fits in ≤2 files (data model + one helper/codeunit, or UI layer only)
- Verify: No external API/integration complexity (no event subscribers, no extensions to base objects)
- If both confirmed SIMPLE, skip research; proceed to design with project context only.
- If borderline, default to MEDIUM and run research phase.

## Pattern Reference Definition

A "Pattern reference" is a file path + line number pointing to an existing AL code example in the current project that the developer should inspect first when implementing a similar feature. It is the closest structural or behavioral analogue already in the codebase, not an exact template — the developer uses it as a starting point for understanding project conventions, not as copy-paste code.

Example: "Pattern reference: Modules\Cust\Src\CustPostingGr.Codeunit.al:245-280 — similar table extension with trigger logic"
```

- [ ] **Step 4: Verify changes**

Run:
```bash
grep -A5 "Pattern reference" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-solution-architect.md | head -10
```

Expected: Definition visible and clear.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-solution-architect.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
fix(agents): clarify operational gaps in al-dev-solution-architect

Three clarity fixes:

1. Add active SIMPLE-tier gate with verification steps
   (was: vague statement; now: explicit checklist before skipping research)

2. Add formal definition of 'Pattern reference' term
   (was: used without explanation; now: defined as "existing code analogue
   in project for starting point, not copy-paste template")

3. Remove undefined $AL_DEV_SHARED_PLUGIN_ROOT references if any
   (not found in current file; this was prophylactic)

Code logic unchanged; operational clarity improved.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 1 file changed, multiple line additions.

---

### Task 8: Add al-dev-commit-preflight to Agent Map Catalog

**Files:**
- Modify: `docs/al-dev-agent-map.md` (Layer 1 catalog table, around line 8)

**Rationale:** Agent file exists and is dispatched at `/al-dev-commit` Step 9.5; must be added to the agent map catalog table.

- [ ] **Step 1: Read current catalog table**

Run:
```bash
sed -n '7,28p' /Users/russelllaing/al-dev-shared/docs/al-dev-agent-map.md
```

Expected: 19-row catalog table (lines 7-27, with header on lines 7-8).

- [ ] **Step 2: Find insertion point (alphabetical order)**

Agent should go between `al-dev-commit-agent-execute` and `al-dev-commit-message-drafter`.

Check line 11 (currently commit-agent-execute) and line 12 (currently commit-message-drafter).

- [ ] **Step 3: Verify agent details from source file**

Run:
```bash
head -15 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-preflight.md
```

Expected: Description, model, and tools frontmatter.

Extract:
- **Model:** claude-haiku-4-5-20251001 (after Task 4 normalization)
- **Tools:** Bash, Read (from frontmatter)
- **Spawned by:** /al-dev-commit (Step 9.5)

- [ ] **Step 4: Insert row into catalog table**

Edit `docs/al-dev-agent-map.md`, insert between lines 11 and 12.

New row:
```markdown
| al-dev-commit-preflight | claude-haiku-4-5-20251001 | Bash, Read | /al-dev-commit (preflight phase: Step 9.5) |
```

- [ ] **Step 5: Update header count (if table grew)**

Check line 3. If it currently says "19 agents", change to "20 agents".

Run:
```bash
sed -n '3p' /Users/russelllaing/al-dev-shared/docs/al-dev-agent-map.md
```

Expected: Header mentioning agent count. Update if needed.

- [ ] **Step 6: Verify insertion**

Run:
```bash
sed -n '7,30p' /Users/russelllaing/al-dev-shared/docs/al-dev-agent-map.md
```

Expected: al-dev-commit-preflight row visible in alphabetical position; table properly formatted.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-agent-map.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
docs(maps): add al-dev-commit-preflight to agent map catalog

Agent al-dev-commit-preflight exists in profile-al-dev-shared/agents/
and is dispatched at /al-dev-commit Step 9.5 but was missing from the
agent map catalog table.

Added row with model, tools, and spawner reference.
Updated agent count from 19 to 20.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 1 file changed, 1-2 lines added.

---

### Task 9: Add al-dev-diagram-generator to Plugin Map

**Files:**
- Modify: `docs/al-dev-plugin-map.md` (Layer 2 skill sections)

**Rationale:** Skill file `al-dev-diagram-generator/SKILL.md` exists but is not documented in the plugin map.

- [ ] **Step 1: Read the skill file to extract details**

Run:
```bash
head -20 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-diagram-generator/SKILL.md
```

Expected: Frontmatter with description, arguments, etc.

- [ ] **Step 2: Find where to insert in plugin map**

Run:
```bash
grep -n "^### /al-dev-" /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md | head -15
```

Expected: Existing skill sections. Diagram-generator should go in alphabetical order among utility skills.

- [ ] **Step 3: Read the skill's full structure**

Run:
```bash
cat /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-diagram-generator/SKILL.md
```

Expected: Full SKILL.md content. Extract:
- Purpose/description
- Arguments
- Outputs
- Key phases/steps (brief summary)

- [ ] **Step 4: Create plugin map section for diagram-generator**

Based on the skill file, add a new section in `docs/al-dev-plugin-map.md` under Layer 2 (Per-Skill Drill-Downs).

Template (adapt to actual skill content):

```markdown
### /al-dev-diagram-generator

**Purpose:** Generate relationship diagrams for the al-dev plugin (skill/agent dependencies, knowledge cross-references).

**Inputs:**
- Surface: which surface to diagram (plugin skills, agents, both)
- Output format: mermaid (default) or graphviz

**Outputs:**
- `.dev/YYYY-MM-DD-al-dev-plugin-diagram.md` — mermaid diagram of skill/agent/knowledge relationships

**Phases:**
1. Parse skill/agent/knowledge file structures
2. Build dependency graph
3. Render as mermaid flowchart

**Notes:** Maintainer tool for plugin architecture visualization. Not part of main development workflow.
```

- [ ] **Step 5: Update plugin map header**

Change line 5 header from "19 distributed skills" to "20 distributed skills" (or appropriate count).

- [ ] **Step 6: Verify insertion**

Run:
```bash
grep -n "^### /al-dev-diagram-generator" /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md
```

Expected: Section exists with proper heading.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-plugin-map.md

git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
docs(maps): add al-dev-diagram-generator to plugin map

Skill al-dev-diagram-generator exists in profile-al-dev-shared/skills/
but was missing from the plugin map documentation.

Added section in Layer 2 with purpose, inputs, outputs, and phases.
Updated skill count from 19 to 20.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
```

Expected: Commit succeeds; 1 file changed, several lines added.

---

## Verification Checklist

Before claiming completion, run:

```bash
# 1. Verify all commits were created
git -C /Users/russelllaing/al-dev-shared log --oneline -n 9 | head -10

# 2. Verify no non-canonical tool names remain
grep -r "USER_GATE\|MCP:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/ && echo "FAIL" || echo "PASS: No non-canonical tool names"

# 3. Verify all agent model IDs are canonical
grep "^model:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/*.md | grep -v "claude-" && echo "FAIL" || echo "PASS: All models canonical"

# 4. Verify no spurious name: fields
grep "^name:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/*.md && echo "FAIL" || echo "PASS: No spurious name fields"

# 5. Verify knowledge file exists
ls -la /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/review-panel-invocation-pattern.md && echo "PASS: Knowledge file created"

# 6. Verify agent map has commit-preflight
grep "al-dev-commit-preflight" /Users/russelllaing/al-dev-shared/docs/al-dev-agent-map.md | head -1

# 7. Verify plugin map has diagram-generator
grep "al-dev-diagram-generator" /Users/russelllaing/al-dev-shared/docs/al-dev-plugin-map.md | head -1
```

---

## Summary

This plan executes the top 5 harness-agnostic plugin health fixes in 9 atomic commits:

1. **Knowledge extraction** — review-panel dispatch template
2. **Skill de-inlining** — review-develop references knowledge
3. **Agent cleanup** — remove spurious frontmatter fields
4. **Agent model normalization** — canonical IDs across 16 agents
5. **Agent tool normalization** — canonical tool names across 4 agents
6. **Clarity fix (commit-preflight)** — operational issues resolved
7. **Clarity fix (solution-architect)** — undefined references resolved
8. **Map update (agents)** — add missing agent catalog entry
9. **Map update (skills)** — add missing skill documentation

All changes maintain harness-agnostic vocabulary and follow atomic commit conventions.
