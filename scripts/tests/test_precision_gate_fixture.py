import tempfile
import unittest
from pathlib import Path

from scripts.al_dev_tools.health import precision_gate_fixture as mod


class PrecisionGateFixtureTest(unittest.TestCase):
    def test_read_expected_ids_ignores_blank_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "expected.txt"
            path.write_text("fixture-one\n\nfixture-two\n", encoding="utf-8")
            self.assertEqual(
                ["fixture-one", "fixture-two"], mod.read_expected_ids(path)
            )

    def test_verify_retained_ids_passes_when_all_ids_present(self) -> None:
        dossier = (
            "## Quality findings\n\n- **[fixture-one]** retained\n"
            "- **[fixture-two]** retained\n"
        )
        self.assertEqual(
            [], mod.verify_retained_ids(dossier, ["fixture-one", "fixture-two"])
        )

    def test_verify_retained_ids_reports_missing_ids(self) -> None:
        dossier = "## Quality findings\n\n- **[fixture-one]** retained\n"
        self.assertEqual(
            ["fixture-two"],
            mod.verify_retained_ids(dossier, ["fixture-one", "fixture-two"]),
        )

    def test_verify_retained_ids_ignores_dropped_sections(self) -> None:
        dossier = (
            "## Dropped (unverified)\n\n- **[fixture-one]** retained\n\n"
            "## Quality findings\n\n- **[fixture-two]** retained\n"
        )
        self.assertEqual(
            ["fixture-one"],
            mod.verify_retained_ids(dossier, ["fixture-one", "fixture-two"]),
        )
