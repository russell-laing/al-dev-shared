# Lens Neutrality Audit — 2026-05-30

**Scope:** All 21 lens agents in `.claude/agents/` audited for
harness-specific assumptions (projected tool tokens, `mcp__` prefixes,
dated `claude-*` model IDs, harness dispatch syntax, harness settings paths).

**Method:** `grep -rlnE 'AskUserQuestion|mcp__|ask_user|subagent_type|agent_type:|claude-[a-z]|~/\.claude' .claude/agents/*.md`

**Result:** CLEAN. The two prior offenders —
`quality-agent-lens-structure.md` (hardcoded Claude tool list) and
`design-agent-lens-tool-hygiene.md` (`mcp__` reasoning) — were corrected to
the shared-source vocabulary. The remaining 19 lens agents contain no
harness-specific tokens.

**Guard against regression:** `scripts/validate-lens-agents.py` now asserts
the structure lens's canonical tool list equals the projection-policy source
tokens (`projection_rules.claude` keys). Any future divergence fails the
validator and the pre-commit hook.
