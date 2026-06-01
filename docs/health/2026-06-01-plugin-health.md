# Plugin Health — 2026-06-01

> Comprehensive health sweep of profile-al-dev-shared plugin surface.
> All lenses completed; 73 findings ranked by severity and dimension.

---

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| **High** | 0 | 5 | 3 | **8** |
| **Medium** | 5 | 4 | 2 | **11** |
| **Low** | 3 | 1 | 0 | **4** |

### Top 5 Ranked Actions

1. **[HIGH] Add `name:` field to 20 agents** — Required for canonical registration
   - Files: All agents in `profile-al-dev-shared/agents/`
   - Fix: Add `name: <agent-name>` to YAML frontmatter (20 × 1 min)

2. **[HIGH] Fix al-dev-code-review critical model mismatch** — File declares `haiku`, map documents `sonnet`
   - File: `profile-al-dev-shared/agents/al-dev-code-review.md`
   - Fix: Update to match map specification (1 min)

3. **[MEDIUM] Label 160+ unlabeled code blocks** — Affects all agents and skills
   - Files: All of `profile-al-dev-shared/agents/` and `profile-al-dev-shared/skills/`
   - Fix: Add language specifiers (bash, json, python, al, yaml) to code blocks (~90 min)

4. **[MEDIUM] Trim unused tools from 14 agents** — Improve clarity of actual capabilities
   - Affects: al-dev-commit-ooxml-validator, al-dev-commit-recover-verifier, al-dev-developer-tdd, al-dev-developer-traditional, al-dev-diagnostics-fixer, al-dev-docs-writer, al-dev-expert-reviewer, al-dev-performance-reviewer, al-dev-release-notes-writer, al-dev-script-engineer, al-dev-security-reviewer, al-dev-support-researcher, plan-map-changes-duck-worker, plugin-health-team
   - Fix: Remove unused tools from frontmatter (5 min each)

5. **[HIGH] Clarify ambiguous instructions in 6 agents + 22 skills** — Blocks usability and testing
   - Top blockers: al-dev-commit-recover-verifier, al-dev-developer-tdd, al-dev-interview
   - Fix: Resolve conditional paths, bounds, and failure cases per file

---

## Design Suggestions

### Tool Hygiene: 14 Agents with Unused Declarations

Trim unused tools to improve clarity of actual capabilities:

- **al-dev-commit-ooxml-validator**: Remove `Read`
- **al-dev-commit-recover-verifier**: Remove `Bash`, `Read`
- **al-dev-developer-tdd**: Remove `Edit`, `Glob`
- **al-dev-developer-traditional**: Remove `Edit`, `Glob`
- **al-dev-diagnostics-fixer**: Audit `Glob`, `Grep`, `Bash` usage
- **al-dev-docs-writer**: Audit `Glob`, `Grep` usage
- **al-dev-expert-reviewer**: Remove `Grep`
- **al-dev-performance-reviewer**: Remove `Grep`
- **al-dev-release-notes-writer**: Remove unused MCP declarations
- **al-dev-script-engineer**: Audit `Edit`, `Glob`, `Grep` usage
- **al-dev-security-reviewer**: Remove `Grep`
- **al-dev-support-researcher**: Audit `Read`, MCP usage
- **plan-map-changes-duck-worker**: Remove `Bash`
- **plugin-health-team**: Remove `Bash`, `Read`

### Model Fit: 4 Agents Need Stronger Models

Upgrade to match task complexity:

| Agent | Current | Recommended | Justification |
|-------|---------|-------------|---------------|
| al-dev-interview | haiku | sonnet | Conduct 40+ deep technical questions with iterative refinement |
| al-dev-support-reply-drafter | haiku | sonnet | Requires critical judgment to distinguish customer opinions from technical facts |
| al-dev-code-review | haiku | sonnet | "Comprehensive" code review with "high signal-to-noise ratio" |
| al-dev-commit-recover-verifier | haiku | sonnet | Choose fallback strategy and determine unrecoverability under uncertainty |

### Scope Isolation: 7 Agents with Separable Concerns

Consider splitting to isolate concerns:

- **al-dev-commit-agent-analysis**: Analysis / Validation checking
- **al-dev-diagnostics-fixer**: Parse / Apply fixes
- **al-dev-solution-architect**: Complexity classification / Design phase
- **al-dev-ticket-agent**: Fetch metadata / Parse images
- **al-dev-support-researcher**: Research / Synthesize findings
- **plan-map-changes-duck-worker**: Universal checks / Type-specific checks
- **plugin-health-team**: Batch orchestration / Result aggregation

### Caller Alignment: 2 Agent Map Corrections

- **al-dev-commit-message-drafter** (line 94): `PROPOSED_GROUPS` should be OUTPUT not INPUT
- **al-dev-commit-recover-verifier** (line 551): `REPO` should be optional not required

### Skill Complexity: 3 Skills Over-Phased

Atomise into layered concerns:

- **al-dev-plan** (8 phases): Split discovery (0–1.6) from debate/synthesis (2–6)
- **al-dev-review-develop** (6 phases): Split compile gate (1–2) from review panel (3–6)
- **al-dev-develop** (5 phases): Split preparation (0–2) from execution (3–4)

### Skill Merge Candidates: 2 Pairs

- **al-dev-explore + al-dev-perf**: Both pre-analysis tributaries with identical structure
- **al-dev-document + al-dev-release-notes**: Both light orchestrators with single writer agent

### Skill Handoff Gaps: 1 Orphaned Output

- **al-dev-release-notes**: Output never consumed downstream; natural next: `/plugin-publish` (deferred)

---

## Quality Findings

### Critical: Model Mismatch in al-dev-code-review

File `profile-al-dev-shared/agents/al-dev-code-review.md` declares `model: haiku-4-5` but docs/al-dev-agent-map.md documents `model: sonnet-4-6`. This creates a contract violation: callers expect sonnet-level code review quality. Immediate action required.

### Bloat: 8 Agents and 7 Skills Over-Instrumented

**Agents:**
- **plan-map-changes-duck-worker** (397 lines): 131-line procedure block should extract to knowledge file
- **al-dev-solution-architect** (151 lines): Evidence hierarchy repeated 3 times
- **al-dev-developer-tdd & al-dev-developer-traditional**: Duplicate AL standards; reference shared knowledge
- **al-dev-commit-agent-analysis** (151 lines): Highly procedural; could reference template

**Skills:**
- al-dev-commit, al-dev-fix, al-dev-develop, plan-map-changes, al-dev-plan, al-dev-review-develop, al-dev-consolidate

### Clarity: 6 Agents with Ambiguous Instructions

- **al-dev-commit-recover-verifier**: "Previous commit" ambiguous
- **al-dev-developer-tdd**: Incomplete pre-flight verification conditional
- **al-dev-interview**: "Expect 40+ questions" lacks bounds
- **al-dev-solution-architect**: "If it is available" vague
- **plan-map-changes-duck-worker**: Universal check failure path not specified
- **plugin-health-team**: "Pending for resume" is pseudo-code

### Clarity: All 22 Skills with Ambiguous Instructions

Examples: advisory mode failure (al-dev-commit), multi-match tiebreaker (al-dev-consolidate), deduplication logic (al-dev-develop), lint-halt condition (al-dev-fix), suggestion vs requirement (al-dev-help), question batching (al-dev-interview), partial response handling (al-dev-investigate), unverified classification (al-dev-perf), clarification retry count (al-dev-plan), unexpected fields (al-dev-release-notes), reviewer timeout (al-dev-review-develop), curl error handling (al-dev-ticket), retry logic (commit-recover), U1–U3 details (plan-map-changes), dispatch mechanism (plan-with-critic-swarm), dispatch.py failure (plugin-health), group membership (verify-commits).

### Description Mismatch: 3 Agents

- **CRITICAL: al-dev-code-review**: Model mismatch (file haiku vs. map sonnet)
- **al-dev-commit-agent-execute**: Outputs include `STRIPPED_ATTRIBUTIONS` but caller skill doesn't consume it
- **al-dev-explore**: Description incomplete (explores but also writes; should say "explores and documents")

### Name Fit: 6 Agents

- **al-dev-developer-tdd & al-dev-developer-traditional**: Better: `al-dev-implement-{tdd|traditional}`
- **al-dev-ticket-agent**: No verb; better: `al-dev-ticket-fetcher`
- **plan-map-changes-duck-worker**: Methodology in name; better: `al-dev-duck-verifier`
- **plugin-health-team**: Role not verb; better: `plugin-health-orchestrator`
- **al-dev-commit-agent-{analysis|execute}**: "Agent" redundant; better: `al-dev-commit-{analyzer|executor}`

### Name Fit: 7 Skills

- **al-dev-diagram-generator**: Better: `al-dev-generate-diagrams`
- **al-dev-perf**: Abbreviated; better: `al-dev-analyze-perf`
- **al-dev-release-notes**: Implicit verb; better: `al-dev-generate-release-notes`
- **al-dev-ticket**: Scope overloaded
- **plan-map-changes**: Better: `implement-map-suggestions`
- **plan-with-critic-swarm**: Better: `al-dev-plan-with-review`
- **plugin-health**: Better: `plugin-audit` or `plugin-health-sweep`

### Structure Issues: Critical Gaps

**20 agents missing `name:` field** — Required for canonical registration across all harnesses

**160+ unlabeled code blocks** — All agents and skills; missing language specifiers (bash, json, python, al, yaml, etc.)

**Missing Outputs sections** — 1 agent (plugin-health-team) missing explicit documentation; multiple skills lack documented `.dev/` artifact list

---

## Naming Violations

1. **20 agents**: missing `name:` in frontmatter (required field)
2. **2 agents**: non-canonical model names (opus → claude-opus-4-7)
3. **3 files**: output file naming violations (template literals not rendered, redundancy, undated artifacts)

---

## Graph Deltas

No orphaned agents or dead links detected in plugin surface. All 24 agents referenced by skills are properly registered and documented.

Pre-planning skills (al-dev-explore, al-dev-interview, al-dev-perf) correctly positioned as optional tributaries to main Layer 1 lifecycle.

---

## Next Steps

1. Review this dossier and prioritize findings
2. Run `/plan-map-changes` to scope improvements against live codebase
3. Execute via issue-driven workflow or planning skill

---

**Generated by /plugin-health-report on 2026-06-01**
