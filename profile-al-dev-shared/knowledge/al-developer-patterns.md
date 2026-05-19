# AL Developer Patterns and Conventions

Referenced by: `al-dev-developer` agent

## Standard AL Patterns

### RecordRef Operations
Pattern for operations on record references with error handling.

Example: Use RecordRef for dynamic table access when the table isn't known at compile time. Always validate the table ID before operations.

### Query Performance Best Practices
When writing queries, use filters to reduce record set scope; avoid FINDSET in loops. Instead, collect IDs and batch-process.

### Record Modification Patterns
Use ModifyAll for batch updates. For single-record updates, use Modify with error checking.

## Common AL Mistakes to Avoid

### Incorrect Event Subscriber Signature
Do not use incompatible parameter types. Event subscribers must match the event's exact signature (including var parameters). Use the AL symbols MCP to verify procedure signatures before writing subscribers.

### Performance Anti-Pattern: N+1 Queries
Use batch operations instead of record-by-record processing. Load all data first, then process in-memory when possible.

### Unreferenced Variables
Remove unused variables. They clutter the code and indicate dead code paths.

## Error Handling Rules

### String Substitution with Labels
Use `Error(label, args)` instead of `Error(StrSubstNo(...))` to satisfy AA0231.

Good:
```al
Error(SomeLabel, fieldValue);
```

Bad:
```al
Error(StrSubstNo(SomeLabel, fieldValue));
```

### User-Facing Errors
Wrap in Error() function with user-friendly message text. Avoid exposing internal IDs or technical details.

### Handling Missing Information
If implementation requires clarification from the user, stop and ask. Document what information is missing and why it matters.

## AL Naming Conventions

- Object names must be ≤30 characters
- Use AL prefix convention (e.g., prefix `ARR` for array processing codeunits)
- Be descriptive: `PaymentProcessor` is better than `Proc`
