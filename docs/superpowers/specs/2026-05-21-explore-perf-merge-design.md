# Design Spec: Merge /al-dev-explore + /al-dev-perf

**Status:** Draft — run /al-dev-plan after approving this design to generate the implementation plan
**Date:** 2026-05-21
**Source:** docs/al-dev-plugin-map.md — Architectural suggestions > Merge

---

## Problem Statement

Both /al-dev-explore and /al-dev-perf spawn a single Explore subagent and write a dated `.dev/`
output file. The plugin map suggests merging into a unified skill with a mode flag. However,
rubber-ducking found 4 structural differences that must be explicitly resolved in this design.

## Structural Differences (verified by rubber-ducking)

| Aspect | /al-dev-explore | /al-dev-perf |
|--------|-----------------|--------------|
| Pre-spawn MCP step | None | Step 1a: al_get_object_summary + al_search_object_members classify each codeunit |
| Spawn prompt template | General codebase exploration with Glob + Grep + Read pattern | Performance anti-pattern analysis with severity escalation rules |
| Anti-patterns reference | None | Reads knowledge/perf-anti-patterns-prompt.md and pastes full content into spawn prompt |
| Output filename | *-al-dev-explore-findings.md | *-al-dev-perf-perf-analysis.md |
| Context integration | Step 4: offers to update project-context.md | None |

## Proposed Unified Interface

```
/al-dev-explore [question]       # general mode (default)
/al-dev-explore --perf [scope]   # performance mode
/al-dev-explore --perf scan all  # performance scan, all codeunits
```

Flag: `--perf` (boolean) — avoids collision with the existing file/directory scope argument
that /al-dev-perf already uses.

## Step Mapping

| Step | General mode | Performance mode (--perf) |
|------|-------------|--------------------------|
| Step 0 | — | MCP classification: al_get_object_summary + al_search_object_members for each codeunit |
| Step 1 | Load context (project-context.md, ticket context) | Determine scope (codeunit files) |
| Step 2 | Spawn Explore subagent with general prompt | Spawn Explore subagent with perf prompt + classification + anti-patterns content |
| Step 3 | Write findings | Write perf analysis |
| Step 4 | Context integration (offer project-context.md update) | Present result + suggest /al-dev-plan |

## Output Filenames

- General mode: `.dev/$(date +%Y-%m-%d)-al-dev-explore-findings.md`  
- Performance mode: `.dev/$(date +%Y-%m-%d)-al-dev-perf-perf-analysis.md`

Performance mode preserves the existing filename so that the Connect wiring added in
docs/superpowers/plans/2026-05-21-plugin-map-improvements.md Task 7 continues to work without
changes. The glob pattern `*-al-dev-perf-perf-analysis.md` in /al-dev-plan and /al-dev-fix
remains valid.

## Spawn Prompt Templates

### General mode prompt

From al-dev-explore/SKILL.md Step 2:

```text
Spawn an explore agent:
  purpose: Explore [user's question]
  prompt: [user's question in full]
  output: structured findings summary

Prompt:
  "Answer this question about the codebase: [USER_QUESTION]

   Project context (if available):
   [Paste relevant sections from project-context.md — directory structure,
   key objects, architectural patterns]

   Requirements:
   1. Use Glob to find candidate files first, then Read selectively
   2. Use Grep for pattern searches (event subscribers, field usage, etc.)
   3. Do NOT read entire files unless the question requires full context
   4. Provide concrete, specific answers with file paths and line numbers

   Structure your findings as:

   ANSWER: Direct answer to the question (2-5 sentences)

   FILES:
   - path/to/file.al — one-line description of relevance

   SNIPPETS:
   [Max 3 key code excerpts, kept brief]

   CONNECTIONS:
   [How the discovered pieces relate to each other]

   GAPS:
   [What could not be determined from the code alone, if any]"
```

### Performance mode prompt

From al-dev-perf/SKILL.md Step 2:

```text
Spawn an explore agent:
  purpose: Perf scan: [scope description]
  prompt: [performance analysis prompt]
  output: performance findings with file:line references

Prompt:
  "Scan these AL codeunit files for performance anti-patterns.
   Read each file fully, then report ALL findings.

   Files to analyse: [file paths from Step 1]

   Codeunit classifications (from AL Symbols pre-research):
   [paste the classification summary from Step 1a]

   Severity escalation rule: For any P1–P8 finding in a codeunit
   classified as Entry Point, Hot Path, or Batch Processor — escalate
   its severity by one level (LOW→MEDIUM, MEDIUM→HIGH, HIGH→CRITICAL).
   Reflect this in the SEVERITY field and explain it in the IMPACT field.

   Anti-patterns to find and 'Do NOT flag' exclusions: See `knowledge/perf-anti-patterns-prompt.md`. Paste the full content of that file here before dispatching.

   For EACH finding report:
   PATTERN: [P1–P8 ID]
   SEVERITY: CRITICAL | HIGH | MEDIUM | LOW
   FILE: [exact path]
   LINE: [line number]
   CODE: [3–5 lines of the problematic code]
   FIX: [3–5 lines of the corrected version]
   IMPACT: [estimated frequency — per record, per batch, etc.]"
```

The performance mode prompt MUST include the full content of `knowledge/perf-anti-patterns-prompt.md` before dispatch, as documented in al-dev-perf/SKILL.md line 98.

## Files to Change (when this design is approved)

- Modify `profile-al-dev-shared/skills/al-dev-explore/SKILL.md` — add --perf mode and conditional branching logic
- Delete `profile-al-dev-shared/skills/al-dev-perf/SKILL.md`
- Update `docs/al-dev-plugin-map.md` — remove /al-dev-perf from Layer 1 tributary and Layer 2

## Classification Metadata (Step 1a only in perf mode)

From al-dev-perf/SKILL.md Step 1a, the MCP classification step applies only when `--perf` flag is set:

| Indicator | Classification | Severity modifier |
| --- | --- | --- |
| Has `OnRun()` | Entry Point | +1 level |
| Has `[EventSubscriber]` attribute | Hot Path | +1 level |
| Name contains Batch/Process/Import/Post/Transfer/Run | Batch Processor | +1 level |
| None of the above | Utility | none |

If al-mcp-server is unavailable or returns no result for a codeunit, default to Utility (no modifier).

## Open Questions

1. **Should Step 4 (context integration) run in performance mode?** Recommendation: No — current
   /al-dev-perf does not do context integration; keep behaviour consistent. General mode offers context update; perf mode suggests /al-dev-plan for fixes.

2. **Should the anti-patterns file be embedded in the unified skill or always read at runtime?** Recommendation: keep as a runtime read (`knowledge/perf-anti-patterns-prompt.md`) so the
   anti-patterns can be updated without changing the skill itself.

3. **How should the unified skill name be documented in help/usage?** Recommendation: update the skill description to mention both modes: "Explore codebases fast, or analyze performance with --perf mode."

## Implementation Order

1. Modify `/al-dev-explore/SKILL.md` to add conditional Steps 0 and branching in Steps 1–4
2. Delete `/al-dev-perf/SKILL.md` (file removal)
3. Update `docs/al-dev-plugin-map.md` to remove /al-dev-perf and note the mode in /al-dev-explore
4. Verify all Connect wiring in `/al-dev-plan` and `/al-dev-fix` that references `*-al-dev-perf-perf-analysis.md` still works
