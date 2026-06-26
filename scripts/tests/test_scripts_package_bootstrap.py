from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class ScriptsPackageBootstrapTest(unittest.TestCase):
    def test_scripts_package_has_stable_roots(self) -> None:
        import scripts

        self.assertEqual(REPO_ROOT / "scripts", scripts.SCRIPTS_ROOT)
        self.assertEqual(REPO_ROOT, scripts.REPO_ROOT)

    def test_docs_package_exports_shared_modules(self) -> None:
        from scripts.al_dev_tools.docs import (
            maintainer_guide_sections,
            map_doc_sections,
        )

        self.assertTrue(hasattr(map_doc_sections, "collect_inventory"))
        self.assertTrue(hasattr(maintainer_guide_sections, "build_sections"))

    def test_target_wrappers_no_longer_mutate_sys_path(self) -> None:
        for rel_path in (
            "scripts/generate-map-doc-sections.py",
            "scripts/generate-maintainer-guide.py",
            "scripts/generate-plugin-graph.py",
            "scripts/derive-agent-callers.py",
            "scripts/derive-skill-spawned-agents.py",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            self.assertNotIn("sys.path.insert", text, rel_path)

    def test_plugin_graph_uses_package_imports(self) -> None:
        text = (REPO_ROOT / "scripts/generate-plugin-graph.py").read_text(encoding="utf-8")
        self.assertIn("from scripts.al_dev_tools.docs.map_doc_sections import", text)


if __name__ == "__main__":
    unittest.main()
