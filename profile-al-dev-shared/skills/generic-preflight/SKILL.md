---
name: generic-preflight
description: >-
  Parameterized preflight skill for plan and review phases. Handles resume
  logic, context gathering, and state checkpointing for both /plan and
  /review-develop flows via context-type argument.
argument-hint: "[context-type: planning|review]"
---

# Generic Preflight Skill

Shared Phase 0 resume-check + context-gathering logic for the planning and
review preflight flows — invoked as `/generic-preflight --context-type planning`
or `/generic-preflight --context-type review`. Reduces duplication by
parameterizing the context type.

## Phase 0: Resume Check & Initialization

Check `.dev/<context-type>-preflight-checkpoint.md` for resume capability.

If exists, read checkpoint and present resume option:

```text
Resume previous work on [context]? Run:
  /generic-preflight --resume --context-type <type>

```

If not exists, proceed to Phase 1 (context gathering).

## Phase 1: Gather Project Context

- [ ] Check for `.dev/project-context.md`

```bash
if [ -f .dev/project-context.md ]; then
    echo "Project context found"
else
    echo "ERROR: .dev/project-context.md missing"
    exit 1
fi
```

- [ ] Extract project type (AL/Python/etc) from context

```bash
grep -o "project_type: [^,]*" .dev/project-context.md
```

## Phase 2: Validate Environment

- [ ] Confirm required tools installed

```bash
for tool in git jq grep; do
    command -v $tool >/dev/null 2>&1 || { echo "ERROR: $tool not found"; exit 1; }
done
```

- [ ] Check git remotes

```bash
git remote -v | grep -q origin || { echo "ERROR: no origin remote"; exit 1; }
```

## Phase 3: Emit Preflight Checkpoint

Write `.dev/<context-type>-preflight-checkpoint.md` with:

- Timestamp
- Context file path
- Ready/blocked status
- Next command (downstream skill to invoke)

## Implementation Notes

This skill is invoked by:

- `/plan` (context-type: planning)
- `/review-develop` (context-type: review)

Each caller receives the context in their expected output file. The skill handles
both paths via the `context-type` argument.
