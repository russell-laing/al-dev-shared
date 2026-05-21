# Knowledge File Quality Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve 19 HIGH and MEDIUM severity knowledge file gaps that block agent guidance, incomplete workflow documentation, and missing code examples.

**Architecture:** Fix critical guidance documents first (HIGH priority: 6 issues affecting core agent behavior), then medium-priority completeness issues (MEDIUM priority: 13 issues affecting workflow guidance). Each fix is isolated to a single knowledge file with no cross-file dependencies, enabling parallel execution.

**Tech Stack:** Markdown editing, no code changes. Validation via re-running the audit after completion.

---

## HIGH Priority Fixes (Critical — Blocks Agent Guidance)

### Task 1: Audit compile-lint-procedure.md for completeness

**Files:**
- Read: `profile-al-dev-shared/knowledge/compile-lint-procedure.md`
- Verify against: `/al-dev-fix`, `/al-dev-develop`, `/al-dev-lint` skills (referenced 7+ times)

- [ ] **Step 1: Read the file to check its coverage**

Run: `head -100 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/compile-lint-procedure.md`

Document what you find:
- Does it cover al-compile command options and output format? (yes/no)
- Does it explain error log parsing procedures? (yes/no)
- Does it define diagnostic categorization rules? (yes/no)
- Does it explain auto-fix applicability criteria? (yes/no)

- [ ] **Step 2: If gaps found, expand the file**

If any of the four areas above is missing or thin (less than 5 lines), add a new section covering it. Use this structure:

```markdown
### [Missing Topic]

[2-3 sentences explaining the concept]

Example:
[One concrete example showing how it applies]
```

- [ ] **Step 3: Verify completeness**

Re-read the file end-to-end. Confirm that all four areas now have 5+ lines of substantive content. If still thin, add more detail.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/compile-lint-procedure.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(knowledge): verify and expand compile-lint-procedure coverage"
```

---

### Task 2: Audit perf-anti-patterns-prompt.md for completeness

**Files:**
- Read: `profile-al-dev-shared/knowledge/perf-anti-patterns-prompt.md`
- Verify against: `al-dev-performance-reviewer` agent (primary reference)

- [ ] **Step 1: Read the file to check taxonomy coverage**

Run: `wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/perf-anti-patterns-prompt.md`

Then: `head -150 /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/perf-anti-patterns-prompt.md`

Document what you find:
- Are all 8 performance patterns explicitly named and defined? List them.
- Is there a severity classification section (Critical/High/Medium)? (yes/no)
- Are exclusion rules documented (when NOT to flag a pattern)? (yes/no)
- Is trade-off guidance present (performance vs maintainability)? (yes/no)

- [ ] **Step 2: If gaps found, add missing sections**

If any area is missing or has fewer than 10 lines, add a new section. Use this structure:

```markdown
### [Topic: e.g., Severity Rules]

[3-4 sentences explaining the concept]

**Examples:**
- Critical: [1-line example]
- High: [1-line example]
- Medium: [1-line example]
```

- [ ] **Step 3: Verify all 8 patterns are named**

Create a quick list of the 8 patterns by name. If fewer than 8 are present, research common AL performance anti-patterns and add missing ones with definitions.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/perf-anti-patterns-prompt.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(knowledge): verify and expand perf-anti-patterns taxonomy"
```

---

### Task 3: Expand workflow-routing.md with COMPLEX workflow example

**Files:**
- Edit: `profile-al-dev-shared/knowledge/workflow-routing.md` (lines 116-150)
- Add: Detailed COMPLEX workflow execution example

- [ ] **Step 1: Read the COMPLEX section**

Run: `sed -n '116,150p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/workflow-routing.md`

Confirm that lines 116-150 describe COMPLEX routing but lack a detailed execution example.

- [ ] **Step 2: Add concrete COMPLEX workflow example after line 150**

Insert this detailed example showing how an "approval workflow" feature maps to agent sequence + time:

```markdown
#### COMPLEX Workflow Example: Approval Workflow Feature

**Feature:** Add multi-step approval routing for purchase orders (requires table modification, page redesign, event subscribers, auto-notification).

**Classification:** 4 subsystems + novel architecture + unclear performance impact → COMPLEX

**Workflow Sequence:**

1. **Phase 1 — Architect Debate** (45-60 min)
   - 2-3 architect agents propose competing approval designs
   - Agents debate: centralized state machine vs event-driven vs table-based
   - You pick the best approach

2. **Phase 2 — Detailed Planning** (30-45 min)
   - Solution architect writes task-by-task plan (15-20 tasks)
   - Coverage: schema changes, page controls, event subscribers, notifications
   - Plan includes test strategy and verification steps

3. **Phase 3 — Implementation** (2-4 hours)
   - Parallel developer + 3 specialist reviewers (security, AL patterns, performance)
   - Per-file commits as features are completed
   - Auto-fix compile errors; checkpoint after each logical section

4. **Phase 4 — Verification & Integration** (30-60 min)
   - Run full test suite; verify no regressions in related workflows
   - Security reviewer confirms permission checks on approval transitions
   - Performance reviewer confirms no query loops in notification broadcast

**Total estimate:** 4-6 hours wall-clock time (highly parallelized)

**Key decision point:** Architecture choice in Phase 1 determines implementation scope — wrong choice = 2× rework. This is why COMPLEX tasks get architect debate upfront.
```

- [ ] **Step 3: Verify the example is clear**

Re-read the example. Does it show:
- How the feature is classified as COMPLEX? ✓
- What agent sequence executes it? ✓
- Time estimates for each phase? ✓
- How the result differs from SIMPLE/MEDIUM workflows? ✓

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/workflow-routing.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(knowledge): add COMPLEX workflow example to workflow-routing"
```

---

### Task 4: Expand al-developer-patterns.md — User-Facing Errors section

**Files:**
- Read: `profile-al-dev-shared/knowledge/al-developer-patterns.md`
- Edit: Line 189-191 (User-Facing Errors section)

- [ ] **Step 1: Locate the section**

Run: `sed -n '189,191p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/al-developer-patterns.md`

Confirm it shows only 1 line of content.

- [ ] **Step 2: Replace the stub with detailed guidance**

Replace lines 189-191 with:

```markdown
#### User-Facing Errors

User-facing error messages should be clear, actionable, and avoid internal technical details. The message should explain WHAT went wrong and HOW to fix it, not system internals.

**❌ BAD: Internal error message**
```al
if (PurchHeader.Status <> PurchHeader.Status::Open) then
    Error('Transaction state mismatch: cannot update PurchHeader with Status=' + Format(PurchHeader.Status));
```

**✅ GOOD: User-friendly error message**
```al
if (PurchHeader.Status <> PurchHeader.Status::Open) then
    Error('Purchase order must be in Open status to make changes. Current status: %1', Format(PurchHeader.Status));
```

The GOOD version:
- Names the action that failed ("Purchase order must be in Open status")
- Shows the current state ("Current status: X")
- Is readable without understanding internal field names
```

- [ ] **Step 3: Verify the example is clear**

Does the GOOD example:
- Explain what went wrong? ✓
- Explain how to fix it? ✓
- Avoid internal jargon? ✓

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/al-developer-patterns.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(knowledge): expand user-facing errors section with examples"
```

---

### Task 5: Expand al-developer-patterns.md — Handling Missing Information section

**Files:**
- Edit: `profile-al-dev-shared/knowledge/al-developer-patterns.md`
- Edit: Line 192-194 (Handling Missing Information section)

- [ ] **Step 1: Locate and replace the stub**

Run: `sed -n '192,194p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/al-developer-patterns.md`

Replace this 1-line stub with:

```markdown
#### Handling Missing Information

When required data is not provided or cannot be computed, ask for clarification explicitly instead of assuming defaults. Document the assumption and what the user should provide.

**Example: Requesting Missing Information**

In a sales invoice workflow, if the customer's shipping address is missing, provide a clear error asking for it:

```al
procedure ValidateShippingAddress(SalesHeader: Record "Sales Header") Result: Boolean
begin
    if SalesHeader."Ship-to Address" = '' then begin
        // Clear, specific request with next steps
        Error('Shipping address required for Order %1. Go to Sales Orders, select this order, choose Actions > Edit Ship-To Address.', 
            SalesHeader."No.");
    end;
    Result := true;
end;
```

The error message:
- Identifies what is missing (Shipping address)
- For which record (Order #X)
- How to provide it (exact menu path)
```

- [ ] **Step 2: Verify clarity**

Does the example:
- Show what to ask for? ✓
- Show how to communicate the ask? ✓
- Provide actionable next steps? ✓

- [ ] **Step 3: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/al-developer-patterns.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(knowledge): expand handling-missing-information section with example"
```

---

### Task 6: Expand proportional-planning.md with bad example analysis

**Files:**
- Read: `profile-al-dev-shared/knowledge/proportional-planning.md` (lines 310-325)
- Edit: Add analysis after the bad example

- [ ] **Step 1: Locate the bad example**

Run: `sed -n '310,325p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/proportional-planning.md`

Confirm it shows a 946-line plan labeled "❌ BAD" but lacks explanation of what went wrong.

- [ ] **Step 2: Add analysis after the bad example**

After the bad example ends, insert:

```markdown
**Why this plan is too large:**

This 946-line plan violates SIMPLE proportionality in four ways:

1. **Over-decomposed tasks:** Each task is 5-10 lines when SIMPLE tasks should be 1-2 lines (write test, run test, implement, commit). This plan has 50+ tasks where 10-12 would suffice.

2. **Redundant detail:** Task descriptions repeat the same validation pattern 20+ times instead of explaining the pattern once and applying it.

3. **Unnecessary architecture sections:** Plan includes "Infrastructure Setup," "Logging Framework," and "Monitoring Dashboard" sections that are out of scope for a simple feature. SIMPLE features don't need infrastructure design.

4. **Gold-plating test coverage:** Plan requires 100+ test cases for a simple feature. SIMPLE tests should cover: happy path, one error case, one edge case. Total: 3-5 tests per function.

**What went wrong in the planning process:**
The planner treated this SIMPLE feature like a MEDIUM or COMPLEX feature, creating overhead that adds no value. This is over-planning — common when a planner defaults to "include everything possible" instead of "include only what's necessary."

**How to avoid this:**
- Count the required test cases BEFORE you plan (happy + error + edge = 3-5)
- Count the required files BEFORE you plan (1-2 files for SIMPLE)
- Review your task count: SIMPLE = 10-15 tasks, MEDIUM = 20-30, COMPLEX = 40+
- If your plan is 5× the expected size, you're likely over-planning
```

- [ ] **Step 3: Verify the analysis is helpful**

Does it:
- Explain specific problems? ✓
- Help future planners avoid the same mistakes? ✓
- Tie back to SIMPLE/MEDIUM/COMPLEX classification? ✓

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/proportional-planning.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(knowledge): add bad example analysis to proportional-planning"
```

---

### Task 7: Expand verification-and-planning.md — grep example for forbidden patterns

**Files:**
- Read: `profile-al-dev-shared/knowledge/verification-and-planning.md` (lines 16-44)
- Edit: Add concrete grep example under "Step 2: Forbidden Pattern Scan"

- [ ] **Step 1: Locate the verification checklist**

Run: `sed -n '16,44p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/verification-and-planning.md`

Find the section describing "Step 2: Forbidden Pattern Scan" and confirm it lacks concrete examples.

- [ ] **Step 2: Add a grep example in the text**

Find the line that mentions "Step 2: Forbidden Pattern Scan" and after it, insert:

```markdown
**Step 2: Forbidden Pattern Scan**

Scan all changed files for patterns that indicate incomplete work. Use grep to find:

```bash
# Check for unrendered templates
git diff --name-only --cached | xargs grep -l "\[date\]\|\[YYYY-MM-DD\]" 2>/dev/null && echo "❌ Found unrendered date placeholders"

# Check for TODO/TBD markers (incomplete work)
git diff --cached --unified=0 | grep "^\+" | grep -E "TODO|TBD" && echo "❌ Found incomplete work markers"

# Check for harness-specific debug comments
git diff --cached | grep -E "claude:|copilot:" && echo "❌ Found harness-specific debug code"

# If all checks pass:
echo "✅ No forbidden patterns found"
```

Run this before committing to catch common verification failures.
```

- [ ] **Step 3: Verify the example is executable**

Does the grep example:
- Show actual bash commands? ✓
- Cover the 3-4 most common failures? ✓
- Show success/failure output? ✓

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/verification-and-planning.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(knowledge): add grep examples to verification checklist"
```

---

### Task 8: Expand verification-and-planning.md — critique and falsification examples

**Files:**
- Read: `profile-al-dev-shared/knowledge/verification-and-planning.md` (lines 136-159)
- Edit: Add example architect outputs after "The Three Architect Outputs" section

- [ ] **Step 1: Locate the architect outputs section**

Run: `sed -n '136,159p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/verification-and-planning.md`

Confirm it describes outputs but lacks concrete text examples.

- [ ] **Step 2: Add example proposal, critique, and falsification**

After line 159, insert:

```markdown
#### Example: Architect Debate on Caching Strategy

**Proposal (Architect A):**
> "Use in-memory cache with 5-minute TTL. Pros: fast, simple. Cons: stale data risk if config changes during window."

**Strong Critique (Architect B):**
> "5-minute TTL is risky for multi-tenant scenarios where tenant A's config could pollute tenant B's cache if deletion happens mid-window. Proposal lacks tenant isolation strategy. Better: use Redis with event-driven invalidation so cache clears immediately when config changes."

**Why that's a strong critique:** It identifies a specific failure case (tenant pollution), explains why it matters (correctness issue), and proposes a concrete alternative (Redis with invalidation).

**Weak Critique (Architect C):**
> "In-memory cache might not be performant enough."

**Why it's weak:** "Might not" is vague (no concrete scenario). No data supporting the concern. No alternative proposed.

**Falsification (You, the decision-maker):**
> "Test case: In-memory cache with Event Subscriber that clears cache on config-change events. Tenant A creates config, Tenant B reads it (should miss cache). Tenant A deletes config, Tenant B reads again (should still miss). If this test passes with immediate invalidation, Architect A's proposal is falsified — we need Redis only if we cannot guarantee event-driven invalidation. Let's prototype event-driven invalidation first."

**Why that's a strong falsification:** It proposes a testable scenario that would validate or invalidate the proposal. Testing beats philosophy.
```

- [ ] **Step 3: Verify the examples are clear**

Does the debate example:
- Show what a strong critique looks like? ✓
- Show what a weak critique looks like? ✓
- Show how to falsify a proposal? ✓

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/verification-and-planning.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(knowledge): add architect debate examples to verification"
```

---

## MEDIUM Priority Fixes (Incomplete Guidance)

### Task 9: Expand tdd-workflow.md with all five variant sections

**Files:**
- Edit: `profile-al-dev-shared/knowledge/tdd-workflow.md`
- Expand: Five sections with 3-5 lines each (Auto-Detection, File Output Options, Failures-Only Filter, CI/CD Integration, Example Workflows)

- [ ] **Step 1: Locate the variants section**

Run: `sed -n '90,120p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/tdd-workflow.md`

Identify the five subsections (Auto-Detection, File Output Options, Failures-Only Filter, CI/CD Integration, Example Workflows).

- [ ] **Step 2: Expand Auto-Detection section**

Replace the 2-line stub with:

```markdown
#### Auto-Detection from app.json

The TDD workflow can auto-detect test framework and project structure from app.json fields:

- **"test"** field in app.json specifies the test framework (e.g., "test": "XUnit Adapter")
- **"id"** field identifies the app scope — tests are isolated by app ID to prevent cross-app test pollution
- **"version"** field tags test results with app version so regressions are tracked per release

Auto-detection skips manual configuration and routes tests to the correct runner automatically. If app.json lacks test field, the workflow prompts for framework choice.
```

- [ ] **Step 3: Expand File Output Options section**

Replace the 2-line stub with:

```markdown
#### File Output Options

Test runners can output results in multiple formats:

- **--format json** — Machine-readable JSON for CI/CD pipelines and reporting dashboards
- **--format text** — Human-readable output for local development (default)
- **--format junit** — JUnit XML format for Jenkins and GitHub Actions integration
- **--format csv** — Tabular format for spreadsheet analysis and trend reporting

Default: text. Use JSON in CI/CD so downstream tools can parse results and trigger notifications or gates.
```

- [ ] **Step 4: Expand Failures-Only Filter section**

Replace the 2-line stub with:

```markdown
#### Failures-Only Filter

The `--failures-only` flag reduces output noise by showing only failed tests:

```bash
npm test -- --failures-only
```

Use this during iterative development to focus on broken tests. After fixes, run the full test suite without the flag to ensure no regressions in previously passing tests.

**When to use:**
- Local: Iterating on a specific feature (many tests may pass; focus on the 2-3 failures)
- CI: NOT recommended (hides passing tests and can miss silent regressions)
```

- [ ] **Step 5: Expand CI/CD Integration section**

Replace the 2-line stub with:

```markdown
#### CI/CD Integration

Integrate TDD workflow into CI/CD pipelines with these patterns:

**GitHub Actions example:**
```yaml
- name: Run tests
  run: npm test -- --format json --output test-results.json
- name: Report results
  if: always()
  run: |
    if [ -f test-results.json ]; then
      npx junit-reporter test-results.json
    fi
```

**Key pattern:** Run tests with structured output (JSON/JUnit), then parse and report. Gate merges on test results: no failures before merge.
```

- [ ] **Step 6: Expand Example Workflows section**

Replace the 2-line stub with:

```markdown
#### Example Workflows

**Local development:**
```bash
npm test -- --watch        # Run tests; re-run on file changes
npm test -- --failures-only --watch  # Focus on failures during iteration
```

**CI/CD pipeline:**
```bash
npm test -- --format junit --bail  # Stop at first failure; generate report
```

**Manual verification before commit:**
```bash
npm test                    # Run full suite once
npm test -- --coverage      # Check coverage metrics
```
```

- [ ] **Step 7: Verify all five sections are expanded**

Re-read all five sections. Each should have 3-5 lines of substantive content (examples, concrete flags, or guidance).

- [ ] **Step 8: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/tdd-workflow.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(knowledge): expand tdd-workflow variant sections"
```

---

### Task 10: Expand documentation-rtm-guide.md with Examples and User Perspective sections

**Files:**
- Edit: `profile-al-dev-shared/knowledge/documentation-rtm-guide.md`
- Expand: Two sections (Examples, User Perspective)

- [ ] **Step 1: Locate the two stub sections**

Run: `sed -n '96,105p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/documentation-rtm-guide.md`

Find the "Examples" section (line ~96) and "User Perspective" section (line ~100).

- [ ] **Step 2: Expand the Examples section**

Replace the stub with:

```markdown
#### Examples

**Technical documentation with RTM references:**

> **Requirement REQ-003:** "Sales order approval workflow must notify approver within 5 minutes of submission."
> 
> **Implementation:** When a sales order is submitted with Status = Pending Approval, the system triggers an event subscriber that sends email to the approver (from Approver User table, configured in Sales & Receivables Setup). The notification includes the order number, total amount, and approval link.
> 
> **Verification:** See Approval Workflow Tests (ref: REQ-003-v1, REQ-003-v2)

Each sentence ties back to a specific requirement. Readers can trace from documentation to requirement to test coverage.
```

- [ ] **Step 3: Expand the User Perspective section**

Replace the stub with:

```markdown
#### User Perspective

User-facing documentation de-emphasizes requirements and RTM details:

**User Guide (less RTM detail):**
> When your purchase order is ready for review, click "Submit for Approval." The approver will receive an email within a few minutes and can approve or reject the order using the link in the email. You'll be notified when the order is approved.

**Technical Documentation (more RTM detail):**
> PO approval flow: Status = Open → Submit → Status = Pending Approval (triggers event subscriber) → Approver receives notification email (within 5 min SLA per REQ-003) → Approver clicks link → Portal opens approval page → Approver clicks Approve → Status = Approved (triggers audit log per REQ-002)

User guides omit the requirement IDs and SLA details; technical docs include them for traceability.
```

- [ ] **Step 4: Verify clarity**

Do both examples:
- Show a concrete before/after? ✓
- Demonstrate the difference in RTM detail? ✓
- Help writers choose which level to use? ✓

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/documentation-rtm-guide.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(knowledge): expand rtm-guide examples and user perspective"
```

---

### Task 11: Expand code-review-patterns.md with AL code example

**Files:**
- Edit: `profile-al-dev-shared/knowledge/code-review-patterns.md`
- Expand: "Naming Convention Violations" section with AL code examples

- [ ] **Step 1: Locate the naming violations section**

Run: `sed -n '7,17p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/code-review-patterns.md`

Confirm it shows naming rule violations but uses object names only (not AL code samples).

- [ ] **Step 2: Add AL code examples after the rules**

After line 17, insert:

```markdown
#### Examples in AL Code

**❌ BAD: Violates character limit (>30 chars) and post-fix naming**
```al
codeunit 50100 "VeryLongNamingConventionViolationExampleCodeunitPostFix" { }
table 50101 "PurchaseOrderApprovalDataTable" { }
```

**✅ GOOD: Follows 30-char limit and pre-fix convention**
```al
codeunit 50100 "PurchaseApprovalProcessor" { }
table 50101 "PurchaseApprovalData" { }
```

**Detection during review:**
- Count characters in object names: if > 30, flag it
- Check naming order: pre-fix (category first, e.g., "Purchase Approval") vs post-fix (category last, bad)
- Look for abbreviations that obscure meaning (OK: "PO" for Purchase Order; NOT OK: "PAPD" for Purchase Approval Processing Details)
```

- [ ] **Step 3: Verify the examples are clear**

Do the AL code examples:
- Show a clear bad vs good contrast? ✓
- Explain how to detect violations? ✓
- Show the actual code, not just object names? ✓

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/code-review-patterns.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(knowledge): add AL code examples to code-review-patterns"
```

---

## Post-Implementation Verification

### Task 12: Re-run knowledge audit and verify issue count drops

**Files:**
- Audit: All modified knowledge files

- [ ] **Step 1: Run the audit script**

Run: `python3 /Users/russelllaing/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-plans/../../../scripts/audit-knowledge-quality.py 2>/dev/null | tail -50`

(Or use the available audit tool in the plugin)

- [ ] **Step 2: Verify warning count drops**

Compare the output warning count to the baseline:
- **Baseline:** 34 warnings (6 HIGH, 13 MEDIUM, 15 LOW)
- **Expected after fixes:** < 10 warnings (only LOW false-positives and intentional stubs remain)

If warning count is still high, identify remaining issues and add targeted fixes.

- [ ] **Step 3: Check that all HIGH and MEDIUM issues are resolved**

Scan the audit output:
- Any HIGH severity issues remaining? (should be 0)
- Any MEDIUM severity issues remaining? (should be 0)
- LOW issues that remain? (expected: 5-10 false positives, which are acceptable)

- [ ] **Step 4: Commit the audit results**

```bash
git -C /Users/russelllaing/al-dev-shared add docs/al-dev-knowledge-quality.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(audit): update knowledge quality report — all HIGH/MEDIUM issues resolved"
```

---

## Summary

**Total Tasks:** 12
- HIGH Priority: 8 tasks (fixes 6 critical issues)
- MEDIUM Priority: 3 tasks (fixes 13 completeness issues)
- Verification: 1 task (re-audit and confirm)

**Estimated Effort:** 90-120 minutes total
- Tasks 1-8 (HIGH): ~60 minutes
- Tasks 9-11 (MEDIUM): ~40 minutes
- Task 12 (Verification): ~10 minutes

**Key Dependencies:** None. Each task is independent and can be executed in any order.
