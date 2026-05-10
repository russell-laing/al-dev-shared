# Workflow Resilience

Protocols for multi-phase skills (`al-dev-plan`,
`al-dev-develop`) to survive usage limits and resume cleanly.

## Progress Checkpointing

### Write Protocol

Ensure `.dev/` exists before writing:

```bash
mkdir -p .dev
```

After each named phase boundary, overwrite
`.dev/progress.md` with:

```markdown
## Progress Checkpoint

**Completed phases:** Phase 1 — Read Context, Phase 3 — Architect Debate

**Current state:** [1-2 sentences]

**Next step:** [exact next action]

**Pending decisions:** [list, or "none"]
```

Latest state always wins — overwrite, never append.
Write the checkpoint before spawning subagents for the next
phase and again after collecting their output.

### Read Protocol (Phase 0)

At skill startup, before Phase 1, read `.dev/progress.md`
if it exists. If the file exists, display its contents and ask:
*"Resume from checkpoint? (yes / restart)"*

- **yes** — skip completed phases, start from the recorded
  next step
- **restart** — delete `.dev/progress.md` and start fresh

If no file exists, proceed to Phase 1 normally.

## Subagent Fallback

If an agent returns empty output or hits a usage limit:

1. Use any partial output the agent returned before failing
2. If no output at all, synthesize from the relevant plan
   document:
   - For develop phases: `.dev/02-solution-plan.md`
   - For plan phases: `.dev/01-requirements.md`
3. Log the fallback in `.dev/progress.md` under
   **Pending decisions**: `"Phase X synthesized directly
   (agent hit limit)"`
4. For plan/develop waves, prefer single-agent execution if
   a parallel wave has already failed once
