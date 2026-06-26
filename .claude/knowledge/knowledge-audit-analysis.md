# Knowledge Audit Analysis Contract

This file defines the five operative contracts for the **Phase 2 analysis** step of
`/audit-knowledge-quality`. Phase 3 (findings report) and any parallel dispatch depend
on the return schema and severity rules defined here.

---

## 1. Progress Tracking

Before analyzing any file, create one progress todo per flagged file named
`[issue-type] [filename]`. Mark each todo `in_progress` when analysis begins and
`completed` when the file analysis is written to findings.

---

## 2. Path Selection (Parallel vs Sequential)

Count the flagged files and choose the execution path with one threshold-driven
decision:

- **4 or more flagged files AND no ordering dependencies among them** → parallel path.
- **Otherwise** (3 or fewer flagged files, or any ordering dependency between flagged
  files) → sequential path.

### Parallel Exploration (4+ files)

Invoke `superpowers:dispatching-parallel-agents` (if parallel dispatch is unavailable,
use the sequential path instead). Dispatch one Explore subagent per file to: read the
knowledge file, search for referencing agent/skill, and run the gap/severity assessment
(steps 1–4). Each subagent must return YAML with fields:
`{file, issue_type, gap_description, severity}`. Collect all records before proceeding
to Phase 3.

### Sequential Analysis (≤3 files or fallback)

For each flagged file, execute the four steps defined in §3 (Mandatory Reads) and §4
(Per-Issue Treatment and Severity) below.

---

## 3. Mandatory Reads of Referencing Agents/Skills

For each flagged file:

1. **Read the file** — Understand its structure and current content.
2. **Read the referencing agent/skill** — Find where the file is referenced and what
   guidance it's supposed to provide (search `.md` files in
   `profile-al-dev-shared/agents/` and `profile-al-dev-shared/skills/` for references
   to the knowledge file).
   - If no referencing agent or skill is found, note the file as orphaned with severity
     LOW.

---

## 4. Per-Issue THIN/NO-CODE/DEAD-REF Treatment and Severity Criteria

### Issue Treatment

- **[THIN]:** Is the section intentionally brief (overview/summary)? Or is it a topic
  that SHOULD have more content?
- **[NO-CODE]:** The heading implies a pattern/example/usage. What code examples should
  be in the body?
- **[DEAD-REF]:** Is the referenced file truly missing, or is the reference malformed?

### Severity Criteria

- **HIGH:** Agent explicitly references the file for guidance it doesn't contain
  (for example, "Reference the related knowledge doc for the required examples").
  Missing content blocks the worker.
- **MEDIUM:** File is referenced but content gap is incomplete/shallow (agent can work
  around it).
- **LOW:** False positive (file is intentionally brief) or formatting issue (easily
  fixed).

---

## 5. Structured YAML Return Schema

Each analyzed file — whether analyzed via the parallel or sequential path — must produce
a record conforming to this schema before Phase 3 may proceed:

```yaml
file: <exact-relative-path-to-knowledge-file>
issue_type: <THIN|NO-CODE|DEAD-REF>
gap_description: <one-line description of what is missing or wrong>
severity: <HIGH|MEDIUM|LOW>
```

Phase 3 consumes this schema to populate the findings report and the machine-readable
High-Priority Fix Tasks block. All four fields are required; omit no field.
