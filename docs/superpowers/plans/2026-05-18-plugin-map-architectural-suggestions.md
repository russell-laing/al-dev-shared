# Plugin Map Architectural Suggestions — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the five architectural suggestions from the Observations section of `docs/al-dev-plugin-map.md` — a review-panel pattern doc, an explore-subagent pattern doc, moving al-dev-align out of the distributed plugin, updating the Layer 1 diagram, and merging al-dev-autonomous into al-dev-develop.

**Architecture:** Each task is a self-contained edit. Tasks 1–4 are purely additive (new knowledge docs, diagram additions, skill references). Task 5 is the only structural change (merge + archive). Do Tasks 1–4 first so the knowledge docs exist before autonomous is retired.

**Tech Stack:** Markdown files (SKILL.md, knowledge docs, plugin map diagram). No code compilation required. Verification is text-based (grep + wc -l).

---

## File Map

| Task | Files Created | Files Modified |
|------|--------------|----------------|
| 1 | `knowledge/explore-subagent-pattern.md` | `skills/al-dev-explore/SKILL.md`, `skills/al-dev-perf/SKILL.md`, `skills/al-dev-investigate/SKILL.md` |
| 2 | `knowledge/review-panel-pattern.md` | `skills/al-dev-develop/SKILL.md`, `skills/al-dev-autonomous/SKILL.md` |
| 3 | `.claude/skills/al-dev-align/SKILL.md` | `docs/al-dev-plugin-map.md` (scope line) |
| 4 | — | `docs/al-dev-plugin-map.md` (Layer 1 diagram) |
| 5 | `archived/skills/al-dev-autonomous/SKILL.md` | `skills/al-dev-develop/SKILL.md`, `docs/al-dev-plugin-map.md` |

All paths are relative to `/Users/russelllaing/al-dev-shared/profile-al-dev-shared/` unless otherwise specified.

---

## Task 1: Create explore-subagent-pattern.md and update three callers

**Files:**
- Create: `profile-al-dev-shared/knowledge/explore-subagent-pattern.md`
- Modify: `profile-al-dev-shared/skills/al-dev-explore/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-perf/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`

**Context:** Three skills independently define their Explore subagent spawn invocation. The structural pattern (context loading, agent spawn format, output convention) is shared; only the domain-specific prompt differs per skill. This task extracts the structural mechanics into a single reference doc.

- [ ] **Step 1: Read the three caller skills to confirm the shared structure**

  ```bash
  grep -n "Spawn\|explore agent\|subagent_type\|Explore" \
    profile-al-dev-shared/skills/al-dev-explore/SKILL.md \
    profile-al-dev-shared/skills/al-dev-perf/SKILL.md \
    profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
  ```

  Expected: each skill shows a "Spawn an explore agent:" block with context load → spawn → write output → present pattern.

- [ ] **Step 2: Write `knowledge/explore-subagent-pattern.md`**

  ```markdown
  # Explore Subagent Pattern

  Skills that delegate codebase investigation to a focused read-only
  agent follow this three-step structure. The domain-specific prompt
  content (what to look for, what to report) stays local to each
  skill; only the structural mechanics are documented here.

  ## When to Use an Explore Subagent

  Use an Explore subagent when:
  - The investigation covers multiple files or directories
  - Results must be written to `.dev/` for persistence
  - The question is bounded (one analytical lens)

  Do NOT use an Explore subagent for:
  - Simple single-file reads (use Read directly)
  - Tasks that require editing (Explore agents are read-only)

  ## Step A — Load Context

  Before spawning, check for and read:

  1. `.dev/project-context.md` (if it exists) — key objects,
     architectural patterns, directory layout
  2. Latest ticket context (glob):
     `$(ls .dev/*-al-dev-ticket-ticket-context.md 2>/dev/null | sort | tail -1)`
  3. Latest explore findings (glob):
     `$(ls .dev/*-al-dev-explore-findings.md 2>/dev/null | sort | tail -1)`

  Pass relevant excerpts (not the full files) into the agent prompt
  to narrow scope and avoid redundant discovery.

  ## Step B — Spawn Invocation Format

  The canonical Agent tool invocation for an Explore subagent:

  ```text
  Spawn an explore agent:
    purpose: [Domain] scan: [scope description]
    prompt: [domain-specific investigation prompt — defined locally
             in each skill, not here]
    output: structured findings with file paths and line numbers
  ```

  Agent type: `Explore` (the fast read-only search agent).

  Spawn count guidance:
  - ×1 for a single analytical lens (explore, perf, single-topic investigate)
  - ×2 in parallel for hypothesis testing (investigate splits hypotheses
    evenly across two agents)

  ## Step C — Output File Convention

  Write findings to `.dev/` immediately after the agent returns.
  Do NOT accumulate results in memory and write at the end of the skill.

  Naming: `$(date +%Y-%m-%d)-<skill-name>-<artifact-name>.md`

  Examples:
  - `2026-05-18-al-dev-explore-findings.md`
  - `2026-05-18-al-dev-perf-perf-analysis.md`
  - `2026-05-18-al-dev-explore-findings.md` (investigate also uses this name)

  Files are date-prefixed to preserve history. Do not overwrite previous runs.

  ## Step D — Present to User

  After writing the file, show a short inline summary and reference the file:

  ```text
  [Domain] analysis complete → .dev/[filename].md

  [2–5 sentence summary of findings]

  [Suggest next command if findings warrant one]
  ```
  ```

- [ ] **Step 3: Verify the file was written**

  ```bash
  wc -l profile-al-dev-shared/knowledge/explore-subagent-pattern.md
  ```

  Expected: 70+ lines. If fewer, re-check Step 2.

- [ ] **Step 4: Add a reference line to al-dev-explore SKILL.md**

  In `profile-al-dev-shared/skills/al-dev-explore/SKILL.md`, find the `### Step 2 — Spawn Explore Subagent` heading. Add this line immediately after the heading:

  ```
  > Pattern: `knowledge/explore-subagent-pattern.md` — Steps A–D.
  > Domain-specific prompt content is below.
  ```

  Verify:
  ```bash
  grep -n "explore-subagent-pattern" profile-al-dev-shared/skills/al-dev-explore/SKILL.md
  ```
  Expected: 1 match.

- [ ] **Step 5: Add a reference line to al-dev-perf SKILL.md**

  In `profile-al-dev-shared/skills/al-dev-perf/SKILL.md`, find `### Step 2 — Spawn Performance Analysis Agent`. Add immediately after the heading:

  ```
  > Pattern: `knowledge/explore-subagent-pattern.md` — Steps A–D.
  > Performance-specific prompt content is below.
  ```

  Verify:
  ```bash
  grep -n "explore-subagent-pattern" profile-al-dev-shared/skills/al-dev-perf/SKILL.md
  ```
  Expected: 1 match.

- [ ] **Step 6: Add a reference line to al-dev-investigate SKILL.md**

  In `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`, find `### Step 3 — Spawn Parallel Investigation Agents`. Add immediately after the heading:

  ```
  > Pattern: `knowledge/explore-subagent-pattern.md` — Steps A–D.
  > Hypothesis-testing prompt structure is below; spawn ×2 in parallel.
  ```

  Verify:
  ```bash
  grep -n "explore-subagent-pattern" profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
  ```
  Expected: 1 match.

- [ ] **Step 7: Verify no content was accidentally removed from any skill**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-explore/SKILL.md \
         profile-al-dev-shared/skills/al-dev-perf/SKILL.md \
         profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
  ```

  Expected: each file count is 2–3 lines MORE than before (the reference lines added). If any count dropped, read the file and check for accidental deletion.

- [ ] **Step 8: Scan for forbidden placeholder patterns in changed files**

  ```bash
  grep -rn '\[date\]\|YYYY-MM-DD\|TODO\|TBD\|Co-Authored-By\|claude:\|copilot:' \
    profile-al-dev-shared/knowledge/explore-subagent-pattern.md \
    profile-al-dev-shared/skills/al-dev-explore/SKILL.md \
    profile-al-dev-shared/skills/al-dev-perf/SKILL.md \
    profile-al-dev-shared/skills/al-dev-investigate/SKILL.md \
    --color=never || true
  ```

  Expected: no output. If any pattern is found, fix before committing.

- [ ] **Step 9: Commit**

  ```bash
  git add \
    profile-al-dev-shared/knowledge/explore-subagent-pattern.md \
    profile-al-dev-shared/skills/al-dev-explore/SKILL.md \
    profile-al-dev-shared/skills/al-dev-perf/SKILL.md \
    profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
  git commit -m "$(cat <<'EOF'
  docs(knowledge): add explore-subagent-pattern.md and reference from three callers

  Extracts the structural mechanics of the Explore subagent spawn pattern
  (context loading, invocation format, output convention) into a shared
  knowledge doc. al-dev-explore, al-dev-perf, and al-dev-investigate each
  add a reference pointer; domain-specific prompt content remains local.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

## Task 2: Create review-panel-pattern.md and update two callers

**Files:**
- Create: `profile-al-dev-shared/knowledge/review-panel-pattern.md`
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md`

**Context:** The identical three-reviewer panel (security + expert + performance in parallel) is defined independently in Phase 5 of both skills. Extracting it to a knowledge doc means adding a 4th reviewer only requires one edit. The reviewer type names and brief role descriptions are the shared content.

- [ ] **Step 1: Read the reviewer definitions in both skills to capture exact text**

  ```bash
  grep -n -A 4 "al-dev-security-reviewer\|al-dev-expert-reviewer\|al-dev-performance-reviewer" \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md | head -40
  grep -n -A 4 "al-dev-security-reviewer\|al-dev-expert-reviewer\|al-dev-performance-reviewer" \
    profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md | head -40
  ```

  Expected: near-identical reviewer descriptions in both files.

- [ ] **Step 2: Write `knowledge/review-panel-pattern.md`**

  ```markdown
  # Review Panel Pattern

  The three-reviewer panel is the standard parallel review composition
  used by /al-dev-develop and /al-dev-autonomous. Spawn all three
  reviewers in a single batch (one message, three Agent tool calls).

  ## Composition

  **al-dev-security-reviewer:**
  Review all implemented code for permission issues, data exposure
  risks, authentication gaps.

  **al-dev-expert-reviewer:**
  Review for AL naming conventions, BC best practices
  (SetLoadFields, FieldCaption), code organization, event patterns.

  **al-dev-performance-reviewer:**
  Review for query efficiency, N+1 patterns, SetLoadFields usage,
  loop efficiency, record variable scoping.

  Each reviewer reads ALL implemented AL files.

  ## Spawn Instructions

  Spawn all three as a single batch:
  - Agent type: `al-dev-security-reviewer`, `al-dev-expert-reviewer`,
    `al-dev-performance-reviewer`
  - Prompt each reviewer with: paths to ALL implemented AL files
  - Pattern: ×3 parallel (one message, three Agent calls)

  ## Synthesis (after all three complete)

  1. Read all three review outputs.
  2. Cross-reference overlapping findings — issues raised by multiple
     reviewers are higher priority than single-reviewer findings.
  3. Where reviewers contradict each other (e.g. AL Expert recommends
     a pattern that Performance flags as slow), apply judgement to
     resolve using the severity categories in the calling skill.
  4. Consolidate into a single categorised list before assigning fixes.

  ## Adding a Fourth Reviewer

  Add the new reviewer type here with its role description, then update
  the spawn batch in each calling skill's review phase.
  ```

- [ ] **Step 3: Verify the file was written**

  ```bash
  wc -l profile-al-dev-shared/knowledge/review-panel-pattern.md
  ```

  Expected: 40+ lines.

- [ ] **Step 4: Add a reference line to al-dev-develop SKILL.md**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find `## Phase 5: Spawn Review Team`. Add immediately after the heading:

  ```
  > Canonical panel: `knowledge/review-panel-pattern.md`.
  > Role descriptions and synthesis steps are in that doc.
  ```

  Verify:
  ```bash
  grep -n "review-panel-pattern" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```
  Expected: 1 match.

- [ ] **Step 5: Add a reference line to al-dev-autonomous SKILL.md**

  In `profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md`, find `## Phase 5: Spawn Review Team`. Add immediately after the heading:

  ```
  > Canonical panel: `knowledge/review-panel-pattern.md`.
  > Role descriptions and synthesis steps are in that doc.
  ```

  Verify:
  ```bash
  grep -n "review-panel-pattern" profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
  ```
  Expected: 1 match.

- [ ] **Step 6: Verify no content was accidentally removed**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
         profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
  ```

  Expected: each count is 2 lines MORE than before the edit.

- [ ] **Step 7: Scan for forbidden placeholder patterns**

  ```bash
  grep -rn '\[date\]\|YYYY-MM-DD\|TODO\|TBD\|Co-Authored-By\|claude:\|copilot:' \
    profile-al-dev-shared/knowledge/review-panel-pattern.md \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
    profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md \
    --color=never || true
  ```

  Expected: no output.

- [ ] **Step 8: Commit**

  ```bash
  git add \
    profile-al-dev-shared/knowledge/review-panel-pattern.md \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
    profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
  git commit -m "$(cat <<'EOF'
  docs(knowledge): add review-panel-pattern.md and reference from develop and autonomous

  Extracts the canonical three-reviewer panel composition (security,
  expert, performance) and synthesis instructions into a shared
  knowledge doc. Both al-dev-develop and al-dev-autonomous now
  reference it instead of duplicating the reviewer definitions.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

## Task 3: Move /al-dev-align to .claude/skills/

**Files:**
- Create: `.claude/skills/al-dev-align/SKILL.md` (at repo root `.claude/`, NOT inside `profile-al-dev-shared/`)
- Delete: `profile-al-dev-shared/skills/al-dev-align/SKILL.md`
- Keep in place: `profile-al-dev-shared/skills/al-dev-align/check-alignment.py` and `tests/`
- Modify: `docs/al-dev-plugin-map.md` (scope note)

**Context:** The al-dev-align skill audits the plugin's own consistency with harness repos — it has no value to AL developers using the distributed plugin. The `review-plugin-map` and `analyze-plugin-design` maintenance skills already live in `.claude/skills/`. The Python script MUST stay in `profile-al-dev-shared/skills/al-dev-align/` because its fallback path computation (`Path(__file__).resolve().parent.parent.parent`) depends on being 3 levels inside the plugin. The SKILL.md's existing path reference (`$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-align/check-alignment.py`) works unchanged from the new location.

- [ ] **Step 1: Read current SKILL.md content to use verbatim in new location**

  ```bash
  cat profile-al-dev-shared/skills/al-dev-align/SKILL.md
  ```

  Note the exact content — you will write this verbatim to the new path in Step 2.

- [ ] **Step 2: Create `.claude/skills/al-dev-align/SKILL.md`**

  Write the exact content read in Step 1 to:
  `/Users/russelllaing/al-dev-shared/.claude/skills/al-dev-align/SKILL.md`

  No content changes — identical copy.

- [ ] **Step 3: Verify the new file matches the old file**

  ```bash
  diff \
    profile-al-dev-shared/skills/al-dev-align/SKILL.md \
    .claude/skills/al-dev-align/SKILL.md
  ```

  Expected: no output (files are identical).

- [ ] **Step 4: Verify the Python script path reference still resolves**

  ```bash
  grep -n "AL_DEV_SHARED_PLUGIN_ROOT\|check-alignment" \
    .claude/skills/al-dev-align/SKILL.md
  ```

  Expected: reference uses `$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-align/check-alignment.py`.
  The script at that path still exists:
  ```bash
  ls profile-al-dev-shared/skills/al-dev-align/check-alignment.py
  ```
  Expected: file present.

- [ ] **Step 5: Delete the old SKILL.md from the plugin**

  ```bash
  git rm profile-al-dev-shared/skills/al-dev-align/SKILL.md
  ```

  Expected: `rm 'profile-al-dev-shared/skills/al-dev-align/SKILL.md'`

- [ ] **Step 6: Update the plugin map scope line**

  In `docs/al-dev-plugin-map.md`, find:
  ```
  **Scope:** Active skills only. Archived items (al-dev-test, test-engineer agents, al-dev-test-coverage-reviewer) excluded.
  ```

  Replace with:
  ```
  **Scope:** Active skills only. Archived items (al-dev-test, test-engineer agents, al-dev-test-coverage-reviewer) excluded. /al-dev-align moved to `.claude/skills/` (project-local maintenance tool, not distributed).
  ```

  Verify:
  ```bash
  grep -n "al-dev-align" docs/al-dev-plugin-map.md
  ```
  Expected: the updated scope line.

- [ ] **Step 7: Update the Last Updated line in plugin map**

  Find the `**Last updated:**` line and update the date to `2026-05-18` and the note to:
  ```
  **Last updated:** 2026-05-18 (al-dev-align moved to .claude/skills/; explore and review-panel patterns added)
  ```

- [ ] **Step 8: Scan for forbidden patterns in changed files**

  ```bash
  grep -rn '\[date\]\|YYYY-MM-DD\|TODO\|TBD\|Co-Authored-By\|claude:\|copilot:' \
    .claude/skills/al-dev-align/SKILL.md \
    docs/al-dev-plugin-map.md \
    --color=never || true
  ```

  Expected: no output.

- [ ] **Step 9: Commit**

  ```bash
  git add \
    .claude/skills/al-dev-align/SKILL.md \
    docs/al-dev-plugin-map.md
  git commit -m "$(cat <<'EOF'
  refactor(align): move al-dev-align skill to .claude/skills/ (project-local only)

  al-dev-align audits plugin internal consistency for harness repos — it
  has no value to AL developers consuming the distributed plugin. Moving
  to .claude/skills/ alongside review-plugin-map and analyze-plugin-design.
  The Python check-alignment.py script stays in the plugin for path resolution.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

## Task 4: Extend Layer 1 diagram with explore, interview, and release-notes

**Files:**
- Modify: `docs/al-dev-plugin-map.md` (Layer 1 Mermaid diagram only)

**Context:** Three skills are missing from the lifecycle overview. /al-dev-explore and /al-dev-interview are pre-planning tributaries (optional inputs, not on the main spine). /al-dev-release-notes is a post-commit output. Use dashed arrows (`-.->`) for optional/tributary paths to visually distinguish them from the mandatory development spine.

- [ ] **Step 1: Read the current Layer 1 diagram**

  ```bash
  sed -n '/## Layer 1/,/^---$/p' docs/al-dev-plugin-map.md
  ```

  Confirm the current diagram boundaries and node names before editing.

- [ ] **Step 2: Replace the Layer 1 Mermaid diagram**

  Find the entire code fence from ` ```mermaid ` to the matching ` ``` ` in the Layer 1 section and replace with:

  ````markdown
  ```mermaid
  flowchart TD
      %% Pre-planning tributaries (optional)
      Explore("al-dev-explore") -.->|explore-findings.md| Investigate
      Explore -.->|explore-findings.md| Plan
      Interview("al-dev-interview") -.->|interview-requirements.md| Plan

      %% Entry points
      Ticket("al-dev-ticket") -->|ticket-context.md| Support("al-dev-support")
      Investigate("al-dev-investigate")
      FixDirect("al-dev-fix") -->|AL code| Commit("al-dev-commit")

      %% Investigation path branches
      Investigate -->|explore-findings.md| Decision1{Needs<br/>full plan?}
      Decision1 -->|Yes| Plan("al-dev-plan")
      Decision1 -->|No| FixDirect

      %% Main development spine
      Plan -->|solution-plan.md| Develop("al-dev-develop")
      Plan -->|solution-plan.md| Autonomous("al-dev-autonomous")
      Develop -->|code-review.md| Commit
      Autonomous -->|code-review.md| Commit

      %% Complexity gate within plan
      Note["Trivial requests<br/>route to /fix"] -.-> Plan

      %% Outputs
      Commit --> Git(["✓ git commit"])
      Git -.-> ReleaseNotes("al-dev-release-notes")
      ReleaseNotes --> Notes(["✓ release notes"])
      Support --> Reply(["✓ customer reply"])

      style Ticket fill:#e1f5ff
      style Support fill:#e1f5ff
      style Investigate fill:#f3e5f5
      style Explore fill:#f3e5f5
      style Interview fill:#e8f5e9
      style Plan fill:#fff3e0
      style Develop fill:#fff3e0
      style Autonomous fill:#fff3e0
      style FixDirect fill:#e8f5e9
      style Commit fill:#e8f5e9
      style Git fill:#c8e6c9
      style Notes fill:#c8e6c9
      style Reply fill:#c8e6c9
      style ReleaseNotes fill:#e3f2fd
  ```
  ````

- [ ] **Step 3: Verify the diagram syntax is valid**

  Count the style lines to ensure none were dropped:
  ```bash
  grep -c "style " docs/al-dev-plugin-map.md
  ```
  Expected: at least 13 (original 9 + 4 new nodes).

  Verify all new nodes appear:
  ```bash
  grep -n "Explore\|Interview\|ReleaseNotes\|Notes" docs/al-dev-plugin-map.md | head -20
  ```
  Expected: all four node names present in the Layer 1 section.

- [ ] **Step 4: Verify the file line count increased (no content lost)**

  ```bash
  wc -l docs/al-dev-plugin-map.md
  ```

  Expected: approximately 10–15 lines MORE than before (new nodes + style lines added).

- [ ] **Step 5: Scan for forbidden patterns**

  ```bash
  grep -n '\[date\]\|TODO\|TBD\|Co-Authored-By\|claude:\|copilot:' \
    docs/al-dev-plugin-map.md || true
  ```

  Expected: no output. (`YYYY-MM-DD` is intentional in the **Last updated** line — skip that match.)

- [ ] **Step 6: Commit**

  ```bash
  git add docs/al-dev-plugin-map.md
  git commit -m "$(cat <<'EOF'
  docs(plugin-map): add explore, interview, and release-notes to Layer 1 diagram

  Adds three missing skills to the lifecycle overview: al-dev-explore and
  al-dev-interview as dashed-line pre-planning tributaries, and
  al-dev-release-notes as a post-commit output. Main spine is unchanged.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

## Task 5: Merge /al-dev-autonomous into /al-dev-develop and archive autonomous

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` (add `--autonomous` arg handling + autonomous phases)
- Create: `profile-al-dev-shared/archived/skills/al-dev-autonomous/SKILL.md`
- Delete: `profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md` (via `git rm`)
- Modify: `docs/al-dev-plugin-map.md` (remove Autonomous node from Layer 1 + remove autonomous drill-down)

**Context:** /al-dev-autonomous is structurally /al-dev-develop plus three additions: Phase 1A (signature verification), Phase 4A (static validation), and a 5-attempt self-healing compile loop in place of the single compile pass. The suggestion proposes `--verify-signatures` as the flag but the full feature set warrants `--autonomous`. The validator script at `$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-autonomous/validate-code-review.py` stays in place (referenced from the archived skill).

This is the largest task. Read all files carefully before editing.

- [ ] **Step 1: Read both skill files in full before making any changes**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
         profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md
  ```

  Note the line counts as your baseline. Read both files fully.

- [ ] **Step 2: Add argument detection block to al-dev-develop Phase 1**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find `## Phase 1: Read Context` and add this block immediately after the heading (before the existing numbered list):

  ```markdown
  **Autonomous mode detection:**
  Check `$ARGUMENTS` for `--autonomous`. If present:
  - After Step 3 below, run Phase 1A (Signature Verification) before
    proceeding to Phase 2
  - After Phase 4 (Verify on Completion), run Phase 4A (Static Validation)
    before spawning the review team
  - In Phase 8, use the 5-attempt compile-verify loop instead of the
    single compile pass
  - In Phase 9, use the extended code review template (includes autonomous
    verification results section)

  ```

- [ ] **Step 3: Insert Phase 1A after Phase 1 content**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find `## Phase 2: Partition Work` and insert the following Phase 1A block immediately before it:

  ```markdown
  ## Phase 1A: Signature Verification (--autonomous only)

  Skip this phase if `--autonomous` is not in `$ARGUMENTS`.

  Before dispatching any developer, verify every external procedure
  signature via the AL symbols MCP.

  For each external procedure identified in Phase 1, run the
  appropriate MCP query:

  ```text
  al_get_object_definition — for base objects being extended:
    confirms field names, IDs, and trigger signatures

  al_search_object_members — for event signatures and methods:
    locates exact event publisher signatures with var parameters

  al_find_references — to detect existing similar extensions:
    avoids duplicate subscriber registration
  ```

  Verify for each procedure:

  - Exact procedure name (case-sensitive)
  - Parameter list: names, types, var vs value modifier
  - Return type if applicable

  Write verified signatures to:
  `.dev/$(date +%Y-%m-%d)-al-dev-autonomous-signatures.md`

  Use this format:

  ```markdown
  ## Verified Signatures

  ### [ObjectType] [ObjectName].[ProcedureName]
  - Parameters: [ParamName: Type; var ParamName: Type]
  - Return: [Type or void]
  - Source: al_search_object_members / al_get_object_definition
  - Verified: [ISO timestamp]

  ### NOT VERIFIED: [ProcedureName]
  - Reason: [not found in MCP / ambiguous match]
  - Risk: Developer must not guess this signature
  ```

  If any procedure is NOT VERIFIED, include this block in the
  developer spawn prompt:

  ```text
  ⚠️ Unverified signatures — do NOT guess these:
  - [ProcedureName]: [reason not verified]
  STOP and report back if you need to call this procedure.
  ```

  ```

- [ ] **Step 4: Insert Phase 4A before Phase 5**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find `## Phase 5: Spawn Review Team` and insert immediately before it:

  ```markdown
  ## Phase 4A: Static Validation (--autonomous only)

  Skip this phase if `--autonomous` is not in `$ARGUMENTS`.

  Run these checks on all newly created AL files before the
  review team is spawned. Fix CRITICAL issues by dispatching
  a developer before proceeding.

  ### Check 1: Object Name Length

  ```bash
  grep -rn -E \
    '^(table|page|codeunit|report|enum|interface|xmlport|query|permissionset)\s+[0-9]+\s+' \
    --include="*.al" .
  ```

  For each match, the object name is everything after the numeric
  ID. Count its characters. Flag any name exceeding 30 characters
  as a CRITICAL issue.

  ### Check 2: Compile Guard Logic

  ```bash
  grep -rn '#if\|#else\|#endif' --include="*.al" .
  ```

  For each `#if` directive, read the surrounding block. Verify:

  - The condition matches the intended feature flag
  - Every `#if` has a matching `#endif`
  - The `#else` branch, if present, contains the correct fallback

  Flag any inverted condition or unmatched directive as CRITICAL.

  ### Check 3: Label and Message Consistency

  ```bash
  grep -rn "label\|Error(\|Message(\|FieldCaption" \
    --include="*.al" . | head -50
  ```

  Cross-reference against the solution plan's feature descriptions.
  Flag any label using different terminology than the plan as a HIGH issue.

  ### Static Validation Report

  Write to:
  `.dev/$(date +%Y-%m-%d)-al-dev-autonomous-static-validation.md`

  ```markdown
  ## Static Validation Results

  ### Object Name Lengths
  | Object | Name | Length | Status |
  | --- | --- | --- | --- |
  | table 50100 | ABCSomeName | 11 | ✅ |

  ### Compile Guards
  | File | Line | Directive | Status |
  | --- | --- | --- | --- |

  ### Label Consistency
  | File:Line | Label Text | Plan Term | Status |
  | --- | --- | --- | --- |

  ### Summary
  CRITICAL issues: N (must fix before review)
  HIGH issues: N (flagged in code review)
  ```

  If CRITICAL issues found: dispatch a developer with the specific
  violations. Wait for fixes. Re-run the relevant check before
  spawning the review team.

  ```

- [ ] **Step 5: Replace Phase 8 with conditional compile logic**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find `## Phase 8: Compile + Lint Pass` and replace the phase content with:

  ```markdown
  ## Phase 8: Compile + Lint Pass

  **Standard mode** (no `--autonomous`): Follow
  `knowledge/compile-lint-procedure.md` in full.

  Write lint report to:
  `.dev/$(date +%Y-%m-%d)-al-dev-lint-lint-report.md`

  Additional rules for this skill:

  - If compilation errors remain after the developer fix pass,
    reassign to the responsible developer agent and iterate.
  - If `al-compile` is unavailable, skip the diagnostics-fixer
    step and note "Compilation not verified" in the Phase 10
    review summary.
  - Unresolved lint items from the lint report are surfaced at
    the Phase 10 user approval gate — no new gate here.
  - If the diagnostics-fixer introduces a regression (new
    compile errors), spawn a new `al-dev-developer` agent with
    the regression details, re-run `al-compile`, then
    re-spawn diagnostics-fixer.

  Write `.dev/progress.md` per `knowledge/workflow-resilience.md`.

  ---

  **Autonomous mode** (`--autonomous` in `$ARGUMENTS`):

  Run the compile-verify loop. Track attempt count.

  ### Setup

  Always initialize these at Phase 8 entry:

  ```bash
  mkdir -p .dev
  ATTEMPT=1
  MAX_ATTEMPTS=5
  ```

  ### Compile Step

  ```bash
  if command -v al-compile &>/dev/null; then
    al-compile --output \
      .dev/compile-errors-attempt-${ATTEMPT}.log
  else
    al compile /project:. /packagecachepath:.alpackages \
      /errorlog:.dev/compile-errors-attempt-${ATTEMPT}.log
  fi
  ```

  ### After Each Compile

  **If log is absent, empty, or contains no `Error` lines:**
  Compilation is clean. Record that it took N attempts.
  Proceed to Phase 9.

  **If only `Warning` lines (no `Error` lines):**
  Spawn `al-dev-diagnostics-fixer` once to resolve warnings.
  Do NOT count this as a failed attempt.
  After it completes, read its lint report to confirm clean
  compile, then proceed to Phase 9.

  **If `Error` lines found:**

  Parse the log. Extract per error: file path, line number,
  error code, message text. Group by file.

  Resolve the signatures file path before spawning:

  ```bash
  SIGFILE=$(ls .dev/*-al-dev-autonomous-signatures.md \
    2>/dev/null | sort | tail -1)
  ```

  Spawn **al-dev-developer** with this prompt (substitute actual
  values of `ATTEMPT` and `SIGFILE` — do not paste literal variable names):

  ```text
  Fix compilation errors in the AL project.
  This is attempt [ATTEMPT] of 5.

  Errors from .dev/compile-errors-attempt-[ATTEMPT].log:
  [paste full error list grouped by file]

  Verified signatures (use these exactly — do NOT alter):
  [paste relevant entries from [SIGFILE]]

  Context from solution plan for each erroring file:
  [paste relevant plan excerpt per file]

  Rules:
  - Fix ONLY the listed errors — do not refactor other code
  - If a signature error matches an "unverified" procedure,
    use the AL symbols MCP NOW to get the correct signature
    before fixing
  - Do NOT re-compile after fixing (the orchestrator compiles)
  - Report: [file:line] → [what changed] for each fix
  ```

  Increment: `ATTEMPT=$((ATTEMPT + 1))`

  If `ATTEMPT <= MAX_ATTEMPTS`: return to Compile Step.

  ### After 5 Failed Attempts

  Present to user:

  ```text
  Compilation still failing after 5 attempts.

  Remaining errors (.dev/compile-errors-attempt-5.log):
  [list all remaining errors]

  Summary of fix attempts:
  - Attempt 1: [files changed, what was tried]
  - Attempt 2: [files changed, what was tried]
  ...

  These errors likely require architectural review or a
  change to the solution plan approach.
  ```

  USER_GATE — ask the user with options:

  - Show full error detail for all 5 logs
  - Assign manual fix with more context
  - Revise solution plan approach

  ```

- [ ] **Step 6: Add autonomous template to Phase 9**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find `## Phase 9: Validate and Write Code Review` and add after "Use this structure:" section (after the closing ``` of the code review template, before the validator block):

  ```markdown
  **Autonomous mode addition** (`--autonomous`):
  Append this additional section to the code review:

  ```markdown
  ### Autonomous Verification Results

  #### Signature Verification
  | Procedure | Status | Source |
  | --- | --- | --- |
  | ObjectName.ProcedureName | ✅ Verified | al_search_object_members |
  | ObjectName.OtherProc | ⚠️ Not verified | Not found in MCP |

  Unverified risks: [describe any NOT VERIFIED entries]

  #### Static Validation
  | Check | Result |
  | --- | --- |
  | Object names (≤30 chars) | ✅ All valid / ❌ N fixed |
  | Compile guards (#if logic) | ✅ All correct / ❌ N fixed |
  | Label consistency | ✅ Matches plan / ⚠️ N flagged |

  #### Compile-Verify Loop
  - Attempts required: N of 5
  - Final status: ✅ Clean / ⚠️ N warnings remain
  ```

  In autonomous mode, use the standard develop validator (same as
  non-autonomous mode — the autonomous additions don't require a separate
  validator):
  `$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-develop/validate-code-review.py`

  ```

- [ ] **Step 7: Update Phase 10 approval summary to include autonomous metrics**

  In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, find `## Phase 10: Present to User for Approval` and add after the opening template block:

  ```markdown
  **Autonomous mode:** add this block before "Review findings":

  ```text
  Autonomous verification:
  ✅ N external signatures verified via AL symbols MCP
     [N unverified — see risks in code review]
  ✅ Object names: all ≤30 chars [or: N violations fixed]
  ✅ Compile guards: all correct [or: N inversions fixed]
  ✅ Labels: consistent with plan [or: N discrepancies flagged]
  ✅ Compilation clean (N of 5 attempts)
  ```

  ```

- [ ] **Step 8: Update the al-dev-develop description in the frontmatter**

  Find the `description:` field in `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`:

  ```yaml
  description: >-
    Implement an AL/BC solution using parallel developers
    and 3-specialist review (security, AL expert, performance).
    Use when implementing a planned feature,
    generating AL code, or building from a solution plan.
    Requires a solution plan. Prefer over ad-hoc
    implementation for anything beyond a trivial fix.
  ```

  Replace with:

  ```yaml
  description: >-
    Implement an AL/BC solution using parallel developers
    and 3-specialist review (security, AL expert, performance).
    Use when implementing a planned feature,
    generating AL code, or building from a solution plan.
    Requires a solution plan. Pass --autonomous to activate
    signature verification, static validation, and a
    self-healing compile loop (replaces /al-dev-autonomous).
    Prefer over ad-hoc implementation for anything beyond a trivial fix.
  ```

- [ ] **Step 9: Archive al-dev-autonomous (move whole directory)**

  ```bash
  mkdir -p profile-al-dev-shared/archived/skills/al-dev-autonomous
  git mv profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md \
         profile-al-dev-shared/archived/skills/al-dev-autonomous/SKILL.md
  if [ -d profile-al-dev-shared/skills/al-dev-autonomous/tests ]; then
    git mv profile-al-dev-shared/skills/al-dev-autonomous/tests \
           profile-al-dev-shared/archived/skills/al-dev-autonomous/tests
  fi
  ```

  Verify:
  ```bash
  ls profile-al-dev-shared/archived/skills/al-dev-autonomous/
  ls profile-al-dev-shared/skills/ | grep autonomous
  ```

  Expected: `SKILL.md` (and `tests/` if it existed) in archived; `ls skills/ | grep autonomous` returns empty.

- [ ] **Step 10: Remove al-dev-autonomous from the plugin map**

  In `docs/al-dev-plugin-map.md`:

  a. In the Layer 1 Mermaid diagram, find and remove these two lines:
  ```
      Plan -->|solution-plan.md| Autonomous("al-dev-autonomous")
      Autonomous -->|code-review.md| Commit
  ```

  b. Remove the `style Autonomous fill:#fff3e0` line.

  c. Remove the entire `### /al-dev-autonomous` section (heading + description + Mermaid block).

  d. In the Observations section, find the sentence about autonomous in "Potential shared agents not yet extracted" if present and remove it.

  e. Update the `**Last updated:**` line:
  ```
  **Last updated:** 2026-05-18 (al-dev-autonomous merged into al-dev-develop --autonomous; al-dev-align moved to .claude/skills/)
  ```

- [ ] **Step 11: Verify al-dev-develop SKILL.md line count is substantially larger**

  ```bash
  wc -l profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: 380+ lines (was ~300 before; autonomous phases add ~80–100 lines).

- [ ] **Step 12: Scan for forbidden patterns in all changed files**

  ```bash
  grep -rn '\[date\]\|TODO\|TBD\|Co-Authored-By\|claude:\|copilot:' \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
    profile-al-dev-shared/archived/skills/al-dev-autonomous/SKILL.md \
    docs/al-dev-plugin-map.md \
    --color=never || true
  ```

  Expected: no output.

- [ ] **Step 13: Verify develop skill still contains all key phase headings**

  ```bash
  grep -n "^## Phase" profile-al-dev-shared/skills/al-dev-develop/SKILL.md
  ```

  Expected: Phase 0, Phase 1, Phase 1A, Phase 2, Phase 3, Phase 4, Phase 4A, Phase 5, Phase 6, Phase 7, Phase 8, Phase 9, Phase 10 all present.

- [ ] **Step 14: Commit**

  ```bash
  git add \
    profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
    profile-al-dev-shared/archived/skills/al-dev-autonomous/SKILL.md \
    docs/al-dev-plugin-map.md
  git commit -m "$(cat <<'EOF'
  feat(develop): merge al-dev-autonomous into al-dev-develop via --autonomous flag

  Adds --autonomous mode to al-dev-develop activating: Phase 1A signature
  verification, Phase 4A static validation (object names, compile guards,
  label consistency), and a 5-attempt self-healing compile loop. Archives
  al-dev-autonomous to archived/skills/. Updates plugin map to remove the
  autonomous node and reflect the merged skill.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

## Acceptance Criteria (full plan)

Before marking the plan complete, verify:

- [ ] `knowledge/explore-subagent-pattern.md` exists with Steps A–D documented
- [ ] `knowledge/review-panel-pattern.md` exists with reviewer definitions and synthesis steps
- [ ] All three explore callers reference `explore-subagent-pattern.md`
- [ ] Both develop/autonomous reference `review-panel-pattern.md`
- [ ] `.claude/skills/al-dev-align/SKILL.md` exists and is identical to the original
- [ ] `profile-al-dev-shared/skills/al-dev-align/SKILL.md` no longer exists
- [ ] `profile-al-dev-shared/skills/al-dev-align/check-alignment.py` still exists
- [ ] Layer 1 diagram shows Explore, Interview, and ReleaseNotes nodes
- [ ] `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` contains Phase 1A and Phase 4A
- [ ] `profile-al-dev-shared/skills/al-dev-autonomous/SKILL.md` no longer exists in `skills/`
- [ ] `profile-al-dev-shared/archived/skills/al-dev-autonomous/SKILL.md` exists
- [ ] `git log --oneline -5` shows 5 commits (one per task)
