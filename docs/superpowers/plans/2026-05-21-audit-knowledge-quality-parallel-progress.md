# Plan: Add Parallel Exploration and Progress Tracking to audit-knowledge-quality

## Context

The skill at `.claude/skills/audit-knowledge-quality/SKILL.md` analyzes flagged knowledge files sequentially in Phase 2. It currently processes each of N files through a multi-step checklist:

1. Read the file
2. Read the referencing agent/skill  
3. Understand the gap (THIN/NO-CODE/DEAD-REF classification)
4. Assess severity (HIGH/MEDIUM/LOW)

For typical runs (5-15 flagged files), this sequential reading inside the main context works. But for larger audits (20+ files), two gaps emerge:

1. **No parallel file discovery** — Phase 2 reads files sequentially inside main context. When files are independent (different knowledge topics, different referencing agents), these reads can be parallelized via Explore subagents.

2. **No progress tracking** — Phase 2 processes N files with a 4-step checklist each. Nothing instructs the agent to create todos, so multi-file runs have no checkpoint structure. A missed file or skipped step is invisible.

## What Changes

### Change 1: Progress tracking via TodoWrite

Add an instruction at the top of Phase 2:

> Before analyzing any file, create one TodoWrite todo per flagged file named `[issue-type] [filename]`. Mark each todo in-progress when analysis begins, complete when the file analysis is written to findings.

This gives a visible checkpoint list without changing the analysis output format.

### Change 2: Parallel dispatch gate

Add an instruction after the TodoWrite instruction:

> When 4+ files are flagged, invoke `superpowers:dispatching-parallel-agents` before starting sequential analysis. Dispatch one Explore subagent per file to: read the knowledge file, search for referencing agent/skill, and run the gap/severity assessment (steps 1–4). Each agent returns a structured analysis record. Collect all records before proceeding to Phase 3.
>
> For ≤3 flagged files (or files with ordering dependencies), the sequential inline path is fine — keep it as the fallback.

## Files to Modify

Single file: `.claude/skills/audit-knowledge-quality/SKILL.md`

- Add ~4 lines at the start of Phase 2 (TodoWrite instruction)
- Add ~8 lines after TodoWrite instruction, before step 1 (parallel dispatch gate)
- No changes to Phase 1, Phase 3, or Phase 4

## Verification

1. Confirm file was edited: `wc -l` shows line count increased by ~12 lines
2. Confirm no forbidden patterns:
   ```bash
   grep -E '\[date\]|TODO|TBD|YYYY-MM-DD' .claude/skills/audit-knowledge-quality/SKILL.md
   ```
   Expect no output (YYYY-MM-DD is not used in this skill).
3. Manual trace: read Phase 2 and confirm:
   - TodoWrite instruction appears before step 1
   - Parallel-dispatch gate appears between TodoWrite and step 1
   - Phase 3 structure is intact
