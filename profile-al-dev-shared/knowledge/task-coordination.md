# Task Coordination System

**Version:** 2.15.0

This profile uses Claude Code's native **Tasks** system for workflow coordination, persistence, and multi-agent collaboration.

## Overview

Tasks replace the previous `.dev/workflow-state.json` approach with native capabilities:

- **Persistence:** Tasks stored in `~/.claude/tasks/` survive session restarts
- **Dependencies:** Tasks can block/be blocked by other tasks
- **Multi-agent:** Subagents share the same task list via `CLAUDE_CODE_TASK_LIST_ID`
- **Broadcasting:** Updates sync across all sessions working on the same list

## Task Structure for AL Development

### Full Development Cycle Tasks

```
Task: "[Feature Name] - Full Development Cycle"
├── Task: Requirements Analysis
│   ├── Status: pending → in_progress → completed
│   ├── Output: .dev/01-requirements.md
│   └── Blocks: Solution Planning
│
├── Task: Solution Planning
│   ├── Status: pending (blocked)
│   ├── Blocked By: Requirements Analysis
│   ├── Output: .dev/02-solution-plan.md
│   └── Blocks: Development
│
├── Task: Development
│   ├── Status: pending (blocked)
│   ├── Blocked By: Solution Planning
│   ├── Output: AL source files
│   └── Blocks: Code Review
│
├── Task: Code Review
│   ├── Status: pending (blocked)
│   ├── Blocked By: Development
│   ├── Output: .dev/03-code-review.md
│   └── Blocks: Diagnostics (if passed)
│
├── Task: Diagnostics
│   ├── Status: pending (blocked)
│   ├── Blocked By: Code Review
│   ├── Output: .dev/04-diagnostics.md
│   └── Blocks: Testing
│
├── Task: Testing
│   ├── Status: pending (blocked)
│   ├── Blocked By: Diagnostics
│   ├── Output: .dev/05-test-plan.md
│   └── Blocks: Test Review
│
├── Task: Test Review
│   ├── Status: pending (blocked)
│   ├── Blocked By: Testing
│   ├── Output: .dev/06-test-review.md
│   └── Blocks: Documentation
│
└── Task: Documentation
    ├── Status: pending (blocked)
    ├── Blocked By: Test Review
    └── Output: docs/ or wiki/
```

### Lightweight Workflow Tasks (SIMPLE)

```
Task: "[Feature Name] - Quick Implementation"
├── Task: Planning (lightweight)
│   └── Blocks: Development
├── Task: Development
│   └── Blocks: Review
└── Task: Code Review
```

## How to Use Tasks

### Creating Tasks at Workflow Start

When starting `/dev-cycle`, create the task structure:

```
TaskCreate: "Requirements Analysis"
  - description: "Extract requirements from user request"
  - activeForm: "Analyzing requirements"

TaskCreate: "Solution Planning"
  - description: "Design architecture and implementation plan"
  - activeForm: "Designing solution"

TaskUpdate: "Solution Planning"
  - addBlockedBy: ["Requirements Analysis"]

... (continue for all phases)
```

### Subagent Task Updates

Each spawned agent updates its assigned task:

**When agent starts:**
```
TaskUpdate: taskId
  - status: "in_progress"
  - owner: "[agent-name]"
```

**When agent completes:**
```
TaskUpdate: taskId
  - status: "completed"
```

### Checking Task Status

Before spawning an agent, check if its task is unblocked:

```
TaskList → Find task for current phase
  - If blockedBy is empty or all blockers completed → Can proceed
  - If still blocked → Wait or show status to user
```

### Multi-Session Coordination

To resume work or coordinate parallel agents:

```bash
# Get task list ID from first session
TaskList → Note the list ID

# In new session or for subagent
CLAUDE_CODE_TASK_LIST_ID=<list-id> claude
```

Or set in agent spawn environment.

## Integration with Approval Gates

Tasks track approvals via metadata:

```
TaskUpdate: "Solution Planning"
  - status: "completed"
  - metadata: { "approved": true, "approved_at": "2026-01-23T10:30:00Z" }
```

Before starting blocked task, check approval:

```
TaskGet: "Solution Planning"
  - Check metadata.approved == true
  - If not approved, prompt user
```

## Task States

| Status | Meaning |
|--------|---------|
| `pending` | Not started, may be blocked |
| `in_progress` | Agent currently working |
| `completed` | Finished successfully |

## Dependency Rules

1. **Requirements** → No blockers (can always start)
2. **Planning** → Blocked by Requirements
3. **Development** → Blocked by Planning (and Planning must be approved)
4. **Code Review** → Blocked by Development
5. **Diagnostics** → Blocked by Code Review (only if review passed)
6. **Testing** → Blocked by Diagnostics
7. **Test Review** → Blocked by Testing
8. **Documentation** → Blocked by Test Review

## Iteration Handling

When code-reviewer finds Critical/High issues:

```
TaskUpdate: "Code Review"
  - status: "completed"
  - metadata: { "passed": false, "issues": 3, "severity": "high" }

TaskUpdate: "Development"
  - status: "pending"  # Reset for re-work
  - Remove from blockedBy of Code Review

# Re-run development, then re-run code review
```

## Agent Implementation

### Agent Workflow with Tasks

```markdown
## Workflow

1. **Check assigned task**
   - TaskGet: Get task details
   - Verify not blocked (blockedBy should be empty or all completed)

2. **Start work**
   - TaskUpdate: status = "in_progress", owner = "agent-name"

3. **Do work**
   - Read inputs, perform agent function, write outputs

4. **Complete**
   - TaskUpdate: status = "completed"
   - Add relevant metadata (output file, findings, etc.)
```

### Example: al-developer with Tasks

```markdown
## Workflow

1. **Get task**
   - TaskGet: Development task
   - Verify Planning task is completed AND approved

2. **Start**
   - TaskUpdate: status = "in_progress", owner = "al-developer"

3. **Implement**
   - Read project-context.md
   - Read 02-solution-plan.md
   - Write AL code
   - Run al-compile

4. **Complete**
   - TaskUpdate: status = "completed"
   - metadata: { files_created: [...], compile_result: "success" }
```

## Benefits Over Previous Approach

| Previous (.dev/workflow-state.json) | New (Tasks) |
|-------------------------------------|-------------|
| Manual JSON file management | Native tool support |
| No persistence across sessions | Persisted in ~/.claude/tasks |
| No dependency enforcement | Built-in dependency tracking |
| Single-session only | Multi-session coordination |
| Manual state checking | TaskList shows blockers |
| No broadcasting | Updates sync across sessions |

## Viewing Tasks

```bash
# In Claude Code
/tasks              # View all tasks

# Or use TaskList tool
TaskList            # Returns all tasks with status and blockers
```

## Environment Variables

```bash
# Share task list across sessions
CLAUDE_CODE_TASK_LIST_ID=<id> claude

# Disable if not needed
CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=true
```

## Migration from workflow-state.json

If you have existing `.dev/workflow-state.json`:

1. Read current state
2. Create equivalent Tasks with proper dependencies
3. Set task statuses to match workflow state
4. Delete workflow-state.json (optional, Tasks are now source of truth)

---

**Key Principle:** Tasks are the coordination layer. Agents check task status before starting, update status as they work, and respect dependency chains. This enables reliable multi-phase workflows with persistence and multi-agent coordination.
