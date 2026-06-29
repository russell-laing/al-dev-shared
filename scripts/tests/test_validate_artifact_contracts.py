from __future__ import annotations

import inspect
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.al_dev_tools.shared_surface_names import (
    LEGACY_SHARED_PREFIX,
    runtime_artifact_patterns,
)
from scripts.validate_artifact_contracts import (  # noqa: E402
    RUNTIME_ARTIFACT_RULES,
    main,
    run_artifact_tests,
    validate,
)


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


def _make_runtime_artifacts(repo: Path, artifacts: dict[str, str]) -> None:
    dev = repo / ".dev"
    dev.mkdir()
    for name, body in artifacts.items():
        (dev / name).write_text(body, encoding="utf-8")


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


def test_run_artifact_tests_passes_when_latest_runtime_artifacts_match(tmp_path: Path) -> None:
    contract = _make_contract([{"skill": "my-skill"}])
    repo = _make_repo(tmp_path, contract, {"my-skill": _GOOD_BODY})
    patterns = runtime_artifact_patterns()
    _make_runtime_artifacts(repo, {
        f"2026-06-28-{patterns['ticket']['context'].lstrip('*-')}": "TICKET_ID: 1",
        f"2026-06-28-{patterns['interview']['requirements'].lstrip('*-')}": "REQ: 1",
        f"2026-06-28-{patterns['explore']['findings'].lstrip('*-')}": "## ANSWER",
        f"2026-06-28-{patterns['investigate']['findings'].lstrip('*-')}": "Root Cause",
        f"2026-06-28-{patterns['handoff']['prompt'].lstrip('*-')}": "## Context",
    })

    assert run_artifact_tests(repo) is True


def test_run_artifact_tests_fails_when_latest_runtime_artifact_is_missing_marker(tmp_path: Path) -> None:
    contract = _make_contract([{"skill": "my-skill"}])
    repo = _make_repo(tmp_path, contract, {"my-skill": _GOOD_BODY})
    patterns = runtime_artifact_patterns()
    _make_runtime_artifacts(repo, {
        f"2026-06-28-{patterns['ticket']['context'].lstrip('*-')}": "plain body without markers",
    })

    assert run_artifact_tests(repo) is False


def test_runtime_artifact_patterns_use_prefix_free_skill_names() -> None:
    patterns = runtime_artifact_patterns()
    assert patterns["ticket"]["context"] == "*-ticket-ticket-context.md"
    assert patterns["interview"]["requirements"] == "*-interview-requirements.md"
    assert patterns["handoff"]["prompt"] == "*-handoff-handoff-prompt.md"
    assert all(
        LEGACY_SHARED_PREFIX not in value
        for group in patterns.values()
        for value in group.values()
    )


def test_runtime_artifact_patterns_cover_task1_artifact_canon() -> None:
    patterns = runtime_artifact_patterns()
    assert patterns["develop-orchestrate"]["progress"] == "*-develop-progress.md"
    assert patterns["develop-orchestrate"]["checklist"] == "*-develop-checklist.md"
    assert patterns["develop-orchestrate"]["scope"] == "*-develop-scope.md"
    assert patterns["develop-orchestrate"]["phase4_handoff"] == "*-develop-phase4-handoff.md"
    assert patterns["developer-tdd"]["test_plan"] == "*-test-test-plan.md"
    assert patterns["developer-tdd"]["log"] == "*-developer-tdd-log.md"
    assert patterns["review-develop"]["code_review"] == "*-develop-code-review.md"
    assert patterns["perf"]["analysis"] == "*-perf-perf-analysis.md"


def test_validator_runtime_rules_are_helper_backed() -> None:
    patterns = runtime_artifact_patterns()
    expected = {
        ("ticket", patterns["ticket"]["context"]),
        ("interview", patterns["interview"]["requirements"]),
        ("explore", patterns["explore"]["findings"]),
        ("investigate", patterns["investigate"]["findings"]),
        ("handoff", patterns["handoff"]["prompt"]),
    }
    actual = {(rule.skill, rule.pattern) for rule in RUNTIME_ARTIFACT_RULES}
    assert actual == expected


def test_main_returns_zero_for_happy_fixture_when_runtime_tests_pass(tmp_path: Path) -> None:
    contract = _make_contract([{"skill": "my-skill"}])
    repo = _make_repo(tmp_path, contract, {"my-skill": _GOOD_BODY})
    with mock.patch("scripts.validate_artifact_contracts.run_artifact_tests", return_value=True):
        assert main([str(repo)]) == 0


def test_main_returns_one_for_happy_fixture_when_runtime_tests_fail(tmp_path: Path) -> None:
    contract = _make_contract([{"skill": "my-skill"}])
    repo = _make_repo(tmp_path, contract, {"my-skill": _GOOD_BODY})
    with mock.patch("scripts.validate_artifact_contracts.run_artifact_tests", return_value=False):
        assert main([str(repo)]) == 1


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
