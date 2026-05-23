# Shared Profile Harness-Agnostic Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the authored `profile-al-dev-shared` surface genuinely harness agnostic for Claude Code, Codex, and Copilot CLI while preserving explicit harness-mapping and generated projection artifacts where they belong.

**Architecture:** Treat the shared plugin as two layers. Layer 1 is the authored shared surface (`skills/`, `agents/`, most `knowledge/`, `markdown/`) and should use canonical shared vocabulary only. Layer 2 is the intentional harness-aware boundary (`knowledge/harness-concepts.md`, `knowledge/agent-tool-projection-policy.md`, `generated/agents/**`, and repo-local harness docs), which may mention Claude/Copilot/Codex by name because its job is to explain or generate projections.

**Tech Stack:** Markdown, Python 3.13, Bash, ripgrep, existing repo validators

---

## Current State Summary

- Shared agents are already mostly aligned with the abstraction model. For example, [profile-al-dev-shared/agents/al-dev-developer.md](/Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-developer.md:1) uses shared capabilities (`Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`) instead of harness-native tool names.
- Harness mapping exists and Codex is already present in the projection policy and generated outputs. See [profile-al-dev-shared/knowledge/agent-tool-projection-policy.md](/Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/agent-tool-projection-policy.md:1) and [profile-al-dev-shared/generated/agents/README.md](/Users/russelllaing/al-dev-shared/profile-al-dev-shared/generated/agents/README.md:1).
- The remaining problem is not projections. It is leakage inside authored shared docs and skill content that still instructs users or agents in Claude-specific or Copilot-specific terms.
- Known authored leaks currently include:
  - `profile-al-dev-shared/skills/al-dev-handoff/SKILL.md`
  - `profile-al-dev-shared/knowledge/review-panel-pattern.md`
  - `profile-al-dev-shared/knowledge/commit-conventions.md`
  - `profile-al-dev-shared/knowledge/script-engineer-conventions.md`
  - `profile-al-dev-shared/knowledge/session-analysis-report-format.md`
  - `profile-al-dev-shared/knowledge/verification-and-planning.md`
- Some harness-named files are correct by design and must not be “cleaned” into false neutrality:
  - `profile-al-dev-shared/knowledge/harness-concepts.md`
  - `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`
  - `profile-al-dev-shared/generated/agents/**`

## Recommendations

1. Define an explicit shared-surface neutrality rule and enforce it with a dedicated validator instead of relying on ad-hoc grep or memory.
2. Remove harness-branded instructions from authored shared skills and knowledge files unless the file’s purpose is specifically projection or cross-harness mapping.
3. Promote Codex to a first-class participant in shared mapping/reference docs wherever the repo still compares only Claude Code and Copilot CLI.
4. Keep generated harness-native artifacts derived-only. The source of truth remains shared authored files plus the projection policy.
5. Add the new validator to maintainer workflow so regressions are caught before new shared content lands.

## File Structure

- Create: `scripts/validate_harness_neutrality.py`
- Create: `scripts/tests/test_validate_harness_neutrality.py`
- Modify: `profile-al-dev-shared/skills/al-dev-handoff/SKILL.md`
- Modify: `profile-al-dev-shared/knowledge/review-panel-pattern.md`
- Modify: `profile-al-dev-shared/knowledge/commit-conventions.md`
- Modify: `profile-al-dev-shared/knowledge/script-engineer-conventions.md`
- Modify: `profile-al-dev-shared/knowledge/session-analysis-report-format.md`
- Modify: `profile-al-dev-shared/knowledge/verification-and-planning.md`
- Modify: `profile-al-dev-shared/knowledge/harness-concepts.md`
- Modify: `.github/copilot-instructions.md`
- Modify: `AGENTS.md`

---

### Task 1: Add a Harness-Neutrality Validator

**Files:**
- Create: `scripts/validate_harness_neutrality.py`
- Test: `scripts/tests/test_validate_harness_neutrality.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from scripts.validate_harness_neutrality import scan_paths


def test_flags_harness_specific_tokens_in_shared_docs(tmp_path: Path) -> None:
    plugin_root = tmp_path / "profile-al-dev-shared"
    knowledge = plugin_root / "knowledge"
    skills = plugin_root / "skills" / "demo"
    generated = plugin_root / "generated" / "agents" / "codex"

    knowledge.mkdir(parents=True)
    skills.mkdir(parents=True)
    generated.mkdir(parents=True)

    (skills / "SKILL.md").write_text("Open Claude Code in: /tmp\\n", encoding="utf-8")
    (knowledge / "harness-concepts.md").write_text(
        "AskUserQuestion | ask_user | request_user_input\\n",
        encoding="utf-8",
    )
    (generated / "demo.toml").write_text("model = 'gpt-5'\\n", encoding="utf-8")

    findings = scan_paths(plugin_root)

    assert any(item.path.endswith("skills/demo/SKILL.md") for item in findings)
    assert not any(item.path.endswith("knowledge/harness-concepts.md") for item in findings)
    assert not any(item.path.endswith("generated/agents/codex/demo.toml") for item in findings)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3.13 -m pytest scripts/tests/test_validate_harness_neutrality.py -q`
Expected: FAIL with `ModuleNotFoundError` or import failure because `scripts/validate_harness_neutrality.py` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys

SCAN_DIRS = ("skills", "agents", "knowledge", "markdown", "bc-code-intel-knowledge")
ALLOWLIST = {
    "knowledge/harness-concepts.md",
    "knowledge/agent-tool-projection-policy.md",
}
FORBIDDEN_PATTERNS = {
    "Open Claude Code": re.compile(r"\bOpen Claude Code\b"),
    "Restart Claude Code": re.compile(r"\bRestart Claude Code\b"),
    "Copilot session wording": re.compile(r"\bstart a new Copilot CLI session\b"),
    "Claude tool token": re.compile(r"\bAskUserQuestion\b"),
    "Copilot tool token": re.compile(r"\bask_user\b"),
    "Claude dispatch token": re.compile(r"\bsubagent_type\b"),
    "Copilot dispatch token": re.compile(r'\bagent_type:\s*"explore"\b'),
    "Claude MCP token": re.compile(r"\bmcp__plugin_profile-claude\b"),
    "Claude settings path": re.compile(r"~\/\.claude\b"),
    "Copilot settings path": re.compile(r"~\/\.copilot\b"),
}


@dataclass(frozen=True)
class Finding:
    path: str
    rule: str
    excerpt: str


def iter_markdown_files(plugin_root: Path):
    for directory in SCAN_DIRS:
        base = plugin_root / directory
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".yml"}:
                yield path


def scan_paths(plugin_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_markdown_files(plugin_root):
        rel = path.relative_to(plugin_root).as_posix()
        if rel in ALLOWLIST or rel.startswith("generated/") or rel.startswith("archived/"):
            continue
        text = path.read_text(encoding="utf-8")
        for rule, pattern in FORBIDDEN_PATTERNS.items():
            match = pattern.search(text)
            if match:
                findings.append(Finding(rel, rule, match.group(0)))
    return findings


def main() -> int:
    plugin_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("profile-al-dev-shared")
    findings = scan_paths(plugin_root)
    if not findings:
        print("PASS: no harness-specific leakage in shared authored surface")
        return 0
    for finding in findings:
        print(f"{finding.path}: {finding.rule}: {finding.excerpt}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3.13 -m pytest scripts/tests/test_validate_harness_neutrality.py -q`
Expected: PASS with `1 passed`

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  scripts/validate_harness_neutrality.py \
  scripts/tests/test_validate_harness_neutrality.py
git -C /Users/russelllaing/al-dev-shared commit -m "✨ feat(validation): add shared-surface harness neutrality validator"
```

---

### Task 2: Remove Harness Leakage from Authored Shared Content

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-handoff/SKILL.md`
- Modify: `profile-al-dev-shared/knowledge/review-panel-pattern.md`
- Modify: `profile-al-dev-shared/knowledge/commit-conventions.md`
- Modify: `profile-al-dev-shared/knowledge/script-engineer-conventions.md`

- [ ] **Step 1: Run the validator against the repo to capture the failing baseline**

Run: `python3.13 scripts/validate_harness_neutrality.py profile-al-dev-shared`
Expected: FAIL listing at least:
- `skills/al-dev-handoff/SKILL.md`
- `knowledge/review-panel-pattern.md`
- `knowledge/commit-conventions.md`
- `knowledge/script-engineer-conventions.md`

- [ ] **Step 2: Replace Claude-specific handoff wording with harness-neutral continuation wording**

```markdown
To continue in [target repo name]:
1. Open a new session rooted at: [target-repo-path]
2. Paste the prompt from .dev/[date]-al-dev-handoff-handoff-prompt.md
   (preview: cat .dev/[date]-al-dev-handoff-handoff-prompt.md)
```

- [ ] **Step 3: Replace Claude-specific agent invocation examples with canonical shared syntax**

```markdown
Dispatch agent: al-dev-shared:al-dev-security-reviewer
  description: "Security review of implemented code"
  prompt: "Review these AL files for security issues: [file list]. Check permissions, data exposure, auth gaps."

Dispatch agent: al-dev-shared:al-dev-expert-reviewer
  description: "AL patterns and BC best practices review"
  prompt: "Review these AL files for naming, patterns, BC conventions: [file list]. Check SetLoadFields, naming consistency, event patterns."

Dispatch agent: al-dev-shared:al-dev-performance-reviewer
  description: "Performance analysis of implemented code"
  prompt: "Review these AL files for query efficiency and performance: [file list]. Check N+1 patterns, SetLoadFields, loop scoping."
```

- [ ] **Step 4: Rewrite knowledge docs that currently describe Claude-specific behavior as generic harness behavior**

```markdown
Every project must declare the `project-type` field in its project instructions file. This field tells the active harness how to categorize the project and what workflows apply.
```

```markdown
Scripts often need to communicate results to parent processes (the active harness, CI/CD, Slack, etc.). Use structured protocol output instead of free-form logging.
```

```markdown
Parent process reads each line, parses JSON, and updates the UI:
```

- [ ] **Step 5: Re-run validator to verify these authored files are clean**

Run: `python3.13 scripts/validate_harness_neutrality.py profile-al-dev-shared`
Expected: either `PASS: no harness-specific leakage in shared authored surface` or remaining failures only in files scheduled for Task 3.

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-handoff/SKILL.md \
  profile-al-dev-shared/knowledge/review-panel-pattern.md \
  profile-al-dev-shared/knowledge/commit-conventions.md \
  profile-al-dev-shared/knowledge/script-engineer-conventions.md
git -C /Users/russelllaing/al-dev-shared commit -m "🧹 chore(knowledge): remove harness-branded wording from shared content"
```

---

### Task 3: Make Codex First-Class in Shared Mapping and Reporting Docs

**Files:**
- Modify: `profile-al-dev-shared/knowledge/harness-concepts.md`
- Modify: `profile-al-dev-shared/knowledge/session-analysis-report-format.md`
- Modify: `profile-al-dev-shared/knowledge/verification-and-planning.md`

- [ ] **Step 1: Write a failing test that asserts Codex appears in the intentionally harness-aware reference docs**

```python
from pathlib import Path


def test_codex_is_present_in_mapping_docs() -> None:
    harness_concepts = Path("profile-al-dev-shared/knowledge/harness-concepts.md").read_text(encoding="utf-8")
    report_format = Path("profile-al-dev-shared/knowledge/session-analysis-report-format.md").read_text(encoding="utf-8")
    verification = Path("profile-al-dev-shared/knowledge/verification-and-planning.md").read_text(encoding="utf-8")

    assert "Codex" in harness_concepts
    assert "Codex" in report_format
    assert "Codex" in verification
```

- [ ] **Step 2: Run test to verify it fails where Codex is still missing**

Run: `python3.13 -m pytest scripts/tests/test_validate_harness_neutrality.py -q`
Expected: FAIL because `session-analysis-report-format.md` and `verification-and-planning.md` do not yet mention Codex consistently.

- [ ] **Step 3: Update the mapping docs so Codex is represented explicitly**

```markdown
| Concept | Description | Claude Code | Copilot CLI | Codex |
|---|---|---|---|---|
| **USER_GATE** | A blocking user-confirmation point; never continue past this without a user response | `AskUserQuestion` tool | `ask_user` tool | `request_user_input` tool |
| **explore agent** | A fast parallel exploration agent | `subagent_type: Explore` | `agent_type: "explore"` in task tool | delegated subagent/tool-search workflow in the active Codex session |
```

```markdown
**Data source:** {e.g. "Claude Code JSONL transcript" | "Copilot CLI session_store (SQL)" | "Codex session transcript / tool trace"}
```

```markdown
| Need | Claude Code | Copilot CLI | Codex |
|---|---|---|---|
| User decision gate | USER_GATE | USER_GATE | USER_GATE |
```

- [ ] **Step 4: Re-run the doc-presence test and the neutrality validator**

Run: `python3.13 -m pytest scripts/tests/test_validate_harness_neutrality.py -q`
Expected: PASS

Run: `python3.13 scripts/validate_harness_neutrality.py profile-al-dev-shared`
Expected: PASS because the Codex/Claude/Copilot mentions live only in allowed harness-aware reference docs.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/knowledge/harness-concepts.md \
  profile-al-dev-shared/knowledge/session-analysis-report-format.md \
  profile-al-dev-shared/knowledge/verification-and-planning.md \
  scripts/tests/test_validate_harness_neutrality.py
git -C /Users/russelllaing/al-dev-shared commit -m "✨ feat(docs): add Codex to shared mapping and reporting references"
```

---

### Task 4: Wire the Neutrality Check into Maintainer Workflow

**Files:**
- Modify: `.github/copilot-instructions.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Add the validator command to maintainer instructions**

````markdown
### Validate Shared-Surface Harness Neutrality

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Checks:
- Shared authored files do not contain harness-branded instructions or tool tokens
- Harness-aware mapping docs are excluded by allowlist
- Generated projections are excluded because they are derived artifacts
````

- [ ] **Step 2: Add a short boundary rule to the repo-local maintainer guidance**

```markdown
`profile-al-dev-shared/` is split into:

- shared authored content that must remain harness agnostic
- intentional harness-mapping documentation
- generated harness-native projection artifacts

Before committing shared-content changes, run `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`.
```

- [ ] **Step 3: Run the validator and existing knowledge validator together**

Run: `python3.13 scripts/validate_harness_neutrality.py profile-al-dev-shared`
Expected: PASS

Run: `python3.13 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge`
Expected: PASS or only pre-existing unrelated advisories.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  .github/copilot-instructions.md \
  AGENTS.md
git -C /Users/russelllaing/al-dev-shared commit -m "📚 docs(maintainers): document harness neutrality validation"
```

---

## Test Plan

- Unit test the new validator with a temporary fixture tree that includes:
  - one shared file with forbidden Claude wording
  - one allowlisted mapping doc with intentional harness tokens
  - one generated artifact path that must be ignored
- Run the validator against the real repo before and after cleanup.
- Re-run `scripts/validate-knowledge-quality.py` after doc edits to catch formatting or structure regressions.
- Spot-check generated Codex, Claude, and Copilot projections only if shared agent metadata changes. This plan does not require projection regeneration unless agent source files are edited.

## Assumptions

- Scope is the authored `profile-al-dev-shared` surface plus minimal maintainer docs, not a full rewrite of repo-local harness docs such as `AGENTS.md` into a neutral format.
- `knowledge/harness-concepts.md`, `knowledge/agent-tool-projection-policy.md`, and `generated/agents/**` are allowed to mention harnesses explicitly because they define the projection boundary.
- The desired end state is not “never mention Claude/Copilot/Codex anywhere.” The desired end state is “shared authored operational content is neutral; mapping/projection content is explicit and isolated.”
- Validation should fail closed on new shared-content leaks, but should not block intentional cross-harness reference material.
