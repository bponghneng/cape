"""Integration tests for create_issue CLI scripts."""

import pytest
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock


def run_script(script_name: str, args: list[str]) -> subprocess.CompletedProcess:
    """Helper function to run a CLI script."""
    cmd = ["uv", "run", f"workflows/{script_name}"] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )


class TestCreateIssueFromString:
    """Tests for create_issue_from_string.py script."""

    @patch('supabase_client.get_client')
    def test_string_valid_description(self, mock_get_client):
        """Test script with valid description returns issue ID."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [{
            "id": 456,
            "description": "Test description",
            "status": "pending",
        }]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Run script
        result = run_script("create_issue_from_string.py", ["Test description"])

        # Verify results
        assert result.returncode == 0
        assert "456" in result.stdout
        assert result.stdout.strip() == "456"

    @patch('supabase_client.get_client')
    def test_string_empty_description(self, mock_get_client):
        """Test script with empty description exits with error."""
        # Setup mock (should not be called)
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Run script with empty string
        result = run_script("create_issue_from_string.py", [""])

        # Verify error exit
        assert result.returncode == 1

    @patch.dict('os.environ', {}, clear=True)
    def test_string_missing_env_vars(self):
        """Test script with missing environment variables exits with error."""
        # Run script without environment variables
        result = run_script("create_issue_from_string.py", ["Test"])

        # Verify error exit
        assert result.returncode == 1


class TestCreateIssueFromFile:
    """Tests for create_issue_from_file.py script."""

    @patch('supabase_client.get_client')
    def test_file_valid_description(self, mock_get_client):
        """Test script with valid file returns issue ID."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [{
            "id": 789,
            "description": "File description",
            "status": "pending",
        }]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("File description")
            temp_path = f.name

        try:
            # Run script
            result = run_script("create_issue_from_file.py", [temp_path])

            # Verify results
            assert result.returncode == 0
            assert "789" in result.stdout
            assert result.stdout.strip() == "789"
        finally:
            Path(temp_path).unlink()

    def test_file_nonexistent_file(self):
        """Test script with non-existent file exits with error."""
        # Run script with non-existent path
        result = run_script("create_issue_from_file.py", ["/tmp/nonexistent_file_12345.txt"])

        # Verify error exit
        assert result.returncode == 1

    def test_file_directory_path(self):
        """Test script with directory path exits with error."""
        # Run script with directory path
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_script("create_issue_from_file.py", [tmpdir])

        # Verify error exit
        assert result.returncode == 1

    def test_file_empty_file(self):
        """Test script with empty file exits with error."""
        # Create empty temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name

        try:
            # Run script
            result = run_script("create_issue_from_file.py", [temp_path])

            # Verify error exit
            assert result.returncode == 1
        finally:
            Path(temp_path).unlink()

    @patch('supabase_client.get_client')
    def test_file_multiline_description(self, mock_get_client):
        """Test script with multi-line file uses full content."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        multiline_content = "Line 1\nLine 2\nLine 3"
        mock_response.data = [{
            "id": 999,
            "description": multiline_content,
            "status": "pending",
        }]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Create temp file with multiple lines
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(multiline_content)
            temp_path = f.name

        try:
            # Run script
            result = run_script("create_issue_from_file.py", [temp_path])

            # Verify results
            assert result.returncode == 0
            assert "999" in result.stdout

            # Verify insert was called with full multiline content
            insert_call = mock_client.table.return_value.insert.call_args
            assert insert_call[0][0]["description"] == multiline_content
        finally:
            Path(temp_path).unlink()
