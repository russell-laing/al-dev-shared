#!/usr/bin/env python3
"""
Extract unimplemented suggestions from map Observations sections.

Parses al-dev-skills-map.md and/or al-dev-agent-map.md Observations sections,
filters for unimplemented suggestions, and outputs a JSON artifact for queuing.

Usage:
    python3 extract-suggestions.py --surface skills --filter all [--output <path>]
    python3 extract-suggestions.py --surface agents --filter trim [--output <path>]
    python3 extract-suggestions.py --surface both --filter merge
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any


class SuggestionExtractor:
    """Extract suggestions from map Observations sections."""

    # Suggestion type keywords (used in bold headers)
    SUGGESTION_TYPES = {
        'trim', 'merge', 'split', 'inline', 'align', 'connect',
        'promote', 'extend', 'atomise', 'implemented'
    }

    def __init__(self, docs_dir: str = None):
        """Initialize with path to docs directory."""
        if docs_dir is None:
            # Default to docs/ relative to cwd
            docs_dir = 'docs'
        self.docs_dir = Path(docs_dir)

    def extract_from_file(self, map_file: str) -> List[Dict[str, Any]]:
        """
        Extract suggestions from a single map file.

        Args:
            map_file: Path to map file (e.g., 'al-dev-skills-map.md')

        Returns:
            List of suggestion dicts with id, type, subject, proposed_change, target_files
        """
        map_path = self.docs_dir / map_file

        if not map_path.exists():
            return []

        try:
            with open(map_path, 'r') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"Failed to read {map_path}: {e}")

        # Find Observations section
        obs_match = re.search(r'^## Observations\s*\n(.*?)(?=^##\s|\Z)', content, re.MULTILINE | re.DOTALL)
        if not obs_match:
            return []

        obs_section = obs_match.group(1)
        suggestions = []
        suggestion_id = {}  # Track suggestion counts by type

        # Split by suggestions (marked with **)
        # Pattern: **Type: Title** on its own or with status marker
        suggestion_pattern = r'^\*\*([A-Za-z]+):\s+([^\*]+)\*\*(.+?)(?=^\*\*|$)'

        for match in re.finditer(suggestion_pattern, obs_section, re.MULTILINE | re.DOTALL):
            suggestion_type_raw = match.group(1).lower()
            subject = match.group(2).strip()
            body = match.group(3).strip()

            # Skip implemented/completed suggestions
            if suggestion_type_raw == 'implemented' or '← implemented' in body or '← completed' in body:
                continue

            # Determine suggestion type (map to our canonical types)
            suggestion_type = self._normalize_type(suggestion_type_raw)
            if suggestion_type is None:
                continue

            # Extract target files from body
            target_files = self._extract_files(body)

            # Generate unique ID
            if suggestion_type not in suggestion_id:
                suggestion_id[suggestion_type] = 1
            else:
                suggestion_id[suggestion_type] += 1

            sid = f"{suggestion_type}-{suggestion_id[suggestion_type]:03d}"

            suggestions.append({
                'id': sid,
                'type': suggestion_type,
                'subject': subject,
                'proposed_change': body[:500],  # First 500 chars as summary
                'target_files': target_files
            })

        return suggestions

    def _normalize_type(self, raw_type: str) -> str:
        """Normalize suggestion type to canonical form."""
        raw_type = raw_type.lower().strip()

        # Map variants to canonical types
        mappings = {
            'trim': 'trim',
            'merge': 'merge',
            'split': 'split',
            'inline': 'inline',
            'align': 'align',
            'connect': 'connect',
            'promote': 'promote',
            'extend': 'extend',
            'atomise': 'atomise',
            'atomize': 'atomise',
        }

        return mappings.get(raw_type)

    def _extract_files(self, body: str) -> List[str]:
        """Extract file paths from suggestion body."""
        files = set()

        # Look for markdown file paths
        patterns = [
            r'`([^`]*\.md)`',  # Backtick-quoted files
            r'`([^`]*\.py)`',
            r'\[([^\]]*\.md)\]',  # Bracket-quoted files
            r'profile-al-dev-shared[/\w\-\.]+',  # Explicit paths
            r'\.dev/[/\w\-\.]+',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, body)
            files.update(matches)

        return sorted(list(files))

    def extract_all(self, surface: str) -> List[Dict[str, Any]]:
        """
        Extract suggestions from specified surface(s).

        Args:
            surface: 'skills', 'agents', or 'both'

        Returns:
            Combined list of suggestions
        """
        all_suggestions = []

        if surface in ('skills', 'both'):
            all_suggestions.extend(self.extract_from_file('al-dev-skills-map.md'))

        if surface in ('agents', 'both'):
            all_suggestions.extend(self.extract_from_file('al-dev-agent-map.md'))

        return all_suggestions

    def filter_suggestions(self, suggestions: List[Dict], filter_type: str) -> List[Dict]:
        """
        Filter suggestions by type.

        Args:
            suggestions: List of suggestion dicts
            filter_type: 'all' or specific type (trim, merge, etc.)

        Returns:
            Filtered list
        """
        if filter_type == 'all':
            return suggestions

        return [s for s in suggestions if s['type'] == filter_type]


def main():
    parser = argparse.ArgumentParser(
        description='Extract unimplemented suggestions from map Observations sections'
    )
    parser.add_argument(
        '--surface',
        choices=['skills', 'agents', 'both'],
        default='both',
        help='Which maps to read (default: both)'
    )
    parser.add_argument(
        '--filter',
        choices=['all', 'trim', 'merge', 'split', 'inline', 'align', 'connect', 'promote', 'extend', 'atomise'],
        default='all',
        help='Suggestion type filter (default: all)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: stdout)'
    )

    args = parser.parse_args()

    # Determine docs directory
    # Try multiple locations: cwd/docs, ../docs, etc.
    docs_dir = 'docs'
    if not Path(docs_dir).exists():
        # Try parent directory
        docs_dir = '../docs'
    if not Path(docs_dir).exists():
        # Try absolute path if running from repo root
        docs_dir = '/Users/russelllaing/al-dev-shared/docs'

    try:
        extractor = SuggestionExtractor(docs_dir)
        suggestions = extractor.extract_all(args.surface)
        filtered = extractor.filter_suggestions(suggestions, args.filter)

        output = {
            'surface': args.surface,
            'filter': args.filter,
            'suggestion_count': len(filtered),
            'suggestions': filtered
        }

        output_json = json.dumps(output, indent=2)

        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write(output_json)
            except Exception as e:
                print(f"Error writing to {args.output}: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(output_json)

        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
