# Documentation RTM Guide

Referenced by: `docs-writer` agent and `/document` skill

## Overview

This guide documents how to parse source requirements, track status, and render **Requirements Traceability Matrix (RTM)** data in feature documentation. The RTM system links documented requirements to implementation status, ensures completeness, and provides traceability for stakeholder sign-off.

---

## RTM Token System

Requirements and acceptance criteria are encoded in `*-interview-requirements.md` files as line-anchored `REQ:` and `ACC:` tokens:

### Token Format

**Requirement token:**
```
REQ:REQ-NNN [Requirement description]
```

Example:
```
REQ:REQ-001 Users can set a credit limit per customer
REQ:REQ-002 System prevents saving sales orders that exceed the limit
```

**Acceptance criteria token:**
```
ACC:ACC-NNN [Criterion description]
```

Example:
```
ACC:ACC-001 Credit limit field accepts zero or positive numbers only
ACC:ACC-002 Error message displayed if limit is exceeded
```

The token examples above are internal parsing patterns, not output examples. Use the later RTM table templates and audience rules when rendering documentation.

### Parsing Rules

1. Scan the latest `*-interview-requirements.md` file for all `REQ:REQ-NNN` and `ACC:ACC-NNN` tokens.
2. Each requirement (`REQ-NNN`) may have multiple acceptance criteria (`ACC-NNN`).
3. **Every REQ-NNN found in the requirements file must appear in the RTM table** — this is the completeness check.
4. `ACC-NNN` criteria linked to a REQ-NNN should be listed on the same RTM table row (if audience rules permit) or in a separate row.

---

## Status Inference

The RTM status for each requirement is inferred from the **presence of `.dev/` files** in the project. The inferred status **overrides** any `status:` field in the requirements file itself for RTM rendering.

### Status Rules

| .dev/ Files Present | Inferred Status | Meaning |
|---|---|---|
| Only `*-interview-requirements.md` | `DEFINED` | Requirements documented, no design or code yet |
| + `*-plan-solution-plan.md` | `IN-PROGRESS` | Architecture designed, implementation starting |
| + `*-develop-code-review.md` | `IMPLEMENTED` | Code written and reviewed |
| + Test results or explicit sign-off | `VERIFIED` | Tested, validated, or signed off by stakeholder |

**Application rule:** Query for the latest `*-plan-solution-plan.md`, `*-develop-code-review.md`, and any test/sign-off artifact. Determine the highest status level supported by those current-run artifacts and apply that to all requirements in the RTM table.

---

## Audience-Based RTM Rules

The format, completeness, and content of the RTM table varies by target audience. The agent receives an `AUDIENCE` parameter and renders the RTM accordingly.

### Audience Rules

| Audience | Include RTM? | Table Columns | Content Style | Notes |
|---|---|---|---|---|
| **technical** | ✅ Yes, full | ID, Type, Priority, Status, Requirement, Acceptance Criteria | Code-aware; include object references, field names, formula details | For AL developers; completeness is critical |
| **functional** | ✅ Yes, reduced | ID, Status, Requirement | Plain language; no code references; remove technical jargon | For business analysts / consultants |
| **user** | ❌ No | — | — | End-user guides don't include traceability |
| **executive** | ❌ No | — | Summary line instead | Replace RTM with: "X requirements delivered, Y verified, Z in progress" |

### When to Omit the RTM Table

- **user** and **executive** audiences: Replace the full RTM table with a one-line requirements summary.
  - Example: "Feature delivers 8 requirements: 7 verified, 1 in progress"
- This maintains traceability for internal review while keeping user/executive docs focused on value, not mechanics.

```markdown
Requirements summary: 8 delivered, 7 verified, 1 in progress.
```

---

## Inline Requirement References

In feature documentation narrative sections, reference requirements by ID immediately after the statement that fulfills them.

### Format

```markdown
[Feature description or workflow step] (REQ-NNN)
```

### Examples

The examples below show the same requirement traced at different audience
depths so writers can choose detail deliberately instead of improvising.

**Technical audience:**

```markdown
### User Perspective

For end-user documentation, keep the focus on what the user can do next rather
than on internal IDs, SLA wording, or implementation terms.

Users can set a per-customer credit limit (REQ-001). The system prevents 
saving sales orders if the total exceeds this limit (REQ-002).

### Technical Implementation

The validation is performed in codeunit XX's `ValidateCreditLimit()` method 
(REQ-002, ACC-002), which compares the order total against the customer 
record's `Credit Limit` field (REQ-001, ACC-001).
```

**Functional audience:**

```markdown
### Workflows

**Credit Limit Validation**

Users set a per-customer credit limit (REQ-001). When processing a sales 
order, the system checks if the order total will exceed this limit (REQ-002) 
and prevents saving if it does (ACC-002).
```

**Functional RTM Table Example:**

| ID | Status | Requirement |
|---|---|---|
| REQ-001 | VERIFIED | Users can set a credit limit per customer |
| REQ-002 | VERIFIED | System prevents saving orders that exceed the credit limit |
| REQ-003 | IN-PROGRESS | System sends warning email if order approaches 80% of limit |

### Application Rules

1. Include inline references for **technical** and **functional** audiences only.
2. Omit inline references for **user** and **executive** audiences (they don't include RTM data).
3. Place the REQ-NNN ID **immediately after** the statement it traces to.
4. Multiple references can appear on a single statement: `(REQ-001, REQ-002, ACC-002)`.

### RTM Detail by Audience

How much RTM detail to include depends on who will read the documentation.

Use the sections below as a slider: increase detail for technical readers and
reduce traceability noise for user-facing material.

#### RTM Reference Example

**Technical documentation with RTM references:**

> **Requirement REQ-003:** "Sales order approval workflow must notify approver within 5 minutes of submission."
>
> **Implementation:** When a sales order is submitted with Status = Pending Approval, the system triggers an event subscriber that sends email to the approver (from Approver User table, configured in Sales & Receivables Setup). The notification includes the order number, total amount, and approval link.
>
> **Verification:** See Approval Workflow Tests (ref: REQ-003-v1, REQ-003-v2)

Each sentence ties back to a specific requirement. Readers can trace from documentation to requirement to test coverage.

#### User Perspective

User-facing documentation de-emphasizes requirements and RTM details:

**User Guide (less RTM detail):**
> When your purchase order is ready for review, click "Submit for Approval." The approver will receive an email within a few minutes and can approve or reject the order using the link in the email. You'll be notified when the order is approved.

**Technical Documentation (more RTM detail):**
> PO approval flow: Status = Open → Submit → Status = Pending Approval (triggers event subscriber) → Approver receives notification email (within 5 min SLA per REQ-003) → Approver clicks link → Portal opens approval page → Approver clicks Approve → Status = Approved (triggers audit log per REQ-002)

User guides omit the requirement IDs and SLA details; technical docs include them for traceability.

---

## RTM Table Formats

### Full RTM (Technical Audience)

**Location:** End of feature documentation.

**Columns:**
- **ID**: Requirement identifier (REQ-NNN) or acceptance criterion (ACC-NNN)
- **Type**: Functional / Non-Functional / Constraint
- **Priority**: High / Medium / Low
- **Status**: DEFINED / IN-PROGRESS / IMPLEMENTED / VERIFIED
- **Requirement**: Full requirement text (plain language)
- **Acceptance Criteria**: For REQ rows: list linked ACC-NNN criteria; for ACC rows: leave blank or repeat criterion text

**Template:**

```markdown
## Requirements Traceability

| ID | Type | Priority | Status | Requirement | Acceptance Criteria |
|---|---|---|---|---|---|
| REQ-001 | Functional | High | IMPLEMENTED | Users can set a credit limit per customer | ACC-001: Credit limit accepts zero or positive numbers only |
| REQ-002 | Functional | High | IMPLEMENTED | System prevents saving orders exceeding the limit | ACC-002: Error shown if order total exceeds limit; ACC-003: Limit field is read-only for locked orders |
| ACC-001 | — | — | IMPLEMENTED | Credit limit field accepts zero or positive numbers only | — |
| ACC-002 | — | — | IMPLEMENTED | Error message displayed if limit is exceeded | — |
| ACC-003 | — | — | IMPLEMENTED | Credit Limit field is read-only when order is locked | — |
```

### Reduced RTM (Functional Audience)

**Location:** End of feature documentation.

**Columns:**
- **ID**: Requirement identifier (REQ-NNN only; no ACC rows)
- **Status**: DEFINED / IN-PROGRESS / IMPLEMENTED / VERIFIED
- **Requirement**: Requirement text in plain language; no code references

**Template:**

```markdown
## Requirements Traceability

| ID | Status | Requirement |
|---|---|---|
| REQ-001 | IMPLEMENTED | Users can set a credit limit per customer |
| REQ-002 | IMPLEMENTED | System prevents saving orders exceeding the limit |
```

### Summary Line (User/Executive Audience)

**Location:** In a brief "Status" or "Scope" section at the start of the document.

**Format:**

```markdown
**Requirements Status:** X requirements delivered (Y verified, Z implemented, W in progress).
```

**Example:**

```markdown
**Requirements Status:** 8 requirements delivered (7 verified, 1 in progress).
```

---

## Examples

### Example 1: Functional RTM — "How to Process a Sales Order"

**Use case:** Documenting a feature from the business user's perspective. RTM maps user stories to instructions.

| User Requirement | Page Section | Step | Verification |
|------------------|-------------|------|--------------|
| "Create sales order for customer" | Sales Order Card | Enter header (customer, date) | Customer details auto-populate |
| "Add line items with quantity" | Sales Order Lines | Click Add Line, enter Item No., Quantity | System calculates line total |
| "System should verify customer credit" | Sales Order Card | Click Validate (before posting) | Credit warning appears if exceeded |
| "Apply discount if quantity threshold met" | Sales Order Lines | Quantity > 10 auto-applies 5% discount | Discount appears in Amount field |
| "Post order to create invoice" | Sales Order Card | Click Post | Order status changes to "Posted" |
| "Verify invoice in Accounts Receivable" | Posted Invoices | Search customer invoices | New invoice appears in list |

**RTM structure:** Each row is a user action (requirement) → UI location → steps → how to verify. Rows flow in business-logic order (create → validate → post → verify).

**Who uses this RTM?** Functional testers, business analysts, and consultants validating new features.

### Example 2: Technical Admin RTM — "Deploying the Sales Module Update"

**Use case:** Documenting a system administration task. RTM maps deployment requirements to configuration steps.

| Admin Requirement | Configuration Area | Procedure | Verification Command |
|------------------|-------------------|-----------|---------------------|
| "Apply hotfix to codeunit 50000" | Code Deployments | Import .al file via DevOps | `al-compile --output errors.log` returns no errors |
| "Update customer credit limit validation" | Table 18 extensions | Modify validation rule in Customer table | Run test suite: `pytest tests/customer-validation/` |
| "Enable credit limit enforcement on sales order posting" | Permission Set assignments | Add "Post Sales Order" permission to all Sales roles | User can post order without "Access Denied" |
| "Configure audit logging for order amendments" | Audit Trail setup | Enable field-change logging on Sales Header | Changes appear in Audit Log within 5 minutes |
| "Validate integration with external billing system" | Integration endpoints | Test webhook endpoint with mock payload | Webhook returns HTTP 200 OK; order appears in billing system |

**RTM structure:** Each row is an admin task → config location → how to perform it → how to verify it works. Rows follow deployment sequence (code → config → permissions → testing).

**Who uses this RTM?** System administrators, DevOps engineers, deployment teams.

### Example 3: Developer RTM — "Implementing Customer Credit Limit Enforcement"

**Use case:** Documenting a code feature. RTM maps functional requirements to code modules and tests.

| Functional Requirement | Code Module | Implementation | Test Coverage |
|-------|---|---|---|
| "Customer credit limit is set and stored" | Table 18 (Customer) | Add field "Credit Limit" (Decimal, min 0) | `test_CustomerCreditLimitField_CanBeSet()` |
| "Credit limit cannot be negative" | Table 18 validation | Add validation: `if "Credit Limit" < 0 then Error(...)` | `test_CustomerCreditLimitField_RejectsNegative()` |
| "Sales order cannot post if customer exceeds credit" | Codeunit 80 (Sales-Post) | Add pre-post check in OnBeforePostSalesHeader | `test_SalesOrder_BlockedWhenCreditExceeded()` |
| "Sales order warning if approaching limit (90%)" | Page 42 (Sales Order) | Add FactBox field binding to credit usage % | `test_SalesOrderPage_WarningAppearsAt90Percent()` |
| "Credit limit overrides for emergency orders" | Table 109 (Sales Order Header) | Add field "Override Credit Check" (boolean) | `test_SalesOrder_AllowsOverride_WhenFlagSet()` |
| "Audit log tracks credit overrides" | Codeunit 50001 (Audit Handler) | Log credit override to audit table | `test_AuditLog_RecordsCreditOverride()` |

**RTM structure:** Each row is a requirement → code location → how implemented → corresponding test. Rows follow data-flow order (store → validate → use → display).

**Who uses this RTM?** Developers writing code, code reviewers verifying coverage, QA testers writing test plans.

### When to Omit RTM Table

**Omit RTM if:**
- Documentation is <500 words (RTM adds overhead for small docs)
- Feature is a bug fix or internal refactor with no new requirements (RTM is for requirements tracing, not code refactoring)
- Feature is a simple config change with 1-2 steps (too granular for RTM; use numbered list instead)
- Audience is `user` or `executive`, where the earlier audience rules already replace the RTM table with a summary line

**Include RTM if:**
- Feature is new and spans 3+ modules (track req → code → test mappings)
- Documentation is for multiple audiences (functional users + admins + developers; RTM tailors to each)
- Compliance/audit trail required (RTM documents what was implemented, who verified, where the evidence is)
- Stakeholder sign-off needed (RTM is the deliverable artifact)

---

## Folder Structure

Documentation output follows this structure in the target project:

```
docs/                           (or wiki/ if that is the project's preference)
├── Features/                   (Main: feature docs, one file per feature per audience)
│   ├── CreditLimitManagement-technical.md
│   ├── CreditLimitManagement-functional.md
│   └── SalesOrderValidation-technical.md
├── API/                        (Public codeunit API references)
│   └── CreditManagementAPI.md
├── Setup/                      (Installation, permissions, configuration)
│   └── InstallationGuide.md
├── Architecture/               (System design, data model, integrations)
│   └── DataModel.md
└── README.md                   (Overview and navigation)
```

**Multi-audience rule:** If the same feature is documented for multiple audiences (technical, functional, user, executive), create separate files for each with the audience appended to the filename. Example:
- `Features/CreditLimitManagement-technical.md`
- `Features/CreditLimitManagement-functional.md`
- `Features/CreditLimitManagement-user.md`

**Directory detection:** The agent detects whether `docs/` or `wiki/` exists in the target project and outputs to whichever is present. If neither exists, it creates `docs/`.

**Sub-folder names remain the same** whether the root is `docs/` or `wiki/`.

---

## Checklist: Completeness Verification

When reviewing generated documentation, verify:

1. ✅ **All REQ-NNN tokens are present:** Count REQ-NNN in the requirements file; count REQ-NNN in the RTM table. Must be equal.
2. ✅ **Status is inferred correctly:** Check which `.dev/` files exist; confirm RTM status matches the rule above.
3. ✅ **Inline references are present** (technical and functional audiences): Scan narrative sections for `(REQ-NNN)` anchors.
4. ✅ **Table format matches audience:** Technical = full table; Functional = reduced table; User/Executive = summary line only.
5. ✅ **Acceptance criteria are included** (technical audience only): For each REQ, list its ACC-NNN criteria in the Acceptance Criteria column.
6. ✅ **Plain language is used** (functional and user audiences): No AL code, no object IDs, no technical jargon.
