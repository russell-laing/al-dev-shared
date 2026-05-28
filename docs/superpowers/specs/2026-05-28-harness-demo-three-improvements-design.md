# Design: Three Improvements from Harness Engineering Demo

**Date:** 2026-05-28
**Goal:** Apply three patterns from `coleam00/harness-engineering-demo` to strengthen `profile-al-dev-shared`
**Scope:** Skill frontmatter safety gates, solution plan pattern references, verifiable acceptance criteria
**Effort:** ~90 minutes total
**Source inspiration:** https://github.com/coleam00/harness-engineering-demo

---

## Background

Review of `coleam00/harness-engineering-demo` surfaced three patterns directly applicable to
`profile-al-dev-shared`:

1. **`disable-model-invocation: true`** — prevents auto-trigger of side-effect skills; the demo
   applies this to all four of its skills and documents it as the convention for "user-only,
   side-effect" invocations.

2. **Pattern Reference field in plan tasks** — each task in the demo's plan template includes
   `Pattern: <file>:L<line> — what to mirror`, forcing the planner to locate a concrete code
   analogue before writing instructions.

3. **Verifiable acceptance criteria** — the demo's `PROMPT.md` format requires each acceptance
   criterion to be a programmatically-checkable condition, not prose.

None of these patterns are addressed by today's earlier work (artifact-contract validator, skill
scaffold template, validator self-correction messages, hybrid improvements). All three changes
are additive and non-breaking.

---

## Existing Coverage Reviewed

- `docs/superpowers/plans/2026-05-28-artifact-contract-validator-and-skill-template.md` — adds
  a structural validator and skill scaffold template. Does not touch skill frontmatter flags or
  plan content quality.
- `docs/superpowers/plans/2026-05-28-shared-artifact-contracts-and-gates.md` — adds artifact
  contract matrix and final-gate wording. Acceptance criteria format is not in scope.
- `docs/superpowers/plans/2026-05-28-profile-al-dev-shared-hybrid-improvements.md` — adds
  compile gate to `al-dev-commit`, investigation tightening, intent-preflight. Does not address
  plan content quality or invocation safety.
- `docs/superpowers/plans/2026-05-28-harness-coverage-model.md` — coverage table only; does not
  change runtime behaviour.

---

## Problem Statement

Three narrow gaps remain after today's work:

1. **Accidental auto-trigger risk on action skills.** Skills that dispatch developer agents, commit
   to git, or write source code can be silently auto-triggered if a user's message matches their
   description. There is no frontmatter gate preventing this.

2. **Plan tasks lack a concrete pattern anchor.** When the solution architect writes an
   implementation task, it describes *what* to build but does not point the developer agent at an
   existing code pattern to mirror. Developer agents must infer patterns from scratch, which
   increases variance in output.

3. **Acceptance criteria are prose, not verifiable conditions.** The current plan template allows
   "validation works correctly" as an acceptance criterion. The commit gate cannot check this.
   The developer agent cannot self-verify against it. There is no structural connection between a
   plan's acceptance criteria and the `al-dev-commit` final gate.

---

## Change A: Explicit-Invocation Gates

### Mechanism

The `disable-model-invocation: true` YAML frontmatter field prevents a skill from being
auto-triggered by the model. The skill remains available as an explicit `/skill-name` slash
command.

### Classification Criterion

A skill receives `disable-model-invocation: true` when it meets **any** of:
- Dispatches developer agents that write source files
- Commits or modifies the git state
- Writes files outside `.dev/` (source code, release artifacts, documentation)
- Is only valid as a sequential follow-on to a preceding skill (workflow-ordered)

A skill keeps auto-trigger when it is an **entry point** — a skill the user invokes by describing
a goal ("plan this", "investigate this bug", "look at this ticket").

### Skills Receiving the Flag

| Skill | Reason |
|---|---|
| `al-dev-develop` | Dispatches developer agents; writes source files |
| `al-dev-commit` | Commits to git |
| `al-dev-fix` | Writes source code fixes |
| `al-dev-lint` | Can write files in `--fix` mode |
| `al-dev-review-develop` | Workflow-ordered: only valid after `al-dev-develop` |
| `al-dev-release-notes` | Writes durable release artifact |
| `al-dev-handoff` | Writes durable handoff artifact |
| `al-dev-document` | Writes documentation files |
| `al-dev-consolidate` | Writes `.dev/sessions/` consolidation artifacts |
| `commit-recover` | Modifies git state |
| `verify-commits` | Workflow-ordered sequential tool |
| `plan-with-critic-swarm` | Alternative planner; explicit invocation only |

### Skills Keeping Auto-Trigger

`al-dev-plan`, `al-dev-ticket`, `al-dev-investigate`, `al-dev-explore`, `al-dev-interview`,
`al-dev-support`, `al-dev-help`, `al-dev-perf`

### Convention Documentation

The skill scaffold template at `templates/skill-template/SKILL.md` receives a comment block
explaining the convention so that future skills default to the right choice.

### Files Changed

- `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-fix/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-lint/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-release-notes/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-handoff/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-document/SKILL.md`
- `profile-al-dev-shared/skills/al-dev-consolidate/SKILL.md`
- `profile-al-dev-shared/skills/commit-recover/SKILL.md`
- `profile-al-dev-shared/skills/verify-commits/SKILL.md`
- `profile-al-dev-shared/skills/plan-with-critic-swarm/SKILL.md`
- `templates/skill-template/SKILL.md` (convention comment)

---

## Change B: Pattern Reference per Object in Solution Plans

### Problem

The solution plan's Object Design section names objects and describes their purpose but does not
tell the developer agent what existing code to mirror. Developer agents must infer patterns from
scratch, which is slower and produces higher variance than following a verified existing example.

### Addition to `knowledge/solution-plan-template.md`

Each object entry in the Object Design section gains a required `Pattern reference:` line:

```markdown
**Codeunits:**
- Object ID 52xxx: "SalesPostingGuard"
  Purpose: Validate posting date on sales order release
  Key Methods: `ValidatePostingDate(SalesHeader: Record "Sales Header")`
  Pattern reference: `src/Codeunit/CustomerCreditCheck.Codeunit.al:L45` — mirrors the
    validation-on-release pattern (subscriber + guard codeunit split)
```

When no analogue exists:
```markdown
  Pattern reference: none — establishing new posting-guard pattern
```

The `none` declaration is explicit, not optional. It prevents silent omission from passing
unnoticed during review.

### Addition to `agents/al-dev-solution-architect.md`

The Research phase gains an explicit sub-step (add after the existing symbol-navigation
instructions, before the Design solution step):

> For each object in the Object Design, use `AL LSP` `find_references` or `al_find_references`
> (MCP fallback) to locate an existing object that uses the same structural pattern. Record its
> file path and line number as the `Pattern reference`. If no analogue exists in the project,
> record `none` with a one-line rationale.

### Files Changed

- `profile-al-dev-shared/knowledge/solution-plan-template.md`
- `profile-al-dev-shared/agents/al-dev-solution-architect.md`

---

## Change C: Verifiable Acceptance Criteria

### Problem

Prose acceptance criteria ("validation works correctly") cannot be checked by the developer
agent mid-task or by the `al-dev-commit` final gate. The existing artifact-contract matrix
requires success evidence but does not define what form that evidence must take at the plan
level.

### Format

Each criterion must be one of three types:

**Structural check** — file or symbol existence:
```
1. `src/Codeunit/SalesPostingGuard.Codeunit.al` exists and contains `procedure ValidatePostingDate`
2. `src/PageExtension/SalesOrderExt.PageExt.al` contains `SalesPostingGuard.ValidatePostingDate`
```

**Gate check** — tool exit code:
```
3. `al-compile` exits 0 with no new errors in `.dev/compile-errors.log`
```

**Pattern check** — forbidden code pattern is absent:
```
4. No `Error(StrSubstNo(` in new or modified files
```

**Manual check** — where no machine-checkable form exists, mark explicitly:
```
5. [manual] Posting is blocked when order date is before work date
```

Unlabelled prose criteria are not permitted. Each criterion must be actionable by the developer
agent for self-verification and by the `al-dev-commit` gate for completion confirmation.

### Addition to `knowledge/solution-plan-template.md`

The Acceptance Criteria section is reformulated to use the four-type format above, with one
example of each type.

### Addition to `agents/al-dev-solution-architect.md`

The Write output step gains (add as the final instruction in that step):

> Acceptance criteria must be numbered, with each criterion matching one of the four verifiable
> types (structural, gate, pattern, manual). Do not write unlabelled prose criteria.

### Addition to `skills/al-dev-commit/SKILL.md`

The pre-commit checklist step gains a cross-reference:

> Read the acceptance criteria from the solution plan (if present). For each structural, gate,
> or pattern criterion, confirm the condition is satisfied before proceeding. `[manual]` criteria
> are noted but do not block the commit gate.

### Files Changed

- `profile-al-dev-shared/knowledge/solution-plan-template.md`
- `profile-al-dev-shared/agents/al-dev-solution-architect.md`
- `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`

---

## Combined Scope Summary

| Change | Files touched | Risk |
|---|---|---|
| A — Explicit-invocation gates | 12 skill SKILL.md frontmatters + 1 template | Minimal — frontmatter only, no body changes |
| B — Pattern Reference | `solution-plan-template.md` + `al-dev-solution-architect.md` | Low — additive field, no existing fields removed |
| C — Verifiable criteria | `solution-plan-template.md` + `al-dev-solution-architect.md` + `al-dev-commit/SKILL.md` | Low — reformats template section, does not change runtime logic |

**Note:** B and C both modify the same two files. The implementation plan must combine these
into a single task per shared file — do not create separate tasks that each open and edit the
same file independently.

No generated projection artifacts need updating (frontmatter fields are Claude Code-specific;
B and C changes are agent-internal).

**Harness neutrality:** `disable-model-invocation` is a Claude Code-specific field. The
projection policy (`knowledge/agent-tool-projection-policy.md`) must be checked to confirm this
field is not propagated to Copilot or Codex projections. If it is, add an exclusion rule. If it
is not projected, no action is needed.

---

## Acceptance Criteria for This Design

1. All 12 target skills contain `disable-model-invocation: true` in their frontmatter
2. The 8 entry-point skills do **not** contain the flag
3. `templates/skill-template/SKILL.md` contains a comment explaining the convention
4. `knowledge/solution-plan-template.md` Object Design section includes `Pattern reference:` in
   each object block
5. `agents/al-dev-solution-architect.md` Step 4 includes the pattern-lookup sub-step
6. `knowledge/solution-plan-template.md` Acceptance Criteria section uses the four-type format
7. `agents/al-dev-solution-architect.md` Step 8 prohibits unlabelled prose criteria
8. `skills/al-dev-commit/SKILL.md` pre-commit step cross-references criteria check
9. `python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents` exits 0 after
   agent edits
10. `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared` exits 0 after all
    changes
