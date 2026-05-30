# Plugin Map Stale Observations Cleanup

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mark all 6 stale "Quality suggestions" in `docs/al-dev-agent-map.md` and 1 stale "Extension opportunities" entry in `docs/al-dev-plugin-map.md` as already-implemented — rubber-duck verification on 2026-05-29 confirmed every open suggestion is already live in the codebase.

**Architecture:** Two independent documentation edits, one commit each. No source file changes — the agent and skill files were already updated in prior sessions; the map Observations sections were not updated to reflect that.

**Tech Stack:** Markdown edits only.

---

## Why these suggestions are stale

Parallel Explore subagents read every affected file on 2026-05-29 and found:

| Suggestion | Finding |
|---|---|
| Remodel al-dev-solution-architect | Both /al-dev-plan and /al-dev-fix already conditionally pass `model: sonnet` for SIMPLE tier |
| Split al-dev-commit-agent-execute | `al-dev-commit-preflight` already exists (Step 9.5); execute agent already only handles git commits |
| Align al-dev-commit-recover-verifier | Inputs table line 23 already reads "Inferred from working directory; not passed explicitly" |
| Align al-dev-ticket-agent | Inputs table rows 19–22 already document env-var injection mechanism with a Note block |
| Align al-dev-developer TDD activation | Inputs table already marks test-plan Optional; agent body already has dual-path logic |
| Align al-dev-review-develop stub | SKILL.md is fully implemented with Phases 5–10 including reviewer spawn calls |
| Connect /al-dev-fix routing clarity | workflow-routing.md lines 40–46 already document the non-trivial architect escalation path |

---

## File Structure

| File | Change |
|---|---|
| `docs/al-dev-agent-map.md` | Replace 6 open Quality suggestions with ✅ confirmed-implemented entries |
| `docs/al-dev-plugin-map.md` | Replace 1 open Extension opportunities entry with ✅ confirmed-implemented entry |

---

### Task 1: Update agent map — mark all 6 Quality suggestions as confirmed implemented

**Files:**
- Modify: `docs/al-dev-agent-map.md`

- [ ] **Step 1: Read the Quality suggestions section to confirm it matches expected state**

```bash
grep -n "Quality suggestions\|Remodel\|Split: al-dev\|Align: al-dev\|stub skill" \
  docs/al-dev-agent-map.md
```

Expected: 6 open suggestion headings with no ✅ prefix.

- [ ] **Step 2: Replace the Quality suggestions block**

Use the Edit tool with the following exact replacement. The old_string must match the file exactly — if the grep output differs, read lines 526–558 of the file first and adjust.

**old_string** (replace this entire block):
```
### Quality suggestions

**Remodel: al-dev-solution-architect** ← highest leverage
Observation: Agent performs SIMPLE/MEDIUM/COMPLEX routing internally but uses opus for all complexity levels, including SIMPLE tasks (2–3 files, project-context-only research, no MCP lookups required).
Suggestion: Add a complexity-gated model: pass the complexity tier in the dispatch prompt; spawn with sonnet when classification is SIMPLE, reserve opus for MEDIUM and COMPLEX.
Trade-off: Requires spawning skills (/al-dev-plan, /al-dev-fix) to include the tier in their dispatch blocks; modest caller change for significant cost reduction on simple tasks.

**Split: al-dev-commit-agent-execute**
Observation: Agent body mixes two concerns: (a) pre-flight lint and OOXML validation with fix-and-retry loops, and (b) git commit execution with hook retry logic. Validation could fail and be retried independently of commit invocation.
Suggestion: Extract pre-flight lint/OOXML validation into a new agent al-dev-commit-preflight-validator; keep al-dev-commit-agent-execute focused on git commit invocation and hook handling.
Trade-off: New agent file to maintain; each phase becomes narrower and independently testable; commit-recover skill may also reuse the standalone preflight validator.

**Align: al-dev-commit-recover-verifier**
Observation: Agent Inputs table documents `REPO` as a required "Project root directory" parameter, but the /commit-recover skill passes `CORRUPTION_LOG` path explicitly and relies on working directory context for the repo root — no `REPO:` field appears in the dispatch prompt block.
Suggestion: Either (a) update the Inputs table to note "REPO is inferred from working directory, not passed explicitly," or (b) update /commit-recover dispatch to include `REPO: $(pwd)` as an explicit field.
Trade-off: Option (a) is documentation-only and lower friction; option (b) makes the dispatch self-documenting if REPO ever needs to differ from cwd.

**Align: al-dev-ticket-agent**
Observation: Agent Inputs table documents `FRESHDESK_API_KEY` and `FRESHDESK_DOMAIN` with the note "resolved from the harness environment and set as shell variables." The agent body cross-references `knowledge/ticket-agent-invocation-pattern.md` for the setup mechanism, but the Inputs table itself does not state how these variables reach the agent's bash execution context.
Suggestion: Expand the Inputs table rows to read "available as shell environment variables in the agent's bash execution context; exported by the spawning skill per knowledge/ticket-agent-invocation-pattern.md." Eliminates the need to chase the knowledge file to understand the caller contract.
Trade-off: Documentation-only change; self-documents the pass mechanism without changing behavior.

**Align: Clarify al-dev-developer TDD activation path**
Observation: Agent Inputs table documents `.dev/*-al-dev-test-test-plan.md` as required input "from /al-dev-develop," but the /al-dev-develop skill contains no logic to create test plans. Agent body gates the TDD workflow on test-plan file presence, but no spawning skill is documented as providing this file.
Suggestion: Update Inputs table row for test-plan: mark as "Optional: User-supplied or created upstream" and clarify which skill creates test plans. If TDD is not actively used, remove the test-plan input and the CRITICAL gate from the agent body.
Trade-off: Documentation-only change; prevents confusion about TDD activation contract.

**Align: al-dev-review-develop is a stub skill**
Observation: /al-dev-review-develop describes Phases 5–10 of the develop workflow but its SKILL.md body is a stub with no actual phase instructions. The three reviewer agents (expert, security, performance) are documented as its callers, but the skill contains no spawn calls.
Suggestion: Implement /al-dev-review-develop by copying Phases 5–10 from /al-dev-develop per the skill's own notes. Until then, /al-dev-develop is the only active spawner of the review panel.
Trade-off: Skill body is incomplete; review panel spawning works through /al-dev-develop only.
```

**new_string** (replace with this):
```
### Quality suggestions

All suggestions confirmed implemented as of 2026-05-29. Parallel Explore subagents read each affected file; every open suggestion was already live in the codebase.

**✅ Confirmed implemented: Remodel al-dev-solution-architect** (2026-05-29)
Both /al-dev-plan and /al-dev-fix already conditionally pass `model: sonnet` for SIMPLE tier and omit the model parameter (defaulting to opus) for MEDIUM/COMPLEX. No spawning-skill change needed.

**✅ Confirmed implemented: Split al-dev-commit-agent-execute** (2026-05-29)
Pre-flight lint and OOXML validation already extracted into `al-dev-commit-preflight` (dispatched at Step 9.5). al-dev-commit-agent-execute handles only git commit invocation and hook retry logic.

**✅ Confirmed implemented: Align al-dev-commit-recover-verifier** (2026-05-29)
Inputs table line 23 already reads: "Inferred from working directory; not passed explicitly by /commit-recover."

**✅ Confirmed implemented: Align al-dev-ticket-agent** (2026-05-29)
Inputs table rows already document FRESHDESK_API_KEY and FRESHDESK_DOMAIN as "available as shell environment variable in agent bash context" with a Note block explaining the injection mechanism.

**✅ Confirmed implemented: Align al-dev-developer TDD activation** (2026-05-29)
Inputs table already marks test-plan as Optional. Agent body correctly implements dual-path logic (TDD if file present, traditional if absent).

**✅ Confirmed implemented: Align al-dev-review-develop stub** (2026-05-29)
al-dev-review-develop/SKILL.md is fully implemented with all Phases 5–10 including reviewer spawn calls in Phase 6-7. Not a stub.
```

- [ ] **Step 3: Verify all 6 suggestions now show ✅**

```bash
grep -n "Confirmed implemented\|Quality suggestions" docs/al-dev-agent-map.md
```

Expected output: "Quality suggestions" header + 6 lines each containing "✅ Confirmed implemented".

```bash
grep -c "✅ Confirmed implemented" docs/al-dev-agent-map.md
```

Expected: `6`

- [ ] **Step 4: Update the agent map header date**

Change the `**Last updated:**` line at the top of `docs/al-dev-agent-map.md` from `2026-05-29 (19 agents; analysis refreshed with 4 new suggestions; workflow diagrams regenerated)` to `2026-05-29 (19 agents; all 6 quality suggestions confirmed implemented; Observations section cleaned up)`.

- [ ] **Step 5: Commit**

```bash
git add docs/al-dev-agent-map.md
git commit -m "$(cat <<'EOF'
docs(agent-map): mark all 6 quality suggestions as confirmed implemented

Parallel rubber-duck sweep (2026-05-29) verified every open suggestion in
the Observations section was already live in the codebase before the sweep.
Staleness arose because prior sessions updated agent/skill files without
updating the map. Suggestions now carry ✅ status with confirmation date.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Update plugin map — mark /al-dev-fix routing Connect suggestion as confirmed implemented

**Files:**
- Modify: `docs/al-dev-plugin-map.md`

- [ ] **Step 1: Read the Extension opportunities section to confirm it matches expected state**

```bash
grep -n "Extension opportunities\|al-dev-fix routing\|routing clarity" \
  docs/al-dev-plugin-map.md
```

Expected: item 2 with `/al-dev-fix` routing text and no ✅ prefix.

- [ ] **Step 2: Replace the stale Extension opportunities entry**

Use the Edit tool with the following exact replacement:

**old_string**:
```
2. **`/al-dev-fix` routing clarity**: Align the routing docs with the live skill so "fast fix" does not imply "always trivial" or "never uses an architect".
```

**new_string**:
```
2. **✅ Confirmed implemented: `/al-dev-fix` routing clarity** (2026-05-29): `workflow-routing.md` lines 40–46 already document the non-trivial architect escalation path explicitly. No prose update needed.
```

- [ ] **Step 3: Verify the entry now shows ✅**

```bash
grep -n "routing clarity" docs/al-dev-plugin-map.md
```

Expected: one line containing "✅ Confirmed implemented".

- [ ] **Step 4: Commit**

```bash
git add docs/al-dev-plugin-map.md
git commit -m "$(cat <<'EOF'
docs(plugin-map): mark /al-dev-fix routing Connect suggestion as confirmed implemented

workflow-routing.md lines 40-46 already document the non-trivial architect
escalation path. Suggestion was written against a stale version of the file.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```
