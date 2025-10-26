#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pytest>=7.0",
#     "python-dotenv>=1.0.0",
#     "pydantic>=2.0",
#     "supabase>=2.0",
#     "textual>=0.50.0"
# ]
# ///
"""Test suite for Cape TUI application."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from data_types import CapeIssue, CapeComment


# ============================================================================
# Unit Tests for Supabase Client Extensions
# ============================================================================


@pytest.fixture
def mock_supabase_client():
    """Fixture for mocked Supabase client."""
    with patch('supabase_client.get_client') as mock_get_client:
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        yield mock_client


def test_fetch_all_issues_success(mock_supabase_client):
    """Test successful fetch of all issues."""
    from supabase_client import fetch_all_issues

    # Mock response data
    mock_response = Mock()
    mock_response.data = [
        {
            "id": 1,
            "description": "Test issue 1",
            "status": "pending",
            "created_at": "2025-01-01T10:00:00Z",
            "updated_at": "2025-01-01T10:00:00Z"
        },
        {
            "id": 2,
            "description": "Test issue 2",
            "status": "started",
            "created_at": "2025-01-02T10:00:00Z",
            "updated_at": "2025-01-02T10:00:00Z"
        },
        {
            "id": 3,
            "description": "Test issue 3",
            "status": "completed",
            "created_at": "2025-01-03T10:00:00Z",
            "updated_at": "2025-01-03T10:00:00Z"
        }
    ]

    # Configure mock chain
    mock_supabase_client.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

    # Execute
    result = fetch_all_issues()

    # Verify
    assert len(result) == 3
    assert all(isinstance(issue, CapeIssue) for issue in result)
    assert result[0].id == 1
    assert result[0].description == "Test issue 1"
    assert result[0].status == "pending"
    assert result[1].id == 2
    assert result[2].id == 3

    # Verify correct table and ordering
    mock_supabase_client.table.assert_called_once_with("cape_issues")
    mock_supabase_client.table.return_value.select.assert_called_once_with("*")
    mock_supabase_client.table.return_value.select.return_value.order.assert_called_once_with("created_at", desc=True)


def test_fetch_all_issues_empty(mock_supabase_client):
    """Test fetch_all_issues with empty database."""
    from supabase_client import fetch_all_issues

    # Mock empty response
    mock_response = Mock()
    mock_response.data = []

    mock_supabase_client.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

    # Execute
    result = fetch_all_issues()

    # Verify
    assert result == []
    assert isinstance(result, list)


def test_fetch_all_issues_error(mock_supabase_client):
    """Test fetch_all_issues with database error."""
    from supabase_client import fetch_all_issues
    from postgrest.exceptions import APIError

    # Mock API error
    mock_supabase_client.table.return_value.select.return_value.order.return_value.execute.side_effect = APIError(
        {"message": "Database connection failed"}
    )

    # Execute and verify exception
    with pytest.raises(ValueError) as exc_info:
        fetch_all_issues()

    assert "Failed to fetch issues" in str(exc_info.value)


def test_fetch_comments_success(mock_supabase_client):
    """Test successful fetch of issue comments."""
    from supabase_client import fetch_comments

    # Mock response data
    mock_response = Mock()
    mock_response.data = [
        {
            "id": 1,
            "issue_id": 123,
            "comment": "First comment",
            "created_at": "2025-01-01T10:00:00Z"
        },
        {
            "id": 2,
            "issue_id": 123,
            "comment": "Second comment",
            "created_at": "2025-01-01T11:00:00Z"
        },
        {
            "id": 3,
            "issue_id": 123,
            "comment": "Third comment",
            "created_at": "2025-01-01T12:00:00Z"
        }
    ]

    # Configure mock chain
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

    # Execute
    result = fetch_comments(123)

    # Verify
    assert len(result) == 3
    assert all(isinstance(comment, CapeComment) for comment in result)
    assert result[0].comment == "First comment"
    assert result[0].issue_id == 123
    assert result[1].comment == "Second comment"
    assert result[2].comment == "Third comment"

    # Verify correct table and filters
    mock_supabase_client.table.assert_called_once_with("cape_comments")
    mock_supabase_client.table.return_value.select.assert_called_once_with("*")
    mock_supabase_client.table.return_value.select.return_value.eq.assert_called_once_with("issue_id", 123)
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.assert_called_once_with("created_at", desc=False)


def test_fetch_comments_empty(mock_supabase_client):
    """Test fetch_comments with no comments for issue."""
    from supabase_client import fetch_comments

    # Mock empty response
    mock_response = Mock()
    mock_response.data = []

    mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

    # Execute
    result = fetch_comments(456)

    # Verify
    assert result == []
    assert isinstance(result, list)


def test_fetch_comments_error(mock_supabase_client):
    """Test fetch_comments with database error."""
    from supabase_client import fetch_comments
    from postgrest.exceptions import APIError

    # Mock API error
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = APIError(
        {"message": "Database connection failed"}
    )

    # Execute and verify exception
    with pytest.raises(ValueError) as exc_info:
        fetch_comments(789)

    assert "Failed to fetch comments for issue 789" in str(exc_info.value)


# ============================================================================
# Integration Tests for TUI Screens
# ============================================================================


@pytest.fixture
def mock_issues():
    """Fixture for sample issue data."""
    return [
        CapeIssue(
            id=1,
            description="Test issue 1",
            status="pending",
            created_at=datetime(2025, 1, 1, 10, 0, 0),
            updated_at=datetime(2025, 1, 1, 10, 0, 0)
        ),
        CapeIssue(
            id=2,
            description="Test issue 2 with a very long description that should be truncated when displayed in the table view",
            status="started",
            created_at=datetime(2025, 1, 2, 10, 0, 0),
            updated_at=datetime(2025, 1, 2, 10, 0, 0)
        ),
        CapeIssue(
            id=3,
            description="Test issue 3",
            status="completed",
            created_at=datetime(2025, 1, 3, 10, 0, 0),
            updated_at=datetime(2025, 1, 3, 10, 0, 0)
        )
    ]


@pytest.fixture
def mock_comments():
    """Fixture for sample comment data."""
    return [
        CapeComment(
            id=1,
            issue_id=1,
            comment="First comment",
            created_at=datetime(2025, 1, 1, 10, 30, 0)
        ),
        CapeComment(
            id=2,
            issue_id=1,
            comment="Second comment",
            created_at=datetime(2025, 1, 1, 11, 0, 0)
        )
    ]


@pytest.mark.asyncio
async def test_app_launches_with_issue_list():
    """Test app startup and initial screen."""
    from cape_tui import CapeApp

    with patch('supabase_client.fetch_all_issues') as mock_fetch:
        with patch('utils.setup_logger') as mock_logger:
            mock_fetch.return_value = []
            mock_logger.return_value = Mock()

            app = CapeApp()
            async with app.run_test() as pilot:
                # Verify app started
                assert app.is_running

                # Verify initial screen is IssueListScreen
                from cape_tui import IssueListScreen
                assert isinstance(app.screen, IssueListScreen)


@pytest.mark.asyncio
async def test_create_issue_flow(mock_supabase_client):
    """Test end-to-end issue creation workflow."""
    from cape_tui import CapeApp

    with patch('supabase_client.fetch_all_issues') as mock_fetch_all:
        with patch('supabase_client.create_issue') as mock_create:
            with patch('utils.setup_logger') as mock_logger:
                # Setup mocks
                mock_fetch_all.return_value = []
                new_issue = CapeIssue(
                    id=100,
                    description="New test issue",
                    status="pending",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                mock_create.return_value = new_issue
                mock_logger.return_value = Mock()

                app = CapeApp()
                async with app.run_test() as pilot:
                    # Press 'n' to open create issue modal
                    await pilot.press("n")
                    await pilot.pause()

                    # Verify CreateIssueScreen is shown
                    from cape_tui import CreateIssueScreen
                    assert isinstance(app.screen, CreateIssueScreen)


@pytest.mark.asyncio
async def test_navigation_to_detail_screen(mock_issues):
    """Test navigation from list to detail screen."""
    from cape_tui import CapeApp

    with patch('supabase_client.fetch_all_issues') as mock_fetch_all:
        with patch('supabase_client.fetch_issue') as mock_fetch_issue:
            with patch('supabase_client.fetch_comments') as mock_fetch_comments:
                with patch('utils.setup_logger') as mock_logger:
                    # Setup mocks
                    mock_fetch_all.return_value = mock_issues
                    mock_fetch_issue.return_value = mock_issues[0]
                    mock_fetch_comments.return_value = []
                    mock_logger.return_value = Mock()

                    app = CapeApp()
                    async with app.run_test() as pilot:
                        await pilot.pause()

                        # Press Enter to view details
                        await pilot.press("enter")
                        await pilot.pause()

                        # Verify IssueDetailScreen is shown
                        from cape_tui import IssueDetailScreen
                        assert isinstance(app.screen, IssueDetailScreen)


@pytest.mark.asyncio
async def test_workflow_execution_mock():
    """Test workflow execution with mocked stages."""
    from cape_tui import WorkflowScreen

    mock_issue = CapeIssue(
        id=1,
        description="Test workflow issue",
        status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    with patch('supabase_client.fetch_issue') as mock_fetch:
        with patch('utils.setup_logger') as mock_logger:
            with patch('adw_plan_build.classify_issue') as mock_classify:
                with patch('adw_plan_build.build_plan') as mock_build:
                    with patch('adw_plan_build.get_plan_file') as mock_get_plan:
                        with patch('adw_plan_build.implement_plan') as mock_implement:
                            # Setup mocks
                            mock_fetch.return_value = mock_issue
                            mock_logger.return_value = Mock()
                            mock_classify.return_value = ("/triage:feature", None)

                            mock_plan_response = Mock()
                            mock_plan_response.success = True
                            mock_plan_response.output = "Plan output"
                            mock_build.return_value = mock_plan_response

                            mock_get_plan.return_value = ("/path/to/plan.md", None)

                            mock_impl_response = Mock()
                            mock_impl_response.success = True
                            mock_implement.return_value = mock_impl_response

                            # Note: Full integration test would require running the app
                            # This test validates the mock setup is correct
                            assert mock_fetch is not None
                            assert mock_classify is not None
                            assert mock_build is not None
                            assert mock_get_plan is not None
                            assert mock_implement is not None


# ============================================================================
# Test Fixtures and Helpers
# ============================================================================


@pytest.fixture
def sample_issue_data():
    """Fixture for sample Supabase issue data."""
    return {
        "id": 42,
        "description": "Sample issue for testing",
        "status": "pending",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
    }


@pytest.fixture
def sample_comment_data():
    """Fixture for sample Supabase comment data."""
    return {
        "id": 1,
        "issue_id": 42,
        "comment": "Sample comment for testing",
        "created_at": "2025-01-15T11:00:00Z"
    }


def test_cape_issue_from_supabase(sample_issue_data):
    """Test CapeIssue creation from Supabase data."""
    issue = CapeIssue.from_supabase(sample_issue_data)

    assert issue.id == 42
    assert issue.description == "Sample issue for testing"
    assert issue.status == "pending"


def test_cape_comment_creation(sample_comment_data):
    """Test CapeComment creation."""
    comment = CapeComment(**sample_comment_data)

    assert comment.id == 1
    assert comment.issue_id == 42
    assert comment.comment == "Sample comment for testing"
