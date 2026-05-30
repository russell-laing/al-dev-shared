# Harness-Neutrality Enforcement — Design

**Date:** 2026-05-30
**Origin:** Rubber-duck of `docs/health/2026-05-29-plugin-health.md`
(`~/.claude/plans/rubber-duck-docs-health-2026-05-29-plugi-delightful-comet.md`)
**Status:** Approved design — ready for implementation plan

## Context

A `/plugin-health` sweep recommended changes that would have pushed
harness-specific tokens *into* the harness-neutral plugin surface
(`profile-al-dev-shared/`): rewriting `USER_GATE` → `AskUserQuestion`, `MCP:
<capability>` → `mcp__`, and pinning Claude-specific model IDs. Those tokens are
the Claude *projection output*, not the shared *source* vocabulary, and applying
them would also crash `generate-agent-projections.py`.

Root cause: maintainer lens agents hardcode the Claude projection-output
vocabulary as their notion of "canonical," and nothing forces that notion to
track `agent-tool-projection-policy.md`. The canonical vocabulary currently
lives in **four** places that have already drifted:

1. `knowledge/agent-tool-projection-policy.md` frontmatter (missing all MCP mappings)
2. `knowledge/harness-concepts.md` prose table
3. `scripts/generate-agent-projections.py` `default_projection_policy()` (has MCP mappings)
4. Hardcoded lists inside lens prompts (`quality-agent-lens-structure`, `design-agent-lens-tool-hygiene`)

This effort applies the verdict's accepted fixes **and** makes harness-neutrality
a strictly enforced, drift-proof property: one source of truth, validators that
fail on leakage, and a pre-commit gate that blocks it.

Out of scope (tracked via the normal `/plan-map-changes` flow, not neutrality):
spurious `name:` frontmatter fields, agent/plugin map staleness, bloat/clarity
findings.

## Goals

- Correct the lens prompts so sweeps stop recommending harness-specific tokens.
- Finish the documented (2026-05-27) haiku downgrade that was never applied to file.
- Make `agent-tool-projection-policy.md` the single machine-readable source of
  canonical capability vocabulary and model aliases.
- Close the neutrality validator's blind spots (generic `mcp__`, Claude model IDs).
- Add a checked-in pre-commit gate so neutrality cannot regress.

## Components

### C1 — Specific fixes (the verdict's accepted items)

- **`.claude/agents/quality-agent-lens-structure.md`** — replace the hardcoded
  "canonical names" list (lines 29–31) with the shared-**source** vocabulary:
  `USER_GATE, Read, Write, Edit, Glob, Grep, Bash, MCP: al-mcp-server,
  MCP: bc-code-intelligence, MCP: microsoft-docs`. Remove `AskUserQuestion`,
  `mcp__`-prefixed, and `Agent`/`WebSearch`/`WebFetch` (no shared agent uses
  them; they are not in the projection mapping and would break generation).
- **`.claude/agents/design-agent-lens-tool-hygiene.md`** — change the
  `mcp__`-prefixed reasoning (line 32) to the shared `MCP: <capability>` form so
  it correctly recognises MCP tools in shared agents.
- **Model downgrade** — convert all 5 shared agents whose `model:` is a
  `claude-*` ID to the tier alias documented in `docs/al-dev-agent-map.md`
  (all `haiku`): `al-dev-code-review`, `al-dev-commit-recover-verifier`,
  `al-dev-expert-reviewer`, `al-dev-performance-reviewer`,
  `al-dev-security-reviewer`. No map edit needed — the map already says `haiku`;
  the files catch up.

### C2 — Single source of truth

- **Complete the policy frontmatter** in `agent-tool-projection-policy.md`: add
  the MCP capability mappings (`MCP: al-mcp-server`, `MCP: bc-code-intelligence`,
  `MCP: microsoft-docs`) for `claude`/`copilot`/`codex`, matching what the
  generator currently hardcodes. Add `shared_model_aliases: [haiku, sonnet, opus]`.
- **Make the generator policy-driven** — `generate-agent-projections.py` loads
  the projection table from the policy frontmatter (PyYAML 6.0.3 is available)
  instead of `default_projection_policy()`. Remove the hardcoded dict; fail
  closed if the policy is missing or a capability has no mapping (preserve the
  existing `ValueError` contract).
- **Verification gate:** after the refactor, regenerate and assert
  `git diff profile-al-dev-shared/generated/` is empty — proves projection
  output is byte-identical and only the source of the table changed.

### C3 — Lens audit + sync test

- **Audit** all 21 lens agents in `.claude/agents/` for harness-specific
  assumptions of the same class. Known offenders fixed in C1; confirm the other
  19 are clean and record the result.
- **Sync test** in `scripts/validate-lens-agents.py`: parse the canonical tool
  list out of `quality-agent-lens-structure.md` and assert it equals the
  projection-policy source-token set (the `projection_rules` keys). Any future
  divergence between lens and policy fails the validator. The lens keeps a
  human-readable hardcoded list (no runtime policy read); the test keeps it honest.

### C4 — Harden `validate_harness_neutrality.py`

- **Generic `mcp__`** — add a forbidden pattern for any `mcp__` token (not just
  `mcp__plugin_profile-claude`). The two policy/concept files remain allowlisted.
- **Model allowlist** — add a check scoped to `agents/*.md`: parse the
  frontmatter `model:` value (strip any inline `# comment`) and fail unless it is
  in `shared_model_aliases` loaded from the policy. Catches `claude-*` dated IDs,
  cross-vendor names, and typos. Single source: the allowlist comes from the
  policy, not a second hardcoded copy.

### C5 — Pre-commit gate

- **Checked-in hook** — `.githooks/pre-commit` runs, and blocks the commit on
  any failure of:
  - `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`
  - `python3 scripts/validate-lens-agents.py`
  - a "projections current" check (regenerate to a temp dir and diff, or
    regenerate + `git diff --exit-code` on `generated/`).
- **Enablement** — `git config core.hooksPath .githooks` (one-time; currently
  unset/default). Document the enable step and the hook's checks in
  `CLAUDE.md` under Development Commands.

## Data flow (after)

```text
agent-tool-projection-policy.md (frontmatter)   ← single source
  ├─ generate-agent-projections.py  (loads table → projections)
  ├─ validate-lens-agents.py        (sync test: lens list == policy keys)
  └─ validate_harness_neutrality.py (model allowlist + mcp__/token scan)
                                     ↑ run by .githooks/pre-commit
```

## Verification

End-to-end, all must pass:

1. `python3 scripts/generate-agent-projections.py` then
   `git diff --exit-code profile-al-dev-shared/generated/` → no diff.
2. `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared` → PASS.
3. `python3 scripts/validate-lens-agents.py` → PASS (incl. new sync test).
4. **Negative tests** (inject then revert):
   - Add `model: claude-sonnet-4-6` to a shared agent → neutrality FAILS.
   - Add a `mcp__foo` token to a shared file → neutrality FAILS.
   - Edit the structure-lens list to drop a policy token → lens sync test FAILS.
   - Stage a bad change and attempt a commit → pre-commit hook blocks it.
5. `grep -rE '^model:\s*claude-' profile-al-dev-shared/agents/*.md` → empty.

## Risks & mitigations

- **Generator refactor changes output** — mitigated by the byte-identical
  `git diff` gate (Verification #1); if any diff appears, the policy frontmatter
  is incomplete and must be reconciled before merge.
- **Hook bypass (`--no-verify`)** — accepted; the hook is fast local feedback,
  not a security control. CI can be added later if an unbypassable backstop is needed.
- **Allowlist too strict for a future model** — adding a model means one edit to
  `shared_model_aliases` in the policy (the single source), which the validator reads.
