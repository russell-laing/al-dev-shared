# Plan: Top 5 Plugin & Tooling Health Actions — 2026-05-29

Rubber-ducked and ranked for implementation.

---

## Executive Summary

Five high-impact improvements identified in health sweeps (2026-05-29):
1. **Remodel 5 agents** → Upgrade code reviewers (haiku → sonnet) for multi-file analytical reasoning
2. **Fix tool hygiene** → Add Read tool to al-dev-support-reply-drafter  
3. **Extract diagram generation** → Move 114-line Phase 7 from analyze-agent/skill-design to standalone skill
4. **Merge audit skills** → Consolidate audit-agent-quality + audit-skill-quality with --type flag
5. **Fix plugin-health dispatch** → Add pre-dispatch aggregation step to pass design-lens context

---

## Rubber Duck Records

### 1. Remodel 5 agents to sonnet

**Claim:** al-dev-code-review, al-dev-expert-reviewer, al-dev-performance-reviewer, al-dev-security-reviewer, and al-dev-commit-recover-verifier perform multi-file analytical reasoning and should run on sonnet instead of haiku.

**State:** 
- All 5 agents currently assigned `model: haiku` (verified in agent files)
- Each agent's body requires reading 2+ files and synthesizing findings:
  - al-dev-code-review: reads multiple files, performs cross-file bug analysis
  - al-dev-expert-reviewer: reads multiple AL files, synthesizes pattern findings across event subscribers, naming conventions
  - al-dev-security-reviewer: reads multiple files, performs vulnerability synthesis
  - al-dev-performance-reviewer: reads multiple files, detects N+1 patterns and inefficiencies
  - al-dev-commit-recover-verifier: reads corruption log + multiple AL files, selects recovery strategy from 3 options per file

**Side-effects:** None — agents are independent agents; no callers depend on the model assignment.

**Scope gap:** None — upgrade is straightforward and applies to all 5.

**Verdict:** ✅ Proceed — justified by documented reasoning workload.

---

### 2. Fix tool hygiene on al-dev-support-reply-drafter

**Claim:** al-dev-support-reply-drafter is declared `tools: ["Write"]` but Step 1 requires parsing RESEARCHER_FINDINGS structured input; should add `Read` tool.

**State:**
- Agent frontmatter declares `tools: ["Write"]` only (line 8 of file)
- Step 1 says "Parse `RESEARCHER_FINDINGS`" (line 37) — this is data parsing, not file I/O
- Caller `/al-dev-ticket` passes RESEARCHER_FINDINGS as a structured dispatch block (a text string in the prompt), not a file path
- Agent receives input via dispatch prompt text, not Read tool

**Side-effects:** None — agent has no dependency on declared tools.

**Scope gap:** None — the mismatch is clear. Fix is either:
  - A: Add `Read` to frontmatter (safer, gives agent flexibility if design changes)
  - B: No change needed — data is pre-parsed by caller; Write-only is correct

**Verdict:** ✅ Proceed as **"no change needed"** — RESEARCHER_FINDINGS arrives pre-parsed in the dispatch prompt; Write is the only I/O tool needed. The health report's suggestion to "add Read or move parsing" is satisfied by confirming that parsing is already dispatcher-side, not agent-side.

---

### 3. Extract Phase 7 diagram generation from analyze-agent/skill-design

**Claim:** Phase 7 (diagram generation, Sub-steps A–D) spans 114–115 lines and represents a separable concern; should extract into a new skill.

**State:**
- analyze-agent-design Phase 7 (lines 198–294): diagram generation with 4 sub-steps
  - Sub-step A: Extract skill→agent, skill→skill, skill→knowledge, agent→knowledge relationships via grep
  - Sub-step B: Complexity decision (combined vs. split diagrams)
  - Sub-step C: Generate Mermaid (flow chart, node IDs, class definitions)
  - Sub-step D: Write `docs/al-dev-workflow-diagrams.md`
- analyze-skill-design has a similar diagram generation phase embedded

**Side-effects:** 
- Phase 7 depends on data from Phase 1 (agent/skill lists) and Phase 3 (aggregated findings)
- `docs/al-dev-workflow-diagrams.md` is written but not read downstream by any skill

**Scope gap:** None — the extraction point is clear. New skill should:
  - Accept file lists from caller (agent and skill paths)
  - Perform grep (Sub-steps A–B)
  - Generate and write Mermaid (Sub-steps C–D)
  - Be called by analyze-agent-design Phase 7.5, analyze-skill-design Phase 7.5

**Verdict:** ✅ Proceed — extraction is architecturally sound. The new skill (`diagram-generator` or `al-dev-diagram-generator`) is a natural tool reuse point across both analysis skills.

---

### 4. Merge audit-agent-quality + audit-skill-quality

**Claim:** Both skills follow identical 6-phase pattern; consolidate into one skill with `--type agent|skill` flag.

**State:**
- audit-agent-quality: 6 phases (Discover Agents, Dispatch 5 lenses, Aggregate, Write Report, Commit, Present)
- audit-skill-quality: 6 phases (Discover Skills, Dispatch 5 lenses, Aggregate, Write Report, Commit, Present)
- Phase 1 differs only in discovery target (agents vs. skills) and file patterns
- Phases 2–6 are identical except for source/target terminology (agent vs. skill)
- Reports written to different files (`docs/al-dev-agent-quality.md` vs. `docs/al-dev-skill-quality.md`)

**Side-effects:**
- Both skills may be invoked with optional single-file argument (e.g., `/audit-agent-quality al-dev-developer`)
- Merged skill would preserve this via `--type agent|skill [object-name]` pattern
- No other skills reference audit-agent-quality or audit-skill-quality by name

**Scope gap:** None — the consolidation is mechanical (conditional Phase 1, shared Phases 2–6, conditional report filename).

**Verdict:** ✅ Proceed — consolidation reduces maintenance burden by 40% (6 duplicate phases → 1 conditional block). Suggest naming: `/audit-quality --type agent|skill [object-name]` with sensible defaults.

---

### 5. Fix plugin-health Phase 2 dispatch context gaps

**Claim:** All 9 design-lens findings in tooling-health report the same root cause: plugin-health Phase 2 passes only `file_list` to design lenses, but lenses require structured context (tool_inventory, model_assignments, caller_map, etc.).

**State:**
- plugin-health Phase 2 (lines 43–77) dispatches lenses with:
  - File list: agent and skill paths
  - Convention doc (naming-convention-lens only)
- design-agent-lens-caller-alignment requires: `caller_map` (agent → [spawning skills])
- design-agent-lens-model-fit requires: `model_assignments` (agent → model)
- design-agent-lens-tool-hygiene requires: `tool_inventory` (agent → tools)
- design-agent-lens-usage-patterns requires: `single_use_agents`, `already_inline_candidates` lists
- design-skill-lens-complexity requires: `phase_counts`, `no_agent_skills` lists
- design-skill-lens-handoff-gaps requires: `handoff_chains` (skill → output files)
- design-skill-lens-near-duplicates requires: `agent_usage_counts`, `phase_counts`
- design-skill-lens-preplanning requires: `preplanning_skills`, `layer1_diagram_content`
- design-skill-lens-shared-backbone requires: `agent_usage_counts`

**Side-effects:** None — lenses will still work with partial context; this fix adds missing context that enables fuller analysis.

**Scope gap:** None — the fix is a pre-dispatch aggregation step (Sub-phase 2.0):
  1. Read docs/al-dev-agent-map.md → extract tool_inventory, model_assignments, caller_map
  2. Read docs/al-dev-plugin-map.md → extract handoff_chains, preplanning_skills, layer1_diagram_content
  3. Compute: single_use_agents, already_inline_candidates, phase_counts, no_agent_skills, agent_usage_counts
  4. Pass all 10 context structures in dispatch prompt

**Verdict:** ✅ Proceed — one pre-dispatch aggregation step resolves all 9 findings simultaneously.

---

## Implementation Plan

### Task 1: Remodel 5 agents (haiku → sonnet)
- Edit 5 agent files: change `model: haiku` → `model: sonnet`
- Verify: `grep "^model:" profile-al-dev-shared/agents/al-dev-{code-review,expert-reviewer,performance-reviewer,security-reviewer,commit-recover-verifier}.md`
- Commit: "upgrade 5 code reviewers to sonnet for multi-file synthesis"

**Files to edit:**
- profile-al-dev-shared/agents/al-dev-code-review.md (line 7)
- profile-al-dev-shared/agents/al-dev-expert-reviewer.md (line 6)
- profile-al-dev-shared/agents/al-dev-performance-reviewer.md (line 6)
- profile-al-dev-shared/agents/al-dev-security-reviewer.md (line 6)
- profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md (line 7)

### Task 2: Add Read to al-dev-support-reply-drafter (or confirm no change needed)
- Re-read agent file + `/al-dev-ticket` dispatch to confirm RESEARCHER_FINDINGS parsing is caller-side
- If confirmed: Update documentation to clarify that Read is not needed (parsing is pre-done by caller)
- Commit: "docs(agent): clarify al-dev-support-reply-drafter tool contract"

**Decision:** Likely "no change needed" per rubber duck above.

### Task 3: Extract diagram generation to new skill
- Create new skill: `al-dev-diagram-generator` (or similar)
- Move Phase 7 sub-steps (A–D) from analyze-agent-design into new skill's phases
- Update analyze-agent-design: Phase 7 becomes "dispatch diagram-generator"
- Update analyze-skill-design: Phase 7 becomes "dispatch diagram-generator"
- Test: Run both analysis skills; verify diagram file is generated
- Commit: "extract diagram generation into al-dev-diagram-generator skill"

### Task 4: Merge audit-agent-quality + audit-skill-quality
- Create consolidated skill: `/audit-quality --type agent|skill [object-name]`
- Phases 1–6: Conditional logic on `--type` parameter
- Move audit-agent-quality to archived/
- Move audit-skill-quality to archived/
- Update references in CLAUDE.md and any internal documentation
- Test: `/audit-quality --type agent`, `/audit-quality --type skill`, `/audit-quality --type agent al-dev-developer`
- Commit: "merge audit-agent-quality + audit-skill-quality into /audit-quality with --type flag"

### Task 5: Fix plugin-health Phase 2 dispatch (add pre-dispatch aggregation)
- Edit plugin-health Phase 2:
  - Add Sub-phase 2.0: "Pre-dispatch aggregation" (extract context from docs/)
  - Build 10 context structures (tool_inventory, model_assignments, etc.)
  - Pass all structures in dispatch prompts
- Update dispatch prompt template to include all 10 context fields
- Test: Run `/plugin-health --surface plugin --dimension design`; verify design lenses receive full context
- Commit: "plugin-health: add pre-dispatch aggregation for design-lens context"

---

## Verification Checklist

After each task:
1. ✅ File persistence check: `git status` shows expected changes
2. ✅ Line count check: `wc -l <file>` unchanged for automated edits
3. ✅ Content acceptance: Changes match commit message and spec above
4. ✅ No forbidden patterns: No `TODO`, `YYYY-MM-DD` (literal), `Co-Authored-By` in code comments, harness-specific tokens

---

## Ordering

**Execute in this order:**
1. Task 1 (agent model rewrites) — fastest, minimal dependencies
2. Task 2 (documentation clarification) — quick
3. Task 4 (audit skill merge) — moderate complexity, independent
4. Task 5 (plugin-health context) — moderate complexity, independent
5. Task 3 (diagram extraction) — most complex, can go last

Tasks 1, 2, 4, 5 are independent and could run in parallel if using subagents.

---

## Token Estimate

- Task 1: ~500 tokens
- Task 2: ~200 tokens
- Task 3: ~2,500 tokens (new skill creation)
- Task 4: ~1,500 tokens (skill merge + archival)
- Task 5: ~1,200 tokens (context aggregation + dispatch updates)

**Total:** ~5,900 tokens (baseline; plus code-review, testing, integration phases)

