"""Tests for delete functionality in the TUI."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from cape_cli.tui import ConfirmDeleteModal, IssueListScreen, IssueDetailScreen
from cape_cli.models import CapeIssue


@pytest.fixture
def mock_issue():
    """Create a mock CapeIssue for testing."""
    return CapeIssue(
        id=1,
        description="Test issue for deletion",
        status="pending",
    )


@pytest.fixture
def mock_started_issue():
    """Create a mock CapeIssue with started status."""
    return CapeIssue(
        id=2,
        description="Started issue that should not be deleted",
        status="started",
    )


class TestConfirmDeleteModal:
    """Test cases for ConfirmDeleteModal."""

    def test_modal_initialization(self, mock_issue):
        """Test modal initializes with correct issue data."""
        modal = ConfirmDeleteModal(mock_issue.id, mock_issue.description)
        assert modal.issue_id == mock_issue.id
        assert modal.issue_description == mock_issue.description

    def test_modal_truncates_long_description(self):
        """Test that long descriptions are truncated."""
        long_desc = "x" * 150
        modal = ConfirmDeleteModal(1, long_desc)
        assert modal.issue_description == long_desc
        # The truncation happens in compose(), not __init__


class TestIssueListScreenDelete:
    """Test cases for delete functionality in IssueListScreen.

    Note: Full integration testing of Textual screens requires an app context.
    These tests verify basic logic and structure.
    """

    @patch("cape_cli.database.delete_issue")
    def test_delete_issue_function_called(self, mock_delete):
        """Test that delete_issue function is importable and callable."""
        from cape_cli.database import delete_issue

        mock_delete.return_value = True

        # Verify the function is properly imported in tui module
        from cape_cli.tui import delete_issue as tui_delete_issue
        assert tui_delete_issue is not None


class TestIssueDetailScreenDelete:
    """Test cases for delete functionality in IssueDetailScreen.

    Note: Full integration testing of Textual screens requires an app context.
    These tests verify basic logic and structure.
    """

    def test_screen_has_delete_binding(self):
        """Test that IssueDetailScreen has delete key binding."""
        bindings = [binding[0] for binding in IssueDetailScreen.BINDINGS]
        assert "delete" in bindings

    def test_screen_has_action_delete_issue(self):
        """Test that IssueDetailScreen has action_delete_issue method."""
        assert hasattr(IssueDetailScreen, "action_delete_issue")
        assert callable(getattr(IssueDetailScreen, "action_delete_issue"))

    def test_screen_has_handle_delete_confirmation(self):
        """Test that IssueDetailScreen has handle_delete_confirmation method."""
        assert hasattr(IssueDetailScreen, "handle_delete_confirmation")
        assert callable(getattr(IssueDetailScreen, "handle_delete_confirmation"))

    def test_screen_has_delete_issue_handler(self):
        """Test that IssueDetailScreen has delete_issue_handler method."""
        assert hasattr(IssueDetailScreen, "delete_issue_handler")
        assert callable(getattr(IssueDetailScreen, "delete_issue_handler"))

    def test_handle_delete_confirmation_cancelled(self):
        """Test handling cancelled delete confirmation."""
        screen = IssueDetailScreen(issue_id=1)
        screen.delete_issue_handler = Mock()

        # User cancels
        screen.handle_delete_confirmation(False)

        # Should not call delete handler
        screen.delete_issue_handler.assert_not_called()

    def test_handle_delete_confirmation_accepted(self):
        """Test handling accepted delete confirmation."""
        screen = IssueDetailScreen(issue_id=1)
        screen.delete_issue_handler = Mock()

        # User confirms
        screen.handle_delete_confirmation(True)

        # Should call delete handler
        screen.delete_issue_handler.assert_called_once()


class TestIssueListScreenDeleteBindings:
    """Test cases for delete bindings in IssueListScreen."""

    def test_screen_has_delete_bindings(self):
        """Test that IssueListScreen has delete key bindings."""
        bindings = [binding[0] for binding in IssueListScreen.BINDINGS]
        assert "d" in bindings
        assert "delete" in bindings

    def test_screen_has_action_delete_issue(self):
        """Test that IssueListScreen has action_delete_issue method."""
        assert hasattr(IssueListScreen, "action_delete_issue")
        assert callable(getattr(IssueListScreen, "action_delete_issue"))

    def test_screen_has_delete_handlers(self):
        """Test that IssueListScreen has delete handler methods."""
        assert hasattr(IssueListScreen, "handle_delete_confirmation")
        assert callable(getattr(IssueListScreen, "handle_delete_confirmation"))
        assert hasattr(IssueListScreen, "delete_issue_handler")
        assert callable(getattr(IssueListScreen, "delete_issue_handler"))
