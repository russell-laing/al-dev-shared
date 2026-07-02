# Health Quality Loop — Implementation Plan Spec

**Date:** 2026-07-02  
**Source:** plan-plugin-findings-verify checkpoint (18 verified findings)  
**Target:** Fix quality/naming issues across plugin skills and agents

## Executive Summary

Implement 18 verified findings from quality audit: update tool lists, descriptions, agent names, and flag consistency across the distributed plugin surface. All changes target `profile-al-dev-shared/` (harness-neutral shared layer).

## Verified Findings (Rubber-Ducked)

### PROCEED — 14 verified real issues

| Event ID | Object | Finding | Fix Scope |
|----------|--------|---------|-----------|
| disp_20260702_000103 | explore.md | Tool list omits Bash | Add Bash to tools frontmatter |
| disp_20260702_000109 | evidence-gatherer.md | MCP tools undeclared | Extend tools list (AL MCP, LSP) |
| disp_20260702_000112 | release-notes-writer.md | Description says extract, body delegates to sub-agent | Update description to clarify orchestrator role |
| disp_20260702_000114 | explore.md | Generic name | Rename to codebase-explorer |
| disp_20260702_000117 | document.md | Formatting-Sweep Variant 105 lines bundled | Informational; already acceptable as secondary mode |
| disp_20260702_000183 | generic-preflight | Checkpoint filename consistency (.dev/*-preflight-checkpoint.md) | Document and verify consistency across /plan and /review-develop callers |
| disp_20260702_000184 | ticket.md | --research-reply (frontmatter) vs --mode=full (body) mismatch | Harmonize to canonical flag name |
| disp_20260702_000187 | fix.md | Compile-failure rule duplicated at lines 159–161, 289–304, 334–337 | Consolidate to one location (-30 to -50 lines) |
| disp_20260702_000188 | bc-research | Frontmatter name "research" mismatches parent dir bc-research | Fix name to bc-research in frontmatter |
| disp_20260702_000189 | commit-preflight.md | Line 158 header "NEW MANDATORY GATE" is temporal marker | Rewrite header to describe function not timeline |
| disp_20260702_000190 | document.md | Hardcoded path ~/al-dev-shared/ at line 104 | Use $AL_DEV_SHARED_PLUGIN_ROOT env var (consistent with interview/SKILL.md:136) |
| disp_20260702_000192 | generic-preflight | Name doesn't signal narrow scope to /plan, /review-develop | Already documented; no action needed |
| disp_20260702_000194 | ticket.md | Phase 0.5 gate before Phase 1 ticket resolution and Phase 3 fetch | Move to post-fetch (Phase 2.5) |
| disp_20260702_000195 | plan-with-critics.md | Description correctly foregrounds six parallel critics | Already accurate; no action needed |

### MODIFY — 4 verified with narrower scope after rubber-duck

| Event ID | Object | Finding | Corrected Scope |
|----------|--------|---------|-----------------|
| disp_20260702_000104 | support-reply-drafter.md | "Critical reading" uses vague language | Issue is incomplete tools list (AL MCP, LSP, MS Docs, BC Code History); extend tools |
| disp_20260702_000113 | findings-synthesizer.md | Generic name | Rename to evidence-synthesizer OR update description to clarify evidence input→findings output |
| disp_20260702_000132 | commit-recover.md | Description says log "always present", Step 1 says "may be absent" | Update description to clarify .dev/commit-integrity.log is optional |
| disp_20260702_000133 | develop-orchestrate.md | Description subordinates review-handoff to dispatch | Reweight description to highlight 3-step handoff choreography (preflight, validation, dispatch) |

## Implementation Constraints

### Global Scope
- All changes to `profile-al-dev-shared/` must maintain harness neutrality (generic vocabulary per knowledge/harness-concepts.md)
- No agent/skill file renames in this phase (frontmatter name changes only)
- No projection regeneration needed (quality/naming changes don't alter body content)
- No new dependencies or structural changes

### Verification Patterns (Per Correction Patterns Doc)

| Task Type | Verification | Command |
|-----------|--------------|---------|
| Add tool | Tool declared in frontmatter + grep-bounded | `grep -n 'tools:' <file>` and `grep -A5 'tools:' <file>` |
| Rename tool/agent | Old name absent, new name present | `grep -qF 'old_name' <file> && exit 1; grep -qF 'new_name' <file>` |
| Update description | New text present, old text absent | `grep -qF 'new phrase' <file> && ! grep -qF 'old phrase' <file>` |
| Consolidate duplication | Source folded, duplicates removed | `wc -l <file>` and `grep -c 'duplicate phrase' <file>` |
| Environment variable | Hardcoded path replaced with `$VAR` | `grep -qF '$AL_DEV_SHARED_PLUGIN_ROOT' <file> && ! grep -qF '~/al-dev-shared/' <file>` |
| Gate reorder | Phase moved to correct position | `grep -n 'Phase' <file>` and verify sequence |

### Commit Format

Every task commits with:
```
<emoji> type(scope): subject
```
- Subject ≤72 characters (tool project: subject-only, no body)
- Emoji from canonical table: 🐛 fix, 🚚 move/rename, 📦 chore
- Scope from component name (e.g., `fix(explore)`, `chore(ticket)`)

Example: `🐛 fix(explore): add Bash to tools list`

### Event ID Closure

Each task's verification block must include:
```yaml
closes_event_ids:
  - disp_20260702_000XXX
  - disp_20260702_000YYY
```

Special cases (informational tasks with no implementation work):
```yaml
closes_event_ids: []
```

## Task Breakdown

**16 actionable tasks** (grouped by component):

1. explore.md → add Bash tool (closes_event_ids: [000103])
2. explore.md → rename to codebase-explorer (closes_event_ids: [000114])
3. evidence-gatherer.md → add MCP tools (closes_event_ids: [000109])
4. support-reply-drafter.md → add AL MCP/LSP/MS Docs/BC Code History (closes_event_ids: [000104])
5. release-notes-writer.md → update description for orchestrator role (closes_event_ids: [000112])
6. bc-research → fix frontmatter name (closes_event_ids: [000188])
7. findings-synthesizer.md → rename to evidence-synthesizer (closes_event_ids: [000113])
8. commit-recover.md → update description (optional log) (closes_event_ids: [000132])
9. develop-orchestrate.md → reweight description (handoff emphasis) (closes_event_ids: [000133])
10. commit-preflight.md → rewrite line 158 header (closes_event_ids: [000189])
11. ticket.md → harmonize flag names (--research-reply to --mode=full) (closes_event_ids: [000184])
12. ticket.md → move gate to post-fetch (Phase 0.5 to Phase 2.5) (closes_event_ids: [000194])
13. document.md → replace hardcoded path with env var (closes_event_ids: [000190])
14. fix.md → consolidate compile-failure rule (closes_event_ids: [000187])
15. generic-preflight.md → document checkpoint filename consistency (closes_event_ids: [000183])
16. Validation gate: harness neutrality + shared-surface validators (closes_event_ids: [])

**2 informational tasks** (no implementation work):

- Task 17: Record disp_20260702_000192 (generic-preflight name) as informational; description adequately documents scope (closes_event_ids: [])
- Task 18: Record disp_20260702_000195 (plan-with-critics) as verified & accurate; no action needed (closes_event_ids: [])

## Acceptance Criteria

✓ All 18 event IDs explicitly mapped to tasks  
✓ 16 actionable tasks + 2 informational tasks  
✓ All edits target `profile-al-dev-shared/` (harness-neutral shared layer)  
✓ Commits follow canonical format (subject ≤72 chars, subject-only)  
✓ Verification steps bind to task-specific outcomes (not pre-existing matches)  
✓ No projection regen (quality/naming changes only, body untouched)  
✓ Shared-surface validators pass (harness neutrality confirmed)

---

Write implementation plan with 18 tasks (16 actionable + 2 informational). Suppress writing-plans Execution Handoff; hand off to `/implement-plugin-health` instead.
