---
name: al-dev-document
description: >-
  Generate comprehensive technical documentation including a requirements
  traceability matrix (RTM) with inline requirement references.
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

**Context-continuation check:** If the current session opens with a
continuation summary (the harness prefix "This session is being continued
from a previous conversation"), read that summary now — before the
audience prompt and before any `.dev/` file reads. The summary may
already contain the audience selection, prior scope findings, and RTM
status; use it as the primary source and load `.dev/` files in Step 1
only to fill gaps.

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

Verify the template exists. Replace `[AUDIENCE]` below with the value chosen
above (`technical`, `functional`, `user`, or `executive`) before running:

```bash
ls ~/al-dev-shared/profile-al-dev-shared/knowledge/doc-templates/[AUDIENCE].md 2>/dev/null \
  || echo "Template not found — docs-writer will use inline structure from Step 2"
# Non-zero exit here is expected and normal — do not retry.
```

If the echo fires, omit `TEMPLATE_PATH` from the spawn prompt and let the docs-writer use the inline documentation structure defined in Step 2.

### Step 1: Identify Documentation Scope (1-2 min)

If a continuation summary was read in Step 0, load `.dev/` files only
to fill gaps the summary does not cover. If the summary provides audience,
scope, RTM status, and the required plan/requirements artifact paths,
proceed to Step 2 immediately without re-reading those files.

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
this block (do NOT present to user until all three rows are filled in). When the
document contains one or more Mermaid/diagram blocks, add one Diagram row per
diagram as well:

```text
VERIFICATION
- Section: <name> | Claim: <field/method/object ID> | Source: <file:line> | Match: yes/no
- Section: <name> | Claim: <field/method/object ID> | Source: <file:line> | Match: yes/no
- Section: <name> | Claim: <field/method/object ID> | Source: <file:line> | Match: yes/no
- Diagram (one row per diagram present): <diagram title> | Claim: <conditional label / node name / edge / branch> | Source: <file:line> | Match: yes/no
```

If any row shows `no`, send the specific mismatch back to docs-writer before
presenting. When a Diagram row shows `no`, also scan every other diagram in the
document for the **same error class** before re-presenting — same error class
means: a wrong conditional/edge label, a stale node name, or a missing branch.
Skipping this block is visible to the user — do not omit it.

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

## Formatting-Sweep Variant

Use this variant when the task is **formatting or bolding terms across an existing document**
rather than writing a new document from scratch. This variant is reached by explicit
`/al-dev-document` invocation; it is not auto-routed from free-form requests.

### Step FS-1: Enumerate all targets before editing (grep-first — mandatory)

Before spawning the docs-writer, enumerate every candidate location **and** compute which
lines fall inside fenced code blocks, so code-fence hits are excluded with certainty rather
than guessed from a context-free grep line:

```bash
# 1. Candidate hits (replace the term list with the user's actual target terms)
grep -n "Term One\|Term Two\|Term Three" docs/Features/YourFile.md

# 2. Compute fenced-code line numbers (no literal backticks, so this block stays valid)
python3 - <<'PY'
fence = chr(96) * 3
path = "docs/Features/YourFile.md"
inside = False
for n, line in enumerate(open(path), 1):
    if line.lstrip().startswith(fence):
        inside = not inside
        print(n, "fence-boundary")
        continue
    if inside:
        print(n, "in-fence")
PY
```

Classify each candidate hit using BOTH outputs:

- Line number appears in the fenced-code output (step 2) → **excluded** (code fence)
- Already bold (the term is wrapped in `**...**`) → skip
- Inside inline backticks → **excluded**
- Inside a blockquote line (starts with `>`) → **excluded**
- Otherwise prose → apply bold

Record two explicit lists before spawning: **prose hits** (line numbers to bold) and
**excluded hits** (line numbers + reason). Do not begin editing until both lists are
complete.

### Step FS-2: Spawn docs-writer with explicit formatting rules

Include a `**Formatting rules**` block in the spawn prompt. Omitting it causes mid-sweep
clarification interruptions. Pass the prose-hit list to edit and the excluded-hit list so
the docs-writer never has to re-derive code-fence context it cannot see:

```text
Spawn single docs-writer teammate:

"Format the following terms in [docs/Features/YourFile.md].

**Formatting rules (apply exactly — do not stop to ask):**
- Bold these exact terms wherever they appear in prose: [list every term]
- Also bold these variant forms: [list abbreviations / shortened names]
- Do NOT bold inside: AL code fences, inline backticks, tester blockquotes (> lines)
- When in doubt about a variant form, apply bold — do not ask.

Target locations — PROSE HITS ONLY (edit only these line numbers):
[paste the prose-hit line numbers from FS-1]

Excluded hits — do NOT edit these (code fence / inline code / blockquote):
[paste the excluded line numbers with their reason from FS-1]

Re-run the FS-4 verification after all edits and report any line still unbolded."
```

### Step FS-3: Long-running sweep protocol (150+ lines or multiple files)

If the sweep covers more than 150 lines or more than one file, include a checkpoint
instruction in the spawn prompt:

```text
"Before starting, write .dev/format-sweep-progress.md:
- [ ] File 1: <path> — 0/<N> targets
- [ ] File 2: <path> — not started

After each target is applied, tick it off in the progress file.
On any resumption (after a 'continue' prompt), read .dev/format-sweep-progress.md
before attempting any edit — this prevents 'no changes to make' errors on
already-formatted content.
Delete the progress file when all targets are confirmed complete."
```

### Step FS-4: Verify sweep is complete (per-occurrence — do not use a `grep -v` filter)

After the docs-writer finishes, re-list every candidate occurrence and inspect each one:

```bash
grep -n "Term One\|Term Two\|Term Three" docs/Features/YourFile.md
```

For **each line printed**, confirm that every prose occurrence of every target term on that
line is wrapped in `**...**`. Do **not** filter the output with `grep -v` on the bold
marker: a line passes such a filter as soon as it contains any bold text, even when another
target term on the same line is still plain — exactly the mixed-format state this sweep
exists to clean up. The sweep is complete only when no unbolded prose occurrence of any
target term remains across all printed lines (excluded code-fence / inline-code / blockquote
hits from FS-1 stay plain by design).

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

**Timing:** Usually run after `/al-dev-develop-orchestrate`.

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

Feature documents produced by this skill can be folded into a session summary
alongside other `.dev/` outputs (exploration findings, interview notes, release
notes) when assembling a session index.
