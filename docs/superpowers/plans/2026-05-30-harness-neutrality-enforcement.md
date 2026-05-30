# Harness-Neutrality Enforcement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop maintainer lens sweeps from recommending harness-specific tokens, finish the documented haiku downgrade, and make harness-neutrality a drift-proof property backed by one source of truth, hardened validators, and a checked-in pre-commit gate.

**Architecture:** `agent-tool-projection-policy.md` frontmatter becomes the single machine-readable source for both the projection table and the model allowlist. The generator loads its table from that frontmatter (no hardcoded dict); two validators read the same frontmatter (lens-list sync + model allowlist + generic `mcp__` scan); a `.githooks/pre-commit` runs all three plus a "projections current" check.

**Tech Stack:** Python 3.13, PyYAML 6.0.3 (confirmed available), Bash git hooks, Markdown.

**Repo testing note:** This repo validates scripts by *running them*, not via `pytest` (which hits a libexpat conflict under Python 3.13 — see CLAUDE.md). Accordingly, the "tests" in this plan are (a) transient inline-Python verifications using the CLAUDE.md `importlib` pattern, and (b) running the actual validator/generator scripts and asserting their output. The durable regression guards are the `git diff --exit-code` byte-identical gate and the lens↔policy sync test.

---

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `.claude/agents/quality-agent-lens-structure.md` | Structural-conventions lens prompt | Replace hardcoded canonical tool list with shared-source vocabulary, wrapped in machine-readable markers |
| `.claude/agents/design-agent-lens-tool-hygiene.md` | Tool-hygiene lens prompt | Change `mcp__`-prefixed reasoning to `MCP: <capability>` form |
| `profile-al-dev-shared/agents/al-dev-code-review.md` (+4) | Shared agent definitions | `model: claude-sonnet-4-6` → `model: haiku` |
| `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md` | Single source of truth | Complete frontmatter: MCP mappings, reconciled codex strings, `shared_model_aliases` |
| `scripts/generate-agent-projections.py` | Projection generator | Load table from policy frontmatter; remove hardcoded dict |
| `scripts/validate-lens-agents.py` | Lens validator | Add lens↔policy sync test |
| `scripts/validate_harness_neutrality.py` | Neutrality validator | Add generic `mcp__` scan + policy-sourced model allowlist |
| `.githooks/pre-commit` | Commit gate | New: run all three checks + projections-current diff |
| `docs/health/2026-05-30-lens-neutrality-audit.md` | C3 audit record | New: record the 21-lens audit result |
| `CLAUDE.md` | Maintainer docs | Document the hook + `core.hooksPath` enable step |

Tasks are ordered by dependency: baseline first, then C1 source fixes, then C2 single-source-of-truth (depends on the policy being complete), then C3/C4 validators (depend on C1+C2), then C5 hook (depends on all validators), then end-to-end verification.

---

## Task 1: Baseline — reconcile pre-existing projection staleness

The committed `generated/` projections are already stale vs. their shared source (two agents edited without regenerating). The byte-identical gate in Task 7 and the hook in Task 9 cannot pass until this is fixed. This task touches **only** generated projection files.

**Files:**
- Modify: `profile-al-dev-shared/generated/agents/{claude,copilot,codex}/al-dev-solution-architect.*`
- Modify: `profile-al-dev-shared/generated/agents/{claude,copilot,codex}/al-dev-support-reply-drafter.*`

- [ ] **Step 1: Confirm the staleness (pre-state)**

Run: `python3 scripts/generate-agent-projections.py && git diff --stat profile-al-dev-shared/generated/`
Expected: a non-empty diff listing 6 files (claude/copilot/codex × solution-architect + support-reply-drafter). The generator has now rewritten them in place.

- [ ] **Step 2: Verify the regenerated content is the intended catch-up**

Run: `git diff profile-al-dev-shared/generated/agents/claude/al-dev-solution-architect.md`
Expected: the diff adds an `Implementation Tasks` section (Files/Gotcha/Validate) — i.e. the projection now matches the current shared source. No other agents appear.

- [ ] **Step 3: Commit the regenerated baseline**

```bash
git add profile-al-dev-shared/generated/
git commit -m "chore(projections): regenerate stale projections to match shared source

Establishes a byte-identical baseline so the neutrality enforcement
work can assert an empty generated/ diff."
```

- [ ] **Step 4: Verify the tree is now byte-identical**

Run: `python3 scripts/generate-agent-projections.py && git diff --exit-code profile-al-dev-shared/generated/ && echo CLEAN`
Expected: `CLEAN` (exit 0, no diff).

---

## Task 2: C1 — Fix the structural-conventions lens canonical tool list

Replace the hardcoded Claude-projection vocabulary with the harness-neutral source vocabulary, wrapped in machine-readable markers so Task 8's sync test can parse it.

**Files:**
- Modify: `.claude/agents/quality-agent-lens-structure.md:29-31`

- [ ] **Step 1: Replace the canonical-names bullet**

Replace this exact block:

```markdown
- `tools` field is present in YAML frontmatter and contains only canonical names:
  `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `Agent`, `AskUserQuestion`,
  `WebSearch`, `WebFetch`, or `mcp__`-prefixed tool names
```

with:

```markdown
- `tools` field is present in YAML frontmatter and contains only canonical
  **source-vocabulary** capability names — the harness-neutral terms, not any
  harness's projected tool names. The canonical set is:
  <!-- canonical-tools:start -->
  `USER_GATE`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `MCP: al-mcp-server`, `MCP: bc-code-intelligence`, `MCP: microsoft-docs`
  <!-- canonical-tools:end -->
```

- [ ] **Step 2: Verify the tokens and markers are present**

Run: `grep -n 'canonical-tools:start\|canonical-tools:end\|MCP: al-mcp-server\|USER_GATE' .claude/agents/quality-agent-lens-structure.md`
Expected: 4 matching lines — both markers, the MCP token, and `USER_GATE`.

- [ ] **Step 3: Verify the removed tokens are gone**

Run: `grep -nE 'AskUserQuestion|mcp__|WebSearch|WebFetch' .claude/agents/quality-agent-lens-structure.md || echo GONE`
Expected: `GONE`.

- [ ] **Step 4: Commit**

```bash
git add .claude/agents/quality-agent-lens-structure.md
git commit -m "fix(lens): structure lens uses shared-source tool vocabulary

Replaces the Claude projection-output tool names with the canonical
neutral capability set and wraps it in canonical-tools markers for the
lens-policy sync test."
```

---

## Task 3: C1 — Fix the tool-hygiene lens MCP reasoning

**Files:**
- Modify: `.claude/agents/design-agent-lens-tool-hygiene.md:32`

- [ ] **Step 1: Replace the `mcp__` red-flag line**

Replace this exact line:

```markdown
- Agent has `mcp__`-prefixed tools but no MCP usage is described in the body
```

with:

```markdown
- Agent has `MCP: <capability>` tools (the shared source form) but no MCP usage is described in the body
```

- [ ] **Step 2: Verify**

Run: `grep -n 'MCP: <capability>' .claude/agents/design-agent-lens-tool-hygiene.md && (grep -q 'mcp__' .claude/agents/design-agent-lens-tool-hygiene.md && echo "STILL HAS mcp__" || echo OK)`
Expected: the matched line, then `OK`.

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/design-agent-lens-tool-hygiene.md
git commit -m "fix(lens): tool-hygiene lens recognises shared MCP: <capability> form

Aligns the MCP red-flag wording with the source vocabulary so it
correctly detects MCP tools declared in shared agents."
```

---

## Task 4: C1 — Apply the documented haiku model downgrade

The agent map already records all five reviewer/verifier agents as `haiku`; the files still carry `claude-sonnet-4-6`. Bring the files into line. The generator does **not** project `model:`, so this produces no `generated/` diff.

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-code-review.md`
- Modify: `profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md`
- Modify: `profile-al-dev-shared/agents/al-dev-expert-reviewer.md`
- Modify: `profile-al-dev-shared/agents/al-dev-performance-reviewer.md`
- Modify: `profile-al-dev-shared/agents/al-dev-security-reviewer.md`

- [ ] **Step 1: Downgrade all five in one pass**

In each of the five files, replace the frontmatter line `model: claude-sonnet-4-6` with `model: haiku`. (Use the Edit tool per file; the string is identical in all five.)

- [ ] **Step 2: Verify no `claude-*` model IDs remain**

Run: `grep -rE '^model:\s*claude-' profile-al-dev-shared/agents/*.md || echo CLEAN`
Expected: `CLEAN`.

- [ ] **Step 3: Verify all five now read haiku**

Run: `grep -E '^model: haiku' profile-al-dev-shared/agents/al-dev-{code-review,commit-recover-verifier,expert-reviewer,performance-reviewer,security-reviewer}.md`
Expected: 5 lines, each `model: haiku`.

- [ ] **Step 4: Verify projections unchanged (model is not projected)**

Run: `python3 scripts/generate-agent-projections.py && git diff --exit-code profile-al-dev-shared/generated/ && echo CLEAN`
Expected: `CLEAN`.

- [ ] **Step 5: Commit**

```bash
git add profile-al-dev-shared/agents/al-dev-code-review.md profile-al-dev-shared/agents/al-dev-commit-recover-verifier.md profile-al-dev-shared/agents/al-dev-expert-reviewer.md profile-al-dev-shared/agents/al-dev-performance-reviewer.md profile-al-dev-shared/agents/al-dev-security-reviewer.md
git commit -m "fix(agents): downgrade 5 reviewer agents to haiku tier alias

Applies the 2026-05-27 downgrade already recorded in the agent map.
Replaces claude-sonnet-4-6 dated IDs with the neutral haiku alias."
```

---

## Task 5: C2 — Complete the projection-policy frontmatter

Make the policy frontmatter the exact machine source the generator will load: add MCP mappings for all three harnesses, reconcile the codex `native_capability` strings to match what the generator currently emits (so output stays byte-identical), and add `shared_model_aliases`. This task edits **only** the policy file; the generator still uses its hardcoded dict until Task 6, so no `generated/` diff results yet.

**Files:**
- Modify: `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md:1-54` (the frontmatter block)

- [ ] **Step 1: Replace the entire frontmatter block**

Replace everything from the opening `---` through the closing `---` on line 54 with this exact block:

```yaml
---
shared_capabilities:
  - USER_GATE
  - shared `tools:` metadata
shared_model_aliases:
  - haiku
  - sonnet
  - opus
projection_rules:
  claude:
    USER_GATE:
      tool: AskUserQuestion
    Read:
      tool: Read
    Write:
      tool: Write
    Edit:
      tool: Edit
    Glob:
      tool: Glob
    Grep:
      tool: Grep
    Bash:
      tool: Bash
    "MCP: al-mcp-server":
      tool: "mcp__plugin_profile-claude-al-dev_al-mcp-server__<tool>"
    "MCP: bc-code-intelligence":
      tool: "mcp__plugin_profile-claude-al-dev_bc-code-intelligence-mcp__<tool>"
    "MCP: microsoft-docs":
      tool: "mcp__plugin_profile-claude-al-dev_microsoft_docs_mcp__<tool>"
  copilot:
    USER_GATE:
      tool: ask_user
    Read:
      tool: read
    Write:
      tool: edit
    Edit:
      tool: edit
    Glob:
      tool: glob
    Grep:
      tool: grep
    Bash:
      tool: execute
    "MCP: al-mcp-server":
      tool: "al-mcp-server-<tool>"
    "MCP: bc-code-intelligence":
      tool: "bc-code-intelligence-mcp-<tool>"
    "MCP: microsoft-docs":
      tool: "microsoft_docs_mcp-<tool>"
  codex:
    USER_GATE:
      developer_instruction: request_user_input
    Read:
      native_capability: read files available in the active Codex session
    Write:
      native_capability: edit files available in the active Codex session
    Edit:
      native_capability: edit files available in the active Codex session
    Glob:
      native_capability: search files available in the active Codex session
    Grep:
      native_capability: search file contents available in the active Codex session
    Bash:
      native_capability: run shell commands allowed by the active Codex session
    "MCP: al-mcp-server":
      native_capability: use the AL symbol lookup MCP capability available in the active Codex session
    "MCP: bc-code-intelligence":
      native_capability: use the BC code intelligence MCP capability available in the active Codex session
    "MCP: microsoft-docs":
      native_capability: use the Microsoft Docs MCP capability available in the active Codex session
failure_policy:
  - Generation fails if a shared capability has no documented harness mapping.
  - Codex output must use documented TOML keys only; do not invent a synthetic tools field.
---
```

(The prose body below the frontmatter is unchanged. The codex strings above are deliberately the generator's exact current wording — e.g. "read files available in the active Codex session" — so that Task 6 stays byte-identical.)

- [ ] **Step 2: Verify the frontmatter parses and contains every mapping**

Run:

```bash
python3 -c "
import yaml, re
fm = re.match(r'^---\n(.*?)\n---', open('profile-al-dev-shared/knowledge/agent-tool-projection-policy.md').read(), re.DOTALL).group(1)
d = yaml.safe_load(fm)
assert d['shared_model_aliases'] == ['haiku','sonnet','opus'], d['shared_model_aliases']
for h in ('claude','copilot','codex'):
    keys = set(d['projection_rules'][h])
    expected = {'USER_GATE','Read','Write','Edit','Glob','Grep','Bash','MCP: al-mcp-server','MCP: bc-code-intelligence','MCP: microsoft-docs'}
    assert keys == expected, (h, keys ^ expected)
print('PASS: policy frontmatter complete and parseable')
"
```

Expected: `PASS: policy frontmatter complete and parseable`.

- [ ] **Step 3: Verify the generator output is still byte-identical (it still uses its hardcoded dict here)**

Run: `python3 scripts/generate-agent-projections.py && git diff --exit-code profile-al-dev-shared/generated/ && echo CLEAN`
Expected: `CLEAN`.

- [ ] **Step 4: Commit**

```bash
git add profile-al-dev-shared/knowledge/agent-tool-projection-policy.md
git commit -m "feat(policy): complete projection frontmatter as single source

Adds MCP capability mappings for all three harnesses, reconciles codex
native_capability strings to the generator's exact wording, and adds
shared_model_aliases for the neutrality model allowlist."
```

---

## Task 6: C2 — Make the generator policy-driven

Load the projection table from the policy frontmatter and delete the hardcoded `default_projection_policy()`. A transient equality check proves the loaded table equals the old dict *before* deletion; the `git diff --exit-code` gate proves output is byte-identical *after*.

**Files:**
- Modify: `scripts/generate-agent-projections.py`

- [ ] **Step 1: Add the PyYAML import**

At the top of the imports (after `import re`), add:

```python
import yaml
```

- [ ] **Step 2: Add the policy loader (immediately above `def default_projection_policy`)**

```python
def load_projection_policy(policy_path: Path) -> dict:
    """Load the projection table from the policy frontmatter.

    claude/copilot capabilities map to a flat tool-name string (the `tool`
    key); codex capabilities keep their dict form (`developer_instruction`
    or `native_capability`), matching what the render functions expect.
    """
    frontmatter, _ = _extract_frontmatter(policy_path.read_text(encoding="utf-8"))
    data = yaml.safe_load(frontmatter)
    rules = data.get("projection_rules")
    if not rules:
        raise ValueError(f"Projection policy {policy_path} has no projection_rules")
    policy: dict = {}
    for harness, capabilities in rules.items():
        policy[harness] = {}
        for capability, mapping in capabilities.items():
            if "tool" in mapping:
                policy[harness][capability] = mapping["tool"]
            else:
                policy[harness][capability] = dict(mapping)
    return policy
```

- [ ] **Step 3: Prove the loaded table equals the hardcoded dict (transient check, before deletion)**

Run:

```bash
python3 -c "
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('gen', 'scripts/generate-agent-projections.py')
gen = importlib.util.module_from_spec(spec); spec.loader.exec_module(gen)
loaded = gen.load_projection_policy(Path('profile-al-dev-shared/knowledge/agent-tool-projection-policy.md'))
hard = gen.default_projection_policy()
assert loaded == hard, 'MISMATCH:\n' + '\n'.join(
    f'{h}:{k}: loaded={loaded[h].get(k)!r} hard={hard[h].get(k)!r}'
    for h in hard for k in set(hard[h]) | set(loaded.get(h, {}))
    if loaded.get(h, {}).get(k) != hard[h].get(k))
print('PASS: loaded policy is byte-equal to hardcoded dict')
"
```

Expected: `PASS: loaded policy is byte-equal to hardcoded dict`. If this fails, the codex/MCP strings in Task 5 do not match — fix the policy frontmatter before continuing.

- [ ] **Step 4: Add a `--policy-path` argument and switch `main()` to the loader**

In `main()`, replace this block:

```python
    parser.add_argument("--agents-root", default="profile-al-dev-shared/agents")
    parser.add_argument("--output-root", default="profile-al-dev-shared/generated/agents")
    args = parser.parse_args()

    agents_root = Path(args.agents_root)
    output_root = Path(args.output_root)
    agents = [load_agent(path) for path in sorted(agents_root.glob("*.md"))]
    write_all_projections(output_root, agents, default_projection_policy())
```

with:

```python
    parser.add_argument("--agents-root", default="profile-al-dev-shared/agents")
    parser.add_argument("--output-root", default="profile-al-dev-shared/generated/agents")
    parser.add_argument(
        "--policy-path",
        default="profile-al-dev-shared/knowledge/agent-tool-projection-policy.md",
    )
    args = parser.parse_args()

    agents_root = Path(args.agents_root)
    output_root = Path(args.output_root)
    policy = load_projection_policy(Path(args.policy_path))
    agents = [load_agent(path) for path in sorted(agents_root.glob("*.md"))]
    write_all_projections(output_root, agents, policy)
```

- [ ] **Step 5: Delete `default_projection_policy()`**

Remove the entire `def default_projection_policy() -> dict:` function — from its `def` line through the final `}` of the returned dict and the blank line that follows, up to (not including) `def _project_tools`. The `ValueError` fail-closed contract in `_project_tools` is unchanged.

- [ ] **Step 6: Verify the hardcoded dict is gone**

Run: `grep -n 'default_projection_policy' scripts/generate-agent-projections.py || echo GONE`
Expected: `GONE`.

- [ ] **Step 7: Byte-identical gate — regenerate and diff**

Run: `python3 scripts/generate-agent-projections.py && git diff --exit-code profile-al-dev-shared/generated/ && echo CLEAN`
Expected: `CLEAN`. This is the C2 verification gate: it proves only the *source* of the table changed, not the output.

- [ ] **Step 8: Commit**

```bash
git add scripts/generate-agent-projections.py
git commit -m "refactor(generator): load projection table from policy frontmatter

Removes the hardcoded default_projection_policy() dict; the generator now
reads agent-tool-projection-policy.md as the single source. Output is
byte-identical (git diff on generated/ is empty)."
```

---

## Task 7: C3 — Lens audit + lens↔policy sync test

Confirm all 21 lens agents are free of harness-specific assumptions (the two offenders were fixed in Tasks 2–3), record the audit, and add a sync test that fails if the structure lens's canonical list ever diverges from the policy source tokens.

**Files:**
- Create: `docs/health/2026-05-30-lens-neutrality-audit.md`
- Modify: `scripts/validate-lens-agents.py`

- [ ] **Step 1: Run the audit sweep across all 21 lens agents**

Run: `grep -rlnE 'AskUserQuestion|mcp__|ask_user|subagent_type|agent_type:|claude-[a-z]|~/\.claude' .claude/agents/*.md || echo CLEAN`
Expected: `CLEAN` (Tasks 2–3 removed the only two offenders).

- [ ] **Step 2: Record the audit result**

Create `docs/health/2026-05-30-lens-neutrality-audit.md`:

```markdown
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
```

- [ ] **Step 3: Add the sync-test imports and helpers to the validator**

In `scripts/validate-lens-agents.py`, after the existing `from pathlib import Path` import block, add:

```python
import yaml

POLICY_PATH = os.path.join(REPO, "profile-al-dev-shared/knowledge/agent-tool-projection-policy.md")
STRUCTURE_LENS = os.path.join(AGENTS_DIR, "quality-agent-lens-structure.md")


def _canonical_tools_from_lens(path: str):
    """Extract the backtick-quoted tokens between the canonical-tools markers."""
    text = open(path).read()
    block = re.search(
        r"<!-- canonical-tools:start -->(.*?)<!-- canonical-tools:end -->",
        text,
        re.DOTALL,
    )
    if not block:
        return None
    return set(re.findall(r"`([^`]+)`", block.group(1)))


def _policy_source_tokens(path: str):
    """Return the projection_rules.claude capability keys from the policy."""
    fm = re.match(r"^---\n(.*?)\n---", open(path).read(), re.DOTALL).group(1)
    data = yaml.safe_load(fm)
    return set(data["projection_rules"]["claude"].keys())
```

(`REPO`, `AGENTS_DIR`, `os`, `re`, `Path` are already defined/imported at the top of the file.)

- [ ] **Step 4: Append the sync check after the agent loop, before the `if failures:` block**

Insert immediately before the final `if failures:` line:

```python
lens_tokens = _canonical_tools_from_lens(STRUCTURE_LENS)
policy_tokens = _policy_source_tokens(POLICY_PATH)
if lens_tokens is None:
    failures.append(_format_failure(
        STRUCTURE_LENS,
        "lens-canonical-markers",
        "could not find <!-- canonical-tools:start/end --> markers",
        "wrap the canonical tool list in canonical-tools:start/end HTML comments",
    ))
elif lens_tokens != policy_tokens:
    missing = policy_tokens - lens_tokens
    extra = lens_tokens - policy_tokens
    failures.append(_format_failure(
        STRUCTURE_LENS,
        "lens-policy-sync",
        f"canonical tool list diverges from projection policy "
        f"(missing from lens: {sorted(missing)}; extra in lens: {sorted(extra)})",
        "reconcile the structure lens canonical-tools list with "
        "projection_rules.claude keys in agent-tool-projection-policy.md",
    ))
```

- [ ] **Step 5: Run the validator and confirm the sync test passes**

Run: `python3 scripts/validate-lens-agents.py`
Expected: `PASS — 21 agents valid, 4 skills refactored.`

- [ ] **Step 6: Prove the sync test actually fails on divergence (inject, assert, revert)**

```bash
cp .claude/agents/quality-agent-lens-structure.md /tmp/lens.bak
# Drop one token from the canonical list:
sed -i '' 's/`MCP: microsoft-docs`//' .claude/agents/quality-agent-lens-structure.md
python3 scripts/validate-lens-agents.py; echo "exit=$?"
cp /tmp/lens.bak .claude/agents/quality-agent-lens-structure.md && rm /tmp/lens.bak
python3 scripts/validate-lens-agents.py
```

Expected: first run prints a `lens-policy-sync` failure with `exit=1`; after restore, the final run prints `PASS — 21 agents valid, 4 skills refactored.`

- [ ] **Step 7: Commit**

```bash
git add scripts/validate-lens-agents.py docs/health/2026-05-30-lens-neutrality-audit.md
git commit -m "test(lens): assert structure lens list matches projection policy

Records the 21-lens neutrality audit (CLEAN) and adds a sync test that
fails whenever the structure lens canonical-tools list diverges from the
projection-policy source tokens."
```

---

## Task 8: C4 — Harden the neutrality validator

Add a generic `mcp__` scan (catches any `mcp__` token, not just the Claude plugin prefix) and a policy-sourced model allowlist scoped to `agents/*.md`.

**Files:**
- Modify: `scripts/validate_harness_neutrality.py`

- [ ] **Step 1: Add the PyYAML import**

After `import re`, add:

```python
import yaml
```

- [ ] **Step 2: Generalise the MCP forbidden pattern**

In `FORBIDDEN_PATTERNS`, replace this entry:

```python
    "Claude MCP token": re.compile(r"\bmcp__plugin_profile-claude\b"),
```

with:

```python
    "MCP tool token": re.compile(r"mcp__\w+"),
```

Then in `_RULE_FIX`, replace the `"Claude MCP token"` key with:

```python
    "MCP tool token": (
        'remove the harness-native "mcp__"-prefixed tool token; shared files '
        'use the "MCP: <capability>" form from knowledge/harness-concepts.md'
    ),
```

- [ ] **Step 3: Add the model-allowlist loader and scan**

After the `should_skip` function, add:

```python
def load_model_aliases(plugin_root: Path) -> set[str]:
    """Load the allowed model tier aliases from the projection policy."""
    policy = plugin_root / "knowledge" / "agent-tool-projection-policy.md"
    fm = re.match(r"^---\n(.*?)\n---", policy.read_text(encoding="utf-8"), re.DOTALL)
    if not fm:
        return set()
    data = yaml.safe_load(fm.group(1))
    return set(data.get("shared_model_aliases", []))


def scan_models(plugin_root: Path) -> list[Finding]:
    """Fail any agents/*.md whose model: value is not a canonical tier alias."""
    findings: list[Finding] = []
    aliases = load_model_aliases(plugin_root)
    agents_dir = plugin_root / "agents"
    if not aliases or not agents_dir.exists():
        return findings
    for path in sorted(agents_dir.glob("*.md")):
        relative_path = path.relative_to(plugin_root).as_posix()
        match = re.search(r"^model:\s*(.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
        if not match:
            continue
        value = match.group(1).split("#", 1)[0].strip()
        if value not in aliases:
            findings.append(Finding(relative_path, "Non-canonical model", value))
    return findings
```

- [ ] **Step 4: Wire the model scan into `scan_paths` and add its fix text**

At the end of `scan_paths`, change the final `return findings` to:

```python
    findings.extend(scan_models(plugin_root))
    return findings
```

And add to `_RULE_FIX`:

```python
    "Non-canonical model": (
        "set the agent's model: to a canonical tier alias "
        "(haiku, sonnet, opus) listed in shared_model_aliases in "
        "knowledge/agent-tool-projection-policy.md"
    ),
```

- [ ] **Step 5: Confirm the validator still passes on the clean tree**

Run: `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`
Expected: `PASS: no harness-specific leakage in shared authored surface`. (Task 4 removed all `claude-*` model IDs, so the model scan finds nothing.)

- [ ] **Step 6: Prove both new rules fail on injected violations (inject, assert, revert)**

```bash
# Model violation:
cp profile-al-dev-shared/agents/al-dev-developer.md /tmp/dev.bak
sed -i '' 's/^model: sonnet/model: claude-sonnet-4-6/' profile-al-dev-shared/agents/al-dev-developer.md
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared; echo "exit=$?"
cp /tmp/dev.bak profile-al-dev-shared/agents/al-dev-developer.md && rm /tmp/dev.bak

# Generic mcp__ violation in a non-allowlisted file:
printf '\nmcp__foo_bar__baz\n' >> profile-al-dev-shared/knowledge/workflow-routing.md
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared; echo "exit=$?"
git checkout profile-al-dev-shared/knowledge/workflow-routing.md
```

Expected: the model run prints a `Non-canonical model` finding with `exit=1`; the `mcp__` run prints an `MCP tool token` finding with `exit=1`. After both reverts:

Run: `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`
Expected: `PASS: no harness-specific leakage in shared authored surface`.

- [ ] **Step 7: Commit**

```bash
git add scripts/validate_harness_neutrality.py
git commit -m "feat(neutrality): scan generic mcp__ tokens and enforce model allowlist

Generalises the MCP forbidden pattern to any mcp__ token and adds an
agents/*.md model check sourced from shared_model_aliases in the
projection policy (single source, strips inline comments)."
```

---

## Task 9: C5 — Pre-commit gate

Add a checked-in hook that runs the two validators plus a projections-current check against a temp dir (no working-tree mutation), enable it, and document it.

**Files:**
- Create: `.githooks/pre-commit`
- Modify: `CLAUDE.md` (Development Commands section)

- [ ] **Step 1: Create the hook**

Create `.githooks/pre-commit`:

```bash
#!/usr/bin/env bash
# Harness-neutrality pre-commit gate. Blocks commits that break neutrality,
# lens-policy sync, or leave generated projections stale.
# Bypass (use sparingly): git commit --no-verify
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "pre-commit: validating harness neutrality..."
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared

echo "pre-commit: validating lens agents (incl. lens-policy sync)..."
python3 scripts/validate-lens-agents.py

echo "pre-commit: checking projections are current..."
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
python3 scripts/generate-agent-projections.py --output-root "$tmp" >/dev/null
if ! diff -r "$tmp" profile-al-dev-shared/generated/agents >/dev/null 2>&1; then
  echo "ERROR: generated projections are stale." >&2
  echo "  Run: python3 scripts/generate-agent-projections.py" >&2
  echo "  then stage profile-al-dev-shared/generated/ and commit again." >&2
  exit 1
fi

echo "pre-commit: all neutrality checks passed."
```

- [ ] **Step 2: Make the hook executable**

Run: `chmod +x .githooks/pre-commit && ls -l .githooks/pre-commit`
Expected: the listing shows the `x` permission bits (e.g. `-rwxr-xr-x`).

- [ ] **Step 3: Enable the hooks path**

Run: `git config core.hooksPath .githooks && git config core.hooksPath`
Expected: prints `.githooks`. (Note: `core.hooksPath` was previously the default `.git/hooks`; this repoints it. This is a local-config, one-time step — document it for other clones in Step 5.)

- [ ] **Step 4: Verify the hook runs and passes on the clean tree**

Run: `.githooks/pre-commit`
Expected: the three progress lines followed by `pre-commit: all neutrality checks passed.` (exit 0).

- [ ] **Step 5: Document the hook in CLAUDE.md**

In `CLAUDE.md`, under `## Development Commands` → `### Validation (All Harnesses)`, after the four existing validation commands, add:

```markdown
### Pre-commit Neutrality Gate

A checked-in hook at `.githooks/pre-commit` blocks any commit that fails
harness neutrality, lens-policy sync, or leaves generated projections stale.
Enable it once per clone:

\`\`\`bash
git config core.hooksPath .githooks
\`\`\`

The hook runs, in order:

- `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`
- `python3 scripts/validate-lens-agents.py`
- a projections-current check (regenerates to a temp dir and diffs against
  `profile-al-dev-shared/generated/`)

Bypass with `git commit --no-verify` only when intentionally committing a
work-in-progress; the hook is fast local feedback, not a security control.
```

(Replace the `\`\`\`` fences above with real triple-backtick fences when writing the file.)

- [ ] **Step 6: Prove the hook blocks a bad commit (inject, attempt, revert)**

```bash
cp profile-al-dev-shared/agents/al-dev-developer.md /tmp/dev.bak
sed -i '' 's/^model: sonnet/model: claude-sonnet-4-6/' profile-al-dev-shared/agents/al-dev-developer.md
git add profile-al-dev-shared/agents/al-dev-developer.md
git commit -m "TEST: should be blocked"; echo "exit=$?"
git restore --staged profile-al-dev-shared/agents/al-dev-developer.md
cp /tmp/dev.bak profile-al-dev-shared/agents/al-dev-developer.md && rm /tmp/dev.bak
```

Expected: the commit is rejected by the neutrality validator with a non-zero `exit=`; no commit is created (`git log --oneline -1` is unchanged from Task 8's commit).

- [ ] **Step 7: Commit the hook and docs**

```bash
git add .githooks/pre-commit CLAUDE.md
git commit -m "feat(hooks): add checked-in pre-commit neutrality gate

Runs neutrality + lens-policy sync + projections-current checks before
every commit. Enabled via 'git config core.hooksPath .githooks';
documented under CLAUDE.md Development Commands."
```

---

## Task 10: End-to-end verification

Run the spec's full verification matrix against the finished tree.

- [ ] **Step 1: Projections byte-identical (Verification #1)**

Run: `python3 scripts/generate-agent-projections.py && git diff --exit-code profile-al-dev-shared/generated/ && echo CLEAN`
Expected: `CLEAN`.

- [ ] **Step 2: Neutrality passes (Verification #2)**

Run: `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`
Expected: `PASS: no harness-specific leakage in shared authored surface`.

- [ ] **Step 3: Lens validator + sync test pass (Verification #3)**

Run: `python3 scripts/validate-lens-agents.py`
Expected: `PASS — 21 agents valid, 4 skills refactored.`

- [ ] **Step 4: No `claude-*` model IDs remain (Verification #5)**

Run: `grep -rE '^model:\s*claude-' profile-al-dev-shared/agents/*.md || echo CLEAN`
Expected: `CLEAN`.

- [ ] **Step 5: Confirm the commit count matches the plan**

Run: `git log --oneline -9`
Expected: 9 commits from Tasks 1–9, newest first:
1. feat(hooks): add checked-in pre-commit neutrality gate
2. feat(neutrality): scan generic mcp__ tokens and enforce model allowlist
3. test(lens): assert structure lens list matches projection policy
4. refactor(generator): load projection table from policy frontmatter
5. feat(policy): complete projection frontmatter as single source
6. fix(agents): downgrade 5 reviewer agents to haiku tier alias
7. fix(lens): tool-hygiene lens recognises shared MCP: <capability> form
8. fix(lens): structure lens uses shared-source tool vocabulary
9. chore(projections): regenerate stale projections to match shared source

- [ ] **Step 6: Forbidden-pattern scan on the changed files**

Run: `git diff master~9 --name-only | xargs grep -nE '\[20[0-9]{2}-[0-9]{2}-[0-9]{2}\]|YYYY-MM-DD|TODO|TBD' 2>/dev/null || echo CLEAN`
Expected: `CLEAN`. (Only the files this plan created/edited need to be placeholder-free. If a match surfaces inside CLAUDE.md's existing convention prose rather than in a new placeholder, confirm by file before treating it as a failure.)

---

## Notes for the executor

- **Negative tests must be reverted.** Tasks 7, 8, and 9 each inject a violation to prove a check fails, then restore the file. Verify the restore with the trailing `PASS`/clean run before committing — never commit with an injected violation present.
- **`sed -i ''` is the macOS form.** On the darwin platform (per environment) `sed -i ''` is correct; do not drop the empty-string argument.
- **The byte-identical gate is the safety net for Task 6.** If Step 7 of Task 6 shows any `generated/` diff, the policy frontmatter (Task 5) does not match the generator's prior output — reconcile the differing codex/MCP string before deleting `default_projection_policy()`.
