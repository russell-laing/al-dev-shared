# AL Symbol Pre-Flight Checklist

Referenced by: `developer-tdd` and `developer-traditional`
agents (`SYMBOL_PREFLIGHT_GATE`), `develop-orchestrate` skill Phase 3 spawn
prompt.

## Purpose

Complete this checklist before writing any AL code. It prevents the most
common cause of compilation errors: referencing fields, events, or procedures
that don't exist in the base app or in the project's own objects.

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

   > **Definition of `unverified`:** A symbol is unverified when it cannot be
   > located via AL LSP query, AL MCP lookup, or scoped text search with
   > documented `file:line` evidence.

## Pre-Flight Checklist

### 1. Field References

For every base-table field you plan to reference, verify it exists using the
strongest available evidence source. Prefer `AL LSP` workspace-semantic lookup
when available. Otherwise use `AL MCP`:

```text
al_get_object_definition(objectType: 'Table', objectName: 'Sales Header')
```

If neither semantic provider is available, use a tightly scoped text search and
label the result as `text search`. Adjust the search roots to the project
layout, for example:

```bash
rg -n 'field\([0-9]+; "Document Type"' src .alpackages
```

- [ ] Field name is exact (including spacing, e.g., `"Sell-to Customer No."`)
- [ ] Field data type matches your intended usage
- [ ] Field exists in the version of BC the project targets

**Common mistake:** Referencing `"Document Type Option"` as `"Document Type"`, or
using a field that exists in W1 but not in a localized base app.

### 2. Event Subscriber Signatures

For every event publisher you plan to subscribe to, prefer `AL LSP`
find-references or hover/signature information when available. Otherwise use
`AL MCP`:

```text
al_search_object_members(
  objectName: 'Sales-Post',
  objectType: 'Codeunit',
  memberType: 'procedures',
  pattern: 'OnAfterPostSalesDoc',
  includeDetails: true)
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

If `AL LSP` lookup is unavailable or ambiguous, use `AL MCP` such as
`al_find_references` to locate the publisher source and read its exact
signature. If the only evidence is `rg`, label the result as `text search` and
include the exact file:line evidence in the pre-flight summary.

### 3. Object Names and IDs

For every new object you plan to create:

- [ ] Object name is ≤ 30 characters (BC hard limit — count manually)
- [ ] Object name includes the project prefix from the plan
- [ ] Object ID is within your assigned range (specified in the solution plan)
- [ ] No existing object uses the same ID:

```bash
rg -n '^(table|tableextension|page|pageextension|codeunit|enum|enumextension|report|xmlport|query)\s+<YOUR_ID>\s' .
```

### 4. Object Types You Extend

For every object you write a table/page/codeunit extension for, prefer
workspace-semantic lookup through `AL LSP` when available. Otherwise use
`AL MCP`:

```text
al_search_objects(pattern: 'Customer', objectType: 'Table')
```

- [ ] Object type is correct (extending a `Table`, not a `TableExtension`)
- [ ] Object name exactly matches (including quotes if the base name has spaces)

## Gate

**Do not write any AL code until this checklist is complete.**

Report a pre-flight summary before beginning implementation:

```text
Pre-flight complete:
- Evidence sources used: [AL LSP / AL MCP / text search]
- Fields verified: [field name -> source label + evidence, or "none referenced"]
- Events verified: [event name -> source label + var-params confirmed, or "none"]
- Objects verified: [object name -> source label + evidence, or "none"]
- Object names: [all ≤30 chars — confirmed]
- Object IDs: [in assigned range from the solution plan, no conflicts]
- Text-verified only: [items verified by text search, or "none"]
- Unverified: [required item and reason, or "none"]
```

If any required item cannot be verified by `AL LSP`, `AL MCP`, or scoped text
search, do NOT guess. Report it as `unverified` and stop until the orchestrator
or user provides guidance.
