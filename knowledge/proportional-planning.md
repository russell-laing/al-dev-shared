# Proportional Planning Guidelines

**Core Principle:** Planning detail must match implementation complexity. Simple changes need concise plans, complex features need comprehensive documentation.

## Planning Output Targets by Complexity

### 🟢 TRIVIAL (Skip Planning)
- No planning documents
- Direct fix + compile

---

### 🟡 SIMPLE (Lightweight Planning)

**Characteristics:**
- Extends existing patterns
- 2-3 files
- Clear implementation path
- Examples: Add field to extension, simple validation, UI field addition

**Planning Target: 100-150 lines total**

**⚠️ CRITICAL: NO COMPLETE CODE IN PLANNING**

Solution plans describe WHAT to build and WHY, not HOW (code). Code is written by al-developer during implementation.

#### Requirements (50-75 lines)
```markdown
# Requirements: [Feature Name]

## What We're Doing
[2-3 sentence summary of the change]

## Files to Change
1. [File 1] - [What changes]
2. [File 2] - [What changes]
3. [File 3] - [What changes]

## Functional Requirements
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

## Non-Functional
- Performance: [Any concerns?]
- Compatibility: [BC version]
- Permissions: [What's needed]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]
```

**DON'T:**
- Write user stories (overkill)
- Create detailed acceptance criteria
- List edge cases extensively
- Add multiple NFR sections

#### Solution Plan (50-75 lines)
```markdown
# Solution Plan: [Feature Name]

## Approach
[2-3 sentences describing the solution]

## Implementation

### File 1: [Name]
**Purpose:** [One line]
**Changes:**
- Add field X (Boolean)
- Add field Y (Code[20])

### File 2: [Name]
**Purpose:** [One line]
**Changes:**
- Add control for field X
- Add control for field Y

### File 3: [Name]
**Purpose:** [One line]
**Changes:**
- Add IF check for field X
- Call validation procedure

## Implementation Order
1. File 1 (no dependencies)
2. File 2 (depends on File 1)
3. File 3 (depends on File 1)

## Testing
- Test scenario 1
- Test scenario 2
```

**DO:**
- List fields/procedures by name and type
- Describe what changes, not show code

**DON'T:**
- Write complete AL code (field definitions, triggers, procedures)
- Create ASCII diagrams (visual overkill)
- Write "Design Rationale" section
- List alternatives considered
- Include "Potential Issues" section
- Create detailed object allocation tables

**Remember: al-developer writes the code, not solution-planner.**

---

### 🟠 MEDIUM (Balanced Planning)

**Characteristics:**
- Some design decisions needed
- 4-8 files
- Multiple integration points
- Examples: Multi-file validation, event subscribers, moderate business logic

**Planning Target: 200-400 lines total**

**⚠️ CRITICAL: DESCRIBE CODE, DON'T WRITE IT**

Solution plans explain WHAT fields/procedures are needed and WHY, not the complete AL implementation.

#### Requirements (100-150 lines)
- Brief summary
- Functional requirements (5-8 items)
- Key non-functionals (3-4 items)
- Integration points
- Success criteria

**Include:** Core requirements, integration points
**Omit:** Detailed acceptance criteria, extensive user stories

#### Solution Plan (100-250 lines)
- High-level approach (1 paragraph)
- Architecture overview (text, no ASCII art unless truly helpful)
- Implementation per file:
  - Purpose
  - Key fields/procedures BY NAME (not full code)
  - Integration points
- Implementation sequence
- Testing approach

**DO:**
- List field names, types, purpose
- List procedure names, parameters, purpose
- Describe validation logic in plain English

**DON'T:**
- Write complete table definitions with all field properties
- Write complete procedure implementations
- Write triggers with full code logic
- Show more than 5-10 lines of code per object

**Remember: al-developer writes the AL code during implementation.**

---

### 🔴 COMPLEX (Comprehensive Planning)

**Characteristics:**
- New architecture/patterns
- 9+ files
- Unclear requirements need exploration
- Examples: Approval workflows, API integrations, new posting routines

**Planning Target: 400-800 lines total**

**⚠️ CRITICAL: ARCHITECTURAL DOCUMENTATION, NOT CODE**

Even complex features: Describe the design comprehensively, but don't write the AL code. That's al-developer's job.

#### Requirements (150-300 lines)
- Detailed user stories
- Comprehensive functional requirements
- Full non-functional requirements
- Integration analysis
- Questions for clarification
- Detailed acceptance criteria

**Include everything:** This is where thoroughness is justified.

#### Solution Plan (250-500 lines)
- Design philosophy
- Architecture diagrams (ASCII art appropriate here)
- Alternatives considered with pros/cons
- Data model (tables and key fields listed)
- Integration patterns (described, not coded)
- Per-file breakdown:
  - Object purpose
  - **Field/procedure LISTS** (not implementations)
  - Integration points
  - Key validations (described in English)
- Performance considerations
- Error handling strategy
- Testing requirements
- Implementation sequence

**DO:**
- Comprehensive field lists with types and purposes
- Procedure signatures (name, parameters, return type, purpose)
- Validation rules in plain English
- Data flow descriptions
- Architecture diagrams

**DON'T:**
- Write 200-line table definitions
- Write 100-line procedure implementations
- Write complete triggers with full logic
- Write complete page layouts
- Show more than 10-15 lines of AL code per object

**Remember: ARCHITECTURE YES, IMPLEMENTATION NO. al-developer writes the actual AL code.**

---

## Agent-Specific Guidelines

### requirements-engineer

**Output target by complexity:**
- SIMPLE: 50-75 lines
- MEDIUM: 100-150 lines
- COMPLEX: 150-300 lines

**For SIMPLE features:**
1. Skip user stories (just list requirements)
2. Skip detailed acceptance criteria (just checkboxes)
3. 3-5 functional requirements max
4. 2-3 non-functional requirements max
5. Brief, bulleted format
6. No exploration of edge cases beyond basics

**For MEDIUM features:**
1. Brief user story per requirement (1-2 sentences)
2. Simple acceptance criteria (3-5 items per requirement)
3. 5-8 functional requirements
4. 3-5 non-functional requirements
5. Integration points documented

**For COMPLEX features:**
1. Detailed user stories with context
2. Comprehensive acceptance criteria
3. 8+ functional requirements
4. 5+ non-functional requirements
5. Deep integration analysis
6. Questions for clarification

### solution-planner

**Output target by complexity:**
- SIMPLE: 50-100 lines
- MEDIUM: 100-300 lines
- COMPLEX: 300-600 lines

**For SIMPLE features:**
1. NO ASCII diagrams
2. NO "Alternatives Considered" section
3. NO detailed architecture sections
4. Brief approach (1 paragraph)
5. File-by-file implementation with essential code only
6. Implementation order (dependency list)
7. Skip: rationale, rollback plans, migration paths, extensive troubleshooting

**For MEDIUM features:**
1. ASCII diagrams ONLY if genuinely helpful (not decorative)
2. Brief alternatives section (2-3 options, 1 paragraph each)
3. Architecture overview (text-based, 1-2 paragraphs)
4. Code templates for non-obvious patterns
5. Integration points documented
6. Basic error handling approach

**For COMPLEX features:**
1. Full ASCII diagrams showing architecture
2. Detailed alternatives analysis
3. Design rationale section
4. Comprehensive code templates
5. Performance considerations
6. Error handling strategy
7. Rollback and migration plans
8. Extensive troubleshooting guide

---

## Red Flags: When Planning is Too Detailed

**Stop and reconsider if you're writing:**

1. **ASCII diagrams for 3-file changes** → Remove them
2. **"Alternatives Considered" for obvious patterns** → Skip it
3. **User stories for field additions** → Just list requirements
4. **Migration plans for table extensions** → Not needed (BC handles it)
5. **Rollback strategies for simple changes** → Git is your rollback
6. **500+ line plans for "add a field"** → Way too much

**Ask yourself:**
- Is this diagram adding clarity or just looking professional?
- Would a developer need this level of detail?
- Am I documenting obvious BC patterns?
- Could this be 50% shorter without losing value?

---

## Examples

### ❌ BAD: SIMPLE Feature with 946-line Plan

**Feature:** Add boolean to Customer, modify codeunit IF statement
**Lines written:** 946 (requirements 240, solution 946)
**Problem:**
- ASCII diagrams for 3-file change
- Detailed data flow diagrams
- Alternatives analysis for obvious pattern
- Extensive code templates for standard table extension

**Should have been:** 100-150 lines total

---

### ✅ GOOD: SIMPLE Feature with Proportional Plan

**Feature:** Add boolean to Customer, modify codeunit IF statement
**Lines:** 120 total (requirements 60, solution 60)

```markdown
# Requirements: Zero Pricing Toggle

## What
Add Customer."Zero Price Shopify" boolean to conditionally apply zero pricing in existing Codeunit 50011.

## Files
1. Tab-Ext Customer - add boolean field
2. Pag-Ext Customer Card - show field
3. Codeunit 50011 - add IF check

## Requirements
1. Boolean field on Customer table (default: false)
2. Field visible on Customer Card
3. IF true, set price to 0 in UpdateLinePrice
4. IF false, use existing price calculation

## Non-Functional
- Performance: SetLoadFields for customer read (<10ms)
- Permissions: Inherits Customer table permissions

---

# Solution Plan

## Approach
Extend Customer table with boolean, extend Customer Card to show it, modify UpdateLinePrice to check field before applying pricing.

## File 1: TabExt50001.CustomerExt.al
field(50001; "Zero Price Shopify"; Boolean) {
    DataClassification = CustomerContent;
}

## File 2: PagExt50001.CustomerCardExt.al
addafter(Blocked) {
    field("Zero Price Shopify"; Rec."Zero Price Shopify") { }
}

## File 3: Codeunit 50011 - UpdateLinePrice
Add before existing price logic:

if IsZeroPriceCustomer(SalesHeader."Sell-to Customer No.") then begin
    SalesLine."Unit Price" := 0;
    SalesLine."Line Amount" := 0;
    SalesLine.Modify(true);
    exit;
end;

procedure IsZeroPriceCustomer(CustomerNo: Code[20]): Boolean
var
    Customer: Record Customer;
begin
    if not Customer.Get(CustomerNo) then
        exit(false);
    exit(Customer."Zero Price Shopify");
end;

## Order
1. Table extension (foundation)
2. Page extension (UI)
3. Codeunit modification (logic)

## Testing
- Customer with toggle ON → prices = 0
- Customer with toggle OFF → normal prices
```

**Total: ~120 lines. Everything needed, nothing extra.**

---

### ✅ GOOD: COMPLEX Feature with Comprehensive Plan

**Feature:** Multi-level approval workflow with email notifications
**Lines:** 650 total (requirements 250, solution 400)
**Justified because:**
- New architectural component
- Multiple integration points
- State machine logic
- External dependencies (email)
- Security implications

---

## Enforcement

### In Main Orchestrator

Before spawning agents, classify request:

```markdown
User request: "Add zero pricing toggle to Customer"

Classification: SIMPLE
- Extends existing pattern (table + page extension)
- 3 files
- One IF statement change

Target planning: 100-150 lines total

Spawning requirements-engineer with instruction:
"Keep output to 50-75 lines. No user stories, brief requirements list only."

Spawning solution-planner with instruction:
"Keep output to 50-100 lines. No ASCII diagrams, no alternatives section, essential code only."
```

### In Agents

Each agent checks their output length before returning:

```markdown
requirements-engineer:
- Feature classified as: SIMPLE
- Target output: 50-75 lines
- Current output: 68 lines ✓
- Contains: requirements list, 3 NFRs, success criteria
- Does NOT contain: user stories, detailed acceptance criteria ✓
```

---

## Quick Reference

| Complexity | Req Lines | Plan Lines | Total | Include | Omit |
|------------|-----------|------------|-------|---------|------|
| TRIVIAL | 0 | 0 | 0 | Nothing | Everything |
| SIMPLE | 50-75 | 50-100 | 100-150 | Essentials | Stories, diagrams, alternatives |
| MEDIUM | 100-150 | 100-300 | 200-400 | Design decisions | Extensive analysis |
| COMPLEX | 150-300 | 300-600 | 400-800 | Everything | Nothing (thorough appropriate) |

---

**Remember:** Planning should clarify, not overwhelm. If your plan takes longer to read than to implement, it's too detailed.
