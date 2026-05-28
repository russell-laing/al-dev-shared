# Artifact-Contract Conformance Validator and Skill Scaffold Template

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a structural sensor (`validate_artifact_contracts.py`) that enforces the artifact-contract matrix, and a scaffold template for new skills that bakes in the contract structure by default.

**Architecture:** Two independent deliverables: (1) A standalone Python validator following the existing `validate_harness_neutrality.py` conventions — same `@dataclass` violations pattern, same `tmp_path` unittest fixtures, same `validate(repo_root)` entry point. (2) Three inert markdown template files at `templates/skill-template/` (repo root, not inside `profile-al-dev-shared/`). Both reference `artifact-contracts.md` as the single source of truth.

**Tech Stack:** Python 3, stdlib only (`pathlib`, `re`, `dataclasses`), existing `unittest` runner pattern (no pytest).

---

## File Map

| Path | Status | Responsibility |
|---|---|---|
| `scripts/validate_artifact_contracts.py` | New | Five-rule conformance validator entry point |
| `scripts/tests/test_validate_artifact_contracts.py` | New | Six unit tests, one per rule + happy path |
| `templates/skill-template/SKILL.md.tmpl` | New | Canonical skill structure with boilerplate pre-filled |
| `templates/skill-template/tests/scenarios.yaml.tmpl` | New | Canonical scenario file skeleton |
| `templates/skill-template/README.md` | New | Maintainer checklist for scaffolding a new skill |
| `profile-al-dev-shared/knowledge/artifact-contracts.md` | Modify | Add one-line cross-link to template |
| `CLAUDE.md` | Modify | Add validator to validation command list |
| `docs/harness-coverage-model.md` | Modify | Add new coverage row |

---

## Task 1: Write Failing Tests

TDD step one: write the test file before the implementation exists. Running it will fail with `ModuleNotFoundError` until Task 2 delivers the validator. The tests exercise each of the five conformance rules and the happy path.

**Files:**
- Create: `scripts/tests/test_validate_artifact_contracts.py`

- [ ] **Step 1: Write the test file**

```python
# scripts/tests/test_validate_artifact_contracts.py
from __future__ import annotations

import inspect
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_artifact_contracts import validate  # noqa: E402


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _make_contract(rows: list[dict]) -> str:
    """Build a minimal artifact-contracts.md with the given matrix rows."""
    header = (
        "# Artifact Contracts\n\n"
        "## Contract Matrix\n\n"
        "| Skill | Required inputs | Durable outputs | Resume read order |"
        " Handoff artifact | Success evidence |\n"
        "|------|---|---|---|---|---|\n"
    )
    body = header
    for row in rows:
        body += (
            f"| `{row['skill']}` |"
            f" {row.get('inputs', 'some input')} |"
            f" {row.get('outputs', 'some output')} |"
            f" {row.get('resume', 'resume state')} |"
            f" {row.get('handoff', 'handoff artifact')} |"
            f" {row.get('evidence', 'evidence text')} |\n"
        )
    return body


def _make_repo(tmp_path: Path, contract_content: str, skills: dict[str, str]) -> Path:
    """Create a minimal repo layout for testing."""
    knowledge = tmp_path / "profile-al-dev-shared" / "knowledge"
    knowledge.mkdir(parents=True)
    (knowledge / "artifact-contracts.md").write_text(contract_content, encoding="utf-8")

    skills_root = tmp_path / "profile-al-dev-shared" / "skills"
    for name, body in skills.items():
        skill_dir = skills_root / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")

    return tmp_path


# A skill body that satisfies both rule 2 (cross-reference) and rule 3 (final-gate).
_GOOD_BODY = (
    "## Artifact Contract\n\n"
    "Use `knowledge/artifact-contracts.md` as the source of truth.\n\n"
    "Do not claim complete until the success evidence named in "
    "`knowledge/artifact-contracts.md` has been read in the current run.\n"
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_happy_path(tmp_path: Path) -> None:
    """Fixture matrix + matching skill stubs → no violations."""
    contract = _make_contract([{"skill": "my-skill"}])
    repo = _make_repo(tmp_path, contract, {"my-skill": _GOOD_BODY})
    violations, count = validate(repo)
    assert violations == [], f"Expected no violations, got: {violations}"
    assert count == 1


def test_missing_cross_reference(tmp_path: Path) -> None:
    """Skill body lacks knowledge/artifact-contracts.md reference → rule 2 violation."""
    contract = _make_contract([{"skill": "my-skill"}])
    # Has the final-gate phrase but no reference to the contract file path.
    body = (
        "Do not claim complete until the success evidence named in "
        "the contract has been read.\n"
    )
    repo = _make_repo(tmp_path, contract, {"my-skill": body})
    violations, _ = validate(repo)
    assert any(v.rule == "artifact-contract-cross-reference" for v in violations), (
        f"Expected rule 2 violation. Got: {[v.rule for v in violations]}"
    )


def test_missing_final_gate(tmp_path: Path) -> None:
    """Skill body lacks canonical final-gate phrase → rule 3 violation."""
    contract = _make_contract([{"skill": "my-skill"}])
    # Has the cross-reference but no "success evidence named in" phrase.
    body = "Use `knowledge/artifact-contracts.md` as the source of truth.\n"
    repo = _make_repo(tmp_path, contract, {"my-skill": body})
    violations, _ = validate(repo)
    assert any(v.rule == "artifact-contract-final-gate" for v in violations), (
        f"Expected rule 3 violation. Got: {[v.rule for v in violations]}"
    )


def test_path_mismatch(tmp_path: Path) -> None:
    """Success evidence column names a .dev/ path the skill body never mentions → rule 4 violation."""
    contract = _make_contract([{
        "skill": "my-skill",
        "evidence": "`.dev/my-skill-report.md` must exist and be read",
    }])
    # Good body for rules 2+3 but does NOT mention .dev/my-skill-report.md.
    body = (
        "Use `knowledge/artifact-contracts.md`.\n\n"
        "Do not claim complete until the success evidence named in "
        "`knowledge/artifact-contracts.md` has been read.\n"
    )
    repo = _make_repo(tmp_path, contract, {"my-skill": body})
    violations, _ = validate(repo)
    assert any(v.rule == "success-evidence-alignment" for v in violations), (
        f"Expected rule 4 violation. Got: {[v.rule for v in violations]}"
    )


def test_orphan_reference(tmp_path: Path) -> None:
    """Skill body references contract doc but has no matrix row → rule 5 violation."""
    # Matrix only has 'good-skill'; 'orphan-skill' references the contract but is absent.
    contract = _make_contract([{"skill": "good-skill"}])
    orphan_body = "See `knowledge/artifact-contracts.md` for details.\n"
    repo = _make_repo(tmp_path, contract, {
        "good-skill": _GOOD_BODY,
        "orphan-skill": orphan_body,
    })
    violations, _ = validate(repo)
    assert any(v.rule == "orphan-contract-reference" for v in violations), (
        f"Expected rule 5 violation. Got: {[v.rule for v in violations]}"
    )


def test_unresolved_row(tmp_path: Path) -> None:
    """Matrix row names a skill whose SKILL.md does not exist → rule 1 violation."""
    contract = _make_contract([{"skill": "missing-skill"}])
    repo = _make_repo(tmp_path, contract, {})  # no SKILL.md files created
    violations, _ = validate(repo)
    assert any(v.rule == "row-resolution" for v in violations), (
        f"Expected rule 1 violation. Got: {[v.rule for v in violations]}"
    )


# ---------------------------------------------------------------------------
# Runner (unittest-compatible, no pytest required)
# ---------------------------------------------------------------------------

def _run(func):
    sig = inspect.signature(func)
    if not sig.parameters:
        func()
    elif list(sig.parameters) == ["tmp_path"]:
        with tempfile.TemporaryDirectory() as td:
            func(Path(td))
    else:
        raise TypeError(f"Unsupported signature: {func.__name__}{sig}")


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Confirm tests fail with ModuleNotFoundError**

```bash
python3 scripts/tests/test_validate_artifact_contracts.py 2>&1 | head -5
```

Expected: `ModuleNotFoundError: No module named 'scripts.validate_artifact_contracts'`

- [ ] **Step 3: Commit test skeleton**

```bash
git add scripts/tests/test_validate_artifact_contracts.py
git commit -m "test(validator): add six failing conformance tests for artifact-contract validator"
```

---

## Task 2: Write Validator Implementation

Implement `scripts/validate_artifact_contracts.py` with all five conformance rules. After this task all six tests pass.

**Files:**
- Create: `scripts/validate_artifact_contracts.py`

- [ ] **Step 1: Write the validator**

```python
#!/usr/bin/env python3
# scripts/validate_artifact_contracts.py
"""Validate that skills listed in artifact-contracts.md honour the contract structure."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CROSS_REF_TOKEN = "knowledge/artifact-contracts.md"
_FINAL_GATE_PHRASE = "success evidence named in"


@dataclass(frozen=True)
class Violation:
    path: str
    rule: str
    issue: str
    fix: str


# ---------------------------------------------------------------------------
# Table parsing
# ---------------------------------------------------------------------------

def _table_cells(line: str) -> list[str]:
    """Return stripped cell values from a markdown pipe-table line."""
    parts = line.strip().split("|")
    return [c.strip() for c in parts[1:-1]]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.match(r"^:?-+:?$", c) for c in cells)


def parse_contract_matrix(text: str) -> list[dict[str, str]]:
    """Parse the Contract Matrix table rows into dicts keyed by column header."""
    rows: list[dict[str, str]] = []
    headers: list[str] | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if headers is not None:
                break  # blank or prose line ends the table
            continue
        cells = _table_cells(stripped)
        if _is_separator(cells):
            continue
        if headers is None:
            headers = cells
        elif len(cells) >= len(headers):
            rows.append(dict(zip(headers, cells)))

    return rows


# ---------------------------------------------------------------------------
# Skill-name extraction and path-token extraction
# ---------------------------------------------------------------------------

def extract_skill_name(raw: str) -> str:
    """Extract skill name from a cell value like '`al-dev-plan`'."""
    m = re.search(r"`([^`]+)`", raw)
    return m.group(1) if m else raw.strip()


def extract_path_tokens(text: str) -> list[str]:
    """Return .dev/ path-like tokens found in text (used for rule 4)."""
    return re.findall(r"\.dev/[a-zA-Z0-9*._-]+", text)


# ---------------------------------------------------------------------------
# Per-row conformance checks (rules 1–4)
# ---------------------------------------------------------------------------

def check_row(
    row: dict[str, str],
    skill_name: str,
    skills_root: Path,
) -> list[Violation]:
    rel_skill = f"profile-al-dev-shared/skills/{skill_name}/SKILL.md"
    rel_contract = "profile-al-dev-shared/knowledge/artifact-contracts.md"
    skill_path = skills_root / skill_name / "SKILL.md"

    # Rule 1: row resolution
    if not skill_path.is_file():
        return [Violation(
            rel_contract,
            "row-resolution",
            f"row '{skill_name}' does not resolve to an existing SKILL.md at {rel_skill}",
            "create the SKILL.md or remove the row from the matrix",
        )]

    try:
        body = skill_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [Violation(
            rel_skill,
            "row-resolution",
            f"SKILL.md is unreadable: {exc}",
            "fix file permissions or encoding",
        )]

    violations: list[Violation] = []

    # Rule 2: cross-reference present
    if _CROSS_REF_TOKEN not in body:
        violations.append(Violation(
            rel_skill,
            "artifact-contract-cross-reference",
            f"contract row exists but body has no reference to '{_CROSS_REF_TOKEN}'",
            "add the standard cross-reference block under the intent-preflight section",
        ))

    # Rule 3: final-gate rule present
    if _FINAL_GATE_PHRASE not in body:
        violations.append(Violation(
            rel_skill,
            "artifact-contract-final-gate",
            f"body lacks the canonical final-gate phrase '{_FINAL_GATE_PHRASE}'",
            f"add final-gate wording containing '{_FINAL_GATE_PHRASE}' before any completion claim",
        ))

    # Rule 4: success-evidence path alignment
    evidence = row.get("Success evidence", "")
    tokens = extract_path_tokens(evidence)
    if tokens and not any(tok in body for tok in tokens):
        violations.append(Violation(
            rel_contract,
            "success-evidence-alignment",
            f"row '{skill_name}' names success-evidence path(s) {tokens} "
            f"but the skill body never references them",
            "update the matrix row or the skill body so the path appears in both",
        ))

    return violations


# ---------------------------------------------------------------------------
# Orphan check (rule 5)
# ---------------------------------------------------------------------------

def check_orphans(
    skills_root: Path,
    matrix_skill_names: set[str],
) -> list[Violation]:
    violations: list[Violation] = []
    if not skills_root.exists():
        return violations

    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        try:
            body = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue
        if _CROSS_REF_TOKEN not in body:
            continue
        skill_name = skill_md.parent.name
        if skill_name not in matrix_skill_names:
            rel = f"profile-al-dev-shared/skills/{skill_name}/SKILL.md"
            violations.append(Violation(
                rel,
                "orphan-contract-reference",
                f"skill '{skill_name}' references '{_CROSS_REF_TOKEN}' "
                f"but has no row in the Contract Matrix",
                f"add a row for '{skill_name}' to artifact-contracts.md",
            ))
    return violations


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def validate(
    repo_root: Path | None = None,
) -> tuple[list[Violation], int]:
    """
    Run all five conformance rules against the live tree.

    Returns (violations, skill_count) where skill_count is the number of
    rows found in the contract matrix (zero if the matrix could not be parsed).
    """
    root = repo_root if repo_root is not None else _REPO_ROOT
    contract_path = root / "profile-al-dev-shared" / "knowledge" / "artifact-contracts.md"
    skills_root = root / "profile-al-dev-shared" / "skills"

    if not contract_path.exists():
        return [Violation(
            str(contract_path),
            "contract-missing",
            "artifact-contracts.md not found",
            "create the contract document",
        )], 0

    try:
        text = contract_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [Violation(
            "profile-al-dev-shared/knowledge/artifact-contracts.md",
            "contract-unreadable",
            str(exc),
            "fix file permissions or encoding",
        )], 0

    rows = parse_contract_matrix(text)

    if not rows:
        return [Violation(
            "profile-al-dev-shared/knowledge/artifact-contracts.md",
            "empty-contract",
            "the contract document exists but has no rows in its Contract Matrix table",
            "add rows to the Contract Matrix table in artifact-contracts.md",
        )], 0

    violations: list[Violation] = []
    matrix_skill_names: set[str] = set()

    for row in rows:
        skill_name = extract_skill_name(row.get("Skill", ""))
        if not skill_name:
            continue
        matrix_skill_names.add(skill_name)
        violations.extend(check_row(row, skill_name, skills_root))

    violations.extend(check_orphans(skills_root, matrix_skill_names))
    return violations, len(matrix_skill_names)


def _format_violation(v: Violation) -> str:
    return (
        f"{v.path}\n"
        f"  rule: {v.rule}\n"
        f"  issue: {v.issue}\n"
        f"  fix: {v.fix}"
    )


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    repo_root = Path(args[0]) if args else None
    violations, skill_count = validate(repo_root)

    if not violations:
        print(f"OK: {skill_count} skills conform to artifact-contracts.md")
        return 0

    blocks = "\n\n".join(_format_violation(v) for v in violations)
    print(blocks)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run the tests**

```bash
python3 scripts/tests/test_validate_artifact_contracts.py -v
```

Expected output (all six lines):
```
test_happy_path ... ok
test_missing_cross_reference ... ok
test_missing_final_gate ... ok
test_path_mismatch ... ok
test_orphan_reference ... ok
test_unresolved_row ... ok
----------------------------------------------------------------------
Ran 6 tests in 0.XXXs

OK
```

If any test fails, read the assertion message and fix the corresponding rule in the validator before continuing.

- [ ] **Step 3: Commit the implementation**

```bash
git add scripts/validate_artifact_contracts.py
git commit -m "feat(validator): add artifact-contract conformance validator (5 rules)"
```

---

## Task 3: Live Tree Validation Run

Run the validator against the actual repository to confirm exit 0 and triage any real drift before documentation or templates land.

**Files:**
- No file changes in this task (unless drift is found — see step 3)

- [ ] **Step 1: Run against the live tree**

```bash
python3 scripts/validate_artifact_contracts.py
```

Expected: `OK: 6 skills conform to artifact-contracts.md`

- [ ] **Step 2: If exit 0 — done**

No further action. Proceed to Task 4.

- [ ] **Step 3: If exit non-zero — triage each violation**

For each violation block printed:
- `row-resolution`: the skill name in the matrix does not match a directory under `profile-al-dev-shared/skills/`. Fix: correct the name in `artifact-contracts.md`.
- `artifact-contract-cross-reference`: the SKILL.md body does not contain `knowledge/artifact-contracts.md`. Fix: add the standard cross-reference block to that SKILL.md.
- `artifact-contract-final-gate`: the SKILL.md body does not contain `success evidence named in`. Fix: add the final-gate sentence to that SKILL.md.
- `success-evidence-alignment`: the Success evidence column in the matrix names a `.dev/` path that does not appear in the SKILL.md. Fix: update the matrix row or the skill body.
- `orphan-contract-reference`: a SKILL.md references the contract doc but has no matrix row. Fix: add a row to `artifact-contracts.md`.

After fixing, re-run until exit 0.

- [ ] **Step 4: Commit any drift fixes**

```bash
git add profile-al-dev-shared/knowledge/artifact-contracts.md
# add any skill files that were changed
git commit -m "fix(contracts): resolve drift surfaced by artifact-contract validator"
```

---

## Task 4: Documentation Updates

Add the new validator command to `CLAUDE.md` and add a new coverage row to `docs/harness-coverage-model.md`.

**Files:**
- Modify: `CLAUDE.md` (repo root)
- Modify: `docs/harness-coverage-model.md`

- [ ] **Step 1: Open CLAUDE.md and locate the validation block**

Find the section `### Validation (All Harnesses)` in `CLAUDE.md`. It currently lists three validators in a bash block. Add a fourth:

```
# Validate that skills honour the artifact-contract matrix
python3 scripts/validate_artifact_contracts.py
```

Insert it as the last line inside the existing `\`\`\`bash` block, after the `validate-knowledge-quality.py` line.

The final block should look like:
```bash
# Validate that shared source has no harness-specific leakage
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared

# Validate agent structure (frontmatter, tools, model assignment)
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents

# Validate knowledge file quality
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge

# Validate that skills honour the artifact-contract matrix
python3 scripts/validate_artifact_contracts.py
```

- [ ] **Step 2: Open docs/harness-coverage-model.md and locate the Coverage Table**

Find the `## Coverage Table` section. The table has columns: `Behavior | Category | Guide | Sensor | Enforcement strength | Owner | Gap`.

Add this row at the end of the table (after the last existing `|` row, before the `---` divider):

```
| Skills honour the artifact-contract matrix | Workflow behavior | `profile-al-dev-shared/knowledge/artifact-contracts.md` | `scripts/validate_artifact_contracts.py`; `scripts/tests/test_validate_artifact_contracts.py` | `guide + blocking enforcement` | Shared profile plus repo-local validation script | Promote new contract rows by adding the SKILL.md cross-reference and final-gate wording together — the validator will catch omissions on the next run. |
```

- [ ] **Step 3: Verify forbidden patterns absent in both changed files**

```bash
grep -n "YYYY-MM-DD\|TODO\|TBD\|\[date\]" CLAUDE.md docs/harness-coverage-model.md
```

Expected: no output.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md docs/harness-coverage-model.md
git commit -m "docs(validator): add artifact-contract validator to CLAUDE.md and coverage model"
```

---

## Task 5: Create Template Files

Create the three files under `templates/skill-template/`. These are inert markdown — no logic, no projection involvement.

**Files:**
- Create: `templates/skill-template/SKILL.md.tmpl`
- Create: `templates/skill-template/tests/scenarios.yaml.tmpl`
- Create: `templates/skill-template/README.md`

- [ ] **Step 1: Create the templates directory and SKILL.md.tmpl**

```bash
mkdir -p templates/skill-template/tests
```

Write `templates/skill-template/SKILL.md.tmpl` with this exact content:

```markdown
---
name: {{skill-name}}
description: >-
  {{one-paragraph trigger description — used for auto-invocation routing.
  State what user request phrases trigger this skill.}}
argument-hint: "{{optional args | leave empty if none}}"
---

## Intent Preflight

Before any mutating action, apply `knowledge/intent-preflight.md`.

Default intent for this skill is `{{REVIEW | EDIT | COMMIT}}`.

## Artifact Contract

This skill is governed by `knowledge/artifact-contracts.md`.

Do not claim the work is complete, validated, clean, or ready for the next
workflow step until the success evidence named in `knowledge/artifact-contracts.md`
for this skill has been produced and read in the current run.

## Inputs

{{Describe the required inputs — files, user request, prior skill outputs.}}

## Phases

{{Describe the phases or steps the skill executes.}}

## Outputs

{{Describe the durable output files written to .dev/ and their naming pattern.}}

## Resume Behaviour

Follow `knowledge/workflow-resilience.md`. Read `.dev/progress.md` first;
reconcile against the resume read-order declared in `knowledge/artifact-contracts.md`.
```

- [ ] **Step 2: Write tests/scenarios.yaml.tmpl**

Write `templates/skill-template/tests/scenarios.yaml.tmpl` with this exact content:

```yaml
# scenarios for {{skill-name}} — see knowledge/skill-test-format.md
scenarios:
  - name: {{skill-name}}-trigger-canonical
    request: "{{phrasing that should trigger this skill}}"
    expected: trigger
    rationale: "{{why this phrasing must trigger}}"

  - name: {{skill-name}}-no-trigger-review-only
    request: "{{phrasing that resembles this skill but must not trigger — typically a review/audit framing}}"
    expected: no-trigger
    rationale: "{{why this phrasing must NOT trigger}}"
```

- [ ] **Step 3: Write README.md**

Write `templates/skill-template/README.md` with this exact content:

```markdown
# Skill scaffold template

To add a new shared skill:

1. Copy this directory to `profile-al-dev-shared/skills/<your-skill-name>/`.
2. Rename `SKILL.md.tmpl` → `SKILL.md` and `tests/scenarios.yaml.tmpl` → `tests/scenarios.yaml`.
3. Replace every `{{placeholder}}` value.
4. Add a row for the new skill to `profile-al-dev-shared/knowledge/artifact-contracts.md`
   with the declared inputs, outputs, resume read-order, handoff artefact, and success
   evidence.
5. If user-invocable, register the skill in `.claude-plugin/marketplace.json`.
6. Run the validators:

   ```bash
   python3 scripts/validate_artifact_contracts.py
   python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
   python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge
   ```

7. If the new skill spawns or relies on a new agent, see `profile-al-dev-shared/agents/`
   and regenerate projections:

   ```bash
   python3 scripts/generate-agent-projections.py
   ```
```

- [ ] **Step 4: Verify file count**

```bash
find templates/ -type f | sort
```

Expected:
```
templates/skill-template/README.md
templates/skill-template/SKILL.md.tmpl
templates/skill-template/tests/scenarios.yaml.tmpl
```

- [ ] **Step 5: Verify no harness-specific tokens in templates**

```bash
grep -rn "AskUserQuestion\|subagent_type\|ask_user\|~/\.claude\|~/\.copilot" templates/
```

Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add templates/
git commit -m "feat(template): add skill scaffold template with contract structure pre-filled"
```

---

## Task 6: Cross-Link and Smoke Test

Add the one-line cross-link to `artifact-contracts.md`, then scaffold a throwaway skill to confirm the template passes the validator without structural changes.

**Files:**
- Modify: `profile-al-dev-shared/knowledge/artifact-contracts.md`

- [ ] **Step 1: Add the cross-link to artifact-contracts.md**

In `profile-al-dev-shared/knowledge/artifact-contracts.md`, find the `## Rules` section at the top. Insert the following line immediately after the opening paragraph (after `Use this document when:`… block, before `## Rules`):

```markdown
> New skills should be scaffolded from `templates/skill-template/` so this contract is honoured by default.
```

Alternatively, if a better natural placement exists (e.g., between `## Rules` and `## Contract Matrix`), place it there. The requirement is: visible near the top of the document, before the matrix table.

- [ ] **Step 2: Verify the cross-link is present**

```bash
grep -n "templates/skill-template" profile-al-dev-shared/knowledge/artifact-contracts.md
```

Expected: one matching line.

- [ ] **Step 3: Smoke-test the template**

Scaffold a temporary skill and validate it:

```bash
cp -r templates/skill-template /tmp/smoke-skill-test
```

Create a minimal SKILL.md at `/tmp/smoke-skill-test/SKILL.md` by copying and filling the template. The filled content must include both:
- the substring `knowledge/artifact-contracts.md` (satisfies rule 2)
- the substring `success evidence named in` (satisfies rule 3)

Then run the validator pointing at a throwaway repo layout:

```bash
python3 - <<'EOF'
import sys, tempfile
from pathlib import Path
sys.path.insert(0, ".")
from scripts.validate_artifact_contracts import validate, _CROSS_REF_TOKEN, _FINAL_GATE_PHRASE

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    knowledge = root / "profile-al-dev-shared" / "knowledge"
    knowledge.mkdir(parents=True)
    skill_dir = root / "profile-al-dev-shared" / "skills" / "smoke-skill"
    skill_dir.mkdir(parents=True)

    # Write a minimal contract referencing the smoke skill
    (knowledge / "artifact-contracts.md").write_text(
        "# Artifact Contracts\n\n## Contract Matrix\n\n"
        "| Skill | Required inputs | Durable outputs | Resume read order | Handoff artifact | Success evidence |\n"
        "|------|---|---|---|---|---|\n"
        "| `smoke-skill` | user request | `.dev/smoke.md` | `.dev/progress.md` | `.dev/smoke.md` | current run evidence |\n",
        encoding="utf-8",
    )
    # Write a skill body scaffolded from the template (placeholders filled)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: smoke-skill\ndescription: smoke test\n---\n\n"
        f"Use `{_CROSS_REF_TOKEN}` as the source of truth.\n\n"
        f"Do not claim complete until the {_FINAL_GATE_PHRASE} "
        f"`{_CROSS_REF_TOKEN}` has been read.\n",
        encoding="utf-8",
    )
    violations, count = validate(root)
    if violations:
        for v in violations:
            print(f"FAIL: {v.path} / {v.rule}: {v.issue}")
        sys.exit(1)
    print(f"PASS: smoke-skill conforms ({count} skills validated)")
EOF
```

Expected: `PASS: smoke-skill conforms (1 skills validated)`

- [ ] **Step 4: Run neutrality validator to confirm templates don't affect shared surface**

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected: `PASS: no harness-specific leakage in shared authored surface`

- [ ] **Step 5: Run the live tree validator one final time**

```bash
python3 scripts/validate_artifact_contracts.py
```

Expected: `OK: 6 skills conform to artifact-contracts.md`

- [ ] **Step 6: Commit**

```bash
git add profile-al-dev-shared/knowledge/artifact-contracts.md
git commit -m "docs(contracts): add cross-link to skill scaffold template"
```

---

## Verification Checklist (run before reporting complete)

```bash
# All six unit tests pass
python3 scripts/tests/test_validate_artifact_contracts.py -v

# Live tree exits 0
python3 scripts/validate_artifact_contracts.py

# Neutrality not broken
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared

# All 8 files present
git status --short | head -20

# No forbidden patterns in any changed file
git diff HEAD~4 --name-only | xargs grep -l "YYYY-MM-DD\|TODO\|TBD\|\[date\]" 2>/dev/null && echo "FORBIDDEN PATTERNS FOUND" || echo "Clean"
```
