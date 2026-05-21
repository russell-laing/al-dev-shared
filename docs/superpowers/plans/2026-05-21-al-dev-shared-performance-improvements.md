# AL-Dev-Shared Performance Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce the two highest-frequency AL session friction patterns identified in the 2026-05-21 insights report: (1) subagent-generated AL code with non-existent field references and missing `var` modifiers, and (2) wasted debugging effort on stale compile logs.

**Architecture:** Three coordinated additions to `profile-al-dev-shared`: a new symbol pre-flight knowledge file that developer agents must complete before writing code; a governance token (`SYMBOL_PREFLIGHT_GATE`) wired into the `al-dev-developer` agent and the `al-dev-develop` Phase 3 spawn prompt; and a freshness-check section in `compile-lint-procedure.md` paired with three new rows in `anti-patterns.md`.

**Tech Stack:** Markdown (skill/agent/knowledge docs), Bash (verification greps), AL symbols MCP (referenced, not invoked in this plan)

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `profile-al-dev-shared/knowledge/al-symbol-pre-flight.md` | **Create** | Mandatory pre-flight checklist for AL developer agents |
| `profile-al-dev-shared/agents/al-dev-developer.md` | **Modify** | Add `SYMBOL_PREFLIGHT_GATE` governance token + reference to checklist |
| `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` | **Modify** | Harden Phase 3 spawn prompt from guidance to a hard gate |
| `profile-al-dev-shared/knowledge/compile-lint-procedure.md` | **Modify** | Add Step 0 (log freshness check) + baseline/diff pattern |
| `profile-al-dev-shared/knowledge/anti-patterns.md` | **Modify** | Add three new rows for stale logs, missing pre-flight, abstract options |

---

## Context: Why These Changes

From the 2026-05-21 insights report (yesterday's sessions):

**Friction 1 — Subagent code quality (46 buggy_code events):**
Parallel AL developer agents produce code with non-existent field references, wrong object type declarations, and missing `var` modifiers on event subscribers. These are caught only during rubber-duck or review passes, requiring fix cycles that could have been prevented. Root cause: the `al-dev-develop` Phase 3 spawn prompt says "Before writing code, use the AL Symbols MCP" as guidance — it is not enforced as a hard gate, so agents skip it.

**Friction 2 — Stale compile logs:**
In one session, Claude debugged a stale `.dev/compile-errors.log` extensively (the log predated recent edits) before the user interrupted — and then hit the weekly usage limit just as real fixes began. `compile-lint-procedure.md` has no freshness check; it does not warn agents to verify the log is current before treating it as authoritative.

---

## Task 1: Create `knowledge/al-symbol-pre-flight.md`

**Files:**
- Create: `profile-al-dev-shared/knowledge/al-symbol-pre-flight.md`

- [ ] **Step 1: Write the file**

```bash
cat > /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/al-symbol-pre-flight.md << 'ENDOFFILE'
# AL Symbol Pre-Flight Checklist

Referenced by: `al-dev-developer` agent (SYMBOL_PREFLIGHT_GATE),
`al-dev-develop` skill Phase 3 spawn prompt.

## Purpose

Complete this checklist before writing any AL code. It prevents the most
common cause of compilation errors: referencing fields, events, or procedures
that don't exist in the base app or in the project's own objects.

Missing `var` modifiers and non-existent field names are the top two causes
of subagent-generated compile failures. This checklist catches them at
design time, before a single line is written.

## Pre-Flight Checklist

### 1. Field References

For every base-table field you plan to reference, verify it exists:

```text
al_get_object_definition(objectType: 'Table', objectName: '<TableName>')
```

- [ ] Field name is exact (including spacing, e.g., `"Sell-to Customer No."`)
- [ ] Field data type matches your intended usage
- [ ] Field exists in the version of BC the project targets

**Common mistake:** Referencing `"Document Type Option"` as `"Document Type"`, or
using a field that exists in W1 but not in a localized base app.

### 2. Event Subscriber Signatures

For every event publisher you plan to subscribe to:

```text
al_search_object_members(searchTerm: '<EventName>', objectType: 'Codeunit')
```

- [ ] Event publisher name is exact (case-sensitive)
- [ ] Every `var` parameter in the publisher is declared `var` in your subscriber
- [ ] Parameter types match exactly (`Record "Sales Header"`, not `SalesHeader`)
- [ ] Parameter count matches the publisher

**Missing `var` is a compile error, not a warning. Example:**

```al
// WRONG — AL0118 compile error
local procedure OnAfterPostSalesDoc(SalesHeader: Record "Sales Header"; ...)
begin end;

// CORRECT — var modifier matches the publisher
local procedure OnAfterPostSalesDoc(var SalesHeader: Record "Sales Header"; ...)
begin end;
```

If the MCP result is ambiguous, use `al_find_references` to locate the
publisher source and read its exact signature.

### 3. Object Names and IDs

For every new object you plan to create:

- [ ] Object name is ≤ 30 characters (BC hard limit — count manually)
- [ ] Object name includes the project prefix from the plan
- [ ] Object ID is within your assigned range (specified in the solution plan)
- [ ] No existing object uses the same ID:

```bash
grep -rn --include="*.al" \
  -E "^(table|page|codeunit|enum|report|xmlport|query)\s+<YOUR_ID>\s" .
```

### 4. Object Types You Extend

For every object you write a table/page/codeunit extension for:

```text
al_search_objects(searchTerm: '<ObjectName>', objectType: '<Table|Page|Codeunit>')
```

- [ ] Object type is correct (extending a `Table`, not a `TableExtension`)
- [ ] Object name exactly matches (including quotes if the base name has spaces)

## Gate

**Do not write any AL code until this checklist is complete.**

Report a pre-flight summary before beginning implementation:

```text
Pre-flight complete:
- Fields verified: [list field names checked, or "none referenced"]
- Events verified: [list event names + var-params confirmed, or "none"]
- Object names: [all ≤30 chars — confirmed]
- Object IDs: [in range <X>–<Y>, no conflicts]
- Anything unverified: [name the item and reason]
```

If any item cannot be verified via MCP, do NOT guess — report it as
unverified and stop until the orchestrator or user provides guidance.
ENDOFFILE
```

- [ ] **Step 2: Verify the file was written**

```bash
ls -la /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/al-symbol-pre-flight.md
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/al-symbol-pre-flight.md
```

Expected: file exists, non-zero size, ~80+ lines.

- [ ] **Step 3: Verify required section headings exist**

```bash
grep -n "## Pre-Flight Checklist\|## Gate\|### 1. Field References\|### 2. Event Subscriber\|SYMBOL_PREFLIGHT_GATE\|Pre-flight complete" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/al-symbol-pre-flight.md
```

Expected: all 6 patterns match.

- [ ] **Step 4: Verify forbidden patterns absent**

```bash
grep -n "TODO\|TBD\|YYYY-MM-DD\|TBC" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/al-symbol-pre-flight.md \
  && echo "FAIL: forbidden patterns found" || echo "PASS: no forbidden patterns"
```

Expected: `PASS: no forbidden patterns`

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/knowledge/al-symbol-pre-flight.md
git -C /Users/russelllaing/al-dev-shared commit -m \
  "docs(knowledge): add al-symbol-pre-flight mandatory checklist for developer agents"
```

---

## Task 2: Update `agents/al-dev-developer.md`

Add `SYMBOL_PREFLIGHT_GATE` governance token and reference to the new checklist in the Standards section.

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-developer.md`

- [ ] **Step 1: Read the current file to confirm exact anchor strings**

Read `profile-al-dev-shared/agents/al-dev-developer.md` and locate:
1. The Governance Tokens table (starts at `| Token | Gate | Action |`)
2. The AL Code Patterns paragraph in Standards (starts with `Reference \`knowledge/al-developer-patterns.md\``)

Note the exact line numbers for both.

- [ ] **Step 2: Add SYMBOL_PREFLIGHT_GATE row to the Governance Tokens table**

The current table ends with:
```
| `FIX_ITERATION_LIMIT` | After 5 compile failures | Stop and escalate |
```

Using the Edit tool, insert this row immediately after the `FIX_ITERATION_LIMIT` row:

```
| `SYMBOL_PREFLIGHT_GATE` | Before writing any AL code | Complete `knowledge/al-symbol-pre-flight.md` checklist — report pre-flight summary before coding starts; stop if any item cannot be verified |
```

- [ ] **Step 3: Add checklist reference to Standards > AL Code Patterns**

The current AL Code Patterns section opens with:
```
Reference `knowledge/al-developer-patterns.md` for standard AL patterns, common mistakes to avoid, error handling rules, and naming conventions. Key principles:
```

Using the Edit tool, prepend this line immediately before that sentence:

```
Before writing any AL code, complete the symbol pre-flight checklist (`knowledge/al-symbol-pre-flight.md`). This is enforced by `SYMBOL_PREFLIGHT_GATE` — report your pre-flight summary before implementation begins.

```

- [ ] **Step 4: Verify both changes landed**

```bash
grep -n "SYMBOL_PREFLIGHT_GATE\|al-symbol-pre-flight" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
```

Expected: at least 3 matches (governance table row + reference in Standards + knowledge file path).

- [ ] **Step 5: Verify governance token table has all 5 rows**

```bash
grep -c "^| \`" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md
```

Expected: 5 (was 4, now 5 after adding SYMBOL_PREFLIGHT_GATE).

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/agents/al-dev-developer.md
git -C /Users/russelllaing/al-dev-shared commit -m \
  "feat(agent): add SYMBOL_PREFLIGHT_GATE to al-dev-developer — mandatory pre-flight before AL code generation"
```

---

## Task 3: Harden Phase 3 Spawn Prompt in `al-dev-develop/SKILL.md`

Change the Phase 3 developer spawn prompt MCP guidance block from soft guidance to a hard gate with an explicit reference to the pre-flight checklist.

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`

- [ ] **Step 1: Read Phase 3 to confirm exact anchor string**

Read `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` lines 230–280. Locate the block:

```
Before writing code, use the AL Symbols MCP (`al-mcp-server`)
to verify base app objects you will extend or subscribe to:
- al_get_object_definition — confirm field names, IDs, and
  triggers on base tables you are extending
- al_search_object_members — locate the exact event signatures
  you plan to subscribe to
- al_find_references — check if similar extensions already
  exist in the project
```

Note the exact indentation and line range.

- [ ] **Step 2: Replace the guidance block with the hard gate**

Using the Edit tool, replace the block identified in Step 1 with:

```
SYMBOL_PREFLIGHT_GATE — Complete BEFORE writing any AL code.
Follow `knowledge/al-symbol-pre-flight.md` for the full checklist.
Required checks:
1. Field references: verify each base field via al_get_object_definition
   (exact field name, including spacing and capitalisation)
2. Event signatures: verify via al_search_object_members — every var
   parameter in the publisher MUST be declared var in your subscriber;
   missing var = AL0118 compile error
3. Object names: count characters — each must be ≤30
4. Object IDs: confirm all are in your assigned range with no duplicates

Report your pre-flight summary before writing a single line of AL:
"Pre-flight complete: fields verified [list], events verified [list],
names/IDs OK [or: issue found]."

DO NOT proceed past pre-flight if any item is unverified. Stop and
report back to the orchestrator with the unverified item.
```

- [ ] **Step 3: Verify the hard gate text is present**

```bash
grep -n "SYMBOL_PREFLIGHT_GATE\|pre-flight summary\|al-symbol-pre-flight\|DO NOT proceed past pre-flight" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: all 4 patterns match, each appearing exactly once.

- [ ] **Step 4: Verify the old soft-guidance text is gone**

```bash
grep -n "use the AL Symbols MCP.*al-mcp-server" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  && echo "FAIL: old soft-guidance still present" || echo "PASS: old text removed"
```

Expected: `PASS: old text removed`

- [ ] **Step 5: Verify Phase 1.5 autonomous block is still intact**

```bash
grep -n "Phase 1.5\|Signature Verification\|--autonomous" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md | head -5
```

Expected: at least 3 matches — the Phase 1.5 block must be untouched.

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m \
  "feat(skill): harden al-dev-develop Phase 3 spawn prompt — symbol pre-flight is now a hard gate not guidance"
```

---

## Task 4: Add Stale Log Freshness Check to `compile-lint-procedure.md`

Add a new Step 0 (Log Freshness Check) before the existing Step 1, plus an optional baseline/diff pattern for edit sessions.

**Files:**
- Modify: `profile-al-dev-shared/knowledge/compile-lint-procedure.md`

- [ ] **Step 1: Read the current file to confirm the anchor for insertion**

Read `profile-al-dev-shared/knowledge/compile-lint-procedure.md`. The document currently opens with:

```
# Compile + Lint Procedure
```

followed by the introductory paragraph and then `## Step 1 — Compile`.

Note the exact text immediately before `## Step 1 — Compile`.

- [ ] **Step 2: Insert Step 0 block before Step 1**

Using the Edit tool, insert the following block immediately before `## Step 1 — Compile`:

```markdown
## Step 0 — Log Freshness Check

**Never trust an existing compile log.** Before reading or acting on
`.dev/compile-errors.log`, verify it is not stale:

```bash
LOG=".dev/compile-errors.log"
if [[ -f "$LOG" ]]; then
  NEWEST_AL=$(find . -name "*.al" -newer "$LOG" 2>/dev/null | head -1)
  if [[ -n "$NEWEST_AL" ]]; then
    echo "⚠️  Log is stale — .al files modified since last compile. Deleting stale log."
    rm -f "$LOG"
  else
    echo "Log appears current (no .al files newer than log)."
  fi
fi
```

If any `.al` file is newer than the log, delete the old log and proceed
to Step 1 to compile fresh.

**Claiming "only pre-existing warnings" is only valid if the log was
produced AFTER the most recent edit.** If the log predates recent changes,
it is evidence of the previous state, not the current one.

### Optional: Baseline + Diff for Edit Sessions

When modifying existing AL files (not creating new ones), capturing a
baseline before editing lets you show exactly which diagnostics are new:

```bash
# 1. Before any edits — capture baseline
al-compile --output .dev/compile-baseline.log 2>/dev/null || true

# 2. After edits — compile and diff
al-compile --output .dev/compile-errors.log
diff .dev/compile-baseline.log .dev/compile-errors.log | grep '^[<>]'
```

Lines prefixed `>` are new diagnostics introduced by your edits.
Lines prefixed `<` are diagnostics your edits resolved.

**Only claim success if the diff shows zero new `Error` lines.**
New `Warning` lines introduced by your edits must be acknowledged
(even if the compile is technically clean).

```

- [ ] **Step 3: Verify Step 0 is present and Step 1 still follows it**

```bash
grep -n "## Step 0\|## Step 1\|Log Freshness\|Never trust an existing\|Baseline.*Diff" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/compile-lint-procedure.md
```

Expected: `## Step 0` appears before `## Step 1`; all 5 patterns match.

- [ ] **Step 4: Verify Step 1 content is unchanged**

```bash
grep -n "al-compile --output .dev/compile-errors.log" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/compile-lint-procedure.md | head -3
```

Expected: the original Step 1 compile command is still present (line number will have shifted but text must match).

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/knowledge/compile-lint-procedure.md
git -C /Users/russelllaing/al-dev-shared commit -m \
  "docs(knowledge): add Step 0 log freshness check to compile-lint-procedure — prevent stale log trust"
```

---

## Task 5: Add Three New Rows to `knowledge/anti-patterns.md`

Document three recurring friction patterns as explicit anti-patterns so agents learn to avoid them.

**Files:**
- Modify: `profile-al-dev-shared/knowledge/anti-patterns.md`

- [ ] **Step 1: Read the current file to locate the table tail**

Read `profile-al-dev-shared/knowledge/anti-patterns.md`. The table currently ends with:

```
| **Monolith agents** | One agent doing everything | Decompose into specialist agents |
```

Note the exact last row text.

- [ ] **Step 2: Append three new rows**

Using the Edit tool, insert the following three rows immediately after the `Monolith agents` row:

```
| **Trusting stale compile logs** | Reading `.dev/compile-errors.log` from a previous run and treating it as the current state — e.g., claiming "only pre-existing warnings" when the log predates recent edits | Run Step 0 (freshness check) from `knowledge/compile-lint-procedure.md` before reading any log; if any .al file is newer than the log, delete it and recompile |
| **Missing symbol pre-flight** | Writing AL code that references base-table fields, event publishers, or procedures without first verifying they exist — produces AL0118 and missing-var compile errors | Complete `knowledge/al-symbol-pre-flight.md` checklist before writing any AL code (`SYMBOL_PREFLIGHT_GATE`); report pre-flight summary before implementation begins |
| **Abstract option presentation** | Presenting design choices with only abstract descriptions ("approach A uses events, approach B uses tables") without concrete examples, forcing the user to ask for a second round of detail before deciding | Lead each option with a concrete artifact: a code snippet, a file-path list, or a before/after example. State one specific tradeoff per option, not abstract philosophy |
```

- [ ] **Step 3: Verify three new rows are present**

```bash
grep -c "Trusting stale compile logs\|Missing symbol pre-flight\|Abstract option presentation" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/anti-patterns.md
```

Expected: `3`

- [ ] **Step 4: Verify the original rows are still intact**

```bash
grep -c "^| \*\*" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/anti-patterns.md
```

Expected: `17` (was 14 rows, now 17 after adding 3).

- [ ] **Step 5: Verify forbidden patterns absent**

```bash
grep -n "TODO\|TBD\|YYYY-MM-DD" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/anti-patterns.md \
  && echo "FAIL" || echo "PASS"
```

Expected: `PASS`

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/knowledge/anti-patterns.md
git -C /Users/russelllaing/al-dev-shared commit -m \
  "docs(knowledge): add stale-log, missing-pre-flight, and abstract-options anti-patterns"
```

---

## Self-Review

### Spec Coverage

| Friction source (insights report) | Task that addresses it |
|---|---|
| Subagent AL code with non-existent field references | Tasks 1, 2, 3 (pre-flight gate) |
| Missing `var` modifiers on event subscribers | Tasks 1, 3 (explicit var-param check in checklist and gate) |
| Wrong object type declarations | Task 1 (check 4) |
| Stale compile log debugging waste | Tasks 4, 5 |
| Abstract option presentation | Task 5 (anti-pattern row) |

All five friction sources are addressed. No gaps.

### Placeholder Scan

No TBD, TODO, YYYY-MM-DD, or similar placeholders in any task content above. Verification step 4/5 in each task explicitly checks for these.

### Type Consistency

- `SYMBOL_PREFLIGHT_GATE` — exact name used in Tasks 1, 2, 3, and 5. Consistent.
- `knowledge/al-symbol-pre-flight.md` — exact path used in Tasks 1, 2, 3. Consistent.
- `al_get_object_definition`, `al_search_object_members`, `al_find_references` — MCP tool names consistent across Tasks 1 and 3.
- `compile-lint-procedure.md` referenced as `knowledge/compile-lint-procedure.md` in Task 5 (anti-patterns). This matches the document path.
