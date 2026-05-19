# Documentation RTM Guide

Referenced by: `al-dev-docs-writer` agent

## RTM Handling (Requirements Traceability Matrix)

### Status Inference
Infer RTM status from existing doc structure and codebase state. If docs exist but aren't up-to-date, mark as `in-progress` or `review-pending`. If docs don't exist, mark as `not-started`.

### Token Parsing
Parse RTM tokens from markdown frontmatter or comment blocks. Common tokens:
- `status: in-progress` — being written
- `status: review-pending` — awaiting review
- `status: complete` — published

### Documentation Output
RTM documentation goes to the standard folder:
- `docs/` for technical and API documentation
- `wiki/` for conceptual and architectural documentation

### RTM Rules
Follow these rules when generating documentation:
- Status tokens must match the codebase state
- Document all public APIs with parameter descriptions
- Update status when implementation changes
- Link documentation to source code where applicable

## Folder Structure

### docs/ Folder
Use for technical and API documentation, implementation guides, architecture decisions.

Expected files:
- `docs/API.md` — public API reference
- `docs/ARCHITECTURE.md` — system design
- `docs/INSTALL.md` — setup instructions

### wiki/ Folder
Use for conceptual and architectural documentation, decision logs, patterns.

Expected files:
- `wiki/DESIGN_DECISIONS.md` — major design choices
- `wiki/PATTERNS.md` — reusable patterns
- `wiki/GLOSSARY.md` — terminology

## Template: API Documentation

Use this structure for API documentation:

```markdown
# [Module Name] API Reference

## Overview
[One sentence describing the module's purpose]

## Public Functions

### FunctionName
**Signature:** `procedure FunctionName(param: Type): ReturnType`

**Description:** What this function does.

**Parameters:**
- `param` — what this parameter represents

**Returns:** What the function returns.

**Example:**
[Code example showing how to use it]

### AnotherFunction
[Repeat structure above]

## Error Handling
[Document what errors can be raised and why]

## Performance Considerations
[Document any performance implications]
```
