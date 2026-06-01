# Architectural Decisions

This file records key model assignments, skill design decisions, and deprecations
that are stable and should not be re-litigated via health sweeps or analysis tools.

When a health sweep or rubber-duck analysis generates a recommendation that
contradicts a decision here, reject the recommendation and reference this file.

---

## Agent Model Assignments

### al-dev-code-review: haiku (not sonnet)

**Decided:** 2026-06-01
**Reason:** No active callers — no skill references this agent in any dispatch.
Upgrading to sonnet adds cost with no benefit.
**Do not:** Recommend sonnet upgrade via health sweep until a caller is added.
**Revisit if:** A skill begins dispatching this agent for code-review duties.

### al-dev-interview: sonnet (not haiku)

**Decided:** 2026-06-01
**Reason:** Conducts 40+ adaptive questions with conflict resolution and spec synthesis.
Haiku cannot sustain this reasoning scope across multiple turns.
**Do not:** Downgrade to haiku — will degrade spec quality and increase downstream rework.

### al-dev-commit-message-drafter: sonnet (not haiku)

**Decided:** 2026-06-01
**Reason:** Multi-step task: commit grouping analysis + message composition. Haiku
was underspecified; sonnet provides appropriate sustained reasoning.

### al-dev-support-reply-drafter: sonnet (not haiku)

**Decided:** 2026-06-01
**Reason:** Severity classification + tone synthesis for customer replies requires judgment.
Haiku was underspecified for multi-step decision-making.

### al-dev-commit-recover-verifier: sonnet (not haiku)

**Decided:** 2026-06-01
**Reason:** Chooses fallback recovery strategy across three methods, writes recovery report.
Requires sustained reasoning under uncertainty — haiku is insufficient.

---

## Skill Consolidations

### al-dev-support removed (consolidated into al-dev-ticket --mode=full)

**Decided:** 2026-06-01
**Reason:** Duplicate surface — al-dev-support duplicated al-dev-ticket with --mode=full.
Archived at `profile-al-dev-shared/archived/skills/al-dev-support/`.
**Do not:** Recreate al-dev-support as a standalone skill.

---

## Agent Archival

### plugin-health-team and plan-map-changes-duck-worker archived

**Decided:** 2026-06-01
**Reason:** Orphaned after plugin-health and plan-map-changes were restructured.
No active callers. Archived at `profile-al-dev-shared/archived/agents/`.
**Do not:** Reference these agents in new skills without checking archived/ for current contracts.
