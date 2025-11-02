"""Tests for CAPE ADW functionality."""

import pytest
from cape_adw.adw import execute_adw_workflow


def test_execute_adw_workflow():
    """Test that execute_adw_workflow returns the expected success message."""
    issue_id = "123"
    description = "Test issue description"
    result = execute_adw_workflow(issue_id, description)
    assert result == f"Successfully executed ADW workflow for issue {issue_id} with description: {description}"


def test_execute_adw_workflow_with_different_id():
    """Test with a different issue ID."""
    issue_id = "ABC-456"
    description = "Another test description"
    result = execute_adw_workflow(issue_id, description)
    assert result == f"Successfully executed ADW workflow for issue {issue_id} with description: {description}"
