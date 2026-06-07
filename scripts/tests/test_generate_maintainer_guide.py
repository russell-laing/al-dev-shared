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


def _build_map_sync_fixture(root: Path) -> Path:
    skills = root / ".claude" / "skills"
    _write_skill(
        skills,
        "review-maps",
        "name: review-maps\n"
        "description: Map accuracy sync.\n"
        "workflow:\n"
        "  stage: map-sync\n"
        "  invoked-by: user\n"
        "  repeatable: true\n"
        "  next: [sync-documentation-maps]\n",
    )
    _write_skill(
        skills,
        "sync-documentation-maps",
        "name: sync-documentation-maps\n"
        "description: Start async sync.\n"
        "workflow:\n"
        "  stage: map-sync\n"
        "  invoked-by: both\n"
        "  repeatable: true\n"
        "  inputs:\n"
        "    - docs/al-dev-skills-map.md\n"
        "    - docs/al-dev-agent-map.md\n"
        "  outputs:\n"
        "    - .dev/sync-documentation-maps-checkpoint.json\n"
        "    - .dev/sync-documentation-maps-runs/RUN_ID/audit/<surface>-audit.json\n"
        "  next: [sync-documentation-maps-collect]\n",
    )
    _write_skill(
        skills,
        "sync-documentation-maps-collect",
        "name: sync-documentation-maps-collect\n"
        "description: Collect async audits.\n"
        "workflow:\n"
        "  stage: map-sync\n"
        "  invoked-by: user\n"
        "  repeatable: false\n"
        "  inputs:\n"
        "    - .dev/sync-documentation-maps-checkpoint.json\n"
        "    - .dev/sync-documentation-maps-runs/RUN_ID/audit/<surface>-audit.json\n"
        "  outputs:\n"
        "    - .dev/sync-documentation-maps-runs/RUN_ID/updates/<surface>-map.md\n"
        "  next: [sync-documentation-maps-apply]\n",
    )
    _write_skill(
        skills,
        "sync-documentation-maps-apply",
        "name: sync-documentation-maps-apply\n"
        "description: Apply async updates.\n"
        "workflow:\n"
        "  stage: map-sync\n"
        "  invoked-by: user\n"
        "  repeatable: false\n"
        "  inputs:\n"
        "    - .dev/sync-documentation-maps-checkpoint.json\n"
        "    - .dev/sync-documentation-maps-runs/RUN_ID/updates/<surface>-map.md\n"
        "  outputs:\n"
        "    - docs/al-dev-skills-map.md\n"
        "    - docs/al-dev-agent-map.md\n"
        "  next: [sync-documentation-maps-write]\n",
    )
    _write_skill(
        skills,
        "sync-documentation-maps-write",
        "name: sync-documentation-maps-write\n"
        "description: Final regeneration step.\n"
        "workflow:\n"
        "  stage: map-sync\n"
        "  invoked-by: user\n"
        "  repeatable: false\n"
        "  inputs:\n"
        "    - .dev/sync-documentation-maps-checkpoint.json\n"
        "    - docs/al-dev-skills-map.md\n"
        "    - docs/al-dev-agent-map.md\n"
        "  outputs:\n"
        "    - docs/al-dev-workflow-diagrams.md\n"
        "    - docs/al-dev-plugin-graph.md\n"
        "    - docs/maintainer-tooling.md\n"
        "    - profile-al-dev-shared/generated/agents/\n",
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


def test_short_label_preserves_trailing_slash_directory_names() -> None:
    assert lib._short_label("profile-al-dev-shared/generated/agents/") == "generated/agents/"
    assert lib._short_label("profile-al-dev-shared/knowledge/") == "knowledge/"
    assert lib._short_label("profile-al-dev-shared/skills/") == "skills/"
    assert (
        lib._short_label("docs/al-dev-workflow-diagrams.md")
        == ".../al-dev-workflow-diagrams.md"
    )


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


def test_overview_renders_entries_and_manual_steps_without_repeat_loops() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_skills_fixture(Path(td))
        contracts, _ = lib.load_contracts(skills)
        text, node_count = lib.render_overview(contracts)
        assert text.startswith("```mermaid\nflowchart LR")
        assert 'skill_alpha_audit["/alpha-audit"]' in text
        assert 'skill_gamma_plan["/gamma-plan"]' in text
        assert "skill_beta_report" not in text  # internal skill never in overview
        assert 'skill_alpha_audit -- "docs/health/*-dossier.md" --> skill_gamma_plan' in text
        assert "repeat" not in text
        assert 'manual_gamma_plan["implement the plan"]' in text
        assert "skill_gamma_plan --> manual_gamma_plan" in text
        assert "class manual_gamma_plan manualStep" in text
        assert 'subgraph stage_discover["Discover"]' in text
        assert text.index('subgraph stage_discover["Discover"]') < text.index(
            'subgraph stage_decide["Decide"]'
        )
        # Layout-enforced order: invisible ordering chain between consecutive stages
        assert "stage_discover ~~~ stage_decide" in text
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


def test_map_sync_stage_uses_entry_lanes_and_collapsed_downstream_outputs() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_map_sync_fixture(Path(td))
        contracts, _ = lib.load_contracts(skills)
        text, node_count = lib.render_stage_detail(
            contracts,
            "map-sync",
            {
                "docs/al-dev-workflow-diagrams.md",
                "docs/al-dev-plugin-graph.md",
                "docs/maintainer-tooling.md",
                "profile-al-dev-shared/generated/agents/",
            },
        )
        assert 'subgraph map_entry["Normal entry point"]' in text
        assert 'subgraph map_async["Async lane"]' in text
        assert text.index('skill_review_maps["/review-maps"]') < text.index(
            'skill_sync_documentation_maps["/sync-documentation-maps"]'
        )
        assert "review-documentation-map" not in text
        assert "map_in_session" not in text
        assert "skill_review_maps --> art_map_docs" not in text
        assert "art_source_dirs --> skill_review_maps" not in text
        assert "art_source_dirs --> skill_sync_documentation_maps" in text
        assert 'art_downstream_generated["downstream generated"]' in text
        assert "art_profile_al_dev_shared_generated_agents_" not in text
        assert ".../sync-documentation-maps-checkpoint.json" not in text
        assert "repeat" not in text
        assert node_count <= lib.NODE_BUDGET


def test_map_sync_stage_falls_back_when_retired_skill_still_exists() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_map_sync_fixture(Path(td))
        _write_skill(
            skills,
            "review-documentation-map",
            "name: review-documentation-map\n"
            "description: Retired lane still present.\n"
            "workflow:\n"
            "  stage: map-sync\n"
            "  invoked-by: both\n"
            "  repeatable: true\n"
            "  inputs:\n"
            "    - docs/al-dev-skills-map.md\n"
            "    - docs/al-dev-agent-map.md\n"
            "    - profile-al-dev-shared/skills/\n"
            "    - profile-al-dev-shared/agents/\n"
            "  outputs:\n"
            "    - docs/al-dev-skills-map.md\n"
            "    - docs/al-dev-agent-map.md\n",
        )
        contracts, _ = lib.load_contracts(skills)
        text, node_count = lib.render_stage_detail(contracts, "map-sync", set())
        assert 'subgraph map_entry["Normal entry point"]' not in text
        assert 'subgraph map_async["Async lane"]' not in text
        assert 'skill_review_documentation_map["/review-documentation-map"]' in text
        assert 'art_profile_al_dev_shared_skills_["skills/"]' in text
        assert 'art__dev_sync_documentation_maps_checkpoint_json[".../sync-documentation-maps-checkpoint.json"]' in text
        assert node_count > lib.NODE_BUDGET


def test_derive_stage_uses_agent_and_knowledge_lanes_with_optional_fix() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = Path(td) / ".claude" / "skills"
        _write_skill(
            skills,
            "projection-sync",
            "name: projection-sync\n"
            "description: Regenerate projections.\n"
            "workflow:\n"
            "  stage: derive\n"
            "  invoked-by: user\n"
            "  repeatable: true\n"
            "  inputs:\n"
            "    - profile-al-dev-shared/agents/\n"
            "  outputs:\n"
            "    - profile-al-dev-shared/generated/agents/\n"
            "  next: [align-harness-repos]\n",
        )
        _write_skill(
            skills,
            "audit-knowledge-quality",
            "name: audit-knowledge-quality\n"
            "description: Audit knowledge.\n"
            "workflow:\n"
            "  stage: derive\n"
            "  invoked-by: user\n"
            "  repeatable: true\n"
            "  inputs:\n"
            "    - profile-al-dev-shared/knowledge/\n"
            "  outputs:\n"
            "    - docs/al-dev-knowledge-quality.md\n"
            "  next: [fix-knowledge-quality]\n",
        )
        _write_skill(
            skills,
            "fix-knowledge-quality",
            "name: fix-knowledge-quality\n"
            "description: Fix high knowledge findings.\n"
            "workflow:\n"
            "  stage: derive\n"
            "  invoked-by: user\n"
            "  repeatable: true\n"
            "  inputs:\n"
            "    - docs/al-dev-knowledge-quality.md\n"
            "  outputs:\n"
            "    - profile-al-dev-shared/knowledge/\n"
            "  next: [align-harness-repos]\n",
        )
        _write_skill(
            skills,
            "align-harness-repos",
            "name: align-harness-repos\n"
            "description: Validate neutrality.\n"
            "workflow:\n"
            "  stage: derive\n"
            "  invoked-by: user\n"
            "  repeatable: true\n"
            "  inputs:\n"
            "    - profile-al-dev-shared/skills/\n"
            "    - profile-al-dev-shared/agents/\n"
            "    - profile-al-dev-shared/knowledge/\n",
        )
        contracts, _ = lib.load_contracts(skills)
        text, node_count = lib.render_stage_detail(
            contracts,
            "derive",
            {"profile-al-dev-shared/generated/agents/"},
        )
        assert 'subgraph agent_lane["Agent source changed"]' in text
        assert 'subgraph knowledge_lane["Knowledge source changed"]' in text
        assert 'skill_projection_sync["/projection-sync"]' in text
        assert 'skill_audit_knowledge_quality["/audit-knowledge-quality"]' in text
        assert 'skill_fix_knowledge_quality["/fix-knowledge-quality"]' in text
        assert 'skill_align_harness_repos["/align-harness-repos"]' in text
        assert 'art_knowledge_quality_report -- "if HIGH" --> skill_fix_knowledge_quality' in text
        assert "skill_fix_knowledge_quality --> skill_align_harness_repos" in text
        assert 'art_generated_agents["generated/agents/"]' in text
        assert '[".../"]' not in text
        assert "repeat" not in text
        assert node_count <= lib.NODE_BUDGET


def test_focused_stage_renderer_falls_back_when_contract_shape_drifts() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_map_sync_fixture(Path(td))
        write_skill = skills / "sync-documentation-maps-write" / "SKILL.md"
        write_skill.write_text(
            write_skill.read_text(encoding="utf-8").replace(
                "    - docs/al-dev-plugin-graph.md\n",
                "",
            ),
            encoding="utf-8",
        )
        contracts, _ = lib.load_contracts(skills)
        text, node_count = lib.render_stage_detail(contracts, "map-sync", set())
        assert 'subgraph map_entry["Normal entry point"]' not in text
        assert 'subgraph map_async["Async lane"]' not in text
        assert 'art_downstream_generated["downstream generated"]' not in text
        assert 'skill_sync_documentation_maps_write["/sync-documentation-maps-write"]' in text
        assert 'art_docs_al_dev_workflow_diagrams_md[".../al-dev-workflow-diagrams.md"]' in text
        assert 'art__dev_sync_documentation_maps_checkpoint_json[".../sync-documentation-maps-checkpoint.json"]' in text
        assert 'art_docs_al_dev_plugin_graph_md[".../al-dev-plugin-graph.md"]' not in text
        assert 'art_docs_maintainer_tooling_md["docs/maintainer-tooling.md"]' in text
        assert 'art_profile_al_dev_shared_generated_agents_["generated/agents/"]' in text
        assert node_count == 13


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


def test_user_journey_lists_only_user_invoked_skills_in_order() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_skills_fixture(Path(td))
        contracts, _ = lib.load_contracts(skills)
        text = lib.render_user_journey(contracts)
        assert "### Discover steps" in text
        assert "### Decide steps" in text
        assert "`/alpha-audit`" in text
        assert "`/beta-report`" not in text  # internal-only skills excluded
        assert "Repeat as needed." in text
        assert "- reads: `docs/health/<date>-dossier.md`, `docs/ledger.md`" in text
        assert "- writes: `docs/plans/<date>-plan.md`" in text
        assert "2. Manual step: implement the plan." in text


def test_skills_tables_render_glance_and_io() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_skills_fixture(Path(td))
        contracts, _ = lib.load_contracts(skills)
        text = lib.render_skills_tables(contracts)
        assert "### Skills at a glance" in text
        assert "### Inputs and outputs" in text
        assert "| `/alpha-audit` | discover | user | Audits the surface. |" in text
        assert "| `/beta-report` | discover | skill:alpha-audit | Ranks findings into a dossier. |" in text
        assert "| `/gamma-plan` | `docs/health/<date>-dossier.md`, `docs/ledger.md` | `docs/plans/<date>-plan.md` | — |" in text


def test_gaps_table_renders_all_six_signal_groups_with_none_rows() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        skills = _build_skills_fixture(repo)
        contracts, missing = lib.load_contracts(skills)
        gaps = lib.compute_gaps(contracts, missing, repo)
        text = lib.render_gaps_table(gaps)
        for title in (
            "Orphaned artifact",
            "Sourceless input",
            "Manual step",
            "Missing contract",
            "Artifact freshness",
            "Internal-only skill",
        ):
            assert title in text, title
        assert "| Manual step | `implement the plan` | follows /gamma-plan |" in text
        # The fixture has every signal populated, so no "none" rows appear:
        assert "| none | — |" not in text
        empty = {key: [] for key in gaps}
        empty_text = lib.render_gaps_table(empty)
        assert empty_text.count("| none | — |") == 6


def test_build_sections_wraps_all_marker_keys_and_warns_over_budget() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        skills = _build_skills_fixture(repo)
        contracts, missing = lib.load_contracts(skills)
        sections, warnings = lib.build_sections(contracts, missing, repo)
        expected_keys = {
            "maintainer-workflow-overview",
            "maintainer-stage-map-sync",
            "maintainer-stage-discover",
            "maintainer-stage-decide",
            "maintainer-stage-derive",
            "maintainer-stage-support",
            "maintainer-user-journey",
            "maintainer-skills-tables",
            "maintainer-gaps",
        }
        assert set(sections) == expected_keys
        for key, body in sections.items():
            assert body.startswith(f"<!-- BEGIN GENERATED: {key} -->\n"), key
            assert body.endswith(f"\n<!-- END GENERATED: {key} -->"), key
        assert warnings == []

        # Add a 16-artifact skill to force a named node-budget warning:
        inputs = "\n".join(f"    - docs/big/file-{i}.md" for i in range(16))
        _write_skill(
            skills,
            "zz-big",
            "name: zz-big\n"
            "description: Big.\n"
            "workflow:\n"
            "  stage: derive\n"
            "  invoked-by: user\n"
            "  repeatable: false\n"
            "  inputs:\n" + inputs + "\n",
        )
        contracts2, missing2 = lib.load_contracts(skills)
        _, warnings2 = lib.build_sections(contracts2, missing2, repo)
        assert any("maintainer-stage-derive" in w and "17" in w for w in warnings2), warnings2


def _guide_template(*, drop_key: str | None = None) -> str:
    keys = [
        "maintainer-workflow-overview",
        "maintainer-stage-map-sync",
        "maintainer-stage-discover",
        "maintainer-stage-decide",
        "maintainer-stage-derive",
        "maintainer-stage-support",
        "maintainer-user-journey",
        "maintainer-skills-tables",
        "maintainer-gaps",
    ]
    parts = ["# Maintainer Tooling Reference", "", "Hand-authored intro.", ""]
    for key in keys:
        if key == drop_key:
            continue
        parts.append(f"<!-- BEGIN GENERATED: {key} -->")
        parts.append("stale placeholder")
        parts.append(f"<!-- END GENERATED: {key} -->")
        parts.append("")
    parts.append("Hand-authored outro.")
    return "\n".join(parts) + "\n"


def _patched_cli(root: Path):
    cli = _load_module("generate-maintainer-guide.py", "generate_maintainer_guide")
    cli.REPO = root
    cli.SKILLS_DIR = root / ".claude" / "skills"
    cli.GUIDE_PATH = root / "docs" / "maintainer-tooling.md"
    return cli


def test_cli_main_rewrites_only_marked_regions() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _build_skills_fixture(root)
        guide = root / "docs" / "maintainer-tooling.md"
        guide.parent.mkdir(parents=True)
        guide.write_text(_guide_template(), encoding="utf-8")
        cli = _patched_cli(root)
        assert cli.main() == 0
        text = guide.read_text(encoding="utf-8")
        assert "Hand-authored intro." in text
        assert "Hand-authored outro." in text
        assert "stale placeholder" not in text
        assert 'skill_alpha_audit["/alpha-audit"]' in text
        assert "| Manual step | `implement the plan` | follows /gamma-plan |" in text


def test_cli_main_fails_closed_on_malformed_contract() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        skills = _build_skills_fixture(root)
        _write_skill(
            skills,
            "broken-skill",
            "name: broken-skill\n"
            "description: Broken.\n"
            "workflow:\n"
            "  stage: nonsense\n"
            "  invoked-by: user\n",
        )
        guide = root / "docs" / "maintainer-tooling.md"
        guide.parent.mkdir(parents=True)
        guide.write_text(_guide_template(), encoding="utf-8")
        before = guide.read_bytes()
        cli = _patched_cli(root)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            assert cli.main() == 1
        assert "broken-skill" in stderr.getvalue()  # error names the offending skill
        assert guide.read_bytes() == before  # byte-identical: no partial rewrite


def test_cli_main_fails_closed_when_marker_pair_missing() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _build_skills_fixture(root)
        guide = root / "docs" / "maintainer-tooling.md"
        guide.parent.mkdir(parents=True)
        guide.write_text(_guide_template(drop_key="maintainer-gaps"), encoding="utf-8")
        before = guide.read_bytes()
        cli = _patched_cli(root)
        assert cli.main() == 1
        assert guide.read_bytes() == before


def test_skills_tables_escapes_pipe_in_description() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = Path(td) / ".claude" / "skills"
        _write_skill(
            skills,
            "pipe-skill",
            "name: pipe-skill\n"
            "description: Handles foo | bar inputs.\n"
            "workflow:\n"
            "  stage: discover\n"
            "  invoked-by: user\n"
            "  repeatable: false\n",
        )
        contracts, _ = lib.load_contracts(skills)
        text = lib.render_skills_tables(contracts)
        # The pipe in the Role cell must be backslash-escaped so the row keeps 4 columns:
        assert r"Handles foo \| bar inputs." in text
        glance_row = next(
            line for line in text.splitlines() if line.startswith("| `/pipe-skill`")
        )
        # 4 columns => 5 unescaped delimiters; the escaped \| does not count as a delimiter.
        assert glance_row.count("|") - glance_row.count("\\|") == 5


def test_compute_gaps_excludes_self_generated_guide_from_freshness() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        skills = repo / ".claude" / "skills"
        _write_skill(
            skills,
            "writer-skill",
            "name: writer-skill\n"
            "description: Writes the guide.\n"
            "workflow:\n"
            "  stage: map-sync\n"
            "  invoked-by: user\n"
            "  repeatable: false\n"
            "  outputs:\n"
            "    - docs/maintainer-tooling.md\n"
            "    - docs/other-output.md\n",
        )
        contracts, missing = lib.load_contracts(skills)
        gaps = lib.compute_gaps(contracts, missing, repo)
        stale_items = [item for item, _ in gaps["stale-artifact"]]
        # The guide must NOT report its own freshness (self-referential, breaks idempotence):
        assert "docs/maintainer-tooling.md" not in stale_items
        # But other produced artifacts still get a freshness row:
        assert "docs/other-output.md" in stale_items
        # And the guide is still surfaced as an orphaned artifact (time-invariant signal):
        orphan_items = [item for item, _ in gaps["orphaned-artifact"]]
        assert "docs/maintainer-tooling.md" in orphan_items


def test_live_contracts_select_focused_map_sync_and_derive_renderers() -> None:
    skills = REPO_ROOT / ".claude" / "skills"
    contracts, _ = lib.load_contracts(skills)
    map_sync_text, _ = lib.render_stage_detail(contracts, "map-sync", set())
    assert 'subgraph map_entry["Normal entry point"]' in map_sync_text, (
        "live map-sync contracts no longer match the focused renderer; "
        "the guide will degrade to the dense generic diagram"
    )
    assert 'subgraph map_async["Async lane"]' in map_sync_text
    assert 'skill_review_documentation_map["/review-documentation-map"]' not in map_sync_text
    assert "skill_review_maps --> art_map_docs" not in map_sync_text
    assert "art_source_dirs --> skill_sync_documentation_maps" in map_sync_text
    derive_text, _ = lib.render_stage_detail(contracts, "derive", set())
    assert 'subgraph agent_lane["Agent source changed"]' in derive_text, (
        "live derive contracts no longer match the focused-renderer shape; "
        "the guide will degrade to the dense generic diagram"
    )


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
