# Security Review Code Examples

Referenced by: `al-dev-security-reviewer` agent

## Common Security Issues in AL/BC

### SQL Injection via String Concatenation

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
