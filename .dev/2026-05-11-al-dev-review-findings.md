# Session Friction Analysis — russell-laing/al-dev-shared

**Date:** 2026-05-11
**Sessions analysed:** 5 sessions (2026-05-10 → 2026-05-11)
**Data source:** Copilot CLI session_store (SQL)

> **Scope:** This report is based on conversation turns, checkpoints, and file edits recorded in session_store. Raw tool-call errors, permission denials, and subagent-internal file operations are not captured in this data source. The al-dev-align branch created several files via subagents (check-alignment.py, test suite, SKILL.md) that do not appear in the `FILE_CHURN` table because session_store does not track subagent file writes. This means churn figures are under-counted; actual `SKILL.md` churn was 5 commits.

---

## Summary

The two-day session cluster (10–11 May) completed two significant deliverables — the harness-agnostic migration and the new `al-dev-align` audit skill — but the `al-dev-align` session (c538a090) accumulated at least 3 avoidable fix rounds caused by two root causes: a plan-spec self-contradiction around harness tokens, and a same-class JSON capture bug that the per-task quality reviewer missed in Step 1 and had to catch again in Step 7. A systemic Python environment conflict (libexpat / pytest) added friction to every task in that session without any workaround being documented. The 38-turn analysis session (8c6e7788) that preceded the migration suggests discovery and planning are sometimes interleaved rather than sequenced, which can cause churn when execution starts on an unsettled design.

---

## Friction Patterns

### Pattern 1: Same-class bug missed by per-task quality reviewers — HIGH

**Evidence:** 2 occurrences in 1 session (c538a090), same root cause

> "Step 1 JSON capture missing → fixed → Step 7 same bug found → fixed"

The JSON stdout capture pattern was absent from the bash command in Step 1 of SKILL.md. The quality reviewer found it and it was fixed. The same omission appeared in Step 7; the same reviewer found it again. Because per-task reviewers evaluate only the task's additions in isolation, they do not carry forward a running "known bugs checklist" that would flag recurrence of the same class of error.

**Recommendation:** Add to `AGENTS.md` under a new `## Quality Review Conventions` section:

```markdown
## Quality Review Conventions

**Iterative task reviews (per-task scope):**
When a quality reviewer finds a bug class in one task, it MUST add that class
to an explicit "watch list" carried into every subsequent task review in the
same session. Append to the review prompt:

  "Previously found in this session: [list bug classes]. Check all new bash
   command blocks for stdout capture; check all new JSON output paths for
   completeness."

This prevents the same class of bug being found twice across two sequential
review cycles.
```

---

### Pattern 2: Plan-spec self-contradiction causing 3 fix rounds — HIGH

**Evidence:** 3 fix rounds in 1 session (c538a090, Task 6)

> "Task 6 spec compliance review returned NON-COMPLIANT because SKILL.md body contained harness-specific tokens (claude, copilot) in code block examples. The spec said 'no harness-specific tokens' but the plan itself used those tokens in the specified SKILL.md content."

The plan author wrote content for SKILL.md that included harness-specific token literals (as code-block examples) while simultaneously imposing a prohibition on such tokens. The contradiction was not caught during plan review, only during Task 6's spec-compliance check — at which point 3 rounds of corrections were needed because each fix introduced a new variant of the same problem.

**Recommendation:** Add to `docs/superpowers/specs/` template and to `AGENTS.md`:

```markdown
## Plan Self-Review Requirement

Before submitting any plan for execution, the plan author MUST perform a
self-consistency pass:

1. **Token audit:** If the plan prohibits harness-specific tokens in output
   files, scan all *plan-specified file content* for those same tokens. Any
   occurrence in a code block example counts as a violation of the plan's own
   rule and must be resolved (genericise the example or add an explicit
   exception with reasoning) before execution begins.

2. **Constraint propagation check:** For every "must not contain X" rule in
   a spec, verify that no task step directs an agent to write content that
   contains X.

Unresolved contradictions at plan-review time cost 3× more to fix during
execution than at authoring time.
```

---

### Pattern 3: Python environment blocker undocumented — MEDIUM

**Evidence:** Affected all 7 tasks of session c538a090 (systemic, no workaround recorded)

> "Python 3.13 libexpat conflict prevented pytest from running throughout the session. All test verification was done via python3.13 -c inline scripts."

The libexpat conflict is a known macOS Python 3.13 issue. Because it was not documented before the session, each task had to discover and work around it independently. No canonical workaround was recorded for future sessions.

**Recommendation:** Add to `AGENTS.md` under a new `## Known Environment Issues` section:

```markdown
## Known Environment Issues

**Python 3.13 / libexpat conflict (macOS)**
`pytest` may fail with a libexpat dynamic-library conflict under Python 3.13
on macOS. Workaround: run tests inline:

```bash
python3.13 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('mod', 'path/to/script.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.some_function() == expected_value, 'Test failed'
print('PASS')
"
```

Until the environment is repaired, use this pattern for all Python test
verification in al-dev-shared sessions.
```

---

### Pattern 4: Final code review scope wider than per-task reviews — HIGH

**Evidence:** 2 bugs (duplicate-token detection logic, flexible separator regex) caught only by the final code review in session c538a090; zero per-task reviews caught them

Per-task reviewers validating isolated additions cannot evaluate cross-task interactions. The final review is the only backstop for a class of bugs that should be caught earlier.

**Recommendation:** Add to `AGENTS.md`:

```markdown
## Tiered Code Review Protocol

Per-task reviews check task-scope correctness. A **mid-point integration
review** must be scheduled at the halfway task (e.g. after Task 4 of 7) to
review the whole module assembled so far — not just the latest additions.

Integration review checklist additions (beyond per-task scope):
- [ ] All regex patterns tested against the full token set, not just the
      tokens introduced in the current task
- [ ] Deduplication / set-membership logic verified end-to-end across all
      scan functions added to date
- [ ] CLI flag names consistent across all `argparse` definitions added so far
```

---

### Pattern 5: Session_store blind to subagent file operations — LOW

**Evidence:** FILE_CHURN table shows 8 files with 1 edit each; actual branch had 5+ files created by subagents and SKILL.md with 5 commits

This is a tool-scope limitation. Analyst reports should note when a session was subagent-driven and supplement session_store data with `git log --oneline` counts.

---

## File Churn

| File | Sessions | Edits (tracked) | Inferred Cause |
|---|---|---|---|
| `profile-al-dev-shared/skills/al-dev-align/SKILL.md` | 1 | 1 tracked + ~5 commits | Plan-spec contradiction + repeated JSON capture bug |
| `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` | 1 | 1 | Advisory alignment check integration |
| `profile-al-dev-shared/skills/al-dev-handoff/SKILL.md` | 1 | 1 | Advisory alignment check integration |
| `profile-al-dev-shared/knowledge/feedback-resolution.md` | 1 | 1 | Harness-agnostic migration |
| `AGENTS.md` | 1 | 1 | Harness mapping table added |

---

## Action Items (Priority Order)

1. **AGENTS.md** — Add `## Quality Review Conventions`: per-task reviewers carry a running "known bug class" watch-list forward. *(Pattern 1 — HIGH)*

2. **AGENTS.md + plan template** — Add `## Plan Self-Review Requirement`: token-audit and constraint-propagation check before execution. *(Pattern 2 — HIGH)*

3. **AGENTS.md** — Add `## Tiered Code Review Protocol`: mandate mid-point integration review at task N/2. *(Pattern 4 — HIGH)*

4. **AGENTS.md** — Add `## Known Environment Issues`: Python 3.13 / libexpat workaround. *(Pattern 3 — MEDIUM)*

5. **al-dev-session-analyst agent** — Add git-log supplement instruction for subagent-heavy sessions. *(Pattern 5 — LOW)*
