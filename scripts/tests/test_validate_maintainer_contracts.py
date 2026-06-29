"""Behavioral tests for scripts/validate_maintainer_contracts.py."""

import importlib.util
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "validate_maintainer_contracts.py"


def _load():
    spec = importlib.util.spec_from_file_location("vmc", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_skill(root: Path, name: str, body: str) -> None:
    d = root / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(body, encoding="utf-8")


def test_missing_reference_is_flagged():
    module = _load()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # A skill that the validator treats as multi-phase but omits the ref.
        name = sorted(module.MULTI_PHASE_SKILLS)[0]
        _make_skill(root, name, "# Skill\n\nNo contract reference here.\n")
        violations = module.check_coverage(root)
        assert any(name in v and "phase-proof" in v for v in violations), violations
    print("PASS test_missing_reference_is_flagged")


def test_present_reference_passes():
    module = _load()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        name = sorted(module.MULTI_PHASE_SKILLS)[0]
        _make_skill(root, name, "# Skill\n\nSee ../../knowledge/phase-proof-contract.md\n")
        violations = [v for v in module.check_coverage(root) if name in v]
        assert violations == [], violations
    print("PASS test_present_reference_passes")


def test_unlisted_skill_not_required():
    module = _load()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_skill(root, "not-a-maintainer-skill", "# Skill\n\nNothing required.\n")
        violations = [v for v in module.check_coverage(root) if "not-a-maintainer-skill" in v]
        assert violations == [], violations
    print("PASS test_unlisted_skill_not_required")


def test_bare_filename_does_not_satisfy():
    module = _load()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        name = sorted(module.MULTI_PHASE_SKILLS)[0]
        # A bare-filename mention (no ../../knowledge/ prefix) must NOT count.
        _make_skill(root, name, "# Skill\n\nSee phase-proof-contract.md\n")
        violations = [v for v in module.check_coverage(root) if name in v]
        assert violations != [], "bare filename must not satisfy the relative-path requirement"
    print("PASS test_bare_filename_does_not_satisfy")


def test_false_positive_classes_reference_is_required():
    module = _load()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_skill(root, "discover-plugin-health", "# Skill\n\nNo tracker reference here.\n")
        _make_skill(root, "report-plugin-health", "# Skill\n\nAlso missing the tracker.\n")
        violations = module.check_coverage(root)
        assert any(
            "discover-plugin-health" in v and "false-positive-classes" in v
            for v in violations
        ), violations
        assert any(
            "report-plugin-health" in v and "false-positive-classes" in v
            for v in violations
        ), violations
    print("PASS test_false_positive_classes_reference_is_required")


def test_token_usage_block_is_required_for_report_plugin_health():
    module = _load()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_skill(root, "report-plugin-health", "# Skill\n\nSee ../../knowledge/false-positive-classes.md\n")
        violations = module.check_coverage(root)
        assert any(
            "report-plugin-health" in v and "token-usage" in v
            for v in violations
        ), violations
    print("PASS test_token_usage_block_is_required_for_report_plugin_health")


def test_implement_skill_requires_procedure_log_contract():
    module = _load()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_skill(
            root,
            "implement-plugin-health",
            "# Skill\n\nSee ../../knowledge/phase-proof-contract.md\n",
        )
        violations = module.check_coverage(root)
        assert any(
            "implement-plugin-health-procedure-log.jsonl" in v for v in violations
        ), violations
    print("PASS test_implement_skill_requires_procedure_log_contract")


if __name__ == "__main__":
    test_missing_reference_is_flagged()
    test_present_reference_passes()
    test_unlisted_skill_not_required()
    test_bare_filename_does_not_satisfy()
    test_false_positive_classes_reference_is_required()
    test_token_usage_block_is_required_for_report_plugin_health()
    test_implement_skill_requires_procedure_log_contract()
    print("\nAll tests passed")
