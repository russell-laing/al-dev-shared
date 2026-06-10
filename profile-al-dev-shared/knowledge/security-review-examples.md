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

### Authorization Propagation Gap

Why it matters: A page-level `OnOpenPage` guard only protects that page. A
public management codeunit called by the page is independently reachable from
API pages, test codeunits, or future code, bypassing the guard entirely.

**Bad — guard only at page, codeunit is public:**

```al
// Page has OnOpenPage guard — but Cod50504 has no Access modifier
codeunit 50504 "ACAKAU08 Email Retry Mgt."   // callable by any extension
{
    procedure RetryRecord(var Entry: Record "...")
    begin
        // No caller check
    end;
}
```

**Good — codeunit restricted to this extension:**

```al
codeunit 50504 "ACAKAU08 Email Retry Mgt."
{
    Access = Internal;   // only callable within this extension
    procedure RetryRecord(var Entry: Record "...")
    begin
        // Caller is already trusted (same extension)
    end;
}
```

**Review checklist item:** For every page with an `OnOpenPage` authorization
guard, check every public codeunit it calls. If the codeunit is only intended
to be called from within this extension, it must have `Access = Internal` or
an inline caller-identity guard.

---

### Admin Page Missing OnOpenPage Guard

Why it matters: A page with `UsageCategory = Administration` is surfaced to
all users with the permission set. Without an `OnOpenPage` guard, any such
user can open it and change admin-only settings.

**Pattern to check:** Any page with `UsageCategory = Administration` must
have an `OnOpenPage` trigger that either:

- Calls `if not GuardIsAdmin() then Error(NotAuthorizedErr)`, OR
- Declares `AccessByPermission = tabledata "..." = M;` at the page level.

**Bad:**

```al
page 50517 "Email Retry Setup"
{
    UsageCategory = Administration;
    SourceTable = "Email Retry Setup";
    // No OnOpenPage guard
}
```

**Good — Option 1: OnOpenPage guard with elevated role check**

```al
page 50517 "Email Retry Setup"
{
    UsageCategory = Administration;
    SourceTable = "Email Retry Setup";

    trigger OnOpenPage()
    begin
        if not (UserSetupMgt.IsAdminUser(UserId())) then
            Error(NotAuthorizedAdminErr);
    end;
}
```

**Good — Option 2: AccessByPermission at page level (BC standard pattern)**

```al
page 50517 "Email Retry Setup"
{
    UsageCategory = Administration;
    SourceTable = "Email Retry Setup";
    AccessByPermission = tabledata "Email Retry Setup" = M;
}
```

---

### GDPR DataClassification for User Identity Fields

Why it matters: BC user identity data (security IDs, display names) must be
classified as `EndUserIdentifiableInformation`, not `CustomerContent`.
Incorrect classification affects GDPR subject-access-request handling and
data-export tooling.

**Fields requiring `EndUserIdentifiableInformation`:**

- `User Security ID` (Guid linked to a BC user)
- Display names, email addresses, or user-facing name fields

**Bad:**

```al
field(10; "Sender User Security Id"; Guid)
{
    DataClassification = CustomerContent;   // Wrong: this is user identity
}
```

**Good:**

```al
field(10; "Sender User Security Id"; Guid)
{
    DataClassification = EndUserIdentifiableInformation;
}
field(11; "Sender Display Name"; Text[250])
{
    DataClassification = EndUserIdentifiableInformation;
}
```

**Review checklist item:** For every new table, scan all fields. If a field
name contains `User`, `UserId`, `Security Id`, `Display Name`, `Email`, or
`Person`, verify its `DataClassification`. System-internal GUIDs with no
link to an individual use `SystemMetadata`.

---

### Permission Set Tier Design

Why it matters: A single permission set granting full `RMID` on all objects
gives every user admin capabilities. Features with sensitive management
operations should split into a base viewer set and an admin set.

**Bad — flat permission set:**

```al
permissionset 50500 "MY Feature"
{
    Permissions =
        tabledata "Retry Entry" = RMID,         // All users can delete
        tabledata "Retry Setup" = RMID,          // All users can toggle setup
        codeunit "Retry Mgt." = X;
}
```

**Good — split viewer / admin:**

```al
permissionset 50500 "MY Feature"
{
    // Viewer: read entries, execute retry logic
    Permissions =
        tabledata "Retry Entry" = RM,
        codeunit "Retry Mgt." = X,
        page "Retry Entries" = X;
}

permissionset 50501 "MY Feature Admin"
{
    IncludedPermissionSets = "MY Feature";
    // Admin adds: modify/delete entries, full setup control
    Permissions =
        tabledata "Retry Entry" = ID,
        tabledata "Retry Setup" = RMID,
        codeunit "Retry Install" = X,
        page "Retry Setup" = X;
}
```

**Review checklist item:** When a feature has both a list page (end users)
and a setup/admin page (admins), the permission set should be split. Check
whether `RMID` on setup tables is accessible to all permission set holders.

---

### AccessByPermission vs OnOpenPage SUPER Check

Why it matters: Authentication and authorization in BC follow a layered
permission model. `AccessByPermission` declares the baseline permission set
requirement for the page. `OnOpenPage` is reserved for elevated or
role-specific supplementary checks, not as a replacement for the permission
model. Guarding a page solely with a boolean flag on User Setup (`"Is Email
Retry Admin"`) as the *only* access control is non-standard and hard to
discover; instead, use `AccessByPermission` for base access, then add the
boolean check in `OnOpenPage` only when an elevated secondary role is needed.

**Preferred BC pattern — layered authorization:**

```al
page 50516 "Email Retry Entries"
{
    // Base-level access: declared at page level per BC's permission model
    AccessByPermission = tabledata "Email Retry Entry" = R;

    trigger OnOpenPage()
    begin
        // Elevated admin check only (supplementary to AccessByPermission, not a replacement)
        if not UserSetupMgt.IsEmailRetryAdmin(UserId()) then
            Error(NotRetryAdminErr,
                  'You must be designated as Email Retry Admin in User Setup.' +
                  ' Contact your system administrator.');
    end;
}
```

**Key rules:**

1. `AccessByPermission` at the page level provides base access control per
   BC's standard permission model — this is mandatory.
2. The `OnOpenPage` check with `IsEmailRetryAdmin()` is an *additional*
   elevated authorization layer (e.g., a feature admin role that sits *above*
   the base permission set).
3. The User Setup boolean (`IsEmailRetryAdmin`) is acceptable *only* as a
   secondary elevated check in the `OnOpenPage` trigger, not as the sole
   access control mechanism.
4. Always pair `AccessByPermission` with an actionable error message in
   `OnOpenPage` that tells the user what to do next.
