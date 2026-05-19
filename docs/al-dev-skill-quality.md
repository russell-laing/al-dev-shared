# AL Dev Skill Quality Audit

**Last run:** 2026-05-19
**Skills audited:** 16
**Resolution status:** ✅ All 12 findings resolved (2026-05-19)

## Summary

| Severity | Count |
|----------|-------|
| High     | 4     |
| Medium   | 4     |
| Low      | 4     |

## Findings

### /al-dev-commit

**[High] Lens 2 — Structural Conventions**
Observation: Frontmatter lacks `argument-hint` field. Skill description mentions orchestrator with user-facing gates, but no hint about optional arguments.
Fix: Add `argument-hint: "[optional args]"` to frontmatter (empty if no args expected), or document why this skill takes no arguments.

---

### /al-dev-develop

**[Low] Lens 1 — Prompt Clarity**
Observation: Phase 1.5 and Phase 4.5 introduce numbered substeps within phases, and some sections use jargon-heavy language (e.g., "Scope Expansion Gate", "developer spawn prompt") that could confuse newcomers.
Fix: Add a glossary section at the top explaining key terms, or split jargon-heavy phases into separate knowledge documents.

---

### /al-dev-explore

No findings.

---

### /al-dev-fix

**[Medium] Lens 2 — Structural Conventions**
Observation: Step numbering mixes "Step 1", "Step 2", "Step 3" with internal substeps labeled as phases (no explicit "Phase" label in the main flow). Examples at lines 333–399 are ~70 lines and dominate the end of the file.
Fix: Extract examples into a separate `Examples` section at the very end, or reference them from a companion knowledge document.

**[Low] Lens 4 — Bloat**
Observation: Two detailed examples (Example 1 and Example 2, lines 333–399) take up 67 lines. While helpful, they could be condensed to 3-5 lines each or moved to a reference guide.
Fix: Summarize examples to 1-2 sentences with a pointer to a detailed walkthrough in a knowledge doc, or remove one example and keep only the more complex case.

---

### /al-dev-handoff

**[Medium] Lens 2 — Structural Conventions**
Observation: Step numbering includes "Step 0.5", which is unusual and confusing. Fractional step numbers are non-standard and may cause parsing issues.
Fix: Rename "Step 0.5" to "Step 1" and renumber subsequent steps (2, 3, 4, 5, 6) for consistency.

---

### /al-dev-help

**[High] Lens 2 — Structural Conventions**
Observation: Frontmatter lacks `argument-hint` field, despite skill accepting arguments like "commands", "skills", "agents", "all", or a free-text description.
Fix: Add `argument-hint: "[commands|skills|agents|all|description]"` to frontmatter.

---

### /al-dev-interview

No findings.

---

### /al-dev-investigate

**[High] Lens 1 — Prompt Clarity**
Observation: Step 0 (Target Confirmation) ends with "Do these match? If findings and request disagree, stop and confirm before proceeding." This is ambiguous — does "confirm" mean restart the step, ask the user, or proceed anyway? No explicit branch given.
Fix: Replace with explicit decision tree: "If all align → continue to Step 1. If findings/request disagree → STOP and ask user for confirmation before proceeding."

---

### /al-dev-lint

**[High] Lens 1 — Prompt Clarity**
Observation: Step 1 shows two AL compile commands (`al-compile --output .dev/compile-errors.log` vs `al compile /project:. /packagecachepath:.alpackages ...`). It's unclear which is correct, when to use each, or why both are provided. The skill doesn't explain the difference.
Fix: Add a note: "Use `al-compile` if available (preferred). Fallback to `al compile` if `al-compile` is not in PATH. Both produce the same output log format."

---

### /al-dev-perf

**[Low] Lens 2 — Structural Conventions**
Observation: Step numbering includes "Step 1.5", which is non-standard. While explained, it's inconsistent with typical numbering (should be "Step 2" with subsections).
Fix: Rename "Step 1.5" to "Step 1a" or move it into Step 1 as a substep for clarity.

---

### /al-dev-plan

**[Low] Lens 2 — Structural Conventions**
Observation: Phase numbering includes "Phase 0", "Phase 0.5", "Phase 1–7", which is non-standard. While explained in context, the fractional numbering may be confusing for users accustomed to sequential numbering.
Fix: Consider renaming to sequential phases (Phase 1–8) with descriptive headers instead, or document why fractional numbering is used (e.g., "Phase 0 checks for prior progress; Phase 0.5 routes based on complexity; Phase 1 onwards is the main flow").

---

### /al-dev-release-notes

No findings.

---

### /al-dev-support

No findings.

---

### /al-dev-ticket

**[Medium] Lens 1 — Prompt Clarity**
Observation: Credential verification is mentioned in Step 2 and implicitly repeated in Step 2's dispatch prompt. The logic could be streamlined to avoid the appearance of redundant checks.
Fix: Move credential check earlier (after Step 1 branch decision, before dispatch) so it's a single check, not split between orchestrator and agent.

---

### /al-dev-document

No findings.

---

### /commit-learn

**[Medium] Lens 5 — Name Fit**
Observation: Skill name "commit-learn" is somewhat opaque. It could be mistaken for "learn from commits" rather than "recover corrupted files from commit integrity failures". The actual scope is file recovery, not learning.
Fix: Rename to `/commit-recover` or `/file-integrity-recover` for clarity. Keep "commit-learn" as an alias if backwards compatibility is needed.

---

## Skill Quality Summary

**Clean skills (no findings):**
- /al-dev-explore
- /al-dev-interview
- /al-dev-release-notes
- /al-dev-support
- /al-dev-document

**Skills with findings:**
- /al-dev-commit — 1 High
- /al-dev-develop — 1 Low
- /al-dev-fix — 2 findings (1 Medium, 1 Low)
- /al-dev-handoff — 1 Medium
- /al-dev-help — 1 High
- /al-dev-investigate — 1 High
- /al-dev-lint — 1 High
- /al-dev-perf — 1 Low
- /al-dev-plan — 1 Low
- /al-dev-ticket — 1 Medium

## Recommendations

**High priority (fix before next release):**
1. Add missing `argument-hint` fields to `/al-dev-commit` and `/al-dev-help`
2. Clarify Step 0 branching logic in `/al-dev-investigate`
3. Clarify AL compile command syntax in `/al-dev-lint`

**Medium priority (fix when touching the file):**
1. Rename Step 0.5 → Step 1 in `/al-dev-handoff`
2. Condense or move examples in `/al-dev-fix`
3. Streamline credential check in `/al-dev-ticket`
4. Rename `/commit-learn` to `/commit-recover`

**Low priority (nice to have):**
1. Improve jargon in `/al-dev-develop` with glossary
2. Standardize step numbering (avoid fractional steps in `/al-dev-perf` and `/al-dev-plan`)
