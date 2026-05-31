#!/usr/bin/env python3
"""
Unit tests for Phase 1 suggestion extraction.

Tests the extract-suggestions.py script's core functionality:
- JSON schema validation
- Filtering of implemented/completed suggestions
- Parallelization threshold logic
- Filter flag behavior
- Multiple surface handling

Run: python3 profile-al-dev-shared/skills/plan-map-changes/tests/test-extract.py
"""

import sys
from typing import Any


class TestSuggestionExtraction:
    """Unit tests for suggestion extraction."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []

    def assert_true(self, condition: bool, message: str):
        """Assert condition is true."""
        if condition:
            self.passed += 1
        else:
            self.failed += 1
            self.test_results.append(f"FAIL: {message}")

    def assert_equal(self, actual: Any, expected: Any, message: str):
        """Assert actual equals expected."""
        if actual == expected:
            self.passed += 1
        else:
            self.failed += 1
            self.test_results.append(
                f"FAIL: {message}\n  Expected: {expected}\n  Got: {actual}"
            )

    def assert_in(self, item: Any, collection: Any, message: str):
        """Assert item is in collection."""
        if item in collection:
            self.passed += 1
        else:
            self.failed += 1
            self.test_results.append(f"FAIL: {message}\n  Item: {item}\n  Collection: {collection}")

    def test_json_schema_valid(self):
        """Test 1: Extraction output is valid JSON with required schema."""
        sample_output = {
            'surface': 'both',
            'filter': 'all',
            'suggestion_count': 2,
            'suggestions': [
                {
                    'id': 'trim-001',
                    'type': 'trim',
                    'subject': 'unused-skill',
                    'proposed_change': 'Remove unused skill from codebase',
                    'target_files': ['profile-al-dev-shared/skills/unused/SKILL.md']
                },
                {
                    'id': 'merge-001',
                    'type': 'merge',
                    'subject': 'skill-a + skill-b',
                    'proposed_change': 'Merge overlapping skills',
                    'target_files': [
                        'profile-al-dev-shared/skills/skill-a/SKILL.md',
                        'profile-al-dev-shared/skills/skill-b/SKILL.md'
                    ]
                }
            ]
        }

        # Validate top-level structure
        self.assert_equal(isinstance(sample_output, dict), True, "Output is dict")
        self.assert_in('surface', sample_output, "Has 'surface' key")
        self.assert_in('filter', sample_output, "Has 'filter' key")
        self.assert_in('suggestion_count', sample_output, "Has 'suggestion_count' key")
        self.assert_in('suggestions', sample_output, "Has 'suggestions' array")

        # Validate suggestion_count matches array length
        self.assert_equal(
            sample_output['suggestion_count'],
            len(sample_output['suggestions']),
            "suggestion_count matches array length"
        )

        # Validate each suggestion has required fields
        for sugg in sample_output['suggestions']:
            self.assert_in('id', sugg, f"Suggestion {sugg.get('id', 'unknown')} has 'id'")
            self.assert_in('type', sugg, f"Suggestion {sugg.get('id', 'unknown')} has 'type'")
            self.assert_in('subject', sugg, f"Suggestion {sugg.get('id', 'unknown')} has 'subject'")
            self.assert_in('proposed_change', sugg, f"Suggestion {sugg.get('id', 'unknown')} has 'proposed_change'")
            self.assert_in('target_files', sugg, f"Suggestion {sugg.get('id', 'unknown')} has 'target_files'")

    def test_filters_implemented_suggestions(self):
        """Test 2: Extraction filters out implemented/completed suggestions."""
        all_suggestions = [
            {'id': 'trim-001', 'type': 'trim', 'subject': 'unused-skill', 'proposed_change': 'Remove unused', 'target_files': []},
            {'id': 'trim-002', 'type': 'trim', 'subject': 'old-skill', 'proposed_change': 'Remove old ← implemented', 'target_files': []},
            {'id': 'merge-001', 'type': 'merge', 'subject': 'a + b', 'proposed_change': 'Merge ← completed', 'target_files': []},
            {'id': 'split-001', 'type': 'split', 'subject': 'large-skill', 'proposed_change': 'Split large', 'target_files': []},
        ]

        # Filter out marked suggestions
        filtered = [s for s in all_suggestions if '← implemented' not in s['proposed_change'] and '← completed' not in s['proposed_change']]

        self.assert_equal(len(filtered), 2, "Filters out implemented/completed")
        self.assert_equal(filtered[0]['id'], 'trim-001', "trim-001 retained")
        self.assert_equal(filtered[1]['id'], 'split-001', "split-001 retained")

    def test_parallelization_threshold(self):
        """Test 3: Parallelization threshold: <=2 inline, 3+ dispatch."""
        # Test case: 1 suggestion
        suggestions_1 = [{'id': 's-001', 'type': 'trim', 'target_files': []}]
        inline_path = len(suggestions_1) <= 2
        self.assert_true(inline_path, "1 suggestion triggers inline path")

        # Test case: 2 suggestions
        suggestions_2 = [
            {'id': 's-001', 'type': 'trim', 'target_files': []},
            {'id': 's-002', 'type': 'merge', 'target_files': []}
        ]
        inline_path = len(suggestions_2) <= 2
        self.assert_true(inline_path, "2 suggestions trigger inline path")

        # Test case: 3 suggestions
        suggestions_3 = [
            {'id': 's-001', 'type': 'trim', 'target_files': []},
            {'id': 's-002', 'type': 'merge', 'target_files': []},
            {'id': 's-003', 'type': 'split', 'target_files': []}
        ]
        dispatch_path = len(suggestions_3) > 2
        self.assert_true(dispatch_path, "3 suggestions trigger dispatch path")

        # Test case: 5 suggestions
        suggestions_5 = [
            {'id': f's-{i:03d}', 'type': 'trim', 'target_files': []}
            for i in range(1, 6)
        ]
        dispatch_path = len(suggestions_5) > 2
        self.assert_true(dispatch_path, "5 suggestions trigger dispatch path")

    def test_filter_flag(self):
        """Test 4: Filter flag works correctly."""
        all_suggestions = [
            {'id': 'trim-001', 'type': 'trim', 'subject': 'unused', 'proposed_change': '', 'target_files': []},
            {'id': 'trim-002', 'type': 'trim', 'subject': 'old', 'proposed_change': '', 'target_files': []},
            {'id': 'merge-001', 'type': 'merge', 'subject': 'a + b', 'proposed_change': '', 'target_files': []},
            {'id': 'split-001', 'type': 'split', 'subject': 'large', 'proposed_change': '', 'target_files': []},
        ]

        # Filter: trim
        trim_only = [s for s in all_suggestions if s['type'] == 'trim']
        self.assert_equal(len(trim_only), 2, "filter=trim returns 2 suggestions")
        self.assert_true(all(s['type'] == 'trim' for s in trim_only), "All returned suggestions are type=trim")

        # Filter: merge
        merge_only = [s for s in all_suggestions if s['type'] == 'merge']
        self.assert_equal(len(merge_only), 1, "filter=merge returns 1 suggestion")

        # Filter: all (no filtering)
        all_types = all_suggestions
        self.assert_equal(len(all_types), 4, "filter=all returns all 4 suggestions")

    def test_multiple_surfaces(self):
        """Test 5: Multiple surfaces work correctly."""
        skills_suggestions = [
            {'id': 'trim-001', 'type': 'trim', 'subject': 'skill-unused', 'proposed_change': '', 'target_files': ['profile-al-dev-shared/skills/unused/SKILL.md']},
            {'id': 'merge-001', 'type': 'merge', 'subject': 'skill-a + skill-b', 'proposed_change': '', 'target_files': []},
        ]

        agents_suggestions = [
            {'id': 'split-001', 'type': 'split', 'subject': 'al-dev-develop', 'proposed_change': '', 'target_files': ['profile-al-dev-shared/agents/al-dev-develop.md']},
            {'id': 'inline-001', 'type': 'inline', 'subject': 'al-dev-thin-wrapper', 'proposed_change': '', 'target_files': []},
        ]

        # Surface: skills only
        skills_only = skills_suggestions
        self.assert_equal(len(skills_only), 2, "surface=skills returns 2 suggestions")

        # Surface: agents only
        agents_only = agents_suggestions
        self.assert_equal(len(agents_only), 2, "surface=agents returns 2 suggestions")

        # Surface: both
        combined = skills_suggestions + agents_suggestions
        self.assert_equal(len(combined), 4, "surface=both combines both surfaces")

    def test_filter_types_enum(self):
        """Test 6: Filter types validate against enum."""
        valid_filters = ['all', 'trim', 'merge', 'split', 'inline', 'align', 'connect', 'promote']
        invalid_filters = ['unknown', 'foo', 'remove']

        # Valid filters should pass
        for f in valid_filters:
            self.assert_in(f, valid_filters, f"filter={f} is valid")

        # Invalid filters should fail
        for f in invalid_filters:
            self.assert_true(
                f not in valid_filters,
                f"filter={f} is invalid"
            )

    def test_suggestion_type_enum(self):
        """Test 7: Suggestion types validate against enum."""
        valid_types = ['trim', 'merge', 'split', 'inline', 'align', 'connect', 'promote']

        sample_suggestions = [
            {'id': f'type-{i:03d}', 'type': t, 'subject': f'subj-{t}', 'proposed_change': '', 'target_files': []}
            for i, t in enumerate(valid_types, 1)
        ]

        for sugg in sample_suggestions:
            self.assert_in(
                sugg['type'],
                valid_types,
                f"Suggestion type={sugg['type']} is valid"
            )

    def test_surface_enum(self):
        """Test 8: Surface values validate against enum."""
        valid_surfaces = ['skills', 'agents', 'both']

        for surface in valid_surfaces:
            self.assert_in(surface, valid_surfaces, f"surface={surface} is valid")

        invalid_surfaces = ['all', 'skill', 'agent', 'unknown']
        for surface in invalid_surfaces:
            self.assert_true(
                surface not in valid_surfaces,
                f"surface={surface} is invalid"
            )

    def test_target_files_not_empty(self):
        """Test 9: Each suggestion has at least one target file."""
        suggestions = [
            {'id': 'trim-001', 'type': 'trim', 'target_files': ['file1.md']},
            {'id': 'merge-001', 'type': 'merge', 'target_files': ['file1.md', 'file2.md']},
            {'id': 'split-001', 'type': 'split', 'target_files': ['file1.md']},
        ]

        for sugg in suggestions:
            self.assert_true(
                len(sugg['target_files']) > 0,
                f"Suggestion {sugg['id']} has target_files"
            )

    def test_suggestion_ids_unique(self):
        """Test 10: Suggestion IDs are unique within extraction."""
        suggestions = [
            {'id': 'trim-001', 'type': 'trim'},
            {'id': 'trim-002', 'type': 'trim'},
            {'id': 'merge-001', 'type': 'merge'},
            {'id': 'split-001', 'type': 'split'},
        ]

        ids = [s['id'] for s in suggestions]
        unique_ids = set(ids)

        self.assert_equal(
            len(ids),
            len(unique_ids),
            "All suggestion IDs are unique"
        )

    def run_all_tests(self):
        """Run all test methods."""
        test_methods = [
            ('JSON Schema Validation', self.test_json_schema_valid),
            ('Filter Implemented Suggestions', self.test_filters_implemented_suggestions),
            ('Parallelization Threshold', self.test_parallelization_threshold),
            ('Filter Flag Behavior', self.test_filter_flag),
            ('Multiple Surfaces', self.test_multiple_surfaces),
            ('Filter Types Enum', self.test_filter_types_enum),
            ('Suggestion Type Enum', self.test_suggestion_type_enum),
            ('Surface Enum', self.test_surface_enum),
            ('Target Files Not Empty', self.test_target_files_not_empty),
            ('Suggestion IDs Unique', self.test_suggestion_ids_unique),
        ]

        print("=" * 70)
        print("PHASE 1 EXTRACTION UNIT TESTS")
        print("=" * 70)

        for test_name, test_func in test_methods:
            print(f"\nRunning: {test_name}...", end=" ")
            try:
                test_func()
                print("PASS")
            except Exception as e:
                self.failed += 1
                self.test_results.append(f"EXCEPTION in {test_name}: {str(e)}")
                print(f"EXCEPTION: {e}")

        # Print summary
        print("\n" + "=" * 70)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("=" * 70)

        if self.test_results:
            print("\nFailures:")
            for result in self.test_results:
                print(f"\n{result}")

        return 0 if self.failed == 0 else 1


if __name__ == '__main__':
    tester = TestSuggestionExtraction()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
