# Sync Documentation Maps — Async Agent Teams Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `/sync-documentation-maps` so audit and update operations run asynchronously via remote agent teams, freeing the lead session after dispatch rather than blocking it for 1–2 hours.

**Architecture:** The current skill already runs skill-map and agent-map audits in parallel. The improvement is **session-freeing**: dispatch via `RemoteTrigger`, write artifacts to `.dev/sync-documentation-maps-runs/<run-id>/`, and exit. Two new sub-skills (`collect` and `finalize`) complete the workflow in follow-up sessions. Four named agent files document the audit/update logic.

**Tech Stack:** Markdown SKILL.md + agent `.md` files, `RemoteTrigger` for async dispatch, `TaskGet` for status polling, `.dev/` for artifact coordination.

---

## File Structure

| Action | Path | Responsibility |
| ------ | ---- | -------------- |
| Modify | `.claude/skills/sync-documentation-maps/SKILL.md` | Dispatch coordinator: spawn audit teams, write checkpoint, exit |
| Create | `.claude/skills/sync-documentation-maps-collect/SKILL.md` | Fetch audit artifacts, present findings, spawn update teams |
| Create | `.claude/skills/sync-documentation-maps-finalize/SKILL.md` | Write updated maps to disk, refresh graph, commit |
| Create | `.claude/agents/sync-documentation-maps-skill-audit.md` | Remote agent: audit skills vs. skills map, write JSON |
| Create | `.claude/agents/sync-documentation-maps-agent-audit.md` | Remote agent: audit agents vs. agent map, write JSON |
| Create | `.claude/agents/sync-documentation-maps-skill-update.md` | Remote agent: apply audit findings, write updated skills map |
| Create | `.claude/agents/sync-documentation-maps-agent-update.md` | Remote agent: apply audit findings, write updated agent map |

Runtime artifacts under `.dev/sync-documentation-maps-runs/<run-id>/` (never committed).

---

### Task 1: Create sync-documentation-maps-skill-audit Agent

**Files:**

- Create: `.claude/agents/sync-documentation-maps-skill-audit.md`

- [ ] **Step 1: Verify .claude/agents/ directory exists**

  ```bash
  ls .claude/agents/ | head -5
  ```

  Expected: lists existing agent `.md` files (e.g., `design-agent-lens-tool-hygiene.md`).

- [ ] **Step 2: Write the agent file**

  Create `.claude/agents/sync-documentation-maps-skill-audit.md`.

  **Frontmatter:**

  ```yaml
  ---
  name: sync-documentation-maps-skill-audit
  description: >-
    Audits active skills in profile-al-dev-shared/skills/ against
    docs/al-dev-skills-map.md and writes a structured JSON discrepancy report
    to the run artifact directory. Called by /sync-documentation-maps dispatch phase.
  model: claude-sonnet-4-6
  tools: ["Read", "Bash", "Write"]
  ---
  ```

  **Body — Inputs section:**

  A two-column table with fields `run_id` (the timestamp run ID) and `result_dir`
  (absolute path to `.dev/sync-documentation-maps-runs/<run_id>/`).

  **Body — Outputs section:**

  Writes `<result_dir>/audit/skill-audit.json` and returns its absolute path.
  Describe the JSON schema: object with fields `surface` ("skills"), `run_id`,
  `total_files` (int), `map_entries` (int), `discrepancies` (array of objects
  each with `type`, `skill`, `detail`), and `summary` (string).
  Valid `type` values: `missing_from_map`, `stale_in_map`, `phase_count_mismatch`,
  `agent_name_mismatch`.

  **Body — Instructions section:**

  Five numbered steps:

  1. Build active skill list by running `ls profile-al-dev-shared/skills/` and
     `ls profile-al-dev-shared/archived/skills/ 2>/dev/null`. Active skills =
     the `skills/` list minus any names also in `archived/skills/`.

  2. For each active skill, Read `profile-al-dev-shared/skills/<name>/SKILL.md`.
     Extract: phase count (count `## Phase N` headings), agents spawned
     (`al-dev-shared:<agent-name>` patterns), output files (`.dev/` path writes).

  3. Read `docs/al-dev-skills-map.md`. Extract Layer 1 flowchart node IDs and the
     list of `### /skill-name` headings in Layer 2.

  4. Identify discrepancies: active skill with no Layer 2 section → `missing_from_map`;
     Layer 2 section for an archived skill → `stale_in_map`; phase count label mismatch
     → `phase_count_mismatch`; agent name mismatch → `agent_name_mismatch`.

  5. Write the JSON report to `<result_dir>/audit/skill-audit.json`. Verify the file
     exists with `ls -la`. Return only the absolute file path; do not summarise
     findings to the user.

- [ ] **Step 3: Verify the file was written**

  ```bash
  ls -la .claude/agents/sync-documentation-maps-skill-audit.md
  wc -l .claude/agents/sync-documentation-maps-skill-audit.md
  ```

  Expected: file exists, ≥40 lines.

- [ ] **Step 4: Run markdownlint**

  ```bash
  markdownlint .claude/agents/sync-documentation-maps-skill-audit.md 2>&1
  ```

  Expected: no errors.

- [ ] **Step 5: Commit**

  ```bash
  git add .claude/agents/sync-documentation-maps-skill-audit.md
  git commit -m "$(cat <<'EOF'
  feat(agent): add sync-documentation-maps-skill-audit agent

  Remote agent that audits profile-al-dev-shared skills against the skills map
  and writes a structured JSON discrepancy report to the run artifact directory.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

### Task 2: Create sync-documentation-maps-agent-audit Agent

**Files:**

- Create: `.claude/agents/sync-documentation-maps-agent-audit.md`

- [ ] **Step 1: Write the agent file**

  Create `.claude/agents/sync-documentation-maps-agent-audit.md`.

  **Frontmatter:**

  ```yaml
  ---
  name: sync-documentation-maps-agent-audit
  description: >-
    Audits active agents in profile-al-dev-shared/agents/ against
    docs/al-dev-agent-map.md and writes a structured JSON discrepancy report
    to the run artifact directory. Called by /sync-documentation-maps dispatch phase.
  model: claude-sonnet-4-6
  tools: ["Read", "Bash", "Write"]
  ---
  ```

  **Body — Inputs section:**

  A two-column table with fields `run_id` and `result_dir` (same as skill-audit agent).

  **Body — Outputs section:**

  Writes `<result_dir>/audit/agent-audit.json` and returns its absolute path.
  JSON schema: same shape as skill-audit but with `surface` = "agents", and
  `discrepancies` array items use field `agent` instead of `skill`.
  Valid `type` values: `missing_from_map`, `stale_in_map`, `model_mismatch`,
  `tools_mismatch`, `caller_mismatch`.

  **Body — Instructions section:**

  Six numbered steps:

  1. Build active agent list by running `ls profile-al-dev-shared/agents/` and
     `ls profile-al-dev-shared/archived/agents/ 2>/dev/null`. Active agents =
     `.md` files in `agents/` minus any names also in `archived/agents/`.

  2. For each active agent, Read `profile-al-dev-shared/agents/<name>.md`.
     Extract from frontmatter: `model`, `tools` list, `description` (first sentence).

  3. Cross-reference callers: for each agent, grep
     `grep -rl "al-dev-shared:<name-without-.md>" profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null`
     AND `grep -rl "<name-without-.md>" profile-al-dev-shared/skills/ .claude/skills/ 2>/dev/null`.
     Union both result sets to build the caller list.

  4. Read `docs/al-dev-agent-map.md`. Extract Layer 1 Catalog table rows and
     the list of `### <agent-name>` headings in Layer 2.

  5. Identify discrepancies: active agent not in Layer 1 table → `missing_from_map`;
     Layer 1 row for an archived agent → `stale_in_map`; model mismatch →
     `model_mismatch`; tools list mismatch → `tools_mismatch`; spawned-by mismatch
     vs. grep results → `caller_mismatch`.

  6. Write the JSON report to `<result_dir>/audit/agent-audit.json`. Verify with
     `ls -la`. Return only the absolute file path.

- [ ] **Step 2: Verify the file was written**

  ```bash
  ls -la .claude/agents/sync-documentation-maps-agent-audit.md
  wc -l .claude/agents/sync-documentation-maps-agent-audit.md
  ```

  Expected: file exists, ≥40 lines.

- [ ] **Step 3: Run markdownlint**

  ```bash
  markdownlint .claude/agents/sync-documentation-maps-agent-audit.md 2>&1
  ```

  Expected: no errors.

- [ ] **Step 4: Commit**

  ```bash
  git add .claude/agents/sync-documentation-maps-agent-audit.md
  git commit -m "$(cat <<'EOF'
  feat(agent): add sync-documentation-maps-agent-audit agent

  Remote agent that audits profile-al-dev-shared agents against the agent map
  and writes a structured JSON discrepancy report to the run artifact directory.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

### Task 3: Create sync-documentation-maps-skill-update Agent

**Files:**

- Create: `.claude/agents/sync-documentation-maps-skill-update.md`

- [ ] **Step 1: Write the agent file**

  Create `.claude/agents/sync-documentation-maps-skill-update.md`.

  **Frontmatter:**

  ```yaml
  ---
  name: sync-documentation-maps-skill-update
  description: >-
    Reads skill audit findings from the run artifact directory and writes an
    updated docs/al-dev-skills-map.md to the run updates directory.
    Called by /sync-documentation-maps-collect update dispatch phase.
  model: claude-sonnet-4-6
  tools: ["Read", "Bash", "Write"]
  ---
  ```

  **Body — Inputs section:**

  A two-column table with fields `run_id` and `result_dir`.

  **Body — Outputs section:**

  Writes `<result_dir>/updates/skills-map.md` (the full updated map content)
  and returns its absolute path. File must be ≥100 lines and begin with `# AL Dev`.

  **Body — Instructions section:**

  Five numbered steps:

  1. Read `<result_dir>/audit/skill-audit.json`. Parse the `discrepancies` array.
     Stop with error if the file does not exist.

  2. Read `docs/al-dev-skills-map.md` as the base to update.

  3. Apply each discrepancy fix:
     `missing_from_map` — read the skill file, insert a new Layer 2 `### /skill-name`
     section following the existing template; add node/edge/style to Layer 1 if it is
     a lifecycle skill.
     `stale_in_map` — remove the Layer 2 section; remove node, edges, and style
     directive from Layer 1; confirm no orphaned `style` lines remain.
     `phase_count_mismatch` — rewrite the Layer 2 `flowchart LR` block to match.
     `agent_name_mismatch` — update Layer 2 agent references.
     After any Layer 1 edit: confirm every `style X` line has a matching node ID;
     delete orphaned style lines.

  4. Replace the `**Last updated:**` value with today's date (YYYY-MM-DD).

  5. Write the complete updated map to `<result_dir>/updates/skills-map.md`. Verify
     with `ls -la` and `wc -l` (must be ≥100 lines). Return only the absolute path.

- [ ] **Step 2: Verify the file was written**

  ```bash
  ls -la .claude/agents/sync-documentation-maps-skill-update.md
  wc -l .claude/agents/sync-documentation-maps-skill-update.md
  ```

  Expected: file exists, ≥40 lines.

- [ ] **Step 3: Run markdownlint**

  ```bash
  markdownlint .claude/agents/sync-documentation-maps-skill-update.md 2>&1
  ```

  Expected: no errors.

- [ ] **Step 4: Commit**

  ```bash
  git add .claude/agents/sync-documentation-maps-skill-update.md
  git commit -m "$(cat <<'EOF'
  feat(agent): add sync-documentation-maps-skill-update agent

  Remote agent that applies skill-audit findings and writes an updated skills
  map to the run artifact directory for finalization review.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

### Task 4: Create sync-documentation-maps-agent-update Agent

**Files:**

- Create: `.claude/agents/sync-documentation-maps-agent-update.md`

- [ ] **Step 1: Write the agent file**

  Create `.claude/agents/sync-documentation-maps-agent-update.md`.

  **Frontmatter:**

  ```yaml
  ---
  name: sync-documentation-maps-agent-update
  description: >-
    Reads agent audit findings from the run artifact directory and writes an
    updated docs/al-dev-agent-map.md to the run updates directory.
    Called by /sync-documentation-maps-collect update dispatch phase.
  model: claude-sonnet-4-6
  tools: ["Read", "Bash", "Write"]
  ---
  ```

  **Body — Inputs section:**

  A two-column table with fields `run_id` and `result_dir`.

  **Body — Outputs section:**

  Writes `<result_dir>/updates/agent-map.md` (the full updated map content)
  and returns its absolute path. File must be ≥50 lines and begin with `# AL Dev`.

  **Body — Instructions section:**

  Five numbered steps:

  1. Read `<result_dir>/audit/agent-audit.json`. Parse the `discrepancies` array.
     Stop with error if the file does not exist.

  2. Read `docs/al-dev-agent-map.md` as the base to update.

  3. Apply each discrepancy fix:
     `missing_from_map` — read the agent file, add a row to Layer 1 Catalog table
     and insert a new `### <agent-name>` Layer 2 profile section.
     `stale_in_map` — remove the agent's Layer 1 table row and Layer 2 section.
     `model_mismatch` — correct the model value in both Layer 1 row and Layer 2 field.
     `tools_mismatch` — correct the tools list in both Layer 1 row and Layer 2 field.
     `caller_mismatch` — correct the spawned-by field in both layers to match grep results.

  4. Replace the `**Last updated:**` value with today's date (YYYY-MM-DD).

  5. Write the complete updated map to `<result_dir>/updates/agent-map.md`. Verify
     with `ls -la` and `wc -l` (must be ≥50 lines). Return only the absolute path.

- [ ] **Step 2: Verify the file was written**

  ```bash
  ls -la .claude/agents/sync-documentation-maps-agent-update.md
  wc -l .claude/agents/sync-documentation-maps-agent-update.md
  ```

  Expected: file exists, ≥40 lines.

- [ ] **Step 3: Run markdownlint**

  ```bash
  markdownlint .claude/agents/sync-documentation-maps-agent-update.md 2>&1
  ```

  Expected: no errors.

- [ ] **Step 4: Commit**

  ```bash
  git add .claude/agents/sync-documentation-maps-agent-update.md
  git commit -m "$(cat <<'EOF'
  feat(agent): add sync-documentation-maps-agent-update agent

  Remote agent that applies agent-audit findings and writes an updated agent
  map to the run artifact directory for finalization review.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

### Task 5: Rewrite sync-documentation-maps as Dispatch Coordinator

**Files:**

- Modify: `.claude/skills/sync-documentation-maps/SKILL.md`

- [ ] **Step 1: Confirm current file**

  ```bash
  wc -l .claude/skills/sync-documentation-maps/SKILL.md
  head -5 .claude/skills/sync-documentation-maps/SKILL.md
  ```

  Expected: ~176 lines; frontmatter shows `name: sync-documentation-maps`.

- [ ] **Step 2: Write the new skill**

  Replace the entire `.claude/skills/sync-documentation-maps/SKILL.md` with
  a skill that has this structure:

  **Frontmatter:**

  ```yaml
  ---
  name: sync-documentation-maps
  description: >-
    Use when plugin documentation maps are out of sync with the current codebase,
    or to verify accuracy after adding/removing skills or agents. Dispatches
    parallel remote audit teams via RemoteTrigger and exits — session freed after
    ~5 minutes. Collect results with /sync-documentation-maps-collect.
    Triggers: "sync documentation maps", "update maps", "are the maps accurate".
  argument-hint: "[--all] [--skip-commit]"
  ---
  ```

  **Body — overview paragraph:**

  Lightweight dispatch coordinator. Spawns parallel remote audit teams for
  skills and agents via RemoteTrigger, writes a checkpoint with team IDs and
  artifact paths, then exits. Note: the skill-map and agent-map audits already
  ran in parallel in the previous design; the improvement is that the lead
  session is freed after dispatch rather than waiting inline for 90+ minutes.

  Document the three-skill workflow:
  1. `/sync-documentation-maps` — dispatch audit teams (this skill, ~5 min)
  2. `/sync-documentation-maps-collect --team-ids <ids>` — collect results, spawn updates
  3. `/sync-documentation-maps-finalize --team-ids <ids>` — write maps, commit

  **Phase 0 — Parse Arguments:**
  If `--all` present, set `AUTO_UPDATE=true`. If `--skip-commit` present, set `SKIP_COMMIT=true`.

  **Phase 1 — Generate Run Context:**

  ```bash
  RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
  RUN_DIR="/Users/russelllaing/al-dev-shared/.dev/sync-documentation-maps-runs/${RUN_ID}"
  mkdir -p "${RUN_DIR}/audit"
  mkdir -p "${RUN_DIR}/updates"
  ls -la "${RUN_DIR}/"
  ```

  **Phase 2 — Build File Lists:**

  ```bash
  ls profile-al-dev-shared/skills/
  ls profile-al-dev-shared/archived/skills/ 2>/dev/null
  ls profile-al-dev-shared/agents/
  ls profile-al-dev-shared/archived/agents/ 2>/dev/null
  ```

  **Phase 3 — Spawn Audit Teams via RemoteTrigger:**

  Dispatch both tasks simultaneously (before waiting for either). For each task,
  reference the corresponding agent file for the full instructions
  (`.claude/agents/sync-documentation-maps-skill-audit.md` and
  `.claude/agents/sync-documentation-maps-agent-audit.md`). Pass `RUN_ID` and
  `RUN_DIR` in each prompt. Capture returned task IDs as `SKILL_TEAM_ID` and
  `AGENT_TEAM_ID`.

  **Phase 4 — Write Checkpoint:**

  Write `.dev/sync-documentation-maps-checkpoint.json` with fields:
  `operation`, `run_id`, `spawned_at`, `skill_audit_team_id`, `agent_audit_team_id`,
  `phase` ("audit"), `status` ("dispatched"), `auto_update`, `skip_commit`,
  `result_dir`, `manifest_path`.

  Also write the same JSON to `<RUN_DIR>/manifest.json`.

  Verify both files exist:

  ```bash
  ls -la .dev/sync-documentation-maps-checkpoint.json
  ls -la "${RUN_DIR}/manifest.json"
  ```

  Append the run ID, team IDs, and next-step command to `.dev/progress.md`.

  **Phase 5 — Return to User:**

  Print the team IDs, run directory, checkpoint path, and next-step command
  (`/sync-documentation-maps-collect --team-ids <SKILL_TEAM_ID>,<AGENT_TEAM_ID>`).
  Exit.

  **Arguments section:**

  Document `--all` (propagated via checkpoint to skip user prompt in collect phase)
  and `--skip-commit` (propagated to prevent commit in finalize phase).

- [ ] **Step 3: Verify the file was written and not truncated**

  ```bash
  ls -la .claude/skills/sync-documentation-maps/SKILL.md
  wc -l .claude/skills/sync-documentation-maps/SKILL.md
  ```

  Expected: file exists, ≥60 lines.

- [ ] **Step 4: Run markdownlint**

  ```bash
  markdownlint .claude/skills/sync-documentation-maps/SKILL.md 2>&1
  ```

  Expected: no errors.

- [ ] **Step 5: Commit**

  ```bash
  git add .claude/skills/sync-documentation-maps/SKILL.md
  git commit -m "$(cat <<'EOF'
  refactor(skill): rewrite sync-documentation-maps as async dispatch coordinator

  Replaces the in-session wait pattern with RemoteTrigger-based dispatch that
  spawns parallel skill and agent audit teams, writes a checkpoint, and exits.
  Session freed after ~5 min vs. blocking 90+ min. Audits already ran in
  parallel before; the improvement is session-freeing, not parallelism.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

### Task 6: Create sync-documentation-maps-collect Skill

**Files:**

- Create: `.claude/skills/sync-documentation-maps-collect/SKILL.md`

- [ ] **Step 1: Create the skill directory**

  ```bash
  mkdir -p .claude/skills/sync-documentation-maps-collect
  ls -la .claude/skills/sync-documentation-maps-collect/
  ```

  Expected: empty directory created.

- [ ] **Step 2: Write the skill**

  Create `.claude/skills/sync-documentation-maps-collect/SKILL.md`.

  **Frontmatter:**

  ```yaml
  ---
  name: sync-documentation-maps-collect
  description: >-
    Collect results from /sync-documentation-maps audit teams. Reads audit
    artifacts, presents discrepancy findings, asks which maps to update, and
    dispatches remote update teams. Second step of the async sync workflow.
  argument-hint: "--team-ids <skill-id>,<agent-id> [--wait]"
  ---
  ```

  **Body:** Eight phases:

  **Phase 0 — Parse Arguments:** Split `--team-ids` on comma to get `SKILL_TEAM_ID`
  and `AGENT_TEAM_ID`. Error if absent. Set `WAIT_MODE=true` if `--wait` present.

  **Phase 1 — Load Checkpoint:** Read `.dev/sync-documentation-maps-checkpoint.json`.
  Extract `run_id`, `result_dir`, `auto_update`, `skip_commit`. Error if file absent.

  **Phase 2 — Optionally Poll Teams:** If `WAIT_MODE=true`, use `TaskGet` to poll
  both team IDs until `completed` or `failed`. Log status each check.
  Timeout after 30 minutes. If `WAIT_MODE=false`, proceed immediately.

  **Phase 3 — Read Audit Artifacts:** Run `ls -la` on both
  `<result_dir>/audit/skill-audit.json` and `<result_dir>/audit/agent-audit.json`.
  Parse JSON for each present file. Report pending for any absent file.
  If both absent, advise `--wait` and stop.

  **Phase 4 — Present Findings:** Show `summary` and each discrepancy bullet for
  each surface. If both have zero discrepancies, report maps are accurate and stop
  (update checkpoint status to "complete").

  **Phase 5 — Ask User What to Update:** If `AUTO_UPDATE=true`, set
  `UPDATE_CHOICE=both`. Otherwise use `AskUserQuestion` with options:
  skills only, agents only, both, neither. If neither, update checkpoint
  status to "skipped" and stop.

  **Phase 6 — Spawn Update Teams via RemoteTrigger:** Based on `UPDATE_CHOICE`,
  dispatch update tasks referencing `.claude/agents/sync-documentation-maps-skill-update.md`
  and/or `.claude/agents/sync-documentation-maps-agent-update.md`.
  Pass `RUN_ID` and `RUN_DIR` in each prompt. Capture `SKILL_UPDATE_TEAM_ID`
  and/or `AGENT_UPDATE_TEAM_ID`.

  **Phase 7 — Write Updated Checkpoint:** Update
  `.dev/sync-documentation-maps-checkpoint.json` and `<RUN_DIR>/manifest.json`
  to add `skill_update_team_id`, `agent_update_team_id`, `update_choice`, and
  set `phase` to "update", `status` to "dispatched".

  **Phase 8 — Return to User:** Print the finalize command with non-null team IDs
  and exit.

- [ ] **Step 3: Verify the file was written**

  ```bash
  ls -la .claude/skills/sync-documentation-maps-collect/SKILL.md
  wc -l .claude/skills/sync-documentation-maps-collect/SKILL.md
  ```

  Expected: file exists, ≥60 lines.

- [ ] **Step 4: Run markdownlint**

  ```bash
  markdownlint .claude/skills/sync-documentation-maps-collect/SKILL.md 2>&1
  ```

  Expected: no errors.

- [ ] **Step 5: Commit**

  ```bash
  git add .claude/skills/sync-documentation-maps-collect/SKILL.md
  git commit -m "$(cat <<'EOF'
  feat(skill): add sync-documentation-maps-collect sub-skill

  Collects audit results from remote teams, presents discrepancy findings,
  and dispatches update teams for selected maps. Second step of the async
  sync-documentation-maps workflow.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

### Task 7: Create sync-documentation-maps-finalize Skill

**Files:**

- Create: `.claude/skills/sync-documentation-maps-finalize/SKILL.md`

- [ ] **Step 1: Create the skill directory**

  ```bash
  mkdir -p .claude/skills/sync-documentation-maps-finalize
  ls -la .claude/skills/sync-documentation-maps-finalize/
  ```

  Expected: empty directory created.

- [ ] **Step 2: Write the skill**

  Create `.claude/skills/sync-documentation-maps-finalize/SKILL.md`.

  **Frontmatter:**

  ```yaml
  ---
  name: sync-documentation-maps-finalize
  description: >-
    Finalize sync-documentation-maps updates. Reads updated map artifacts from
    remote update teams, writes them to docs/, refreshes the dependency graph,
    and commits. Final step of the async sync-documentation-maps workflow.
  argument-hint: "--team-ids <ids> [--skip-commit]"
  ---
  ```

  **Body:** Eight phases:

  **Phase 0 — Parse Arguments:** Parse `--team-ids` into `UPDATE_TEAM_IDS`.
  Set `SKIP_COMMIT=true` if `--skip-commit` present.

  **Phase 1 — Load Checkpoint:** Read `.dev/sync-documentation-maps-checkpoint.json`.
  Extract `run_id`, `result_dir`, `update_choice`, `skip_commit`.
  Error if absent or if `phase` is not "update".

  **Phase 2 — Check Update Team Status:** Call `TaskGet` for each ID in
  `UPDATE_TEAM_IDS`. Report `completed`/`running`/`failed` per team.
  Artifact check in Phase 3 is the authoritative gate; continue regardless of status.

  **Phase 3 — Read and Validate Update Artifacts:** Run `ls -la` and `wc -l` on
  `<result_dir>/updates/skills-map.md` (if skills or both selected) and
  `<result_dir>/updates/agent-map.md` (if agents or both selected).
  For each: absent → report and skip that surface; empty or missing `# AL Dev`
  header → report invalid and skip; valid → read content and proceed.
  If all expected artifacts are missing, stop with clear message.

  **Phase 4 — Write Updated Maps to Disk:**

  ```bash
  cp "${RUN_DIR}/updates/skills-map.md" docs/al-dev-skills-map.md
  wc -l docs/al-dev-skills-map.md
  # and/or for agents:
  cp "${RUN_DIR}/updates/agent-map.md" docs/al-dev-agent-map.md
  wc -l docs/al-dev-agent-map.md
  ```

  Verify ≥100 lines for skills map, ≥50 lines for agent map.

  **Phase 5 — Refresh Dependency Graph:**

  ```bash
  python3 scripts/generate-agent-projections.py
  ```

  Report but continue on non-zero exit.

  **Phase 6 — Present Summary:** List each updated file with line count and
  graph refresh status.

  **Phase 7 — Commit:** If `SKIP_COMMIT=true`, print dry-run message and stop.
  Otherwise:

  ```bash
  git status
  git add docs/al-dev-skills-map.md docs/al-dev-agent-map.md
  git add profile-al-dev-shared/generated/ 2>/dev/null || true
  git diff --cached --stat
  git commit -m "docs: sync documentation maps with current codebase"
  git log --oneline -n 1
  ```

  **Phase 8 — Update Checkpoint:** Set `phase` to "complete" and `status` to
  "done" in both `.dev/sync-documentation-maps-checkpoint.json` and
  `<RUN_DIR>/manifest.json`. Append completion record to `.dev/progress.md`.

- [ ] **Step 3: Verify the file was written**

  ```bash
  ls -la .claude/skills/sync-documentation-maps-finalize/SKILL.md
  wc -l .claude/skills/sync-documentation-maps-finalize/SKILL.md
  ```

  Expected: file exists, ≥60 lines.

- [ ] **Step 4: Run markdownlint**

  ```bash
  markdownlint .claude/skills/sync-documentation-maps-finalize/SKILL.md 2>&1
  ```

  Expected: no errors.

- [ ] **Step 5: Commit**

  ```bash
  git add .claude/skills/sync-documentation-maps-finalize/SKILL.md
  git commit -m "$(cat <<'EOF'
  feat(skill): add sync-documentation-maps-finalize sub-skill

  Reads update artifacts from remote teams, writes updated maps to docs/,
  refreshes the dependency graph, and commits. Final step of the async
  sync-documentation-maps workflow.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  EOF
  )"
  ```

---

### Task 8: End-to-End Verification

**Files:** no changes; read-only verification.

- [ ] **Step 1: Verify all seven files exist**

  ```bash
  ls -la \
    .claude/agents/sync-documentation-maps-skill-audit.md \
    .claude/agents/sync-documentation-maps-agent-audit.md \
    .claude/agents/sync-documentation-maps-skill-update.md \
    .claude/agents/sync-documentation-maps-agent-update.md \
    .claude/skills/sync-documentation-maps/SKILL.md \
    .claude/skills/sync-documentation-maps-collect/SKILL.md \
    .claude/skills/sync-documentation-maps-finalize/SKILL.md
  ```

  Expected: all seven listed with non-zero sizes.

- [ ] **Step 2: Verify required frontmatter fields**

  ```bash
  python3 -c "
  agents = [
    '.claude/agents/sync-documentation-maps-skill-audit.md',
    '.claude/agents/sync-documentation-maps-agent-audit.md',
    '.claude/agents/sync-documentation-maps-skill-update.md',
    '.claude/agents/sync-documentation-maps-agent-update.md',
  ]
  skills = [
    '.claude/skills/sync-documentation-maps/SKILL.md',
    '.claude/skills/sync-documentation-maps-collect/SKILL.md',
    '.claude/skills/sync-documentation-maps-finalize/SKILL.md',
  ]
  for f in agents:
    c = open(f).read()
    missing = [r for r in ['name:', 'description:', 'model:', 'tools:'] if r not in c]
    print(f + ': ' + ('OK' if not missing else 'MISSING: ' + str(missing)))
  for f in skills:
    c = open(f).read()
    missing = [r for r in ['name:', 'description:', 'argument-hint:'] if r not in c]
    print(f + ': ' + ('OK' if not missing else 'MISSING: ' + str(missing)))
  "
  ```

  Expected: all seven print `OK`.

- [ ] **Step 3: Check for forbidden patterns**

  ```bash
  grep -rn "TODO\|TBD\|\[date\]" \
    .claude/agents/sync-documentation-maps-skill-audit.md \
    .claude/agents/sync-documentation-maps-agent-audit.md \
    .claude/agents/sync-documentation-maps-skill-update.md \
    .claude/agents/sync-documentation-maps-agent-update.md \
    .claude/skills/sync-documentation-maps/SKILL.md \
    .claude/skills/sync-documentation-maps-collect/SKILL.md \
    .claude/skills/sync-documentation-maps-finalize/SKILL.md \
    2>/dev/null
  ```

  Expected: no output.

- [ ] **Step 4: Run markdownlint on all seven files**

  ```bash
  markdownlint \
    .claude/agents/sync-documentation-maps-skill-audit.md \
    .claude/agents/sync-documentation-maps-agent-audit.md \
    .claude/agents/sync-documentation-maps-skill-update.md \
    .claude/agents/sync-documentation-maps-agent-update.md \
    .claude/skills/sync-documentation-maps/SKILL.md \
    .claude/skills/sync-documentation-maps-collect/SKILL.md \
    .claude/skills/sync-documentation-maps-finalize/SKILL.md \
    2>&1
  ```

  Expected: no errors.

- [ ] **Step 5: Confirm skill directories visible**

  ```bash
  ls .claude/skills/ | grep sync-documentation-maps
  ```

  Expected output includes `sync-documentation-maps`, `sync-documentation-maps-collect`,
  and `sync-documentation-maps-finalize`.

- [ ] **Step 6: Confirm all commits landed**

  ```bash
  git log --oneline -n 8
  ```

  Expected: 7 commits visible — one per file (4 agents, 3 skills).

---

## Spec Coverage Checklist

| Success criterion | Plan coverage |
| --- | --- |
| Skill and agent audits run in parallel | Task 5 Phase 3: two RemoteTrigger calls dispatched before either completes |
| Session freed after dispatch | Task 5 Phase 5: skill exits after checkpoint write, ~5 min total |
| Session token burn reduced | Audits no longer block the lead session; in-session work is checkpoint I/O only |
| Audit results identical to current system | Agent instructions mirror review-skill-map / review-agent-map audit logic |
| Updated maps identical to current system | Update agent instructions mirror review-skill-map / review-agent-map update logic |
| Multi-session workflow supported | Checkpoint persists across sessions; collect/finalize each read it on startup |
| Same interface (--all, --skip-commit) | Task 5 Phase 0: args written to checkpoint; Tasks 6/7 read them |
| Partial-failure handling | Task 6 Phase 3: missing artifacts reported per-surface; other surface continues |
| Error on no active run | Tasks 6/7 Phase 1: missing checkpoint triggers clear error message |
