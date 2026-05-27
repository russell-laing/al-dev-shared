# AL LSP Guidance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update shared `profile-al-dev-shared` guidance so AL LSP is described as an optional preferred semantic navigation provider while preserving AL MCP and text-search fallbacks.

**Architecture:** Add a harness-neutral `AL semantic navigation` concept, then thread evidence-source labels through symbol pre-flight, planning, development, architect, developer, and performance guidance. Keep this as documentation-only profile guidance: no generated projections, manifests, helper scripts, or runtime `al launchlspserver` integration.

**Tech Stack:** Markdown profile guidance, YAML frontmatter-bearing skill and agent files, repo validation scripts, `rg`.

---

## File Structure

Modify these files only:

- `profile-al-dev-shared/knowledge/harness-concepts.md` — define the generic `AL semantic navigation` concept and evidence-source vocabulary without raw harness tool IDs.
- `profile-al-dev-shared/knowledge/al-symbol-pre-flight.md` — make semantic verification the preferred path, retain AL MCP examples as concrete fallback, and require evidence-source labels.
- `profile-al-dev-shared/skills/al-dev-plan/SKILL.md` — prefer semantic navigation during Phase 1 base-app/project pre-research and Phase 1.5 external symbol verification.
- `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` — prefer semantic navigation during autonomous signature verification and developer pre-flight, and require evidence-source reporting.
- `profile-al-dev-shared/agents/al-dev-solution-architect.md` — require verification-source labels in schema mapping and external symbol evidence.
- `profile-al-dev-shared/agents/al-dev-developer.md` — require named evidence source before AL code is written.
- `profile-al-dev-shared/skills/al-dev-perf/SKILL.md` — allow semantic document symbols for codeunit classification, with AL MCP and text fallback.

Do not modify:

- `profile-al-dev-shared/generated/**`
- `.claude/**`
- `.claude-plugin/**`
- `scripts/**`
- plugin manifests or marketplace files

### Evidence Labels Contract

Use these exact labels in all changed guidance:

```text
AL LSP
AL MCP
text search
unverified
```

Meaning:

```text
AL LSP: workspace-semantic verification from an active harness or adapter that exposes AL language-server operations.
AL MCP: object, member, reference, or package symbol verification through al-mcp-server.
text search: scoped textual verification, weaker than semantic verification.
unverified: required symbol evidence was not established; stop or escalate before implementation if the symbol is required.
```

## Task 1: Add Harness-Neutral Semantic Navigation Concept

**Files:**
- Modify: `profile-al-dev-shared/knowledge/harness-concepts.md`

- [ ] **Step 1: Write the failing concept check**

Run:

```bash
rg -n "AL semantic navigation|AL LSP|text search|unverified" profile-al-dev-shared/knowledge/harness-concepts.md
```

Expected before implementation: FAIL or incomplete output. The file currently defines `MCP: al-mcp-server` but does not define `AL semantic navigation` or the four evidence labels.

- [ ] **Step 2: Add authoring guidance**

In `profile-al-dev-shared/knowledge/harness-concepts.md`, under `## Skill Author Guidelines`, add these bullets after `Reference MCP tools by capability name — never by raw harness-specific tool ID`:

```markdown
- Use `AL semantic navigation` when guidance needs symbol-aware AL operations
  such as definition lookup, reference search, document symbols, hover/type
  information, or rename-impact checks
- Treat AL LSP as an optional provider of `AL semantic navigation` only when
  the active harness or adapter exposes it; do not assume availability from
  ALTool documentation alone
- Label symbol evidence as `AL LSP`, `AL MCP`, `text search`, or `unverified`
  whenever the distinction affects planning, implementation, or risk
```

- [ ] **Step 3: Add the generic concept table row**

In the `## Generic Concept Vocabulary` table, add this row immediately before `MCP: al-mcp-server`:

```markdown
| **AL semantic navigation** | Preferred symbol-aware AL workspace operations: go-to-definition, find-references, document symbols, hover/type information, and rename/refactor impact checks. Providers are harness-dependent and optional. | AL LSP when exposed by Claude Code or an adapter; otherwise use supported AL symbol tools | AL LSP when exposed by Copilot CLI or an adapter; otherwise use supported AL symbol tools | AL LSP when exposed by the active Codex environment or adapter; otherwise use supported AL symbol tools |
```

- [ ] **Step 4: Add evidence-source semantics section**

After the `## USER_GATE Semantics` section and before `## AL_DEV_SHARED_PLUGIN_ROOT`, add:

```markdown
## AL Semantic Navigation and Evidence Labels

`AL semantic navigation` is a generic capability, not a required tool. Use it
when the active harness exposes a workspace-aware AL semantic provider such as
AL LSP through the harness itself or an adapter.

Preferred order for AL symbol questions:

1. `AL LSP` — workspace-semantic verification for go-to-definition,
   find-references, document symbols, hover/type information, and rename or
   refactor impact checks.
2. `AL MCP` — object/member/package symbol verification through
   `al-mcp-server`, including object definitions, member searches, and
   reference lookup.
3. `text search` — tightly scoped `rg` or file-read evidence when no semantic
   provider is available. Report this as text-verified only.
4. `unverified` — required symbol evidence was not established. Stop or
   escalate before implementation if the symbol is required.

Do not claim AL LSP is available because ALTool documentation exists. Use AL
LSP only when the active harness exposes an LSP-capable tool or adapter.
```

- [ ] **Step 5: Verify concept wording**

Run:

```bash
rg -n "AL semantic navigation|AL LSP|AL MCP|text search|unverified|launchlspserver" profile-al-dev-shared/knowledge/harness-concepts.md
```

Expected: PASS with `AL semantic navigation`, all four evidence labels, and no `launchlspserver` matches.

- [ ] **Step 6: Commit**

```bash
git add profile-al-dev-shared/knowledge/harness-concepts.md
git commit -m "docs: add AL semantic navigation concept"
```

## Task 2: Reframe Symbol Pre-Flight Around Evidence Sources

**Files:**
- Modify: `profile-al-dev-shared/knowledge/al-symbol-pre-flight.md`

- [ ] **Step 1: Write the failing evidence-label check**

Run:

```bash
rg -n "Evidence source|AL LSP|AL MCP|text search|unverified|semantically verified|text-verified" profile-al-dev-shared/knowledge/al-symbol-pre-flight.md
```

Expected before implementation: FAIL or incomplete output. The file currently gives MCP commands but does not require source labels.

- [ ] **Step 2: Replace the purpose text**

In `## Purpose`, replace the two paragraphs after the first sentence with:

```markdown
Missing `var` modifiers and non-existent field names are the top two causes
of subagent-generated compile failures. This checklist catches them at design
time by requiring each required symbol to be verified through the strongest
available evidence source.

Preferred verification order:

1. `AL LSP` — use when the active harness or adapter exposes workspace-aware
   AL semantic operations such as go-to-definition, find-references, document
   symbols, hover/type information, or rename-impact checks.
2. `AL MCP` — use `al-mcp-server` for object definitions, member searches,
   references, and package/base-app symbol exploration.
3. `text search` — use tightly scoped `rg` searches only when no semantic
   provider is available; label the result as text-verified only.
4. `unverified` — do not guess required fields, events, procedures, or object
   names. Stop and report the blocker.
```

- [ ] **Step 3: Update field reference guidance**

In `### 1. Field References`, replace the line `For every base-table field you plan to reference, verify it exists:` and the MCP-only command lead-in with this exact Markdown:

~~~markdown
For every base-table field you plan to reference, verify it exists using the
strongest available evidence source. Prefer `AL LSP` workspace-semantic lookup
when available. Otherwise use `AL MCP`:

```text
al_get_object_definition(objectType: 'Table', objectName: 'Sales Header')
```

If neither semantic provider is available, use a tightly scoped text search and
label the result as `text search`, for example:

```bash
rg -n 'field\([0-9]+; "Document Type"' src .alpackages
```
~~~

- [ ] **Step 4: Update event subscriber guidance**

In `### 2. Event Subscriber Signatures`, replace the lead-in before the checklist with this exact Markdown:

~~~markdown
For every event publisher you plan to subscribe to, prefer `AL LSP`
find-references or hover/signature information when available. Otherwise use
`AL MCP`:

```text
al_search_object_members(searchTerm: 'OnAfterPostSalesDoc', objectType: 'Codeunit')
```
~~~

Replace `If the MCP result is ambiguous` with:

```markdown
If semantic lookup is unavailable or ambiguous, use `al_find_references` to
locate the publisher source and read its exact signature. If the only evidence
is `rg`, label the result as `text search` and include the exact file:line
evidence in the pre-flight summary.
```

- [ ] **Step 5: Update object lookup guidance**

In `### 4. Object Types You Extend`, replace the lead-in with this exact Markdown:

~~~markdown
For every object you write a table/page/codeunit extension for, prefer
workspace-semantic lookup through `AL LSP` when available. Otherwise use
`AL MCP`:

```text
al_search_objects(searchTerm: 'Customer', objectType: 'Table')
```
~~~

- [ ] **Step 6: Replace the pre-flight summary template**

In `## Gate`, replace the summary block with:

```text
Pre-flight complete:
- Evidence sources used: [AL LSP / AL MCP / text search]
- Fields verified: [field name -> source label + evidence, or "none referenced"]
- Events verified: [event name -> source label + var-params confirmed, or "none"]
- Objects verified: [object name -> source label + evidence, or "none"]
- Object names: [all ≤30 chars — confirmed]
- Object IDs: [in range 50100–50199, no conflicts]
- Text-verified only: [items verified by text search, or "none"]
- Unverified: [required item and reason, or "none"]
```

Replace the final sentence with:

```markdown
If any required item cannot be verified by `AL LSP`, `AL MCP`, or scoped text
search, do NOT guess. Report it as `unverified` and stop until the orchestrator
or user provides guidance.
```

- [ ] **Step 7: Verify symbol pre-flight wording**

Run:

```bash
rg -n "Evidence sources used|AL LSP|AL MCP|text search|Text-verified only|Unverified|Do NOT guess" profile-al-dev-shared/knowledge/al-symbol-pre-flight.md
```

Expected: PASS with matches for all labels and the updated summary fields.

- [ ] **Step 8: Commit**

```bash
git add profile-al-dev-shared/knowledge/al-symbol-pre-flight.md
git commit -m "docs: label AL symbol preflight evidence"
```

## Task 3: Update Planning and Development Skill Guidance

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`

- [ ] **Step 1: Write failing skill checks**

Run:

```bash
rg -n "AL semantic navigation|AL LSP|AL MCP|text search|unverified|evidence source" profile-al-dev-shared/skills/al-dev-plan/SKILL.md profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected before implementation: FAIL or incomplete output. The skills currently describe AL MCP but not semantic navigation or source-labeled verification.

- [ ] **Step 2: Update `al-dev-plan` Phase 1 pre-research**

In `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, replace Phase 1 step 4 with:

```markdown
4. Pre-research base app and project integration points using the
   strongest available AL symbol evidence before spawning architects.
   Prefer `AL semantic navigation` when the active harness exposes an
   `AL LSP` provider or adapter:
   - go-to-definition — confirm where relevant objects, procedures, and
     events are defined
   - find-references — understand subscriber/refactor impact
   - document symbols — identify object members and event publishers
   - hover/type information — confirm field, procedure, and parameter types

   If `AL LSP` is unavailable, use the AL Symbols MCP (`al-mcp-server`):
   - `al_search_objects` — find relevant base app tables,
     pages, or codeunits the feature will extend or interact
     with (e.g. "Sales Header", "Customer", "Item")
   - `al_get_object_definition` — inspect the fields,
     triggers, and events on key base objects
   - `al_search_object_members` — locate existing events or
     procedures the solution can subscribe to

   If no semantic provider is available, use tightly scoped `rg`
   searches and label the result as `text search` rather than
   semantically verified.

   Include findings and their evidence source (`AL LSP`, `AL MCP`,
   `text search`, or `unverified`) in every architect prompt so architects
   start from real object knowledge, not assumptions.

   If no provider is available or no results are returned (e.g., no BC
   workspace is active), proceed directly to Phase 2 using general AL
   knowledge. Do not stop unless a required symbol is marked `unverified`.
```

- [ ] **Step 3: Update `al-dev-plan` Phase 1.5 symbol verification**

In `profile-al-dev-shared/skills/al-dev-plan/SKILL.md`, replace Phase 1.5 step 2 with:

```markdown
2. **Symbol/API verification:** For each function, procedure, field, or table mentioned:
   - Prefer `AL semantic navigation` (`AL LSP`) when the active harness exposes it:
     go-to-definition for definitions, find-references for usage, document
     symbols for members, and hover/type information for signatures
   - If `AL LSP` is unavailable, use AL MCP (`al_search_objects`,
     `al_search_object_members`, `al_get_object_definition`, or
     `al_find_references`) to confirm the symbol exists
   - If no semantic provider is available, use scoped text search:
     `rg -n "symbol_name" src/ --glob "*.al"`
   - Record the evidence source as `AL LSP`, `AL MCP`, `text search`, or
     `unverified`
   - If not found → mark as **unverified**
   - If found but context differs → mark as **partially verified**
```

Then replace the evidence table in Phase 1.5 step 3 with:

```markdown
| Claim | Type | Status | Evidence Source | Evidence |
| --- | --- | --- | --- | --- |
| "File X has problem Y" | file+issue | Verified | text search | File exists, issue confirmed at line Z |
| "Function Q is slow" | performance | Unverified | unverified | Function exists but no profiling data provided |
| "Table R has no indexes" | schema | Verified | AL MCP | Object definition confirms table R, no key definitions found |
```

- [ ] **Step 4: Update `al-dev-plan` architect tool verification**

In Phase 3, replace the `Verify architects use MCP tools:` bullet and its sub-bullets with:

```markdown
4. Verify architects use available semantic evidence:
   - AL semantic navigation (`AL LSP`) when the active harness exposes it for
     definition lookup, references, document symbols, hover/type information,
     and rename/refactor impact checks
   - AL Symbols MCP (`al-mcp-server`) for base app object exploration
     (`al_search_objects`, `al_get_object_definition`, `al_find_references`)
   - BC Code Intelligence for architecture patterns
   - MS Docs for BC API documentation
   - Scoped text search only as a weaker fallback, labeled `text search`
```

- [ ] **Step 5: Update `al-dev-develop` glossary and Phase 1.5**

In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, replace the Phase 1.5 glossary paragraph with:

```markdown
**Phase 1.5 (Autonomous):** Optional signature verification phase
activated by the `--autonomous` flag. Uses the strongest available
AL symbol evidence before developers are spawned: `AL LSP` through
an active harness or adapter when available, otherwise AL Symbols MCP,
otherwise scoped text search labeled as weaker evidence. This reduces
downstream compilation errors.
```

Then replace the first three paragraphs of `## Phase 1.5: Signature Verification (--autonomous only)` with:

```markdown
Skip this phase if `--autonomous` is not in `$ARGUMENTS`.

Before dispatching any developer, verify every external procedure
signature using the strongest available AL symbol evidence.

Preferred order:

1. `AL LSP` through active harness/adaptor semantic operations:
   go-to-definition, find-references, document symbols, and hover/type
   information.
2. `AL MCP` through `al-mcp-server`:
```

Keep the existing MCP command list immediately after that, then add this paragraph after the command list:

```markdown
3. `text search` through scoped `rg` only when no semantic provider is
   available. Text-search evidence must be labeled as weaker evidence and
   include file:line references.
```

- [ ] **Step 6: Update the autonomous signatures report format**

In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, replace the `Verified Signatures` example block with:

```markdown
## Verified Signatures

### [ObjectType] [ObjectName].[ProcedureName]
- Parameters: [ParamName: Type; var ParamName: Type]
- Return: [Type or void]
- Evidence source: [AL LSP / AL MCP / text search]
- Evidence: [go-to-definition result / al_search_object_members / file:line]
- Verified: [ISO timestamp]

### NOT VERIFIED: [ProcedureName]
- Evidence source: unverified
- Reason: [not found in semantic provider / ambiguous match / no provider available]
- Risk: Developer must not guess this signature
```

- [ ] **Step 7: Update developer spawn pre-flight text**

In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, inside the Phase 3 developer prompt, replace the `SYMBOL_PREFLIGHT_GATE` required checks section with:

```text
SYMBOL_PREFLIGHT_GATE — Complete BEFORE writing any AL code.
Follow `knowledge/al-symbol-pre-flight.md` for the full checklist.
Use the strongest available evidence source and label each item:
1. AL LSP when the active harness exposes workspace-semantic navigation
   for definitions, references, document symbols, hover/type information,
   or rename/refactor impact checks
2. AL MCP through al-mcp-server for object definitions, member searches,
   references, and package/base-app symbol exploration
3. text search only as a weaker scoped fallback with exact file:line evidence
4. unverified when required symbol evidence cannot be established

Required checks:
1. Field references: verify each base field with source label
   (exact field name, including spacing and capitalisation)
2. Event signatures: verify every var parameter in the publisher and label
   the source; missing var = AL0118 compile error
3. Object names: count characters — each must be ≤30
4. Object IDs: confirm all are in your assigned range with no duplicates

Report your pre-flight summary before writing a single line of AL:
"Pre-flight complete: evidence sources used [AL LSP/AL MCP/text search],
fields verified [list + source], events verified [list + source],
objects verified [list + source], names/IDs OK [or: issue found],
unverified [none or list]."

DO NOT proceed past pre-flight if any required item is unverified.
Stop and report back to the orchestrator with the unverified item.
```

- [ ] **Step 8: Verify skill wording**

Run:

```bash
rg -n "AL semantic navigation|AL LSP|AL MCP|text search|unverified|Evidence source|Evidence sources used|rename/refactor impact" profile-al-dev-shared/skills/al-dev-plan/SKILL.md profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: PASS with matches in both skill files.

- [ ] **Step 9: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-plan/SKILL.md profile-al-dev-shared/skills/al-dev-develop/SKILL.md
git commit -m "docs: prefer semantic AL evidence in workflows"
```

## Task 4: Update Architect and Developer Agent Contracts

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-solution-architect.md`
- Modify: `profile-al-dev-shared/agents/al-dev-developer.md`

- [ ] **Step 1: Write failing agent checks**

Run:

```bash
rg -n "Evidence Source|AL LSP|AL MCP|text search|unverified|semantic navigation" profile-al-dev-shared/agents/al-dev-solution-architect.md profile-al-dev-shared/agents/al-dev-developer.md
```

Expected before implementation: FAIL or incomplete output.

- [ ] **Step 2: Update architect research workflow**

In `profile-al-dev-shared/agents/al-dev-solution-architect.md`, replace research phase step 4 with:

```markdown
4. **Research phase (MEDIUM/COMPLEX only):**
   - AL semantic navigation: use `AL LSP` when the active harness exposes it
     for definitions, references, document symbols, hover/type information,
     and rename/refactor impact checks
   - Base app exploration: if `AL LSP` is unavailable, use AL MCP Server
     (`al_get_object_definition`, `al_find_references`, `al_search_objects`)
   - Architecture questions: Use BC Code Intelligence (`ask_bc_expert`)
   - Official patterns: Use Microsoft Docs (`microsoft_docs_search`)
   - Text fallback: use scoped text search only when no semantic provider is
     available, and label it as `text search`
```

Replace `**MCP Tools:** Use AL MCP Server first...` with:

```markdown
**Symbol Evidence:** Prefer `AL LSP` semantic navigation when exposed by the
active harness or adapter. Use AL MCP Server for base app and package symbol
exploration when LSP is unavailable. Use scoped text search only as a weaker
fallback and label it `text search`.
```

- [ ] **Step 3: Update architect schema mapping table**

In `## Schema Mapping Decisions`, replace the table with:

```markdown
| Field/Table | Source | Exists? | Evidence Source | Rationale | Risk |
|-----------|--------|---------|-----------------|-----------|------|
| G/L Register No. | G/L Entry | NO | AL MCP | Use "Entry No." (PK) instead | Low |
| Customer Type | Customer | YES | AL LSP | Link to code in AC_CUSTOMER_TYPE | Low |
| Document No. | Purch. Header | YES | text search | Primary document identifier; text-verified only | Medium |
```

Replace the format bullets with:

```markdown
**Format per mapping:**
- **[Field Name]** in [Source Table]: [YES/NO]
  - Evidence Source: [AL LSP / AL MCP / text search / unverified]
  - Evidence: [semantic operation, MCP query, or exact file:line]
  - Alternative: [If field doesn't exist, what should be used?]
  - Rationale: [Why this choice is correct]
  - Risk: [Low/Medium/High — data integrity implications]
```

Add this sentence after the format bullets:

```markdown
If a required external symbol is `unverified`, do not design code that depends
on guessing its signature or existence; call out the blocker in the plan.
```

- [ ] **Step 4: Update developer standards**

In `profile-al-dev-shared/agents/al-dev-developer.md`, replace the first paragraph under `### AL Code Patterns` with:

```markdown
Before writing any AL code, complete the symbol pre-flight checklist
(`knowledge/al-symbol-pre-flight.md`). This is enforced by
`SYMBOL_PREFLIGHT_GATE` — report your pre-flight summary before implementation
begins. The summary must name the evidence source for each required symbol:
`AL LSP`, `AL MCP`, `text search`, or `unverified`.
```

Add this paragraph immediately after it:

```markdown
Prefer `AL LSP` semantic navigation when the active harness exposes it for
definition lookup, references, document symbols, hover/type information, and
rename/refactor impact checks. If unavailable, use AL MCP. Use scoped text
search only as a weaker fallback with exact file:line evidence. Stop before
implementation if a required symbol remains `unverified`.
```

- [ ] **Step 5: Verify agent wording and frontmatter neutrality**

Run:

```bash
rg -n "Evidence Source|AL LSP|AL MCP|text search|unverified|semantic navigation|rename/refactor impact" profile-al-dev-shared/agents/al-dev-solution-architect.md profile-al-dev-shared/agents/al-dev-developer.md
```

Expected: PASS with matches in both agent files.

Run:

```bash
sed -n '1,20p' profile-al-dev-shared/agents/al-dev-solution-architect.md
sed -n '1,20p' profile-al-dev-shared/agents/al-dev-developer.md
```

Expected: Frontmatter remains valid. Do not add raw AL LSP tool IDs to `tools:`.

- [ ] **Step 6: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-solution-architect.md profile-al-dev-shared/agents/al-dev-developer.md
git commit -m "docs: require symbol evidence labels in agents"
```

## Task 5: Update Performance Classification Fallbacks

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-perf/SKILL.md`

- [ ] **Step 1: Write failing performance guidance check**

Run:

```bash
rg -n "document symbols|AL LSP|AL MCP|text search|Evidence source" profile-al-dev-shared/skills/al-dev-perf/SKILL.md
```

Expected before implementation: FAIL or incomplete output. The file currently only names AL Symbols MCP plus a Utility fallback.

- [ ] **Step 2: Replace Step 1a provider wording**

In `### Step 1a — Identify Entry-Point Metadata`, replace the first paragraph and MCP bullet list with this exact Markdown:

~~~markdown
For each codeunit found in Step 1, use the strongest available symbol evidence
to classify it before spawning the analysis agent. Prefer `AL LSP` document
symbols when the active harness exposes semantic navigation. Otherwise use
`AL MCP`:

- `al_get_object_summary` — check for OnRun() and codeunit type
- `al_search_object_members` — detect event subscriber attributes

If no semantic provider is available, use scoped text search:

```bash
rg -n "trigger OnRun\\(|\\[EventSubscriber\\]|codeunit [0-9]+ .*Batch|codeunit [0-9]+ .*Process|codeunit [0-9]+ .*Import|codeunit [0-9]+ .*Post|codeunit [0-9]+ .*Transfer|codeunit [0-9]+ .*Run" src --glob "*.al"
```
~~~

- [ ] **Step 3: Add source labels to the classification summary**

Replace the summary example with:

```text
Codeunit classifications:
- CreateJobV6.Codeunit.al → Entry Point (has OnRun; evidence source: AL LSP)
- BatchPostSales.Codeunit.al → Batch Processor (name heuristic; evidence source: text search)
- StringHelper.Codeunit.al → Utility (no indicators found; evidence source: AL MCP)
```

Replace `If al-mcp-server is unavailable or returns no result for a codeunit, default to Utility (no modifier). Do not block the analysis.` with:

```markdown
If neither `AL LSP` nor `AL MCP` is available and scoped text search finds no
entry-point indicators, default to Utility (no modifier). Do not block the
analysis. Label the source as `text search` if the fallback search ran, or
`unverified` if no lookup could be performed.
```

- [ ] **Step 4: Update the Step 2 prompt**

In the Step 2 prompt, replace:

```text
   Codeunit classifications (from AL Symbols pre-research):
```

with:

```text
   Codeunit classifications (with evidence source labels: AL LSP, AL MCP, text search, or unverified):
```

- [ ] **Step 5: Update Notes**

Replace the note beginning `AL Symbols lookup (Step 1a) enriches severity...` with:

```markdown
- Symbol lookup (Step 1a) enriches severity by context. Prefer `AL LSP`
  document symbols when available, otherwise use `AL MCP`, then scoped text
  search. If no lookup can be performed, fall back to equal-weight analysis and
  label classification evidence as `unverified`.
```

- [ ] **Step 6: Verify performance guidance**

Run:

```bash
rg -n "document symbols|AL LSP|AL MCP|text search|unverified|evidence source" profile-al-dev-shared/skills/al-dev-perf/SKILL.md
```

Expected: PASS with provider order and evidence-source labels.

- [ ] **Step 7: Commit**

```bash
git add profile-al-dev-shared/skills/al-dev-perf/SKILL.md
git commit -m "docs: classify performance scope with semantic evidence"
```

## Task 6: Validate Guidance-Only Scope

**Files:**
- Verify only: `profile-al-dev-shared/**`
- Verify only: `profile-al-dev-shared/generated/**`
- Verify only: `.claude/**`
- Verify only: `.claude-plugin/**`

- [ ] **Step 1: Confirm only intended files changed**

Run:

```bash
git diff --name-only HEAD
```

Expected output exactly these paths:

```text
profile-al-dev-shared/agents/al-dev-developer.md
profile-al-dev-shared/agents/al-dev-solution-architect.md
profile-al-dev-shared/knowledge/al-symbol-pre-flight.md
profile-al-dev-shared/knowledge/harness-concepts.md
profile-al-dev-shared/skills/al-dev-develop/SKILL.md
profile-al-dev-shared/skills/al-dev-perf/SKILL.md
profile-al-dev-shared/skills/al-dev-plan/SKILL.md
```

If the current task commits were made separately, run this instead to inspect the branch range:

```bash
git diff --name-only master...HEAD
```

Expected: the same seven paths.

- [ ] **Step 2: Confirm generated and manifest files are untouched**

Run:

```bash
git diff --name-only HEAD -- profile-al-dev-shared/generated .claude .claude-plugin scripts
```

Expected: no output.

- [ ] **Step 3: Run harness neutrality validation**

Run:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected: PASS with no harness-specific leakage errors.

- [ ] **Step 4: Run agent structure validation**

Run:

```bash
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
```

Expected: PASS. If it fails on the changed agent files, fix frontmatter or tool declarations without adding AL LSP raw tool IDs.

- [ ] **Step 5: Run projection-sensitive tests because agent files changed**

Run:

```bash
python3 scripts/tests/test_generate_agent_projections.py
```

Expected: PASS. This verifies projection behavior without editing generated projections.

- [ ] **Step 6: Search for hard dependency language**

Run:

```bash
rg -n "must use LSP|required LSP|requires LSP|launchlspserver|al launchlspserver|ALTool" profile-al-dev-shared/knowledge profile-al-dev-shared/skills profile-al-dev-shared/agents
```

Expected: no output. If a sentence needs to say LSP is preferred, use `prefer AL LSP when the active harness exposes it` or equivalent optional wording.

- [ ] **Step 7: Search for stale MCP-only phrasing**

Run:

```bash
rg -n "Use AL MCP Server first|via MCP, do NOT guess|AL Symbols MCP \\(`al-mcp-server`\\) before|MCP result is ambiguous|from AL Symbols pre-research" profile-al-dev-shared/knowledge/al-symbol-pre-flight.md profile-al-dev-shared/skills/al-dev-plan/SKILL.md profile-al-dev-shared/skills/al-dev-develop/SKILL.md profile-al-dev-shared/skills/al-dev-perf/SKILL.md profile-al-dev-shared/agents/al-dev-solution-architect.md profile-al-dev-shared/agents/al-dev-developer.md
```

Expected: no output. Replace stale MCP-only wording with semantic-first wording and explicit fallback labels.

- [ ] **Step 8: Verify evidence labels are present in every changed file**

Run:

```bash
for file in \
  profile-al-dev-shared/knowledge/harness-concepts.md \
  profile-al-dev-shared/knowledge/al-symbol-pre-flight.md \
  profile-al-dev-shared/skills/al-dev-plan/SKILL.md \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/agents/al-dev-solution-architect.md \
  profile-al-dev-shared/agents/al-dev-developer.md \
  profile-al-dev-shared/skills/al-dev-perf/SKILL.md
do
  printf '%s\n' "$file"
  rg -n "AL LSP|AL MCP|text search|unverified" "$file"
done
```

Expected: each file prints at least one match for the evidence-label vocabulary, with the strongest wording in `harness-concepts.md` and `al-symbol-pre-flight.md`.

- [ ] **Step 9: Commit validation fixes**

If validation required edits, commit them:

```bash
git add profile-al-dev-shared/knowledge/harness-concepts.md profile-al-dev-shared/knowledge/al-symbol-pre-flight.md profile-al-dev-shared/skills/al-dev-plan/SKILL.md profile-al-dev-shared/skills/al-dev-develop/SKILL.md profile-al-dev-shared/agents/al-dev-solution-architect.md profile-al-dev-shared/agents/al-dev-developer.md profile-al-dev-shared/skills/al-dev-perf/SKILL.md
git commit -m "docs: validate AL semantic guidance wording"
```

If no validation edits were needed, do not create an empty commit.

## Self-Review Checklist

- [ ] Spec coverage: all seven target files have a task, and the out-of-scope list prevents generated projection, manifest, script, and runtime dependency edits.
- [ ] Optionality: every AL LSP reference says it is used only when the active harness or adapter exposes it.
- [ ] Fallbacks: AL MCP remains a valid concrete provider; text search is labeled weaker; required unknowns are labeled `unverified`.
- [ ] Evidence labels: plans, pre-flight summaries, agent outputs, and performance classifications can distinguish `AL LSP`, `AL MCP`, `text search`, and `unverified`.
- [ ] Validation: harness neutrality, agent validation, projection-sensitive test, hard-dependency search, stale MCP-only search, and changed-file scope check are all included.
