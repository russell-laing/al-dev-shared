"""Tests for workflow_utils.py"""

import pytest
from workflow_utils import invoke_workflow, wait_for_workflow


def test_invoke_workflow_returns_task_id():
    """Test that invoke_workflow returns a valid task ID."""
    task_id = invoke_workflow(
        script="/path/to/workflow.js",
        args='[{"test": "data"}]',  # args is JSON string
        label="test-run"
    )

    # Task ID should be a non-empty string
    assert isinstance(task_id, str)
    assert len(task_id) > 0


def test_wait_for_workflow_returns_mock_findings():
    """Test that wait_for_workflow returns mock findings on success."""
    task_id = "test-task-id"

    result = wait_for_workflow(task_id, timeout_seconds=10)

    # Should return a list of findings
    assert isinstance(result, list)
    assert len(result) > 0
    assert all("lens" in r and "findings" in r for r in result)
