"""Unit tests for create_issue() function in supabase_client.py."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from postgrest.exceptions import APIError

from supabase_client import create_issue
from data_types import CapeIssue


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    with patch('supabase_client.get_client') as mock_get_client:
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        yield mock_client


def test_create_issue_success(mock_supabase_client):
    """Test successful issue creation."""
    # Setup mock response
    mock_response = Mock()
    mock_response.data = [{
        "id": 123,
        "description": "Test issue",
        "status": "pending",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }]

    # Configure mock client chain
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

    # Call function
    result = create_issue("Test issue")

    # Verify results
    assert isinstance(result, CapeIssue)
    assert result.id == 123
    assert result.description == "Test issue"
    assert result.status == "pending"

    # Verify mock calls
    mock_supabase_client.table.assert_called_once_with("cape_issues")
    mock_supabase_client.table.return_value.insert.assert_called_once_with({
        "description": "Test issue",
        "status": "pending",
    })


def test_create_issue_empty_description(mock_supabase_client):
    """Test that empty description raises ValueError."""
    with pytest.raises(ValueError, match="Issue description cannot be empty"):
        create_issue("")


def test_create_issue_whitespace_only(mock_supabase_client):
    """Test that whitespace-only description raises ValueError."""
    with pytest.raises(ValueError, match="Issue description cannot be empty"):
        create_issue("   ")


def test_create_issue_trims_description(mock_supabase_client):
    """Test that description is trimmed before insertion."""
    # Setup mock response
    mock_response = Mock()
    mock_response.data = [{
        "id": 124,
        "description": "Test",
        "status": "pending",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }]

    # Configure mock client chain
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

    # Call function with whitespace
    result = create_issue("  Test  ")

    # Verify trimming happened
    mock_supabase_client.table.return_value.insert.assert_called_once_with({
        "description": "Test",
        "status": "pending",
    })
    assert result.description == "Test"


def test_create_issue_database_error(mock_supabase_client):
    """Test that database errors are converted to ValueError with context."""
    # Configure mock to raise APIError
    api_error = APIError({"message": "Database connection failed"})
    mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = api_error

    # Test that ValueError is raised with proper message
    with pytest.raises(ValueError, match="Failed to create issue"):
        create_issue("Test issue")


def test_create_issue_empty_response(mock_supabase_client):
    """Test that empty response data raises ValueError."""
    # Setup mock response with no data
    mock_response = Mock()
    mock_response.data = None

    # Configure mock client chain
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

    # Test that ValueError is raised
    with pytest.raises(ValueError, match="Issue creation returned no data"):
        create_issue("Test issue")


@patch('supabase_client.logger')
def test_create_issue_logs_error(mock_logger, mock_supabase_client):
    """Test that database errors are logged."""
    # Configure mock to raise APIError
    api_error = APIError({"message": "Database connection failed"})
    mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = api_error

    # Call function and catch exception
    with pytest.raises(ValueError):
        create_issue("Test issue")

    # Verify logger.error was called
    mock_logger.error.assert_called_once()
    assert "Database error creating issue" in str(mock_logger.error.call_args)
