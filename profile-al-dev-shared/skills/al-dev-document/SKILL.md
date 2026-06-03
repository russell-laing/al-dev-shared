---
name: al-dev-document
description: Generate comprehensive technical documentation.
argument-hint: "[feature name or file path to document]"
---


# Generate comprehensive technical documentation using single docs-writer teammate

---

## Purpose

Create complete documentation for implemented features:

- Spawn single docs-writer specialist
- You review for completeness and accuracy
- Present final documentation to user

---

## Usage

```bash
/al-dev-document
```

**Prerequisites:**

- Implementation must be complete (AL code exists)
- Optionally: Test results available

---

## How This Command Works

**Your Role:** Engineering Manager
**Teammate:** docs-writer specialist (single agent)
**You:** Review documentation quality, verify technical accuracy, present

### ❌ DON'T

- Write documentation yourself
- Accept incomplete documentation
- Skip technical accuracy verification

### ✅ DO

- Spawn docs-writer with clear scope
- Review for completeness
- Verify code references are accurate
- Present polished documentation

---

## Implementation Steps

### Step 0: Select Audience (< 1 min)

Ask the user which audience they are writing for:

```text
Which audience are you writing for?

1. technical — AL developer reference
   (object IDs, code, extension points)
2. functional — business analyst / consultant
   (workflows, validation rules, plain language)
3. user — end user guide
   (step-by-step, navigation, troubleshooting)
4. executive — one-page summary
   (what was built, business value)
```

Wait for the user's response. Then set:

- `AUDIENCE` = one of:
  `technical` | `functional` | `user` | `executive`
- `TEMPLATE_PATH` = `knowledge/doc-templates/[AUDIENCE].md`

Verify the template exists:

```bash
ls ~/al-dev-shared/profile-al-dev-shared/knowledge/doc-templates/[AUDIENCE].md 2>/dev/null \
  || echo "Template not found — docs-writer will use inline structure from Step 2"
# Non-zero exit here is expected and normal — do not retry.
```

If the echo fires, omit `TEMPLATE_PATH` from the spawn prompt and let the docs-writer use the inline documentation structure defined in Step 2.

### Step 1: Identify Documentation Scope (1-2 min)

```text
Determine what needs documenting:

1. Find implemented AL files
2. Read latest requirements file — note how many REQ: tokens are present:
   `$(ls .dev/*-al-dev-interview-requirements.md 2>/dev/null | sort | tail -1)`
3. Read latest solution plan if available:
   `$(ls .dev/*-al-dev-plan-solution-plan.md 2>/dev/null | sort | tail -1)`
4. Determine inferred RTM status from .dev/ files present:
   - only `*-al-dev-interview-requirements.md` → DEFINED
   - `*-al-dev-plan-solution-plan.md` present → IN-PROGRESS
   - `*-al-dev-develop-code-review.md` present → IMPLEMENTED
5. Identify target audience (developers, users, admins)
```

### Step 2: Spawn Docs-Writer Teammate (10-30 min)

```text
Spawn single docs-writer teammate:

"Write comprehensive technical documentation for [feature].

Implemented files to document:
- [List AL files created]

Audience context:
- AUDIENCE: [AUDIENCE]
- TEMPLATE_PATH: [TEMPLATE_PATH]

Context available:
- Requirements: `$(ls .dev/*-al-dev-interview-requirements.md 2>/dev/null | sort | tail -1)` (parse REQ: tokens for RTM)
- Solution plan: `$(ls .dev/*-al-dev-plan-solution-plan.md 2>/dev/null | sort | tail -1)`
- Code review: `$(ls .dev/*-al-dev-develop-code-review.md 2>/dev/null | sort | tail -1)` (if exists)

RTM instructions:
- Parse all REQ: tokens from the latest `*-al-dev-interview-requirements.md`
- Inferred status for all requirements: [DEFINED/IN-PROGRESS/IMPLEMENTED/VERIFIED]
  (determined from .dev/ files present — override the token status field)
- Add inline requirement ID references in narrative sections
- Append RTM table to the end of the feature doc

Documentation structure:

## [Feature Name] - Technical Documentation

### Overview
[What this feature does, business purpose, 2-3 paragraphs]

### Architecture

**Objects Created:**
[Table of objects with IDs, names, types, purposes]

**BC Integration:**
- Extends: [Base tables/pages]
- Events: [Subscribed events]
- Dependencies: [Base BC functionality used]

### Data Model

**Tables / Table Extensions:**
[For each table/extension: fields added, purposes, constraints]

**Key Relationships:**
[How tables relate to each other and BC base tables]

### Business Logic

**Codeunits:**
[For each codeunit: purpose, key methods, interfaces]

**Validation Rules:**
[List all validation rules, where implemented, error messages]

**Event Handlers:**
[Event subscriptions, what they do, why]

### User Interface

**Pages / Page Extensions:**
[For each page: what's added, where accessed, user actions]

**User Workflows:**
[Step-by-step workflows for key scenarios]

### API / Integration (if applicable)
[API endpoints, integration points, external dependencies]

### Testing
[If test results available: test coverage summary, how to run tests]

### Configuration
[Any setup required: permissions, configuration tables, etc.]

### Maintenance Notes
[For developers: where to find key logic, how to extend, common modifications]

### Known Limitations
[Any constraints, edge cases not handled, future enhancements]

Output to: docs/Features/[FeatureName]-[AUDIENCE].md"
```

### Step 3: Review Documentation (3-5 min)

```text
When docs-writer completes:

1. Read the documentation yourself

2. Verify technical accuracy:
   - Are object IDs correct?
   - Are code references accurate?
   - Are workflow descriptions correct?
   - Do validation rules match implementation?

3. Check completeness:
   - All objects documented?
   - Key methods explained?
   - User workflows clear?
   - Edge cases noted?
   - RTM table present at end of doc?
   - All REQ: tokens from the latest `*-al-dev-interview-requirements.md` accounted for in RTM table?
   - Inline requirement ID references present in narrative sections?

4. Verify clarity:
   - Can a new developer understand this?
   - Are examples helpful?
   - Is jargon explained?
```

**MANDATORY before presenting to user** — spot-check three sections and output
this block (do NOT present to user until all three rows are filled in):

```text
VERIFICATION
- Section: <name> | Claim: <field/method/object ID> | Source: <file:line> | Match: yes/no
- Section: <name> | Claim: <field/method/object ID> | Source: <file:line> | Match: yes/no
- Section: <name> | Claim: <field/method/object ID> | Source: <file:line> | Match: yes/no
```

If any row shows `no`, send the specific mismatch back to docs-writer before
presenting. Skipping this block is visible to the user — do not omit it.

### Step 4: Request Refinements (if needed)

```text
If gaps found:

"Docs-writer, refinements needed:

1. [Gap 1]: Missing documentation for [method/object X]
   → Add section explaining [specific aspect]

2. [Gap 2]: Workflow description for [scenario Y] is unclear
   → Add step-by-step with screenshots or code examples

3. [Gap 3]: No mention of [integration point Z]
   → Document how this integrates with [base BC functionality]

Update docs/Features/[FeatureName]-[AUDIENCE].md"

Iterate until documentation is comprehensive.

When applying fixes with the Edit tool: include 2–3 lines of surrounding
context to ensure the match is unique, or use `replace_all: true` when
updating all instances of a repeated string (e.g. markdown lint directives).
```

### Step 5: Clean Up

```text
The docs-writer agent terminates automatically when it returns its result. No explicit shutdown is needed. Proceed to Step 6.
```

### Step 6: Present to User

```text
"Documentation complete → docs/Features/[FeatureName]-[AUDIENCE].md

Documented:
- [N] objects (tables, pages, codeunits)
- [N] user workflows
- [N] integration points with BC
- [N] requirements traced (RTM: X VERIFIED, Y IMPLEMENTED, Z DEFINED)
- Testing and configuration guidance

Documentation includes:
- Architecture overview
- Data model
- Business logic
- User workflows
- Maintenance notes
- RTM appendix table

Ready for review?"

(No formal approval needed - documentation is reference material)
```

---

## Documentation Best Practices

### For Technical Audiences (Developers)

```text
Include:
- Object structure and relationships
- Key methods and interfaces
- Extension points (events, procedures)
- How to modify or extend
- Testing approach
```

### For Business Audiences (Users/Admins)

```text
Include:
- What the feature does (business value)
- How to access and use it
- Step-by-step workflows
- Configuration requirements
- Troubleshooting common issues
```

### Code Examples

```text
Show actual AL code snippets for:
- Complex validation logic
- Event usage
- API integration patterns
- Test examples
```

### Visual Aids

```text
Consider including:
- Object relationship diagrams
- Workflow flowcharts
- UI screenshots (if available)
- Data flow diagrams
```

---

## Output Files

**Docs-writer creates:**

- `docs/Features/[FeatureName]-[AUDIENCE].md` - Main documentation

**Optional additional outputs:**

- `docs/diagrams/` - Architecture diagrams
- `docs/api/` - API documentation
- `docs/users/` - User guides

---

## Success Criteria

✅ Single docs-writer teammate created comprehensive documentation
✅ You verified technical accuracy against implementation
✅ All objects, workflows, and integrations documented
✅ All REQ: tokens from the latest `*-al-dev-interview-requirements.md` appear in RTM appendix table
✅ Inline requirement ID references present in narrative sections
✅ Documentation is clear and complete
✅ Maintenance notes help future developers

---

## When to Use /al-dev-document

**✅ Use /al-dev-document when:**

- Feature implementation is complete
- You want technical reference documentation
- Onboarding new developers
- Preparing for handoff

**❌ Don't use /al-dev-document when:**

- Implementation is incomplete (document after coding)
- Quick prototype (not worth documentation overhead)

**Timing:** Usually run after `/al-dev-develop`.

---

## Tips

**Document While Fresh:**
Run `/al-dev-document` right after implementation while context is fresh.

**Include Examples:**
Code snippets and workflow examples make documentation much more useful.

**Think About Maintenance:**
Future developers will read this - explain WHY not just WHAT.

**Link to Code:**
Reference specific files and line numbers for key logic.

---

**Remember:** Spawn docs-writer, review for accuracy and completeness,
present polished documentation.

## Optional Downstream Handoff

Feature documents produced by this skill can be consumed by `/al-dev-consolidate`
as part of a session summary. If you want to consolidate this feature doc with
other session outputs (exploration findings, interview notes, release notes) into
a single session index, run `/al-dev-consolidate` after this skill completes.
