"""Tests for TUI auto-refresh functionality."""

import pytest
from unittest.mock import Mock, patch, PropertyMock
from datetime import datetime
from cape_cli.models import CapeIssue, CapeComment
from cape_cli.tui import IssueDetailScreen


@pytest.fixture
def mock_issue_started():
    """Create a mock issue with 'started' status."""
    return CapeIssue(
        id=1,
        description="Test issue with started status",
        status="started",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 30, 0),
    )


@pytest.fixture
def mock_issue_pending():
    """Create a mock issue with 'pending' status."""
    return CapeIssue(
        id=2,
        description="Test issue with pending status",
        status="pending",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 30, 0),
    )


@pytest.fixture
def mock_issue_completed():
    """Create a mock issue with 'completed' status."""
    return CapeIssue(
        id=3,
        description="Test issue with completed status",
        status="completed",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 13, 0, 0),
    )


@pytest.fixture
def mock_comments():
    """Create mock comments."""
    return [
        CapeComment(
            id=1,
            issue_id=1,
            comment="First comment",
            created_at=datetime(2024, 1, 1, 12, 10, 0),
        ),
        CapeComment(
            id=2,
            issue_id=1,
            comment="Second comment",
            created_at=datetime(2024, 1, 1, 12, 20, 0),
        ),
    ]


def test_auto_refresh_activates_for_started_status(mock_issue_started, mock_comments):
    """Test that auto-refresh activates when issue status is 'started'."""
    # Create screen instance
    screen = IssueDetailScreen(issue_id=1)

    # Mock set_interval to return a mock timer
    mock_timer = Mock()
    mock_timer.resume = Mock()
    mock_timer.pause = Mock()
    screen.set_interval = Mock(return_value=mock_timer)

    # Mock query_one to avoid widget lookup issues
    screen.query_one = Mock(return_value=Mock())

    # Set initial state
    screen.auto_refresh_active = False
    screen.refresh_timer = mock_timer

    # Simulate data display with started status
    screen._display_data(mock_issue_started, mock_comments)

    # Verify auto-refresh was activated
    assert screen.auto_refresh_active is True
    mock_timer.resume.assert_called_once()


def test_auto_refresh_inactive_for_pending_status(mock_issue_pending, mock_comments):
    """Test that auto-refresh remains inactive when issue status is 'pending'."""
    # Create screen instance
    screen = IssueDetailScreen(issue_id=2)

    # Mock set_interval to return a mock timer
    mock_timer = Mock()
    mock_timer.resume = Mock()
    mock_timer.pause = Mock()

    # Mock query_one to avoid widget lookup issues
    screen.query_one = Mock(return_value=Mock())

    # Set initial state
    screen.auto_refresh_active = False
    screen.refresh_timer = mock_timer

    # Simulate data display with pending status
    screen._display_data(mock_issue_pending, mock_comments)

    # Verify auto-refresh was NOT activated
    assert screen.auto_refresh_active is False
    mock_timer.resume.assert_not_called()


def test_auto_refresh_inactive_for_completed_status(mock_issue_completed, mock_comments):
    """Test that auto-refresh remains inactive when issue status is 'completed'."""
    # Create screen instance
    screen = IssueDetailScreen(issue_id=3)

    # Mock set_interval to return a mock timer
    mock_timer = Mock()
    mock_timer.resume = Mock()
    mock_timer.pause = Mock()

    # Mock query_one to avoid widget lookup issues
    screen.query_one = Mock(return_value=Mock())

    # Set initial state
    screen.auto_refresh_active = False
    screen.refresh_timer = mock_timer

    # Simulate data display with completed status
    screen._display_data(mock_issue_completed, mock_comments)

    # Verify auto-refresh was NOT activated
    assert screen.auto_refresh_active is False
    mock_timer.resume.assert_not_called()


def test_timer_cleanup_on_unmount():
    """Test that timer is properly stopped when screen is unmounted."""
    # Create screen instance
    screen = IssueDetailScreen(issue_id=1)

    # Mock timer
    mock_timer = Mock()
    mock_timer.stop = Mock()
    screen.refresh_timer = mock_timer
    screen.auto_refresh_active = True

    # Simulate unmount
    screen.on_unmount()

    # Verify timer was stopped
    mock_timer.stop.assert_called_once()
    assert screen.auto_refresh_active is False


def test_auto_refresh_deactivates_on_status_change(
    mock_issue_started, mock_issue_completed, mock_comments
):
    """Test that auto-refresh deactivates when issue status changes from 'started' to 'completed'."""
    # Create screen instance
    screen = IssueDetailScreen(issue_id=1)

    # Mock set_interval to return a mock timer
    mock_timer = Mock()
    mock_timer.resume = Mock()
    mock_timer.pause = Mock()

    # Mock query_one to avoid widget lookup issues
    screen.query_one = Mock(return_value=Mock())

    # Set initial state
    screen.auto_refresh_active = False
    screen.refresh_timer = mock_timer

    # Simulate data display with started status
    screen._display_data(mock_issue_started, mock_comments)

    # Verify auto-refresh was activated
    assert screen.auto_refresh_active is True
    mock_timer.resume.assert_called_once()

    # Simulate status change to completed
    screen._display_data(mock_issue_completed, mock_comments)

    # Verify auto-refresh was deactivated
    assert screen.auto_refresh_active is False
    mock_timer.pause.assert_called_once()
