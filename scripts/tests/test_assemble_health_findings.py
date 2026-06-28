import os
import tempfile
import json
from pathlib import Path

from scripts.al_dev_tools.health import assemble_health_findings as mod


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


def test_format_metrics_emits_eight_fields():
    counts = {
        "severity": {"design": {"high": 0, "medium": 1, "low": 0},
                     "quality": {"high": 2, "medium": 3, "low": 1},
                     "naming": {"high": 0, "medium": 0, "low": 0}},
        "raw_count": 12, "verified_count": 7, "dropped_unverified_count": 3,
        "stale_dropped_count": 1, "suppressed_count": 1, "failed_lens_count": 0,
        "new_count": 5, "recurring_count": 2,
    }
    out = mod.format_metrics(counts)
    for field in ("raw_count", "verified_count", "dropped_unverified_count",
                  "stale_dropped_count", "suppressed_count", "failed_lens_count",
                  "new_count", "recurring_count"):
        assert f"{field}:" in out, field
    assert "<!-- benchmark-metrics" in out and "-->" in out
    assert "| High" in out  # severity table present


def test_format_metrics_missing_field_raises():
    try:
        mod.format_metrics({"severity": {}, "raw_count": 1})
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError on missing metric field")


if __name__ == "__main__":
    test_assembles_with_markers_and_frontmatter()
    test_failed_lenses_and_incomplete_status()
    test_ignores_out_of_dimension_lens()
    test_format_metrics_emits_eight_fields()
    test_format_metrics_missing_field_raises()
    print("PASS")
