# Design (Parked): Validator Self-Correction Message Audit

**Date:** 2026-05-28
**Status:** Parked — revisit after the artifact-contract validator and skill scaffold template land
**Goal:** Audit existing repo-local validators so their failure output instructs self-correction rather than only reporting violations
**Scope:** Three existing scripts and their tests
**Effort estimate:** ~45 minutes

---

## Status

This design is **not scheduled for implementation**. It is recorded here so the underlying observation is not lost, and so the work can be picked up cleanly later without re-deriving the analysis.

Active companion design: `docs/superpowers/specs/2026-05-28-artifact-contract-validator-and-skill-template-design.md`.

---

## Background

`profile-al-dev-shared` ships three repo-local validators:

- `scripts/validate_harness_neutrality.py` — flags harness-specific vocabulary leakage
- `scripts/validate-lens-agents.py` — checks authored-agent frontmatter and structural conventions
- `scripts/validate-knowledge-quality.py` — flags structural issues in knowledge documents

Each validator reliably emits *that* something is wrong, but the messages vary in how well they instruct *what to do about it*.

Fowler — *Harness Engineering* — describes the pattern at length: a maintainability sensor reaches its full value when its output drives self-correction. A linter message that names the file, the rule, and a single concrete fix lets an agent (or maintainer) act without re-research. Osmani — *Agent Harness Engineering* — calls this "failures verbose, success silent": failure output should not just shout, it should prescribe.

The new artifact-contract validator described in the companion design already adopts this pattern in its output shape. The three existing validators could be brought into alignment with the same convention, producing a consistent self-correction style across the repo's sensor surface.

---

## Problem Statement

Current validator output names the violation but not always the rule reference or the corrective action. Examples of the inconsistency:

- A neutrality violation may say `harness token "Claude Code" found in skills/foo/SKILL.md:42` without naming `knowledge/harness-concepts.md` as the rule source or suggesting a concrete substitution.
- A lens-agent violation may report `agent missing tools section` without naming the canonical agent template or the projection policy that depends on the section.
- A knowledge-quality violation may report `stub section detected` without saying which canonical section structure the document is expected to follow.

The effect is that maintainers (and agents reading the failure output) must re-locate the rule each time. The fix is bounded: standardise the message shape and add the missing breadcrumbs.

---

## Proposed Message Shape

A common shape across all three validators:

```text
<file>:<line> — <rule-id>: <one-sentence statement of the violation>
  rule: <canonical knowledge doc that defines the rule>
  fix: <single concrete action a maintainer or agent can take>
```

Worked example for neutrality:

```text
profile-al-dev-shared/skills/foo/SKILL.md:42 — neutrality-violation: forbidden harness token "Claude Code"
  rule: knowledge/harness-concepts.md says shared authored files use generic vocabulary
  fix: replace "Claude Code" with "the harness", or move the line to .claude/ if it must be harness-specific
```

Worked example for lens-agents:

```text
profile-al-dev-shared/agents/foo.md — agent-structure: missing tools block in frontmatter
  rule: knowledge/agent-tool-projection-policy.md requires a declared tools list for projection
  fix: add a tools: list to the frontmatter; run scripts/generate-agent-projections.py after editing
```

Worked example for knowledge-quality:

```text
profile-al-dev-shared/knowledge/foo.md:1 — knowledge-stub: section "## Body" has no content
  rule: knowledge documents must have substantive content under every declared header
  fix: either fill the section or remove the header
```

---

## Scope of the Audit

The audit is strictly an **output-only** change. The validator detection logic does not change.

For each of the three scripts:

1. Enumerate the failure messages currently emitted.
2. Rewrite each message to the proposed shape.
3. Update each unit test that asserts on message content.
4. Verify against fixture inputs that the output remains parseable by anything that already consumes it (the plugin-health daemon and any CI invocations).

**Out of scope:**

- New rules
- Changed detection logic
- New validator scripts (the artifact-contract validator is its own design)
- Output format changes beyond the message body (no JSON output mode, no severity levels)

---

## Files That Would Change

| File | Change |
|---|---|
| `scripts/validate_harness_neutrality.py` | Message strings only |
| `scripts/validate-lens-agents.py` | Message strings only |
| `scripts/validate-knowledge-quality.py` | Message strings only |
| `scripts/tests/test_validate_harness_neutrality.py` | Assertions matching new strings |
| Any existing tests for the other two validators (if present) | Same |

No new files. No file removals.

---

## Why This Is Parked

The active design (artifact-contract validator + skill scaffold template) targets a structural drift risk created by today's commits. Its leverage decays the longer it waits.

This validator-message audit:

- targets long-standing UX, not new drift
- has no dependency on the active design
- can be picked up in any future session without losing context

Therefore: park, document, revisit.

---

## Pickup Notes for Future Implementation

When restarting this work:

1. Confirm the artifact-contract validator from the companion design exists and is using the standard message shape; treat it as the canonical reference.
2. Walk each of the three scripts and inventory the messages they emit on planted violations against fixture inputs.
3. Refactor messages to the standard shape; keep one commit per validator so the diffs stay reviewable.
4. Run the full validator suite against the live tree afterwards to confirm no behavioural regression.

---

## Rejected Alternatives

### Introduce structured output (JSON / SARIF)

Rejected for this design. The maintainer audience reads plain text from the terminal, and the agent audience parses prose well. Structured output is a larger lift and a separate decision.

### Add severity levels

Rejected for this design. The validators currently treat any violation as a failure; adding warning/error tiers would require deciding which rules degrade and which block, and that is a policy decision, not a message-shape decision.

### Build a shared validator library

Rejected for this design. The three validators are short scripts with different domains. Sharing a message-formatting helper is a reasonable refactor inside the audit, but the validators themselves stay independent.
