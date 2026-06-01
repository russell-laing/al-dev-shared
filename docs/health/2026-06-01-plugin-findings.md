# Plugin Surface Findings — 2026-06-01

> Health sweep of profile-al-dev-shared/ (24 agents, 20 distributed skills + 2 utility skills)
> 
> All lenses completed in single session; zero missing lens outputs.

---

## Design Findings

### Design-Agent-Lens-Tool-Hygiene

**Trim candidates** — Agents with unused tool declarations:

- **al-dev-commit-ooxml-validator:** Read (declared but not used)
- **al-dev-commit-recover-verifier:** Bash, Read (declared but not used)
- **al-dev-developer-tdd:** Edit, Glob (declared but not used)
- **al-dev-developer-traditional:** Edit, Glob (declared but not used)
- **al-dev-diagnostics-fixer:** Glob, Grep, Bash (not all used)
- **al-dev-docs-writer:** Glob, Grep (not all used)
- **al-dev-expert-reviewer:** Grep (declared but not used)
- **al-dev-performance-reviewer:** Grep (declared but not used)
- **al-dev-release-notes-writer:** MCP: al-mcp-server, MCP: bc-code-intelligence (not used)
- **al-dev-script-engineer:** Edit, Glob, Grep (not all used)
- **al-dev-security-reviewer:** Grep (declared but not used)
- **al-dev-support-researcher:** Read, MCP: bc-code-intelligence (not all used)
- **plan-map-changes-duck-worker:** Bash (declared but not used)
- **plugin-health-team:** Bash, Read (declared but not used)

**Action:** Trim unused tools from frontmatter to improve clarity of actual capabilities.

---

### Design-Agent-Lens-Model-Fit

**Remodel candidates:**

| Agent | Current | Recommended | Justification |
|-------|---------|-------------|---------------|
| al-dev-interview | haiku | sonnet | Conduct 40+ deep technical questions with iterative refinement. Requires sustained multi-turn reasoning beyond haiku's mechanical design. |
| al-dev-support-reply-drafter | haiku | sonnet | Requires critical judgment to distinguish customer opinions from technical facts. Haiku appropriate for mechanical drafting only. |
| al-dev-code-review | haiku | sonnet | Described as "comprehensive" code review with "high signal-to-noise ratio." Should match parallel specialist reviewers. |
| al-dev-commit-recover-verifier | haiku | sonnet | Choose fallback strategy and determine unrecoverability. Requires decision-making under uncertainty. |

---

### Design-Agent-Lens-Scope-Isolation

**Split candidates** — Agents with separable concerns:

- **al-dev-commit-agent-analysis:** Analysis / Validation checking
- **al-dev-diagnostics-fixer:** Parse / Apply fixes
- **al-dev-solution-architect:** Complexity classification / Design phase
- **al-dev-ticket-agent:** Fetch metadata / Parse images
- **al-dev-support-researcher:** Research / Synthesize findings
- **plan-map-changes-duck-worker:** Universal checks / Type-specific checks
- **plugin-health-team:** Batch orchestration / Result aggregation

---

### Design-Agent-Lens-Caller-Alignment

**Alignment issues:**

1. **al-dev-commit-message-drafter:** Agent map lists PROPOSED_GROUPS as INPUT; should be OUTPUT (line 94).
2. **al-dev-commit-recover-verifier:** Agent map marks REPO as required; should be optional/inferred (line 551).

---

### Design-Agent-Lens-Usage-Patterns

**Status: PASS** — Single-use agents appropriately kept separate despite brief scope (documented contracts justify independence over inlining).

---

### Design-Skill-Lens-Complexity

**Atomise candidates:**

1. **al-dev-plan (8 phases)** — Split discovery (0–1.6) from debate/synthesis (2–6).
2. **al-dev-review-develop (6 phases)** — Split compile gate (1–2) from review panel (3–6).
3. **al-dev-develop (5 phases)** — Split preparation (0–2) from execution (3–4).

---

### Design-Skill-Lens-Near-Duplicates

**Merge candidates:**

- **al-dev-explore + al-dev-perf** (both pre-analysis tributaries with identical structure)
- **al-dev-document + al-dev-release-notes** (both light orchestrators, single writer agent)

(al-dev-interview/al-dev-investigate and al-dev-lint/commit-recover justified as separate despite structural similarity due to different user interaction models and triggers.)

---

### Design-Skill-Lens-Handoff-Gaps

**Extend candidates:**

- **al-dev-release-notes output** — Orphaned (never consumed downstream). Natural next: `/al-dev-publish` (deferred).

---

### Design-Skill-Lens-Preplanning

**Status: PASS** — All pre-planning skills correctly positioned in Layer 1 as optional tributaries with documented consumption.

---

### Design-Skill-Lens-Shared-Backbone

**Status: PASS** — All agents used 2+ times have documented invocation patterns in knowledge files.

---

## Quality Findings

### Quality-Agent-Lens-Bloat

**Bloat candidates:**

- **plan-map-changes-duck-worker** (397 lines): 131-line procedure block should extract to knowledge file.
- **al-dev-solution-architect** (151 lines): Evidence hierarchy repeated 3 times; consolidate to single section.
- **al-dev-developer-tdd & al-dev-developer-traditional:** Duplicate AL code standards and compile safeguards; reference shared knowledge instead.
- **al-dev-commit-agent-analysis** (151 lines): Highly procedural; could reference template.

---

### Quality-Agent-Lens-Clarity

**Clarity issues** — 6 agents with ambiguous instructions:

- **al-dev-commit-recover-verifier:** "Previous commit" ambiguous.
- **al-dev-developer-tdd:** Incomplete pre-flight verification conditional.
- **al-dev-interview:** "Expect 40+ questions" lacks bounds.
- **al-dev-solution-architect:** "If it is available" vague.
- **plan-map-changes-duck-worker:** Universal check failure path not specified.
- **plugin-health-team:** "Pending for resume" is pseudo-code.

---

### Quality-Agent-Lens-Description

**Contract mismatches:**

- **CRITICAL: al-dev-code-review** — Model mismatch: file declares `haiku`, map documents `sonnet`.
- **al-dev-commit-agent-execute:** Outputs include STRIPPED_ATTRIBUTIONS but caller skill doesn't consume it.
- **al-dev-explore:** Description incomplete ("explores" but also Writes; should say "explores and documents").

---

### Quality-Agent-Lens-Name-Fit

**Name-fit issues (6 agents):**

- **al-dev-developer-tdd & -traditional:** Role + methodology split; better: `al-dev-implement-{tdd|traditional}`.
- **al-dev-ticket-agent:** No verb; better: `al-dev-ticket-fetcher`.
- **plan-map-changes-duck-worker:** Methodology in name; better: `al-dev-duck-verifier` or consistent prefix.
- **plugin-health-team:** Role not verb; better: `plugin-health-orchestrator`.
- **al-dev-commit-agent-{analysis|execute}:** "Agent" in name redundant; better: `al-dev-commit-{analyzer|executor}`.

---

### Quality-Agent-Lens-Structure

**Structural issues:**

- **20 of 24 agents:** Missing `name:` field in frontmatter (required).
- **21 agents:** 140+ unlabeled code blocks (missing language specifiers).
- **1 agent (plugin-health-team):** Missing Inputs and Outputs sections.

---

### Quality-Skill-Lens-Bloat

**Bloat candidates (7 skills):**

- **al-dev-commit, al-dev-fix, al-dev-develop, plan-map-changes, al-dev-plan, al-dev-review-develop, al-dev-consolidate** — Oversized phases, repetitive dispatch patterns, dead conditional branches.

---

### Quality-Skill-Lens-Clarity

**Clarity issues — All 22 skills have ambiguous instructions:**

Examples: al-dev-commit (advisory mode failure path), al-dev-consolidate (multi-match tiebreaker), al-dev-develop (deduplication logic), al-dev-fix (lint-halt condition), al-dev-help (suggestion vs. requirement), al-dev-interview (sync vs. async questions), al-dev-investigate (partial responses), al-dev-perf (unverified classification), al-dev-plan (clarification retry count), al-dev-release-notes (unexpected fields), al-dev-review-develop (reviewer timeout), al-dev-ticket (curl error handling), commit-recover (retry logic), plan-map-changes (U1-U3 details), plan-with-critic-swarm (dispatch mechanism), plugin-health (dispatch.py failure), verify-commits (group membership).

---

### Quality-Skill-Lens-Description

**Status: PASS** — All descriptions align with body content and documented outputs.

---

### Quality-Skill-Lens-Name-Fit

**Name-fit issues (7 skills):**

- **al-dev-diagram-generator:** Methodology not verb; better: `al-dev-generate-diagrams`.
- **al-dev-perf:** Abbreviated; better: `al-dev-analyze-perf`.
- **al-dev-release-notes:** Implicit verb; better: `al-dev-generate-release-notes`.
- **al-dev-ticket:** Scope overloaded (context-only vs. full).
- **plan-map-changes:** Domain object + action; better: `implement-map-suggestions`.
- **plan-with-critic-swarm:** Methodology in name; better: `al-dev-plan-with-review`.
- **plugin-health:** Abstract noun; better: `plugin-audit` or `plugin-health-sweep`.

---

### Quality-Skill-Lens-Structure

**Structural issues:**

- **All 22 skills:** 160+ unlabeled code blocks (blocks without language specifiers: bash, json, python, al, etc.).
- **Multiple skills:** Missing explicit "Outputs" section documenting which .dev/ files are written.

---

### Naming-Convention-Lens

**Violations:**

1. **20 agents:** Missing `name:` in frontmatter.
2. **2 agents:** Model names not canonical (`opus` → `claude-opus-4-7`).
3. **3 files:** Output file naming: template literals not rendered, redundant "plan-plan", undated artifacts.

---

## Highest-Leverage Actions

1. **Trim unused tools** (14 agents) — Quick wins, 5 min each.
2. **Label code blocks** (160+ across skills) — Systematic: 1 pass per file, 2–5 min each.
3. **Remodel agents** (4 agents to stronger models) — Strategic: interview/support-reply-drafter/code-review/commit-recover-verifier.
4. **Add `name:` frontmatter** (20 agents) — Required for canonical registration, 1 min each.
5. **Fix critical model mismatch** (al-dev-code-review: haiku vs. sonnet) — 1 min.
6. **Resolve alignment issues** (2 agent map corrections) — 5 min.
7. **Extract shared standards** (AL patterns, compile safeguards) to knowledge files — Medium effort, high payoff.
8. **Split 3 skills** (al-dev-plan, al-dev-review-develop, al-dev-develop) into layered concerns — High impact, planning phase required.

---

Next: Run `/plan-map-changes --mode=full` to prioritize and scope improvements.
