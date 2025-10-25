#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pytest", "python-dotenv", "pydantic", "supabase"]
# ///
"""Unit tests for ADW comment insertion functionality."""

from unittest.mock import Mock, patch

import pytest
from postgrest.exceptions import APIError

from adw_plan_build import insert_progress_comment
from data_types import CapeComment


@pytest.fixture
def mock_logger():
    """Create a mock logger instance."""
    logger = Mock()
    logger.debug = Mock()
    logger.error = Mock()
    return logger


@pytest.fixture
def mock_create_comment():
    """Create a mock for create_comment function."""
    with patch('adw_plan_build.create_comment') as mock:
        yield mock


def test_insert_comment_success(mock_create_comment, mock_logger):
    """Test successful comment insertion logs at DEBUG level with comment ID."""
    # Arrange
    mock_comment = CapeComment(
        id=123,
        issue_id=1,
        comment="Test comment"
    )
    mock_create_comment.return_value = mock_comment

    # Act
    insert_progress_comment(1, "Test comment", mock_logger)

    # Assert
    mock_create_comment.assert_called_once_with(1, "Test comment")
    mock_logger.debug.assert_called_once()
    debug_msg = mock_logger.debug.call_args[0][0]
    assert "Comment inserted" in debug_msg
    assert "ID=123" in debug_msg
    assert "Test comment" in debug_msg


def test_insert_comment_database_error(mock_create_comment, mock_logger):
    """Test APIError is caught and logged at ERROR level."""
    # Arrange
    mock_create_comment.side_effect = APIError({"message": "Database connection failed"})

    # Act
    insert_progress_comment(1, "Test", mock_logger)

    # Assert
    mock_logger.error.assert_called_once()
    error_msg = mock_logger.error.call_args[0][0]
    assert "Failed to insert comment" in error_msg
    assert "issue 1" in error_msg


def test_insert_comment_value_error(mock_create_comment, mock_logger):
    """Test ValueError is caught and logged at ERROR level."""
    # Arrange
    mock_create_comment.side_effect = ValueError("Invalid issue ID")

    # Act
    insert_progress_comment(1, "Test", mock_logger)

    # Assert
    mock_logger.error.assert_called_once()
    error_msg = mock_logger.error.call_args[0][0]
    assert "Failed to insert comment" in error_msg


def test_insert_comment_generic_exception(mock_create_comment, mock_logger):
    """Test generic exceptions are caught and logged."""
    # Arrange
    mock_create_comment.side_effect = RuntimeError("Unexpected error")

    # Act
    insert_progress_comment(1, "Test", mock_logger)

    # Assert
    mock_logger.error.assert_called_once()
    error_msg = mock_logger.error.call_args[0][0]
    assert "Failed to insert comment" in error_msg


def test_insert_comment_logs_with_comment_id(mock_create_comment, mock_logger):
    """Test that DEBUG log includes the actual comment ID from database."""
    # Arrange
    mock_comment = CapeComment(
        id=456,
        issue_id=1,
        comment="Progress update"
    )
    mock_create_comment.return_value = mock_comment

    # Act
    insert_progress_comment(1, "Progress update", mock_logger)

    # Assert
    mock_logger.debug.assert_called_once()
    debug_msg = mock_logger.debug.call_args[0][0]
    assert "ID=456" in debug_msg


# Integration Tests


def test_workflow_inserts_all_comments_on_success(mock_create_comment, mock_logger):
    """Test that all 4 comments are inserted during a successful workflow."""
    # Arrange
    comment_ids = [100, 101, 102, 103]
    mock_comments = [
        CapeComment(id=cid, issue_id=1, comment=f"Comment {cid}")
        for cid in comment_ids
    ]
    mock_create_comment.side_effect = mock_comments

    # Act - Simulate all 4 workflow stages
    insert_progress_comment(1, "Workflow started - Issue fetched and validated", mock_logger)
    insert_progress_comment(1, "Issue classified as /triage:feature", mock_logger)
    insert_progress_comment(1, "Implementation plan created successfully", mock_logger)
    insert_progress_comment(1, "Solution implemented successfully", mock_logger)

    # Assert
    assert mock_create_comment.call_count == 4
    assert mock_logger.debug.call_count == 4
    assert mock_logger.error.call_count == 0


def test_workflow_continues_on_comment_failure(mock_create_comment, mock_logger):
    """Test that workflow continues when comment insertion fails."""
    # Arrange - First call fails, second succeeds
    mock_create_comment.side_effect = [
        APIError({"message": "Database connection failed"}),
        CapeComment(id=200, issue_id=1, comment="Success")
    ]

    # Act
    insert_progress_comment(1, "First comment", mock_logger)
    insert_progress_comment(1, "Second comment", mock_logger)

    # Assert
    assert mock_create_comment.call_count == 2
    assert mock_logger.error.call_count == 1
    assert mock_logger.debug.call_count == 1


def test_workflow_logs_comment_errors(mock_create_comment, mock_logger):
    """Test that comment insertion errors include issue_id and error details."""
    # Arrange
    mock_create_comment.side_effect = ValueError("Issue 123 not found")

    # Act
    insert_progress_comment(123, "Test", mock_logger)

    # Assert
    mock_logger.error.assert_called_once()
    error_msg = mock_logger.error.call_args[0][0]
    assert "issue 123" in error_msg
    assert "Issue 123 not found" in error_msg
