# AL Dev Plugin Map — Design Spec

**Date:** 2026-05-16
**Status:** Approved for implementation
**Audience:** Plugin author (personal reference for gap analysis and extension planning)

## Goal

Produce `docs/al-dev-plugin-map.md` — a single Markdown document with Mermaid diagrams
that shows the active skills, agents, and their relationships in `profile-al-dev-shared`.
The document is a personal reference tool for spotting coverage gaps and extension
opportunities, not onboarding material.

**Scope:** Active skills only. Archived items (`al-dev-test`, all `*-test-engineer` agents,
`al-dev-test-coverage-reviewer`) must not appear.

---

## Document Structure (Option A)

Two layers:

1. **Lifecycle overview** — one diagram covering all entry points and how they connect
2. **Per-skill drill-downs** — one diagram per skill showing internal phases, agents
   spawned, and key `.dev/` outputs

---

## Layer 1 — Lifecycle Overview Diagram

**Type:** Mermaid `flowchart TD`

**What it shows:**

- Three entry paths into the lifecycle:
  - Support path: `/ticket` → `/support`
  - Investigation path: `/investigate` → decision (fix | plan)
  - Direct fix: `/fix`
- Main development spine: `/plan` → `/develop` → `/commit`
- Complexity gate on `/plan`: trivial requests route to `/fix`, everything else
  proceeds through the spine
- File handoffs labelled on edges: `ticket-context.md`, `explore-findings.md`,
  `solution-plan.md`, `code-review.md`
- Terminal nodes: `git commit`, `customer reply`

**Node legend:** Use Mermaid shape conventions —
  - Skills: rounded rectangle `(skill-name)`
  - Decision gates: diamond `{question}`
  - Outputs: stadium/pill shape `([file.md])`
  - Agents: not shown at this level (detail is in Layer 2)

---

## Layer 2 — Per-Skill Drill-Down Diagrams

**Type:** Mermaid `flowchart LR` (one per skill, left-to-right for readability)

**What each diagram shows:**
- Numbered phases inside the skill
- Which agent(s) are spawned at each phase, and in what pattern (serial/parallel/×N)
- Key `.dev/` file written as output

### `/al-dev-ticket`

| Phase | Agent | Pattern | Output |
|-------|-------|---------|--------|
| 1 — Fetch & write context | `al-dev-ticket-agent` | ×1 | `ticket-context.md` |

### `/al-dev-support`

| Phase | Agent | Pattern | Output |
|-------|-------|---------|--------|
| 1 — Research & draft reply | `al-dev-support-agent` | ×1 | customer reply |

### `/al-dev-investigate`

| Phase | Agent | Pattern | Output |
|-------|-------|---------|--------|
| 1 — Form hypotheses | *(skill itself)* | — | 2–4 hypotheses inline |
| 2 — Test hypotheses | `al-dev-explore` | ×2 parallel | — |
| 3 — Synthesise | *(skill itself)* | — | `explore-findings.md` |

### `/al-dev-fix`

Two sub-paths depending on complexity:

**Trivial path:**
| Phase | Agent | Pattern | Output |
|-------|-------|---------|--------|
| 1 — Implement | `al-dev-developer` | ×1 | AL source files |
| 2 — Compile + lint | *(skill itself)* | — | — |

**Non-trivial path:**
| Phase | Agent | Pattern | Output |
|-------|-------|---------|--------|
| 1 — Analyse | `al-dev-solution-architect` | ×1 (5 min) | approach summary |
| 2 — Implement | `al-dev-developer` | ×1 | AL source files |
| 3 — Compile + lint | *(skill itself)* | — | — |

### `/al-dev-plan`

| Phase | Agent | Pattern | Output |
|-------|-------|---------|--------|
| 1 — Context gather | *(skill itself)* | — | — |
| 2 — Competing designs | `al-dev-solution-architect` | ×2–3 parallel | design proposals |
| 3 — Synthesise winner | *(skill itself)* | — | `solution-plan.md` |

### `/al-dev-develop`

| Phase | Agent | Pattern | Output |
|-------|-------|---------|--------|
| 1 — Read plan | *(skill itself)* | — | — |
| 2 — Implement | `al-dev-developer` | ×2–3 parallel | AL source files |
| 3 — Review | `al-dev-security-reviewer` | ×1 parallel | — |
| 3 — Review | `al-dev-expert-reviewer` | ×1 parallel | — |
| 3 — Review | `al-dev-performance-reviewer` | ×1 parallel | `code-review.md` |
| 4 — Synthesise | *(skill itself)* | — | — |

*(3 reviewers run in parallel — security, AL expert, performance)*

### `/al-dev-commit`

| Phase | Agent | Pattern | Output |
|-------|-------|---------|--------|
| 1 — Analysis pass | `al-dev-commit-agent` | ×1 | commit groups + messages |
| 2 — Execution pass | `al-dev-commit-agent` | ×1 | git commits |

---

## Annotations to Include

After the lifecycle diagram, include a short **Gap & Opportunity** section with
placeholder annotations — empty bullet points under each of these headings so the
document is ready for you to fill in as you analyse:

```markdown
## Observations

### Agents used by only one skill
- (fill in)

### Skills with no dedicated agent (skill does the work itself)
- (fill in)

### Potential shared agents not yet extracted
- (fill in)

### Extension opportunities
- (fill in)
```

---

## Output File

**Path:** `docs/al-dev-plugin-map.md`

**Format:** GitHub-flavoured Markdown with Mermaid code blocks.

Follow `profile-al-dev-shared/markdown/md-mermaid-helper.md` for all diagram syntax.

---

## What to Exclude

- `al-dev-test` skill
- `al-dev-unit-test-engineer`, `al-dev-integration-test-engineer`,
  `al-dev-scenario-test-engineer`, `al-dev-edge-case-test-engineer`,
  `al-dev-test-coverage-reviewer` agents
- Skills out of scope for this document: `al-dev-align`, `al-dev-autonomous`,
  `al-dev-document`, `al-dev-explore`, `al-dev-handoff`, `al-dev-help`,
  `al-dev-interview`, `al-dev-lint`, `al-dev-perf`, `al-dev-plan`,
  `al-dev-release-notes`, `commit-learn`
  *(these are peripheral — not part of the core lifecycle being mapped)*
