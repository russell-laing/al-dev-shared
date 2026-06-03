---
title: AL Linting Rules Reference
tags:
  - linting
  - al-analyser
  - codecop
  - appsourcecop
  - lintercop
---

# AL Linting Rules Reference

Quick reference for AL code analyser rules.
Use rule IDs to look up fixes for compile or lint output.

The quick reference below lists the most common fixes only. Entries marked `judgment-required` need a project-specific choice rather than a shared default. Use the detailed tables when the top list is incomplete or when you need the authoritative rule details.

## Quick Reference — Most Common Fixes

| Symptom | Rule | Fix |
| --- | --- | --- |
| Missing prefix on object name | AS0011, AS0098 | Add the app's assigned affix or prefix |
| Missing DataClassification on field | AS0016 | `judgment-required`: choose the correct `DataClassification` value |
| Missing Caption | LC0016 | Add `Caption = '...';` |
| Missing ToolTip | AA0218 | Add `ToolTip = 'Specifies ...';` |
| ToolTip does not start with "Specifies" | LC0036 | Rewrite to start with "Specifies" |
| Temp variable missing Temp prefix | AA0073 | Rename variable with `Temp` prefix |
| Label missing Lbl suffix | AA0074 | Rename with `Lbl` suffix |
| TextConst missing Txt suffix | AA0074 | Rename with `Txt` suffix |
| Field ID out of range | AS0013, PTE0002 | `judgment-required`: use an ID from the project's assigned range |
| Object ID out of range | PTE0001 | `judgment-required`: use an ID from the project's assigned range |
| Commit() without comment | LC0002 | Add `// Required: <reason>` before Commit() |
| Unused variable declared | AA0137 | Remove the variable declaration |
| String concat in Error() | AA0216 | Replace with label + placeholders |
| FlowField editable | LC0001 | Add `Editable = false;` |
| Text assigned to target with smaller size | LC0051 | Wrap with `CopyStr()` or increase target size |
| Wrong `.Get()` argument count or type | LC0075 | Match `.Get()` args to PK field count and types |

---

## AL Compiler Diagnostics (AL prefix)

| Rule ID | Severity | Title | Fix | Applies To |
| --- | --- | --- | --- | --- |
| AL0104 | Error | Syntax error, expected | Add missing syntax element | All |
| AL0118 | Error | Name does not exist in context | Check spelling or add declaration | All |
| AL0121 | Error | Variable name already defined | Rename duplicate variable | All |
| AL0130 | Error | var argument must be assignable | Use var only for modified params | All |
| AL0133 | Error | Cannot convert type | Fix type mismatch | All |
| AL0156 | Error | Not a valid field type | Use valid field type | Tables |
| AL0161 | Error | Inaccessible due to protection level | Check access modifiers | All |
| AL0225 | Error | Required property missing | Add required property | All |
| AL0231 | Error | Member with ID already defined | Use unique IDs | All |
| AL0247 | Error | Extension target not found | Verify target exists | Extensions |
| AL0269 | Error | SourceTable must be set | Add `SourceTable = ...;` | Pages |
| AL0302 | Error | Used before declared | Move declaration before usage | All |
| AL0320 | Error | Field is read-only | Remove assignment to read-only field | All |
| AL0359 | Error | PK cannot include FlowField | Remove FlowField from PK | Tables |
| AL0413 | Error | Procedure cannot have body | Remove body from interface method | Interfaces |
| AL0414 | Error | Procedure must declare body | Add begin..end block | All |
| AL0415 | Error | local cannot be specified here | Remove local keyword | All |
| AL0416 | Error | Method cannot have return value | Remove return from trigger | All |
| AL0424 | Error | Variable named Rec auto-created | Rename variable | Pages, Reports |
| AL0432 | Warning | Marked for removal | Replace with recommended alternative | All |
| AL0433 | Error | Removed | Use current supported alternative | All |
| AL0451 | Error | Assembly not found | Check assembly reference path | All |
| AL0584 | Error | Interface member cannot have variables | Remove variables | Interfaces |
| AL0621 | Error | Preprocessor directive expected | Fix directive syntax | All |
| AL0623 | Error | #endif expected | Add missing #endif | All |
| AL0624 | Error | Unexpected preprocessor directive | Remove invalid directive | All |
| AL0629 | Error | Preprocessor expression not valid | Fix expression syntax | All |
| AL0659 | Error | Call is ambiguous | Qualify method call | All |
| AL0666 | Error | Not assignable | Use compatible types | All |
| AL0667 | Error | Not available in runtime version | Use compatible feature | All |
| AL0668 | Warning | Being deprecated | Plan migration to alternative | All |
| AL0774 | Error | Try method should not specify return | Remove explicit return | All |
| AL0779 | Error | Cannot assign to FlowField class | Don't assign to FlowFields | Tables |
| AL0803 | Error | Interface implementation adds behavior | Don't add interface impls in extensions | Extensions |
| AL0847 | Error | Does not contain definition | Fix reference to missing member | All |
| AL0852 | Error | Method can't implement interface method | Fix method signature | All |
| AL0968 | Error | StrSubstNo first param must be text constant | Use label as first param | All |
| AL1021 | Error | Table does not exist | Fix table reference | All |
| AL1022 | Error | Field does not exist in table | Fix field reference | All |
| AL1034 | Error | Type inference failed | Explicitly specify variable type | All |

---

## CodeCop Rules (AA prefix)

| Rule ID | Severity | Title | Fix | Applies To |
| --- | --- | --- | --- | --- |
| AA0001 | Warning | One space on each side of binary operator | Add spaces around operators | All |
| AA0005 | Warning | Use BEGIN..END only for compound statements | Remove unnecessary BEGIN..END | All |
| AA0008 | Warning | Function calls should have parentheses | Add parentheses to calls | All |
| AA0021 | Warning | Variable declarations ordered by type | Group variables by type | All |
| AA0040 | Warning | Avoid nested WITH statements | Replace WITH with direct references | All |
| AA0073 | Warning | Temp variable must be prefixed with Temp | Add `Temp` prefix to variable name | All |
| AA0074 | Warning | TextConst/Label must have approved suffix | Add `Lbl` for Label, `Txt` for TextConst | All |
| AA0101 | Warning | Use camelCase in API pages | Use camelCase property values | API Pages |
| AA0102 | Warning | Use camelCase field names in API pages | Use camelCase for field names | API Pages |
| AA0136 | Warning | Unreachable code | Remove code after exit statements | All |
| AA0137 | Warning | Unused variable declared | Remove unused variable | All |
| AA0139 | Warning | Text assigned to smaller target | Use `CopyStr` or increase target size | All |
| AA0150 | Warning | Avoid unnecessary VAR parameters | Remove VAR for unmodified params | All |
| AA0175 | Warning | Only find record if you need it | Use `IsEmpty()` for existence check | All |
| AA0181 | Warning | Use FINDSET + REPEAT | Replace FIND + NEXT with FindSet + repeat | All |
| AA0194 | Warning | Only write actions that have effect | Remove or implement empty actions | Pages |
| AA0198 | Warning | No identical local and global variable names | Use unique names | All |
| AA0207 | Warning | Event subscriber must be local | Add `local` keyword to subscriber | All |
| AA0210 | Warning | Filtering on non-indexed field | Filter on indexed fields when possible | All |
| AA0213 | Warning | Missing RunObject property | Add `RunObject = ...;` | Pages |
| AA0214 | Warning | Modify local record before saving | Make changes before calling `Modify()` | All |
| AA0216 | Warning | No string concatenation in Error | Use label with placeholders | All |
| AA0217 | Warning | StrSubstNo first param must be label | Use label as first param | All |
| AA0218 | Warning | ToolTip required on all controls | Add `ToolTip = 'Specifies ...';` | Pages |
| AA0231 | Warning | StrSubstNo must not be used directly in Error | Assign to ErrorInfo.Message first | All |
| AA0233 | Warning | Inefficient record navigation | Use FindSet() for multiple records | All |
| AA0235 | Warning | Install codeunits must subscribe CompanyInitialize | Add OnCompanyInitialize subscriber | Install CUs |
| AA0462 | Warning | Date formulas should be enclosed in < > | Enclose in angle brackets | All |
| AA0470 | Info | Label comments should document placeholders | Add Comment = '%1 = ...' | All |

---

## AppSourceCop Rules (AS prefix)

| Rule ID | Severity | Title | Fix | Applies To |
| --- | --- | --- | --- | --- |
| AS0011 | Error | Affix required | Add the app's assigned affix or prefix to the object name | All |
| AS0013 | Error | Field identifier must be in allowed range | Use an ID from the project's assigned range | Tables |
| AS0016 | Error | Fields must use DataClassification | Choose the correct `DataClassification` value for the field | Tables |
| AS0068 | Error | Cannot change table extension target | Keep original target table | TableExt |
| AS0069 | Error | Same number of option members required | Maintain same option count | Tables |
| AS0070 | Error | Same option member names required | Maintain same option names | Tables |
| AS0071 | Error | Same ordinal values required | Maintain option ordinal values | Tables |
| AS0072 | Error | Obsolete reason required | Add reason to [Obsolete] attribute | All |
| AS0073 | Error | ObsoleteTag required | Add version tag to [Obsolete] | All |
| AS0074 | Error | ObsoleteState required | Add ObsoleteState parameter | All |
| AS0075 | Error | SubstitutionMessage required | Add replacement info to [Obsolete] | All |
| AS0079 | Warning | Affix required for extension procedures | Add prefix to extension procedures | Extensions |
| AS0080 | Error | Fields must not decrease in length | Only increase field lengths | Tables |
| AS0082 | Error | Cannot rename enum value | Keep original enum value names | Enums |
| AS0083 | Error | Cannot delete enum value | Mark as obsolete instead | Enums |
| AS0084 | Error | Fields must not change data type | Maintain field data types | Tables |
| AS0085 | Error | Fields must not be deleted | Mark as obsolete instead | Tables |
| AS0086 | Warning | Fields must not increase in length | Evaluate performance impact | Tables |
| AS0087 | Warning | Enum caption must not contain commas | Use semicolon or other separator | Enums |
| AS0088 | Error | Cannot move procedure to another object | Keep procedures in original object | All |
| AS0089 | Warning | Affix required for global variables in extensions | Add prefix to global variables | Extensions |
| AS0092 | Error | Version-specific suppressWarning not allowed | Handle errors properly | All |
| AS0094 | Warning | Permission sets not in XML | Use AL for permission sets | PermissionSets |
| AS0095 | Error | Cannot reduce access modifier | Only increase access modifiers | Tables |
| AS0096 | Error | Cannot change field order with TableData | Maintain field order | Tables |
| AS0097 | Error | Cannot remove extensible from procedures | Keep extensible property | All |
| AS0098 | Warning | Affix needed | Add prefix/suffix to object name | All |
| AS0099 | Error | Member ID not in allowed range | Use IDs in assigned range | All |
| AS0100 | Info | Use Microsoft curated action icons | Use standard Microsoft icons | Pages |
| AS0102 | Error | Cannot change PageType value | Keep original PageType | PageExt |
| AS0103 | Warning | Permission sets must cover all objects | Include all objects in permission sets | PermSets |
| AS0104 | Error | Cannot change RunObject value | Keep original RunObject | PageExt |
| AS0105 | Error | Cannot change SourceTableTemporary | Keep original value | PageExt |
| AS0110 | Warning | No permissions for objects from another app | Only include own permissions | PermSetExt |
| AS0111 | Warning | No permission sets from another app | Only include own permission sets | PermSetExt |
| AS0112 | Warning | No nested permission sets from another app | Check nested permission sets | PermSetExt |
| AS0113 | Warning | No wildcard permissions | Use specific object permissions | PermSetExt |
| AS0114 | Info | Setup tables need SetupCategory | Add `SetupCategory = Application;` | Tables |
| AS0115 | Info | Setup pages need UsageCategory = Administration | Set `UsageCategory = Administration;` | Pages |
| AS0116 | Error | Event subscriber references non-existent event | Verify publisher event exists | EventSubs |
| AS0117 | Warning | Objects should not have version list | Remove VersionList property | All |
| AS0118 | Error | Subscriber return value must match publisher | Match return types | EventSubs |
| AS0124 | Error | Cannot change extension object target | Keep original extension target | Extensions |

---

## UICop Rules (AW prefix)

| Rule ID | Severity | Title | Fix | Applies To |
| --- | --- | --- | --- | --- |
| AW0016 | Warning | Rich Text Editor must be alone in FastTab | Move to separate FastTab group | Pages |

---

## PerTenantExtensionCop Rules (PTE prefix)

| Rule ID | Severity | Title | Fix | Applies To |
| --- | --- | --- | --- | --- |
| PTE0001 | Error | Object ID must be in free range | Use an ID from the project's assigned range | All |
| PTE0002 | Error | Field ID must be in free range | Use a field ID from the project's assigned range | Tables |
| PTE0003 | Error | Must not subscribe to CompanyOpen events | Use CompanyInitialize instead | All |
| PTE0004 | Error | Tables must have matching permission set | Create permission set with table perms | Tables |
| PTE0005 | Error | Compilation target must be SaaS-compatible | Use Extension or Cloud target | app.json |
| PTE0006 | Error | Encryption key functions must not be invoked | Remove encryption key calls | All |
| PTE0007 | Error | Test assertions not allowed in non-test context | Move to test codeunit | All |
| PTE0009 | Error | app.json property not allowed in PTE | Remove disallowed property | app.json |
| PTE0010 | Error | Extension name too long | Shorten name | app.json |
| PTE0011 | Error | Publisher name too long | Shorten publisher name | app.json |
| PTE0012 | Warning | InternalsVisibleTo is not a security feature | Use proper access modifiers | All |
| PTE0013 | Error | Entitlements cannot be defined in extension | Remove entitlement definitions | app.json |
| PTE0014 | Warning | Permission sets not in XML | Convert to AL permissionset objects | PermSets |
| PTE0015 | Error | Extension name not valid | Remove special characters | app.json |
| PTE0016 | Warning | No permissions for objects from another app | Remove external object permissions | PermSetExt |
| PTE0017 | Warning | No permission sets from another app | Remove external permission set refs | PermSetExt |
| PTE0018 | Warning | No nested external permission sets | Verify nested deps for external refs | PermSetExt |
| PTE0019 | Warning | No wildcard permissions | Use specific object permissions | PermSetExt |
| PTE0020 | Warning | Use application property instead of Base App dep | Use `"application": "20.0.0.0"` | app.json |
| PTE0021 | Error | Cannot define reserved namespaces | Use non-reserved namespace | All |
| PTE0022 | Warning | Member ID should be in allowed range | Use an ID from the project's assigned range | All |
| PTE0023 | Info | Enum ordinal should be in allowed range | Use ordinals in assigned range | Enums |

---

## LinterCop Rules (LC prefix)

| Rule ID | Severity | Title | Fix | Applies To |
| --- | --- | --- | --- | --- |
| LC0000 | Info | Internal rule error | Report to rule maintainer | All |
| LC0001 | Warning | FlowFields should not be editable | Add `Editable = false;` | Tables |
| LC0002 | Warning | Commit() needs justifying comment | Add `// Required: <reason>` before Commit() | All |
| LC0003 | Warning | Do not use Object ID for declarations | Use symbolic names (Database::Customer) | All |
| LC0004 | Warning | DrillDownPageId and LookupPageId must be set | Set both properties on table | Tables |
| LC0005 | Warning | Variable/method casing must match definition | Use exact casing from declaration | All |
| LC0006 | Error | AutoIncrement cannot be used in temporary table | Remove AutoIncrement | Tables |
| LC0007 | Disabled | Every table needs DataPerCompany property | Add `DataPerCompany = true/false;` | Tables |
| LC0008 | Warning | Filter operators not allowed in SetRange | Use SetFilter for complex filters | All |
| LC0009 | Disabled | Show code metrics per function | Enable rule to see metrics | All |
| LC0010 | Warning | Warn about high cyclomatic complexity | Simplify function or break into smaller | All |
| LC0011 | Disabled | Every object needs Access property | Add `Access = Internal/Public;` | All |
| LC0012 | Warning | No hardcoded IDs in Codeunit.Run() | Use `Codeunit::"Name"` syntax | All |
| LC0013 | Warning | Single Code/Text PK field should have NotBlank | Add `NotBlank = true;` on PK field | Tables |
| LC0014 | Warning | Permission set Caption too long | Shorten caption | PermSets |
| LC0015 | Warning | All objects must be in at least one permission set | Add permissions for all objects | All |
| LC0016 | Warning | Caption is missing | Add `Caption = '...';` | All |
| LC0017 | Warning | Writing to FlowField is uncommon | Add comment or use regular field | Tables |
| LC0018 | Info | Events in internal codeunits not accessible | Move events to public codeunit | Codeunits |
| LC0019 | Info | Duplicate DataClassification | Remove per-field classification when set at table | Tables |
| LC0020 | Info | Duplicate ApplicationArea | Remove per-control ApplicationArea when set at page | Pages |
| LC0021 | Info | Use ConfirmManagement for Confirm() | Use `ConfirmMgt.GetResponseOrDefault()` | All |
| LC0022 | Info | Use TranslationHelper for GlobalLanguage() | Use `TranslationHelper.GetGlobalLanguage()` | All |
| LC0023 | Info | Provide DropDown and Brick fieldgroups | Add `fieldgroup(DropDown; ...)` and Brick | Tables |
| LC0024 | Info | Procedure declaration should not end with semicolon | Remove trailing semicolon | All |
| LC0025 | Info | Procedure must be local, internal, or documented | Mark local/internal or add XML doc | All |
| LC0027 | Info | Use Page Management for page launch | Use `PageMgmt.PageRun()` | All |
| LC0028 | Info | Use identifier syntax for event subscribers | Use identifier not string literal | All |
| LC0029 | Info | Use TypeHelper.CompareDateTime for DateTime | Use Type Helper codeunit | All |
| LC0030 | Info | Set Access = Internal on Install/Upgrade CUs | Add `Access = Internal;` | Install/Upgrade |
| LC0031 | Info | Use ReadIsolation instead of LockTable | Use `ReadIsolation(ReadIsolated)` | All |
| LC0032 | Warning | Clear(All) does not affect single instance globals | Reset global variables explicitly | Codeunits |
| LC0033 | Info | Runtime version falling behind | Update runtime version in app.json | app.json |
| LC0035 | Info | Explicitly set AllowInCustomizations | Add `AllowInCustomizations = true;` | Pages |
| LC0036 | Info | ToolTip must start with "Specifies" | Rewrite ToolTip to start with "Specifies" | All |
| LC0051 | Warning | Do not assign a text to a target with smaller size | Wrap assignment with `CopyStr()` or increase target size | All |
| LC0075 | Warning | Incorrect number or type of arguments in .Get() method | Pass correct PK argument count and types to `.Get()` | Record objects |
