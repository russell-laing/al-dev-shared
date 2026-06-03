# Security Review Examples

Used by: `al-dev-security-reviewer` agent

These are review examples for spotting common security issues in AL/BC.
Treat them as illustrative patterns, not production-ready snippets to copy verbatim.

## Common Security Issues in AL/BC

### SQL Injection via String Concatenation

Why it matters: Concatenated query text turns untrusted input into executable logic and can expose or corrupt data.

**Bad:**
```al
query := 'SELECT * FROM ' + tableName;
// DO NOT execute this — tableName could contain SQL
```

**Good:**
```al
// Use filters instead of string concatenation
rec.SetFilter("Name", '%' + searchTerm + '%');
rec.FindSet();
```

### Credential Storage

Why it matters: Plain-text credential handling increases the risk of accidental disclosure through tables, logs, exports, or debugging.

**Bad:**
```al
procedure StoreApiKey(key: Text)
begin
  APIKey := key;  // Plain text field
end;
```

**Good:**
```al
// Use credential management APIs or secure storage
IsolatedStorage.Set(ApiKeyLabel, apiKey, DataScope::Module);
```

### Permission Elevation Risks

Why it matters: User-name checks are brittle and can bypass the platform's intended permission model.

**Bad:**
```al
procedure AdminOperation()
begin
  if UserId() = 'Admin' then
    // Allow sensitive operation
  else
    Error('Not authorized');
end;
```

**Good:**
```al
// Use explicit permission sets
if not UserPermissions.CanExecute(ObjectType::Codeunit, Codeunit::"SensitiveOp") then
  Error('Insufficient permissions');
```

### Data Exposure in Logs

Why it matters: Secrets and sensitive identifiers written to logs often persist beyond the original operation and widen the blast radius of an incident.

**Bad:**
```al
Message('Processing record: ' + RecordKey + ' with password: ' + Password);
```

**Good:**
```al
// Only log non-sensitive information
Message('Processing record: ' + RecordKey);
```

### Insufficient Input Validation

Why it matters: Unvalidated input can cause data corruption, unexpected runtime failures, or downstream security problems.

**Bad:**
```al
procedure ProcessInput(userInput: Text)
begin
  // Directly use userInput without validation
  rec.Field := userInput;
end;
```

**Good:**
```al
procedure ProcessInput(userInput: Text)
begin
  if StrLen(userInput) > MaxLength then
    Error('Input exceeds maximum length');
  if not IsValidFormat(userInput) then
    Error('Invalid format');
  rec.Field := userInput;
end;
```
