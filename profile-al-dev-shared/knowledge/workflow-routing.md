# Workflow Routing: Smart Path Selection

**Purpose:** Route requests to the appropriate workflow based on complexity. Prevents overkill for simple changes.

## CRITICAL: Read Project Context First

**BEFORE making any workflow decision, ALWAYS:**
```
1. Check if .dev/project-context.md exists
2. If exists: Read it completely (saves 5-10 minutes of exploration)
3. If not exists: Create it during first workflow run
```

## Complexity Classification

Analyze the user request and classify:

### 🟢 TRIVIAL (Use Fast Path - 2-5 min)
**Route:** `/al-dev-fix` workflow (no planning, no testing)

**Criteria:**
- Single file modification
- Obvious fix location
- No architectural decisions
- Clear implementation

**Examples:**
- "Fix compilation error in line 47"
- "Change field caption from X to Y"
- "Add field to page extension"
- "Fix typo in error message"
- "Update variable name for consistency"

**Steps:**
1. Read project-context.md
2. Locate file (use context, minimal search)
3. Make change
4. Run al-compile
5. Done (skip all agents)

**Time saved:** 15-25 minutes vs full workflow

---

### 🟡 SIMPLE (Use Lightweight Path - 5-15 min)
**Route:** Lightweight planning + implementation with code-reviewer only

**Criteria:**
- 2-3 file changes
- Pattern exists in project
- Clear requirements
- No new architecture

**Examples:**
- "Add validation field to Customer extension"
- "Extend existing event subscriber with new check"
- "Add similar field to another page"
- "Implement validation like we did for X"

**Steps:**
1. Read project-context.md
2. requirements-engineer → brief plan (50-75 lines max)
3. solution-planner → lightweight plan (50-100 lines max)
   - SKIP MCP tools - use project context only
4. User approval (quick review)
5. al-developer → implement
6. code-reviewer → quick review
7. al-compile
8. Update project-context.md if learned something
9. Done

**Agents used:** requirements-engineer (brief), solution-planner (lightweight), al-developer, code-reviewer
**Planning style:** See `knowledge/proportional-planning.md` - SIMPLE guidelines (100-150 lines total)
**Phases skipped:** testing (unless critical)
**Time saved:** 10-20 minutes vs full workflow

---

### 🟠 MEDIUM (Use Streamlined Path - 20-40 min)
**Route:** Balanced planning + Development

**Criteria:**
- 4-8 file changes
- Multiple objects involved
- Some design decisions needed
- Extends existing patterns

**Examples:**
- "Add credit limit warning on sales orders"
- "Implement cascading field update across extensions"
- "Add new validation with 3 error conditions"

**Steps:**
1. Read project-context.md
2. requirements-engineer → balanced requirements (100-150 lines)
3. solution-planner → balanced plan (100-300 lines)
   - USE MCP tools: get_table_structure, list_events, ask_bc_expert as needed
4. User approval
5. al-developer → implement
6. code-reviewer + diagnostics-fixer
7. Update project-context.md
8. Done

**Agents used:** requirements-engineer (balanced), solution-planner (balanced), al-developer, code-reviewer, diagnostics-fixer
**Planning style:** See `knowledge/proportional-planning.md` - MEDIUM guidelines (200-400 lines total)
**Phases skipped:** test-engineer (unless critical)
**Time saved:** 10-15 minutes vs full workflow

**When to add testing:**
- User explicitly requests tests
- Business-critical logic
- Complex validation rules

---

### 🔴 COMPLEX (Use Full Pipeline - 45-90 min)
**Route:** `/al-dev-dev-cycle` full workflow

**Criteria:**
- New feature (not extension of existing)
- Multiple integration points
- Unclear requirements need clarification
- Architectural decisions needed
- New patterns not in codebase

**Examples:**
- "Add approval workflow system"
- "Integrate with external API"
- "Implement new posting routine"
- "Add complex multi-table validation logic"

**Steps:**
1. Read project-context.md (still helps!)
2. requirements-engineer → comprehensive (150-300 lines)
3. solution-planner → comprehensive (300-600 lines)
   - EXTENSIVE MCP usage: explore base app, consult experts, research patterns
4. Approval gate
5. al-developer
6. code-reviewer + iterations
7. diagnostics-fixer
8. test-engineer
9. test-reviewer
10. Update project-context.md extensively
11. Done

**Agents used:** All
**Planning style:** See `knowledge/proportional-planning.md` - COMPLEX guidelines (400-800 lines total)
**Phases:** All
**Time saved:** None, but thoroughness justified by complexity

---

## Decision Tree

```
User Request
    ↓
Does .dev/project-context.md exist?
    ↓ NO → Create it during workflow (first-time cost)
    ↓ YES → Read it first (saves 5-10 min)
    ↓
Classify request:
    ↓
Is it single file + obvious?
    ↓ YES → 🟢 TRIVIAL: Direct fix (2-5 min)
    ↓ NO
    ↓
Is pattern in codebase + <4 files?
    ↓ YES → 🟡 SIMPLE: Direct implementation + review (5-15 min)
    ↓ NO
    ↓
Clear requirements + extends existing?
    ↓ YES → 🟠 MEDIUM: Plan + develop (20-40 min)
    ↓ NO
    ↓
    └──→ 🔴 COMPLEX: Full pipeline (45-90 min)
```

## Example Classifications

### User: "Add IsBlocked field to Customer extension"
**Classification:** 🟡 SIMPLE
**Reason:** Pattern exists (table extension), single concept, 2 files (table + page)
**Route:** Direct implementation + code-reviewer
**Skip:** requirements, solution plan, testing

### User: "Fix error AL0432 in SalesOrderValidation.al line 87"
**Classification:** 🟢 TRIVIAL
**Reason:** Specific location, compilation error, obvious fix
**Route:** Direct fix + compile
**Skip:** All agents

### User: "Add credit limit validation when posting sales orders with warning threshold"
**Classification:** 🟠 MEDIUM
**Reason:** Multiple files (event subscriber, validation logic, UI), design decisions (threshold logic), extends existing validation
**Route:** solution-planner → al-developer → review → diagnostics
**Skip:** requirements-engineer, testing (unless critical)

### User: "Implement multi-level approval workflow for purchase orders with email notifications"
**Classification:** 🔴 COMPLEX
**Reason:** New architectural component, external integration (email), multiple tables, unclear approval logic
**Route:** Full pipeline with all agents

## Runtime Optimization Rules

### For All Workflows

1. **Project context first:** Always read `.dev/project-context.md` before exploration
2. **Minimal search:** Use context to narrow search scope by 80%
3. **Parallel agents:** solution-planner spawns support agents in parallel (see below)
4. **Incremental updates:** Update project-context.md as you learn, not just at end

### Parallel Agent Execution (MEDIUM/COMPLEX only)

When solution-planner runs, spawn these IN PARALLEL:

```
Task 1: docs-lookup → Research official patterns
Task 2: dependency-navigator → Explore base app
Task 3: bc-expert → Get architecture advice

Wait for all three (takes max time, not sum of times)
Then: Synthesize results into solution plan
```

**Time saved:** 5-10 minutes (sequential would be 15-20 min, parallel is 5-8 min)

### When to Update Project Context

**Always update after:**
- Discovering new architectural patterns
- Adding new objects (tables, pages, codeunits)
- Learning base app integration points
- Establishing new validation patterns

**Quick updates (append only):**
```markdown
## Recent Changes Log

### 2026-01-22 14:30 - al-developer
- Added: Table Ext 50105 "Customer Credit Ext" (CreditLimit, LastReviewDate)
- Added: Codeunit 50102 "Credit Validation Mgt" (CheckCreditLimit(), ValidateThreshold())
- Pattern: Validation in dedicated codeunit, called from event subscriber
```

## Override Mechanism

User can force a specific path:

- `/al-dev-fix` → Always TRIVIAL path
- `/al-dev-develop` → SIMPLE/MEDIUM path (no requirements phase)
- `/al-dev-plan` → MEDIUM path (planning only)
- `/al-dev-dev-cycle` → COMPLEX path (full pipeline)

But AI should suggest if path seems wrong:
```
"This looks like a simple field addition. Would you like to use the fast path instead?
(Direct implementation + review, saves 15-20 minutes)"

[Quick Fix] [Standard Workflow]
```

## Success Metrics

Track actual vs estimated complexity:
- If TRIVIAL took >10 min → should have been SIMPLE
- If MEDIUM took >50 min → should have been COMPLEX
- Learn and adjust classification

Store in `.dev/workflow-metrics.json`:
```json
{
  "classifications": {
    "trivial_correct": 23,
    "trivial_too_simple": 2,
    "medium_correct": 15,
    "medium_too_complex": 3
  }
}
```

Over time, improve classification accuracy.

---

**Key Principle:** Respect user's time. Match tool to task. Project context + smart routing = 40-60% runtime reduction for most changes.
