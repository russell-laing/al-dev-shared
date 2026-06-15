# Knowledge File Quality Report

Generated: 2026-06-14
Issues: HIGH (0), MEDIUM (2), LOW (2)

## HIGH Severity (Blocks Agent Guidance)

None identified.

---

## MEDIUM Severity (Incomplete Guidance)

### developer-invocation-patterns.md

**Section:** Example: Conditional routing in spawning skill (lines 213–238)

**Reference:**

- `agents/al-dev-developer-traditional.md` — Developer agent defers to this for dispatch patterns
- `agents/al-dev-developer-tdd.md` — Developer agent defers to this for dispatch patterns
- `skills/al-dev-fix/SKILL.md` — Skill references this for Context 2 spawning guidance
- `skills/al-dev-develop-orchestrate/SKILL.md` — Skill references this multiple times for dispatcher consistency

**Issue:** THIN — Section header "Example: Conditional routing in spawning skill" introduces the concept with 2 content lines before presenting extensive code examples. While the section as a whole is comprehensive, the introductory prose is minimal. The section assumes readers understand when conditional routing applies and why.

**Missing Content:**

- Clearer explanation of when/why conditional routing applies (vs. static routing)
- Decision tree showing haiku vs. Sonnet routing logic before jumping to code examples

**Fix:** Add 1–2 sentences explaining the purpose and decision criteria before the code examples begin. This will make the section more self-contained and easier for developers implementing dispatcher logic to follow.

---

### investigate-findings-template.md

**Sections:** "Regression Timeline" (lines 18–46) and "Example B: Long-standing defect (Recently working = no)" (lines 33–39)

**Reference:**

- `skills/al-dev-investigate/SKILL.md` — Skill explicitly reads this template before writing investigation findings

**Issue:** NO-CODE — The sections are titled to suggest code or structured investigation procedures, but provide no code examples or command snippets showing how to perform the investigations. Readers see narrative examples but no concrete `git` commands, search patterns, or output structures to follow.

**Missing Content:**

- For "Regression Timeline": Example `git log` or `git blame` command showing what to look for when tracing recent changes (Recently working = yes case)
- For "Example B": Sample investigation commands or output for approaching long-standing defects without recent blame data (e.g., git log with date ranges, searching commit messages)

**Fix:** Add fenced bash code blocks with actual commands or expected command output. Even pseudocode showing the investigation workflow would clarify the procedure.

---

## LOW Severity (Minor/False Positives)

- **File:** `knowledge/handoff-chain-map.md`
  - **Section:** "Identified Handoff Gaps" (lines 98–145)
  - **Issue:** THIN — Thin transition between section headers; "Identified Handoff Gaps" has 1 content line before "Current Deployment Gaps" subsection
  - **Reference:** No references found in active agents or skills (documentation only)
  - **Assessment:** Orphaned from operational guidance surface. File is not actively depended upon for skill/agent execution. The structural thinness is minor given lack of usage.
  - **Fix:** Low priority. Optional cleanup: merge the introductory definition into `## Gap Analysis` or delete the orphaned section header.

- **File:** `knowledge/map-change-rubber-duck-checks.md`
  - **Section:** "Path variations to handle during verification" (lines 529–535)
  - **Issue:** DEAD-REF (FALSE POSITIVE) — Validator flagged references to `knowledge/file.md` at lines 531–532
  - **Reference:** `.claude/skills/plan-health-findings/SKILL.md` — Maintainer skill references this for verification procedures
  - **Assessment:** False positive. Lines 531–532 are documentation examples showing path variation **patterns**, not actual file references. Text uses `knowledge/file.md` as a placeholder example path (like `foo.md`), not a real file to import.
  - **Fix:** None required. Optional: rename placeholder examples to `knowledge/example-file.md` to silence validator.

---

---

## Fix Recommendations

### High Priority

None.

### Medium Priority

1. **developer-invocation-patterns.md** — Add 1–2 sentences of introduction before the code examples in the "Example: Conditional routing in spawning skill" section (lines 213–214). Clarify the purpose: when to use conditional routing vs. static routing, and what the routing decision criteria are. This section is referenced by core developer agents and skills, so clarity improves correct implementation.

2. **investigate-findings-template.md** — Add fenced bash code blocks to the "Regression Timeline" and "Example B" sections with concrete `git` commands or expected output. Show examples of:
   - `git log` with date ranges for recent regressions
   - `git blame` output format
   - Searching commit messages for blame-driven hypotheses
   This template is actively used by `/al-dev-investigate` skill; concrete examples will improve usability.

### Low Priority

- **handoff-chain-map.md** — Optional: merge or reorganize the thin "Identified Handoff Gaps" section header for structural consistency. Not actively referenced by any skill, so low priority.

- **map-change-rubber-duck-checks.md** — Optional: rename example paths at lines 531–532 from `knowledge/file.md` to `knowledge/example-file.md` to silence validator. Does not affect correctness.

---

## High-Priority Fix Tasks

<!-- auto-generated by /audit-knowledge-quality — consumed by /fix-knowledge-quality -->

```yaml
tasks: []
```

*No HIGH-severity issues identified. MEDIUM-severity improvements recommended above.*
