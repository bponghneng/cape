"""Unit tests for state manager."""

import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from cape_cli.models import WorkflowState
from cape_cli.state_manager import StateManager


class TestStateManager:
    """Test StateManager class."""

    def test_write_and_read_state(self, tmp_path):
        """Test writing and reading state files."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            state = WorkflowState(
                workflow_id="test-workflow-123",
                issue_id=42,
                status="running",
                pid=12345,
                started_at=datetime(2024, 1, 1, 12, 0, 0),
                updated_at=datetime(2024, 1, 1, 12, 5, 0),
                current_step="classify",
            )

            # Write state
            StateManager.write_state(state)

            # Read state back
            read_state = StateManager.read_state("test-workflow-123")
            assert read_state is not None
            assert read_state.workflow_id == state.workflow_id
            assert read_state.issue_id == state.issue_id
            assert read_state.status == state.status
            assert read_state.pid == state.pid
            assert read_state.current_step == state.current_step

    def test_read_nonexistent_state(self, tmp_path):
        """Test reading state from nonexistent file."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            state = StateManager.read_state("nonexistent-workflow")
            assert state is None

    def test_read_corrupted_state(self, tmp_path):
        """Test reading state from corrupted file."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            workflow_id = "corrupted-workflow"

            # Create corrupted state file
            from cape_cli.paths import CapePaths

            CapePaths.ensure_directories()
            state_file = CapePaths.get_state_dir() / f"{workflow_id}.json"
            state_file.write_text("not-valid-json")

            # Should return None for corrupted file
            state = StateManager.read_state(workflow_id)
            assert state is None

    def test_read_invalid_schema(self, tmp_path):
        """Test reading state with invalid schema."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            workflow_id = "invalid-schema-workflow"

            # Create state file with missing required fields
            from cape_cli.paths import CapePaths

            CapePaths.ensure_directories()
            state_file = CapePaths.get_state_dir() / f"{workflow_id}.json"
            state_file.write_text(json.dumps({"workflow_id": workflow_id}))

            # Should return None for invalid schema
            state = StateManager.read_state(workflow_id)
            assert state is None

    def test_update_state(self, tmp_path):
        """Test updating state with partial updates."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            # Create initial state
            initial_state = WorkflowState(
                workflow_id="test-workflow-456",
                issue_id=99,
                status="running",
                pid=67890,
                started_at=datetime(2024, 1, 1, 12, 0, 0),
                updated_at=datetime(2024, 1, 1, 12, 0, 0),
            )
            StateManager.write_state(initial_state)

            # Update state
            updated_state = StateManager.update_state(
                "test-workflow-456", status="completed", current_step="done"
            )

            # Verify update
            assert updated_state is not None
            assert updated_state.status == "completed"
            assert updated_state.current_step == "done"
            # Other fields should remain unchanged
            assert updated_state.issue_id == 99
            assert updated_state.pid == 67890
            # updated_at should be different
            assert updated_state.updated_at > initial_state.updated_at

    def test_update_nonexistent_state(self, tmp_path):
        """Test updating nonexistent state."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            result = StateManager.update_state("nonexistent", status="completed")
            assert result is None

    def test_delete_state(self, tmp_path):
        """Test deleting state file."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            state = WorkflowState(
                workflow_id="test-workflow-789",
                issue_id=123,
                status="completed",
                pid=11111,
                started_at=datetime(2024, 1, 1, 12, 0, 0),
                updated_at=datetime(2024, 1, 1, 13, 0, 0),
            )

            # Write and verify file exists
            StateManager.write_state(state)
            assert StateManager.read_state("test-workflow-789") is not None

            # Delete state file
            StateManager.delete_state("test-workflow-789")

            # Verify file is gone
            assert StateManager.read_state("test-workflow-789") is None

    def test_delete_nonexistent_state(self, tmp_path):
        """Test deleting nonexistent state file doesn't raise error."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            # Should not raise exception
            StateManager.delete_state("nonexistent-workflow")

    def test_datetime_serialization(self, tmp_path):
        """Test datetime serialization to ISO 8601."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            state = WorkflowState(
                workflow_id="datetime-test",
                issue_id=1,
                status="running",
                pid=99999,
                started_at=datetime(2024, 3, 15, 14, 30, 45),
                updated_at=datetime(2024, 3, 15, 14, 35, 50),
            )

            StateManager.write_state(state)

            # Read raw JSON to verify ISO format
            from cape_cli.paths import CapePaths

            state_file = CapePaths.get_state_dir() / "datetime-test.json"
            raw_data = json.loads(state_file.read_text())

            # Should be ISO 8601 strings
            assert raw_data["started_at"] == "2024-03-15T14:30:45"
            assert raw_data["updated_at"] == "2024-03-15T14:35:50"

            # Reading back should parse correctly
            read_state = StateManager.read_state("datetime-test")
            assert read_state is not None
            assert read_state.started_at == state.started_at
            assert read_state.updated_at == state.updated_at

    def test_atomic_write_on_failure(self, tmp_path):
        """Test that temp file is cleaned up on write failure."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            state = WorkflowState(
                workflow_id="test-workflow",
                issue_id=1,
                status="running",
                pid=12345,
                started_at=datetime.now(),
                updated_at=datetime.now(),
            )

            # Mock os.replace to raise an exception
            with patch("os.replace", side_effect=OSError("Mock error")):
                with pytest.raises(OSError):
                    StateManager.write_state(state)

                # Check that no temp files are left behind
                from cape_cli.paths import CapePaths

                state_dir = CapePaths.get_state_dir()
                temp_files = list(state_dir.glob(".tmp_*.json"))
                assert len(temp_files) == 0

    def test_write_creates_directory(self, tmp_path):
        """Test that write_state creates directory if it doesn't exist."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            state = WorkflowState(
                workflow_id="test-workflow",
                issue_id=1,
                status="running",
                pid=12345,
                started_at=datetime.now(),
                updated_at=datetime.now(),
            )

            # Directory shouldn't exist yet
            from cape_cli.paths import CapePaths

            state_dir = CapePaths.get_state_dir()
            assert not state_dir.exists()

            # Write should create directory
            StateManager.write_state(state)

            # Directory should now exist
            assert state_dir.exists()
            assert state_dir.is_dir()

    def test_all_status_values(self, tmp_path):
        """Test all valid status values."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            statuses = ["initializing", "running", "completed", "failed", "stopped"]

            for status in statuses:
                workflow_id = f"workflow-{status}"
                state = WorkflowState(
                    workflow_id=workflow_id,
                    issue_id=1,
                    status=status,  # type: ignore
                    pid=12345,
                    started_at=datetime.now(),
                    updated_at=datetime.now(),
                )

                # Should write and read successfully
                StateManager.write_state(state)
                read_state = StateManager.read_state(workflow_id)
                assert read_state is not None
                assert read_state.status == status

    def test_optional_fields(self, tmp_path):
        """Test optional fields (current_step, error_message)."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            # State without optional fields
            state1 = WorkflowState(
                workflow_id="minimal-workflow",
                issue_id=1,
                status="running",
                pid=12345,
                started_at=datetime.now(),
                updated_at=datetime.now(),
            )
            StateManager.write_state(state1)
            read1 = StateManager.read_state("minimal-workflow")
            assert read1 is not None
            assert read1.current_step is None
            assert read1.error_message is None

            # State with optional fields
            state2 = WorkflowState(
                workflow_id="full-workflow",
                issue_id=2,
                status="failed",
                pid=67890,
                started_at=datetime.now(),
                updated_at=datetime.now(),
                current_step="implement",
                error_message="Test error",
            )
            StateManager.write_state(state2)
            read2 = StateManager.read_state("full-workflow")
            assert read2 is not None
            assert read2.current_step == "implement"
            assert read2.error_message == "Test error"
