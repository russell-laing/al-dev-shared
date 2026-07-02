import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


def load_module():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "generate_duplicate_text_report.py"
    )
    spec = importlib.util.spec_from_file_location(
        "generate_duplicate_text_report",
        module_path,
    )
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(spec.name)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        if previous is None:
            sys.modules.pop(spec.name, None)
        else:
            sys.modules[spec.name] = previous
        raise
    return module


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def duplicate_lines(count: int = 8) -> list[str]:
    return [f"duplicate content line {index:02d}" for index in range(1, count + 1)]


class DuplicateTextReportTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def scan(self, **kwargs):
        module = load_module()
        return module.scan_paths(
            root=self.root,
            inputs=[self.root],
            min_lines=8,
            min_nonblank=4,
            min_chars=80,
            **kwargs,
        )

    def test_reports_eight_lines_and_ignores_seven(self):
        eight = duplicate_lines(8)
        seven = [f"short duplicate {index:02d}" for index in range(1, 8)]
        write_lines(self.root / "a.md", eight + ["separator"] + seven)
        write_lines(self.root / "b.md", eight + ["different"] + seven)

        result = self.scan()

        self.assertEqual(len(result.matches), 1)
        self.assertEqual(result.matches[0].line_count, 8)

    def test_collapses_overlapping_windows_into_one_maximal_match(self):
        duplicate = duplicate_lines(12)
        write_lines(self.root / "a.md", ["before a"] + duplicate + ["after a"])
        write_lines(self.root / "b.md", ["before b"] + duplicate + ["after b"])

        result = self.scan()

        self.assertEqual(len(result.matches), 1)
        self.assertEqual(result.matches[0].line_count, 12)
        self.assertEqual(len(result.matches[0].occurrences), 2)

    def test_groups_three_occurrences_into_one_match(self):
        duplicate = duplicate_lines()
        for name in ("a.md", "b.md", "c.md"):
            write_lines(self.root / name, [f"prefix {name}"] + duplicate)

        result = self.scan()

        self.assertEqual(len(result.matches), 1)
        self.assertEqual(len(result.matches[0].occurrences), 3)

    def test_default_exclusions_and_opt_in_flags(self):
        duplicate = duplicate_lines()
        write_lines(self.root / "active-a.md", duplicate)
        write_lines(self.root / "active-b.md", duplicate)
        write_lines(self.root / "archived" / "archived.md", duplicate)
        write_lines(self.root / "generated" / "generated.md", duplicate)
        write_lines(self.root / "__pycache__" / "cache.md", duplicate)
        write_lines(self.root / ".DS_Store", duplicate)
        (self.root / "binary.bin").write_bytes(
            b"\x00" + ("\n".join(duplicate)).encode()
        )

        default = self.scan()
        inclusive = self.scan(
            include_archived=True,
            include_generated=True,
        )

        self.assertEqual(default.scanned_files, 2)
        self.assertEqual(inclusive.scanned_files, 4)
        self.assertEqual(len(default.excluded_files), 5)

    def test_default_excludes_claude_worktree_copies(self):
        duplicate = duplicate_lines()
        write_lines(self.root / ".claude" / "skills" / "active-a.md", duplicate)
        write_lines(self.root / ".claude" / "skills" / "active-b.md", duplicate)
        write_lines(
            self.root
            / ".claude"
            / "worktrees"
            / "feature-a"
            / "copied-a.md",
            duplicate,
        )
        write_lines(
            self.root
            / ".claude"
            / "worktrees"
            / "feature-b"
            / "copied-b.md",
            duplicate,
        )

        result = self.scan()

        self.assertEqual(result.scanned_files, 2)
        self.assertEqual(len(result.matches), 1)
        self.assertEqual(
            {reason for _, reason in result.excluded_files},
            {"worktree"},
        )

    def test_detects_non_overlapping_duplicates_within_one_file(self):
        duplicate = duplicate_lines()
        write_lines(
            self.root / "repeat.md",
            duplicate + ["unique separator"] + duplicate,
        )

        result = self.scan()

        self.assertEqual(len(result.matches), 1)
        self.assertEqual(len(result.matches[0].occurrences), 2)
        self.assertEqual(result.matches[0].scope, "within one file")

    def test_markdown_output_is_deterministic_and_contains_locations(self):
        module = load_module()
        duplicate = duplicate_lines()
        write_lines(self.root / "z.md", duplicate)
        write_lines(self.root / "a.md", duplicate)

        result = self.scan()
        first = module.render_markdown(result, report_date="2026-06-12")
        second = module.render_markdown(result, report_date="2026-06-12")

        self.assertEqual(first, second)
        self.assertIn("# Duplicate Text Report", first)
        self.assertIn("`a.md:1`", first)
        self.assertIn("`z.md:1`", first)
        self.assertIn("8 lines", first)


if __name__ == "__main__":
    unittest.main()
