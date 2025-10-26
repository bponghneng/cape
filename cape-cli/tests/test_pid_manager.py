"""Unit tests for PID file manager."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from cape_cli.pid_manager import PIDFileManager


class TestPIDFileManager:
    """Test PIDFileManager class."""

    def test_write_and_read_pid(self, tmp_path):
        """Test writing and reading PID files."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            workflow_id = "test-workflow-123"
            pid = 12345

            # Write PID
            PIDFileManager.write_pid(workflow_id, pid)

            # Read PID back
            read_pid = PIDFileManager.read_pid(workflow_id)
            assert read_pid == pid

    def test_read_nonexistent_pid(self, tmp_path):
        """Test reading PID from nonexistent file."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            pid = PIDFileManager.read_pid("nonexistent-workflow")
            assert pid is None

    def test_read_corrupted_pid(self, tmp_path):
        """Test reading PID from corrupted file."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            workflow_id = "corrupted-workflow"

            # Create corrupted PID file
            from cape_cli.paths import CapePaths

            CapePaths.ensure_directories()
            pid_file = CapePaths.get_runtime_dir() / f"{workflow_id}.pid"
            pid_file.write_text("not-a-number")

            # Should return None for corrupted file
            pid = PIDFileManager.read_pid(workflow_id)
            assert pid is None

    def test_delete_pid(self, tmp_path):
        """Test deleting PID file."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            workflow_id = "test-workflow-456"
            pid = 67890

            # Write and verify file exists
            PIDFileManager.write_pid(workflow_id, pid)
            assert PIDFileManager.read_pid(workflow_id) == pid

            # Delete PID file
            PIDFileManager.delete_pid(workflow_id)

            # Verify file is gone
            assert PIDFileManager.read_pid(workflow_id) is None

    def test_delete_nonexistent_pid(self, tmp_path):
        """Test deleting nonexistent PID file doesn't raise error."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            # Should not raise exception
            PIDFileManager.delete_pid("nonexistent-workflow")

    def test_is_process_running_current_process(self):
        """Test checking if current process is running."""
        current_pid = os.getpid()
        assert PIDFileManager.is_process_running(current_pid) is True

    def test_is_process_running_invalid_pid(self):
        """Test checking invalid PIDs."""
        # PID 0 and negative PIDs should return False
        assert PIDFileManager.is_process_running(0) is False
        assert PIDFileManager.is_process_running(-1) is False

    def test_is_process_running_nonexistent_pid(self):
        """Test checking nonexistent PID."""
        # Use a very large PID that is unlikely to exist
        assert PIDFileManager.is_process_running(999999999) is False

    def test_cleanup_stale_pids(self, tmp_path):
        """Test cleaning up stale PID files."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            # Create PID file for current process (should NOT be cleaned up)
            active_workflow = "active-workflow"
            PIDFileManager.write_pid(active_workflow, os.getpid())

            # Create PID file for nonexistent process (should be cleaned up)
            stale_workflow = "stale-workflow"
            PIDFileManager.write_pid(stale_workflow, 999999999)

            # Run cleanup
            cleaned = PIDFileManager.cleanup_stale_pids()

            # Should have cleaned up stale workflow
            assert stale_workflow in cleaned
            assert active_workflow not in cleaned

            # Verify stale PID is gone
            assert PIDFileManager.read_pid(stale_workflow) is None
            # Active PID should still exist
            assert PIDFileManager.read_pid(active_workflow) == os.getpid()

    def test_list_active_workflows(self, tmp_path):
        """Test listing active workflows."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            # Create active workflow
            active_workflow = "active-workflow-1"
            active_pid = os.getpid()
            PIDFileManager.write_pid(active_workflow, active_pid)

            # Create stale workflow
            stale_workflow = "stale-workflow-1"
            PIDFileManager.write_pid(stale_workflow, 999999999)

            # List active workflows
            active = PIDFileManager.list_active_workflows()

            # Should only include active workflow
            workflow_ids = [wf_id for wf_id, _ in active]
            assert active_workflow in workflow_ids
            assert stale_workflow not in workflow_ids

            # Check PID is correct
            for wf_id, pid in active:
                if wf_id == active_workflow:
                    assert pid == active_pid

    def test_atomic_write_on_failure(self, tmp_path):
        """Test that temp file is cleaned up on write failure."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            workflow_id = "test-workflow"

            # Mock os.replace to raise an exception
            with patch("os.replace", side_effect=OSError("Mock error")):
                with pytest.raises(OSError):
                    PIDFileManager.write_pid(workflow_id, 12345)

                # Check that no temp files are left behind
                from cape_cli.paths import CapePaths

                pid_dir = CapePaths.get_runtime_dir()
                temp_files = list(pid_dir.glob(".tmp_*.pid"))
                assert len(temp_files) == 0

    def test_concurrent_write_and_read(self, tmp_path):
        """Test writing and reading PIDs concurrently."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            workflow_id = "concurrent-workflow"

            # Write multiple times
            for pid in [111, 222, 333]:
                PIDFileManager.write_pid(workflow_id, pid)

            # Last write should win
            assert PIDFileManager.read_pid(workflow_id) == 333

    def test_write_creates_directory(self, tmp_path):
        """Test that write_pid creates directory if it doesn't exist."""
        with patch.dict(os.environ, {"CAPE_DATA_DIR": str(tmp_path)}):
            workflow_id = "test-workflow"

            # Directory shouldn't exist yet
            from cape_cli.paths import CapePaths

            pid_dir = CapePaths.get_runtime_dir()
            assert not pid_dir.exists()

            # Write should create directory
            PIDFileManager.write_pid(workflow_id, 12345)

            # Directory should now exist
            assert pid_dir.exists()
            assert pid_dir.is_dir()
