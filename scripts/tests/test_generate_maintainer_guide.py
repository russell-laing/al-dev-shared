"""Fixture-based tests for scripts/maintainer_guide_sections.py and generate-maintainer-guide.py."""
from __future__ import annotations

import contextlib
import importlib.util
import inspect
import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(
        module_name,
        REPO_ROOT / "scripts" / filename,
    )
    if spec is None or spec.loader is None:
        raise FileNotFoundError(REPO_ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


lib = _load_module("maintainer_guide_sections.py", "maintainer_guide_sections")


def _write_skill(parent: Path, name: str, frontmatter_yaml: str) -> None:
    skill_dir = parent / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n" + frontmatter_yaml + "---\n\n# " + name + "\n",
        encoding="utf-8",
    )


def _build_skills_fixture(root: Path) -> Path:
    """Four active skills + one archived: covers every contract shape and gap signal."""
    skills = root / ".claude" / "skills"
    _write_skill(
        skills,
        "alpha-audit",
        "name: alpha-audit\n"
        "description: Audits the surface. Second sentence is ignored.\n"
        "workflow:\n"
        "  stage: discover\n"
        "  invoked-by: user\n"
        "  repeatable: true\n"
        "  inputs:\n"
        "    - profile-al-dev-shared/skills/\n"
        "  outputs:\n"
        "    - docs/health/<date>-findings.md\n"
        "  next: [beta-report]\n",
    )
    _write_skill(
        skills,
        "beta-report",
        "name: beta-report\n"
        "description: Ranks findings into a dossier.\n"
        "workflow:\n"
        "  stage: discover\n"
        "  invoked-by: skill:alpha-audit\n"
        "  repeatable: false\n"
        "  inputs:\n"
        "    - docs/health/<date>-findings.md\n"
        "  outputs:\n"
        "    - docs/health/<date>-dossier.md\n"
        "  next: [gamma-plan]\n",
    )
    _write_skill(
        skills,
        "gamma-plan",
        "name: gamma-plan\n"
        "description: Plans accepted findings.\n"
        "workflow:\n"
        "  stage: decide\n"
        "  invoked-by: user\n"
        "  repeatable: true\n"
        "  inputs:\n"
        "    - docs/health/<date>-dossier.md\n"
        "    - docs/ledger.md\n"
        "  outputs:\n"
        "    - docs/plans/<date>-plan.md\n"
        "  manual-followup: implement the plan\n",
    )
    _write_skill(
        skills,
        "delta-notes",
        "name: delta-notes\ndescription: No contract yet.\n",
    )
    _write_skill(
        skills / "archived",
        "old-skill",
        "name: old-skill\ndescription: Archived, must be ignored.\n",
    )
    return skills


def test_load_contracts_parses_and_reports_missing() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_skills_fixture(Path(td))
        contracts, missing = lib.load_contracts(skills)
        assert [c.skill for c in contracts] == ["alpha-audit", "beta-report", "gamma-plan"]
        assert missing == ["delta-notes"]
        alpha = contracts[0]
        assert alpha.stage == "discover"
        assert alpha.invoked_by == "user"
        assert alpha.repeatable is True
        assert alpha.inputs == ("profile-al-dev-shared/skills/",)
        assert alpha.outputs == ("docs/health/<date>-findings.md",)
        assert alpha.next_skills == ("beta-report",)
        assert alpha.manual_followup is None
        assert alpha.description.startswith("Audits the surface.")
        gamma = contracts[2]
        assert gamma.manual_followup == "implement the plan"
        assert gamma.next_skills == ()


def test_parse_contract_returns_none_without_block() -> None:
    assert lib.parse_contract("x", {"name": "x", "description": "d"}) is None


def test_parse_contract_rejects_bad_stage() -> None:
    fm = {"description": "d", "workflow": {"stage": "bogus", "invoked-by": "user"}}
    try:
        lib.parse_contract("bad-skill", fm)
    except ValueError as exc:
        assert "bad-skill" in str(exc) and "stage" in str(exc)
    else:
        raise AssertionError("expected ValueError for bad stage")


def test_parse_contract_rejects_bad_invoked_by() -> None:
    fm = {"description": "d", "workflow": {"stage": "discover", "invoked-by": "cron"}}
    try:
        lib.parse_contract("bad-skill", fm)
    except ValueError as exc:
        assert "bad-skill" in str(exc) and "invoked-by" in str(exc)
    else:
        raise AssertionError("expected ValueError for bad invoked-by")


def test_parse_contract_rejects_empty_input_entry() -> None:
    fm = {
        "description": "d",
        "workflow": {"stage": "discover", "invoked-by": "user", "inputs": ["ok", ""]},
    }
    try:
        lib.parse_contract("bad-skill", fm)
    except ValueError as exc:
        assert "bad-skill" in str(exc) and "inputs" in str(exc)
    else:
        raise AssertionError("expected ValueError for empty input entry")


def test_parse_contract_rejects_unknown_keys() -> None:
    fm = {
        "description": "d",
        "workflow": {"stage": "discover", "invoked-by": "user", "repeatible": True},
    }
    try:
        lib.parse_contract("bad-skill", fm)
    except ValueError as exc:
        assert "bad-skill" in str(exc) and "repeatible" in str(exc)
    else:
        raise AssertionError("expected ValueError for unknown workflow key")


def test_validate_contracts_rejects_unknown_next_and_invoker() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_skills_fixture(Path(td))
        contracts, missing = lib.load_contracts(skills)
        active = {c.skill for c in contracts} | set(missing)
        lib.validate_contracts(contracts, active)  # must not raise
        try:
            lib.validate_contracts(contracts, active - {"beta-report"})
        except ValueError as exc:
            assert "beta-report" in str(exc)
        else:
            raise AssertionError("expected ValueError for unknown next target")


def test_normalize_template() -> None:
    assert (
        lib.normalize_template("docs/health/<date>-<surface>-findings.md")
        == "docs/health/*-*-findings.md"
    )
    assert (
        lib.normalize_template(".dev/runs/RUN_ID/audit/<surface>.json")
        == ".dev/runs/*/audit/*.json"
    )
    assert lib.normalize_template("docs/plain.md") == "docs/plain.md"


def test_producers_consumers_match_on_normalized_templates() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_skills_fixture(Path(td))
        contracts, _ = lib.load_contracts(skills)
        prod = lib.producers(contracts)
        cons = lib.consumers(contracts)
        assert prod["docs/health/*-findings.md"] == ["alpha-audit"]
        assert cons["docs/health/*-findings.md"] == ["beta-report"]
        assert prod["docs/health/*-dossier.md"] == ["beta-report"]
        assert cons["docs/health/*-dossier.md"] == ["gamma-plan"]


def test_artifact_status_latest_never_and_directory() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        (repo / "docs" / "health").mkdir(parents=True)
        (repo / "docs" / "health" / "2026-06-01-findings.md").write_text("x", encoding="utf-8")
        (repo / "profile-al-dev-shared" / "skills").mkdir(parents=True)
        assert lib.artifact_status(repo, "docs/health/<date>-findings.md").startswith("latest ")
        assert lib.artifact_status(repo, "docs/health/<date>-dossier.md") == "never produced"
        assert lib.artifact_status(repo, "docs/never-written.md") == "never produced"
        assert lib.artifact_status(repo, "profile-al-dev-shared/skills/") == "present"
        assert lib.artifact_status(repo, "docs/missing-dir/") == "missing"


def test_compute_gaps_reports_all_six_signals() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        skills = _build_skills_fixture(repo)
        contracts, missing = lib.load_contracts(skills)
        gaps = lib.compute_gaps(contracts, missing, repo)
        assert sorted(gaps) == [
            "internal-only",
            "manual-step",
            "missing-contract",
            "orphaned-artifact",
            "sourceless-input",
            "stale-artifact",
        ]
        orphan_items = [item for item, _ in gaps["orphaned-artifact"]]
        assert orphan_items == ["docs/plans/*-plan.md"]
        sourceless_items = [item for item, _ in gaps["sourceless-input"]]
        assert sourceless_items == ["docs/ledger.md"]  # allowlisted prefix exempted
        assert gaps["manual-step"] == [("implement the plan", "follows /gamma-plan")]
        assert gaps["missing-contract"] == [("delta-notes", "active skill with no workflow contract")]
        assert gaps["internal-only"] == [("beta-report", "dispatched by /alpha-audit")]
        stale_items = [item for item, _ in gaps["stale-artifact"]]
        assert stale_items == [
            "docs/health/*-dossier.md",
            "docs/health/*-findings.md",
            "docs/plans/*-plan.md",
        ]
        assert all(detail == "never produced" for _, detail in gaps["stale-artifact"])


def test_overview_renders_entries_repeat_loops_and_manual_steps() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_skills_fixture(Path(td))
        contracts, _ = lib.load_contracts(skills)
        text, node_count = lib.render_overview(contracts)
        assert text.startswith("```mermaid\nflowchart LR")
        assert 'skill_alpha_audit["/alpha-audit"]' in text
        assert 'skill_gamma_plan["/gamma-plan"]' in text
        assert "skill_beta_report" not in text  # internal skill never in overview
        # Cross-stage closure edge labeled with the artifact that flows along it:
        assert 'skill_alpha_audit -- "docs/health/*-dossier.md" --> skill_gamma_plan' in text
        assert 'skill_alpha_audit -. "repeat" .-> skill_alpha_audit' in text
        assert 'manual_gamma_plan["implement the plan"]' in text
        assert "skill_gamma_plan --> manual_gamma_plan" in text
        assert "class manual_gamma_plan manualStep" in text
        assert 'subgraph stage_discover["Discover"]' in text
        assert node_count == 3  # alpha, gamma, manual node


def test_stage_detail_marks_internal_skills_artifacts_and_orphans() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_skills_fixture(Path(td))
        contracts, _ = lib.load_contracts(skills)
        text, node_count = lib.render_stage_detail(contracts, "discover", set())
        assert 'skill_beta_report["/beta-report"]' in text
        assert "class skill_beta_report internalSkill" in text
        assert "class skill_alpha_audit userSkill" in text
        assert '["docs/health/*-findings.md"]' in text
        assert "skill_alpha_audit -. \"repeat\" .-> skill_alpha_audit" in text
        assert "skill_alpha_audit --> skill_beta_report" in text  # same-stage next edge
        # invoked-by edge suppressed because the next edge already covers the pair:
        assert "skill_alpha_audit -.-> skill_beta_report" not in text
        assert node_count == 5  # 2 skills + 3 artifacts (skills/ input, findings, dossier)

        decide_text, _ = lib.render_stage_detail(
            contracts, "decide", {"docs/plans/*-plan.md"}
        )
        assert "orphanArtifact" in decide_text
        assert 'manual_gamma_plan["implement the plan"]' in decide_text


def test_stage_detail_draws_dispatcher_edge_when_no_next_edge() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = Path(td) / ".claude" / "skills"
        _write_skill(
            skills,
            "parent-skill",
            "name: parent-skill\n"
            "description: Parent.\n"
            "workflow:\n"
            "  stage: discover\n"
            "  invoked-by: user\n"
            "  repeatable: false\n",
        )
        _write_skill(
            skills,
            "child-skill",
            "name: child-skill\n"
            "description: Child.\n"
            "workflow:\n"
            "  stage: discover\n"
            "  invoked-by: skill:parent-skill\n"
            "  repeatable: false\n",
        )
        contracts, _ = lib.load_contracts(skills)
        text, _ = lib.render_stage_detail(contracts, "discover", set())
        assert "skill_parent_skill -.-> skill_child_skill" in text


def test_stage_detail_empty_stage_returns_sentence() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_skills_fixture(Path(td))
        contracts, _ = lib.load_contracts(skills)
        text, node_count = lib.render_stage_detail(contracts, "support", set())
        assert "```mermaid" not in text
        assert "workflow" in text
        assert node_count == 0


def test_stage_detail_node_budget_counts_all_nodes() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = Path(td) / ".claude" / "skills"
        inputs = "\n".join(f"    - docs/big/file-{i}.md" for i in range(16))
        _write_skill(
            skills,
            "big-skill",
            "name: big-skill\n"
            "description: Has many artifacts.\n"
            "workflow:\n"
            "  stage: derive\n"
            "  invoked-by: user\n"
            "  repeatable: false\n"
            "  inputs:\n" + inputs + "\n",
        )
        contracts, _ = lib.load_contracts(skills)
        _, node_count = lib.render_stage_detail(contracts, "derive", set())
        assert node_count == 17  # 1 skill + 16 artifacts: exceeds NODE_BUDGET of 15
        assert node_count > lib.NODE_BUDGET


def _run(func):
    sig = inspect.signature(func)
    if not sig.parameters:
        func()
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
