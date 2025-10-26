"""Tests for database operations."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from cape_cli.database import (
    SupabaseConfig,
    get_client,
    create_issue,
    fetch_issue,
    fetch_all_issues,
    create_comment,
    fetch_comments,
    update_issue_status,
    update_issue_description,
)
from cape_cli.models import CapeIssue, CapeComment


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test_key")


def test_supabase_config_validation_success(mock_env):
    """Test config validation with valid env vars."""
    config = SupabaseConfig()
    config.validate()  # Should not raise


def test_supabase_config_validation_missing_url(monkeypatch):
    """Test config validation fails with missing URL."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test_key")

    config = SupabaseConfig()
    with pytest.raises(ValueError, match="SUPABASE_URL"):
        config.validate()


def test_supabase_config_validation_missing_key(monkeypatch):
    """Test config validation fails with missing key."""
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    config = SupabaseConfig()
    with pytest.raises(ValueError, match="SUPABASE_SERVICE_ROLE_KEY"):
        config.validate()


@patch("cape_cli.database.create_client")
def test_get_client(mock_create_client, mock_env):
    """Test get_client creates and returns client."""
    mock_client = Mock()
    mock_create_client.return_value = mock_client

    # Clear cache and global client
    get_client.cache_clear()
    import cape_cli.database
    cape_cli.database._client = None

    client = get_client()
    assert client is mock_client
    mock_create_client.assert_called_once()


@patch("cape_cli.database.get_client")
def test_create_issue_success(mock_get_client):
    """Test successful issue creation."""
    mock_client = Mock()
    mock_table = Mock()
    mock_insert = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_execute.data = [{"id": 1, "description": "Test issue", "status": "pending"}]
    mock_insert.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = create_issue("Test issue")
    assert issue.id == 1
    assert issue.description == "Test issue"
    assert issue.status == "pending"


@patch("cape_cli.database.get_client")
def test_create_issue_empty_description(mock_get_client):
    """Test creating issue with empty description fails."""
    with pytest.raises(ValueError, match="cannot be empty"):
        create_issue("")


@patch("cape_cli.database.get_client")
def test_create_issue_whitespace_only(mock_get_client):
    """Test creating issue with whitespace-only description fails."""
    with pytest.raises(ValueError, match="cannot be empty"):
        create_issue("   ")


@patch("cape_cli.database.get_client")
def test_fetch_issue_success(mock_get_client):
    """Test successful issue fetch."""
    mock_client = Mock()
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_maybe_single = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.maybe_single.return_value = mock_maybe_single
    mock_execute.data = {"id": 1, "description": "Test issue", "status": "pending"}
    mock_maybe_single.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = fetch_issue(1)
    assert issue.id == 1
    assert issue.description == "Test issue"


@patch("cape_cli.database.get_client")
def test_fetch_issue_not_found(mock_get_client):
    """Test fetching non-existent issue."""
    mock_client = Mock()
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_maybe_single = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.maybe_single.return_value = mock_maybe_single
    mock_execute.data = None
    mock_maybe_single.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError, match="not found"):
        fetch_issue(999)


@patch("cape_cli.database.get_client")
def test_fetch_all_issues_success(mock_get_client):
    """Test fetching all issues."""
    mock_client = Mock()
    mock_table = Mock()
    mock_select = Mock()
    mock_order = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.order.return_value = mock_order
    mock_execute.data = [
        {"id": 1, "description": "Issue 1", "status": "pending"},
        {"id": 2, "description": "Issue 2", "status": "completed"},
    ]
    mock_order.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issues = fetch_all_issues()
    assert len(issues) == 2
    assert issues[0].id == 1
    assert issues[1].id == 2


@patch("cape_cli.database.get_client")
def test_create_comment_success(mock_get_client):
    """Test successful comment creation."""
    mock_client = Mock()
    mock_table = Mock()
    mock_insert = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_execute.data = [{"id": 1, "issue_id": 1, "comment": "Test comment"}]
    mock_insert.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    comment = create_comment(1, "Test comment")
    assert comment.issue_id == 1
    assert comment.comment == "Test comment"


@patch("cape_cli.database.get_client")
def test_fetch_comments_success(mock_get_client):
    """Test fetching comments for an issue."""
    mock_client = Mock()
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_order = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.order.return_value = mock_order
    mock_execute.data = [
        {"id": 1, "issue_id": 1, "comment": "Comment 1"},
        {"id": 2, "issue_id": 1, "comment": "Comment 2"},
    ]
    mock_order.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    comments = fetch_comments(1)
    assert len(comments) == 2
    assert comments[0].comment == "Comment 1"
    assert comments[1].comment == "Comment 2"


@patch("cape_cli.database.get_client")
def test_update_issue_status_success(mock_get_client):
    """Test successful status update."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = [{"id": 1, "description": "Test issue", "status": "started"}]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = update_issue_status(1, "started")
    assert issue.id == 1
    assert issue.status == "started"
    mock_table.update.assert_called_once_with({"status": "started"})


@patch("cape_cli.database.get_client")
def test_update_issue_status_to_completed(mock_get_client):
    """Test updating status to completed."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = [{"id": 1, "description": "Test issue", "status": "completed"}]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = update_issue_status(1, "completed")
    assert issue.status == "completed"


@patch("cape_cli.database.get_client")
def test_update_issue_status_invalid_status(mock_get_client):
    """Test updating with invalid status fails."""
    with pytest.raises(ValueError, match="Invalid status"):
        update_issue_status(1, "invalid_status")


@patch("cape_cli.database.get_client")
def test_update_issue_status_not_found(mock_get_client):
    """Test updating non-existent issue."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = None
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError, match="not found"):
        update_issue_status(999, "started")


@patch("cape_cli.database.get_client")
def test_update_issue_description_success(mock_get_client):
    """Test successful description update."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = [
        {"id": 1, "description": "Updated description", "status": "pending"}
    ]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = update_issue_description(1, "Updated description")
    assert issue.id == 1
    assert issue.description == "Updated description"
    mock_table.update.assert_called_once_with({"description": "Updated description"})


@patch("cape_cli.database.get_client")
def test_update_issue_description_empty(mock_get_client):
    """Test updating with empty description fails."""
    with pytest.raises(ValueError, match="cannot be empty"):
        update_issue_description(1, "")


@patch("cape_cli.database.get_client")
def test_update_issue_description_whitespace_only(mock_get_client):
    """Test updating with whitespace-only description fails."""
    with pytest.raises(ValueError, match="cannot be empty"):
        update_issue_description(1, "   ")


@patch("cape_cli.database.get_client")
def test_update_issue_description_too_short(mock_get_client):
    """Test updating with too short description fails."""
    with pytest.raises(ValueError, match="at least 10 characters"):
        update_issue_description(1, "Short")


@patch("cape_cli.database.get_client")
def test_update_issue_description_too_long(mock_get_client):
    """Test updating with too long description fails."""
    long_description = "x" * 10001
    with pytest.raises(ValueError, match="cannot exceed 10000 characters"):
        update_issue_description(1, long_description)


@patch("cape_cli.database.get_client")
def test_update_issue_description_not_found(mock_get_client):
    """Test updating description of non-existent issue."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = None
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError, match="not found"):
        update_issue_description(999, "Valid description text here")
