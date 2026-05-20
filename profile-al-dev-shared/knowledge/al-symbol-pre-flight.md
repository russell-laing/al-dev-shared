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
