import importlib.util
import os
import tempfile
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "assemble_health_findings",
    str(Path(__file__).resolve().parents[1] / "assemble_health_findings.py"),
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _write_lens(d, lens, findings, count):
    payload = {"lens": lens, "findings": findings, "suggestion_count": count,
               "completed_at": "2026-06-25T00:00:00Z"}
    with open(os.path.join(d, f"2026-06-25-plugin-health-lens-{lens}.json"), "w") as f:
        json.dump(payload, f)


def test_assembles_with_markers_and_frontmatter():
    with tempfile.TemporaryDirectory() as d:
        _write_lens(d, "quality-agent-lens-structure",
                    "### Structural Conventions Findings\n\n- **al-dev-foo** | Medium | x | y", 1)
        _write_lens(d, "quality-skill-lens-structure",
                    "### Structural Conventions Findings\n\n_No issues found._", 0)
        out = mod.assemble_findings(
            lens_dir=d, date="2026-06-25", surface="plugin",
            dimensions=["quality"], failed_lenses=[],
            total_lenses=2, completed_session=2, completed_prior=0, skipped=0,
            completed_at="2026-06-25T00:00:00Z")
        # frontmatter
        assert out.startswith("---\nsurface: plugin\n"), out[:60]
        assert "dimensions:\n  - quality\n" in out
        # both lens markers present (disambiguates the two identical headings)
        assert "<!-- lens: quality-agent-lens-structure -->" in out
        assert "<!-- lens: quality-skill-lens-structure -->" in out
        # duplicate structural headings are uniquified by object-type suffix so
        # the assembled file passes markdownlint MD024 (no-duplicate-heading)
        assert "### Structural Conventions Findings (agents)" in out
        assert "### Structural Conventions Findings (skills)" in out
        assert "### Structural Conventions Findings\n" not in out
        # both blocks copied verbatim
        assert "- **al-dev-foo** | Medium | x | y" in out
        # resume block + status
        assert "## Resume information" in out
        assert "Status: COMPLETE" in out
        assert "## Failed lenses\n\nNone" in out


def test_failed_lenses_and_incomplete_status():
    with tempfile.TemporaryDirectory() as d:
        _write_lens(d, "quality-agent-lens-bloat",
                    "### Bloat Findings\n\n_No issues found._", 0)
        out = mod.assemble_findings(
            lens_dir=d, date="2026-06-25", surface="plugin",
            dimensions=["quality"], failed_lenses=["quality-skill-lens-bloat"],
            total_lenses=2, completed_session=1, completed_prior=0, skipped=0,
            completed_at="2026-06-25T00:00:00Z")
        assert "- quality-skill-lens-bloat" in out
        assert "Status: INCOMPLETE" in out


def test_ignores_out_of_dimension_lens():
    # A stale design lens JSON left in .dev by an interrupted run must NOT be
    # assembled into a quality-only findings file (dimension-aware filtering).
    with tempfile.TemporaryDirectory() as d:
        _write_lens(d, "quality-agent-lens-bloat",
                    "### Bloat Findings\n\n- **al-dev-foo** | Medium | x | y", 1)
        _write_lens(d, "design-agent-lens-tool-hygiene",
                    "### Tool Hygiene Findings\n\n- **al-dev-bar** | Low | x | y", 1)
        out = mod.assemble_findings(
            lens_dir=d, date="2026-06-25", surface="plugin",
            dimensions=["quality"], failed_lenses=[],
            total_lenses=1, completed_session=1, completed_prior=0, skipped=0,
            completed_at="2026-06-25T00:00:00Z")
        assert "<!-- lens: quality-agent-lens-bloat -->" in out
        assert "design-agent-lens-tool-hygiene" not in out
        assert "al-dev-bar" not in out


if __name__ == "__main__":
    test_assembles_with_markers_and_frontmatter()
    test_failed_lenses_and_incomplete_status()
    test_ignores_out_of_dimension_lens()
    print("PASS")
