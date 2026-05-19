# Documentation RTM Guide

Referenced by: `al-dev-docs-writer` agent and `/al-dev-document` skill

## Overview

This guide documents how to parse, track, and render **Requirements Traceability Matrix (RTM)** data in feature documentation. The RTM system links documented requirements to implementation status, ensures completeness, and provides traceability for stakeholder sign-off.

---

## RTM Token System

Requirements and acceptance criteria are encoded in `*-al-dev-interview-requirements.md` files as line-anchored tokens:

### Token Format

**Requirement token:**
```
REQ-NNN: [Requirement description]
```

Example:
```
REQ-001: Users can set a credit limit per customer
REQ-002: System prevents saving sales orders that exceed the limit
```

**Acceptance criteria token:**
```
ACC-NNN: [Criterion description]
```

Example:
```
ACC-001: Credit limit field accepts zero or positive numbers only
ACC-002: Error message displayed if limit is exceeded
```

### Parsing Rules

1. Scan the latest `*-al-dev-interview-requirements.md` file for all `REQ-NNN` and `ACC-NNN` tokens.
2. Each requirement (`REQ-NNN`) may have multiple acceptance criteria (`ACC-NNN`).
3. **Every REQ-NNN found in the requirements file must appear in the RTM table** — this is the completeness check.
4. `ACC-NNN` criteria linked to a REQ-NNN should be listed on the same RTM table row (if audience rules permit) or in a separate row.

---

## Status Inference

The RTM status for each requirement is inferred from the **presence of `.dev/` files** in the project. The inferred status **overrides** any `status:` field in the requirements file itself.

### Status Rules

| .dev/ Files Present | Inferred Status | Meaning |
|---|---|---|
| Only `*-al-dev-interview-requirements.md` | `DEFINED` | Requirements documented, no design or code yet |
| + `*-al-dev-plan-solution-plan.md` | `IN-PROGRESS` | Architecture designed, implementation starting |
| + `*-al-dev-develop-code-review.md` | `IMPLEMENTED` | Code written, peer-reviewed, merged |
| + Test results or explicit sign-off | `VERIFIED` | Tested, validated, or signed off by stakeholder |

**Application rule:** Query for the latest `*-al-dev-plan-solution-plan.md`, `*-al-dev-develop-code-review.md`, and any test/sign-off artifact. Determine the highest status level present and apply that to all requirements in the RTM table.

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

---

## Inline Requirement References

In feature documentation narrative sections, reference requirements by ID immediately after the statement that fulfills them.

### Format

```markdown
[Feature description or workflow step] (REQ-NNN)
```

### Examples

**Technical audience:**
```markdown
### User Perspective

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

### Application Rules

1. Include inline references for **technical** and **functional** audiences only.
2. Omit inline references for **user** and **executive** audiences (they don't include RTM data).
3. Place the REQ-NNN ID **immediately after** the statement it traces to.
4. Multiple references can appear on a single statement: `(REQ-001, REQ-002, ACC-002)`.

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
