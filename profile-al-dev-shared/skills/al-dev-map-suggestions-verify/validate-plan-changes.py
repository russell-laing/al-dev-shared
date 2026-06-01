#!/usr/bin/env python3
"""
Manifest validator for al-dev-map-suggestions-verify skill.

Validates manifest.json structure and content against MANIFEST-SCHEMA.md.

Usage:
    python3 validate-plan-changes.py --manifest <path>

Exit codes:
    0 if manifest is valid
    1 if manifest is invalid or manifest file not found
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, List


class ManifestValidator:
    """Validates al-dev-map-suggestions-verify manifest JSON structure."""

    # Valid enum values
    VALID_OPERATIONS = {'inline', 'remote'}
    VALID_PHASES = {'phase2', 'phase3'}
    VALID_STATUSES = {'pending', 'in_progress', 'completed', 'failed'}
    VALID_SUGGESTION_TYPES = {'trim', 'merge', 'split', 'inline', 'align', 'connect', 'promote'}
    VALID_SUGGESTION_STATUSES = {'pending', 'in_progress', 'completed', 'failed'}
    VALID_ERROR_STATUSES = {'file_not_found', 'parse_error', 'check_failure', 'timeout'}

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_uuid_format(self, value: str, field_name: str) -> bool:
        """Validate UUID format (any version)."""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, str(value).lower()):
            self.errors.append(f"{field_name}: Invalid UUID format: {value}")
            return False
        return True

    def validate_iso8601_timestamp(self, value: str, field_name: str) -> bool:
        """Validate ISO 8601 timestamp format."""
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$'
        if not re.match(iso_pattern, str(value)):
            self.errors.append(f"{field_name}: Invalid ISO 8601 timestamp: {value}")
            return False
        return True

    def validate_root_manifest(self, manifest: Dict[str, Any]) -> bool:
        """Validate root-level manifest structure."""
        is_valid = True

        # Check required fields
        required_fields = ['operation', 'run_id', 'phase', 'status', 'dispatched_at', 'suggestion_count', 'suggestions']
        for field in required_fields:
            if field not in manifest:
                self.errors.append(f"Missing required field: {field}")
                is_valid = False

        # Validate operation enum
        if 'operation' in manifest:
            if manifest['operation'] not in self.VALID_OPERATIONS:
                self.errors.append(
                    f"Invalid operation: {manifest['operation']}. "
                    f"Must be one of: {', '.join(self.VALID_OPERATIONS)}"
                )
                is_valid = False

        # Validate run_id as UUID
        if 'run_id' in manifest:
            if not self.validate_uuid_format(manifest['run_id'], 'run_id'):
                is_valid = False

        # Validate team_id as UUID (optional for inline, required for remote)
        if 'team_id' in manifest:
            if not self.validate_uuid_format(manifest['team_id'], 'team_id'):
                is_valid = False
        elif manifest.get('operation') == 'remote':
            self.errors.append("team_id is required for remote operations")
            is_valid = False

        # Validate phase enum
        if 'phase' in manifest:
            if manifest['phase'] not in self.VALID_PHASES:
                self.errors.append(
                    f"Invalid phase: {manifest['phase']}. "
                    f"Must be one of: {', '.join(self.VALID_PHASES)}"
                )
                is_valid = False

        # Validate status enum
        if 'status' in manifest:
            if manifest['status'] not in self.VALID_STATUSES:
                self.errors.append(
                    f"Invalid status: {manifest['status']}. "
                    f"Must be one of: {', '.join(self.VALID_STATUSES)}"
                )
                is_valid = False

        # Validate dispatched_at timestamp
        if 'dispatched_at' in manifest:
            if not self.validate_iso8601_timestamp(manifest['dispatched_at'], 'dispatched_at'):
                is_valid = False

        # Validate expected_completion timestamp (optional)
        if 'expected_completion' in manifest:
            if not self.validate_iso8601_timestamp(manifest['expected_completion'], 'expected_completion'):
                is_valid = False

        # Validate suggestion_count matches array length
        if 'suggestion_count' in manifest and 'suggestions' in manifest:
            if manifest['suggestion_count'] != len(manifest['suggestions']):
                self.errors.append(
                    f"suggestion_count ({manifest['suggestion_count']}) does not match "
                    f"suggestions array length ({len(manifest['suggestions'])})"
                )
                is_valid = False

        return is_valid

    def validate_suggestion_status(self, sugg: Dict[str, Any], index: int) -> bool:
        """Validate individual suggestion status object."""
        is_valid = True

        # Check required fields
        required_fields = ['id', 'type', 'status']
        for field in required_fields:
            if field not in sugg:
                self.errors.append(f"Suggestion[{index}]: Missing required field: {field}")
                is_valid = False

        # Validate type enum
        if 'type' in sugg:
            if sugg['type'] not in self.VALID_SUGGESTION_TYPES:
                self.errors.append(
                    f"Suggestion[{index}].type: Invalid type: {sugg['type']}. "
                    f"Must be one of: {', '.join(self.VALID_SUGGESTION_TYPES)}"
                )
                is_valid = False

        # Validate status enum
        if 'status' in sugg:
            if sugg['status'] not in self.VALID_SUGGESTION_STATUSES:
                self.errors.append(
                    f"Suggestion[{index}].status: Invalid status: {sugg['status']}. "
                    f"Must be one of: {', '.join(self.VALID_SUGGESTION_STATUSES)}"
                )
                is_valid = False

        # Validate duck_record_path if present
        if 'duck_record_path' in sugg:
            path = sugg['duck_record_path']
            if not isinstance(path, str) or len(path) == 0:
                self.errors.append(f"Suggestion[{index}].duck_record_path: Must be non-empty string")
                is_valid = False
            # Optional: Check if path exists
            # Commented out to allow validation of pending records
            # if not Path(path).exists():
            #     self.warnings.append(f"Suggestion[{index}].duck_record_path: Path does not exist: {path}")

        # Validate error object if status=failed
        if sugg.get('status') == 'failed':
            if 'error' not in sugg:
                self.errors.append(f"Suggestion[{index}]: error object required when status=failed")
                is_valid = False
            else:
                error = sugg['error']
                error_required = ['status', 'error', 'error_detail']
                for field in error_required:
                    if field not in error:
                        self.errors.append(f"Suggestion[{index}].error: Missing required field: {field}")
                        is_valid = False

                # Validate error status enum
                if 'status' in error:
                    if error['status'] not in self.VALID_ERROR_STATUSES:
                        self.errors.append(
                            f"Suggestion[{index}].error.status: Invalid status: {error['status']}. "
                            f"Must be one of: {', '.join(self.VALID_ERROR_STATUSES)}"
                        )
                        is_valid = False

        return is_valid

    def validate_suggestions_array(self, suggestions: List[Dict]) -> bool:
        """Validate suggestions array."""
        is_valid = True

        if not isinstance(suggestions, list):
            self.errors.append("suggestions: Must be an array")
            return False

        for i, sugg in enumerate(suggestions):
            if not isinstance(sugg, dict):
                self.errors.append(f"suggestions[{i}]: Must be an object")
                is_valid = False
                continue

            if not self.validate_suggestion_status(sugg, i):
                is_valid = False

        return is_valid

    def validate(self, manifest_path: str) -> Tuple[bool, str]:
        """
        Validate manifest file.

        Args:
            manifest_path: Path to manifest.json

        Returns:
            (is_valid, summary_message)
        """
        self.errors = []
        self.warnings = []

        manifest_file = Path(manifest_path)

        # Check file exists
        if not manifest_file.exists():
            return False, f"Manifest file not found: {manifest_path}"

        # Read manifest
        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"Error reading manifest: {str(e)}"

        # Validate structure
        if not isinstance(manifest, dict):
            return False, "Manifest root must be a JSON object"

        # Validate root
        root_valid = self.validate_root_manifest(manifest)

        # Validate suggestions array
        suggestions_valid = True
        if 'suggestions' in manifest:
            suggestions_valid = self.validate_suggestions_array(manifest['suggestions'])

        is_valid = root_valid and suggestions_valid

        # Build summary
        if is_valid:
            summary = "✓ Manifest is valid"
            if self.warnings:
                summary += f"\n{len(self.warnings)} warning(s):\n"
                for warning in self.warnings:
                    summary += f"  - {warning}\n"
        else:
            summary = f"✗ Manifest validation failed:\n{len(self.errors)} error(s)"
            for error in self.errors:
                summary += f"\n  - {error}"
            if self.warnings:
                summary += f"\n\n{len(self.warnings)} warning(s):"
                for warning in self.warnings:
                    summary += f"\n  - {warning}"

        return is_valid, summary


def main():
    parser = argparse.ArgumentParser(
        description='Validate al-dev-map-suggestions-verify manifest.json'
    )
    parser.add_argument(
        '--manifest',
        type=str,
        required=True,
        help='Path to manifest.json file to validate'
    )

    args = parser.parse_args()

    validator = ManifestValidator()
    is_valid, summary = validator.validate(args.manifest)

    print(summary)

    return 0 if is_valid else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
